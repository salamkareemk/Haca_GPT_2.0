import os
import sys
sys.path.insert(0, '.')
from vector_store import ChromaVectorStore
from chunker import TextChunker

DB_PATH = 'haca_main.db'
DATA_DIR = 'backend/data'

print("Initializing DB...")
vector_store = ChromaVectorStore(db_path=DB_PATH, collection_name="haca_documents")
print("Clearing old collection...")
vector_store.clear_collection()

print(f"Processing files in {DATA_DIR}...")
chunker = TextChunker()
chunks = chunker.process_data_files(DATA_DIR)

if chunks:
    count = vector_store.add_chunks(chunks)
    print(f"[SUCCESS] Re-indexed {count} chunks into {DB_PATH}")
else:
    print("[ERROR] No chunks created. Check data directory.")
