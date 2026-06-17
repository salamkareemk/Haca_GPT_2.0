import os
import streamlit as st
from dotenv import load_dotenv

from vector_store import ChromaVectorStore
from query_engine import QueryEngine
from llm_integration import HACARagPipeline, MockProvider, OpenAIProvider

# Load environment variables from the specific backend data folder
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "data", ".env")
load_dotenv(env_path)

st.set_page_config(page_title="HACA GPT", page_icon="🤖", layout="wide")

st.title("🤖 HACA GPT - RAG Agent Tester")
st.markdown("Test the HACA GPT RAG Pipeline using this Streamlit interface.")

# Initialize components only once per session
@st.cache_resource
def init_pipeline(use_mock=False, api_key=None):
    vs = ChromaVectorStore()
    engine = QueryEngine(vs)
    
    if use_mock:
        provider = MockProvider()
    else:
        if not api_key:
            provider = MockProvider()
        else:
            provider = OpenAIProvider(api_key=api_key)
            
    pipeline = HACARagPipeline(vs, provider, engine)
    return pipeline

st.sidebar.header("Settings")
use_mock = st.sidebar.checkbox("Use Mock Provider (Testing without API Key)", value=False)
current_api_key = os.getenv("OPENAI_API_KEY")

if use_mock:
    st.sidebar.warning("Using Mock Provider (No real LLM calls)")
else:
    if not current_api_key:
        st.sidebar.error("OPENAI_API_KEY not found in environment. Falling back to MockProvider.")
    else:
        st.sidebar.success("Using OpenAI Provider")

try:
    pipeline = init_pipeline(use_mock, current_api_key)
    st.sidebar.success("✅ Pipeline initialized successfully")
except Exception as e:
    st.sidebar.error(f"❌ Failed to initialize pipeline: {e}")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("View Sources"):
                for source in message["sources"]:
                    st.write(f"- {source}")

# React to user input
if prompt := st.chat_input("Ask a question about HACA..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Query the pipeline
                result = pipeline.answer_question(prompt)
                
                answer = result.get('answer', "No answer generated.")
                sources = result.get('sources', [])
                confidence = result.get('confidence', 0.0)
                
                st.markdown(answer)
                st.caption(f"Confidence: {confidence:.2f}")
                
                if sources:
                    with st.expander("View Sources"):
                        for source in sources:
                            st.write(f"- {source}")
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "sources": sources
                })
            except Exception as e:
                st.error(f"Error generating response: {e}")
