from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import uuid
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import pdfplumber
from pdfminer.high_level import extract_text
import csv
import pandas as pd
from io import StringIO
from ..models.advanced_config import AdvancedConfig

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..core.config import get_settings
from ..services.pinecone_service import PineconeService
from ..utils.preprocessing import TextSplitter, DocumentParser

settings = get_settings()
  
class CustomizableEmbeddingModel:
    """Wrapper for SentenceTransformer models with configurable parameters."""
    
    SUPPORTED_MODELS = {
        "stsb-roberta-large": {
            "dimensions": 1024,
            "description": "Sentence Transformers model optimized for semantic textual similarity"
        },
        "mixedbread-ai/mxbai-embed-large-v1": {
            "dimensions": 1024,
            "description": "Sentence Transformers model by MixedBread AI"
        },
        "multilingual-e5-large": {
            "dimensions": 1024,
            "description": "Multilingua*l embedding model"
        }
    }
    
    def __init__(self, model_name: str = "stsb-roberta-large"):
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(f"Model {model_name} not supported. Choose from: {list(self.SUPPORTED_MODELS.keys())}")
        
        self.model_name = model_name
        self.dimensions = self.SUPPORTED_MODELS[model_name]["dimensions"]
        
        # Load model on initialization for sentence_transformers
        if model_name != "multilingual-e5-large":
            self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        if self.model_name == "multilingual-e5-large":
            # Use Pinecone's inference API for this specific model
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            embeddings = pc.inference.embed(
                model=self.model_name,
                inputs=texts,
                parameters={"input_type": "passage", "truncate": "END"}
            )
            return [e["values"] for e in embeddings]
        else:
            # Use sentence_transformers for other models
            return self.model.encode(texts, convert_to_tensor=False).tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """Embed a query string."""
        if self.model_name == "multilingual-e5-large":
            # Use Pinecone's inference API for this specific model
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            embedding = pc.inference.embed(
                model=self.model_name,
                inputs=query,
                parameters={"input_type": "query", "truncate": "END"}
            )
            return embedding.data[0].values
        else:
            # Use sentence_transformers for other models
            return self.model.encode(query, convert_to_tensor=False).tolist()

class CustomizablePDFParser:
    def __init__(self, parser_type: str):
        self.parser_type = parser_type
        self.parser = DocumentParser(parser_type)

    def parse(self, file_path: str) -> List[Document]:
        if self.parser_type == "PyPDFParser":
            return self.parser.pypdf(file_path)
        elif self.parser_type == "PDFPlumberParser":
            return self.parser.pdfplumber(file_path)
        elif self.parser_type == "PDFMinerParser":
            return self.parser.pdfminer(file_path)
        else:
            raise ValueError(f"Unsupported PDF parser: {self.parser_type}")
            
