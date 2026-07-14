from typing import List, Dict, Any, Optional

from langchain_core.documents import Document

from ..core.config import get_settings
from ..services.pinecone_service import PineconeService, PineconeNotConfiguredError
from ..utils.preprocessing import TextSplitter, DocumentParser

settings = get_settings()

DEFAULT_ADVANCED_CONFIG: Dict[str, Any] = {
    "embeddingModel": "multilingual-e5-large",
    "pdfParser": "PyPDFParser",
    "csvParser": "CSVParser",
    "splitterType": "RecursiveCharacterTextSplitter",
    "chunkSize": 1000,
    "chunkOverlap": 200,
    "separator": "\n\n",
    "maxTokens": 1000,
    "useTunedModel": False,
    "tunedModelName": "",
    "temperature": 0.2,
    "llmModel": "gpt-4o-mini",
    "systemPrompt": "You are a helpful assistant that can answer questions and help with tasks.",
    "blockWords": [],
}

# Maps snake_case model fields -> camelCase config keys
_SNAKE_TO_CAMEL = {
    "embedding_model": "embeddingModel",
    "pdf_parser": "pdfParser",
    "csv_parser": "csvParser",
    "splitter_type": "splitterType",
    "chunk_size": "chunkSize",
    "chunk_overlap": "chunkOverlap",
    "separator": "separator",
    "max_tokens": "maxTokens",
    "use_tuned_model": "useTunedModel",
    "tuned_model_name": "tunedModelName",
    "temperature": "temperature",
    "llm_model": "llmModel",
    "system_prompt": "systemPrompt",
    "block_words": "blockWords",
}


def normalize_advanced_config(advanced_config: Any) -> Dict[str, Any]:
    """Accept an AdvancedConfig document, a dict (snake_case or camelCase),
    or None, and return a complete camelCase config dict."""
    config = dict(DEFAULT_ADVANCED_CONFIG)

    if advanced_config is None:
        return config

    if hasattr(advanced_config, "model_dump"):
        raw = advanced_config.model_dump()
    elif isinstance(advanced_config, dict):
        raw = dict(advanced_config)
    else:
        raw = {}

    for key, value in raw.items():
        camel = _SNAKE_TO_CAMEL.get(key, key)
        if camel in config and value not in (None, ""):
            config[camel] = value

    return config


class CustomizableEmbeddingModel:
    """Wrapper around embedding backends with configurable parameters.

    "multilingual-e5-large" uses Pinecone's hosted inference API (no local
    model download). The other models use sentence-transformers, which is an
    optional heavy dependency (see requirements-ml.txt).
    """

    SUPPORTED_MODELS = {
        "stsb-roberta-large": {
            "dimensions": 1024,
            "description": "Sentence Transformers model optimized for semantic textual similarity",
        },
        "mixedbread-ai/mxbai-embed-large-v1": {
            "dimensions": 1024,
            "description": "Sentence Transformers model by MixedBread AI",
        },
        "multilingual-e5-large": {
            "dimensions": 1024,
            "description": "Multilingual embedding model served via Pinecone inference",
        },
    }

    def __init__(self, model_name: str = "multilingual-e5-large"):
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Model {model_name} not supported. Choose from: {list(self.SUPPORTED_MODELS.keys())}"
            )

        self.model_name = model_name
        self.dimensions = self.SUPPORTED_MODELS[model_name]["dimensions"]
        self.model = None

        if model_name != "multilingual-e5-large":
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise RuntimeError(
                    f"Embedding model '{model_name}' requires sentence-transformers. "
                    "Install it with: pip install -r requirements-ml.txt"
                ) from exc
            self.model = SentenceTransformer(model_name)

    def _pinecone_client(self):
        if not settings.PINECONE_API_KEY:
            raise PineconeNotConfiguredError()
        from pinecone import Pinecone

        return Pinecone(api_key=settings.PINECONE_API_KEY)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        if self.model_name == "multilingual-e5-large":
            pc = self._pinecone_client()
            embeddings = pc.inference.embed(
                model=self.model_name,
                inputs=texts,
                parameters={"input_type": "passage", "truncate": "END"},
            )
            return [e["values"] for e in embeddings]
        return self.model.encode(texts, convert_to_tensor=False).tolist()

    def embed_query(self, query: str) -> List[float]:
        """Embed a query string."""
        if self.model_name == "multilingual-e5-large":
            pc = self._pinecone_client()
            embedding = pc.inference.embed(
                model=self.model_name,
                inputs=query,
                parameters={"input_type": "query", "truncate": "END"},
            )
            return embedding.data[0].values
        return self.model.encode(query, convert_to_tensor=False).tolist()


