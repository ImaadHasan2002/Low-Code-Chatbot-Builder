import asyncio

import pytest
import pytest_asyncio
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.models.advanced_config import AdvancedConfig
from app.models.background_job import BackgroundJob
from app.models.conversation import Conversation
from app.models.knowledge_base import KnowledgeBase
from app.models.theme import Theme
from app.models.user import UserInDB
from app.models.workspace import Workspace

DOCUMENT_MODELS = [
    UserInDB,
    Workspace,
    Conversation,
    KnowledgeBase,
    AdvancedConfig,
    Theme,
    BackgroundJob,
]


@pytest_asyncio.fixture()
async def client():
    """HTTP client backed by an in-memory MongoDB (no external services)."""
    mock_client = AsyncMongoMockClient()
    await init_beanie(
        database=mock_client["test_db"], document_models=DOCUMENT_MODELS
    )
    app.mongodb_client = mock_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture()
async def auth_client(client):
    """Client with a signed-up + logged-in user (cookies set)."""
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "test@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200, resp.text
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200, resp.text
    return client
