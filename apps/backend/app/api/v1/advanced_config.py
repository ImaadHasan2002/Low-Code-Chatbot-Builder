from fastapi import APIRouter, Depends, HTTPException, status, Query
from bson import ObjectId

from ...models.advanced_config import AdvancedConfig
from ...core.security import get_current_user
from ...models.user import UserInDB
from ...utils.mixed import PyObjectId

router = APIRouter()

# camelCase (frontend) -> snake_case (model) field mapping
FIELD_MAP = {
    "huggingfaceToken": "huggingface_token",
    "embeddingModel": "embedding_model",
    "pdfParser": "pdf_parser",
    "csvParser": "csv_parser",
    "splitterType": "splitter_type",
    "chunkSize": "chunk_size",
    "chunkOverlap": "chunk_overlap",
    "separator": "separator",
    "maxTokens": "max_tokens",
    "useTunedModel": "use_tuned_model",
    "tunedModelName": "tuned_model_name",
    "temperature": "temperature",
    "llmModel": "llm_model",
    "systemPrompt": "system_prompt",
    "blockWords": "block_words",
}


@router.get("/")
async def get_advanced_config(
    workspace_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_user)
) -> dict:
    if not workspace_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Workspace ID is required")

    try:
        advanced_config = await AdvancedConfig.find_one(AdvancedConfig.workspace_id == ObjectId(workspace_id))
        return {"advanced_config": advanced_config}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/", response_model=AdvancedConfig)
async def create_advanced_config(
    advanced_config: dict,
    workspace_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_user)
) -> AdvancedConfig:
    try:
        config_data = advanced_config.get("advanced_config", {})
        advanced_config_doc = AdvancedConfig(
            workspace_id=PyObjectId(workspace_id),
            huggingface_token=config_data.get("huggingfaceToken", ""),
            embedding_model=config_data.get("embeddingModel", "multilingual-e5-large"),
            pdf_parser=config_data.get("pdfParser", "PyPDFParser"),
            csv_parser=config_data.get("csvParser", "CSVParser"),
            splitter_type=config_data.get("splitterType", "RecursiveCharacterTextSplitter"),
            chunk_size=config_data.get("chunkSize", 1000),
            chunk_overlap=config_data.get("chunkOverlap", 200),
            separator=config_data.get("separator", "\n\n"),
            max_tokens=config_data.get("maxTokens", 1000),
            use_tuned_model=config_data.get("useTunedModel", False),
            tuned_model_name=config_data.get("tunedModelName", ""),
            temperature=config_data.get("temperature", 0.2),
            llm_model=config_data.get("llmModel", "gpt-4o-mini"),
            system_prompt=config_data.get("systemPrompt", ""),
            block_words=config_data.get("blockWords", []),
        )
        await advanced_config_doc.save()
        return advanced_config_doc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/", response_model=AdvancedConfig)
async def update_advanced_config(
    advanced_config: dict,
    workspace_id: str = Query(...),
    current_user: UserInDB = Depends(get_current_user)
) -> AdvancedConfig:
    try:
        config_data = advanced_config.get("advanced_config", {})
        advanced_config_doc = await AdvancedConfig.find_one(
            AdvancedConfig.workspace_id == ObjectId(workspace_id)
        )
        if not advanced_config_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Advanced config not found for this workspace",
            )
        for key, value in config_data.items():
            field = FIELD_MAP.get(key, key)
            if hasattr(advanced_config_doc, field) and field not in ("id", "workspace_id"):
                setattr(advanced_config_doc, field, value)
        await advanced_config_doc.save()
        return advanced_config_doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
