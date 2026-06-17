import os
import sys
from chunker import TextChunker
from vector_store import ChromaVectorStore


def main(force: bool = False):
    """
    Populate the ChromaDB vector store with data from backend/data.
    
    Args:
        force: If True, clears existing collection and re-populates.
               If False (default), skips if DB already has documents.
    """
    print("=" * 60)
    print("HACA GPT — Vector Database Population")
    print("=" * 60)

    # Connect to the vector store first to check existing data
    print("Connecting to vector store...")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "haca_main.db")
    vector_store = ChromaVectorStore(db_path=db_path)

    existing_count = vector_store.collection.count()

    if existing_count > 0 and not force:
        print(f"\n[OK] Vector store already contains {existing_count} documents.")
        print("     Skipping re-population. Run with --force to re-populate.")
        print("\n[READY] Database is ready to use.")
        return

    if force and existing_count > 0:
        print(f"\n[!] Force mode: clearing {existing_count} existing documents...")
        vector_store.clear_collection()
        print("[OK] Collection cleared.")

    # Path to the data directory
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "data")
    if not os.path.exists(data_dir):
        print(f"\n[ERROR] Data directory not found at: {data_dir}")
        print("        Make sure backend/data/ exists and contains your data files.")
        return

    # Load and chunk data
    print(f"\nLoading data files from: {data_dir}")
    chunker = TextChunker()
    chunks = chunker.process_data_files(data_dir)

    if len(chunks) == 0:
        print("\n[ERROR] No chunks created. Check your data files in backend/data/")
        return

    print(f"\n[OK] Created {len(chunks)} chunks from data files.")

    # Store in vector DB
    print("\nStoring chunks in vector database...")
    count = vector_store.add_chunks(chunks)

    print("\n" + "=" * 60)
    print(f"[SUCCESS] Vector database populated with {count} document chunks!")
    print("[READY]   The chatbot is ready to answer questions.")
    print("=" * 60)


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    main(force=force_flag)
