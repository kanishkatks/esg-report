#!/usr/bin/env python3
"""
ESG Document Processing Pipeline (FAISS Version)

This script runs the complete pipeline:
1. Extract text from PDFs
2. Create FAISS vector database
3. Display results and provide search functionality
"""

import sys
import time
from pathlib import Path

# Import our modules
from parse_pdf import process_pdfs_in_directory
from vector_database import ESGFAISSVectorDatabase

def print_banner():
    """Print a nice banner for the pipeline."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║            ESG Document Processing Pipeline (FAISS)         ║
║                                                              ║
║  📄 PDF Text Extraction → 🧠 Vector Embeddings → 🗄️  FAISS DB  ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def run_complete_pipeline():
    """Run the complete ESG document processing pipeline."""
    print_banner()

    start_time = time.time()

    try:
        # Step 1: PDF Text Extraction
        print("\n" + "="*60)
        print("📄 STEP 1: PDF TEXT EXTRACTION")
        print("="*60)

        processed_files = process_pdfs_in_directory()

        if not processed_files:
            print("❌ No PDF files were processed. Please check:")
            print("   - PDF files exist in the docs/ directory")
            print("   - PDF files are not corrupted")
            print("   - File permissions are correct")
            return False

        print(f"✅ Successfully extracted text from {len(processed_files)} PDF files")

        # Step 2: FAISS Vector Database Creation
        print("\n" + "="*60)
        print("🧠 STEP 2: FAISS VECTOR DATABASE CREATION")
        print("="*60)

        db_manager = ESGFAISSVectorDatabase()
        success = db_manager.run_pipeline()

        if not success:
            print("❌ FAISS vector database creation failed!")
            return False

        # Step 3: Final Statistics and Demo
        print("\n" + "="*60)
        print("📊 PIPELINE SUMMARY")
        print("="*60)

        stats = db_manager.get_statistics()
        elapsed_time = time.time() - start_time

        print(f"⏱️  Total processing time: {elapsed_time:.2f} seconds")
        print(f"📄 PDF files processed: {len(processed_files)}")
        print(f"📝 Text chunks created: {stats['total_chunks']}")
        print(f"📚 Unique source files: {stats['unique_sources']}")
        print(f"🔢 Embedding dimension: {stats['embedding_dimension']}")
        print(f"🗄️  FAISS database ready for queries!")

        # Display source files
        if stats['source_files']:
            print(f"\n📋 Processed source files:")
            for i, source in enumerate(stats['source_files'], 1):
                print(f"   {i}. {source}")

        # Step 4: Search Demonstration
        print("\n" + "="*60)
        print("🔍 SEARCH DEMONSTRATION")
        print("="*60)

        demo_queries = [
            "environmental sustainability",
            "ESG rating methodology",
            "governance transparency",
            "climate change risks"
        ]

        print("🎯 Testing search functionality with sample queries...")
        for query in demo_queries:
            print(f"\n🔍 Query: '{query}'")
            results = db_manager.search(query, k=2)

            if results:
                for result in results[:2]:  # Show top 2 results
                    print(f"  📄 {result['metadata']['source']} (Score: {result['similarity_score']:.3f})")
                    print(f"     {result['text'][:100]}...")
            else:
                print("  ❌ No results found")

        print("\n" + "="*60)
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)

        print("\n💡 Next steps:")
        print("   - Use interactive search: python search_documents.py")
        print("   - Single query search: python search_documents.py --query 'your query'")
        print("   - Batch search: python search_documents.py --batch queries.txt")
        print("   - Check logs in esg_parser.log for details")

        return True

    except KeyboardInterrupt:
        print("\n⚠️  Pipeline interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")

    issues = []

    # Check if docs directory exists
    docs_path = Path("docs")
    if not docs_path.exists():
        issues.append("❌ 'docs' directory not found")
    elif not any(docs_path.glob("*.pdf")):
        issues.append("⚠️  No PDF files found in 'docs' directory")
    else:
        pdf_count = len(list(docs_path.glob("*.pdf")))
        print(f"✅ Found {pdf_count} PDF files in docs directory")

    # Check if .env file exists
    env_path = Path(".env")
    if not env_path.exists():
        issues.append("⚠️  .env file not found (using defaults)")
    else:
        print("✅ Configuration file (.env) found")

    # Check if required Python packages are installed
    try:
        import faiss
        import sentence_transformers
        import fitz
        import sklearn
        print("✅ Required Python packages appear to be installed")
    except ImportError as e:
        issues.append(f"❌ Missing Python package: {e}")

    # Check if vectorstore directory exists (for existing index)
    vectorstore_path = Path("vectorstore")
    if vectorstore_path.exists():
        index_files = list(vectorstore_path.glob("*.index")) + list(vectorstore_path.glob("*.pkl"))
        if index_files:
            print(f"ℹ️  Found existing vector database with {len(index_files)} files")
            print("   The pipeline will recreate the database")

    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"   {issue}")

        if any("❌" in issue for issue in issues):
            print("\n❌ Critical issues found. Please resolve them before running the pipeline.")
            return False
        else:
            print("\n⚠️  Some warnings found, but pipeline can continue.")

    print("✅ Prerequisites check completed\n")
    return True

def show_help():
    """Show help information."""
    help_text = """
