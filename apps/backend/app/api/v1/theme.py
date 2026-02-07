from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from bson import ObjectId
from ...models.theme import Theme
from ...models.user import UserInDB
from ...models.workspace import Workspace
from ...core.security import get_current_user

router = APIRouter()


@router.get("/", response_model=Theme)
async def get_theme(
    workspace_id: str = Query(...),

    # TODO: removing it temporarily later provide publlic api with access token
    # current_user: UserInDB = Depends(get_current_user)
) -> Theme:
    """Get a theme by ID."""
    try:
        workspace = await Workspace.find_one(Workspace.id == ObjectId(workspace_id))
        theme = await Theme.find_one(Theme.id == workspace.theme_config_id)
        if not theme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Theme not found"
            )
        return theme
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get theme: {str(e)}"
        )


@router.post("/", response_model=Theme)
async def create_theme(
    workspace_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_user)
) -> Theme:
    """Create a new theme."""
    try:
        theme_doc = Theme(
            theme=theme.theme,
            position=theme.position,
            primary_color=theme.primary_color, 
            secondary_color=theme.secondary_color,
            text_color=theme.text_color,
            header_text=theme.header_text,
            input_placeholder=theme.input_placeholder,
            width=theme.width,
            height=theme.height,
            border_radius=theme.border_radius,
            launcher=theme.launcher,
            show_header=theme.show_header
        )
        theme = await theme_doc.insert()
        workspace = await Workspace.find_one(Workspace.id == ObjectId(workspace_id))
        workspace.themeId = theme.id
        await workspace.save()

        return theme_doc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create theme: {str(e)}"
        )


@router.put("/", response_model=Theme)
async def update_theme(
    theme: Theme,
    workspace_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_user)
) -> Theme:
    """Update a theme by ID."""
    try:
        workspace = await Workspace.find_one(Workspace.id == ObjectId(workspace_id))
        theme_doc = await Theme.find_one(Theme.id == workspace.theme_config_id)
        if not theme_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Theme not found"
            )
        theme_doc.update(theme.model_dump())
        await theme_doc.save()
        return theme_doc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update theme: {str(e)}"
        )
    
