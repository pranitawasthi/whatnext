from sqlalchemy import Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Recommendation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "recommendations"
    __table_args__ = (UniqueConstraint("user_id", "content_id", name="uq_user_content_recommendation"),)

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content_id: Mapped[str] = mapped_column(String(36), ForeignKey("content.id", ondelete="CASCADE"), index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    user = relationship("User", back_populates="recommendations")
    content = relationship("Content")
