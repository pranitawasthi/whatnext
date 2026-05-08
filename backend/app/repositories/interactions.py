from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interaction import UserInteraction


class InteractionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert(self, user_id: str, content_id: str, rating: int | None, status: str) -> UserInteraction:
        stmt = select(UserInteraction).where(
            UserInteraction.user_id == user_id,
            UserInteraction.content_id == content_id,
        )
        interaction = (await self.db.execute(stmt)).scalar_one_or_none()
        if interaction is None:
            interaction = UserInteraction(user_id=user_id, content_id=content_id, rating=rating, status=status)
            self.db.add(interaction)
        else:
            interaction.rating = rating
            interaction.status = status
        await self.db.flush()
        return interaction

    async def list_for_user(self, user_id: str) -> list[UserInteraction]:
        stmt = (
            select(UserInteraction)
            .where(UserInteraction.user_id == user_id)
            .options(selectinload(UserInteraction.content))
            .order_by(UserInteraction.updated_at.desc())
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def consumed_for_user(self, user_id: str) -> list[UserInteraction]:
        stmt = (
            select(UserInteraction)
            .where(UserInteraction.user_id == user_id)
            .where(UserInteraction.status.in_(["favorite", "liked", "watched", "read"]))
            .options(selectinload(UserInteraction.content))
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def taste_profile_for_user(self, user_id: str) -> list[UserInteraction]:
        stmt = (
            select(UserInteraction)
            .where(UserInteraction.user_id == user_id)
            .where(UserInteraction.status.in_(["favorite", "liked", "watched", "read", "want_to_watch", "want_to_read"]))
            .options(selectinload(UserInteraction.content))
        )
        return list((await self.db.execute(stmt)).scalars().all())
