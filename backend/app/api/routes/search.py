"""
Document search endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import SearchRequest, SearchResponse, SearchResult
from app.services import weaviate_client
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search documents using the specified search method.

    Args:
        request: Search request with query and parameters

    Returns:
        Search results with relevant document chunks
    """
    try:
        if request.use_hybrid:
            # Use hybrid search (BM25 + vector)
            results = await weaviate_client.hybrid_search(
                query=request.query,
                limit=request.limit,
                alpha=0.5  # Balance between BM25 and vector search
            )
        else:
            # Use BM25 search only
            results = await weaviate_client.bm25_search(
                query=request.query,
                limit=request.limit
            )

        # Format results
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                document_id=result["document_id"],
                filename=result["filename"],
                content=result["content"],
                score=result["score"],
                metadata=result.get("metadata", {})
            ))

        return SearchResponse(
            results=search_results,
            total_results=len(search_results),
            query=request.query
        )

    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/", response_model=SearchResponse)
async def search_documents_get(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results"),
    hybrid: bool = Query(True, description="Use hybrid search")
):
    """
    Search documents using GET method for simple queries.

    Args:
        q: Search query string
        limit: Maximum number of results to return
        hybrid: Whether to use hybrid search

    Returns:
        Search results
    """
    request = SearchRequest(
        query=q,
        limit=limit,
        use_hybrid=hybrid
    )
    return await search_documents(request)


@router.post("/bm25", response_model=SearchResponse)
async def bm25_search(request: SearchRequest):
    """
    Search documents using BM25 keyword search only.

    Args:
        request: Search request with query and parameters

    Returns:
        BM25 search results
    """
    try:
        results = await weaviate_client.bm25_search(
            query=request.query,
            limit=request.limit
        )

        # Format results
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                document_id=result["document_id"],
                filename=result["filename"],
                content=result["content"],
                score=result["score"],
                metadata=result.get("metadata", {})
            ))

        return SearchResponse(
            results=search_results,
            total_results=len(search_results),
            query=request.query
        )

    except Exception as e:
        logger.error(f"Error in BM25 search: {e}")
        raise HTTPException(status_code=500, detail="BM25 search failed")


@router.post("/hybrid", response_model=SearchResponse)
async def hybrid_search(
    request: SearchRequest,
    alpha: float = Query(0.5, description="Balance between BM25 (0.0) and vector (1.0) search")
):
    """
    Search documents using hybrid search (BM25 + vector similarity).

    Args:
        request: Search request with query and parameters
        alpha: Balance between BM25 and vector search (0.0 = pure BM25, 1.0 = pure vector)

    Returns:
        Hybrid search results
    """
    try:
        results = await weaviate_client.hybrid_search(
            query=request.query,
            limit=request.limit,
            alpha=alpha
        )

        # Format results
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                document_id=result["document_id"],
                filename=result["filename"],
                content=result["content"],
                score=result["score"],
                metadata=result.get("metadata", {})
            ))

        return SearchResponse(
            results=search_results,
            total_results=len(search_results),
            query=request.query
        )

    except Exception as e:
        logger.error(f"Error in hybrid search: {e}")
        raise HTTPException(status_code=500, detail="Hybrid search failed")


@router.get("/similar/{document_id}")
async def find_similar_documents(
    document_id: str,
    limit: int = Query(5, description="Maximum number of similar documents")
):
    """
    Find documents similar to a given document.

    Args:
        document_id: ID of the reference document
        limit: Maximum number of similar documents to return

    Returns:
        Similar documents
    """
    try:
        # This would require implementing document-to-document similarity
        # For now, return a placeholder response
        return {
            "message": "Similar document search not yet implemented",
            "document_id": document_id,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error finding similar documents: {e}")
        raise HTTPException(status_code=500, detail="Similar document search failed")
