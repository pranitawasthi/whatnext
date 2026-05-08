from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.recommendation import Recommendation


class RecommendationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_user(self, user_id: str, limit: int) -> list[Recommendation]:
        stmt = (
            select(Recommendation)
            .where(Recommendation.user_id == user_id)
            .options(selectinload(Recommendation.content))
            .order_by(Recommendation.score.desc())
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def replace_for_user(self, user_id: str, rows: list[dict]) -> None:
        await self.db.execute(delete(Recommendation).where(Recommendation.user_id == user_id))
        if rows:
            self.db.add_all([Recommendation(**row) for row in rows])
