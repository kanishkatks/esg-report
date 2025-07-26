"""
ESG Document PDF Parser

This module extracts text from PDF documents and saves them as text files.
Supports batch processing of multiple PDFs with comprehensive error handling.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
import fitz  # PyMuPDF

# Load environment variables
load_dotenv()

def setup_logging() -> logging.Logger:
    """Setup logging configuration."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('LOG_FILE', 'esg_parser.log')

    # Create logger
    logger = logging.getLogger(__name__)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, log_level))

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(formatter)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def validate_pdf_file(file_path: Path) -> bool:
    """
    Validate if the file is a readable PDF.

    Args:
        file_path: Path to the PDF file

    Returns:
        bool: True if valid PDF, False otherwise
    """
    try:
        if not file_path.exists():
            return False
        if not file_path.suffix.lower() == '.pdf':
            return False
        if file_path.stat().st_size == 0:
            return False

        # Try to open the PDF to verify it's not corrupted
        doc = fitz.open(str(file_path))
        doc.close()
        return True
    except Exception:
        return False

def extract_text_from_pdf(pdf_path: Path, logger: logging.Logger) -> Optional[str]:
    """
    Extract text from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        logger: Logger instance

    Returns:
        str: Extracted text or None if extraction failed
    """
    try:
        logger.info(f"Processing PDF: {pdf_path.name}")

        # Open the PDF document
        doc = fitz.open(str(pdf_path))

        # Extract text from all pages
        text_content = []
        for page_num in range(len(doc)):
            try:
                page = doc.load_page(page_num)
                page_text = page.get_text()

                # Clean up the text (remove excessive whitespace)
                page_text = ' '.join(page_text.split())
                if page_text.strip():  # Only add non-empty pages
                    text_content.append(page_text)

            except Exception as e:
                logger.warning(f"Error processing page {page_num + 1} of {pdf_path.name}: {e}")
                continue

        doc.close()

        if not text_content:
            logger.warning(f"No text content extracted from {pdf_path.name}")
            return None

        full_text = '\n\n'.join(text_content)
        logger.info(f"Successfully extracted {len(full_text)} characters from {pdf_path.name}")
        return full_text

    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_path.name}: {e}")
        return None

def save_text_file(text: str, output_path: Path, logger: logging.Logger) -> bool:
    """
    Save extracted text to a file.

    Args:
        text: Text content to save
        output_path: Path where to save the text file
        logger: Logger instance

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as text_file:
            text_file.write(text)

        logger.info(f"Saved text to: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to save text file {output_path}: {e}")
        return False

def process_pdfs_in_directory(directory: str = None) -> List[str]:
    """
    Process all PDF files in the specified directory.

    Args:
        directory: Directory containing PDF files (defaults to DOCS_DIRECTORY from env)

    Returns:
        List[str]: List of successfully processed text files
    """
    logger = setup_logging()

    # Get directory from environment or use provided directory
    docs_dir = directory or os.getenv('DOCS_DIRECTORY', 'docs')
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        logger.error(f"Directory does not exist: {docs_path}")
        return []

    if not docs_path.is_dir():
        logger.error(f"Path is not a directory: {docs_path}")
        return []

    # Find all PDF files
    pdf_files = list(docs_path.glob('*.pdf'))
    if not pdf_files:
        logger.warning(f"No PDF files found in {docs_path}")
        return []

    logger.info(f"Found {len(pdf_files)} PDF files to process")

    processed_files = []
    failed_files = []

    for pdf_file in pdf_files:
        # Validate PDF file
        if not validate_pdf_file(pdf_file):
            logger.error(f"Invalid or corrupted PDF file: {pdf_file.name}")
            failed_files.append(pdf_file.name)
            continue

        # Extract text
        text_content = extract_text_from_pdf(pdf_file, logger)
        if text_content is None:
            failed_files.append(pdf_file.name)
            continue

        # Save text file
        text_file_path = pdf_file.with_suffix('.txt')
        if save_text_file(text_content, text_file_path, logger):
            processed_files.append(str(text_file_path))
        else:
            failed_files.append(pdf_file.name)

    # Summary
    logger.info(f"Processing complete: {len(processed_files)} successful, {len(failed_files)} failed")
    if failed_files:
        logger.warning(f"Failed files: {', '.join(failed_files)}")

    return processed_files

def main():
    """Main function to run the PDF processing."""
    try:
        processed_files = process_pdfs_in_directory()

        if processed_files:
            print(f"\n✅ Successfully processed {len(processed_files)} PDF files:")
            for file_path in processed_files:
                print(f"  - {file_path}")
        else:
            print("\n❌ No PDF files were successfully processed.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
