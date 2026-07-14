from app.models.advanced_config import AdvancedConfig


class AdvancedConfigRepository:
    async def create_advanced_config(self, advanced_config: AdvancedConfig) -> AdvancedConfig:
        """Create an AdvancedConfig, returning the existing one if the
        workspace already has a config."""
        existing_config = await AdvancedConfig.find_one(
            AdvancedConfig.workspace_id == advanced_config.workspace_id
        )
        if existing_config:
            return existing_config

        await advanced_config.insert()
        return advanced_config

    async def get_by_workspace(self, workspace_id) -> AdvancedConfig | None:
        return await AdvancedConfig.find_one(AdvancedConfig.workspace_id == workspace_id)
