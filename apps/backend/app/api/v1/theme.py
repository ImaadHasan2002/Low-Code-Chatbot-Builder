from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...core.security import get_current_user
from ...models.theme import Theme, ThemeUpdate
from ...models.user import UserInDB
from ...models.workspace import Workspace

router = APIRouter()


async def _get_workspace_or_404(workspace_id: str) -> Workspace:
    if not ObjectId.is_valid(workspace_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace id"
        )
    workspace = await Workspace.get(ObjectId(workspace_id))
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )
    return workspace


@router.get("/", response_model=Theme)
async def get_theme(
    workspace_id: str = Query(...),
    # NOTE: intentionally public so the embeddable chat widget can load the
    # theme without auth. Consider a scoped public token for production.
) -> Theme:
    """Get the theme for a workspace."""
    workspace = await _get_workspace_or_404(workspace_id)
    theme = None
    if workspace.theme_config_id:
        theme = await Theme.get(workspace.theme_config_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found"
        )
    return theme


@router.post("/", response_model=Theme)
async def create_theme(
    theme: ThemeUpdate,
    workspace_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_user),
) -> Theme:
    """Create a theme for a workspace and link it."""
    workspace = await _get_workspace_or_404(workspace_id)

    theme_doc = Theme(**theme.model_dump(exclude_unset=True))
    await theme_doc.insert()

    workspace.theme_config_id = theme_doc.id
    await workspace.save()

    return theme_doc


@router.put("/", response_model=Theme)
async def update_theme(
    theme: ThemeUpdate,
    workspace_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_user),
) -> Theme:
    """Update the workspace's theme (creates one if missing)."""
    workspace = await _get_workspace_or_404(workspace_id)

    theme_doc = None
    if workspace.theme_config_id:
        theme_doc = await Theme.get(workspace.theme_config_id)

    if not theme_doc:
        theme_doc = Theme(**theme.model_dump(exclude_unset=True))
        await theme_doc.insert()
        workspace.theme_config_id = theme_doc.id
        await workspace.save()
        return theme_doc

    for field, value in theme.model_dump(exclude_unset=True).items():
        setattr(theme_doc, field, value)
    await theme_doc.save()
    return theme_doc
