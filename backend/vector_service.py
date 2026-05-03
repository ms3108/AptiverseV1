"""
Vector Service - No-op stub (ChromaDB removed)

Duplicate detection and semantic search are disabled.
All functions return safe no-op defaults so the rest of
the application continues to work normally.
"""
from typing import List, Dict, Optional


def index_question(question) -> bool:
    """No-op: ChromaDB removed. Returns False (not indexed)."""
    return False


def index_all_questions() -> None:
    """No-op: ChromaDB removed."""
    print("⚠️ vector_service: ChromaDB removed — skipping index_all_questions")


def check_duplicate(title: str, description: str, threshold: float = 0.85) -> Optional[Dict]:
    """No-op: ChromaDB removed. Always returns None (no duplicate found)."""
    return None


def find_similar_questions(query_text: str, limit: int = 5, category: str = None) -> List[Dict]:
    """No-op: ChromaDB removed. Returns empty list."""
    return []


def get_questions_for_topic(topic: str, limit: int = 5) -> List[Dict]:
    """No-op: ChromaDB removed. Returns empty list."""
    return []


def get_recommended_questions(weak_topics: List[str], limit: int = 10) -> List[Dict]:
    """No-op: ChromaDB removed. Returns empty list."""
    return []


def get_collection_stats() -> Dict:
    """No-op: ChromaDB removed."""
    return {"status": "disabled", "count": 0}


def get_weaviate_client():
    """No-op: Weaviate/ChromaDB removed."""
    return None
