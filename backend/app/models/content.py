from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Content(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "content"

    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    genres: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    themes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    mood: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    storytelling_style: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    pacing: Mapped[str] = mapped_column(String(80), default="medium", nullable=False)
    release_year: Mapped[int | None] = mapped_column(Integer)
    content_type: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    poster_url: Mapped[str | None] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(JSON)

    interactions = relationship("UserInteraction", back_populates="content", cascade="all, delete-orphan")
