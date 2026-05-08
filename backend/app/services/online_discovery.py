import re

import httpx

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
        async with httpx.AsyncClient(timeout=12) as client:
            tasks = []
            if content_type in (None, "book"):
                tasks.append(self._search_books(client, query, limit))
            if content_type in (None, "movie"):
                tasks.append(self._search_itunes(client, query, "movie", "movie", limit))
            if content_type in (None, "tv"):
                tasks.append(self._search_itunes(client, query, "tvShow", "tvSeason", limit))
            results: list[dict] = []
            for task in tasks:
                try:
                    results.extend(await task)
                except httpx.HTTPError:
                    continue
            return results[:limit]

    async def _search_books(self, client: httpx.AsyncClient, query: str, limit: int) -> list[dict]:
        response = await client.get(
            "https://openlibrary.org/search.json",
            params={
                "q": query,
                "limit": min(limit, 10),
                "fields": "key,title,author_name,first_publish_year,subject,cover_i",
            },
        )
        response.raise_for_status()
        docs = response.json().get("docs", [])
        items: list[dict] = []
        for doc in docs:
            title = doc.get("title")
            if not title:
                continue
            authors = ", ".join(doc.get("author_name", [])[:2])
            subjects = [str(item).lower() for item in doc.get("subject", [])[:8]]
            cover_id = doc.get("cover_i")
            items.append(
                {
                    "title": title,
                    "description": f"{title} by {authors}. Subjects include {', '.join(subjects[:5])}.".strip(),
                    "genres": subjects[:4] or ["fiction"],
                    "themes": subjects[4:8] or subjects[:4],
                    "mood": [],
                    "storytelling_style": [],
                    "pacing": "unknown",
                    "release_year": doc.get("first_publish_year"),
                    "content_type": "book",
                    "poster_url": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None,
                }
            )
        return items

    async def _search_itunes(
        self,
        client: httpx.AsyncClient,
        query: str,
        media: str,
        entity: str,
        limit: int,
    ) -> list[dict]:
        response = await client.get(
            "https://itunes.apple.com/search",
            params={"term": query, "country": "US", "media": media, "entity": entity, "limit": min(limit, 10)},
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        items: list[dict] = []
        for result in results:
            title = result.get("trackName") or result.get("collectionName")
            description = result.get("longDescription") or result.get("shortDescription") or result.get("description")
            if not title or not description:
                continue
            release_date = result.get("releaseDate") or ""
            artwork = result.get("artworkUrl100")
            content_type = "movie" if media == "movie" else "tv"
            items.append(
                {
                    "title": title,
                    "description": description,
                    "genres": [result.get("primaryGenreName")] if result.get("primaryGenreName") else [],
                    "themes": [],
                    "mood": [],
                    "storytelling_style": [],
                    "pacing": "unknown",
                    "release_year": int(release_date[:4]) if release_date[:4].isdigit() else None,
                    "content_type": content_type,
                    "poster_url": artwork.replace("100x100", "600x600") if artwork else None,
                }
            )
        return items


online_discovery = OnlineDiscoveryService()
