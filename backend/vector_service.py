"""
ChromaDB Vector Database Service
- Free, open-source vector database
- Runs locally (no external service needed)
- Stores question embeddings for semantic search
- Enables duplicate detection and recommendations
- LAZY LOADING: Only initializes when first used (not on app startup)
"""
import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from database import SessionLocal
from models import Question

# ChromaDB client singleton - LAZY LOADED
_client = None
_collection = None
_initialized = False

# Persist directory for ChromaDB
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "/app/chroma_db")


def get_chroma_client():
    """Get or create ChromaDB client - LAZY LOADING"""
    global _client, _initialized
    
    if _client is not None:
        return _client
    
    if _initialized:
        return None  # Already tried and failed
    
    _initialized = True
    
    try:
        # Use persistent storage
        _client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        print(f"✅ ChromaDB initialized at {CHROMA_PERSIST_DIR}")
        return _client
    except Exception as e:
        print(f"⚠️ ChromaDB with persistence failed, using in-memory: {e}")
        try:
            # Fallback to ephemeral (in-memory) client
            _client = chromadb.EphemeralClient()
            return _client
        except Exception as e2:
            print(f"❌ ChromaDB initialization failed completely: {e2}")
            return None


def get_question_collection():
    """Get or create the questions collection"""
    global _collection
    
    if _collection is not None:
        return _collection
    
    client = get_chroma_client()
    if not client:
        return None
    
    try:
        # Get or create collection with default embedding function
        _collection = client.get_or_create_collection(
            name="questions",
            metadata={"description": "Aptiverse question embeddings"}
        )
        print(f"✅ Questions collection ready ({_collection.count()} items)")
        return _collection
    except Exception as e:
        print(f"❌ Failed to get collection: {e}")
        return None


def index_question(question: Question) -> bool:
    """Index a single question into ChromaDB"""
    collection = get_question_collection()
    if not collection:
        return False
    
    try:
        # Create combined text for embedding
        combined_text = f"{question.title}. {question.description}. Topic: {question.topic}. Category: {question.category}. Difficulty: {question.difficulty}."
        
        # Unique ID for the question
        doc_id = f"q_{question.id}"
        
        # Upsert (add or update)
        collection.upsert(
            ids=[doc_id],
            documents=[combined_text],
            metadatas=[{
                "question_id": question.id,
                "title": question.title,
                "topic": question.topic or "",
                "category": question.category or "",
                "difficulty": question.difficulty or "",
            }]
        )
        return True
    except Exception as e:
        print(f"❌ Failed to index question {question.id}: {e}")
        return False


def index_all_questions():
    """Index all questions from PostgreSQL into ChromaDB"""
    collection = get_question_collection()
    if not collection:
        print("❌ No ChromaDB collection available")
        return
    
    db = SessionLocal()
    questions = db.query(Question).all()
    
    success = 0
    failed = 0
    
    # Batch indexing for efficiency
    ids = []
    documents = []
    metadatas = []
    
    for q in questions:
        combined_text = f"{q.title}. {q.description}. Topic: {q.topic}. Category: {q.category}. Difficulty: {q.difficulty}."
        
        ids.append(f"q_{q.id}")
        documents.append(combined_text)
        metadatas.append({
            "question_id": q.id,
            "title": q.title,
            "topic": q.topic or "",
            "category": q.category or "",
            "difficulty": q.difficulty or "",
        })
    
    try:
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        success = len(ids)
        print(f"✅ Indexed {success} questions")
    except Exception as e:
        print(f"❌ Batch indexing failed: {e}")
        failed = len(ids)
    
    db.close()
    print(f"\n📊 Indexing complete: {success} success, {failed} failed")
    print(f"📦 Total in collection: {collection.count()}")


