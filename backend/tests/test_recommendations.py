from types import SimpleNamespace

import pytest

from app.models.content import Content
from app.models.interaction import UserInteraction
from app.services.recommendations import RecommendationService


def interaction(status: str, rating: int | None, embedding: list[float], title: str = "Item") -> UserInteraction:
    return SimpleNamespace(
        status=status,
        rating=rating,
        content=SimpleNamespace(
            title=title,
            embedding=embedding,
            genres=["science fiction"],
            themes=["identity"],
            mood=["dark"],
            storytelling_style=["slow burn"],
        ),
    )


def test_interaction_weight_includes_watchlist_statuses() -> None:
    service = RecommendationService(db=None)

    assert service._interaction_weight(interaction("favorite", 10, [1.0, 0.0])) == pytest.approx(6.0)
    assert service._interaction_weight(interaction("liked", 8, [1.0, 0.0])) == pytest.approx(3.6)
    assert service._interaction_weight(interaction("want_to_watch", None, [1.0, 0.0])) == pytest.approx(0.8)
    assert service._interaction_weight(interaction("dropped", 1, [1.0, 0.0])) == pytest.approx(0.1)


def test_build_user_embedding_weighted_average_is_normalized() -> None:
    service = RecommendationService(db=None)

    vector = service.build_user_embedding(
        [
            interaction("favorite", 10, [1.0, 0.0]),
            interaction("watched", 5, [0.0, 1.0]),
        ]
    )

    assert vector is not None
    assert vector[0] > vector[1]
    assert sum(value * value for value in vector) == pytest.approx(1.0)


def test_build_user_embedding_returns_none_without_vectors() -> None:
    service = RecommendationService(db=None)

    assert service.build_user_embedding([interaction("favorite", 10, [])]) is None


def test_taste_keywords_include_watchlist_content() -> None:
    service = RecommendationService(db=None)

    keywords = service._taste_keywords([interaction("want_to_watch", None, [1.0], title="Severance")])

    assert "severance" in keywords
    assert "identity" in keywords


def test_content_to_dict_preserves_recommendation_payload_shape() -> None:
    service = RecommendationService(db=None)
    content = Content(
        id="content-1",
        title="Arrival",
        description="A linguist meets alien visitors.",
        genres=["science fiction"],
        themes=["language"],
        mood=["meditative"],
        storytelling_style=["nonlinear"],
        pacing="measured",
        release_year=2016,
        content_type="movie",
        poster_url="https://example.test/arrival.jpg",
        embedding=[0.1, 0.2],
    )

    payload = service._content_to_dict(content)

    assert payload == {
        "id": "content-1",
        "title": "Arrival",
        "description": "A linguist meets alien visitors.",
        "genres": ["science fiction"],
        "themes": ["language"],
        "mood": ["meditative"],
        "storytelling_style": ["nonlinear"],
        "pacing": "measured",
        "release_year": 2016,
        "content_type": "movie",
        "poster_url": "https://example.test/arrival.jpg",
    }
