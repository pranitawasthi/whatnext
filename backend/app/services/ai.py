import asyncio
from functools import cached_property

from groq import AsyncGroq
from openai import AsyncOpenAI

from app.core.config import settings
from app.models.content import Content


class AIService:
    def __init__(self) -> None:
        # OpenAI is optional now and used only as a chat explanation fallback.
        self.openai = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.groq = AsyncGroq(api_key=settings.groq_api_key) if settings.groq_api_key else None

    @cached_property
    def embedding_model(self):
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(settings.embedding_model)

    def build_embedding_text(self, item: Content | dict) -> str:
        get = item.get if isinstance(item, dict) else lambda key, default=None: getattr(item, key, default)
        return "\n".join(
            [
                f"Title: {get('title')}",
                f"Type: {get('content_type')}",
                f"Description: {get('description')}",
                f"Genres: {', '.join(get('genres', []) or [])}",
                f"Themes: {', '.join(get('themes', []) or [])}",
                f"Mood: {', '.join(get('mood', []) or [])}",
                f"Storytelling style: {', '.join(get('storytelling_style', []) or [])}",
                f"Pacing: {get('pacing')}",
            ]
        )

    async def embed_text(self, text: str) -> list[float]:
        def encode() -> list[float]:
            vector = self.embedding_model.encode(text, normalize_embeddings=True)
            return [float(value) for value in vector.tolist()]

        return await asyncio.to_thread(encode)

    async def embed_content_payload(self, payload: dict) -> list[float]:
        return await self.embed_text(self.build_embedding_text(payload))

    async def explain(self, liked_titles: list[str], candidate: Content) -> str:
        fallback = (
            f"Because your taste overlaps with {', '.join(liked_titles[:3]) or 'your recent favorites'}, "
            f"{candidate.title} matches similar genres, themes, mood, and storytelling rhythm."
        )
        prompt = (
            "Write one concise recommendation explanation in second person. "
            "Mention themes, mood, pacing, and similarity. Do not invent facts.\n\n"
            f"User liked: {', '.join(liked_titles[:5])}\n"
            f"Candidate: {candidate.title} ({candidate.content_type})\n"
            f"Description: {candidate.description}\n"
            f"Genres: {', '.join(candidate.genres)}\n"
            f"Themes: {', '.join(candidate.themes)}\n"
            f"Mood: {', '.join(candidate.mood)}\n"
            f"Style: {', '.join(candidate.storytelling_style)}\n"
            f"Pacing: {candidate.pacing}"
        )
        try:
            if self.groq:
                response = await self.groq.chat.completions.create(
                    model=settings.explanation_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=90,
                )
                return response.choices[0].message.content or fallback
            if self.openai:
                response = await self.openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=90,
                )
                return response.choices[0].message.content or fallback
        except Exception:
            return fallback
        return fallback


ai_service = AIService()
