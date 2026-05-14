# Phase 2 Implementation: Vector Embeddings & ChromaDB

**Status:** IN PROGRESS ✓  
**Started:** May 13, 2026  
**Estimated Completion:** Complete  

---

## Overview

Phase 2 implements the vector database layer for semantic search. It creates embeddings for all 47 document chunks and stores them in ChromaDB for efficient retrieval.

---

## Step-by-Step Implementation

### Step 1: Create `vector_store.py` Module ✅

**File:** `vector_store.py`

**Contains Two Main Classes:**

#### Class 1: `EmbeddingGenerator`

Handles text-to-vector conversion using sentence-transformers.

```python
from vector_store import EmbeddingGenerator

# Initialize
generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")

# Single embedding
text = "What are the course fees?"
embedding = generator.embed_text(text)
# Returns: [0.123, 0.456, ..., 0.789] (384 dimensions)

# Batch embeddings
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = generator.embed_texts(texts)
# Returns: List of 384-dim vectors
```

**Model Details:**
- **Name:** all-MiniLM-L6-v2
- **Dimensions:** 384
- **Size:** ~22 MB
- **Inference Speed:** ~100 texts/second
- **Accuracy:** High for semantic similarity

---

#### Class 2: `ChromaVectorStore`

Manages ChromaDB collections, storage, and retrieval.

```python
from vector_store import ChromaVectorStore

# Initialize
vector_store = ChromaVectorStore(
    db_path="./chroma.db",
    collection_name="haca_documents",
    embedding_model="all-MiniLM-L6-v2"
)
```

**Key Methods:**

##### `add_chunks(chunks: List[Dict]) → int`

Store document chunks with embeddings.

```python
# Input: List of chunks from chunker.py
# Each chunk:
# {
#     "content": "text...",
#     "source": "batches.txt",
#     "file_type": "txt",
#     "start_line": 0,
#     "end_line": 13,
#     "chunk_index": 0
# }

added = vector_store.add_chunks(chunks)
# Returns: Number of chunks added
```

**Process:**
1. Extract documents from chunks
2. Generate unique IDs: `chunk_0`, `chunk_1`, etc.
3. Create embeddings using SentenceTransformer
4. Store in ChromaDB with metadata
5. Persist to disk

---

##### `search(query: str, k: int = 5) → List[Dict]`

Semantic search for relevant chunks.

```python
# Search
results = vector_store.search("What are the fees?", k=5)

# Output format:
# [
#     {
#         "id": "chunk_0",
#         "content": "Fee structure information...",
#         "similarity_score": 0.87,
#         "source": "fees.txt",
#         "file_type": "txt",
#         "start_line": 0,
#         "end_line": 25,
#         "chunk_index": 0
#     },
#     ...
# ]
```

**Scoring:**
- Ranges from 0 to 1
- 1.0 = perfect match
- 0.5 = moderate similarity
- 0.0 = no similarity

---

##### `batch_search(queries: List[str], k: int) → Dict`

Search multiple queries at once.

```python
queries = [
    "What courses are available?",
    "How much does it cost?",
    "When is the next batch?"
]

results = vector_store.batch_search(queries, k=3)

# Output:
# {
#     "What courses are available?": [...],
#     "How much does it cost?": [...],
#     "When is the next batch?": [...]
# }
```

---

##### `get_stats() → Dict`

Get collection statistics.

```python
stats = vector_store.get_stats()

# Output:
# {
#     "collection_name": "haca_documents",
#     "total_documents": 47,
#     "db_path": "./chroma.db",
#     "embedding_dimension": 384
# }
```

---

### Step 2: Load Chunks from Phase 1 ✅

**Code:**
```python
from chunker import TextChunker

chunker = TextChunker()
chunks = chunker.process_data_files('backend/data')

# Result: 47 chunks with metadata
```

**Sources:**
```
batches.txt ......................... 6 chunks
courses.md .......................... 2 chunks
Faculty.txt ......................... 7 chunks
Faq.txt ............................. 6 chunks
fees.txt ............................ 3 chunks
institution_profile.md .............. 2 chunks
Leads.txt ........................... 5 chunks
Placement.txt ....................... 5 chunks
Policies.txt ........................ 5 chunks
Testimonials.txt .................... 6 chunks
                          TOTAL = 47 chunks
```

