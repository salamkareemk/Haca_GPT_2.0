import sys
sys.path.insert(0, '.')
from vector_store import ChromaVectorStore
from query_engine import QueryEngine

store = ChromaVectorStore(db_path='haca_main.db')
engine = QueryEngine(store)
context = engine.process_query('Who is the Tech School Faculty? List all of them.', k=25, score_threshold=0.25)
print('Length of context:', len(context))
print('Context sample:', context[:1000])
