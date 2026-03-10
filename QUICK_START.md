# 🚀 Production-Scale Chatbot Builder - Quick Start Guide

## What's New?

This update transforms the Low-Code Chatbot Builder into a production-ready platform with powerful new features:

### ✨ Key Features

1. **🤗 HuggingFace Model Integration**
   - Import any embedding model from HuggingFace Hub
   - Use pre-built models or your custom fine-tuned models
   - Automatic GPU acceleration support

2. **⚙️ Advanced Configuration**
   - Fine-tune embedding models
   - Configure text chunking strategies
   - Adjust LLM parameters (temperature, max tokens, etc.)
   - Set web scraping limits and behavior

3. **🕷️ Intelligent Web Scraping**
   - Recursively crawl entire websites
   - Configurable depth (how many links deep to follow)
   - Configurable scale (maximum pages to scrape)
   - Smart URL deduplication and domain filtering

4. **📚 Automatic Knowledge Base**
   - Scraped content automatically chunked and embedded
   - Stored in vector database for fast retrieval
   - Integrated with existing RAG pipeline

## Quick Start

### 1. Configure Your Model (Settings → Advanced)

**Choose an Embedding Model:**
```
Basic: multilingual-e5-large
Advanced: BAAI/bge-large-en-v1.5 (HuggingFace)
Custom: Your own fine-tuned model
```

**For Custom Models:**
1. Enter your HuggingFace API token
2. Toggle "Use Custom HuggingFace Model"
3. Enter model name (e.g., `your-org/your-model`)

### 2. Configure Web Scraping

**Recommended Settings:**

**For Small Sites (blogs, documentation):**
- Max Pages: 50
- Max Depth: 3
- Timeout: 10s
- Same Domain: ON

**For Large Sites (enterprise docs):**
- Max Pages: 200
- Max Depth: 4
- Timeout: 15s
- Same Domain: ON

### 3. Add a Website to Knowledge Base

1. Navigate to **Knowledge Base → Links**
2. Click **"Add Link"**
3. Enter website URL (e.g., `https://docs.example.com`)
4. Click **"Add Link"**

The system will:
- ✅ Crawl the website recursively
- ✅ Extract text from all pages
- ✅ Chunk content intelligently
- ✅ Generate embeddings
- ✅ Store in vector database
- ✅ Ready for chatbot queries!

## Configuration Guide

### Embedding Models

| Model | Dimensions | Best For |
|-------|-----------|----------|
| stsb-roberta-large | 1024 | General purpose, English |
| multilingual-e5-large | 1024 | Multiple languages |
| BAAI/bge-large-en-v1.5 | 1024 | High quality English |
| all-mpnet-base-v2 | 768 | Faster, less memory |
| Custom | Varies | Your specific domain |

### Text Chunking

**Chunk Size:** 500-1000 characters
- Smaller = More precise retrieval
- Larger = More context per chunk

**Chunk Overlap:** 50-200 characters
- Prevents context loss at boundaries
- Higher overlap = more redundancy

### Web Scraping

**Max Depth Explained:**
```
Depth 1: Just the starting page
Depth 2: Starting page + all linked pages
Depth 3: Starting page + linked pages + their links
...
```

**Max Pages:**
- Limits total pages crawled
- Prevents runaway scraping
- Recommended: Start low, increase if needed

## Examples

### Example 1: Scrape Product Documentation

```
URL: https://docs.yourproduct.com
Max Pages: 100
Max Depth: 4
Same Domain: ON
```

Result: Complete product documentation indexed and searchable

### Example 2: Scrape Company Blog

```
URL: https://blog.yourcompany.com
Max Pages: 50
Max Depth: 2
Same Domain: ON
```

Result: All blog posts indexed for customer support

### Example 3: Custom Domain Knowledge

```
Embedding Model: Custom (your-org/medical-embeddings)
HuggingFace Token: [your-token]
URL: https://medical-knowledge.example.com
```

Result: Specialized medical knowledge with domain-specific embeddings

## Troubleshooting

### "Model failed to load"
- ✅ Check model name spelling
- ✅ Verify HuggingFace token permissions
- ✅ Ensure internet connectivity
- ✅ Check available disk space

### "Few pages scraped"
- ✅ Increase Max Pages setting
- ✅ Increase Max Depth setting
- ✅ Check if target site blocks bots
- ✅ Verify starting URL is accessible

### "Out of memory"
- ✅ Use smaller embedding model (768 dimensions)
- ✅ Reduce Max Pages
- ✅ Enable GPU acceleration
- ✅ Reduce chunk size

## Best Practices

1. **Start Small**
   - Begin with conservative settings
   - Scale up based on needs
   - Monitor resource usage

2. **Test Your Models**
   - Try different embedding models
   - Compare retrieval quality
   - Balance quality vs. speed

3. **Respect Target Sites**
   - Use appropriate rate limits
   - Enable same-domain restriction
   - Check robots.txt compliance

4. **Monitor Performance**
   - Watch embedding generation time
   - Track scraping duration
   - Monitor vector database size

## Advanced Features

### RAG Fusion
Automatically enabled! Generates multiple query variations for better retrieval.

### GPU Acceleration
Automatically used when available! Significantly faster embedding generation.

### Batch Processing
Large scraping jobs automatically batched for efficiency.

### Metadata Tracking
Every chunk tagged with source URL, workspace, and knowledge base ID.

## Security Notes

⚠️ **HuggingFace Tokens:** Store securely, never commit to version control

⚠️ **Web Scraping:** Be respectful of target servers, follow their policies

⚠️ **Rate Limiting:** Built-in 0.5s delay between requests

## Need Help?

📖 **Full Documentation:** See `PRODUCTION_FEATURES.md` for comprehensive guide

🔧 **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md` for technical details

🐛 **Issues:** Check logs, review troubleshooting section, open GitHub issue

## What's Next?

This implementation is complete and production-ready! Future enhancements could include:

- 🎯 JavaScript rendering support (Selenium/Playwright)
- 📊 Scraping analytics dashboard
- 🔄 Scheduled re-scraping
- 🎨 Media extraction (images, PDFs)
- 🔐 Authentication support for protected pages

---

**Happy Building! 🚀**

Your chatbot can now learn from any website and use state-of-the-art models from HuggingFace!
