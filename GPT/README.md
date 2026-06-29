# HACA GPT 2.0 — Educational Institution RAG System

> **Retrieval-Augmented Generation (RAG)** system and interactive web application for **Haris & Co Academy (HACA)**.  
> Provides intelligent, context-aware answers about academy courses, fees, batch schedules, faculty mentors, placement stats, and enrollment policies — powered by ChromaDB, Sentence-Transformers, and OpenAI GPT integration.

---

## 🚦 Project Status

| Component | Task | Status |
| :--- | :--- | :--- |
| **Phase 1** | Text Chunking (`chunker.py`) | ✅ Complete |
| **Phase 2** | Vector Embeddings & ChromaDB (`vector_store.py`) | ✅ Complete |
| **Phase 3** | Query Retrieval & Context Building (`query_engine.py`) | ✅ Complete |
| **Phase 4** | LLM Integration & Answer Generation (`llm_integration.py`) | ✅ Complete |
| **Backend API** | Flask REST API Server (`server.py`) | ✅ Complete |
| **Frontend UI** | Premium Glassmorphism Chat Interface (`frontend/`) | ✅ Complete |
| **Testing** | E2E System Tests & Verification (`test_pipeline.py`) | ✅ Complete |

> **Last Build Verification:** All test suites passing, database population verified, web UI fully interactive, and API endpoints verified online.

---

## 🌟 Key Features in HACA GPT 2.0

*   🎨 **Premium Glassmorphic Dark UI:** A sleek, award-winning dark theme (`#0a0a0f`) featuring beautiful frosted-glass cards, golden/amber gradients, modern typography (Inter), and hover interactions.
*   ⌨️ **Real-Time Typing Animation:** Animated thinking bubbles that keep users engaged while the RAG model synthesizes information.
*   ⚡ **Typewriter Effect:** Animated, word-by-word response reveal for comfortable, high-fidelity reading.
*   🏷️ **Source Badges:** Automatically scans the context and presents beautiful labels of files referenced in the generation.
*   📊 **Confidence Meter:** A visual grading bar showing the estimated confidence (0.0 to 1.0) of each response.
*   💡 **Suggested Follow-Ups & Starter Questions:** Dynamically parses 3 relevant follow-up questions from the LLM prompt to suggest next steps. Also features clickable starter chips on initial load.
*   🔄 **Safe Database Re-Indexing:** An API endpoint (`/api/repopulate`) and dedicated scripts (`populate_db.py --force` and `repopulate.py`) to clear and rebuild the database from raw files without database locks.
*   🚀 **Auto-Initialization:** The server detects database state at startup and auto-populates it if the document count falls below threshold.
*   🔑 **Dual Provider Setup:** Plug-and-play architecture featuring `OpenAIProvider` (configured for `gpt-4o-mini`) and `MockProvider` (zero-dependency local testing).
*   📁 **BOM/Windows Native Support:** Built-in safeguards against Windows text encoding bugs, handling UTF-8 with BOM files correctly.

---

## 📅 Table of Contents

