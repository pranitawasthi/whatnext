from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.routes import auth, content, interactions, recommendations, search
from app.core.config import settings
from app.db.session import engine
from app.models import Base
from app.services.vector_store import vector_store


app = FastAPI(
    title="WhatNext AI Recommendations API",
    version="0.1.0",
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await vector_store.ensure_collection()

  
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(interactions.router, prefix="/api/interactions", tags=["interactions"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
