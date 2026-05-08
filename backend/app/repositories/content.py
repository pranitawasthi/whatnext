from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content
from app.services.vector_store import vector_store


class ContentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def create(self, content: Content) -> Content:
        self.db.add(content)
        await self.db.flush()
        await vector_store.upsert_content(content)
        return content

    async def get(self, content_id: str) -> Content | None:
        return await self.db.get(Content, content_id)

    async def find_existing(self, title: str, content_type: str, release_year: int | None = None) -> Content | None:
        stmt = select(Content).where(
            func.lower(Content.title) == title.lower(),
            Content.content_type == content_type,
        )
        if release_year:
            stmt = stmt.where(or_(Content.release_year == release_year, Content.release_year.is_(None)))
        result = await self.db.execute(stmt.limit(1))
        return result.scalar_one_or_none()

    async def list_content(
        self,
        page: int,
        page_size: int,
        content_type: str | None = None,
    ) -> tuple[list[Content], int]:
        stmt = select(Content)
        count_stmt = select(func.count()).select_from(Content)

        if content_type:
            stmt = stmt.where(Content.content_type == content_type)
            count_stmt = count_stmt.where(Content.content_type == content_type)

        stmt = stmt.order_by(Content.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list((await self.db.execute(stmt)).scalars().all())
        total = int((await self.db.execute(count_stmt)).scalar_one())
        return items, total

    async def vector_search(
        self,
        embedding: list[float],
        limit: int,
        content_type: str | None = None,
        exclude_ids: list[str] | None = None,
    ) -> list[tuple[Content, float]]:
        matches = await vector_store.search_content(embedding, limit, content_type, exclude_ids)
        if not matches:
            return []

        scores_by_id = dict(matches)
        ids = list(scores_by_id.keys())
        stmt = select(Content).where(Content.id.in_(ids))
        rows = list((await self.db.execute(stmt)).scalars().all())
        content_by_id = {item.id: item for item in rows}
        return [(content_by_id[item_id], score) for item_id, score in matches if item_id in content_by_id]
