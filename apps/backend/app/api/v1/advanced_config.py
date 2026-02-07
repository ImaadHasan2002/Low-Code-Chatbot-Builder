from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from bson import ObjectId

from ...models.advanced_config import AdvancedConfig
from ...core.security import get_current_user
from ...models.user import UserInDB
from ...utils.mixed import PyObjectId

router = APIRouter()

@router.get("/")
async def get_advanced_config(
    workspace_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_user)
) -> dict:
    print("Workspace ID in get_advanced_config: ", workspace_id)

    if not workspace_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Workspace ID is required")
    
    try:
        advanced_config = await AdvancedConfig.find_one(AdvancedConfig.workspace_id == ObjectId(workspace_id))
        print("Advanced config in get_advanced_config: ", advanced_config)
        return {"advanced_config": advanced_config}
    except Exception as e:
        print("Error in get_advanced_config: ", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/", response_model=AdvancedConfig)
async def create_advanced_config(
    advanced_config: dict,
    workspace_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_user)
) -> AdvancedConfig:
    try:
        print("Advanced config in create_advanced_config: ", advanced_config)
        config_data = advanced_config.get("advanced_config", {})
        print("Config data in create_advanced_config: ", config_data)
        advanced_config_doc = AdvancedConfig(
            workspace_id=PyObjectId(workspace_id),
            huggingface_token=config_data.get("huggingfaceToken", ""),
            embedding_model=config_data.get("embeddingModel", ""),
            pdf_parser=config_data.get("pdfParser", ""),
            csv_parser=config_data.get("csvParser", ""),
            splitter_type=config_data.get("splitterType", ""),
            chunk_size=config_data.get("chunkSize", 1000),
            chunk_overlap=config_data.get("chunkOverlap", 200),
            separator=config_data.get("separator", ""),
            max_tokens=config_data.get("maxTokens", 1000),
            use_tuned_model=config_data.get("useTunedModel", False),
            tuned_model_name=config_data.get("tunedModelName", ""),
            temperature=config_data.get("temperature", 0.2),
            llm_model=config_data.get("llmModel", ""),
            system_prompt=config_data.get("systemPrompt", ""),
            block_words=config_data.get("blockWords", []),
        )
        await advanced_config_doc.save()
        return advanced_config_doc
    except Exception as e:
        print("Error in create_advanced_config: ", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/", response_model=AdvancedConfig)
async def update_advanced_config(
    advanced_config: dict,
    workspace_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_user)
) -> AdvancedConfig:
    try:
        print("Advanced config in update_advanced_config: ", advanced_config)
        config_data = advanced_config.get("advanced_config", {})
        print("Config data in update_advanced_config: ", config_data)
        advanced_config_doc = await AdvancedConfig.find_one(AdvancedConfig.workspace_id == ObjectId(workspace_id))
        print("Advanced config in update_advanced_config: ", advanced_config_doc)
        if advanced_config_doc:
            advanced_config_doc.update(config_data)
            await advanced_config_doc.save()
        return advanced_config_doc
    except Exception as e:
        print("Error in update_advanced_config: ", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
