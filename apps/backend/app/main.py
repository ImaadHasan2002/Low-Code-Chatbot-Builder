from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .models.user import UserInDB
from .models.workspace import Workspace
from .models.conversation import Conversation
from .models.knowledge_base import KnowledgeBase
from .models.advanced_config import AdvancedConfig
from .models.theme import Theme
from .core.config import get_settings
from .api.v1 import auth, knowledge_base, playground, workspaces, script, advanced_config, theme

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb_client = client
    await init_beanie(database=client.core_db, document_models=[UserInDB, Workspace, Conversation, KnowledgeBase, AdvancedConfig, Theme])
    print(f"Successfully connected to MongoDB at {settings.MONGODB_URL}")
    yield
    client.close()
    print("MongoDB connection closed")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-production-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["auth"]
)

app.include_router(
    knowledge_base.router,
    prefix=f"{settings.API_V1_STR}/knowledge-base",
    tags=["knowledge-base"]
)

app.include_router(
    playground.router,
    prefix=f"{settings.API_V1_STR}/playground",
    tags=["playground"]
)

app.include_router(
    workspaces.router,
    prefix=f"{settings.API_V1_STR}/workspaces",
    tags=["workspaces"]
)

app.include_router(
    script.router,
    prefix=f"{settings.API_V1_STR}/script",
    tags=["script"]
)

app.include_router(
    advanced_config.router,
    prefix=f"{settings.API_V1_STR}/advanced-config",
    tags=["advanced-config"]
)

app.include_router(
    theme.router,
    prefix=f"{settings.API_V1_STR}/theme",
    tags=["theme"]
)

@app.get("/")
async def root():
    return {"message": "Welcome to AI Chatbot API"}