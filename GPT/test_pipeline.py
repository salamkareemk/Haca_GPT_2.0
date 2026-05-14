"""
Test script for the complete HACA GPT RAG pipeline.

This script demonstrates the full functionality from query to answer generation.
"""

import os
import sys
from vector_store import ChromaVectorStore
from query_engine import QueryEngine
from llm_integration import HACARagPipeline, MockProvider, OpenAIProvider


def test_query_engine():
    """Test the QueryEngine independently."""
    print("🔍 Testing QueryEngine...")

    try:
        # Initialize components
        vs = ChromaVectorStore()
        engine = QueryEngine(vs)

        # Test query
        query = "What are the fees for courses?"
        context = engine.process_query(query, k=3)

        print(f"✅ Query: {query}")
        print(f"✅ Context length: {len(context)} characters")
        print(f"✅ Context preview: {context[:200]}...")

        return True
    except Exception as e:
        print(f"❌ QueryEngine test failed: {e}")
        return False


def test_rag_pipeline():
    """Test the complete RAG pipeline."""
    print("\n🤖 Testing RAG Pipeline...")

    try:
        # Initialize components
        vs = ChromaVectorStore()
        engine = QueryEngine(vs)

        # Use mock provider for testing (no API key needed)
        llm_provider = MockProvider()
        pipeline = HACARagPipeline(vs, llm_provider, engine)

        # Test queries
        test_queries = [
            "What are the course fees?",
            "When do batches start?",
            "What is the placement rate?"
        ]

        for query in test_queries:
            result = pipeline.answer_question(query)

            print(f"\n📝 Query: {query}")
            print(f"📄 Answer: {result['answer'][:100]}...")
            print(f"🔗 Sources: {result['sources']}")
            print(f"📊 Confidence: {result['confidence']:.2f}")
            print(f"✅ Valid: {result['is_valid']}")

        return True
    except Exception as e:
        print(f"❌ RAG Pipeline test failed: {e}")
        return False


def test_openai_provider():
    """Test OpenAI provider if API key is available."""
    print("\n🔑 Testing OpenAI Provider...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OpenAI API key not found. Skipping OpenAI test.")
        print("   Set OPENAI_API_KEY environment variable to test OpenAI integration.")
        return True

    try:
        provider = OpenAIProvider(api_key=api_key)
        print("✅ OpenAI provider initialized successfully")

        # Quick test with simple prompt
        test_prompt = "Say 'Hello from HACA GPT!' in one sentence."
        response = provider.generate(test_prompt)
        print(f"✅ OpenAI response: {response}")

        return True
    except Exception as e:
        print(f"❌ OpenAI provider test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 HACA GPT - Complete System Test")
    print("=" * 50)

    # Test individual components
    query_engine_ok = test_query_engine()
    rag_pipeline_ok = test_rag_pipeline()
    openai_ok = test_openai_provider()

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Query Engine: {'✅ PASS' if query_engine_ok else '❌ FAIL'}")
    print(f"RAG Pipeline: {'✅ PASS' if rag_pipeline_ok else '❌ FAIL'}")
    print(f"OpenAI Provider: {'✅ PASS' if openai_ok else '❌ FAIL'}")

    all_pass = all([query_engine_ok, rag_pipeline_ok, openai_ok])
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_pass else '❌ SOME TESTS FAILED'}")

    if all_pass:
        print("\n🎉 Backend is ready for frontend integration!")
        print("Next steps:")
        print("1. Create a web API (FastAPI/Flask)")
        print("2. Build a chat interface (React/Streamlit)")
        print("3. Add user authentication")
        print("4. Deploy to production")
    else:
        print("\n🔧 Please fix the failing tests before proceeding to frontend.")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())