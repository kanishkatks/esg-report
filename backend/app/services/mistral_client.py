"""
Mistral AI client service for LLM operations.
"""

import logging
from typing import List, Dict, Any, Optional
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


class MistralService:
    """Service for interacting with Mistral AI API."""

    def __init__(self):
        self.client = None
        self.model = settings.mistral_model

    async def initialize(self) -> bool:
        """Initialize the Mistral client."""
        try:
            self.client = MistralClient(api_key=settings.mistral_api_key)
            logger.info("Mistral client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Mistral client: {e}")
            return False

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0
    ) -> str:
        """
        Generate a response using Mistral AI.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter

        Returns:
            Generated response text
        """
        try:
            # Convert messages to Mistral format
            mistral_messages = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in messages
            ]

            # Generate response
            response = self.client.chat(
                model=self.model,
                messages=mistral_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p
            )

            generated_text = response.choices[0].message.content
            logger.info(f"Generated response with {len(generated_text)} characters")

            return generated_text

        except Exception as e:
            logger.error(f"Error generating response with Mistral: {e}")
            raise

    async def generate_rag_response(
        self,
        user_question: str,
        context_documents: List[Dict[str, Any]],
        chat_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a RAG response using retrieved context.

        Args:
            user_question: The user's question
            context_documents: Retrieved documents for context
            chat_history: Previous chat messages for context
            temperature: Sampling temperature

        Returns:
            Generated response
        """
        try:
            # Build context from retrieved documents
            context_text = self._build_context(context_documents)

            # Create system prompt
            system_prompt = self._create_rag_system_prompt()

            # Build messages
            messages = [{"role": "system", "content": system_prompt}]

            # Add chat history if provided
            if chat_history:
                messages.extend(chat_history[-10:])  # Keep last 10 messages for context

            # Add current question with context
            user_message = self._create_user_message_with_context(user_question, context_text)
            messages.append({"role": "user", "content": user_message})

            # Generate response
            response = await self.generate_response(
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )

            return response

        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            raise

    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        if not documents:
            return "No relevant context found."

        context_parts = []
        for i, doc in enumerate(documents[:5], 1):  # Use top 5 documents
            filename = doc.get("filename", "Unknown")
            content = doc.get("content", "").strip()

            context_parts.append(f"[Document {i}: {filename}]\n{content}")

        return "\n\n".join(context_parts)

    def _create_rag_system_prompt(self) -> str:
        """Create the system prompt for RAG responses."""
        return """You are a helpful AI assistant that answers questions based on the provided context documents.

Instructions:
1. Use the context documents to answer the user's question accurately and comprehensively
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Cite the relevant documents when possible (e.g., "According to Document 1...")
4. Provide clear, well-structured responses
5. If asked about something not in the context, explain that you can only answer based on the provided documents
6. Be concise but thorough in your explanations

Remember: Only use information from the provided context documents to answer questions."""

    def _create_user_message_with_context(self, question: str, context: str) -> str:
        """Create user message with context documents."""
        return f"""Context Documents:
{context}

Question: {question}

Please answer the question based on the context documents provided above."""

    async def generate_embedding_query(self, text: str) -> str:
        """
        Generate a query optimized for embedding search.
        This can help improve retrieval quality.
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Convert the following question into keywords and phrases that would be good for semantic search. Focus on the key concepts and terms."
                },
                {
                    "role": "user",
                    "content": f"Question: {text}"
                }
            ]

            response = await self.generate_response(
                messages=messages,
                temperature=0.3,
                max_tokens=100
            )

            return response.strip()

        except Exception as e:
            logger.error(f"Error generating embedding query: {e}")
            return text  # Fallback to original text

    async def summarize_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Generate a summary of multiple documents."""
        try:
            if not documents:
                return "No documents to summarize."

            # Combine document contents
            combined_text = "\n\n".join([
                f"Document: {doc.get('filename', 'Unknown')}\n{doc.get('content', '')}"
                for doc in documents[:10]  # Limit to 10 documents
            ])

            messages = [
                {
                    "role": "system",
                    "content": "Provide a concise summary of the following documents, highlighting the key points and main themes."
                },
                {
                    "role": "user",
                    "content": combined_text
                }
            ]

            summary = await self.generate_response(
                messages=messages,
                temperature=0.5,
                max_tokens=500
            )

            return summary

        except Exception as e:
            logger.error(f"Error summarizing documents: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if the Mistral service is healthy."""
        try:
            test_messages = [
                {"role": "user", "content": "Hello, this is a test message."}
            ]

            response = await self.generate_response(
                messages=test_messages,
                temperature=0.1,
                max_tokens=10
            )

            return len(response.strip()) > 0

        except Exception as e:
            logger.error(f"Mistral health check failed: {e}")
            return False


# Global service instance
mistral_service = MistralService()
