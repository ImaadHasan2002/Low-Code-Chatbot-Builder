from typing import List
import uuid
import pdfplumber
from pdfminer.high_level import extract_text
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class DocumentParser():
    """Abstract base class for document parsers."""
    def __init__(self, parser_type: str = "PyPDFParser", text_splitter: str = "recursive", **kwargs):
        self.parser_type = parser_type
        self.text_splitter = TextSplitter(text_splitter, **kwargs)
    
    def pypdf(self, file_path: str) -> List[Document]:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"documents: {documents}")
        return self.text_splitter.split_texts(documents)

    def pdfplumber(self, file_path: str) -> List[Document]:
        documents = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": file_path,
                            "page": i + 1,
                            "knowledge_base_id": str(uuid.uuid4())
                        }
                    )
                    documents.append(doc)

        return self.text_splitter.split_texts(documents)

    def pdfminer(self, file_path: str) -> List[Document]:
        text = extract_text(file_path)
        doc = Document(
            page_content=text,
            metadata={
                "source": file_path,
                "knowledge_base_id": str(uuid.uuid4())
            }
        )
        return self.text_splitter.split_texts([doc])
    
    # def split_texts(self, documents: List[Document]) -> List[Document]:
    #     return self.text_splitter.split_texts(documents)

# For CSV and Excel files, you can create similar parsers
# class CSVParser(DocumentParser):
#     """Document parser for CSV files using Python's built-in csv module."""
    
#     def parse(self, file_path: str) -> List[Document]:
#         """Parse CSV file and return list of Document objects."""
#         documents = []
        
#         with open(file_path, 'r', encoding='utf-8') as f:
#             reader = csv.reader(f)
#             headers = next(reader)  # Get headers
            
#             for i, row in enumerate(reader):
#                 # Create a dictionary from headers and row values
#                 row_dict = dict(zip(headers, row))
                
#                 # Format row as text
#                 content = "\n".join([f"{header}: {value}" for header, value in row_dict.items()])
                
#                 doc = Document(
#                     page_content=content,
#                     metadata={
#                         "source": file_path,
#                         "row": i + 1,
#                         "knowledge_base_id": str(uuid.uuid4())
#                     }
#                 )
#                 documents.append(doc)
                
#         return self.split_documents(documents)


# class PandasCSVParser(DocumentParser):
#     """Document parser for CSV files using pandas with advanced handling capabilities."""
    
#     def __init__(self, text_splitter=None, chunk_size=50):
#         super().__init__(text_splitter)
#         self.chunk_size = chunk_size
    
#     def parse(self, file_path: str) -> List[Document]:
#         """Parse CSV file using pandas and return list of Document objects."""
#         documents = []
        
#         # Read CSV into DataFrame
#         df = pd.read_csv(file_path)
#         total_rows = len(df)
        
#         # Process DataFrame in chunks
#         for i in range(0, total_rows, self.chunk_size):
#             chunk = df.iloc[i:min(i+self.chunk_size, total_rows)]
            
#             # Convert DataFrame chunk to string
#             content = chunk.to_string(index=False)
            
#             doc = Document(
#                 page_content=content,
#                 metadata={
#                     "source": file_path,
#                     "rows": f"{i+1}-{min(i+self.chunk_size, total_rows)}",
#                     "total_rows": total_rows,
#                     "columns": list(df.columns),
#                     "knowledge_base_id": str(uuid.uuid4())
#                 }
#             )
#             documents.append(doc)
            
#         return self.split_documents(documents)


# class BatchCSVParser(DocumentParser):
#     """Document parser that batches CSV rows together for more context."""
    
#     def __init__(self, text_splitter=None, batch_size=10, include_headers=True):
#         super().__init__(text_splitter)
#         self.batch_size = batch_size
#         self.include_headers = include_headers
    
#     def parse(self, file_path: str) -> List[Document]:
#         """Parse CSV and create documents from batches of rows."""
#         documents = []
        
#         with open(file_path, 'r', encoding='utf-8') as f:
#             reader = csv.reader(f)
#             headers = next(reader)
            
#             batch = []
#             batch_num = 0
            
#             for row in reader:
#                 batch.append(row)
                
#                 if len(batch) >= self.batch_size:
#                     # Create a document from this batch
#                     content = self._format_batch(batch, headers)
                    
#                     doc = Document(
#                         page_content=content,
#                         metadata={
#                             "source": file_path,
#                             "batch": batch_num,
#                             "row_count": len(batch),
#                             "knowledge_base_id": str(uuid.uuid4())
#                         }
#                     )
#                     documents.append(doc)
                    
#                     # Reset batch
#                     batch = []
#                     batch_num += 1
            
#             # Handle any remaining rows
#             if batch:
#                 content = self._format_batch(batch, headers)
#                 doc = Document(
#                     page_content=content,
#                     metadata={
#                         "source": file_path,
#                         "batch": batch_num,
#                         "row_count": len(batch),
#                         "knowledge_base_id": str(uuid.uuid4())
#                     }
#                 )
#                 documents.append(doc)
        
#         return self.split_documents(documents)
    
#     def _format_batch(self, batch, headers):
#         """Format a batch of rows into a text representation."""
#         lines = []
        
#         if self.include_headers:
#             # Add a header row
#             lines.append(",".join(headers))
        
#         # Add all data rows
#         for row in batch:
#             lines.append(",".join(row))
            
#         return "\n".join(lines)


class TextSplitter:
    def __init__(self, strategy: str = "recursive", **kwargs):
        self.strategy = strategy
        self.kwargs = kwargs

    def split_texts(self, documents: List[Document]):
        if self.strategy == "recursive":
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(**self.kwargs)

            for doc in documents:
                doc.page_content = doc.page_content.replace("\n", "")
                doc.page_content = splitter.split_text(doc.page_content)

            return documents

        elif self.strategy == "sentence":
            import nltk
            nltk.download('punkt', quiet=True)
            from nltk.tokenize import sent_tokenize
            return [sent_tokenize(doc.page_content) for doc in documents]

        elif self.strategy == "token":
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
            result = []
            for doc in documents:
                tokens = enc.encode(doc.page_content)
                size = self.kwargs.get("chunk_size", 100)
                result.append([tokens[i:i+size] for i in range(0, len(tokens), size)])
            return result

        else:
            raise ValueError("Unsupported strategy")
