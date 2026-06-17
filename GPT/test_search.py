from vector_store import ChromaVectorStore

def main():
    vs = ChromaVectorStore(db_path='chroma2.db')
    res = vs.search('who are the faculty of tech school', k=10, score_threshold=0.0)
    for r in res:
        content_preview = r['content'][:60].replace('\n', ' ')
        print(f"{r['similarity_score']:.4f} | {r['source']} | chunk {r['chunk_index']} | {content_preview}")

if __name__ == '__main__':
    main()
