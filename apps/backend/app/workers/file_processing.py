"""Celery worker for background file processing.

docker-compose runs: celery -A app.workers.file_processing worker
This module must therefore expose a Celery application object.
"""

import os

from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

celery_app = Celery(
    "botcraft",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)

# Celery looks for an attribute named `celery` or `app` with `-A module`
app = celery_app


@celery_app.task(name="app.workers.file_processing.process_file")
def process_file(knowledge_base_id: str, workspace_id: str, file_url: str) -> dict:
    """Parse a file and store embeddings asynchronously.

    Runs the same pipeline as the synchronous upload path, but off the
    request thread. Useful for large PDFs.
    """
    from app.services.langchain_service import LangChainService

    service = LangChainService()
    documents = service.parse_document(file_url)
    for doc in documents:
        doc.metadata.update(
            {"workspace_id": str(workspace_id), "knowledge_base_id": str(knowledge_base_id)}
        )
    service.create_embeddings(documents, str(workspace_id), knowledge_base_id=str(knowledge_base_id))
    return {"status": "completed", "chunks": len(documents)}
