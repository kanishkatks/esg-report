"""
Streamlit frontend for RAG Chatbot.
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .source-box {
        background-color: #f5f5f5;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 0.25rem;
        border-left: 3px solid #ff9800;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []


def check_backend_health() -> bool:
    """Check if the backend is healthy."""
    try:
        response = requests.get(f"{BACKEND_URL}/health/", timeout=5)
        return response.status_code == 200
    except:
        return False


def upload_document(file, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Upload a document to the backend."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        data = {}
        if metadata:
            data["metadata"] = json.dumps(metadata)

        response = requests.post(
            f"{BACKEND_URL}/documents/upload",
            files=files,
            data=data,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"Upload failed: {response.text}"}
    except Exception as e:
        return {"status": "error", "message": f"Upload error: {str(e)}"}


def send_chat_message(message: str, session_id: str = None) -> Dict[str, Any]:
    """Send a chat message to the backend."""
    try:
        payload = {
            "message": message,
            "session_id": session_id,
            "use_history": True
        }

        response = requests.post(
            f"{BACKEND_URL}/chat/",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Chat failed: {response.text}"}
    except Exception as e:
        return {"error": f"Chat error: {str(e)}"}


def get_document_stats() -> Dict[str, Any]:
    """Get document statistics from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/documents/stats", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to get stats"}
    except Exception as e:
        return {"error": str(e)}


def search_documents(query: str, limit: int = 5) -> Dict[str, Any]:
    """Search documents."""
    try:
        params = {"q": query, "limit": limit, "hybrid": True}
        response = requests.get(f"{BACKEND_URL}/search/", params=params, timeout=15)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Search failed: {response.text}"}
    except Exception as e:
        return {"error": f"Search error: {str(e)}"}


def render_sidebar():
    """Render the sidebar with controls and information."""
    st.sidebar.markdown("## 🤖 RAG Chatbot")

    # Backend health check
    if check_backend_health():
        st.sidebar.success("✅ Backend Connected")
    else:
        st.sidebar.error("❌ Backend Disconnected")
        st.sidebar.warning("Please ensure the backend is running at " + BACKEND_URL)
        return False

    # Document statistics
    st.sidebar.markdown("### 📊 Document Statistics")
    stats = get_document_stats()
    if "error" not in stats:
        st.sidebar.metric("Total Chunks", stats.get("total_chunks", 0))
    else:
        st.sidebar.error("Failed to load stats")

    # Document upload section
    st.sidebar.markdown("### 📁 Upload Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Choose files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Upload PDF, DOCX, or TXT files to add to the knowledge base"
    )

    if uploaded_files:
        if st.sidebar.button("Upload Files"):
            upload_progress = st.sidebar.progress(0)
            upload_status = st.sidebar.empty()

            for i, file in enumerate(uploaded_files):
                upload_status.text(f"Uploading {file.name}...")
                result = upload_document(file)

                if result.get("status") == "success":
                    st.sidebar.success(f"✅ {file.name} uploaded successfully")
                    if file.name not in st.session_state.uploaded_files:
                        st.session_state.uploaded_files.append(file.name)
                else:
                    st.sidebar.error(f"❌ {file.name}: {result.get('message', 'Upload failed')}")

                upload_progress.progress((i + 1) / len(uploaded_files))

            upload_status.text("Upload complete!")
            st.rerun()

    # Chat controls
    st.sidebar.markdown("### 💬 Chat Controls")
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.rerun()

    # Search section
    st.sidebar.markdown("### 🔍 Document Search")
    search_query = st.sidebar.text_input("Search documents", placeholder="Enter search terms...")
    if search_query and st.sidebar.button("Search"):
        with st.sidebar.spinner("Searching..."):
            search_results = search_documents(search_query)
            if "error" not in search_results:
                st.sidebar.success(f"Found {len(search_results.get('results', []))} results")
                # Store search results in session state to display in main area
                st.session_state.search_results = search_results
            else:
                st.sidebar.error(f"Search failed: {search_results['error']}")

    return True


def render_chat_interface():
    """Render the main chat interface."""
    st.markdown('<div class="main-header">🤖 RAG Chatbot</div>', unsafe_allow_html=True)

    # Display chat messages
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(
                    f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-message assistant-message"><strong>Assistant:</strong> {message["content"]}</div>',
                    unsafe_allow_html=True
                )

                # Display sources if available
                if "sources" in message and message["sources"]:
                    with st.expander("📚 Sources", expanded=False):
                        for i, source in enumerate(message["sources"][:3], 1):  # Show top 3 sources
                            st.markdown(
                                f'<div class="source-box">'
                                f'<strong>Source {i}:</strong> {source["filename"]}<br>'
                                f'<small>Score: {source["score"]:.3f}</small><br>'
                                f'{source["content_preview"]}'
                                f'</div>',
                                unsafe_allow_html=True
                            )

    # Chat input
    if prompt := st.chat_input("Ask me anything about your documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message immediately
        with chat_container:
            st.markdown(
                f'<div class="chat-message user-message"><strong>You:</strong> {prompt}</div>',
                unsafe_allow_html=True
            )

        # Get response from backend
        with st.spinner("Thinking..."):
            response = send_chat_message(prompt, st.session_state.session_id)

            if "error" not in response:
                # Update session ID
                st.session_state.session_id = response.get("session_id")

                # Add assistant response to chat history
                assistant_message = {
                    "role": "assistant",
                    "content": response["response"],
                    "sources": response.get("sources", [])
                }
                st.session_state.messages.append(assistant_message)

                # Display assistant response
                with chat_container:
                    st.markdown(
                        f'<div class="chat-message assistant-message"><strong>Assistant:</strong> {response["response"]}</div>',
                        unsafe_allow_html=True
                    )

                    # Display sources
                    if response.get("sources"):
                        with st.expander("📚 Sources", expanded=False):
                            for i, source in enumerate(response["sources"][:3], 1):
                                st.markdown(
                                    f'<div class="source-box">'
                                    f'<strong>Source {i}:</strong> {source["filename"]}<br>'
                                    f'<small>Score: {source["score"]:.3f}</small><br>'
                                    f'{source["content_preview"]}'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )
            else:
                st.error(f"Error: {response['error']}")

        st.rerun()


def render_search_results():
    """Render search results if available."""
    if hasattr(st.session_state, 'search_results') and st.session_state.search_results:
        st.markdown("### 🔍 Search Results")
        results = st.session_state.search_results.get("results", [])

        for i, result in enumerate(results, 1):
            with st.expander(f"Result {i}: {result['filename']} (Score: {result['score']:.3f})"):
                st.write(result["content"])
                if result.get("metadata"):
                    st.json(result["metadata"])


def main():
    """Main application function."""
    initialize_session_state()

    # Render sidebar and check backend connection
    if not render_sidebar():
        st.error("Cannot connect to backend. Please check your configuration.")
        return

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        render_chat_interface()

    with col2:
        render_search_results()

        # Display uploaded files
        if st.session_state.uploaded_files:
            st.markdown("### 📁 Uploaded Files")
            for filename in st.session_state.uploaded_files:
                st.text(f"✅ {filename}")


if __name__ == "__main__":
    main()