🔧 ESG Document Processing Pipeline Help

USAGE:
  python run_pipeline.py [options]

OPTIONS:
  --help, -h     Show this help message
  --skip-pdf     Skip PDF extraction (use existing text files)
  --search-only  Skip pipeline, just run search demo

EXAMPLES:
  # Run complete pipeline
  python run_pipeline.py

  # Skip PDF extraction if text files already exist
  python run_pipeline.py --skip-pdf

  # Just demonstrate search functionality
  python run_pipeline.py --search-only

SEARCH TOOLS:
  # Interactive search
  python search_documents.py

  # Single query
  python search_documents.py --query "environmental sustainability"

  # Batch search
  python search_documents.py --batch queries.txt --output results.json

CONFIGURATION:
  Edit .env file to customize:
  - DOCS_DIRECTORY: Directory containing PDF files
  - INDEX_DIRECTORY: Directory for FAISS index files
  - CHUNK_SIZE: Maximum characters per text chunk
  - EMBEDDING_MODEL: Sentence transformer model to use
  - LOG_LEVEL: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
    """
    print(help_text)

def search_only_demo():
    """Run search demonstration only."""
    print("🔍 Search Demonstration Mode")
    print("=" * 40)

    db = ESGFAISSVectorDatabase()

    # Try to load existing index
    if not db.load_index():
        print("❌ No existing FAISS index found. Please run the full pipeline first:")
        print("   python run_pipeline.py")
        return False

    if not db.load_embedding_model():
        print("❌ Failed to load embedding model")
        return False

    # Show statistics
    stats = db.get_statistics()
    print(f"📊 Loaded database: {stats['total_chunks']} chunks from {stats['unique_sources']} sources")

    # Interactive search
    print("\n🔍 Enter queries to search (type 'quit' to exit):")
    while True:
        try:
            query = input("\nQuery: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break

            if not query:
                continue

            results = db.search(query, k=3)
            if results:
                print(f"\nTop 3 results for '{query}':")
                for result in results:
                    print(f"  {result['rank']}. Score: {result['similarity_score']:.3f}")
                    print(f"     Source: {result['metadata']['source']}")
                    print(f"     Text: {result['text'][:100]}...")
            else:
                print("No results found")

        except KeyboardInterrupt:
            break

    return True

def main():
    """Main function."""
    # Parse simple command line arguments
    args = sys.argv[1:]

    if '--help' in args or '-h' in args:
        show_help()
        return

    if '--search-only' in args:
        success = search_only_demo()
        sys.exit(0 if success else 1)

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Run pipeline
    skip_pdf = '--skip-pdf' in args

    if skip_pdf:
        print("⏭️  Skipping PDF extraction (using existing text files)")

        # Check if text files exist
        docs_path = Path("docs")
        text_files = list(docs_path.glob("*.txt"))
        if not text_files:
            print("❌ No text files found in docs directory")
            print("   Remove --skip-pdf flag to extract from PDFs")
            sys.exit(1)

        print(f"✅ Found {len(text_files)} existing text files")

        # Run only vector database creation
        print("\n" + "="*60)
        print("🧠 FAISS VECTOR DATABASE CREATION")
        print("="*60)

        db_manager = ESGFAISSVectorDatabase()
        success = db_manager.run_pipeline()

        if success:
            print("\n🎊 FAISS vector database created successfully!")
        else:
            print("\n💥 FAISS vector database creation failed!")
            sys.exit(1)
    else:
        # Run complete pipeline
        success = run_complete_pipeline()

        if success:
            print("\n🎊 All done! Your ESG FAISS vector database is ready to use.")
        else:
            print("\n💥 Pipeline failed. Check the logs for more details.")
            sys.exit(1)

if __name__ == "__main__":
    main()