class CustomizablePDFParser:
    def __init__(self, parser_type: str, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.parser_type = parser_type
        self.parser = DocumentParser(
            parser_type, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def parse(self, file_path: str) -> List[Document]:
        if self.parser_type == "PyPDFParser":
            return self.parser.pypdf(file_path)
        if self.parser_type == "PDFPlumberParser":
            return self.parser.pdfplumber(file_path)
        if self.parser_type == "PDFMinerParser":
            return self.parser.pdfminer(file_path)
        raise ValueError(f"Unsupported PDF parser: {self.parser_type}")


class LangChainService:
    def __init__(self, advanced_config: Optional[Any] = None):
        self.advanced_config = normalize_advanced_config(advanced_config)
        config = self.advanced_config

        self.pinecone_service = PineconeService()
        self.parser = CustomizablePDFParser(
            config["pdfParser"],
            chunk_size=config["chunkSize"],
            chunk_overlap=config["chunkOverlap"],
        )
        self.embedding_model = CustomizableEmbeddingModel(config["embeddingModel"])
        self.text_splitter = TextSplitter(
            "recursive",
            chunk_size=config["chunkSize"],
            chunk_overlap=config["chunkOverlap"],
        )
        # Backwards-compatible alias
        self.chunker = self.text_splitter

    @property
    def index(self):
        return self.pinecone_service.index

    def parse_document(self, file_path: str) -> List[Document]:
        """Process document using the configured parser."""
        return self.parser.parse(file_path)

    def create_embeddings(
        self,
        documents: List[Document],
        workspace_id: str,
        knowledge_base_id: Optional[str] = None,
    ) -> List[List[float]]:
        """Create embeddings and store them in Pinecone under the workspace
        namespace. Returns the embeddings."""
        texts = [doc.page_content if isinstance(doc, Document) else str(doc) for doc in documents]
        if not texts:
            return []

        embeddings = self.embedding_model.embed_documents(texts)

        if knowledge_base_id is None and documents and isinstance(documents[0], Document):
            knowledge_base_id = documents[0].metadata.get("knowledge_base_id", "unknown")

        # Self-bootstrap: create the index on first write if it is missing,
        # sized to the active embedding model.
        self.pinecone_service.ensure_index(dimension=self.embedding_model.dimensions)

        self.pinecone_service.upsert(
            namespace=str(workspace_id),
            embeddings=embeddings,
            knowledge_base_id=str(knowledge_base_id),
            texts=texts,
        )
        return embeddings

    def generate_query_variations(self, query: str, n: int = 3) -> List[str]:
        """Generate multiple variations of the original query using an LLM.
        Falls back to the original query if the LLM is unavailable."""
        if not settings.OPENAI_API_KEY:
            return [query]
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage, SystemMessage

            llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=settings.OPENAI_API_KEY,
                temperature=0.5,
            )

            prompt = (
                f"Generate {n} different versions of the following search query. "
                "Each version should represent the same information need but be phrased differently. "
                "Return only the queries, one per line, without any numbering or additional text.\n\n"
                f"Original query: {query}"
            )

            response = llm.invoke(
                [
                    SystemMessage(content="You are a helpful assistant that generates alternative search queries."),
                    HumanMessage(content=prompt),
                ]
            )

            variations = [line.strip() for line in response.content.strip().split("\n") if line.strip()]
            while len(variations) < n:
                variations.append(query)
            if query not in variations:
                variations.append(query)
            return variations
        except Exception as e:
            print(f"Error generating query variations: {e}")
            return [query]

    def reciprocal_rank_fusion(self, results_list: List[List], k: int = 60) -> List:
        """Combine multiple search results using Reciprocal Rank Fusion."""
        doc_scores = {}

        for results in results_list:
            seen_ids = set()
            for rank, result in enumerate(results):
                doc_id = result.id
                if doc_id in seen_ids:
                    continue
                seen_ids.add(doc_id)
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = {"result": result, "score": 0}
                doc_scores[doc_id]["score"] += 1.0 / (rank + k)

        sorted_docs = sorted(doc_scores.values(), key=lambda x: x["score"], reverse=True)
        return [doc["result"] for doc in sorted_docs]

    def similarity_search(self, query: str, namespace: str, k: int = 4) -> List[Document]:
        """Perform similarity search; returns [] when retrieval is unavailable."""
        if not self.pinecone_service.is_configured:
            print("Pinecone not configured; skipping retrieval.")
            return []
        try:
            query_embedding = self.embedding_model.embed_query(query)
        except Exception as e:
            print("Error embedding query:", e)
            return []

        try:
            results = self.pinecone_service.query(
                namespace=namespace, vector=query_embedding, top_k=k
            )
        except Exception as e:
            print("Error querying Pinecone:", e)
            return []

        return [
            Document(
                page_content=match.metadata.get("source_text", ""),
                metadata=dict(match.metadata or {}),
            )
            for match in results.matches
            if match.metadata
        ]

    def rag_fusion_search(self, query: str, namespace: str, k: int = 4) -> List[Document]:
        """RAG Fusion search: query variations + reciprocal rank fusion.
        Falls back to plain similarity search on any failure."""
        if not self.pinecone_service.is_configured:
            return []
        try:
            query_variations = self.generate_query_variations(query)

            all_results = []
            for q in query_variations:
                query_embedding = self.embedding_model.embed_query(q)
                results = self.pinecone_service.query(
                    namespace=namespace,
                    vector=query_embedding,
                    top_k=max(k * 2, 10),
                )
                all_results.append(results.matches)

            fused_results = self.reciprocal_rank_fusion(all_results)
            top_results = fused_results[:k]

            return [
                Document(
                    page_content=result.metadata.get("source_text", ""),
                    metadata=dict(result.metadata or {}),
                )
                for result in top_results
                if result.metadata
            ]
        except Exception as e:
            print(f"Error in RAG fusion search: {e}")
            return self.similarity_search(query, namespace, k)
