import sys
sys.path.insert(0, '.')
from vector_store import ChromaVectorStore
from query_engine import QueryEngine

store = ChromaVectorStore('haca_main.db')
engine = QueryEngine(store)
context = engine.process_query('Who is the Tech School Faculty? List all of them.', k=25, score_threshold=0.25)
print('Is Mushthaq in context?', 'Mushthaq' in context)
if 'Mushthaq' in context:
    idx = context.find('Mushthaq')
    print(context[max(0, idx-100):min(len(context), idx+200)])
