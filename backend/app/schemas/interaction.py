from pydantic import BaseModel, Field

from app.schemas.content import ContentRead


class InteractionUpsert(BaseModel):
    content_id: str
    rating: int | None = Field(default=None, ge=1, le=10)
    status: str = Field(pattern="^(favorite|liked|watched|read|dropped|want_to_watch|want_to_read)$")


class InteractionRead(BaseModel):
    id: str
    rating: int | None
    status: str
    content: ContentRead

    model_config = {"from_attributes": True}
