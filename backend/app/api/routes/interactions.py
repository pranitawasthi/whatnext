from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.content import ContentRepository
from app.repositories.interactions import InteractionRepository
from app.schemas.interaction import InteractionRead, InteractionUpsert

router = APIRouter()


@router.get("", response_model=list[InteractionRead])
async def list_interactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    return await InteractionRepository(db).list_for_user(current_user.id)


@router.put("", response_model=InteractionRead)
async def upsert_interaction(
    payload: InteractionUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if await ContentRepository(db).get(payload.content_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    interaction = await InteractionRepository(db).upsert(
        current_user.id,
        payload.content_id,
        payload.rating,
        payload.status,
    )
    await db.commit()
    interactions = await InteractionRepository(db).list_for_user(current_user.id)
    return next(item for item in interactions if item.id == interaction.id)
