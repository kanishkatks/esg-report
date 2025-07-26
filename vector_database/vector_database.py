"""
ESG Document FAISS Vector Database Manager

This module creates vector embeddings from text documents and stores them using FAISS.
Features intelligent text chunking, efficient similarity search, and comprehensive error handling.
"""

import os
import sys
import logging
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
from dotenv import load_dotenv
from tqdm import tqdm

import faiss
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

class ESGFAISSVectorDatabase:
    """Manages ESG document vector database operations using FAISS."""

    def __init__(self):
        """Initialize the FAISS vector database manager."""
        self.logger = self._setup_logging()
        self.model = None
        self.index = None
        self.texts = []
        self.metadata = []

        # Configuration from environment
        self.docs_directory = os.getenv('DOCS_DIRECTORY', 'docs')
        self.index_directory = os.getenv('INDEX_DIRECTORY', 'vectorstore')
        self.chunk_size = int(os.getenv('CHUNK_SIZE', '500'))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '50'))
        self.embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.batch_size = int(os.getenv('BATCH_SIZE', '32'))

        # Ensure index directory exists
        Path(self.index_directory).mkdir(parents=True, exist_ok=True)

    def _setup_logging(self) -> logging.Logger:
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

    def load_embedding_model(self) -> bool:
        """
        Load the sentence transformer model for embeddings.

        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            self.logger.info(f"Loading embedding model: {self.embedding_model}")
            self.model = SentenceTransformer(self.embedding_model)
            self.logger.info("✅ Embedding model loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to load embedding model: {e}")
            return False

    def intelligent_chunk_text(self, text: str) -> List[str]:
        """
        Intelligently chunk text while preserving sentence boundaries.

        Args:
            text: Input text to chunk

        Returns:
            List[str]: List of text chunks
        """
        if not text or not text.strip():
            return []

        # Clean the text
        import re
        text = re.sub(r'\s+', ' ', text.strip())

        # Split into sentences using multiple delimiters
        sentence_endings = r'[.!?]+(?:\s+|$)'
        sentences = re.split(sentence_endings, text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            potential_chunk = current_chunk + (" " if current_chunk else "") + sentence

            if len(potential_chunk) <= self.chunk_size:
                current_chunk = potential_chunk
            else:
                # If current chunk is not empty, save it
                if current_chunk:
                    chunks.append(current_chunk)

                # If single sentence is too long, split it further
                if len(sentence) > self.chunk_size:
                    # Split long sentence into smaller parts
                    words = sentence.split()
                    temp_chunk = ""

                    for word in words:
                        if len(temp_chunk + " " + word) <= self.chunk_size:
                            temp_chunk += (" " if temp_chunk else "") + word
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk)
                            temp_chunk = word

                    current_chunk = temp_chunk
                else:
                    current_chunk = sentence

        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(current_chunk)

        # Apply overlap if specified
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._apply_chunk_overlap(chunks)

        return chunks

    def _apply_chunk_overlap(self, chunks: List[str]) -> List[str]:
        """
        Apply overlap between consecutive chunks.

        Args:
            chunks: List of text chunks

        Returns:
            List[str]: Chunks with overlap applied
        """
        if len(chunks) <= 1:
            return chunks

        overlapped_chunks = [chunks[0]]  # First chunk remains unchanged

        for i in range(1, len(chunks)):
            prev_chunk = chunks[i-1]
            current_chunk = chunks[i]

            # Get last N characters from previous chunk for overlap
            overlap_text = prev_chunk[-self.chunk_overlap:] if len(prev_chunk) > self.chunk_overlap else prev_chunk

            # Combine with current chunk
            overlapped_chunk = overlap_text + " " + current_chunk
            overlapped_chunks.append(overlapped_chunk)

        return overlapped_chunks

    def process_text_files(self) -> bool:
        """
        Process all text files in the documents directory.

        Returns:
            bool: True if processing successful, False otherwise
        """
        docs_path = Path(self.docs_directory)

        if not docs_path.exists():
            self.logger.error(f"Documents directory does not exist: {docs_path}")
            return False

        # Find all text files
        text_files = list(docs_path.glob('*.txt'))
        if not text_files:
            self.logger.warning(f"No text files found in {docs_path}")
            return False

        self.logger.info(f"Found {len(text_files)} text files to process")

        all_chunks = []
        all_metadata = []

        for text_file in tqdm(text_files, desc="Processing files"):
            try:
                chunks, metadata = self._process_single_file(text_file)
                all_chunks.extend(chunks)
                all_metadata.extend(metadata)
                self.logger.info(f"✅ Processed {text_file.name}: {len(chunks)} chunks")

            except Exception as e:
                self.logger.error(f"❌ Failed to process {text_file.name}: {e}")
                continue

        if not all_chunks:
            self.logger.error("No chunks were created from any files")
            return False

        self.texts = all_chunks
        self.metadata = all_metadata

        self.logger.info(f"🎉 Processing complete: {len(all_chunks)} total chunks from {len(text_files)} files")
        return True

    def _process_single_file(self, file_path: Path) -> Tuple[List[str], List[Dict]]:
        """
        Process a single text file and create chunks.

        Args:
            file_path: Path to the text file

        Returns:
            Tuple[List[str], List[Dict]]: Chunks and their metadata
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()

            if not text_content.strip():
                self.logger.warning(f"Empty file: {file_path.name}")
                return [], []

            # Create chunks
            chunks = self.intelligent_chunk_text(text_content)
            if not chunks:
                self.logger.warning(f"No chunks created from {file_path.name}")
                return [], []

            # Create metadata for each chunk
            metadata = []
            for i, chunk in enumerate(chunks):
                metadata.append({
                    'source': file_path.name,
                    'chunk_index': i,
                    'chunk_size': len(chunk),
                    'file_path': str(file_path)
                })

            return chunks, metadata

        except Exception as e:
            self.logger.error(f"Error processing file {file_path.name}: {e}")
            return [], []

    def create_faiss_index(self) -> bool:
        """
        Create FAISS index from processed text chunks.

        Returns:
            bool: True if index created successfully, False otherwise
        """
        try:
            if not self.texts:
                self.logger.error("No text chunks available to create index")
                return False

            self.logger.info(f"Generating embeddings for {len(self.texts)} text chunks...")

            # Generate embeddings in batches to manage memory
            all_embeddings = []
            for i in tqdm(range(0, len(self.texts), self.batch_size), desc="Generating embeddings"):
                batch_texts = self.texts[i:i + self.batch_size]
                batch_embeddings = self.model.encode(batch_texts, show_progress_bar=False)
                all_embeddings.append(batch_embeddings)

            # Combine all embeddings
            embeddings = np.vstack(all_embeddings)
            self.logger.info(f"✅ Generated embeddings with shape: {embeddings.shape}")

            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity
            self.index.add(embeddings.astype('float32'))

            self.logger.info(f"✅ Created FAISS index with {self.index.ntotal} vectors")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to create FAISS index: {e}")
            return False

    def save_index(self) -> bool:
        """
        Save FAISS index and metadata to disk.

        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            if self.index is None:
                self.logger.error("No index to save")
                return False

            # Save FAISS index
            index_path = Path(self.index_directory) / "faiss.index"
            faiss.write_index(self.index, str(index_path))

            # Save metadata
            metadata_path = Path(self.index_directory) / "metadata.pkl"
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)

            # Save texts
            texts_path = Path(self.index_directory) / "texts.pkl"
            with open(texts_path, 'wb') as f:
                pickle.dump(self.texts, f)

            # Save configuration
            config_path = Path(self.index_directory) / "config.pkl"
            config = {
                'embedding_model': self.embedding_model,
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap,
                'dimension': self.index.d,
                'total_vectors': self.index.ntotal
            }
            with open(config_path, 'wb') as f:
                pickle.dump(config, f)

            self.logger.info(f"✅ Index and metadata saved to {self.index_directory}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to save index: {e}")
            return False

    def load_index(self) -> bool:
        """
        Load FAISS index and metadata from disk.

        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            index_path = Path(self.index_directory) / "faiss.index"
            metadata_path = Path(self.index_directory) / "metadata.pkl"
            texts_path = Path(self.index_directory) / "texts.pkl"

            if not all(p.exists() for p in [index_path, metadata_path, texts_path]):
                self.logger.error("Index files not found")
                return False

            # Load FAISS index
            self.index = faiss.read_index(str(index_path))

            # Load metadata
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)

            # Load texts
            with open(texts_path, 'rb') as f:
                self.texts = pickle.load(f)

            self.logger.info(f"✅ Loaded index with {self.index.ntotal} vectors")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to load index: {e}")
            return False

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for similar text chunks using the query.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List[Dict]: Search results with scores and metadata
        """
        try:
            if self.index is None or self.model is None:
                self.logger.error("Index or model not loaded")
                return []

            # Generate query embedding
            query_embedding = self.model.encode([query])

            # Search in FAISS index
            distances, indices = self.index.search(query_embedding.astype('float32'), k)

            # Prepare results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.texts):
                    result = {
                        'rank': i + 1,
                        'text': self.texts[idx],
                        'metadata': self.metadata[idx],
                        'distance': float(distance),
                        'similarity_score': 1 / (1 + distance)  # Convert distance to similarity
                    }
                    results.append(result)

            return results

        except Exception as e:
            self.logger.error(f"❌ Search failed: {e}")
            return []

    def get_statistics(self) -> Dict:
        """
        Get statistics about the vector database.

        Returns:
            Dict: Database statistics
        """
        try:
            if not self.texts or not self.metadata:
                return {'total_chunks': 0, 'unique_sources': 0, 'source_files': []}

            unique_sources = set(meta['source'] for meta in self.metadata)

            stats = {
                'total_chunks': len(self.texts),
                'unique_sources': len(unique_sources),
                'source_files': list(unique_sources),
                'index_size': self.index.ntotal if self.index else 0,
                'embedding_dimension': self.index.d if self.index else 0
            }

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {'total_chunks': 0, 'unique_sources': 0, 'source_files': []}

    def run_pipeline(self) -> bool:
        """
        Run the complete vector database creation pipeline.

        Returns:
            bool: True if pipeline completed successfully, False otherwise
        """
        self.logger.info("🚀 Starting ESG FAISS Vector Database Pipeline")

        # Step 1: Load embedding model
        if not self.load_embedding_model():
            return False

        # Step 2: Process text files
        if not self.process_text_files():
            return False

        # Step 3: Create FAISS index
        if not self.create_faiss_index():
            return False

        # Step 4: Save index
        if not self.save_index():
            return False

        # Step 5: Display statistics
        stats = self.get_statistics()
        self.logger.info(f"📊 Database Statistics:")
        self.logger.info(f"   Total chunks: {stats['total_chunks']}")
        self.logger.info(f"   Unique sources: {stats['unique_sources']}")
        self.logger.info(f"   Embedding dimension: {stats['embedding_dimension']}")
        self.logger.info(f"   Source files: {', '.join(stats['source_files'])}")

        self.logger.info("🎉 FAISS vector database pipeline completed successfully!")
        return True

def main():
    """Main function to run the vector database creation."""
    try:
        db_manager = ESGFAISSVectorDatabase()
        success = db_manager.run_pipeline()

        if success:
            print("\n✅ FAISS vector database created successfully!")

            # Demonstrate search functionality
            print("\n🔍 Testing search functionality...")
            query = "environmental sustainability"
            results = db_manager.search(query, k=3)

            if results:
                print(f"\nTop 3 results for '{query}':")
                for result in results:
                    print(f"  {result['rank']}. Score: {result['similarity_score']:.3f}")
                    print(f"     Source: {result['metadata']['source']}")
                    print(f"     Text: {result['text'][:100]}...")
                    print()
        else:
            print("\n❌ FAISS vector database creation failed!")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
