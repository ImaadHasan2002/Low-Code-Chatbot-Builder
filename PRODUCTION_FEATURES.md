# Production-Scale Features

This document describes the production-scale enhancements made to the Low-Code Chatbot Builder platform.

## 🚀 Overview

The platform has been enhanced with the following production-scale features:

1. **HuggingFace Model Integration** - Import and use custom embedding models from HuggingFace
2. **Advanced Hyperparameter Configuration** - Fine-tune model behavior with extensive configuration options
3. **Recursive Web Scraping** - Intelligently crawl and index entire websites
4. **Vector Database Integration** - Efficient storage and retrieval of scraped content

---

## 📦 HuggingFace Model Integration

### Overview
The platform now supports importing custom embedding models from HuggingFace Hub, giving you flexibility to use state-of-the-art models or your own fine-tuned models.

### Supported Models

**Built-in Models:**
- `stsb-roberta-large` - Optimized for semantic textual similarity
- `mixedbread-ai/mxbai-embed-large-v1` - MixedBread AI's embedding model
- `multilingual-e5-large` - Multilingual embedding model
- `BAAI/bge-large-en-v1.5` - BGE Large English model from HuggingFace
- `sentence-transformers/all-mpnet-base-v2` - All MPNet Base V2
- `intfloat/e5-large-v2` - E5 Large V2 model

**Custom Models:**
You can also use any HuggingFace model by:
1. Enabling "Use Custom HuggingFace Model" in Advanced Settings
2. Entering the model identifier (e.g., `organization/model-name`)
3. Providing your HuggingFace API token (for private models)

### Configuration

Navigate to **Settings → Advanced** and configure:

```
HuggingFace Token: your-hf-token-here
Use Custom Embedding Model: [Toggle]
Custom Embedding Model Name: your-org/your-model-name
```

### Technical Details

The embedding model wrapper automatically:
- Detects model type (Sentence Transformers, HuggingFace Transformers, or Pinecone Inference)
- Handles tokenization and mean pooling for HuggingFace models
- Supports GPU acceleration when available
- Normalizes embeddings for optimal similarity search
- Batches large document sets for efficient processing

---

## ⚙️ Hyperparameter Configuration

### Embedding & Text Processing

**Embedding Model Settings:**
- Select from pre-configured models or use your own
- Configure model-specific parameters
- Toggle between different embedding strategies

**Text Splitting Configuration:**
- **Chunk Size:** 1-2000 characters (default: 1000)
  - Size of text chunks for embedding
  - Smaller chunks = more granular retrieval
  - Larger chunks = more context per chunk

- **Chunk Overlap:** 0-500 characters (default: 200)
  - Overlap between consecutive chunks
  - Prevents context loss at chunk boundaries
  
- **Splitter Type:** 
  - `RecursiveCharacterTextSplitter` - Smart splitting based on natural boundaries
  - `CharacterTextSplitter` - Simple character-based splitting

- **Separator:** Custom text separator (default: `\n\n`)

### LLM Configuration

**Model Selection:**
- OpenAI GPT-4o-mini
- Mistral-7B variants
- Llama-2 variants
- Gemma variants

**Generation Parameters:**
- **Temperature:** 0.0-1.0 (default: 0.2)
  - Controls randomness in responses
  - Lower = more deterministic
  - Higher = more creative

- **Max Tokens:** 1-10000 (default: 1000)
  - Maximum length of generated responses

- **System Prompt:** Custom instructions for the AI
  - Define the AI's personality and behavior
  - Set constraints and guidelines

### Fine-tuned Models

Enable custom fine-tuned models from HuggingFace:
- Use domain-specific fine-tuned models
- Configure LoRA parameters
- Set training hyperparameters

---

## 🕷️ Recursive Web Scraping

### Overview
The platform now includes an intelligent web scraper that can recursively crawl websites, extracting and indexing content for your chatbot's knowledge base.

### Features

**Breadth-First Crawling:**
- Systematically explores websites level by level
- Ensures comprehensive coverage within configured limits

**Smart URL Handling:**
- Deduplicates URLs to avoid re-crawling
- Normalizes URLs (removes fragments, handles query parameters)
- Filters by domain to stay within scope

**Configurable Depth & Scale:**
- Control how deep and how wide to crawl
- Set maximum pages to prevent runaway scraping
- Configure timeouts for reliability

