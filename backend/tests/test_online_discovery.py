import pytest

from app.services.online_discovery import OnlineDiscoveryService


def test_extract_keywords_removes_stopwords_and_counts_repeated_terms() -> None:
    service = OnlineDiscoveryService()

    keywords = service.extract_keywords("dark dark psychological sci-fi thriller with movies and books", limit=4)

    assert keywords == ["dark", "psychological", "sci-fi", "thriller"]


@pytest.mark.asyncio
async def test_search_uses_groq_and_normalizes_results(monkeypatch: pytest.MonkeyPatch) -> None:
    service = OnlineDiscoveryService()

    class FakeCompletions:
        def __init__(self) -> None:
            self.kwargs = None

        async def create(self, **kwargs):
            self.kwargs = kwargs
            return type(
                "Response",
                (),
                {
                    "choices": [
                        type(
                            "Choice",
                            (),
                            {
                                "message": type(
                                    "Message",
                                    (),
                                    {
                                        "content": """
                                        ```json
                                        {"items":[
                                          {
                                            "title":"Interstellar",
                                            "description":"A science fiction film about wormholes, time dilation, and family bonds.",
                                            "genres":["Science Fiction","Adventure"],
                                            "themes":["space exploration","time"],
                                            "mood":["awe"],
                                            "storytelling_style":["epic"],
                                            "pacing":"Medium",
                                            "release_year":"2014",
                                            "content_type":"Movie",
                                            "poster_url":"https://img.test/poster.jpg"
                                          },
                                          {
                                            "title":"Wrong Type",
                                            "description":"This should be filtered.",
                                            "content_type":"book"
                                          }
                                        ]}
                                        ```
                                        """,
                                    },
                                )()
                            },
                        )()
                    ]
                },
            )()

    completions = FakeCompletions()
    fake_groq = type("FakeGroq", (), {"chat": type("FakeChat", (), {"completions": completions})()})()
    monkeypatch.setattr("app.services.online_discovery.ai_service.groq", fake_groq)

    results = await service.search("thoughtful aliens", "movie", 5)

    assert completions.kwargs["model"] == "groq/compound-mini"
    assert results == [
        {
            "title": "Interstellar",
            "description": "A science fiction film about wormholes, time dilation, and family bonds.",
            "genres": ["Science Fiction", "Adventure"],
            "themes": ["space exploration", "time"],
            "mood": ["awe"],
            "storytelling_style": ["epic"],
            "pacing": "medium",
            "release_year": 2014,
            "content_type": "movie",
            "poster_url": "https://img.test/poster.jpg",
        }
    ]


@pytest.mark.asyncio
async def test_search_returns_empty_without_groq(monkeypatch: pytest.MonkeyPatch) -> None:
    service = OnlineDiscoveryService()
    monkeypatch.setattr("app.services.online_discovery.ai_service.groq", None)

    results = await service.search("thoughtful aliens", None, 5)

    assert results == []
