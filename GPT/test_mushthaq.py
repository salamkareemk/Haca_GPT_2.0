import sys
sys.path.insert(0, '.')
from vector_store import ChromaVectorStore
from query_engine import QueryEngine

store = ChromaVectorStore('haca_main.db')
engine = QueryEngine(store)
res = engine.vector_store.search("Mushthaq", k=5)
for r in res:
    print(r['source'], r['similarity_score'])
    print(r['content'][:200])
    print('-'*50)