1. [Architecture](#architecture)
2. [Project Structure](#project-structure)
3. [Setup & Installation](#setup--installation)
4. [Backend Components](#backend-components)
5. [Frontend Interface](#frontend-interface)
6. [REST API Reference](#rest-api-reference)
7. [Running the Application](#running-the-application)
8. [Testing Suite](#testing-suite)
9. [Bug Fixes & System Optimizations](#bug-fixes--system-optimizations)
10. [Project Metrics & Statistics](#project-metrics--statistics)

---

## 🗺️ Architecture

```
                  ┌──────────────────────────────┐
                  │   Data Sources (10 Files)    │
                  │   courses, fees, faculty...  │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │ Phase 1: chunker.py (tiktoken)│
                  │ - 450-token chunks, 80 overlap│
                  │ - Windows BOM-handling fixed │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │Phase 2: vector_store.py      │
                  │- all-MiniLM-L6-v2 (384-dim)  │
                  │- haca_main.db (ChromaDB)     │
                  └──────────────┬───────────────┘
                                 │
                  ┌──────────────┴───────────────┐
                  ▼                              ▼
      ┌──────────────────────┐        ┌──────────────────────┐
      │   Flask REST API     │        │  Streamlit Tester    │
      │   (server.py:5000)   │        │     (app.py)         │
      └──────────┬───────────┘        └──────────┬───────────┘
                 │                               │
                 ▼                               │
      ┌──────────────────────┐                   │
      │ Premium Glassmorphic │                   │
      │ Frontend Web App     │                   │
      └──────────┬───────────┘                   │
                 │                               │
                 ▼                               ▼
            ┌───────── User Queries / Messages ─────────┐
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────┐
│              Phase 3 & 4: RAG Pipeline                  │
│  - query_engine.py: preprocessing, search, filter       │
│  - llm_integration.py: prompts, citations, confidence   │
│  - OpenAI Provider (gpt-4o-mini) / Mock Provider        │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
HACA GPT 2.0/
├── .env                          # API keys and global env variables
├── chroma.db/                    # Persistent vector DB (legacy/unused)
├── data set/                     # Copy of the original text datasets
├── whatsapp-web.js-main/         # WhatsApp Web library files (legacy/unused)
└── GPT/
    ├── README.md                 # This file
    ├── server.py                 # Flask REST API Server serving the premium frontend
    ├── app.py                    # Streamlit RAG Agent Tester (fallback interface)
    ├── chunker.py                # Phase 1: Text splitting, token counting (tiktoken)
    ├── vector_store.py           # Phase 2: Embedding generation & ChromaDB store
    ├── query_engine.py           # Phase 3: Semantic retrieval & context assembly
    ├── llm_integration.py        # Phase 4: Prompt builder, LLM connectors & post-processor
    ├── populate_db.py            # CLI DB seeding tool with --force flag
    ├── repopulate.py             # CLI DB clean and repopulation utility script
    ├── run.bat                   # Windows batch launcher (auto python interpreter detection)
    ├── test_pipeline.py          # Complete E2E system testing script
    ├── haca_main.db/             # Canonical persistent Chroma DB
    ├── backend/
    │   └── data/                 # Raw dataset files
    │       ├── .env              # Environment configurations for the backend
    │       ├── batches.txt       # Course batch schedules and capacities
    │       ├── courses.md        # Syllabus and school descriptions
    │       ├── Faculty.txt       # Faculty profiles and mentor names
    │       ├── Faq.txt           # FAQ entries
    │       ├── fees.txt          # Pricing, payment options, scholarships
    │       ├── institution_profile.md # HACA vision, mission, location details
    │       ├── Leads.txt         # Contact forms, lead capture fields
    │       ├── Placement.txt     # Placements percentages and reviews
    │       ├── Policies.txt      # Refund, attendance and code of conduct policies
    │       └── Testimonials.txt  # Student comments
    ├── frontend/                 # Premium Web Application folder
    │   ├── index.html            # Main markup page structure
    │   ├── style.css             # Glassmorphism theme, responsiveness and animations
    │   └── app.js                # Chat logic, event handlers, typewriter effects
    └── docs/                     # Additional phase-specific documentation
        ├── PHASE_2_DOCUMENTATION.md
        ├── PHASE_3_DOCUMENTATION.md
        ├── PHASE_4_DOCUMENTATION.md
        ├── PROJECT_SUMMARY.md
        └── IMPLEMENTATION_CHECKLIST.md
```

---

## 🛠️ Setup & Installation

### Prerequisites
*   Python 3.10+
*   pip
*   ~500 MB free disk space (to cache local Sentence-Transformer embedding models)
*   OpenAI API Key (Optional — falling back to `MockProvider` if missing)

### Step 1: Install Required Dependencies
Open a terminal in the `GPT` directory:
```bash
pip install flask flask-cors tiktoken chromadb sentence-transformers python-dotenv openai streamlit
```

### Step 2: Configure Environment Settings
Create a `.env` file in `GPT/backend/data/` or copy `.env` from your project directory. It should contain:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Step 3: Populate Database
Populate the vector database with the initial dataset chunks:
```bash
python populate_db.py
```
*(Run `python populate_db.py --force` to override and rebuild).*

---

## ⚙️ Backend Components

### Phase 1 — `chunker.py`
Splits raw text files into semantic chunks with metadata preservation.
*   **Tokenization Engine:** Uses tiktoken's `cl100k_base` encoder (matching OpenAI's GPT encoding).
*   **Configurations:** Splits into chunks of 450 tokens with an 80-token overlap between adjacent chunks.
*   **BOM Handling:** Features automatic encoding fallbacks to decode files with Byte Order Marks on Windows machines safely.

### Phase 2 — `vector_store.py`
Maintains embedding model downloads and handles storage in ChromaDB.
*   **Embedding Model:** Local `all-MiniLM-L6-v2` model (384 dimensions).
*   **Database Management:** Automatically manages connections. Uses `get_or_create_collection()` with cosine distance calculation space to eliminate database creation conflicts.

### Phase 3 — `query_engine.py`
Retrieves information based on queries.
*   **Normalizer:** Strips spaces, lowercases input, and filters punctuation.
*   **Filter & Deduplicator:** Applies a minimum similarity score threshold and discards duplicate text blocks.
*   **Context Formatter:** Formats retrieved blocks with numerical citation brackets (e.g., `[From courses.md]`).

### Phase 4 — `llm_integration.py`
Orchestrates prompt generation, model response querying, and post-generation analysis.
*   **Prompt Builder:** Injecting retrieved text alongside strict prompt guidelines (avoiding hallucinations, forcing comprehensive lists, and appending follow-up suggestion markers).
*   **Response Cleaner:** Removes double-spaces while preserving line breaks and carriage returns.
*   **Metadata Parser:** Extracts sources from context blocks and splits the response text to separate suggestions from answers.

---

## 💻 Frontend Interface

The web app is located in `GPT/frontend/` and served directly by the Flask server.

*   **Design Tokens:** Built around a luxury glassmorphism grid layout. Implements `backdrop-filter: blur(12px)` on glass containers, `#0a0a0f` deep dark backgrounds, and active gold buttons.
*   **Interactive Components:**
    *   **Quick Question buttons:** Clicking buttons in the sidebar immediately feeds queries to the agent.
    *   **Starter Chips:** Quick start options in the main chat box on welcome load.
    *   **Typing Bubble:** Fades in while query retrieval is executing to let users know the system is generating.
    *   **Metadata Badges:** Displays response metrics (confidence bar, source tags, and suggestion chips) at the base of answers.
    *   **Clear Chat utility:** Resets local and session storage.

---

## 🔌 REST API Reference

The Flask application exposes the following endpoints:

### 1. Chat Completion (`POST /api/chat`)
Accepts query inputs and returns RAG pipeline responses.
*   **Request JSON:**
    ```json
    {
      "message": "What is the fee for the digital marketing course?"
    }
    ```
*   **Response JSON:**
    ```json
    {
      "answer": "The fee for the AI-integrated Digital Marketing course at HACA is Rs. 50,000 for the offline program...\n\n**Sources:** Fees, Courses",
      "sources": ["fees.txt", "courses.md"],
      "confidence": 0.85,
      "follow_ups": [
        "What is the duration of the digital marketing program?",
        "Are there any scholarship schemes?",
        "What does the digital marketing curriculum cover?"
      ],
      "is_valid": true,
      "context_length": 1420
    }
    ```

### 2. Service Health Check (`GET /api/health`)
Returns backend operational status.
*   **Response JSON:**
    ```json
    {
      "status": "ok",
      "documents_indexed": 47,
      "llm_available": true,
      "pipeline_ready": true
    }
    ```

### 3. Pipeline Metrics (`GET /api/stats`)
Lists statistics from ChromaDB and the pipeline configuration.
*   **Response JSON:**
    ```json
    {
      "documents_indexed": 47,
      "data_directory": "C:\\path\\to\\backend\\data",
      "pipeline": {
        "llm_available": true,
        "pipeline_components": ["QueryEngine", "PromptBuilder", "LLMProvider", "ResponseProcessor"]
      },
      "vector_store": {
        "collection_name": "haca_documents",
        "total_documents": 47,
        "db_path": "C:\\path\\to\\haca_main.db",
        "embedding_dimension": 384
      }
    }
    ```

### 4. Re-populate database (`POST /api/repopulate`)
Clears existing database collections and re-indexes raw files.
*   **Response JSON:**
    ```json
    {
      "success": true,
      "message": "Successfully indexed 47 chunks.",
      "chunks_added": 47
    }
    ```

---

## 🚀 Running the Application

### Option A: Complete Web App with Flask (Recommended)
This runs the Flask REST API server and serves the premium Glassmorphic frontend at the root path.
*   **On Windows:** Double-click `run.bat` in the `GPT/` folder.
*   **Via Command Line:**
    ```bash
    python server.py
    ```
Open your browser and navigate to **`http://localhost:5000`**.

### Option B: Fallback Streamlit Interface
Streamlit can be used to run a quick test on the RAG pipeline.
*   **Command:**
    ```bash
    streamlit run app.py
    ```
Open your browser and navigate to **`http://localhost:8501`**.

---

## 🧪 Testing Suite

To verify the integrity of the database connection, embedding generation, query retrieval, and LLM providers, run:
```bash
python test_pipeline.py
```
This triggers an automated system test that processes queries through all modules. It outputs validation scores and checks key configurations before integration.

---

## 🔧 Bug Fixes & System Optimizations

During recent updates, several critical issues were resolved:

1.  **Windows Unicode Encoding Bugs:** Fixed file ingestion errors by replacing standard file readers with BOM-handling fallbacks (`errors='ignore'`) in `chunker.py`.
2.  **Response Newline Collapsing:** Repaired a bug in the output formatter that collapsed paragraphs and list formatting into single lines. The system prompt cleaner now preserves double carriage returns (`\n\n`) for clean markdown layout structure.
3.  **Collection Initialization Errors:** Refactored ChromaDB collection setup logic to use `get_or_create_collection()` to prevent startup crashes when reconnecting to an existing database.
4.  **Redundant Data Seeding Safeguards:** Updated database seeding logic to verify document counts prior to populating. It will skip writing duplicate entries unless run with the `--force` flag.
5.  **Multi-Query DB Locks:** Implemented `/api/repopulate` to reload text files directly from memory, preventing resource conflicts and lock issues on ChromaDB files.

---

## 📊 Project Metrics & Statistics

| Metric | Value |
| :--- | :--- |
| **Total Ingested Data Files** | 10 files |
| **Total Database Chunks** | 47 chunks |
| **Average Token Size** | ~450 tokens/chunk |
| **Overlap Token Size** | 80 tokens |
| **Embedding Dimension Count** | 384 dimensions |
| **Persistent DB Instance** | ChromaDB (`haca_main.db`) |
| **Active LLM Provider Model** | `gpt-4o-mini` (OpenAI API) |
| **Fallback Provider Model** | `MockProvider` (Offline testing) |
| **Supported OS Environment** | Windows, Linux, macOS |

---

**Last Updated:** June 18, 2026 | Production Build Complete ✅
