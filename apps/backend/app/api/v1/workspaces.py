from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from typing import List
from bson import ObjectId

from ...models.workspace import Workspace, WorkspaceCreate
from ...models.advanced_config import AdvancedConfig
from ...models.theme import Theme
from ...core.security import get_current_user
from ...models.user import UserInDB
from ...services.background_job_service import BackgroundJobService
from ...services.knowledge_base_service import KnowledgeBaseService

router = APIRouter()

@router.post("/", response_model=Workspace)
async def create_workspace(
    workspace: WorkspaceCreate,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user)
) -> Workspace:
    """Create a new workspace with default AdvancedConfig and Theme."""
    try:
        workspace_doc = Workspace(
            name=workspace.name,
            owner_id=current_user.id,
            members=[current_user.id]
        )
        await workspace_doc.insert()

        # Auto-create default AdvancedConfig and Theme for this workspace
        default_config = AdvancedConfig(workspace_id=workspace_doc.id)
        await default_config.insert()

        default_theme = Theme()
        await default_theme.insert()

        workspace_doc.advanced_config_id = default_config.id
        workspace_doc.theme_config_id = default_theme.id
        await workspace_doc.save()

        if workspace.website_url:
            job = await BackgroundJobService().create_job(
                "website_crawl",
                str(current_user.id),
                str(workspace_doc.id),
                payload={
                    "base_url": workspace.website_url,
                    "max_pages": workspace.crawl_max_pages,
                    "max_depth": workspace.crawl_max_depth,
                    "include_paths": workspace.crawl_include_paths,
                    "exclude_paths": workspace.crawl_exclude_paths,
                },
            )
            kb_service = KnowledgeBaseService(workspace_id=workspace_doc.id)
            background_tasks.add_task(
                kb_service.run_crawl_job,
                job_id=str(job.id),
                workspace_id=str(workspace_doc.id),
                base_url=workspace.website_url,
                max_pages=workspace.crawl_max_pages,
                max_depth=workspace.crawl_max_depth,
                include_paths=workspace.crawl_include_paths,
                exclude_paths=workspace.crawl_exclude_paths,
            )

        return workspace_doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workspace: {str(e)}"
        )

@router.get("/", response_model=List[Workspace])
async def get_workspaces(
    current_user: UserInDB = Depends(get_current_user)
) -> List[Workspace]:
    """Get all workspaces for the current user."""
    try:
        workspaces = await Workspace.find(
            {"members": current_user.id}
        ).to_list()
        return workspaces
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workspaces: {str(e)}"
        )

@router.get("/{workspace_id}", response_model=Workspace)
async def get_workspace(
    workspace_id: str,
    current_user: UserInDB = Depends(get_current_user)
) -> Workspace:
    """Get a specific workspace by ID."""
    try:
        workspace = await Workspace.get(ObjectId(workspace_id))
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        if current_user.id not in workspace.members and workspace.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return workspace
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workspace: {str(e)}"
        )

@router.put("/{workspace_id}", response_model=Workspace)
async def update_workspace(
    workspace_id: str,
    workspace_update: WorkspaceCreate,
    current_user: UserInDB = Depends(get_current_user)
) -> Workspace:
    """Update a workspace."""
    try:
        workspace = await Workspace.get(ObjectId(workspace_id))
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        if workspace.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owner can update workspace"
            )

        workspace.name = workspace_update.name
        await workspace.save()
        return workspace
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workspace: {str(e)}"
        )

@router.post("/{workspace_id}/members/{user_id}")
async def add_member(
    workspace_id: str,
    user_id: str,
    current_user: UserInDB = Depends(get_current_user)
) -> dict:
    """Add a member to the workspace."""
    try:
        workspace = await Workspace.get(ObjectId(workspace_id))
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        if workspace.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owner can add members"
            )

        member_id = ObjectId(user_id)
        if member_id not in workspace.members:
            workspace.members.append(member_id)
            await workspace.save()

        return {"message": "Member added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add member: {str(e)}"
        )

@router.delete("/{workspace_id}/members/{user_id}")
async def remove_member(
    workspace_id: str,
    user_id: str,
    current_user: UserInDB = Depends(get_current_user)
) -> dict:
    """Remove a member from the workspace."""
    try:
        workspace = await Workspace.get(ObjectId(workspace_id))
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        if workspace.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owner can remove members"
            )

        member_id = ObjectId(user_id)
        if member_id == workspace.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove workspace owner"
            )

        if member_id in workspace.members:
            workspace.members.remove(member_id)
            await workspace.save()

        return {"message": "Member removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove member: {str(e)}"
        )
