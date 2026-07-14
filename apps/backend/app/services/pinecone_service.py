from typing import List, Optional
from ..core.config import get_settings

settings = get_settings()


class PineconeNotConfiguredError(RuntimeError):
    """Raised when Pinecone is used without credentials configured."""

    def __init__(self):
        super().__init__(
            "Pinecone is not configured. Set PINECONE_API_KEY and "
            "PINECONE_INDEX_NAME (or PINECONE_HOST) in your .env file."
        )


class PineconeService:
    """Thin wrapper around the Pinecone client.

    The client is created lazily so that the application can boot (and
    unrelated features keep working) even when Pinecone credentials are
    missing. Any vector operation without credentials raises
    PineconeNotConfiguredError with a clear message instead of an opaque
    crash at import time.
    """

    def __init__(self):
        self._client = None
        self._index = None
        self._ensured_index = False

    @property
    def is_configured(self) -> bool:
        return bool(settings.PINECONE_API_KEY and (settings.PINECONE_HOST or settings.PINECONE_INDEX_NAME))

    def ensure_index(self, dimension: int = 1024, metric: str = "cosine") -> None:
        """Create the configured serverless index if it does not exist.

        Makes the app self-bootstrapping: a fresh Pinecone account does not
        need the index pre-created in the console. No-op when connecting by
        host (the index already exists) or when already verified this session.
        """
        if self._ensured_index or settings.PINECONE_HOST or not settings.PINECONE_INDEX_NAME:
            self._ensured_index = True
            return

        name = settings.PINECONE_INDEX_NAME
        try:
            existing = {idx["name"] for idx in self.client.list_indexes()}
        except Exception:
            # If listing fails, fall through and let the upsert surface a
            # clearer error rather than masking it here.
            return

        if name not in existing:
            from pinecone import ServerlessSpec

            cloud = settings.PINECONE_CLOUD or "aws"
            region = settings.PINECONE_REGION or "us-east-1"
            self.client.create_index(
                name=name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(cloud=cloud, region=region),
            )
            # Reset the cached index handle so it binds to the new index.
            self._index = None

        self._ensured_index = True

    @property
    def client(self):
        if self._client is None:
            if not settings.PINECONE_API_KEY:
                raise PineconeNotConfiguredError()
            from pinecone import Pinecone  # imported lazily

            self._client = Pinecone(api_key=settings.PINECONE_API_KEY)
        return self._client

    @property
    def index(self):
        if self._index is None:
            if settings.PINECONE_HOST:
                self._index = self.client.Index(host=settings.PINECONE_HOST)
            elif settings.PINECONE_INDEX_NAME:
                self._index = self.client.Index(settings.PINECONE_INDEX_NAME)
            else:
                raise PineconeNotConfiguredError()
        return self._index

    def upsert(
        self,
        namespace: str,
        embeddings: List[List[float]],
        knowledge_base_id: str,
        texts: Optional[List[str]] = None,
    ):
        """Upsert embeddings into Pinecone.

        Each vector gets a unique id derived from the knowledge base id so
        that multiple chunks do not overwrite each other, and the source
        text is stored as metadata so retrieval can return readable context.
        """
        records = []
        for i, e in enumerate(embeddings):
            metadata = {"knowledge_base_id": str(knowledge_base_id)}
            if texts and i < len(texts):
                metadata["source_text"] = texts[i]
            records.append(
                {
                    "id": f"{knowledge_base_id}#{i}",
                    "values": e,
                    "metadata": metadata,
                }
            )

        if records:
            self.index.upsert(namespace=namespace, vectors=records)
        return len(records)

    def query(self, namespace: str, vector: List[float], top_k: int = 10):
        """Query Pinecone with an embedding vector."""
        return self.index.query(
            namespace=namespace,
            vector=vector,
            top_k=top_k,
            include_metadata=True,
        )

    def delete_from_pinecone(self, namespace: str, document_id: str):
        """Delete all vectors belonging to a knowledge base document."""
        try:
            # Delete by metadata filter (covers chunked ids like "<id>#3")
            self.index.delete(
                namespace=namespace,
                filter={"knowledge_base_id": {"$eq": str(document_id)}},
            )
        except Exception:
            # Serverless indexes don't support metadata-filter deletes;
            # fall back to id-prefix listing.
            ids = [
                vec_id
                for page in self.index.list(prefix=f"{document_id}#", namespace=namespace)
                for vec_id in page
            ]
            if ids:
                self.index.delete(namespace=namespace, ids=ids)

    # Backwards-compatible alias (old private name used elsewhere)
    _delete_from_pinecone = delete_from_pinecone
