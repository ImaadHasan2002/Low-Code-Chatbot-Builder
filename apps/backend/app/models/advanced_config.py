from beanie import Document
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId

class AdvancedConfig(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    # TOOD: remove workspace_id
    workspace_id: PyObjectId
    
    # HuggingFace Integration
    huggingface_token: str = Field(default="")
    use_custom_embedding_model: bool = Field(default=False)
    custom_embedding_model_name: str = Field(default="")
    
    # Embedding Configuration
    embedding_model: str = Field(default="multilingual-e5-large")
    
    # Parser Configuration
    pdf_parser: str = Field(default="PyPDFParser")
    csv_parser: str = Field(default="CSVParser")
    
    # Text Splitting Configuration
    splitter_type: str = Field(default="RecursiveCharacterTextSplitter")
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    separator: str = Field(default="\n\n")
    
    # LLM Configuration
    max_tokens: int = Field(default=1000)
    use_tuned_model: bool = Field(default=False)
    tuned_model_name: str = Field(default="")
    temperature: float = Field(default=0.2)
    llm_model: str = Field(default="gpt-4o-mini")
    system_prompt: str = Field(default="You are a helpful assistant that can answer questions and help with tasks.")
    
    # Web Scraping Configuration
    scraping_max_pages: int = Field(default=50)
    scraping_max_depth: int = Field(default=3)
    scraping_timeout: int = Field(default=10)
    scraping_same_domain_only: bool = Field(default=True)
    
    # Security Configuration
    block_words: list[str] = Field(default=[])

    class Config:
        json_encoders = {ObjectId: str}

    class Settings:
        name = "advanced_configs"
