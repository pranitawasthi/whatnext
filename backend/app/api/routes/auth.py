from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserRead
from app.services.auth import AuthService

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    return await AuthService(db).signup(payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    return await AuthService(db).login(payload)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