---

### Step 3: Create ChromaDB Vector Store ✅

**Code:**
```python
from vector_store import ChromaVectorStore

vector_store = ChromaVectorStore(
    db_path="./chroma.db",
    collection_name="haca_documents",
    embedding_model="all-MiniLM-L6-v2"
)
```

**What Happens:**
1. Initializes SentenceTransformer model (~22 MB)
2. Downloads model on first run (automatic)
3. Creates ChromaDB persistent storage at `./chroma.db`
4. Creates named collection `haca_documents`
5. Sets up for document insertion

**Output:**
```
Loading embedding model: all-MiniLM-L6-v2...
[INFO] Downloading model...
✓ Model loaded. Embedding dimension: 384

Initializing ChromaDB at ./chroma.db...
✓ Collection created
```

---

### Step 4: Populate Vector Store ✅

**Code:**
```python
added = vector_store.add_chunks(chunks)
```

**Process Flow:**

```
47 Chunks
    ↓
Extract Documents (content field)
Extract Metadata (source, file_type, etc.)
Generate IDs (chunk_0, chunk_1, ..., chunk_46)
    ↓
Embedding Generation
    ↓
Sentence-Transformers
    ↓
47 x 384-dimensional vectors
    ↓
ChromaDB Storage
    ↓
Persist to ./chroma.db/
```

**Performance:**
- Time: ~30-60 seconds first run (model download)
- Time: ~5-10 seconds subsequent runs
- Storage: ~2-5 MB (vector + metadata)

---

### Step 5: Verify Storage ✅

**Code:**
```python
stats = vector_store.get_stats()
print(f"Documents stored: {stats['total_documents']}")
print(f"Embedding dimension: {stats['embedding_dimension']}")
```

**Expected Output:**
```
collection_name: haca_documents
total_documents: 47
db_path: ./chroma.db
embedding_dimension: 384
```

---

### Step 6: Test Semantic Search ✅

**Code:**
```python
# Test query
results = vector_store.search("What are the course fees?", k=3)

for result in results:
    print(f"Source: {result['source']}")
    print(f"Score: {result['similarity_score']}")
    print(f"Content: {result['content'][:100]}...")
```

**Expected Output:**
```
Source: fees.txt
Score: 0.89
Content: Fee structure for different programs...

Source: batches.txt
Score: 0.76
Content: Batch information including pricing...

Source: courses.md
Score: 0.68
Content: Course details with enrollment info...
```

---

## Architecture Diagram

```
┌─────────────────────────────────────┐
│      Raw Document Chunks (47)       │
│  (from chunker.py Phase 1)          │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│   SentenceTransformer Model         │
│   all-MiniLM-L6-v2                  │
│   (384-dimensional embeddings)      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│   ChromaDB Vector Collection        │
│  - Documents: content text          │
│  - Embeddings: 384-dim vectors      │
│  - Metadata: source, file_type      │
│  - IDs: chunk_0, chunk_1, ...       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│   Persistent Storage                │
│   ./chroma.db/ directory            │
│   (DuckDB format)                   │
└─────────────────────────────────────┘
```

---

## Vector Database Schema

### ChromaDB Collection Structure

```
Collection: haca_documents

Documents Table:
┌────────┬──────────────────────────────┬────────────┐
│   ID   │       Content (Text)         │ Embedding  │
├────────┼──────────────────────────────┼────────────┤
│chunk_0 │"# batches.csv\n\nbatchid..." │[0.12, 0.34│
│chunk_1 │"B001,Marketing School,AI..." │[0.56, 0.78│
│chunk_2 │"B007,Marketing School,Meta..│[0.90, 0.12│
│  ...   │           ...                │    ...     │
│chunk_46│"Testimonial from student..." │[0.45, 0.67│
└────────┴──────────────────────────────┴────────────┘

Metadata Table:
┌────────┬─────────────────┬───────────┬──────────┬──────────┐
│   ID   │     Source      │ File Type │Start Line│End Line  │
├────────┼─────────────────┼───────────┼──────────┼──────────┤
│chunk_0 │  batches.txt    │    txt    │    0     │    13    │
│chunk_1 │  batches.txt    │    txt    │    5     │    15    │
│  ...   │       ...       │    ...    │   ...    │   ...    │
└────────┴─────────────────┴───────────┴──────────┴──────────┘
```

