from uuid import uuid4

from app.models.content import Content
from app.models.interaction import UserInteraction
from app.repositories.content import ContentRepository
from app.repositories.interactions import InteractionRepository
from app.repositories.recommendations import RecommendationRepository
from app.services.ai import ai_service
from app.services.online_discovery import online_discovery


STATUS_WEIGHTS = {
    "favorite": 5.0,
    "liked": 3.0,
    "watched": 1.0,
    "read": 1.0,
    "want_to_watch": 0.8,
    "want_to_read": 0.8,
}


class RecommendationService:
    def __init__(self, db):
        self.db = db
        self.content = ContentRepository(db)
        self.interactions = InteractionRepository(db)
        self.recommendations = RecommendationRepository(db)

    def _interaction_weight(self, interaction: UserInteraction) -> float:
        status_weight = STATUS_WEIGHTS.get(interaction.status, 0.0)
        rating_boost = ((interaction.rating or 5) - 5) / 5
        return max(status_weight + rating_boost, 0.1)

    def build_user_embedding(self, interactions: list[UserInteraction]) -> list[float] | None:
        vectors: list[tuple[list[float], float]] = []
        for interaction in interactions:
            if interaction.content.embedding:
                vectors.append((interaction.content.embedding, self._interaction_weight(interaction)))
        if not vectors:
            return None
        dimensions = len(vectors[0][0])
        totals = [0.0] * dimensions
        weight_sum = sum(weight for _, weight in vectors)
        for vector, weight in vectors:
            for index, value in enumerate(vector):
                totals[index] += value * weight
        averaged = [value / weight_sum for value in totals]
        norm = sum(value * value for value in averaged) ** 0.5
        return [value / norm for value in averaged] if norm else averaged

    async def recommend(self, user_id: str, limit: int, content_type: str | None, refresh: bool) -> list[dict]:
        if not refresh:
            cached = await self.recommendations.list_for_user(user_id, limit)
            if cached:
                return [
                    {
                        **self._content_to_dict(item.content),
                        "score": item.score,
                        "explanation": item.explanation,
                    }
                    for item in cached
                ]

        interactions = await self.interactions.taste_profile_for_user(user_id)
        user_embedding = self.build_user_embedding(interactions)
        if user_embedding is None:
            return []

        consumed_ids = [interaction.content_id for interaction in interactions]
        keywords = self._taste_keywords(interactions)
        if keywords:
            await online_discovery.search_and_import(
                self.db,
                " ".join(keywords),
                content_type,
                max(limit, 12),
            )

        candidates = await self.content.vector_search(user_embedding, limit * 3, content_type, consumed_ids)
        liked_titles = [
            interaction.content.title
            for interaction in sorted(interactions, key=self._interaction_weight, reverse=True)
            if interaction.status in ["favorite", "liked"] or (interaction.rating or 0) >= 8
        ]

        ranked: list[dict] = []
        for candidate, similarity in candidates[:limit]:
            diversity_bonus = 0.03 if candidate.content_type != (interactions[0].content.content_type if interactions else "") else 0
            score = min(similarity + diversity_bonus, 1.0)
            explanation = await ai_service.explain(liked_titles, candidate)
            ranked.append({**self._content_to_dict(candidate), "score": score, "explanation": explanation})

        await self.recommendations.replace_for_user(
            user_id,
            [
                {
                    "id": str(uuid4()),
                    "user_id": user_id,
                    "content_id": row["id"],
                    "score": row["score"],
                    "explanation": row["explanation"],
                }
                for row in ranked
            ],
        )
        await self.db.commit()
        return ranked

    def _taste_keywords(self, interactions: list[UserInteraction]) -> list[str]:
        text = " ".join(
            " ".join(
                [
                    interaction.content.title,
                    " ".join(interaction.content.genres or []),
                    " ".join(interaction.content.themes or []),
                    " ".join(interaction.content.mood or []),
                    " ".join(interaction.content.storytelling_style or []),
                ]
            )
            for interaction in interactions
            if interaction.status in STATUS_WEIGHTS
        )
        return online_discovery.extract_keywords(text, limit=8)

    def _content_to_dict(self, item: Content) -> dict:
        return {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "genres": item.genres,
            "themes": item.themes,
            "mood": item.mood,
            "storytelling_style": item.storytelling_style,
            "pacing": item.pacing,
            "release_year": item.release_year,
            "content_type": item.content_type,
            "poster_url": item.poster_url,
        }
