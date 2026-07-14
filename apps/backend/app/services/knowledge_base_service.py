import csv
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Optional

from bson import ObjectId
from fastapi import HTTPException, UploadFile, status
from langchain_core.documents import Document
from pydantic import ValidationError

from ..core.config import get_settings
from ..models.advanced_config import AdvancedConfig
from ..models.knowledge_base import KnowledgeBase, KnowledgeBaseType
from ..repositories.knowledge_base_repository import KnowledgeBaseRepository
from ..services.aws_service import AWS_Service
from ..services.background_job_service import BackgroundJobService
from ..services.langchain_service import LangChainService
from ..services.pinecone_service import PineconeService
from ..utils.scraping import CrawledPage, crawl_site

settings = get_settings()

CSV_EXTENSIONS = {".csv"}
XLS_EXTENSIONS = {".xls", ".xlsx"}
IMAGE_EXTENSIONS = {".apng", ".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
VIDEO_EXTENSIONS = {".avi", ".mov", ".mp4", ".mpeg", ".mpg", ".webm"}
SUPPORTED_UPLOAD_EXTENSIONS = (
    {".pdf"}
    | CSV_EXTENSIONS
    | XLS_EXTENSIONS
    | IMAGE_EXTENSIONS
    | VIDEO_EXTENSIONS
)


class KnowledgeBaseService:
    def __init__(self, workspace_id: ObjectId):
        self.workspace_id = workspace_id
        self.aws_service = AWS_Service()
        self.pinecone_service = PineconeService()
        self.langchain = LangChainService()
        self.advanced_config = None
        self.knowledge_base_repository = KnowledgeBaseRepository()

    async def initialize(self):
        """Load the workspace's AdvancedConfig and reconfigure LangChain."""
        if not self.advanced_config:
            self.advanced_config = await AdvancedConfig.find_one(
                AdvancedConfig.workspace_id == ObjectId(self.workspace_id)
            )
            if self.advanced_config:
                self.langchain = LangChainService(advanced_config=self.advanced_config)
        return self

    async def scrape_link(
        self,
        link: str,
        workspace_id: ObjectId,
        *,
        max_pages: int = 25,
        max_depth: int = 2,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
    ) -> List[KnowledgeBase]:
        await self.initialize()
        pages = crawl_site(
            link,
            max_pages=max_pages,
            max_depth=max_depth,
            include_paths=include_paths or [],
            exclude_paths=exclude_paths or [],
        )
        if not pages:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No indexable pages were found at that URL",
            )

        return await self._index_crawled_pages(
            workspace_id=workspace_id,
            pages=pages,
            base_url=link,
        )

    async def run_crawl_job(
        self,
        *,
        job_id: str,
        workspace_id: str,
        base_url: str,
        max_pages: int,
        max_depth: int,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
    ) -> None:
        job_service = BackgroundJobService()
        await job_service.update_job_progress(
            job_id,
            status="running",
            message="Crawling website",
            processed_items=0,
            total_items=0,
        )

        try:
            await self.initialize()
            pages = crawl_site(
                base_url,
                max_pages=max_pages,
                max_depth=max_depth,
                include_paths=include_paths or [],
                exclude_paths=exclude_paths or [],
            )
            await job_service.update_job_progress(
                job_id,
                message=f"Indexing {len(pages)} crawled page(s)",
                total_items=len(pages),
            )

            if not pages:
                await job_service.update_job_progress(
                    job_id,
                    status="failed",
                    message="No indexable pages were found at that URL",
                )
                return

            await self._index_crawled_pages(
                workspace_id=ObjectId(workspace_id),
                pages=pages,
                base_url=base_url,
                crawl_job_id=job_id,
                job_service=job_service,
            )
            await job_service.update_job_progress(
                job_id,
                status="completed",
                message=f"Indexed {len(pages)} page(s)",
                processed_items=len(pages),
                total_items=len(pages),
            )
        except Exception as exc:
            await job_service.update_job_progress(
                job_id,
                status="failed",
                message=str(exc),
            )

    async def _index_crawled_pages(
        self,
        *,
        workspace_id: ObjectId,
        pages: List[CrawledPage],
        base_url: str,
        crawl_job_id: Optional[str] = None,
        job_service: Optional[BackgroundJobService] = None,
    ) -> List[KnowledgeBase]:
        saved_pages: List[KnowledgeBase] = []
        for index, page in enumerate(pages, start=1):
            knowledge_base = KnowledgeBase(
                workspace_id=workspace_id,
                type=KnowledgeBaseType.LINK,
                file_url=page.url,
                name=page.title or page.url,
                status="pending",
                metadata={
                    "source_type": "crawler",
                    "base_url": base_url,
                    "crawl_job_id": crawl_job_id,
                    "depth": page.depth,
                    "status_code": page.status_code,
                    "content_length": len(page.content),
                    "title": page.title,
                },
            )
            saved_kb = await self.knowledge_base_repository.create(knowledge_base)
            saved_pages.append(saved_kb)

            try:
                documents = self._documents_for_crawled_page(page, saved_kb)
                self.langchain.create_embeddings(
                    documents, str(workspace_id), knowledge_base_id=str(saved_kb.id)
                )
                saved_kb.status = "indexed"
                await saved_kb.save()
            except Exception:
                saved_kb.status = "failed"
                await saved_kb.save()
                raise

            if job_service and crawl_job_id:
                await job_service.update_job_progress(
                    crawl_job_id,
                    processed_items=index,
                    total_items=len(pages),
                    message=f"Indexed {index} of {len(pages)} page(s)",
                )

        return saved_pages

    def _documents_for_crawled_page(
        self, page: CrawledPage, knowledge_base: KnowledgeBase
    ) -> List[Document]:
        chunks = self.langchain.text_splitter.split_text(page.content)
        return [
            Document(
                page_content=chunk,
                metadata={
                    "workspace_id": str(knowledge_base.workspace_id),
                    "knowledge_base_id": str(knowledge_base.id),
                    "source": page.url,
                    "title": page.title,
                    "depth": page.depth,
                    "chunk_id": f"{knowledge_base.id}-{i}",
                },
            )
            for i, chunk in enumerate(chunks)
        ]

    async def upload_pdf_and_create_knowledge_base(
        self, workspace_id: ObjectId, file: UploadFile, user_id: ObjectId
    ) -> KnowledgeBase:
        """Backward-compatible wrapper for the generalized upload path."""
        return await self.upload_file_and_create_knowledge_base(workspace_id, file, user_id)

    async def upload_file_and_create_knowledge_base(
        self, workspace_id: ObjectId, file: UploadFile, user_id: ObjectId
    ) -> KnowledgeBase:
        """Upload a supported file, create the KB entry, and store embeddings."""
        await self.initialize()
        file_url = None
        result = None
        try:
            filename = file.filename or "upload"
            extension = Path(filename).suffix.lower()
            if extension not in SUPPORTED_UPLOAD_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Unsupported file type. Upload PDF, CSV, XLS/XLSX, image, "
                        "or video files."
                    ),
                )

            kb_type = self._knowledge_base_type_for_extension(extension)
            file.file.seek(0)
            file_url = self.aws_service.upload_to_s3(file)
            file.file.seek(0)

            knowledge_base = KnowledgeBase(
                workspace_id=workspace_id,
                type=kb_type,
                file_url=file_url,
                name=filename,
                status="pending",
                metadata={
                    "source_type": "upload",
                    "extension": extension,
                    "content_type": file.content_type,
                },
            )
            result = await self.knowledge_base_repository.create(knowledge_base)

            await self._process_uploaded_file(result, file)
            result.status = "indexed"
            await result.save()

            return result

        except HTTPException:
            await self._rollback(file_url, result, workspace_id)
            raise
        except Exception as e:
            await self._rollback(file_url, result, workspace_id)
            raise HTTPException(status_code=500, detail=str(e))

    def _knowledge_base_type_for_extension(self, extension: str) -> KnowledgeBaseType:
        if extension == ".pdf":
            return KnowledgeBaseType.PDF
        if extension in CSV_EXTENSIONS:
            return KnowledgeBaseType.CSV
        if extension in XLS_EXTENSIONS:
            return KnowledgeBaseType.XLSX
        if extension in IMAGE_EXTENSIONS:
            return KnowledgeBaseType.IMAGE
        if extension in VIDEO_EXTENSIONS:
            return KnowledgeBaseType.VIDEO
        return KnowledgeBaseType.TEXT

    async def _rollback(self, file_url, result, workspace_id):
        try:
            if file_url:
                await self.aws_service.delete_from_s3(file_url)
            if result:
                await self.knowledge_base_repository.delete(result.id)
                self.pinecone_service.delete_from_pinecone(str(workspace_id), str(result.id))
        except Exception as cleanup_error:
            print(f"Cleanup error (non-fatal): {cleanup_error}")

    async def get_by_workspace(
        self,
        workspace_id: ObjectId,
        skip: int = 0,
        limit: int = 100,
        kb_type: Optional[KnowledgeBaseType] = KnowledgeBaseType.PDF,
    ) -> List[KnowledgeBase]:
        """Get knowledge bases for a workspace with optional type filtering."""
        try:
            filters = [KnowledgeBase.workspace_id == workspace_id]
            if kb_type:
                filters.append(KnowledgeBase.type == kb_type)
            return await KnowledgeBase.find(*filters, skip=skip, limit=limit).to_list()
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data format"
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch knowledge bases",
            )

    async def get_knowledge_base(
        self, knowledge_base_id: str, workspace_id: ObjectId
    ) -> KnowledgeBase:
        """Get a single knowledge base document scoped to a workspace."""
        if not ObjectId.is_valid(knowledge_base_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid knowledge base id",
            )

        kb = await self.knowledge_base_repository.find_by_id(ObjectId(knowledge_base_id))
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge base not found",
            )
        if str(kb.workspace_id) != str(workspace_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Knowledge base does not belong to this workspace",
            )
        return kb

    async def get_knowledge_base_links(self, workspace_id: ObjectId) -> List[KnowledgeBase]:
        """Get all crawled/link knowledge bases for a workspace."""
        return await KnowledgeBase.find(
            KnowledgeBase.workspace_id == workspace_id,
            KnowledgeBase.type == KnowledgeBaseType.LINK,
        ).sort("-updated_at").to_list()

    async def delete_knowledge_base(self, knowledge_base_id: str, workspace_id: str):
        """Delete a knowledge base: DB entry, uploaded file, and vectors."""
        if not ObjectId.is_valid(knowledge_base_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid knowledge base id",
            )

        kb = await self.knowledge_base_repository.find_by_id(ObjectId(knowledge_base_id))
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found"
            )
        if str(kb.workspace_id) != str(workspace_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Knowledge base does not belong to this workspace",
            )

        if kb.type != KnowledgeBaseType.LINK and kb.file_url:
            try:
                await self.aws_service.delete_from_s3(kb.file_url)
            except Exception as e:
                print(f"File delete failed (continuing): {e}")

        try:
            self.pinecone_service.delete_from_pinecone(str(workspace_id), str(kb.id))
        except Exception as e:
            print(f"Pinecone delete failed (continuing): {e}")

        await self.knowledge_base_repository.delete(kb.id)

    async def _process_uploaded_file(
        self, knowledge_base: KnowledgeBase, file: UploadFile
    ):
        """Parse the uploaded file bytes and create + store embeddings."""
        suffix = Path(file.filename or "upload").suffix or ".bin"
        tmp_path: Optional[str] = None
        try:
            file.file.seek(0)
            with NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_path = tmp_file.name
                while chunk := file.file.read(1024 * 1024):
                    tmp_file.write(chunk)
            file.file.seek(0)
            await self._process_file(knowledge_base, tmp_path)
        finally:
            try:
                file.file.seek(0)
            except Exception:
                pass
            if tmp_path:
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except Exception as cleanup_error:
                    print(f"Temporary file cleanup failed (non-fatal): {cleanup_error}")

    async def _process_file(self, knowledge_base: KnowledgeBase, file_path: str):
        """Parse the file and create + store embeddings."""
        try:
            documents = self._parse_file_for_knowledge_base(knowledge_base, file_path)

            for doc in documents:
                doc.metadata.update(
                    {
                        "workspace_id": str(knowledge_base.workspace_id),
                        "knowledge_base_id": str(knowledge_base.id),
                        "source": knowledge_base.file_url,
                    }
                )

            self.langchain.create_embeddings(
                documents=documents,
                workspace_id=str(knowledge_base.workspace_id),
                knowledge_base_id=str(knowledge_base.id),
            )
        except HTTPException:
            raise
        except Exception as e:
            knowledge_base.status = "failed"
            await knowledge_base.save()
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    def _parse_file_for_knowledge_base(
        self, knowledge_base: KnowledgeBase, file_path: str
    ) -> List[Document]:
        if knowledge_base.type == KnowledgeBaseType.PDF:
            return self.langchain.parse_document(file_path)

        if knowledge_base.type == KnowledgeBaseType.CSV:
            text = self._csv_to_text(file_path)
            return self._split_text_document(text, knowledge_base, file_path)

        if knowledge_base.type == KnowledgeBaseType.XLSX:
            text = self._xlsx_to_text(file_path)
            return self._split_text_document(text, knowledge_base, file_path)

        if knowledge_base.type in {KnowledgeBaseType.IMAGE, KnowledgeBaseType.VIDEO}:
            text = self._media_metadata_to_text(knowledge_base, file_path)
            return self._split_text_document(text, knowledge_base, file_path)

        return self._split_text_document(knowledge_base.name, knowledge_base, file_path)

    def _split_text_document(
        self, text: str, knowledge_base: KnowledgeBase, file_path: str
    ) -> List[Document]:
        source_doc = Document(
            page_content=text or knowledge_base.name,
            metadata={"source": file_path, "file_name": knowledge_base.name},
        )
        return self.langchain.text_splitter.split_texts([source_doc])

    def _csv_to_text(self, file_path: str) -> str:
        lines = []
        with open(file_path, newline="", encoding="utf-8-sig", errors="replace") as handle:
            sample = handle.read(4096)
            handle.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample) if sample else csv.excel
            except csv.Error:
                dialect = csv.excel
            reader = csv.reader(handle, dialect)
            for row_index, row in enumerate(reader):
                if row_index >= 1000:
                    lines.append("Additional rows omitted after 1000 rows.")
                    break
                cleaned = [cell.strip() for cell in row if cell and cell.strip()]
                if cleaned:
                    lines.append(" | ".join(cleaned))
        return "\n".join(lines)

    def _xlsx_to_text(self, file_path: str) -> str:
        suffix = Path(file_path).suffix.lower()
        if suffix == ".xls":
            return (
                "Legacy XLS spreadsheet uploaded. Install an XLS parser to extract "
                "cell contents. File name: " + Path(file_path).name
            )

        try:
            with zipfile.ZipFile(file_path) as workbook:
                shared_strings = self._xlsx_shared_strings(workbook)
                lines = []
                worksheet_names = sorted(
                    name
                    for name in workbook.namelist()
                    if name.startswith("xl/worksheets/") and name.endswith(".xml")
                )
                for worksheet_name in worksheet_names:
                    lines.extend(
                        self._xlsx_worksheet_rows(workbook, worksheet_name, shared_strings)
                    )
                return "\n".join(lines)
        except zipfile.BadZipFile as exc:
            raise ValueError("Invalid XLSX file") from exc

    def _xlsx_shared_strings(self, workbook: zipfile.ZipFile) -> List[str]:
        if "xl/sharedStrings.xml" not in workbook.namelist():
            return []
        root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
        strings = []
        for item in root:
            if self._xml_local_name(item.tag) != "si":
                continue
            strings.append(" ".join(text.strip() for text in item.itertext() if text.strip()))
        return strings

    def _xlsx_worksheet_rows(
        self,
        workbook: zipfile.ZipFile,
        worksheet_name: str,
        shared_strings: List[str],
    ) -> List[str]:
        root = ET.fromstring(workbook.read(worksheet_name))
        rows = []
        for element in root.iter():
            if self._xml_local_name(element.tag) != "row":
                continue
            values = []
            for cell in element:
                if self._xml_local_name(cell.tag) != "c":
                    continue
                value = self._xlsx_cell_value(cell, shared_strings)
                if value:
                    values.append(value)
            if values:
                rows.append(" | ".join(values))
            if len(rows) >= 1000:
                rows.append("Additional rows omitted after 1000 rows.")
                break
        return rows

    def _xlsx_cell_value(self, cell: ET.Element, shared_strings: List[str]) -> str:
        cell_type = cell.attrib.get("t")
        raw_value = ""

        for child in cell:
            local_name = self._xml_local_name(child.tag)
            if local_name == "v" and child.text:
                raw_value = child.text.strip()
            elif local_name == "is":
                raw_value = " ".join(text.strip() for text in child.itertext() if text.strip())

        if cell_type == "s" and raw_value.isdigit():
            index = int(raw_value)
            if index < len(shared_strings):
                return shared_strings[index]
        return raw_value

    def _xml_local_name(self, tag: str) -> str:
        return tag.rsplit("}", 1)[-1]

    def _media_metadata_to_text(self, knowledge_base: KnowledgeBase, file_path: str) -> str:
        file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
        media_kind = "image" if knowledge_base.type == KnowledgeBaseType.IMAGE else "video"
        return (
            f"{media_kind.title()} knowledge source uploaded to BotCraft.\n"
            f"File name: {knowledge_base.name}\n"
            f"URL: {knowledge_base.file_url}\n"
            f"Size bytes: {file_size}\n"
            "No OCR or transcription text was extracted in this pass."
        )
