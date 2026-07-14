from typing import Optional

from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_user, get_current_workspace_id
from app.core.config import Settings

settings = Settings()

router = APIRouter()

@router.post("/generate")
async def generate_script(workspace_id: str = Depends(get_current_workspace_id)):
    script_template = (
        f'<script src="{settings.BACKEND_URL.rstrip("/")}/chatbot.js" '
        f'data-workspace-id="{workspace_id}" async></script>'
    )
    return {"script": script_template}


@router.get("/embed-code")
async def get_embed_code(
    workspace_id: Optional[str] = Query(default=None),
    current_workspace_id: str = Depends(get_current_workspace_id),
):
    resolved_workspace_id = workspace_id or current_workspace_id
    return {
        "script": (
            f'<script src="{settings.BACKEND_URL.rstrip("/")}/chatbot.js" '
            f'data-workspace-id="{resolved_workspace_id}" async></script>'
        )
    }
