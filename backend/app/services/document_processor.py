"""
Document processing service for extracting and chunking text from various file formats.
"""

import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import PyPDF2
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing and chunking documents."""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        self.supported_formats = {'.pdf', '.docx', '.txt'}

    def is_supported_format(self, filename: str) -> bool:
        """Check if the file format is supported."""
        _, ext = os.path.splitext(filename.lower())
        return ext in self.supported_formats

    async def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"

            logger.info(f"Extracted text from PDF: {file_path}")
            return text.strip()

        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise

    async def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = ""

            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            logger.info(f"Extracted text from DOCX: {file_path}")
            return text.strip()

        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {e}")
            raise

    async def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

            logger.info(f"Extracted text from TXT: {file_path}")
            return text.strip()

        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    text = file.read()
                logger.info(f"Extracted text from TXT (latin-1): {file_path}")
                return text.strip()
            except Exception as e:
                logger.error(f"Error extracting text from TXT {file_path}: {e}")
                raise
        except Exception as e:
            logger.error(f"Error extracting text from TXT {file_path}: {e}")
            raise

    async def extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from a file based on its extension."""
        _, ext = os.path.splitext(filename.lower())

        if ext == '.pdf':
            return await self.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return await self.extract_text_from_docx(file_path)
        elif ext == '.txt':
            return await self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks using the configured text splitter."""
        try:
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise

    async def process_document(
        self,
        file_path: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a document: extract text, chunk it, and prepare for indexing.

        Returns:
            List of document chunks ready for vector database insertion
        """
        try:
            # Generate unique document ID
            document_id = str(uuid.uuid4())

            # Extract text from the document
            text = await self.extract_text(file_path, filename)

            if not text.strip():
                raise ValueError("No text content found in the document")

            # Split text into chunks
            chunks = self.chunk_text(text)

            # Prepare document chunks for indexing
            processed_chunks = []
            current_time = datetime.now().isoformat()

            for i, chunk in enumerate(chunks):
                if chunk.strip():  # Skip empty chunks
                    chunk_data = {
                        "content": chunk.strip(),
                        "filename": filename,
                        "document_id": document_id,
                        "chunk_index": i,
                        "metadata": {
                            "file_size": os.path.getsize(file_path),
                            "total_chunks": len(chunks),
                            "original_length": len(text),
                            **(metadata or {})
                        },
                        "created_at": current_time
                    }
                    processed_chunks.append(chunk_data)

            logger.info(
                f"Processed document {filename}: "
                f"{len(processed_chunks)} chunks, "
                f"document_id: {document_id}"
            )

            return processed_chunks

        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            raise

    async def process_multiple_documents(
        self,
        file_paths: List[str],
        filenames: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Process multiple documents in batch."""
        try:
            all_chunks = []

            for i, (file_path, filename) in enumerate(zip(file_paths, filenames)):
                metadata = metadata_list[i] if metadata_list else None
                chunks = await self.process_document(file_path, filename, metadata)
                all_chunks.extend(chunks)

            logger.info(f"Processed {len(file_paths)} documents, total chunks: {len(all_chunks)}")
            return all_chunks

        except Exception as e:
            logger.error(f"Error processing multiple documents: {e}")
            raise

    def get_document_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about processed document chunks."""
        if not chunks:
            return {}

        total_chunks = len(chunks)
        total_characters = sum(len(chunk["content"]) for chunk in chunks)
        avg_chunk_size = total_characters / total_chunks if total_chunks > 0 else 0

        # Group by document
        documents = {}
        for chunk in chunks:
            doc_id = chunk["document_id"]
            if doc_id not in documents:
                documents[doc_id] = {
                    "filename": chunk["filename"],
                    "chunk_count": 0,
                    "total_characters": 0
                }
            documents[doc_id]["chunk_count"] += 1
            documents[doc_id]["total_characters"] += len(chunk["content"])

        return {
            "total_documents": len(documents),
            "total_chunks": total_chunks,
            "total_characters": total_characters,
            "average_chunk_size": round(avg_chunk_size, 2),
            "documents": documents
        }


# Global processor instance
document_processor = DocumentProcessor()
