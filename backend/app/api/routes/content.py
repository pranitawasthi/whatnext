from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.content import Content
from app.models.user import User
from app.repositories.content import ContentRepository
from app.schemas.common import PaginatedResponse
from app.schemas.content import ContentCreate, ContentRead
from app.services.ai import ai_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ContentRead])
async def list_content(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    content_type: str | None = Query(default=None, pattern="^(book|movie|tv)$"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    items, total = await ContentRepository(db).list_content(page, page_size, content_type)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{content_id}", response_model=ContentRead)
async def get_content(content_id: str, db: AsyncSession = Depends(get_db)) -> Content:
    item = await ContentRepository(db).get(content_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    return item


@router.post("", response_model=ContentRead, status_code=201)
async def create_content(
    payload: ContentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Content:
    repo = ContentRepository(db)
    data = payload.model_dump()
    data["embedding"] = await ai_service.embed_content_payload(data)
    item = await repo.create(Content(**data))
    await db.commit()
    return item
