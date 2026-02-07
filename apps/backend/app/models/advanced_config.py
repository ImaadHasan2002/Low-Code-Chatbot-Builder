from beanie import Document
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId

class AdvancedConfig(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    # TOOD: remove workspace_id
    workspace_id: PyObjectId
    huggingface_token: str = Field(default="")
    embedding_model: str = Field(default="multilingual-e5-large")
    pdf_parser: str = Field(default="PyPDFParser")
    csv_parser: str = Field(default="CSVParser")
    splitter_type: str = Field(default="RecursiveCharacterTextSplitter")
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    separator: str = Field(default="\n\n")
    max_tokens: int = Field(default=1000)
    use_tuned_model: bool = Field(default=False)
    tuned_model_name: str = Field(default="")
    temperature: float = Field(default=0.2)
    llm_model: str = Field(default="gpt-4o-mini")
    system_prompt: str = Field(default="You are a helpful assistant that can answer questions and help with tasks.")
    block_words: list[str] = Field(default=[])

    class Config:
        json_encoders = {ObjectId: str}

    class Settings:
        name = "advanced_configs"
