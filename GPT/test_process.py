from vector_store import ChromaVectorStore
from query_engine import QueryEngine

def main():
    vs = ChromaVectorStore(db_path='chroma2.db')
    engine = QueryEngine(vs)
    context = engine.process_query('who are the faculty of tech school', k=10)
    print("CONTEXT LENGTH:", len(context))
    print("CONTEXT PREVIEW:\n", context[:500])
    
if __name__ == '__main__':
    main()
