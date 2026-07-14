from pathlib import Path

import certifi
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .models.user import UserInDB
from .models.workspace import Workspace
from .models.conversation import Conversation
from .models.knowledge_base import KnowledgeBase
from .models.advanced_config import AdvancedConfig
from .models.theme import Theme
from .models.background_job import BackgroundJob
from .core.config import get_settings
from .api.v1 import auth, knowledge_base, playground, workspaces, script, advanced_config, theme, chatbot, background_job, conversations

settings = get_settings()
LOCAL_UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
LOCAL_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHATBOT_SCRIPT_PATH = Path(__file__).resolve().parent / "static" / "chatbot.js"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Atlas/mongodb+srv connections use TLS. On macOS the system Python often
    # has no CA bundle, so verification fails with CERTIFICATE_VERIFY_FAILED.
    # Point the driver at certifi's bundle for any TLS-based connection.
    client_kwargs = {"serverSelectionTimeoutMS": 5000}
    if "mongodb+srv://" in settings.MONGODB_URL or "tls=true" in settings.MONGODB_URL.lower() or "ssl=true" in settings.MONGODB_URL.lower():
        client_kwargs["tlsCAFile"] = certifi.where()
    client = AsyncIOMotorClient(settings.MONGODB_URL, **client_kwargs)
    app.mongodb_client = client
    try:
        await init_beanie(
            database=client[settings.DATABASE_NAME],
            document_models=[UserInDB, Workspace, Conversation, KnowledgeBase, AdvancedConfig, Theme, BackgroundJob],
        )
        print(f"Successfully connected to MongoDB database '{settings.DATABASE_NAME}'")
    except Exception as e:
        # Boot in degraded mode so /health can report the problem instead of
        # the whole API crash-looping when the database is unreachable.
        print(f"WARNING: could not initialise MongoDB ({e}). API starting in degraded mode.")
    yield
    client.close()
    print("MongoDB connection closed")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS (origins configurable via CORS_ORIGINS env var, comma-separated)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def public_embed_cors(request: Request, call_next):
    response = await call_next(request)
    if request.url.path in {
        "/chatbot.js",
        f"{settings.API_V1_STR}/theme",
        f"{settings.API_V1_STR}/theme/",
    }:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
    return response


app.mount("/uploads", StaticFiles(directory=str(LOCAL_UPLOAD_DIR)), name="uploads")

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(knowledge_base.router, prefix=f"{settings.API_V1_STR}/knowledge-base", tags=["knowledge-base"])
app.include_router(playground.router, prefix=f"{settings.API_V1_STR}/playground", tags=["playground"])
app.include_router(workspaces.router, prefix=f"{settings.API_V1_STR}/workspaces", tags=["workspaces"])
app.include_router(script.router, prefix=f"{settings.API_V1_STR}/script", tags=["script"])
app.include_router(advanced_config.router, prefix=f"{settings.API_V1_STR}/advanced-config", tags=["advanced-config"])
app.include_router(theme.router, prefix=f"{settings.API_V1_STR}/theme", tags=["theme"])
app.include_router(chatbot.router, prefix=f"{settings.API_V1_STR}/chatbot", tags=["chatbot"])
app.include_router(background_job.router, prefix=f"{settings.API_V1_STR}/background-job", tags=["background-job"])
app.include_router(conversations.router, prefix=f"{settings.API_V1_STR}/conversations", tags=["conversations"])

@app.get("/")
async def root():
    return {"message": "Welcome to AI Chatbot API"}


@app.get("/chatbot.js", include_in_schema=False)
async def chatbot_script():
    """Serve the embeddable widget from the backend origin."""
    if not CHATBOT_SCRIPT_PATH.exists():
        return Response("console.error('BotCraft chatbot script missing');", media_type="application/javascript")
    return FileResponse(
        CHATBOT_SCRIPT_PATH,
        media_type="application/javascript; charset=utf-8",
        headers={"Cache-Control": "public, max-age=300"},
    )


@app.get("/health")
async def health():
    """Liveness/readiness probe for deployments and docker-compose."""
    status = {"status": "ok", "mongo": False}
    try:
        await app.mongodb_client.admin.command("ping")
        status["mongo"] = True
    except Exception:
        status["status"] = "degraded"
    return status
