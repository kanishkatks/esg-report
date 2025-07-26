#!/usr/bin/env python3
"""
ESG Document Search Utility

This script provides a command-line interface for searching through the FAISS vector database.
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Import our vector database module
from vector_database import ESGFAISSVectorDatabase

# Load environment variables
load_dotenv()

def interactive_search():
    """Run interactive search mode."""
    print("🔍 ESG Document Interactive Search")
    print("=" * 50)

    # Initialize database
    db = ESGFAISSVectorDatabase()

    # Load existing index
    if not db.load_index():
        print("❌ Failed to load FAISS index. Please run the pipeline first:")
        print("   python vector-database.py")
        return False

    # Load embedding model
    if not db.load_embedding_model():
        print("❌ Failed to load embedding model")
        return False

    # Display statistics
    stats = db.get_statistics()
    print(f"📊 Database loaded: {stats['total_chunks']} chunks from {stats['unique_sources']} sources")
    print(f"📁 Sources: {', '.join(stats['source_files'])}")
    print()

    # Interactive search loop
    while True:
        try:
            query = input("🔍 Enter your search query (or 'quit' to exit): ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            if not query:
                print("⚠️  Please enter a search query")
                continue

            # Get number of results
            try:
                k = int(input("📊 Number of results (default 5): ") or "5")
                k = max(1, min(k, 20))  # Limit between 1 and 20
            except ValueError:
                k = 5

            # Perform search
            print(f"\n🔍 Searching for: '{query}'...")
            results = db.search(query, k=k)

            if not results:
                print("❌ No results found")
                continue

            # Display results
            print(f"\n📋 Top {len(results)} results:")
            print("-" * 80)

            for result in results:
                print(f"🏆 Rank {result['rank']} | Score: {result['similarity_score']:.3f}")
                print(f"📄 Source: {result['metadata']['source']}")
                print(f"📍 Chunk {result['metadata']['chunk_index']} ({result['metadata']['chunk_size']} chars)")
                print(f"📝 Text: {result['text'][:200]}{'...' if len(result['text']) > 200 else ''}")
                print("-" * 80)

            print()

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error during search: {e}")
            continue

    return True

def batch_search(queries_file: str, output_file: str = None, k: int = 5):
    """Run batch search from a file of queries."""
    print(f"📁 Running batch search from: {queries_file}")

    # Initialize database
    db = ESGFAISSVectorDatabase()

    # Load existing index
    if not db.load_index():
        print("❌ Failed to load FAISS index. Please run the pipeline first:")
        print("   python vector-database.py")
        return False

    # Load embedding model
    if not db.load_embedding_model():
        print("❌ Failed to load embedding model")
        return False

    # Read queries
    try:
        with open(queries_file, 'r', encoding='utf-8') as f:
            queries = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Failed to read queries file: {e}")
        return False

    if not queries:
        print("❌ No queries found in file")
        return False

    print(f"🔍 Processing {len(queries)} queries...")

    # Process queries
    all_results = []
    for i, query in enumerate(queries, 1):
        print(f"🔍 Query {i}/{len(queries)}: {query[:50]}{'...' if len(query) > 50 else ''}")
        results = db.search(query, k=k)
        all_results.append({
            'query': query,
            'results': results
        })

    # Save results if output file specified
    if output_file:
        try:
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            print(f"✅ Results saved to: {output_file}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

    # Display summary
    print(f"\n📊 Batch search completed:")
    print(f"   Queries processed: {len(queries)}")
    print(f"   Results per query: {k}")
    print(f"   Total results: {len(queries) * k}")

    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Search ESG documents using FAISS vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive search mode
  python search_documents.py

  # Batch search from file
  python search_documents.py --batch queries.txt --output results.json --k 10

  # Single query search
  python search_documents.py --query "environmental sustainability" --k 5
        """
    )

    parser.add_argument(
        '--batch',
        type=str,
        help='File containing queries (one per line) for batch search'
    )

    parser.add_argument(
        '--query',
        type=str,
        help='Single query to search for'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output file for batch search results (JSON format)'
    )

    parser.add_argument(
        '--k',
        type=int,
        default=5,
        help='Number of results to return per query (default: 5)'
    )

    args = parser.parse_args()

    try:
        if args.batch:
            # Batch search mode
            success = batch_search(args.batch, args.output, args.k)
        elif args.query:
            # Single query mode
            db = ESGFAISSVectorDatabase()
            if not db.load_index() or not db.load_embedding_model():
                print("❌ Failed to load database")
                sys.exit(1)

            results = db.search(args.query, k=args.k)

            if results:
                print(f"\n🔍 Results for: '{args.query}'")
                print("-" * 60)
                for result in results:
                    print(f"🏆 Rank {result['rank']} | Score: {result['similarity_score']:.3f}")
                    print(f"📄 {result['metadata']['source']}")
                    print(f"📝 {result['text'][:150]}{'...' if len(result['text']) > 150 else ''}")
                    print("-" * 60)
            else:
                print("❌ No results found")

            success = True
        else:
            # Interactive mode (default)
            success = interactive_search()

        if not success:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