def find_similar_questions(query_text: str, limit: int = 5, category: str = None) -> List[Dict]:
    """
    Find semantically similar questions using vector search
    
    Args:
        query_text: Text to search for
        limit: Max results to return
        category: Optional category filter
    
    Returns:
        List of similar questions with scores
    """
    collection = get_question_collection()
    if not collection:
        return []
    
    try:
        # Build query with optional filter
        where_filter = None
        if category:
            where_filter = {"category": category}
        
        results = collection.query(
            query_texts=[query_text],
            n_results=limit,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        similar = []
        if results and results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 1.0
                
                # Convert distance to similarity (ChromaDB uses L2 distance by default)
                # Lower distance = more similar
                similarity = max(0, 1 - (distance / 2))  # Normalize to 0-1
                
                similar.append({
                    "question_id": metadata.get("question_id"),
                    "title": metadata.get("title", ""),
                    "topic": metadata.get("topic", ""),
                    "category": metadata.get("category", ""),
                    "difficulty": metadata.get("difficulty", ""),
                    "similarity": round(similarity, 3),
                    "distance": round(distance, 3),
                })
        
        return similar
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []


def check_duplicate(title: str, description: str, threshold: float = 0.85) -> Optional[Dict]:
    """
    Check if a similar question already exists (for duplicate detection)
    
    Args:
        title: Question title
        description: Question description  
        threshold: Similarity threshold (0.85 = 85% similar)
    
    Returns:
        Similar question if found above threshold, None otherwise
    """
    query_text = f"{title}. {description}"
    similar = find_similar_questions(query_text, limit=1)
    
    if similar and similar[0]["similarity"] >= threshold:
        return similar[0]
    return None


def get_questions_for_topic(topic: str, limit: int = 5) -> List[Dict]:
    """Get questions for a specific topic using semantic search"""
    return find_similar_questions(f"Questions about {topic}", limit=limit)


def get_recommended_questions(weak_topics: List[str], limit: int = 10) -> List[Dict]:
    """
    Get recommended questions based on user's weak topics
    """
    if not weak_topics:
        return []
    
    # Combine weak topics into a query
    query = f"Practice questions for: {', '.join(weak_topics)}"
    return find_similar_questions(query, limit=limit)


def get_collection_stats() -> Dict:
    """Get statistics about the vector collection"""
    collection = get_question_collection()
    if not collection:
        return {"status": "unavailable", "count": 0}
    
    return {
        "status": "ready",
        "count": collection.count(),
        "name": collection.name,
    }


# For backwards compatibility with existing code
def get_weaviate_client():
    """Backwards compatibility - returns None since we use ChromaDB now"""
    return None


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "index":
            print("Indexing all questions into ChromaDB...")
            index_all_questions()
            
        elif command == "search":
            query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "percentage calculation"
            print(f"Searching for: {query}\n")
            results = find_similar_questions(query)
            for r in results:
                print(f"  [{r['similarity']:.2f}] {r['title']}")
                print(f"      {r['category']} - {r['topic']} ({r['difficulty']})")
        
        elif command == "stats":
            stats = get_collection_stats()
            print(f"📊 ChromaDB Stats:")
            print(f"  Status: {stats['status']}")
            print(f"  Questions indexed: {stats['count']}")
            
        elif command == "duplicate":
            title = sys.argv[2] if len(sys.argv) > 2 else "Percentage Increase"
            desc = sys.argv[3] if len(sys.argv) > 3 else "Calculate percentage"
            print(f"Checking for duplicates...")
            dup = check_duplicate(title, desc)
            if dup:
                print(f"⚠️ Duplicate found: {dup['title']} (similarity: {dup['similarity']:.2f})")
            else:
                print("✅ No duplicates found")
                
    else:
        print("ChromaDB Vector Service")
        print("=" * 40)
        print("Usage:")
        print("  python vector_service.py index     - Index all questions")
        print("  python vector_service.py search <query>  - Search questions")
        print("  python vector_service.py stats     - Show collection stats")
        print("  python vector_service.py duplicate <title> <desc>  - Check duplicate")
        print()
        
        # Show current stats
        stats = get_collection_stats()
        print(f"Current status: {stats['status']}, {stats['count']} questions indexed")
