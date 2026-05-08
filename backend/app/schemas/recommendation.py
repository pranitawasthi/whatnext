from pydantic import BaseModel, Field

from app.schemas.content import ContentWithScore


class RecommendationRequest(BaseModel):
    limit: int = Field(default=12, ge=1, le=50)
    content_type: str | None = Field(default=None, pattern="^(book|movie|tv)$")
    refresh: bool = False


class RecommendationRead(ContentWithScore):
    pass


class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    limit: int = Field(default=12, ge=1, le=50)
    content_type: str | None = Field(default=None, pattern="^(book|movie|tv)$")
    include_internet: bool = True


class SearchResponse(BaseModel):
    keywords: list[str]
    items: list[ContentWithScore]
    local_count: int
    internet_count: int
