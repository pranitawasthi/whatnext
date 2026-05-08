from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.content import ContentRepository
from app.schemas.content import ContentWithScore
from app.schemas.recommendation import SearchRequest, SearchResponse
from app.services.ai import ai_service
from app.services.online_discovery import online_discovery

router = APIRouter()


@router.post("", response_model=SearchResponse)
async def semantic_search(payload: SearchRequest, db: AsyncSession = Depends(get_db)) -> dict:
    keywords = online_discovery.extract_keywords(payload.query)
    internet_count = 0
    if payload.include_internet:
        imported, keywords = await online_discovery.search_and_import(
            db, 
            payload.query,
            payload.content_type,
            max(6, payload.limit // 2),
        )
        internet_count = len(imported)

    embedding = await ai_service.embed_text(payload.query)
    rows = await ContentRepository(db).vector_search(embedding, payload.limit, payload.content_type)
    items = [
        {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "genres": item.genres,
            "themes": item.themes,
            "mood": item.mood,
            "storytelling_style": item.storytelling_style,
            "pacing": item.pacing,
            "release_year": item.release_year,
            "content_type": item.content_type,
            "poster_url": item.poster_url,
            "score": score,
        }
        for item, score in rows
    ]
    return {
        "keywords": keywords,
        "items": items,
        "local_count": max(len(items) - internet_count, 0),
        "internet_count": internet_count,
    }
    