### Configuration

Navigate to **Settings → Advanced → Web Scraping Configuration**:

```
Maximum Pages to Scrape: 1-500 (default: 50)
  - Total number of pages to crawl

Maximum Crawl Depth: 1-10 (default: 3)
  - How many links deep to follow from starting URL
  - Depth 1 = only the starting page
  - Depth 2 = starting page + direct links
  - Depth 3 = two levels of links, etc.

Request Timeout: 1-60 seconds (default: 10)
  - Timeout for each HTTP request
  - Prevents hanging on slow/unresponsive pages

Same Domain Only: [Toggle] (default: enabled)
  - Only crawl pages from the same domain
  - Prevents crawling to external sites
```

### Usage

1. Navigate to **Knowledge Base → Links**
2. Click "Add Link"
3. Enter the website URL (e.g., `https://example.com`)
4. Click "Add Link"

The scraper will:
1. Start from the provided URL
2. Extract all links on that page
3. Recursively visit links up to the configured depth
4. Extract text content from each page
5. Chunk the content according to your text splitting settings
6. Generate embeddings using your selected model
7. Store everything in the vector database

### Best Practices

**For Documentation Sites:**
```
Max Pages: 100-200
Max Depth: 4-5
Same Domain Only: Enabled
```

**For Blogs:**
```
Max Pages: 50-100
Max Depth: 2-3
Same Domain Only: Enabled
```

**For Marketing Sites:**
```
Max Pages: 20-50
Max Depth: 2
Same Domain Only: Enabled
```

### Technical Details

**Scraping Process:**
1. **Queue Management:** Uses breadth-first search with URL queue
2. **Visited Tracking:** Maintains set of visited URLs to prevent duplicates
3. **Content Extraction:** Uses BeautifulSoup and LangChain's WebBaseLoader
4. **Rate Limiting:** Includes 0.5s delay between requests to be respectful
5. **Error Handling:** Gracefully handles timeouts, 404s, and connection errors
6. **Logging:** Comprehensive logging for monitoring and debugging

**Text Extraction:**
- Removes navigation, headers, footers automatically
- Extracts main content using LangChain's WebBaseLoader
- Preserves document structure and formatting
- Handles various HTML structures robustly

---

## 🗄️ Vector Database Integration

### Overview
All scraped content is automatically processed and stored in Pinecone vector database for efficient semantic search.

### Processing Pipeline

1. **Content Extraction**
   - Raw HTML is converted to clean text
   - Main content is identified and extracted

2. **Text Chunking**
   - Content is split according to configured chunk size
   - Overlap is applied to preserve context

3. **Embedding Generation**
   - Each chunk is embedded using selected model
   - Batched processing for efficiency
   - GPU acceleration when available

4. **Metadata Tracking**
   - Source URL stored with each chunk
   - Workspace and knowledge base IDs tracked
   - Chunk IDs for traceability

5. **Vector Storage**
   - Embeddings stored in Pinecone
   - Indexed by workspace namespace
   - Optimized for similarity search

### Retrieval

When users ask questions:
1. Question is embedded using the same model
2. Similarity search finds relevant chunks
3. Top-k most relevant chunks are retrieved
4. Context is provided to the LLM
5. LLM generates response based on retrieved context

### Advanced Features

**RAG Fusion:**
- Generates multiple query variations
- Retrieves results for each variation
- Uses Reciprocal Rank Fusion to merge results
- Provides more comprehensive context

---

## 🔧 Installation & Setup

### Backend Requirements

Update your Python environment:
```bash
cd apps/backend
pip install -r requirements.txt
```

New dependencies include:
- `transformers` - HuggingFace transformers library
- `huggingface-hub` - HuggingFace Hub integration
- `accelerate` - GPU acceleration
- `torch` - PyTorch for model inference
- `lxml`, `html5lib` - Additional HTML parsing

### Environment Variables

Add to your `.env` file:
```bash
# HuggingFace (optional - for private models)
HUGGINGFACE_TOKEN=your-hf-token-here
```

### Database Migration

The AdvancedConfig model has been extended with new fields. If you have existing configurations, they will use default values for new fields:
- `use_custom_embedding_model: false`
- `custom_embedding_model_name: ""`
- `scraping_max_pages: 50`
- `scraping_max_depth: 3`
- `scraping_timeout: 10`
- `scraping_same_domain_only: true`

