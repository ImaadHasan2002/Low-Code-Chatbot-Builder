from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId

from ...models.workspace import Workspace, WorkspaceCreate
from ...models.advanced_config import AdvancedConfig
from ...core.security import get_current_user
from ...models.user import UserInDB

router = APIRouter()

@router.post("/", response_model=Workspace)
async def create_workspace(
    workspace: WorkspaceCreate,
    current_user: UserInDB = Depends(get_current_user)
) -> Workspace:
    """Create a new workspace with default AdvancedConfig."""
    print(f"Creating workspace: {workspace}")   
    try:
        # TODO: Check if workspace name is already taken given the owner_id
        workspace_doc = Workspace(
            name=workspace.name,
            owner_id=current_user.id,
            members=[current_user.id]
        )
        await workspace_doc.insert()

        # Auto-create default AdvancedConfig for this workspace
        default_config = AdvancedConfig(workspace_id=workspace_doc.id)
        await default_config.save()
        workspace_doc.advanced_config_id = default_config.id
        await workspace_doc.save()

        return workspace_doc
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
        # Find workspaces where user is either owner or member
        workspaces = await Workspace.find(
            {
                "$or": [
                    {"members": current_user.id}
                ]
            }
        ).to_list()
        return workspaces
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
        
        # Check if user has access to workspace
        if current_user.id not in workspace.members and workspace.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return workspace
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workspace: {str(e)}"
        )

@router.put("/{workspace_id}", response_model=Workspace)
async def update_workspace(
    workspace_id: str,
    workspace_update: Workspace,
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
        
        # Only owner can update workspace
        if workspace.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owner can update workspace"
            )
        
        workspace.name = workspace_update.name
        await workspace.save()
        return workspace
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
        
        # Only owner can add members
        if workspace.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owner can add members"
            )
        
        # Add member if not already in workspace
        member_id = ObjectId(user_id)
        if member_id not in workspace.members:
            workspace.members.append(member_id)
            await workspace.save()
        
        return {"message": "Member added successfully"}
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
        
        # Only owner can remove members
        if workspace.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owner can remove members"
            )
        
        # Cannot remove owner
        member_id = ObjectId(user_id)
        if member_id == workspace.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove workspace owner"
            )
        
        # Remove member if in workspace
        if member_id in workspace.members:
            workspace.members.remove(member_id)
            await workspace.save()
        
        return {"message": "Member removed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove member: {str(e)}"
        )
