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
            # HuggingFace Integration
            huggingface_token=config_data.get("huggingfaceToken", ""),
            use_custom_embedding_model=config_data.get("useCustomEmbeddingModel", False),
            custom_embedding_model_name=config_data.get("customEmbeddingModelName", ""),
            # Embedding Configuration
            embedding_model=config_data.get("embeddingModel", ""),
            # Parser Configuration
            pdf_parser=config_data.get("pdfParser", ""),
            csv_parser=config_data.get("csvParser", ""),
            # Text Splitting Configuration
            splitter_type=config_data.get("splitterType", ""),
            chunk_size=config_data.get("chunkSize", 1000),
            chunk_overlap=config_data.get("chunkOverlap", 200),
            separator=config_data.get("separator", ""),
            # LLM Configuration
            max_tokens=config_data.get("maxTokens", 1000),
            use_tuned_model=config_data.get("useTunedModel", False),
            tuned_model_name=config_data.get("tunedModelName", ""),
            temperature=config_data.get("temperature", 0.2),
            llm_model=config_data.get("llmModel", ""),
            system_prompt=config_data.get("systemPrompt", ""),
            # Web Scraping Configuration
            scraping_max_pages=config_data.get("scrapingMaxPages", 50),
            scraping_max_depth=config_data.get("scrapingMaxDepth", 3),
            scraping_timeout=config_data.get("scrapingTimeout", 10),
            scraping_same_domain_only=config_data.get("scrapingSameDomainOnly", True),
            # Security Configuration
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
            # Update all fields
            advanced_config_doc.huggingface_token = config_data.get("huggingfaceToken", advanced_config_doc.huggingface_token)
            advanced_config_doc.use_custom_embedding_model = config_data.get("useCustomEmbeddingModel", advanced_config_doc.use_custom_embedding_model)
            advanced_config_doc.custom_embedding_model_name = config_data.get("customEmbeddingModelName", advanced_config_doc.custom_embedding_model_name)
            advanced_config_doc.embedding_model = config_data.get("embeddingModel", advanced_config_doc.embedding_model)
            advanced_config_doc.pdf_parser = config_data.get("pdfParser", advanced_config_doc.pdf_parser)
            advanced_config_doc.csv_parser = config_data.get("csvParser", advanced_config_doc.csv_parser)
            advanced_config_doc.splitter_type = config_data.get("splitterType", advanced_config_doc.splitter_type)
            advanced_config_doc.chunk_size = config_data.get("chunkSize", advanced_config_doc.chunk_size)
            advanced_config_doc.chunk_overlap = config_data.get("chunkOverlap", advanced_config_doc.chunk_overlap)
            advanced_config_doc.separator = config_data.get("separator", advanced_config_doc.separator)
            advanced_config_doc.max_tokens = config_data.get("maxTokens", advanced_config_doc.max_tokens)
            advanced_config_doc.use_tuned_model = config_data.get("useTunedModel", advanced_config_doc.use_tuned_model)
            advanced_config_doc.tuned_model_name = config_data.get("tunedModelName", advanced_config_doc.tuned_model_name)
            advanced_config_doc.temperature = config_data.get("temperature", advanced_config_doc.temperature)
            advanced_config_doc.llm_model = config_data.get("llmModel", advanced_config_doc.llm_model)
            advanced_config_doc.system_prompt = config_data.get("systemPrompt", advanced_config_doc.system_prompt)
            advanced_config_doc.scraping_max_pages = config_data.get("scrapingMaxPages", advanced_config_doc.scraping_max_pages)
            advanced_config_doc.scraping_max_depth = config_data.get("scrapingMaxDepth", advanced_config_doc.scraping_max_depth)
            advanced_config_doc.scraping_timeout = config_data.get("scrapingTimeout", advanced_config_doc.scraping_timeout)
            advanced_config_doc.scraping_same_domain_only = config_data.get("scrapingSameDomainOnly", advanced_config_doc.scraping_same_domain_only)
            advanced_config_doc.block_words = config_data.get("blockWords", advanced_config_doc.block_words)
            await advanced_config_doc.save()
        return advanced_config_doc
    except Exception as e:
        print("Error in update_advanced_config: ", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
