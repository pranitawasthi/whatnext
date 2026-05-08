import httpx
import pytest

from app.services.online_discovery import OnlineDiscoveryService


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self.payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("boom", request=httpx.Request("GET", "https://example.test"), response=httpx.Response(self.status_code))


class FakeClient:
    def __init__(self, responses: list[FakeResponse]):
        self.responses = responses
        self.calls: list[tuple[str, dict]] = []

    async def get(self, url: str, params: dict):
        self.calls.append((url, params))
        return self.responses.pop(0)


def test_extract_keywords_removes_stopwords_and_counts_repeated_terms() -> None:
    service = OnlineDiscoveryService()

    keywords = service.extract_keywords("dark dark psychological sci-fi thriller with movies and books", limit=4)

    assert keywords == ["dark", "psychological", "sci-fi", "thriller"]


@pytest.mark.asyncio
async def test_search_books_maps_open_library_results() -> None:
    service = OnlineDiscoveryService()
    client = FakeClient(
        [
            FakeResponse(
                {
                    "docs": [
                        {
                            "title": "Dune",
                            "author_name": ["Frank Herbert"],
                            "first_publish_year": 1965,
                            "subject": ["Science fiction", "Ecology", "Empire", "Desert"],
                            "cover_i": 123,
                        },
                        {"author_name": ["Nobody"]},
                    ]
                }
            )
        ]
    )

    results = await service._search_books(client, "dune", 10)

    assert len(results) == 1
    assert results[0]["title"] == "Dune"
    assert results[0]["content_type"] == "book"
    assert results[0]["release_year"] == 1965
    assert results[0]["genres"] == ["science fiction", "ecology", "empire", "desert"]
    assert results[0]["poster_url"] == "https://covers.openlibrary.org/b/id/123-L.jpg"
    assert client.calls[0][0] == "https://openlibrary.org/search.json"
    assert client.calls[0][1]["fields"]


@pytest.mark.asyncio
async def test_search_itunes_maps_movie_results() -> None:
    service = OnlineDiscoveryService()
    client = FakeClient(
        [
            FakeResponse(
                {
                    "results": [
                        {
                            "trackName": "Interstellar",
                            "longDescription": "A wormhole journey through space and time.",
                            "releaseDate": "2014-11-07T08:00:00Z",
                            "artworkUrl100": "https://img.test/100x100bb.jpg",
                            "primaryGenreName": "Sci-Fi & Fantasy",
                        },
                        {"trackName": "Missing Description"},
                    ]
                }
            )
        ]
    )

    results = await service._search_itunes(client, "interstellar", "movie", "movie", 10)

    assert len(results) == 1
    assert results[0]["title"] == "Interstellar"
    assert results[0]["content_type"] == "movie"
    assert results[0]["release_year"] == 2014
    assert results[0]["genres"] == ["Sci-Fi & Fantasy"]
    assert results[0]["poster_url"] == "https://img.test/600x600bb.jpg"
    assert client.calls[0][0] == "https://itunes.apple.com/search"
    assert client.calls[0][1]["media"] == "movie"


@pytest.mark.asyncio
async def test_search_ignores_failing_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    service = OnlineDiscoveryService()

    async def failing_books(*args, **kwargs):
        raise httpx.ConnectError("offline")

    async def movie_results(*args, **kwargs):
        return [{"title": "Arrival", "content_type": "movie"}]

    monkeypatch.setattr(service, "_search_books", failing_books)
    monkeypatch.setattr(service, "_search_itunes", movie_results)

    results = await service.search("thoughtful aliens", None, 5)

    assert results == [{"title": "Arrival", "content_type": "movie"}, {"title": "Arrival", "content_type": "movie"}]
