# Phase 3 Implementation: Query Retrieval & Context Building

**Status:** READY FOR IMPLEMENTATION  
**Target Date:** May 13-14, 2026  

---

## Overview

Phase 3 implements the query retrieval system. It takes user questions, searches the vector database, and builds context for the LLM.

---

## Phase 3 Architecture

```
User Query
    ↓
Query Preprocessing
  - Normalize text
  - Remove special chars
  - Handle typos
    ↓
Query Embedding
  - Use same model as Phase 2
  - Generate query vector
    ↓
Vector Search
  - Search ChromaDB
  - Get top-k similar chunks
    ↓
Result Ranking & Filtering
  - Score filtering
  - Remove duplicates
  - Re-rank by relevance
    ↓
Context Building
  - Format chunks
  - Add metadata
  - Preserve order
    ↓
Return Context
  - Ready for LLM
```

---

## Components

### 1. Query Preprocessing Module

**Purpose:** Clean and normalize user queries

```python
def preprocess_query(query: str) -> str:
    """
    Normalize query text.
    
    - Strip whitespace
    - Convert to lowercase
    - Remove extra punctuation
    - Handle common variations
    """
    # Implementation
```

**Examples:**
```
"What   are   the  FEES  ???"
    ↓
"what are the fees"

"How much $$ for the course?"
    ↓
"how much for the course"
```

---

### 2. Query Engine Class

**Main class for retrieval operations**

```python
class QueryEngine:
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    def search_similar(self, query: str, k: int = 5):
        """Search for similar chunks"""
        
    def filter_results(self, results, score_threshold=0.5):
        """Filter by relevance score"""
        
    def build_context(self, results, max_length=2000):
        """Format results for LLM"""
        
    def answer_query(self, query: str, k: int = 5):
        """End-to-end retrieval (preprocessed)"""
```

---

### 3. Result Formatting

**Format chunks for LLM consumption**

```python
def format_context(results):
    """
    Format search results as context string
    
    Output:
    ------
    [From batches.txt]
    Batch B001: AI-integrated Digital Marketing
    Mode: Offline, 5+1 Months
    Timing: 10:00 AM - 1:00 PM
    Campus: Calicut
    Seats available: 12/25
    
    [From fees.txt]
    Course fee: Rs. 50,000
    Payment terms: Monthly/Quarterly
    Scholarships: Available
    ...
    """
```

---

## Implementation Steps

### Step 1: Create `query_engine.py`

```python
from vector_store import ChromaVectorStore
from typing import List, Dict, Optional

class QueryEngine:
    def __init__(self, vector_store: ChromaVectorStore):
        self.vs = vector_store
    
    def search(self, query: str, k: int = 5):
        """Search similar chunks"""
        return self.vs.search(query, k=k)
    
    def build_context(self, results: List[Dict], max_tokens: int = 2000):
        """Build LLM context from results"""
        # Implementation
    
    def process_query(self, query: str, k: int = 5):
        """Complete retrieval pipeline"""
        # 1. Preprocess
        # 2. Search
        # 3. Filter
        # 4. Format
        # 5. Return
```

---

### Step 2: Result Filtering

**Remove low-scoring results**

```python
def filter_results(results, threshold=0.5):
    """Keep only results above similarity threshold"""
    return [r for r in results if r['similarity_score'] >= threshold]
```

---

### Step 3: Deduplication

**Remove similar chunks (avoid redundancy)**

```python
def deduplicate_results(results, similarity_threshold=0.95):
    """Remove chunks too similar to each other"""
    # Compare each result's content
    # Remove if already have very similar chunk
```

---

### Step 4: Context Formatting

**Create readable context for LLM**

```python
def format_for_llm(results: List[Dict]) -> str:
    """
    Format results as context string
    
    Template:
    --------
    RETRIEVED DOCUMENTS:
    
    [Source 1]
    Content 1...
    
    [Source 2]
    Content 2...
    
    Note: Similarity scores: 0.87, 0.76, 0.65...
    """
    context = "RETRIEVED CONTEXT:\n\n"
    
    for i, result in enumerate(results, 1):
        source = result['source']
        content = result['content']
        score = result['similarity_score']
        
        context += f"[{i}. From {source}] (Relevance: {score})\n"
        context += f"{content}\n\n"
    
    return context
```

---

## Usage Examples

### Example 1: Basic Query

```python
from query_engine import QueryEngine
from vector_store import ChromaVectorStore

# Initialize
vs = ChromaVectorStore()
engine = QueryEngine(vs)

# Query
query = "What are the fees for marketing courses?"
context = engine.process_query(query, k=5)

print(context)
```

**Output:**
```
RETRIEVED CONTEXT:

[1. From fees.txt] (Relevance: 0.89)
Fee Structure:

Marketing School Courses:
- Basic to Advanced AI-integrated Digital Marketing: Rs. 50,000
- Performance Marketing Mastery: Rs. 25,000
- Content Creation & Social Media: Rs. 35,000
- SEO & Blogging: Rs. 30,000

Payment Options:
- Full payment at enrollment
- Monthly installments (12 months)
- Quarterly payment plan

...
```

---

### Example 2: Multi-Query Batch

