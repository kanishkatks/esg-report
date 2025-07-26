# ESG Document Parser & FAISS Vector Database

A robust system for parsing ESG (Environmental, Social, and Governance) documents from PDF format and creating a searchable vector database using FAISS (Facebook AI Similarity Search).

## Features

- 🔍 **PDF Text Extraction**: Robust PDF parsing with error handling and validation
- 🧠 **Intelligent Text Chunking**: Smart text segmentation preserving sentence boundaries
- 🚀 **Vector Embeddings**: High-quality embeddings using sentence-transformers
- ⚡ **FAISS Vector Database**: Ultra-fast similarity search using Facebook's FAISS library
- 🔧 **Configurable**: Environment-based configuration for flexibility
- 📝 **Comprehensive Logging**: Detailed logging for monitoring and debugging
- 🛡️ **Error Handling**: Robust error handling and recovery mechanisms
- 📈 **Batch Processing**: Memory-efficient processing of large documents
- 🔍 **Interactive Search**: Command-line search interface with multiple modes

## Why FAISS?

FAISS (Facebook AI Similarity Search) offers several advantages over traditional vector databases:

- **⚡ Ultra-fast**: Optimized for similarity search with billions of vectors
- **💾 Memory Efficient**: Requires no external database server
- **🔧 Simple Setup**: No Docker containers or complex configurations
- **📊 Scalable**: Handles large document collections efficiently
- **🎯 Accurate**: State-of-the-art similarity search algorithms

## Prerequisites

- Python 3.8+
- At least 4GB RAM recommended
- No external database required (FAISS runs locally)

## Installation

1. **Clone the repository** (or ensure you have all files)

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   Copy and modify the `.env` file as needed:
   ```bash
   # Edit .env with your preferred settings
   ```

## Configuration

The system uses environment variables for configuration. Key settings in `.env`:

```env
# Document Processing
DOCS_DIRECTORY=docs
INDEX_DIRECTORY=vectorstore
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2
BATCH_SIZE=32

# Logging
LOG_LEVEL=INFO
LOG_FILE=esg_parser.log
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCS_DIRECTORY` | `docs` | Directory containing PDF/text files |
| `INDEX_DIRECTORY` | `vectorstore` | Directory for FAISS index files |
| `CHUNK_SIZE` | `500` | Maximum characters per text chunk |
| `CHUNK_OVERLAP` | `50` | Character overlap between chunks |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `BATCH_SIZE` | `32` | Batch size for processing |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | `esg_parser.log` | Log file path |

## Usage

### Quick Start

```bash
# Run the complete pipeline
python run_pipeline.py
```

This will:
1. Extract text from PDFs in the `docs/` directory
2. Create intelligent text chunks
3. Generate vector embeddings
4. Build and save FAISS index
5. Demonstrate search functionality

### Step-by-Step Usage

#### Step 1: Prepare Documents

Place your PDF documents in the `docs/` directory (or the directory specified in `DOCS_DIRECTORY`).

#### Step 2: Extract Text from PDFs (Optional)

```bash
python parse_pdf.py
```

#### Step 3: Create FAISS Vector Database

```bash
python vector-database.py
```

#### Step 4: Search Documents

**Interactive Search:**
```bash
python search_documents.py
```

**Single Query:**
```bash
python search_documents.py --query "environmental sustainability" --k 5
```

**Batch Search:**
```bash
python search_documents.py --batch queries.txt --output results.json --k 10
```

### Advanced Usage

**Skip PDF extraction (use existing text files):**
```bash
python run_pipeline.py --skip-pdf
```

**Search demonstration only:**
```bash
python run_pipeline.py --search-only
```

**Get help:**
```bash
python run_pipeline.py --help
```

## Project Structure

