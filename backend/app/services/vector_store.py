from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, HasIdCondition, MatchValue, PointStruct, VectorParams
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.models.content import Content


class VectorStore:
    def __init__(self) -> None:
        self.client = AsyncQdrantClient(url=settings.qdrant_url)
        self.collection_name = settings.qdrant_collection

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(5))
    async def ensure_collection(self) -> None:
        exists = await self.client.collection_exists(self.collection_name)
        if exists:
            return
        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=settings.embedding_dimensions, distance=Distance.COSINE),
        )

    async def upsert_content(self, content: Content) -> None:
        if not content.embedding:
            return
        await self.ensure_collection()
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=content.id,
                    vector=content.embedding,
                    payload={
                        "content_id": content.id,
                        "content_type": content.content_type,
                        "title": content.title,
                    },
                )
            ],
            wait=True,
        )

    async def search_content(
        self,
        embedding: list[float],
        limit: int,
        content_type: str | None = None,
        exclude_ids: list[str] | None = None,
    ) -> list[tuple[str, float]]:
        await self.ensure_collection()
        query_filter = self._build_filter(content_type, exclude_ids)
        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            query_filter=query_filter,
            limit=limit,
            with_payload=False,
        )
        return [(str(point.id), float(point.score)) for point in results]

    def _build_filter(self, content_type: str | None, exclude_ids: list[str] | None) -> Filter | None:
        must = []
        must_not = []
        if content_type:
            must.append(FieldCondition(key="content_type", match=MatchValue(value=content_type)))
        if exclude_ids:
            must_not.append(HasIdCondition(has_id=exclude_ids))
        if not must and not must_not:
            return None
        return Filter(must=must or None, must_not=must_not or None)


vector_store = VectorStore()
