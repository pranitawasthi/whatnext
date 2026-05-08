from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserInteraction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_interactions"
    __table_args__ = (
        UniqueConstraint("user_id", "content_id", name="uq_user_content_interaction"),
        CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 10)", name="ck_rating_range"),
    )

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content_id: Mapped[str] = mapped_column(String(36), ForeignKey("content.id", ondelete="CASCADE"), index=True)
    rating: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="watched", index=True)

    user = relationship("User", back_populates="interactions")
    content = relationship("Content", back_populates="interactions")
