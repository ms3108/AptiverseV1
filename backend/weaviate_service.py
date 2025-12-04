"""
Weaviate Vector Database Setup and Management
- Stores question embeddings for semantic search
- Enables duplicate detection via similarity
- Powers RAG-based question recommendations
"""
import os
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Property, DataType, Configure
from typing import List, Dict, Optional, Any
from database import SessionLocal
from models import Question

# Weaviate client singleton
_client = None

def get_weaviate_client():
    """Get or create Weaviate client"""
    global _client
    
    if _client is not None:
        return _client
    
    weaviate_url = os.getenv("WEAVIATE_URL")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
    
    if not weaviate_url:
        print("⚠️ WEAVIATE_URL not configured - vector search disabled")
        return None
    
    try:
        # Connect to Weaviate Cloud
        _client = weaviate.connect_to_weaviate_cloud(
            cluster_url=weaviate_url,
            auth_credentials=Auth.api_key(weaviate_api_key) if weaviate_api_key else None,
        )
        print("✅ Connected to Weaviate Cloud")
        return _client
    except Exception as e:
        print(f"❌ Weaviate connection failed: {e}")
        return None


def close_weaviate_client():
    """Close Weaviate client connection"""
    global _client
    if _client:
        _client.close()
        _client = None


def create_question_schema():
    """Create the Question collection schema in Weaviate"""
    client = get_weaviate_client()
    if not client:
        return False
    
    try:
        # Check if collection already exists
        if client.collections.exists("Question"):
            print("ℹ️ Question collection already exists")
            return True
        
        # Create collection with vectorizer
        client.collections.create(
            name="Question",
            properties=[
                Property(name="question_id", data_type=DataType.INT),
                Property(name="title", data_type=DataType.TEXT),
                Property(name="description", data_type=DataType.TEXT),
                Property(name="topic", data_type=DataType.TEXT),
                Property(name="category", data_type=DataType.TEXT),
                Property(name="difficulty", data_type=DataType.TEXT),
                Property(name="combined_text", data_type=DataType.TEXT),  # For embedding
            ],
            # Use Weaviate's built-in text2vec-weaviate vectorizer (free tier compatible)
            vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),
        )
        print("✅ Question collection created with vectorizer")
        return True
    except Exception as e:
        print(f"❌ Failed to create schema: {e}")
        return False


def index_question(question: Question) -> bool:
    """Index a single question into Weaviate"""
    client = get_weaviate_client()
    if not client:
        return False
    
    try:
        collection = client.collections.get("Question")
        
        # Combine text for better embeddings
        combined_text = f"{question.title}. {question.description}. Topic: {question.topic}. Category: {question.category}."
        
        # Check if already exists
        existing = collection.query.fetch_objects(
            filters=weaviate.classes.query.Filter.by_property("question_id").equal(question.id),
            limit=1
        )
        
        if existing.objects:
            # Update existing
            collection.data.update(
                uuid=existing.objects[0].uuid,
                properties={
                    "question_id": question.id,
                    "title": question.title,
                    "description": question.description,
                    "topic": question.topic,
                    "category": question.category,
                    "difficulty": question.difficulty,
                    "combined_text": combined_text,
                }
            )
        else:
            # Insert new
            collection.data.insert(
                properties={
                    "question_id": question.id,
                    "title": question.title,
                    "description": question.description,
                    "topic": question.topic,
                    "category": question.category,
                    "difficulty": question.difficulty,
                    "combined_text": combined_text,
                }
            )
        return True
    except Exception as e:
        print(f"❌ Failed to index question {question.id}: {e}")
        return False


def index_all_questions():
    """Index all questions from PostgreSQL into Weaviate"""
    client = get_weaviate_client()
    if not client:
        print("❌ No Weaviate client available")
        return
    
    # Create schema if needed
    create_question_schema()
    
    db = SessionLocal()
    questions = db.query(Question).all()
    
    success = 0
    failed = 0
    
    for q in questions:
        if index_question(q):
            success += 1
            print(f"✅ Indexed: {q.title}")
        else:
            failed += 1
            print(f"❌ Failed: {q.title}")
    
    db.close()
    print(f"\n📊 Indexing complete: {success} success, {failed} failed")


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
    client = get_weaviate_client()
    if not client:
        return []
    
    try:
        collection = client.collections.get("Question")
        
        # Build query
        query = collection.query.near_text(
            query=query_text,
            limit=limit,
            return_metadata=weaviate.classes.query.MetadataQuery(distance=True)
        )
        
        # Apply category filter if specified
        if category:
            query = collection.query.near_text(
                query=query_text,
                limit=limit,
                filters=weaviate.classes.query.Filter.by_property("category").equal(category),
                return_metadata=weaviate.classes.query.MetadataQuery(distance=True)
            )
        
        results = []
        for obj in query.objects:
            results.append({
                "question_id": obj.properties.get("question_id"),
                "title": obj.properties.get("title"),
                "description": obj.properties.get("description"),
                "topic": obj.properties.get("topic"),
                "category": obj.properties.get("category"),
                "difficulty": obj.properties.get("difficulty"),
                "similarity": 1 - (obj.metadata.distance or 0),  # Convert distance to similarity
            })
        
        return results
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []


def check_duplicate(title: str, description: str, threshold: float = 0.92) -> Optional[Dict]:
    """
    Check if a similar question already exists (for duplicate detection)
    
    Args:
        title: Question title
        description: Question description
        threshold: Similarity threshold (0.92 = 92% similar)
    
    Returns:
        Similar question if found, None otherwise
    """
    query_text = f"{title}. {description}"
    similar = find_similar_questions(query_text, limit=1)
    
    if similar and similar[0]["similarity"] >= threshold:
        return similar[0]
    return None


def get_questions_for_weak_topic(topic: str, limit: int = 5) -> List[Dict]:
    """Get questions for a specific weak topic using semantic search"""
    return find_similar_questions(f"Questions about {topic}", limit=limit)


def get_recommended_questions(user_history: List[str], limit: int = 10) -> List[Dict]:
    """
    Get recommended questions based on user's practice history
    Uses semantic similarity to find related but different questions
    """
    if not user_history:
        return []
    
    # Combine recent topics/categories into a query
    query = f"Practice questions for: {', '.join(user_history[-5:])}"
    return find_similar_questions(query, limit=limit)


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            print("Setting up Weaviate schema...")
            create_question_schema()
            
        elif command == "index":
            print("Indexing all questions...")
            index_all_questions()
            
        elif command == "search":
            query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "percentage calculation"
            print(f"Searching for: {query}")
            results = find_similar_questions(query)
            for r in results:
                print(f"  [{r['similarity']:.2f}] {r['title']} ({r['category']} - {r['topic']})")
        
        elif command == "test":
            print("Testing Weaviate connection...")
            client = get_weaviate_client()
            if client:
                print("✅ Connection successful!")
                if client.collections.exists("Question"):
                    collection = client.collections.get("Question")
                    count = collection.aggregate.over_all(total_count=True)
                    print(f"📊 Questions indexed: {count.total_count}")
            close_weaviate_client()
    else:
        print("Usage:")
        print("  python weaviate_service.py setup  - Create schema")
        print("  python weaviate_service.py index  - Index all questions")
        print("  python weaviate_service.py search <query>  - Search questions")
        print("  python weaviate_service.py test   - Test connection")
