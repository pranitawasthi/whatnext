from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.recommendation import RecommendationRead, RecommendationRequest
from app.services.recommendations import RecommendationService

router = APIRouter()


@router.post("", response_model=list[RecommendationRead])
async def get_recommendations(
    payload: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return await RecommendationService(db).recommend(
        current_user.id,
        payload.limit,
        payload.content_type,
        payload.refresh,
    )