class LangChainService:
    def __init__(
        self,
        advanced_config: Optional[Dict[str, Any]] = None
    ):
        if advanced_config:
            self.advanced_config = advanced_config
        else:
            advanced_config = {
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
                "blockWords": []
            }

        self.advanced_config = advanced_config

        self.pinecone_service = PineconeService()
        self.index = self.pinecone_service.index        
        self.parser = CustomizablePDFParser(advanced_config["pdfParser"] or "PyPDFParser")        
        self.embedding_model = CustomizableEmbeddingModel(advanced_config["embeddingModel"] or "multilingual-e5-large")
        self.chunker = TextSplitter(advanced_config["splitterType"] or "RecursiveCharacterTextSplitter")
        
    def parse_document(self, file_path: str) -> List[Document]:
        """Process document using the configured parser."""
        return self.parser.parse(file_path)
    
    def create_embeddings(self, documents: List[Document], workspace_id: str):
        """Create embeddings and store in Pinecone."""
        # Extract text from documents
        texts = []

        texts = [doc.page_content if isinstance(doc, Document) else doc for doc in documents]
        
        # Generate embeddings
        embeddings = self.embedding_model.embed_documents(texts)

        return embeddings

    def generate_query_variations(self, query: str, n: int = 3) -> List[str]:
        """
        Generate multiple variations of the original query using LLM.
        
        Args:
            query: Original user query
            n: Number of variations to generate
            
        Returns:
            List of query variations
        """
        try:
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=settings.OPENAI_API_KEY,
                temperature=0.5
            )
            
            prompt = f"""Generate {n} different versions of the following search query. 
            Each version should represent the same information need but be phrased differently.
            Return only the queries, one per line, without any numbering or additional text.
            
            Original query: {query}"""
            
            response = llm.invoke([
                SystemMessage(content="You are a helpful assistant that generates alternative search queries."),
                HumanMessage(content=prompt)
            ])
            
            # Extract query variations from the response
            variations = [line.strip() for line in response.content.strip().split('\n') if line.strip()]
            
            # Ensure we have the requested number of variations
            # If we get fewer than requested, pad with the original query
            while len(variations) < n:
                variations.append(query)
                
            # Add the original query if it's not already included
            if query not in variations:
                variations.append(query)
                
            return variations
        except Exception as e:
            print(f"Error generating query variations: {e}")
            # Return the original query as fallback
            return [query]
    
    def reciprocal_rank_fusion(self, results_list: List[List], k: int = 60) -> List:
        """
        Combine multiple search results using Reciprocal Rank Fusion.
        
        Args:
            results_list: List of search results from different queries
            k: Constant to prevent division by zero issues and control score impact
            
        Returns:
            Fused and re-ranked list of results
        """
        # Create a dictionary to store document scores
        doc_scores = {}
        
        # Process each result list
        for results in results_list:
            # Get unique document IDs to avoid counting duplicates within a single query result
            seen_ids = set()
            
            for rank, result in enumerate(results):
                doc_id = result.id
                
                # Skip if we've already seen this document in this result list
                if doc_id in seen_ids:
                    continue
                    
                seen_ids.add(doc_id)
                
                # Calculate RRF score for this document at this rank
                # RRF score = 1 / (rank + k)
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = {"result": result, "score": 0}
                
                # Add the reciprocal rank score
                doc_scores[doc_id]["score"] += 1.0 / (rank + k)
        
        # Sort documents by their accumulated RRF scores in descending order
        sorted_docs = sorted(doc_scores.values(), key=lambda x: x["score"], reverse=True)
        
        # Return the sorted results
        return [doc["result"] for doc in sorted_docs]
        
    def similarity_search(self, query: str, namespace: str = "67b1c1d1c91e325f5eae3f95", k: int = 4) -> List[Document]:
        """Perform similarity search with error handling."""
        try:
            # Generate query embedding
            try:
                print(f"Embedding query using {self.embedding_model.model_name}")
                query_embedding = self.embedding_model.embed_query(query)
            except Exception as e:
                print("Error embedding query: ", e)
                return []
            
            print("query_embedding sample: ", query_embedding[:5])
            
            # Query Pinecone
            try:
                results = self.index.query(
                    vector=query_embedding,
                    top_k=k,
                    namespace=namespace,
                    include_metadata=True
                )
            except Exception as e:
                print("Error querying Pinecone: ", e)
                return []
            
            # Convert results to Documents
            return [
                Document(
                    page_content=result.metadata["source_text"],
                    metadata=result.metadata
                )
                for result in results.matches
            ]
        except Exception as e:
            raise Exception(f"Error in similarity search: {str(e)}")

    def rag_fusion_search(self, query: str, namespace: str = "67b1c1d1c91e325f5eae3f95", k: int = 4) -> List[Document]:
        """
        Perform RAG Fusion search with query generation and reciprocal rank fusion.
        
        Args:
            query: Original user query
            namespace: Pinecone namespace
            k: Number of results to return
            
        Returns:
            List of retrieved documents
        """
        try:
            # Step 1: Generate query variations
            query_variations = self.generate_query_variations(query)
            print(f"Generated query variations: {query_variations}")
            
            # Step 2: Perform search for each query variation
            all_results = []
            
            for q in query_variations:
                # Generate query embedding
                query_embedding = self.embedding_model.embed_query(q)
                
                # Query Pinecone
                results = self.index.query(
                    vector=query_embedding,
                    top_k=max(k * 2, 10),  # Retrieve more results initially for better fusion
                    namespace=namespace,
                    include_metadata=True
                )

                print(f"Results: {results}")
                
                # Add results to the collection
                all_results.append(results.matches)
            
            # Step 3: Apply reciprocal rank fusion
            fused_results = self.reciprocal_rank_fusion(all_results)
            print(f"Fused results: {fused_results}")
            
            # Step 4: Take the top k results
            top_results = fused_results[:k]
            
            # Convert results to Documents
            documents = [
                Document(
                    page_content=result.metadata["source_text"],
                    metadata=result.metadata
                )
                for result in top_results
            ]
            
            return documents
            
        except Exception as e:
            print(f"Error in RAG fusion search: {e}")
            # Fallback to regular similarity search
            return self.similarity_search(query, namespace, k)
