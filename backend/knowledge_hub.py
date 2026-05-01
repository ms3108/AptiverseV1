"""
Knowledge Hub — Gap 6
Implements:
  - CRUD for user-generated knowledge articles
  - Hybrid search: Postgres LIKE (lexical) + ChromaDB (semantic), merged by weighted score
"""
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

import models
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/knowledge", tags=["knowledge-hub"])

# ---------------------------------------------------------------------------
# ChromaDB knowledge collection (lazy-loaded)
# ---------------------------------------------------------------------------
_kb_collection = None


def _get_kb_collection():
    global _kb_collection
    if _kb_collection is not None:
        return _kb_collection
    try:
        import chromadb
        from chromadb.config import Settings
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "/app/chroma_db")
        client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )
        _kb_collection = client.get_or_create_collection(
            name="knowledge_hub",
            metadata={"description": "Aptiverse knowledge article embeddings"},
        )
        print(f"✅ Knowledge Hub ChromaDB collection ready ({_kb_collection.count()} items)")
        return _kb_collection
    except Exception as e:
        print(f"⚠️ Knowledge Hub ChromaDB unavailable: {e}")
        return None


def _index_article(article: models.KnowledgeContent) -> None:
    """Index (or re-index) an article into ChromaDB."""
    col = _get_kb_collection()
    if not col:
        return
    try:
        doc_id = f"kb_{article.id}"
        combined = f"{article.title}. {article.body}"
        col.upsert(
            ids=[doc_id],
            documents=[combined],
            metadatas=[{
                "article_id": article.id,
                "title": article.title,
                "author_id": article.author_id,
            }],
        )
    except Exception as e:
        print(f"⚠️ Failed to index knowledge article {article.id}: {e}")


def _semantic_search(query: str, limit: int = 10) -> List[dict]:
    """Return semantic matches from ChromaDB."""
    col = _get_kb_collection()
    if not col or col.count() == 0:
        return []
    try:
        results = col.query(
            query_texts=[query],
            n_results=min(limit, col.count()),
            include=["metadatas", "distances"],
        )
        hits = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                meta = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                similarity = max(0.0, 1.0 - distance / 2.0)
                hits.append({
                    "article_id": int(meta.get("article_id", 0)),
                    "semantic_score": round(similarity, 4),
                })
        return hits
    except Exception as e:
        print(f"⚠️ Semantic search error: {e}")
        return []


