from types import SimpleNamespace

import pytest

from app.api.routes import search as search_route
from app.schemas.recommendation import SearchRequest


class FakeOnlineDiscovery:
    def extract_keywords(self, query: str) -> list[str]:
        return ["dark", "thriller"]

    async def search_and_import(self, db, query: str, content_type: str | None, limit: int):
        return [SimpleNamespace(id="internet-1")], ["dark", "thriller"]


class FakeAI:
    async def embed_text(self, query: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class FakeContentRepository:
    def __init__(self, db):
        self.db = db

    async def vector_search(self, embedding, limit, content_type):
        assert embedding == [0.1, 0.2, 0.3]
        assert limit == 2
        assert content_type == "movie"
        return [
            (
                SimpleNamespace(
                    id="movie-1",
                    title="Blade Runner 2049",
                    description="A replicant investigates identity and memory.",
                    genres=["science fiction"],
                    themes=["identity"],
                    mood=["dark"],
                    storytelling_style=["atmospheric"],
                    pacing="slow burn",
                    release_year=2017,
                    content_type="movie",
                    poster_url=None,
                ),
                0.91,
            )
        ]


@pytest.mark.asyncio
async def test_semantic_search_returns_keywords_counts_and_items(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(search_route, "online_discovery", FakeOnlineDiscovery())
    monkeypatch.setattr(search_route, "ai_service", FakeAI())
    monkeypatch.setattr(search_route, "ContentRepository", FakeContentRepository)

    response = await search_route.semantic_search(
        SearchRequest(query="dark sci-fi thriller", limit=2, content_type="movie", include_internet=True),
        db=object(),
    )

    assert response["keywords"] == ["dark", "thriller"]
    assert response["internet_count"] == 1
    assert response["local_count"] == 0
    assert response["items"][0]["title"] == "Blade Runner 2049"
    assert response["items"][0]["score"] == 0.91


@pytest.mark.asyncio
async def test_semantic_search_can_skip_internet(monkeypatch: pytest.MonkeyPatch) -> None:
    class NoInternet(FakeOnlineDiscovery):
        async def search_and_import(self, *args, **kwargs):
            raise AssertionError("internet search should not run")

    monkeypatch.setattr(search_route, "online_discovery", NoInternet())
    monkeypatch.setattr(search_route, "ai_service", FakeAI())
    monkeypatch.setattr(search_route, "ContentRepository", FakeContentRepository)

    response = await search_route.semantic_search(
        SearchRequest(query="dark sci-fi thriller", limit=2, content_type="movie", include_internet=False),
        db=object(),
    )

    assert response["keywords"] == ["dark", "thriller"]
    assert response["internet_count"] == 0
    assert response["items"]
