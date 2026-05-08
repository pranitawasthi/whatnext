from pydantic import BaseModel, Field


class ContentBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=12)
    genres: list[str] = []
    themes: list[str] = []
    mood: list[str] = []
    storytelling_style: list[str] = []
    pacing: str = "medium"
    release_year: int | None = Field(default=None, ge=0, le=2200)
    content_type: str = Field(pattern="^(book|movie|tv)$")
    poster_url: str | None = None


class ContentCreate(ContentBase):
    pass


class ContentRead(ContentBase):
    id: str

    model_config = {"from_attributes": True}


class ContentWithScore(ContentRead):
    score: float | None = None
    explanation: str | None = None
