from typing import List, Optional
from fastapi import HTTPException, status
from bson import ObjectId

from ..models.workspace import Workspace, WorkspaceCreate
from ..models.user import UserInDB
from ..repositories.workspace_repository import WorkspaceRepository

class WorkspaceService:
    def __init__(self):
        self.repository = WorkspaceRepository()

    async def create_workspace(self, workspace_data: WorkspaceCreate, user: UserInDB) -> Workspace:
        """Create a new workspace."""
        workspace = Workspace(
            name=workspace_data.name,
            owner_id=user.id,
            members=[user.id]
        )
        return await self.repository.create(workspace)

    async def get_workspace_by_user_id(self, user_id: str) -> Optional[Workspace]:
        """Get a workspace by user id."""
        try:
            workspace = await self.repository.find_by_user(user_id)
            print(f"Workspace: {workspace}")
            return workspace
        except Exception as e:
            print(f"Error getting workspace by user id: {str(e)}")

    async def get_user_workspaces(self, user: UserInDB) -> List[Workspace]:
        """Get all workspaces for a user."""
        return await self.repository.find_by_user(user.id)

    async def get_workspace_by_id(self, workspace_id: str) -> Workspace:
        """Get a workspace by id."""
        return await self.repository.find_by_id(ObjectId(workspace_id))

    async def get_workspace(self, workspace_id: str, user: UserInDB) -> Workspace:
        """Get a specific workspace."""
        workspace = await self.repository.find_by_id(ObjectId(workspace_id))
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        if user.id not in workspace.members and workspace.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return workspace

    async def update_workspace(self, workspace_id: str, workspace_data: WorkspaceCreate, user: UserInDB) -> Workspace:
        """Update a workspace."""
        workspace = await self.repository.find_by_id(ObjectId(workspace_id))
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        if workspace.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owner can update workspace"
            )
        
        workspace.name = workspace_data.name
        return await self.repository.update(workspace)

    async def add_member(self, workspace_id: str, member_id: str, user: UserInDB) -> Workspace:
        """Add a member to workspace."""
        workspace = await self.repository.find_by_id(ObjectId(workspace_id))
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        if workspace.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owner can add members"
            )
        
        member_obj_id = ObjectId(member_id)
        if member_obj_id not in workspace.members:
            workspace.members.append(member_obj_id)
            await self.repository.update(workspace)
        
        return workspace

    async def remove_member(self, workspace_id: str, member_id: str, user: UserInDB) -> Workspace:
        """Remove a member from workspace."""
        workspace = await self.repository.find_by_id(ObjectId(workspace_id))
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        if workspace.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owner can remove members"
            )
        
        member_obj_id = ObjectId(member_id)
        if member_obj_id == workspace.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove workspace owner"
            )
        
        if member_obj_id in workspace.members:
            workspace.members.remove(member_obj_id)
            await self.repository.update(workspace)
        
        return workspace
