# RAG Chatbot API Documentation

This document provides comprehensive documentation for the RAG Chatbot API endpoints.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, consider implementing API key authentication or OAuth.

## Response Format

All API responses follow a consistent JSON format:

### Success Response
```json
{
  "data": {...},
  "status": "success",
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "detail": "Error description",
  "status_code": 400
}
```

## Endpoints

### Health Check

#### GET /health/
Get the overall health status of the system.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00Z",
  "services": {
    "weaviate": "healthy (documents: 150)",
    "mistral": "healthy"
  }
}
```

#### GET /health/ready
Readiness probe for container orchestration.

**Response:**
```json
{
  "status": "ready"
}
```

#### GET /health/live
Liveness probe for container orchestration.

**Response:**
```json
{
  "status": "alive"
}
```

---

### Document Management

#### POST /documents/upload
Upload and process a single document.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: Document file (PDF, DOCX, or TXT)
  - `metadata`: Optional JSON string with additional metadata

**Example:**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@document.pdf" \
  -F "metadata={\"author\": \"John Doe\", \"category\": \"research\"}"
```

**Response:**
```json
{
  "document_id": "uuid-string",
  "filename": "document.pdf",
  "status": "success",
  "message": "Document processed successfully. 25 chunks indexed."
}
```

#### POST /documents/upload-multiple
Upload and process multiple documents.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Multiple `files` fields

**Response:**
```json
{
  "results": [
    {
      "filename": "doc1.pdf",
      "status": "success",
      "document_id": "uuid-1",
      "message": "Document processed successfully. 15 chunks indexed."
    },
    {
      "filename": "doc2.pdf",
      "status": "error",
      "message": "File too large. Maximum size: 50MB"
    }
  ]
}
```

#### DELETE /documents/{document_id}
Delete a document and all its chunks.

**Parameters:**
- `document_id`: UUID of the document to delete

**Response:**
```json
{
  "status": "success",
  "message": "Document uuid-string deleted successfully"
}
```

#### GET /documents/stats
Get statistics about indexed documents.

**Response:**
```json
{
  "total_chunks": 1250,
  "status": "success"
}
```

#### GET /documents/supported-formats
Get list of supported document formats.

**Response:**
```json
{
  "supported_formats": [".pdf", ".docx", ".txt"],
  "max_file_size_mb": 50
}
```

---

### Search

#### GET /search/
Search documents using query parameters.

**Parameters:**
- `q`: Search query (required)
- `limit`: Maximum number of results (default: 10)
- `hybrid`: Use hybrid search (default: true)

**Example:**
```bash
curl "http://localhost:8000/search/?q=machine%20learning&limit=5&hybrid=true"
```

**Response:**
```json
{
  "results": [
    {
      "document_id": "uuid-string",
      "filename": "ml_paper.pdf",
      "content": "Machine learning is a subset of artificial intelligence...",
      "score": 0.95,
      "metadata": {
        "author": "John Doe",
        "page": 1
      }
    }
  ],
  "total_results": 1,
  "query": "machine learning"
}
```

#### POST /search/
Search documents using JSON payload.

**Request Body:**
```json
{
  "query": "machine learning",
  "limit": 10,
  "use_hybrid": true
}
```

**Response:** Same as GET /search/

#### POST /search/bm25
Perform BM25-only keyword search.

**Request Body:**
```json
{
  "query": "machine learning",
  "limit": 10
}
```

**Response:** Same format as regular search

#### POST /search/hybrid
Perform hybrid search with custom alpha parameter.

**Parameters:**
- `alpha`: Balance between BM25 (0.0) and vector (1.0) search

**Request Body:**
```json
{
  "query": "machine learning",
  "limit": 10
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/search/hybrid?alpha=0.7" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "limit": 5}'
```

---

### Chat

#### POST /chat/
Send a chat message and get an AI-generated response.

**Request Body:**
```json
{
  "message": "What is machine learning?",
  "session_id": "optional-session-id",
  "use_history": true
}
```

**Response:**
```json
{
  "response": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed...",
  "sources": [
    {
      "document_id": "uuid-string",
      "filename": "ml_textbook.pdf",
      "content_preview": "Machine learning is a method of data analysis...",
      "score": 0.92,
      "metadata": {
        "chapter": "Introduction",
        "page": 15
      }
    }
  ],
  "session_id": "generated-or-provided-session-id",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET /chat/sessions/{session_id}/history
Get chat history for a specific session.

**Parameters:**
- `session_id`: Chat session identifier

**Response:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is machine learning?",
      "timestamp": "2024-01-01T12:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Machine learning is...",
      "timestamp": "2024-01-01T12:00:05Z"
    }
  ],
  "session_id": "session-uuid",
  "total_messages": 2
}
```

