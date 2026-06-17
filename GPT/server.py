"""
HACA GPT 2.0 - Flask API Server
Serves the premium HTML frontend and provides the RAG pipeline as a REST API.
"""

import os
import sys
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# ─── Path Setup ───────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.absolute()
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR   = BASE_DIR / "backend" / "data"
ENV_FILE   = DATA_DIR / ".env"
DB_PATH    = str(BASE_DIR / "haca_main.db")   # single canonical DB path

# Load .env from backend/data/
try:
    from dotenv import load_dotenv
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
        print(f"[OK] Loaded environment from {ENV_FILE}")
    else:
        load_dotenv()
except ImportError:
    print("[WARN] python-dotenv not installed.")

# ─── Import Pipeline Components ───────────────────────────────────────────────
from vector_store import ChromaVectorStore
from query_engine  import QueryEngine
from llm_integration import HACARagPipeline, OpenAIProvider, MockProvider

# ─── Flask App ────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=str(FRONTEND_DIR))
CORS(app)

# ─── Globals ──────────────────────────────────────────────────────────────────
pipeline     = None
vector_store = None

# Expected minimum number of chunks from a full data load (400-token chunks from 10 files)
MIN_EXPECTED_CHUNKS = 40

# ─── Helpers ──────────────────────────────────────────────────────────────────
def _load_and_embed_all():
    """Chunk all files in backend/data and add them to the vector store."""
    from chunker import TextChunker
    print(f"  Loading data files from {DATA_DIR} ...")
    chunker = TextChunker()
    chunks  = chunker.process_data_files(str(DATA_DIR))
    if not chunks:
        print("  [WARN] No chunks created — check files in backend/data/")
        return 0
    count = vector_store.add_chunks(chunks)
    print(f"  [OK] Stored {count} chunks in DB.")
    return count


def initialize_pipeline():
    """Initialize the RAG pipeline once at startup."""
    global pipeline, vector_store

    print("\n" + "=" * 60)
    print("  HACA GPT 2.0 — Starting Up")
    print("=" * 60)

    # ── Step 1: Vector store ──────────────────────────────────────────────────
    print(f"\n[1/3] Connecting to vector store at {DB_PATH} ...")
    vector_store = ChromaVectorStore(
        db_path=DB_PATH,
        collection_name="haca_documents"
    )

    doc_count = vector_store.collection.count()
    print(f"  Current document count: {doc_count}")

    if doc_count < MIN_EXPECTED_CHUNKS:
        print(f"\n[!] DB has only {doc_count} docs (need >= {MIN_EXPECTED_CHUNKS}).")
        if doc_count > 0:
            print("    Clearing stale/incomplete collection ...")
            vector_store.clear_collection()
        print("    Auto-populating from backend/data/ ...")
        _load_and_embed_all()
    else:
        print(f"  [OK] Vector store ready with {doc_count} documents.")

    # ── Step 2: Query engine ──────────────────────────────────────────────────
    print("\n[2/3] Setting up query engine ...")
    query_engine = QueryEngine(vector_store)

    # ── Step 3: LLM provider ──────────────────────────────────────────────────
    print("\n[3/3] Setting up LLM provider ...")
    api_key = os.getenv("OPENAI_API_KEY", "")

    if api_key.startswith("sk-"):
        try:
            provider = OpenAIProvider(api_key=api_key, model="gpt-4o-mini")
            print("  [OK] OpenAI gpt-4o-mini ready.")
        except Exception as e:
            print(f"  [WARN] OpenAI init failed: {e}. Using MockProvider.")
            provider = MockProvider()
    else:
        print("  [WARN] No valid OPENAI_API_KEY. Using MockProvider.")
        provider = MockProvider()

    pipeline = HACARagPipeline(vector_store, provider, query_engine)

    final_count = vector_store.collection.count()
    print("\n" + "=" * 60)
    print(f"  [READY] HACA GPT is running!")
    print(f"  Docs indexed : {final_count}")
    print(f"  Open         : http://localhost:5000")
    print("=" * 60 + "\n")


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(str(FRONTEND_DIR), "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(str(FRONTEND_DIR), filename)


@app.route("/api/health", methods=["GET"])
def health():
    try:
        doc_count = vector_store.collection.count() if vector_store else 0
        stats     = pipeline.get_stats() if pipeline else {}
        return jsonify({
            "status"          : "ok",
            "documents_indexed": doc_count,
            "llm_available"   : stats.get("llm_available", False),
            "pipeline_ready"  : pipeline is not None
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def stats():
    try:
        if not pipeline:
            return jsonify({"error": "Pipeline not initialized"}), 503
        store_stats    = vector_store.get_stats()
        pipeline_stats = pipeline.get_stats()
        return jsonify({
            "vector_store"     : store_stats,
            "pipeline"         : pipeline_stats,
            "data_directory"   : str(DATA_DIR),
            "documents_indexed": store_stats.get("total_documents", 0)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        if not pipeline:
            return jsonify({"error": "Pipeline not ready. Please wait and try again."}), 503

        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' field"}), 400

        user_message = data["message"].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        if len(user_message) > 1000:
            return jsonify({"error": "Message too long (max 1000 chars)"}), 400

        result = pipeline.answer_question(
            user_query      = user_message,
            k               = 40,           # retrieve enough chunks to capture all mentors
            score_threshold = 0.10          # low threshold so we don't drop weakly-matched chunks
        )

        return jsonify({
            "answer"        : result.get("answer", ""),
            "sources"       : result.get("sources", []),
            "confidence"    : result.get("confidence", 0.0),
            "follow_ups"    : result.get("follow_ups", []),
            "is_valid"      : result.get("is_valid", False),
            "context_length": result.get("context_length", 0)
        })

    except Exception as e:
        print(f"[ERROR] /api/chat: {e}")
        return jsonify({
            "error"      : str(e),
            "answer"     : "I'm sorry, an error occurred. Please try again.",
            "sources"    : [],
            "confidence" : 0.0,
            "follow_ups" : [],
            "is_valid"   : False
        }), 500


@app.route("/api/repopulate", methods=["POST"])
def repopulate():
    """Re-index all data files into the vector store (safe — no external DB lock)."""
    try:
        if not vector_store:
            return jsonify({"error": "Vector store not initialized"}), 503

        print("[!] /api/repopulate called — clearing and re-indexing ...")
        vector_store.clear_collection()
        count = _load_and_embed_all()

        return jsonify({
            "success"     : True,
            "message"     : f"Successfully indexed {count} chunks.",
            "chunks_added": count
        })
    except Exception as e:
        print(f"[ERROR] /api/repopulate: {e}")
        return jsonify({"error": str(e)}), 500


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        initialize_pipeline()
    except Exception as e:
        print(f"\n[FATAL] Failed to initialize: {e}")
        print("Install deps: pip install flask flask-cors chromadb sentence-transformers tiktoken openai python-dotenv")
        sys.exit(1)

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
