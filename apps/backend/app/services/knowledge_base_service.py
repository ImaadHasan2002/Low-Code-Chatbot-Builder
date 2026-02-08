from typing import List
from fastapi import UploadFile, HTTPException
from bson import ObjectId
import logging
from fastapi import status
from pydantic import ValidationError
from ..models.knowledge_base import KnowledgeBase, KnowledgeBaseType
from ..core.config import get_settings
from ..services.langchain_service import LangChainService
from ..utils.scraping import parse_data
from langchain_core.documents import Document
from ..models.advanced_config import AdvancedConfig
from ..services.aws_service import AWS_Service
from ..services.pinecone_service import PineconeService
from ..repositories.knowledge_base_repository import KnowledgeBaseRepository

settings = get_settings()

class BaseKnowledgebaseService:
    def __init__(self):
        self.aws_service = AWS_Service()
        self.pinecone_service = PineconeService()
        self.langchain = LangChainService()
        self.advanced_config = None
        self.workspace_id = None

    # TODO: rename this function
    async def initialize(self):
        """Initialize async components that require database access"""
        if not self.advanced_config:
            self.advanced_config = await AdvancedConfig.find_one({"workspaceId": ObjectId(self.workspace_id)})
            print("self.advanced_config: ", self.advanced_config)
            self.langchain = LangChainService(
                advanced_config=self.advanced_config
            )
        return self

class KnowledgeBaseService(BaseKnowledgebaseService):
    def __init__(self, workspace_id: ObjectId):
        super().__init__()
        self.workspace_id = workspace_id

    async def scrape_link(self, link: str, workspace_id: str) -> KnowledgeBase:
        await self.initialize()
        # Create the knowledge base entry first so we have an ID
        knowledge_base = KnowledgeBase(
            workspace_id=workspace_id,
            type=KnowledgeBaseType.LINK,
            file_url=link,
            name=link
        )
        
        # Save to get the ID
        saved_kb = await self._save_to_db(knowledge_base)
        
        # Get scraping configuration from advanced config
        max_pages = self.advanced_config.scraping_max_pages if self.advanced_config else 50
        max_depth = self.advanced_config.scraping_max_depth if self.advanced_config else 3
        timeout = self.advanced_config.scraping_timeout if self.advanced_config else 10
        same_domain_only = self.advanced_config.scraping_same_domain_only if self.advanced_config else True
        
        # Get the raw text data with recursive scraping
        raw_texts = parse_data(
            link,
            max_pages=max_pages,
            max_depth=max_depth,
            timeout=timeout,
            same_domain_only=same_domain_only
        )
        
        # Convert to Document objects
        documents = []
        for i, text in enumerate(raw_texts):
            # Split long texts into smaller chunks
            chunks = self.langchain.text_splitter.split_text(text)
            for chunk in chunks:
                documents.append(Document(
                    page_content=chunk,
                    metadata={
                        "workspace_id": str(workspace_id),
                        "knowledge_base_id": str(saved_kb.id),
                        "source": link,
                        "chunk_id": f"{i}-{len(documents)}"
                    }
                ))
        
        # Create embeddings
        self.langchain.create_embeddings(documents, str(workspace_id))
        
        return saved_kb

    async def upload_pdf_and_create_knowledge_base(self, workspace_id: ObjectId, file: UploadFile, user_id: ObjectId) -> KnowledgeBase:
        """Upload a file, process it, and store its embeddings."""
        file_url = None
        result = None
        try:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Only PDF files are supported")

            print(f"filname: {file.filename}")
            self.aws_service.upload_to_s3(file)

            file_url = settings.AWS_BUCKET_URL + file.filename
            print(f"file_url: {file_url}")

            knowledge_base = KnowledgeBase(
                workspace_id=workspace_id,
                type=KnowledgeBaseType.PDF,
                file_url=file_url,
                name=file.filename
            )

            result = await KnowledgeBaseRepository.create(knowledge_base)
            
            await self._process_file(result, file_url)

            return file_url

        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            
            if file_url:
                await self.aws_service.delete_from_s3(file_url)
            if result:
                await self.knowledge_base_repository.delete(result.id)
                await self.pinecone_service.delete_from_pinecone(str(workspace_id), str(result.id))

            raise HTTPException(status_code=500, detail=str(e))

    async def get_by_workspace(self, workspace_id: ObjectId, skip: int = 0, limit: int = 100) -> List[KnowledgeBase]:
        """Get all knowledge bases for a workspace with pagination."""
        try:
            knowledge_bases = await KnowledgeBase.find(
                KnowledgeBase.workspace_id == workspace_id,
                KnowledgeBase.type == KnowledgeBaseType.PDF,
                skip=skip,
                limit=limit
            ).to_list()
            
            return knowledge_bases
            
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data format"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch knowledge bases"
            )

    async def get_knowledge_base_links(self, workspace_id: ObjectId) -> List[KnowledgeBase]:
        """Get all knowledge base links for a workspace."""
        return await KnowledgeBase.find(
            KnowledgeBase.workspace_id == workspace_id,
            KnowledgeBase.type == KnowledgeBaseType.LINK
        ).to_list()

    async def _process_file(self, knowledge_base: KnowledgeBase, file_url: str):
        """Process the file and create embeddings."""
        try:
            # Process documents using LangChain
            documents = self.langchain.parse_document(file_url)
            
            # Add workspace and knowledge base metadata
            for doc in documents:
                print(f"doc: {doc}")
                doc.metadata.update({
                    "workspace_id": str(knowledge_base.workspace_id),
                    "knowledge_base_id": str(knowledge_base.id)
                })

            self.langchain.create_embeddings(
                documents=documents,
                workspace_id=str(knowledge_base.workspace_id)
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    async def _save_to_db(self, knowledge_base: KnowledgeBase) -> KnowledgeBase:
        """Save knowledge base to MongoDB."""
        collection = self._get_collection()
        result = await collection.insert_one(knowledge_base.model_dump(by_alias=True))
        knowledge_base.id = result.inserted_id
        return knowledge_base

    # async def _delete_s3_file(self, file_url: str):
    #     """Delete file from S3."""
    #     try:
    #         key = file_url.split('/')[-1]
    #         self.s3_client.delete_object(
    #             Bucket=settings.AWS_BUCKET_NAME,
    #             Key=key
    #         )
    #     except Exception as e:
    #         print(f"Error deleting S3 file: {str(e)}")

    def _get_collection(self):
        """Get MongoDB collection using the existing connection."""
        from fastapi import Request
        from ..main import app
        return app.mongodb_client[settings.DATABASE_NAME].knowledge_bases

    # async def delete_knowledge_base(self, knowledge_base_id: str, workspace_id: str):
    #     try:
    #         logger.info(f"Deleting knowledge base {knowledge_base_id} from workspace {workspace_id}")
    #         # ... rest of the deletion logic
    #         logger.info(f"Successfully deleted knowledge base {knowledge_base_id}")
    #     except Exception as e:
    #         logger.error(f"Failed to delete knowledge base {knowledge_base_id}: {str(e)}")
    #         raise