#### DELETE /chat/sessions/{session_id}
Clear chat history for a specific session.

**Response:**
```json
{
  "message": "Session session-uuid cleared successfully"
}
```

#### GET /chat/sessions
List all active chat sessions.

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "session-uuid-1",
      "message_count": 10,
      "last_activity": "2024-01-01T12:00:00Z"
    }
  ],
  "total_sessions": 1
}
```

#### POST /chat/summarize
Generate a summary of a chat conversation.

**Request Body:**
```json
{
  "session_id": "session-uuid"
}
```

**Response:**
```json
{
  "session_id": "session-uuid",
  "summary": "The conversation covered topics about machine learning, including definitions, applications, and key algorithms discussed.",
  "message_count": 15
}
```

#### POST /chat/feedback
Submit feedback for a chat response.

**Request Body:**
```json
{
  "session_id": "session-uuid",
  "message_index": 3,
  "rating": 4,
  "feedback": "Good response but could be more detailed"
}
```

**Response:**
```json
{
  "message": "Feedback submitted successfully",
  "session_id": "session-uuid",
  "message_index": 3,
  "rating": 4
}
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input parameters |
| 404 | Not Found - Resource doesn't exist |
| 413 | Payload Too Large - File size exceeds limit |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server-side error |
| 503 | Service Unavailable - Service not ready |

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing rate limiting based on:
- IP address
- API key
- User session

## Examples

### Python Client Example

```python
import requests
import json

class RAGChatbotClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def upload_document(self, file_path, metadata=None):
        """Upload a document to the system."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {}
            if metadata:
                data['metadata'] = json.dumps(metadata)

            response = self.session.post(
                f"{self.base_url}/documents/upload",
                files=files,
                data=data
            )
            return response.json()

    def chat(self, message, session_id=None):
        """Send a chat message."""
        payload = {
            "message": message,
            "use_history": True
        }
        if session_id:
            payload["session_id"] = session_id

        response = self.session.post(
            f"{self.base_url}/chat/",
            json=payload
        )
        return response.json()

    def search(self, query, limit=5):
        """Search documents."""
        params = {
            "q": query,
            "limit": limit,
            "hybrid": True
        }
        response = self.session.get(
            f"{self.base_url}/search/",
            params=params
        )
        return response.json()

# Usage example
client = RAGChatbotClient()

# Upload a document
result = client.upload_document("document.pdf", {"author": "John Doe"})
print(f"Upload result: {result}")

# Chat with the system
chat_response = client.chat("What is this document about?")
print(f"Response: {chat_response['response']}")

# Search documents
search_results = client.search("machine learning")
print(f"Found {len(search_results['results'])} results")
```

### JavaScript Client Example

```javascript
class RAGChatbotClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async uploadDocument(file, metadata = null) {
        const formData = new FormData();
        formData.append('file', file);
        if (metadata) {
            formData.append('metadata', JSON.stringify(metadata));
        }

        const response = await fetch(`${this.baseUrl}/documents/upload`, {
            method: 'POST',
            body: formData
        });

        return await response.json();
    }

    async chat(message, sessionId = null) {
        const payload = {
            message: message,
            use_history: true
        };
        if (sessionId) {
            payload.session_id = sessionId;
        }

        const response = await fetch(`${this.baseUrl}/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        return await response.json();
    }

    async search(query, limit = 5) {
        const params = new URLSearchParams({
            q: query,
            limit: limit.toString(),
            hybrid: 'true'
        });

        const response = await fetch(`${this.baseUrl}/search/?${params}`);
        return await response.json();
    }
}

// Usage example
const client = new RAGChatbotClient();

// Upload document
const fileInput = document.getElementById('file-input');
const file = fileInput.files[0];
client.uploadDocument(file, {author: 'John Doe'})
    .then(result => console.log('Upload result:', result));

// Chat
client.chat('What is machine learning?')
    .then(response => console.log('Response:', response.response));

// Search
client.search('artificial intelligence')
    .then(results => console.log('Search results:', results.results));
```

## WebSocket Support

Currently, the API uses HTTP requests. For real-time features, consider implementing WebSocket endpoints for:
- Real-time chat streaming
- Live document processing status
- Real-time search suggestions

## Monitoring and Logging

The API includes comprehensive logging. Monitor these endpoints for system health:
- `/health/` - Overall system health
- `/health/ready` - Service readiness
- `/health/live` - Service liveness

Log levels can be configured via the `LOG_LEVEL` environment variable.
