"""
Chat endpoints for RAG-powered conversations.
"""

import logging
import uuid
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, ChatMessage
from app.services import weaviate_client, mistral_service

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory chat history storage (in production, use a proper database)
chat_sessions: Dict[str, List[ChatMessage]] = {}


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message using RAG (Retrieval-Augmented Generation).

    Args:
        request: Chat request with user message and optional session ID

    Returns:
        Generated response with sources and session information
    """
    try:
        # Generate or use existing session ID
        session_id = request.session_id or str(uuid.uuid4())

        # Initialize session if it doesn't exist
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []

        # Get chat history for context
        chat_history = []
        if request.use_history and session_id in chat_sessions:
            # Convert ChatMessage objects to dict format for Mistral
            chat_history = [
                {"role": msg.role, "content": msg.content}
                for msg in chat_sessions[session_id][-10:]  # Last 10 messages
            ]

        # Search for relevant documents
        search_results = await weaviate_client.hybrid_search(
            query=request.message,
            limit=5,  # Top 5 most relevant documents
            alpha=0.5  # Balance between BM25 and vector search
        )

        logger.info(f"Found {len(search_results)} relevant documents for query: {request.message}")

        # Generate response using Mistral with retrieved context
        response_text = await mistral_service.generate_rag_response(
            user_question=request.message,
            context_documents=search_results,
            chat_history=chat_history,
            temperature=0.7
        )

        # Store messages in session history
        user_message = ChatMessage(role="user", content=request.message)
        assistant_message = ChatMessage(role="assistant", content=response_text)

        chat_sessions[session_id].extend([user_message, assistant_message])

        # Prepare source information
        sources = []
        for result in search_results:
            sources.append({
                "document_id": result["document_id"],
                "filename": result["filename"],
                "content_preview": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                "score": result["score"],
                "metadata": result.get("metadata", {})
            })

        return ChatResponse(
            response=response_text,
            sources=sources,
            session_id=session_id
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")


@router.get("/sessions/{session_id}/history")
async def get_chat_history(session_id: str):
    """
    Get chat history for a specific session.

    Args:
        session_id: The chat session identifier

    Returns:
        List of chat messages in the session
    """
    try:
        if session_id not in chat_sessions:
            return {"messages": [], "session_id": session_id}

        messages = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in chat_sessions[session_id]
        ]

        return {
            "messages": messages,
            "session_id": session_id,
            "total_messages": len(messages)
        }

    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")


@router.delete("/sessions/{session_id}")
async def clear_chat_session(session_id: str):
    """
    Clear chat history for a specific session.

    Args:
        session_id: The chat session identifier to clear

    Returns:
        Confirmation of session clearing
    """
    try:
        if session_id in chat_sessions:
            del chat_sessions[session_id]
            return {"message": f"Session {session_id} cleared successfully"}
        else:
            return {"message": f"Session {session_id} not found"}

    except Exception as e:
        logger.error(f"Error clearing chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear chat session")


@router.get("/sessions")
async def list_chat_sessions():
    """
    List all active chat sessions.

    Returns:
        List of active session IDs with message counts
    """
    try:
        sessions = []
        for session_id, messages in chat_sessions.items():
            sessions.append({
                "session_id": session_id,
                "message_count": len(messages),
                "last_activity": messages[-1].timestamp.isoformat() if messages else None
            })

        return {
            "sessions": sessions,
            "total_sessions": len(sessions)
        }

    except Exception as e:
        logger.error(f"Error listing chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list chat sessions")


@router.post("/summarize")
async def summarize_conversation(session_id: str):
    """
    Generate a summary of a chat conversation.

    Args:
        session_id: The chat session to summarize

    Returns:
        Summary of the conversation
    """
    try:
        if session_id not in chat_sessions or not chat_sessions[session_id]:
            raise HTTPException(status_code=404, detail="Session not found or empty")

        # Convert chat messages to a format suitable for summarization
        conversation_text = ""
        for msg in chat_sessions[session_id]:
            conversation_text += f"{msg.role.title()}: {msg.content}\n\n"

        # Generate summary using Mistral
        summary_prompt = [
            {
                "role": "system",
                "content": "Provide a concise summary of the following conversation, highlighting the main topics discussed and key points."
            },
            {
                "role": "user",
                "content": f"Conversation to summarize:\n\n{conversation_text}"
            }
        ]

        summary = await mistral_service.generate_response(
            messages=summary_prompt,
            temperature=0.5,
            max_tokens=300
        )

        return {
            "session_id": session_id,
            "summary": summary,
            "message_count": len(chat_sessions[session_id])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to summarize conversation")


@router.post("/feedback")
async def submit_feedback(
    session_id: str,
    message_index: int,
    rating: int,
    feedback: Optional[str] = None
):
    """
    Submit feedback for a specific chat response.

    Args:
        session_id: The chat session ID
        message_index: Index of the message to rate
        rating: Rating from 1-5
        feedback: Optional text feedback

    Returns:
        Confirmation of feedback submission
    """
    try:
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

        if session_id not in chat_sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        if message_index >= len(chat_sessions[session_id]):
            raise HTTPException(status_code=400, detail="Invalid message index")

        # In a production system, you would store this feedback in a database
        logger.info(f"Feedback received for session {session_id}, message {message_index}: rating={rating}, feedback={feedback}")

        return {
            "message": "Feedback submitted successfully",
            "session_id": session_id,
            "message_index": message_index,
            "rating": rating
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")
