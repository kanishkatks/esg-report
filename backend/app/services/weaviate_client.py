"""
Weaviate client service for vector database operations.
"""

import weaviate
import logging
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class WeaviateClient:
    """Weaviate client wrapper for document storage and retrieval."""

    def __init__(self):
        self.client = None
        self.collection_name = "Document"

    async def connect(self) -> bool:
        """Connect to Weaviate instance."""
        try:
            auth_config = None
            if settings.weaviate_api_key:
                auth_config = weaviate.AuthApiKey(api_key=settings.weaviate_api_key)

            self.client = weaviate.Client(
                url=settings.weaviate_url,
                auth_client_secret=auth_config
            )

            # Test connection
            if self.client.is_ready():
                logger.info("Successfully connected to Weaviate")
                await self._create_schema()
                return True
            else:
                logger.error("Failed to connect to Weaviate")
                return False

        except Exception as e:
            logger.error(f"Error connecting to Weaviate: {e}")
            return False

    async def _create_schema(self):
        """Create the document schema if it doesn't exist."""
        try:
            # Check if schema already exists
            existing_classes = self.client.schema.get()["classes"]
            class_names = [cls["class"] for cls in existing_classes]

            if self.collection_name not in class_names:
                schema = {
                    "class": self.collection_name,
                    "description": "A document chunk for RAG retrieval",
                    "vectorizer": "none",  # We'll provide our own vectors
                    "properties": [
                        {
                            "name": "content",
                            "dataType": ["text"],
                            "description": "The text content of the document chunk",
                        },
                        {
                            "name": "filename",
                            "dataType": ["string"],
                            "description": "Original filename of the document",
                        },
                        {
                            "name": "document_id",
                            "dataType": ["string"],
                            "description": "Unique identifier for the source document",
                        },
                        {
                            "name": "chunk_index",
                            "dataType": ["int"],
                            "description": "Index of this chunk within the document",
                        },
                        {
                            "name": "metadata",
                            "dataType": ["text"],
                            "description": "Additional metadata about the document (JSON string)",
                        },
                        {
                            "name": "created_at",
                            "dataType": ["date"],
                            "description": "Timestamp when the document was indexed",
                        }
                    ]
                }

                self.client.schema.create_class(schema)
                logger.info(f"Created schema for class: {self.collection_name}")
            else:
                logger.info(f"Schema for class {self.collection_name} already exists")

        except Exception as e:
            logger.error(f"Error creating schema: {e}")
            raise

    async def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add documents to the vector database."""
        try:
            document_ids = []

            with self.client.batch as batch:
                batch.batch_size = 100

                for doc in documents:
                    # Generate UUID for the document
                    doc_uuid = weaviate.util.generate_uuid5(doc["content"])

                    # Prepare the document object
                    doc_object = {
                        "content": doc["content"],
                        "filename": doc["filename"],
                        "document_id": doc["document_id"],
                        "chunk_index": doc.get("chunk_index", 0),
                        "metadata": json.dumps(doc.get("metadata", {})),
                        "created_at": doc.get("created_at")
                    }

                    # Add to batch
                    batch.add_data_object(
                        data_object=doc_object,
                        class_name=self.collection_name,
                        uuid=doc_uuid,
                        vector=doc.get("vector")  # Optional: provide pre-computed vector
                    )

                    document_ids.append(doc_uuid)

            logger.info(f"Added {len(documents)} documents to Weaviate")
            return document_ids

        except Exception as e:
            logger.error(f"Error adding documents to Weaviate: {e}")
            raise

    async def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining BM25 and vector similarity.

        Args:
            query: Search query
            limit: Maximum number of results
            alpha: Balance between BM25 (0.0) and vector (1.0) search
        """
        try:
            result = (
                self.client.query
                .get(self.collection_name, [
                    "content", "filename", "document_id",
                    "chunk_index", "metadata", "created_at"
                ])
                .with_hybrid(
                    query=query,
                    alpha=alpha
                )
                .with_limit(limit)
                .with_additional(["score"])
                .do()
            )

            documents = result["data"]["Get"][self.collection_name]

            # Format results
            formatted_results = []
            for doc in documents:
                try:
                    metadata = json.loads(doc.get("metadata", "{}"))
                except (json.JSONDecodeError, TypeError):
                    metadata = {}

                formatted_results.append({
                    "content": doc["content"],
                    "filename": doc["filename"],
                    "document_id": doc["document_id"],
                    "chunk_index": doc["chunk_index"],
                    "metadata": metadata,
                    "created_at": doc.get("created_at"),
                    "score": doc["_additional"]["score"]
                })

            logger.info(f"Hybrid search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Error performing hybrid search: {e}")
            raise

    async def vector_search(
        self,
        query_vector: List[float],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search."""
        try:
            result = (
                self.client.query
                .get(self.collection_name, [
                    "content", "filename", "document_id",
                    "chunk_index", "metadata", "created_at"
                ])
                .with_near_vector({
                    "vector": query_vector
                })
                .with_limit(limit)
                .with_additional(["distance"])
                .do()
            )

            documents = result["data"]["Get"][self.collection_name]

            # Format results
            formatted_results = []
            for doc in documents:
                try:
                    metadata = json.loads(doc.get("metadata", "{}"))
                except (json.JSONDecodeError, TypeError):
                    metadata = {}

                formatted_results.append({
                    "content": doc["content"],
                    "filename": doc["filename"],
                    "document_id": doc["document_id"],
                    "chunk_index": doc["chunk_index"],
                    "metadata": metadata,
                    "created_at": doc.get("created_at"),
                    "score": 1.0 - doc["_additional"]["distance"]  # Convert distance to similarity
                })

            logger.info(f"Vector search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Error performing vector search: {e}")
            raise

    async def bm25_search(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform BM25 keyword search."""
        try:
            result = (
                self.client.query
                .get(self.collection_name, [
                    "content", "filename", "document_id",
                    "chunk_index", "metadata", "created_at"
                ])
                .with_bm25(
                    query=query
                )
                .with_limit(limit)
                .with_additional(["score"])
                .do()
            )

            documents = result["data"]["Get"][self.collection_name]

            # Format results
            formatted_results = []
            for doc in documents:
                try:
                    metadata = json.loads(doc.get("metadata", "{}"))
                except (json.JSONDecodeError, TypeError):
                    metadata = {}

                formatted_results.append({
                    "content": doc["content"],
                    "filename": doc["filename"],
                    "document_id": doc["document_id"],
                    "chunk_index": doc["chunk_index"],
                    "metadata": metadata,
                    "created_at": doc.get("created_at"),
                    "score": doc["_additional"]["score"]
                })

            logger.info(f"BM25 search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Error performing BM25 search: {e}")
            raise

    async def delete_document(self, document_id: str) -> bool:
        """Delete all chunks of a document."""
        try:
            result = (
                self.client.batch
                .delete_objects(
                    class_name=self.collection_name,
                    where={
                        "path": ["document_id"],
                        "operator": "Equal",
                        "valueString": document_id
                    }
                )
            )

            logger.info(f"Deleted document: {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False

    async def get_document_count(self) -> int:
        """Get total number of document chunks."""
        try:
            result = (
                self.client.query
                .aggregate(self.collection_name)
                .with_meta_count()
                .do()
            )

            count = result["data"]["Aggregate"][self.collection_name][0]["meta"]["count"]
            return count

        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0


# Global client instance
weaviate_client = WeaviateClient()