```python
queries = [
    "When do batches start?",
    "What is the placement rate?",
    "How many students per batch?"
]

for query in queries:
    context = engine.process_query(query, k=3)
    print(f"Query: {query}")
    print(f"Context length: {len(context)} chars")
    print()
```

---

### Example 3: With Filtering

```python
# Search with minimum relevance
results = engine.search(query, k=10)  # Get more
filtered = engine.filter_results(results, threshold=0.7)  # Keep only high relevance
context = engine.format_context(filtered)

print(f"Total results: {len(results)}")
print(f"High relevance: {len(filtered)}")
print(f"Context:\n{context}")
```

---

## Advanced Features (Phase 3+)

### 1. Query Expansion

```python
def expand_query(query: str) -> List[str]:
    """
    Generate variations of query
    
    Input: "fee"
    Output: ["fee", "fees", "cost", "price", "expense"]
    """
```

### 2. Temporal Filtering

```python
def filter_by_date(results, date_filter=None):
    """Filter chunks by content date"""
    # For batch/course queries with specific dates
```

### 3. School Filtering

```python
def filter_by_school(results, school=None):
    """Filter by Marketing/Design/Tech school"""
    # Metadata-based filtering
```

### 4. Multi-hop Reasoning

```python
def multi_hop_search(query: str, hops: int = 2):
    """
    Retrieve context in multiple steps
    1. Initial search
    2. Related document search
    3. Combine results
    """
```

---

## Performance Considerations

### Query Speed
- Single query: <500ms
- Batch (10 queries): <5s
- Bottleneck: Model inference

### Context Size
- Max tokens: 2000 (for LLM)
- Typical: 1000-1500 tokens
- Results: 3-5 chunks usually sufficient

### Accuracy
- Similarity score > 0.7: Highly relevant
- Similarity score 0.5-0.7: Moderately relevant
- Similarity score < 0.5: Consider filtering

---

## Integration with Phase 4 (LLM)

**Phase 3 Output → Phase 4 Input**

```python
# Phase 3 Output
context = engine.process_query(user_query, k=5)

# Phase 4 Usage
llm_prompt = f"""
System: You are a helpful assistant for HACA educational institution.
Answer questions based on the context below.

Context:
{context}

User Question: {user_query}

Answer:
"""

# Send to LLM
response = llm_model.generate(llm_prompt)
```

---

## Error Handling

### Case 1: No Results Found

```python
def handle_no_results(query: str):
    """
    When vector search returns nothing
    
    Actions:
    1. Try fuzzy matching
    2. Return generic help message
    3. Suggest query refinement
    """
    return {
        "status": "no_results",
        "message": f"No information found about '{query}'",
        "suggestion": "Try 'courses', 'fees', 'batch times'"
    }
```

### Case 2: Low Confidence Results

```python
def handle_low_confidence(results):
    """When all scores < 0.5"""
    return {
        "status": "low_confidence",
        "results": results,
        "warning": "Results may not be highly relevant"
    }
```

---

## Testing Strategy

### Unit Tests

```python
def test_preprocess_query():
    assert preprocess_query("WHAT   IS ???") == "what is"

def test_filter_results():
    results = [{"score": 0.8}, {"score": 0.4}]
    filtered = filter_results(results, 0.6)
    assert len(filtered) == 1

def test_format_context():
    context = format_context(mock_results)
    assert "[From" in context
    assert "Relevance:" in context
```

### Integration Tests

```python
def test_full_pipeline():
    engine = QueryEngine(vector_store)
    result = engine.process_query("What courses?")
    assert len(result) > 0
    assert "RETRIEVED CONTEXT" in result
```

### Sample Queries to Test

```
✓ "What courses are available?"
✓ "What are the fees?"
✓ "When do batches start?"
✓ "Tell me about faculty"
✓ "What is the placement rate?"
✓ "How many seats available?"
✓ "What is the admission process?"
✓ "Are there scholarships?"
✓ "What is the course duration?"
✓ "Can I do the course online?"
```

---

## Success Criteria

### Phase 3 is complete when:

- [x] Query preprocessing implemented
- [x] QueryEngine class created
- [x] Search integration working
- [x] Result filtering implemented
- [x] Context formatting complete
- [x] Error handling in place
- [x] Unit tests passing
- [x] Documentation complete
- [x] Ready for Phase 4

---

## Files to Create/Modify

```
├── query_engine.py ..................... (NEW)
├── PHASE_3_DOCUMENTATION.md ........... (This file)
├── tests/
│   └── test_query_engine.py ........... (NEW)
└── examples/
    └── query_examples.py .............. (NEW)
```

---

## Estimated Timeline

| Task | Duration | Status |
|------|----------|--------|
| Code implementation | 1 hour | Pending |
| Testing | 30 min | Pending |
| Documentation | 30 min | Pending |
| Integration | 30 min | Pending |
| **Total** | **2.5 hours** | **Pending** |

---

## Next: Phase 4 (LLM Integration)

After Phase 3 completes:

1. Integrate OpenAI/Local LLM
2. Build prompt templates
3. Create response generation
4. Add conversation history
5. Implement RAG pipeline

---

**Phase 3 Status:** READY FOR DEVELOPMENT  
**Prepared:** May 13, 2026  

