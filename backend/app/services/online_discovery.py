import json
import re
from typing import Any

from app.core.config import settings
from app.models.content import Content
from app.repositories.content import ContentRepository
from app.services.ai import ai_service


STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "and",
    "based",
    "book",
    "books",
    "from",
    "have",
    "movie",
    "movies",
    "recommend",
    "show",
    "shows",
    "that",
    "the",
    "this",
    "with",
}


class OnlineDiscoveryService:
    def extract_keywords(self, text: str, limit: int = 8) -> list[str]:
        words = [word.lower() for word in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", text)]
        scored: dict[str, int] = {}
        for word in words:
            if word in STOPWORDS:
                continue
            scored[word] = scored.get(word, 0) + 1
        return [word for word, _ in sorted(scored.items(), key=lambda item: (-item[1], item[0]))[:limit]]

    async def search_and_import(
        self,
        db,
        query: str,
        content_type: str | None,
        limit: int,
    ) -> tuple[list[Content], list[str]]:
        keywords = self.extract_keywords(query)
        search_query = " ".join(keywords) or query
        payloads = await self.search(search_query, content_type, limit)
        imported: list[Content] = []
        repo = ContentRepository(db)

        for payload in payloads:
            existing = await repo.find_existing(payload["title"], payload["content_type"], payload.get("release_year"))
            if existing:
                imported.append(existing)
                continue
            payload["embedding"] = await ai_service.embed_content_payload(payload)
            imported.append(await repo.create(Content(**payload)))

        await db.commit()
        return imported, keywords

    async def search(self, query: str, content_type: str | None, limit: int) -> list[dict]:
        if not ai_service.groq:
            return []
        try:
            response = await ai_service.groq.chat.completions.create(
                model=settings.online_discovery_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You discover real books, movies, and TV shows for a recommendation app. "
                            "Use web search when available. Return only valid JSON with an items array. "
                            "Do not invent titles, dates, descriptions, or image URLs."
                        ),
                    },
                    {
                        "role": "user",
                        "content": self._build_discovery_prompt(query, content_type, limit),
                    },
                ],
                temperature=0.2,
                max_tokens=1800,
            )
        except Exception:
            return []

        content = response.choices[0].message.content if response.choices else None
        return self._parse_items(content, content_type, limit)

    def _build_discovery_prompt(self, query: str, content_type: str | None, limit: int) -> str:
        type_instruction = content_type if content_type else "book, movie, and tv"
        return (
            f"Find up to {min(limit, 10)} real {type_instruction} recommendations matching this query: {query!r}.\n"
            "Return this exact JSON shape:\n"
            '{"items":[{"title":"string","description":"string","genres":["string"],'
            '"themes":["string"],"mood":["string"],"storytelling_style":["string"],'
            '"pacing":"slow|medium|fast|unknown","release_year":2000,'
            '"content_type":"book|movie|tv","poster_url":null}]}\n'
            "Descriptions should be factual and concise. Use null for release_year or poster_url when uncertain."
        )

    def _parse_items(self, content: str | None, content_type: str | None, limit: int) -> list[dict]:
        if not content:
            return []
        payload = self._load_json(content)
        raw_items = payload.get("items", payload) if isinstance(payload, dict) else payload
        if not isinstance(raw_items, list):
            return []

        items: list[dict] = []
        for raw_item in raw_items:
            normalized = self._normalize_item(raw_item, content_type)
            if normalized:
                items.append(normalized)
            if len(items) >= limit:
                break
        return items

    def _load_json(self, content: str) -> Any:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("[")
            end = cleaned.rfind("]")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    return None
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    return None
            return None

    def _normalize_item(self, item: Any, requested_type: str | None) -> dict | None:
        if not isinstance(item, dict):
            return None

        title = self._clean_string(item.get("title"))
        description = self._clean_string(item.get("description"))
        item_type = self._clean_string(item.get("content_type"))
        item_type = item_type.lower() if item_type else None
        if item_type == "show":
            item_type = "tv"
        if not title or not description or item_type not in {"book", "movie", "tv"}:
            return None
        if requested_type and item_type != requested_type:
            return None

        pacing = self._clean_string(item.get("pacing")) or "unknown"
        pacing = pacing.lower()
        if pacing not in {"slow", "medium", "fast", "unknown"}:
            pacing = "unknown"

        poster_url = self._clean_string(item.get("poster_url"))
        if poster_url and not poster_url.startswith(("http://", "https://")):
            poster_url = None

        return {
            "title": title,
            "description": description,
            "genres": self._clean_string_list(item.get("genres")),
            "themes": self._clean_string_list(item.get("themes")),
            "mood": self._clean_string_list(item.get("mood")),
            "storytelling_style": self._clean_string_list(item.get("storytelling_style")),
            "pacing": pacing,
            "release_year": self._clean_year(item.get("release_year")),
            "content_type": item_type,
            "poster_url": poster_url,
        }

    def _clean_string(self, value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        cleaned = value.strip()
        return cleaned or None

    def _clean_string_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [cleaned for item in value if (cleaned := self._clean_string(item))]

    def _clean_year(self, value: Any) -> int | None:
        if isinstance(value, int):
            return value if 1800 <= value <= 2100 else None
        if isinstance(value, str) and value.isdigit():
            year = int(value)
            return year if 1800 <= year <= 2100 else None
        return None


online_discovery = OnlineDiscoveryService()