---

## 📊 Performance Considerations

### Embedding Models

**Model Size vs. Quality:**
- Smaller models (768 dimensions): Faster, less memory, slightly lower quality
- Larger models (1024 dimensions): Better quality, more resources

**GPU Acceleration:**
- HuggingFace models automatically use GPU when available
- Significantly faster embedding generation
- Recommended for production deployments

### Web Scraping

**Resource Usage:**
- Memory scales with max_pages * average_page_size
- CPU usage primarily during text processing
- Network bandwidth for page downloads

**Optimization Tips:**
- Start with lower max_pages, increase as needed
- Use appropriate max_depth for your use case
- Enable same_domain_only to prevent scope creep
- Monitor scraping logs for performance issues

### Vector Database

**Pinecone Scaling:**
- Free tier: 1 index, limited storage
- Paid tiers: Multiple indexes, unlimited storage
- Query performance scales well with index size

---

## 🔒 Security Considerations

### API Tokens

- HuggingFace tokens are stored in the database
- Tokens should be encrypted at rest (implement in production)
- Use read-only tokens when possible

### Web Scraping

- Respects robots.txt (implement in production)
- Rate limiting prevents overwhelming target servers
- Same domain restriction prevents unauthorized crawling

### Block Words

Configure sensitive terms that should be filtered from responses:
```
Settings → Advanced → Block Words
```

---

## 🐛 Troubleshooting

### HuggingFace Model Loading Issues

**Problem:** Model fails to load
**Solutions:**
- Verify model name is correct (organization/model-name)
- Check HuggingFace token has necessary permissions
- Ensure sufficient disk space for model download
- Check internet connectivity

### Web Scraping Issues

**Problem:** Few or no pages scraped
**Solutions:**
- Verify starting URL is accessible
- Check max_pages and max_depth settings
- Review scraping logs for errors
- Ensure target site doesn't block bots

**Problem:** Scraping is slow
**Solutions:**
- Reduce max_pages or max_depth
- Increase timeout for slow sites
- Check network connectivity
- Consider scraping during off-peak hours

### Memory Issues

**Problem:** Out of memory errors
**Solutions:**
- Reduce batch size for embedding generation
- Lower max_pages for scraping
- Use smaller embedding models
- Enable GPU acceleration to offload CPU memory

---

## 📈 Future Enhancements

Potential additions for future versions:

1. **Advanced Scraping:**
   - JavaScript rendering support
   - PDF document scraping
   - Image and media extraction
   - Scheduled re-scraping

2. **Model Fine-tuning:**
   - In-app model fine-tuning
   - Training data management
   - Evaluation metrics

3. **Enhanced RAG:**
   - Multi-query retrieval
   - Contextual compression
   - Hybrid search (keyword + semantic)

4. **Monitoring:**
   - Scraping analytics
   - Model performance metrics
   - Cost tracking

---

## 📝 API Reference

### Advanced Config API

**Get Configuration:**
```
GET /api/v1/advanced-config?workspace_id={workspace_id}
```

**Create Configuration:**
```
POST /api/v1/advanced-config?workspace_id={workspace_id}
Body: { "advanced_config": { ... } }
```

**Update Configuration:**
```
PUT /api/v1/advanced-config?workspace_id={workspace_id}
Body: { "advanced_config": { ... } }
```

### Knowledge Base API

**Scrape Link:**
```
POST /api/v1/knowledge-base/link
Body: { "link": "https://example.com" }
Headers: { "workspace_id": "workspace_id" }
```

---

## 💡 Best Practices Summary

1. **Start Small:** Begin with conservative scraping settings and scale up
2. **Test Embeddings:** Try different models to find the best quality/performance balance
3. **Monitor Resources:** Watch memory and CPU usage during scraping
4. **Secure Tokens:** Protect HuggingFace tokens and API keys
5. **Regular Updates:** Keep dependencies updated for security and features
6. **Document Changes:** Keep track of configuration changes and their impact

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs for detailed error messages
3. Open an issue on GitHub with:
   - Clear description of the problem
   - Steps to reproduce
   - Relevant logs and error messages
   - Configuration details (sanitize sensitive data)

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-08
