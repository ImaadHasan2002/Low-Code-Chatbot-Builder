from typing import List
import uuid
import pdfplumber
from pdfminer.high_level import extract_text
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class DocumentParser:
    """Parses PDF files into Document chunks using a configurable backend."""

    def __init__(self, parser_type: str = "PyPDFParser", text_splitter: str = "recursive", **kwargs):
        self.parser_type = parser_type
        self.text_splitter = TextSplitter(text_splitter, **kwargs)

    def pypdf(self, file_path: str) -> List[Document]:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return self.text_splitter.split_texts(documents)

    def pdfplumber(self, file_path: str) -> List[Document]:
        documents = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": file_path,
                                "page": i + 1,
                                "knowledge_base_id": str(uuid.uuid4()),
                            },
                        )
                    )
        return self.text_splitter.split_texts(documents)

    def pdfminer(self, file_path: str) -> List[Document]:
        text = extract_text(file_path)
        doc = Document(
            page_content=text,
            metadata={"source": file_path, "knowledge_base_id": str(uuid.uuid4())},
        )
        return self.text_splitter.split_texts([doc])


class TextSplitter:
    """Splits documents into chunks. Always returns a flat List[Document]
    so downstream embedding/upsert code can rely on doc.page_content
    being a string."""

    # Map UI names to internal strategies
    _STRATEGY_ALIASES = {
        "RecursiveCharacterTextSplitter": "recursive",
        "SentenceSplitter": "sentence",
        "TokenSplitter": "token",
    }

    def __init__(self, strategy: str = "recursive", **kwargs):
        self.strategy = self._STRATEGY_ALIASES.get(strategy, strategy)
        # Keep only kwargs that the underlying splitters understand
        self.kwargs = {
            k: v for k, v in kwargs.items()
            if k in ("chunk_size", "chunk_overlap", "separators") and v is not None
        }

    def split_text(self, text: str) -> List[str]:
        """Split a raw string into chunk strings."""
        return [doc.page_content for doc in self.split_texts([Document(page_content=text)])]

    def split_texts(self, documents: List[Document]) -> List[Document]:
        if self.strategy == "recursive":
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            splitter = RecursiveCharacterTextSplitter(**self.kwargs)
            return splitter.split_documents(documents)

        if self.strategy == "sentence":
            import nltk

            nltk.download("punkt", quiet=True)
            nltk.download("punkt_tab", quiet=True)
            from nltk.tokenize import sent_tokenize

            chunks = []
            for doc in documents:
                for sentence in sent_tokenize(doc.page_content):
                    chunks.append(Document(page_content=sentence, metadata=dict(doc.metadata)))
            return chunks

        if self.strategy == "token":
            import tiktoken

            enc = tiktoken.get_encoding("cl100k_base")
            size = self.kwargs.get("chunk_size", 1000)
            chunks = []
            for doc in documents:
                tokens = enc.encode(doc.page_content)
                for i in range(0, len(tokens), size):
                    chunks.append(
                        Document(
                            page_content=enc.decode(tokens[i : i + size]),
                            metadata=dict(doc.metadata),
                        )
                    )
            return chunks

        raise ValueError(f"Unsupported strategy: {self.strategy}")