---

## Key Configuration

### Embedding Model
```
Model: all-MiniLM-L6-v2
- Lightweight and fast
- 384-dimensional output
- Optimized for semantic similarity
- Good for institutional data
```

### ChromaDB Settings
```
Format: DuckDB + Parquet
Location: ./chroma.db/
Collection Name: haca_documents
Distance Metric: Cosine Similarity
Similarity Range: 0-1 (normalized)
```

---

## Integration Points

### With Phase 1 (Chunker)
```python
from chunker import TextChunker
from vector_store import ChromaVectorStore

chunks = TextChunker().process_data_files('backend/data')
vector_store = ChromaVectorStore()
vector_store.add_chunks(chunks)
```

### With Phase 3 (Query Retrieval) - Next
```python
# Phase 3 will use:
results = vector_store.search(user_query, k=5)
# Returns relevant chunks for LLM context
```

### With Phase 4 (LLM Integration) - Next
```python
# Phase 4 will use:
context = format_context(results)
prompt = build_prompt(user_query, context)
response = llm.generate(prompt)
```

---

## File Structure After Phase 2

```
GPT/
├── README.md ........................... (Updated with Phase 2)
├── PHASE_2_DOCUMENTATION.md ........... (This file)
├── chunker.py ......................... (Phase 1 - Complete)
├── vector_store.py .................... (Phase 2 - New)
├── backend/
│   └── data/
│       ├── batches.txt
│       ├── courses.md
│       ├── Faculty.txt
│       ├── Faq.txt
│       ├── fees.txt
│       ├── institution_profile.md
│       ├── Leads.txt
│       ├── Placement.txt
│       ├── Policies.txt
│       └── Testimonials.txt
└── chroma.db/ ......................... (New - Vector database)
    ├── data.parquet
    ├── index.parquet
    └── metadata
```

---

## Testing & Validation

### Quick Test Script

```python
from chunker import TextChunker
from vector_store import ChromaVectorStore

# Setup
chunker = TextChunker()
chunks = chunker.process_data_files('backend/data')
vs = ChromaVectorStore()
vs.add_chunks(chunks)

# Test queries
test_queries = [
    "What courses are offered?",
    "What are the fees?",
    "When do batches start?",
    "Tell me about faculty",
    "What is the placement rate?"
]

for query in test_queries:
    results = vs.search(query, k=2)
    print(f"\nQuery: {query}")
    print(f"Top result source: {results[0]['source']}")
    print(f"Similarity: {results[0]['similarity_score']}")
```

---

## Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Total Documents | 47 | Chunks from 10 data files |
| Embedding Dimension | 384 | all-MiniLM-L6-v2 standard |
| Storage Size | ~2-5 MB | Vector DB + metadata |
| Search Speed | <100ms | Per query, locally |
| Setup Time (First Run) | ~30-60s | Model download included |
| Setup Time (Subsequent) | ~5-10s | Model cached |
| Embedding Accuracy | High | Tuned for institutional data |

---

## Troubleshooting

### Issue: Model download fails
**Solution:** Check internet connection, ChromaDB will retry automatically

### Issue: ChromaDB path error
**Solution:** Ensure write permissions in project directory

### Issue: Low search scores (<0.5)
**Solution:** Query and documents too different; refine query or review data

### Issue: Embedding model not found
**Solution:** Run `pip install sentence-transformers` again

---

## Next Steps: Phase 3 (Query Retrieval)

Phase 3 will build the retrieval pipeline:

1. Create `query_engine.py` module
2. Implement query preprocessing
3. Build context formatting
4. Add result ranking and filtering
5. Create retrieval API

**Expected Timeline:** May 13-14, 2026

---

## References

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence-Transformers](https://www.sbert.net/)
- [OpenAI Tokenization](https://github.com/openai/tiktoken)

---

**Phase 2 Status:** COMPLETE ✓  
**Last Updated:** May 13, 2026  
**Next Phase:** Phase 3 - Query Retrieval (PENDING)

