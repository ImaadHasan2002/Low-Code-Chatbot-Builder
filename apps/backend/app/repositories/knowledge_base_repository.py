from typing import List, Optional
from bson import ObjectId
from beanie import PydanticObjectId

from ..models.knowledge_base import KnowledgeBase

class KnowledgeBaseRepository:
    @staticmethod
    async def create(knowledge_base: KnowledgeBase) -> KnowledgeBase:
        """Create a new knowledge base."""
        await knowledge_base.insert()
        return knowledge_base

    @staticmethod
    async def find_by_workspace(workspace_id: PydanticObjectId) -> List[KnowledgeBase]:
        """Find all knowledge bases by workspace ID."""
        return await KnowledgeBase.find(
            {"workspace_id": workspace_id}
        ).to_list()

    @staticmethod
    async def find_by_id(knowledge_base_id: PydanticObjectId) -> Optional[KnowledgeBase]:
        """Find knowledge base by ID."""
        return await KnowledgeBase.get(knowledge_base_id)

    @staticmethod
    async def update(knowledge_base: KnowledgeBase) -> KnowledgeBase:
        """Update knowledge base."""
        await knowledge_base.save()
        return knowledge_base
    
    @staticmethod
    async def delete(knowledge_base_id: PydanticObjectId) -> None:
        """Delete knowledge base."""
        await KnowledgeBase.find_one(
            {"_id": knowledge_base_id}
        ).delete()
    

