# import os
# from app.utils.langchain_utils import PyPDFParser, PDFPlumberParser, PDFMinerParser, CustomizableEmbeddingModel

# SAMPLE_PDF = r"c:\Users\Imaad\Downloads\botcraft\Day.pdf"

# def test_parser(parser, parser_name):
#     print(f"\nTesting parser: {parser_name}")
#     try:
#         docs = parser.parse(SAMPLE_PDF)
#         print(f"Extracted {len(docs)} chunks.")
#         for i, doc in enumerate(docs[:2]):  # Show first 2 chunks
#             print(f"Chunk {i+1}: {doc.page_content[:100]}...")
#         return docs
#     except Exception as e:
#         print(f"Error with {parser_name}: {e}")
#         return []

# def test_embedding(model_name, texts):
#     print(f"\nTesting embedding model: {model_name}")
#     try:
#         model = CustomizableEmbeddingModel(model_name)
#         embeddings = model.embed_documents(texts)
#         print(f"Embedding shape: {len(embeddings)} x {len(embeddings[0]) if embeddings else 0}")
#         print(f"First vector sample: {embeddings[0][:5] if embeddings else 'N/A'}")
#     except Exception as e:
#         print(f"Error with embedding model {model_name}: {e}")

# if __name__ == "__main__":
#     if not os.path.isfile(SAMPLE_PDF):
#         print(f"File not found: {SAMPLE_PDF}")
#     else:
#         # Test all parsers
#         for parser_cls, name in [
#             (PyPDFParser, "PyPDFParser"),
#             (PDFPlumberParser, "PDFPlumberParser"),
#             (PDFMinerParser, "PDFMinerParser"),
#         ]:
#             parser = parser_cls()
#             docs = test_parser(parser, name)
#             if docs:
#                 # Test all embedding models on first chunk
#                 for model_name in [
#                     "stsb-roberta-large",
#                     "mixedbread-ai/mxbai-embed-large-v1",
#                     "multilingual-e5-large"
#                 ]:
#                     test_embedding(model_name, [docs[0].page_content])