from typing import List, Optional
from bson import ObjectId
from beanie import PydanticObjectId

from ..models.workspace import Workspace

class WorkspaceRepository:
    @staticmethod
    async def create(workspace: Workspace) -> Workspace:
        """Create a new workspace."""
        await workspace.insert()
        return workspace
    
    @staticmethod
    async def find_by_user(user_id: PydanticObjectId) -> List[Workspace]:
        """Find all workspaces where user is owner or member."""
        return await Workspace.find(
            {
                "$or": [
                    {"owner_id": user_id},
                    {"members": user_id}
                ]
            }
        ).to_list()
    
    @staticmethod
    async def find_by_id(workspace_id: PydanticObjectId) -> Optional[Workspace]:
        """Find workspace by ID."""
        return await Workspace.get(workspace_id)
    
    @staticmethod
    async def update(workspace: Workspace) -> Workspace:
        """Update workspace."""
        await workspace.save()
        return workspace
