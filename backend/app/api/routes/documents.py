"""
Document management endpoints.
"""

import os
import logging
import aiofiles
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from app.models.schemas import DocumentUploadResponse
from app.services import document_processor, weaviate_client
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Upload directory
UPLOAD_DIR = "/app/documents/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    metadata: str = Form(None)
):
    """
    Upload and process a document for RAG retrieval.

    Args:
        file: The document file to upload
        metadata: Optional JSON string with additional metadata

    Returns:
        Document upload response with processing status
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)

        max_size = settings.max_file_size_mb * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )

        # Check file format
        if not document_processor.is_supported_format(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported: {', '.join(document_processor.supported_formats)}"
            )

        # Save file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        logger.info(f"Saved uploaded file: {file.filename}")

        # Process document
        try:
            # Parse metadata if provided
            doc_metadata = {}
            if metadata:
                import json
                doc_metadata = json.loads(metadata)

            # Process the document
            chunks = await document_processor.process_document(
                file_path=file_path,
                filename=file.filename,
                metadata=doc_metadata
            )

            if not chunks:
                raise HTTPException(status_code=400, detail="No content could be extracted from the document")

            # Add to vector database
            document_ids = await weaviate_client.add_documents(chunks)

            logger.info(f"Successfully processed and indexed document: {file.filename}")

            return DocumentUploadResponse(
                document_id=chunks[0]["document_id"],
                filename=file.filename,
                status="success",
                message=f"Document processed successfully. {len(chunks)} chunks indexed."
            )

        except Exception as e:
            # Clean up file on processing error
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"Error processing document {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error uploading document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/upload-multiple")
async def upload_multiple_documents(files: List[UploadFile] = File(...)):
    """
    Upload and process multiple documents.

    Args:
        files: List of document files to upload

    Returns:
        List of upload results
    """
    try:
        results = []

        for file in files:
            try:
                # Process each file individually
                result = await upload_document(file)
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "document_id": result.document_id,
                    "message": result.message
                })
            except HTTPException as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": e.detail
                })
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": str(e)
                })

        return {"results": results}

    except Exception as e:
        logger.error(f"Error uploading multiple documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and all its chunks from the vector database.

    Args:
        document_id: The unique identifier of the document to delete

    Returns:
        Deletion status
    """
    try:
        success = await weaviate_client.delete_document(document_id)

        if success:
            return {"status": "success", "message": f"Document {document_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats")
async def get_document_stats():
    """
    Get statistics about indexed documents.

    Returns:
        Document statistics
    """
    try:
        total_count = await weaviate_client.get_document_count()

        return {
            "total_chunks": total_count,
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported document formats.

    Returns:
        List of supported file extensions
    """
    return {
        "supported_formats": list(document_processor.supported_formats),
        "max_file_size_mb": settings.max_file_size_mb
    }
