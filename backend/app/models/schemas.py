"""
Pydantic models for request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentUploadRequest(BaseModel):
    """Request model for document upload."""
    filename: str = Field(..., description="Name of the uploaded file")
    content_type: str = Field(..., description="MIME type of the file")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    document_id: str = Field(..., description="Unique identifier for the document")
    filename: str = Field(..., description="Name of the uploaded file")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")


class ChatMessage(BaseModel):
    """Model for a chat message."""
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Request model for chat queries."""
    message: str = Field(..., description="User's question or message")
    session_id: Optional[str] = Field(None, description="Chat session identifier")
    use_history: bool = Field(True, description="Whether to use chat history for context")


class ChatResponse(BaseModel):
    """Response model for chat queries."""
    response: str = Field(..., description="Generated response")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents used")
    session_id: str = Field(..., description="Chat session identifier")
    timestamp: datetime = Field(default_factory=datetime.now)


class SearchRequest(BaseModel):
    """Request model for document search."""
    query: str = Field(..., description="Search query")
    limit: int = Field(10, description="Maximum number of results to return")
    use_hybrid: bool = Field(True, description="Whether to use hybrid search (BM25 + vector)")


class SearchResult(BaseModel):
    """Model for a search result."""
    document_id: str = Field(..., description="Document identifier")
    filename: str = Field(..., description="Source filename")
    content: str = Field(..., description="Relevant content chunk")
    score: float = Field(..., description="Relevance score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SearchResponse(BaseModel):
    """Response model for document search."""
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results found")
    query: str = Field(..., description="Original search query")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str] = Field(default_factory=dict, description="Status of dependent services")