# ---------------------------------------------------------------------------
# Helper to serialize an article
# ---------------------------------------------------------------------------
def _serialize(article: models.KnowledgeContent, current_user_id: Optional[int] = None) -> dict:
    user_vote = None
    if current_user_id:
        for v in (article.votes or []):
            if v.user_id == current_user_id:
                user_vote = v.vote_type
                break
    return {
        "id": article.id,
        "title": article.title,
        "body": article.body,
        "status": article.status,
        "upvotes": article.upvotes,
        "downvotes": article.downvotes,
        "author": article.author.username if article.author else "Unknown",
        "author_id": article.author_id,
        "user_vote": user_vote,
        "created_at": article.created_at.isoformat() if article.created_at else None,
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("")
def create_article(
    payload: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new knowledge article (self-published)."""
    title = (payload.get("title") or "").strip()
    body = (payload.get("body") or "").strip()

    if not title or len(title) < 5:
        raise HTTPException(status_code=400, detail="Title must be at least 5 characters.")
    if not body or len(body) < 20:
        raise HTTPException(status_code=400, detail="Body must be at least 20 characters.")

    article = models.KnowledgeContent(
        author_id=current_user.id,
        title=title,
        body=body,
        status="published",
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    # Index in ChromaDB for semantic search
    _index_article(article)

    return {"message": "Article published", "article": _serialize(article, current_user.id)}


@router.get("")
def list_articles(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List published knowledge articles, newest first."""
    total = db.query(models.KnowledgeContent).filter(
        models.KnowledgeContent.status == "published"
    ).count()

    articles = db.query(models.KnowledgeContent).filter(
        models.KnowledgeContent.status == "published"
    ).order_by(desc(models.KnowledgeContent.created_at)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "articles": [_serialize(a, current_user.id) for a in articles],
    }


@router.get("/search")
def search_articles(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Hybrid search: combines Postgres lexical (LIKE) + ChromaDB semantic results.
    Returns a merged, deduplicated ranked list.
    """
    q = q.strip()
    article_scores: dict = {}  # article_id -> {article, score}

    # ---- 1. Lexical search (Postgres/SQLite LIKE) ----
    pattern = f"%{q}%"
    lexical_hits = db.query(models.KnowledgeContent).filter(
        models.KnowledgeContent.status == "published",
        or_(
            models.KnowledgeContent.title.ilike(pattern),
            models.KnowledgeContent.body.ilike(pattern),
        ),
    ).limit(limit).all()

    for rank, article in enumerate(lexical_hits):
        lexical_score = 1.0 - (rank / max(len(lexical_hits), 1)) * 0.5  # 1.0 → 0.5
        article_scores[article.id] = {
            "article": article,
            "lexical_score": lexical_score,
            "semantic_score": 0.0,
        }

    # ---- 2. Semantic search (ChromaDB) ----
    semantic_hits = _semantic_search(q, limit=limit)
    for hit in semantic_hits:
        aid = hit["article_id"]
        if aid in article_scores:
            article_scores[aid]["semantic_score"] = hit["semantic_score"]
        else:
            # Fetch from DB if not in lexical results
            article = db.query(models.KnowledgeContent).filter(
                models.KnowledgeContent.id == aid,
                models.KnowledgeContent.status == "published",
            ).first()
            if article:
                article_scores[aid] = {
                    "article": article,
                    "lexical_score": 0.0,
                    "semantic_score": hit["semantic_score"],
                }

    # ---- 3. Hybrid ranking (0.4 * lexical + 0.6 * semantic) ----
    def hybrid_score(entry: dict) -> float:
        return 0.4 * entry["lexical_score"] + 0.6 * entry["semantic_score"]

    ranked = sorted(article_scores.values(), key=hybrid_score, reverse=True)[:limit]

    return {
        "query": q,
        "total": len(ranked),
        "articles": [
            {
                **_serialize(e["article"], current_user.id),
                "lexical_score": round(e["lexical_score"], 3),
                "semantic_score": round(e["semantic_score"], 3),
                "hybrid_score": round(hybrid_score(e), 3),
            }
            for e in ranked
        ],
    }


@router.get("/{article_id}")
def get_article(
    article_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single knowledge article by ID."""
    article = db.query(models.KnowledgeContent).filter(
        models.KnowledgeContent.id == article_id,
        models.KnowledgeContent.status == "published",
    ).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return _serialize(article, current_user.id)


@router.put("/{article_id}")
def update_article(
    article_id: int,
    payload: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update own knowledge article."""
    article = db.query(models.KnowledgeContent).filter(
        models.KnowledgeContent.id == article_id
    ).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorised to edit this article")

    if "title" in payload:
        article.title = payload["title"]
    if "body" in payload:
        article.body = payload["body"]

    db.commit()
    db.refresh(article)

    # Re-index updated content
    _index_article(article)

    return {"message": "Article updated", "article": _serialize(article, current_user.id)}


@router.delete("/{article_id}")
def delete_article(
    article_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Archive (soft-delete) own knowledge article."""
    article = db.query(models.KnowledgeContent).filter(
        models.KnowledgeContent.id == article_id
    ).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorised")

    article.status = "archived"
    db.commit()
    return {"message": "Article archived"}


@router.post("/{article_id}/vote")
def vote_article(
    article_id: int,
    payload: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Vote on an article. payload: {"vote_type": 1} or {"vote_type": -1}.
    Sending the same vote again removes it (toggle).
    """
    vote_type = payload.get("vote_type")
    if vote_type not in (1, -1):
        raise HTTPException(status_code=400, detail="vote_type must be 1 or -1")

    article = db.query(models.KnowledgeContent).filter(
        models.KnowledgeContent.id == article_id,
        models.KnowledgeContent.status == "published",
    ).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    existing = db.query(models.KnowledgeVote).filter(
        models.KnowledgeVote.content_id == article_id,
        models.KnowledgeVote.user_id == current_user.id,
    ).first()

    if existing:
        if existing.vote_type == vote_type:
            # Toggle off
            if vote_type == 1:
                article.upvotes = max(0, article.upvotes - 1)
            else:
                article.downvotes = max(0, article.downvotes - 1)
            db.delete(existing)
            db.commit()
            return {"message": "Vote removed", "upvotes": article.upvotes, "downvotes": article.downvotes}
        else:
            # Flip vote
            if existing.vote_type == 1:
                article.upvotes = max(0, article.upvotes - 1)
                article.downvotes += 1
            else:
                article.downvotes = max(0, article.downvotes - 1)
                article.upvotes += 1
            existing.vote_type = vote_type
    else:
        db.add(models.KnowledgeVote(
            content_id=article_id,
            user_id=current_user.id,
            vote_type=vote_type,
        ))
        if vote_type == 1:
            article.upvotes += 1
        else:
            article.downvotes += 1

    db.commit()
    db.refresh(article)
    return {
        "message": "Vote recorded",
        "upvotes": article.upvotes,
        "downvotes": article.downvotes,
        "user_vote": vote_type,
    }
