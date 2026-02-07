from fastapi import HTTPException
from bson import ObjectId
from app.models.advanced_config import AdvancedConfig

class AdvancedConfigRepository:
    async def create_advanced_config(self, advanced_config: AdvancedConfig):
        try:
            existing_config = await AdvancedConfig.get(advanced_config.workspace_id)
            if existing_config:
                return existing_config
        except Exception as e:
            
        await advanced_config.insert()
        return advanced_config