```
esg-report/tools/esg_parser/
├── docs/                          # Document directory
│   ├── PE-43-2024-INIT_en.pdf    # Sample ESG regulation PDF
│   └── PE-43-2024-INIT_en.txt    # Extracted text
├── vectorstore/                   # FAISS database files
│   ├── faiss.index              # FAISS similarity index
│   ├── metadata.pkl             # Document metadata
│   ├── texts.pkl                # Original text chunks
│   └── config.pkl               # Database configuration
├── parse_pdf.py                   # PDF text extraction
├── vector-database.py             # FAISS vector database creation
├── search_documents.py            # Search interface
├── run_pipeline.py                # Complete pipeline runner
├── requirements.txt               # Python dependencies
├── .env                          # Environment configuration
├── .gitignore                    # Git ignore rules
├── esg_parser.log                # Application logs
└── README.md                     # This file
```

## Search Functionality

### Interactive Search Mode

```bash
python search_documents.py
```

Features:
- Real-time query input
- Configurable number of results
- Detailed result display with scores
- Source file information

### Programmatic Search

```python
from vector_database import ESGFAISSVectorDatabase

# Initialize and load database
db = ESGFAISSVectorDatabase()
db.load_index()
db.load_embedding_model()

# Search
results = db.search("environmental sustainability", k=5)

for result in results:
    print(f"Score: {result['similarity_score']:.3f}")
    print(f"Source: {result['metadata']['source']}")
    print(f"Text: {result['text'][:100]}...")
```

### Batch Search

Create a `queries.txt` file with one query per line:
```
environmental sustainability
ESG rating methodology
governance transparency
climate change risks
```

Run batch search:
```bash
python search_documents.py --batch queries.txt --output results.json
```

## Performance

### FAISS Performance Benefits

- **Search Speed**: Sub-millisecond search times for thousands of documents
- **Memory Usage**: Efficient memory usage with configurable batch processing
- **Scalability**: Handles large document collections (tested with 100k+ chunks)
- **No Dependencies**: No external database servers required

### Optimization Tips

1. **Adjust batch size**: Increase `BATCH_SIZE` for faster processing on high-memory systems
2. **Optimize chunk size**: Experiment with `CHUNK_SIZE` for your document types
3. **Use GPU**: Install `sentence-transformers[gpu]` for GPU acceleration
4. **Index optimization**: FAISS supports various index types for different use cases

## Troubleshooting

### Common Issues

1. **Memory Issues**
   ```bash
   # Reduce batch size in .env
   BATCH_SIZE=16
   ```

2. **Slow Embedding Generation**
   ```bash
   # Use a smaller/faster model
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   ```

3. **PDF Processing Errors**
   - Ensure PDFs are not corrupted
   - Check file permissions
   - Review logs for specific error messages

4. **Search Returns No Results**
   - Verify FAISS index exists in `vectorstore/`
   - Check if documents were processed correctly
   - Try different query terms

### Logs and Debugging

- Application logs: `esg_parser.log`
- Set `LOG_LEVEL=DEBUG` for detailed debugging
- Check vectorstore directory for index files

## API Reference

### ESGFAISSVectorDatabase Class

**Main Methods:**
- `run_pipeline()`: Complete pipeline execution
- `load_index()`: Load existing FAISS index
- `search(query, k=5)`: Search for similar documents
- `get_statistics()`: Get database statistics

**Search Result Format:**
```python
{
    'rank': 1,
    'text': 'document text chunk...',
    'metadata': {
        'source': 'filename.txt',
        'chunk_index': 0,
        'chunk_size': 450,
        'file_path': 'docs/filename.txt'
    },
    'distance': 0.234,
    'similarity_score': 0.876
}
```

## Comparison: FAISS vs Weaviate

| Feature | FAISS | Weaviate |
|---------|-------|----------|
| **Setup** | ✅ Simple (no external services) | ❌ Complex (Docker required) |
| **Speed** | ✅ Ultra-fast | ⚡ Fast |
| **Memory** | ✅ Efficient | ⚡ Good |
| **Scalability** | ✅ Excellent | ✅ Excellent |
| **Dependencies** | ✅ Minimal | ❌ Heavy |
| **Maintenance** | ✅ Low | ⚡ Medium |

## Contributing

1. Follow the existing code style and structure
2. Add comprehensive error handling
3. Include logging for debugging
4. Update documentation for new features
5. Test with various document types and sizes

## License

This project is part of the ESG reporting tools suite. Please refer to the main project license.
