from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.users import UserRepository
from app.schemas.auth import TokenResponse, UserCreate, UserLogin


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)

    async def signup(self, payload: UserCreate) -> TokenResponse:
        existing = await self.users.get_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        user = await self.users.create(payload.email, payload.username, hash_password(payload.password))
        await self.db.commit()
        token = create_access_token(user.id)
        return TokenResponse(access_token=token, user=user)

    async def login(self, payload: UserLogin) -> TokenResponse:
        user = await self.users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        token = create_access_token(user.id)
        return TokenResponse(access_token=token, user=user)
