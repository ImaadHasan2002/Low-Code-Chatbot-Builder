from pinecone import Pinecone
from typing import List
from ..core.config import get_settings

settings = get_settings()

class PineconeService:
    def __init__(self):
        self.pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pinecone_client.Index(host=settings.PINECONE_HOST)

    def upsert(self, namespace: str, embeddings: List[List[float]], knowledge_base_id: str):
        """Upsert embeddings into Pinecone"""
        records = []
        
        for e in embeddings:
            records.append({
                "id": knowledge_base_id,
                "values": e,
                # TODO: Add metadata
                # "metadata": {
                #     "source_text": d.page_content,
                #     "category": workspace_id
                # }
            })
        
        # Upload to Pinecone
        self.pinecone_service.upsert(vectors=records, namespace=workspace_id)
        self.index.upsert(
            namespace=namespace,
            vectors=records
        )

    def query(self, namespace: str, query: str, top_k: int = 10):
        """Query Pinecone"""
        return self.index.query(
            namespace=namespace,
            query=query,
            top_k=top_k
        )

    def _delete_from_pinecone(self, namespace: str, document_id: str):
        """Delete embeddings from Pinecone"""
        self.index.delete(
            namespace=namespace,
            ids=[document_id]
        )