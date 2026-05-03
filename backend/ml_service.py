"""
ML Service — Personalization, BKT Mastery, and Caching
Implements:
  - Bayesian Knowledge Tracing (BKT) for per-topic mastery probabilities
  - Weak-area detection using mastery table (falls back to aggregate stats)
  - Daily practice set generation
  - Redis-backed caching with in-process dict fallback
"""
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

import models

# ---------------------------------------------------------------------------
# Redis client — lazy-loaded, falls back gracefully
# ---------------------------------------------------------------------------
_redis_client = None
_redis_available = None  # None = untested, True/False = tested


def _get_redis():
    global _redis_client, _redis_available
    if _redis_available is False:
        return None
    if _redis_client is not None:
        return _redis_client
    try:
        import redis as redis_lib
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis_lib.from_url(url, decode_responses=True, socket_connect_timeout=1)
        _redis_client.ping()
        _redis_available = True
        print("✅ Redis connected for ML caching")
        return _redis_client
    except Exception as e:
        _redis_available = False
        print(f"⚠️ Redis unavailable, using in-process cache: {e}")
        return None


# ---------------------------------------------------------------------------
# In-process fallback caches (used when Redis is offline)
# ---------------------------------------------------------------------------
_weak_topic_cache: Dict[int, Tuple[datetime, List[str]]] = {}
_practice_set_cache: Dict[Tuple[int, int], Tuple[datetime, List[int]]] = {}


# ---------------------------------------------------------------------------
# Cache helpers — try Redis first, fall back to dict
# ---------------------------------------------------------------------------

def _cache_get(key: str) -> Optional[str]:
    r = _get_redis()
    if r:
        try:
            return r.get(key)
        except Exception:
            pass
    return None


def _cache_set(key: str, value: str, ttl_seconds: int) -> None:
    r = _get_redis()
    if r:
        try:
            r.setex(key, ttl_seconds, value)
            return
        except Exception:
            pass


def _get_cached_topics(user_id: int, ttl_seconds: int) -> Optional[List[str]]:
    raw = _cache_get(f"weak_topics:{user_id}")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    # fallback
    cached = _weak_topic_cache.get(user_id)
    if cached:
        ts, topics = cached
        if datetime.utcnow() - ts < timedelta(seconds=ttl_seconds):
            return topics
        _weak_topic_cache.pop(user_id, None)
    return None


def _set_cached_topics(user_id: int, topics: List[str], ttl_seconds: int = 600) -> None:
    _cache_set(f"weak_topics:{user_id}", json.dumps(topics), ttl_seconds)
    _weak_topic_cache[user_id] = (datetime.utcnow(), topics)


def _get_cached_practice(user_id: int, num_questions: int, ttl_seconds: int) -> Optional[List[int]]:
    raw = _cache_get(f"practice:{user_id}:{num_questions}")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    # fallback
    cached = _practice_set_cache.get((user_id, num_questions))
    if cached:
        ts, ids = cached
        if datetime.utcnow() - ts < timedelta(seconds=ttl_seconds):
            return ids
        _practice_set_cache.pop((user_id, num_questions), None)
    return None


def _set_cached_practice(user_id: int, num_questions: int, question_ids: List[int], ttl_seconds: int = 300) -> None:
    _cache_set(f"practice:{user_id}:{num_questions}", json.dumps(question_ids), ttl_seconds)
    _practice_set_cache[(user_id, num_questions)] = (datetime.utcnow(), question_ids)


# ---------------------------------------------------------------------------
# Backwards-compat stub (admin_routes imported this)
# ---------------------------------------------------------------------------
def get_weaviate_client():
    """Stub — Weaviate replaced by ChromaDB. Returns None."""
    return None


# ---------------------------------------------------------------------------
# BKT (Bayesian Knowledge Tracing) implementation
# ---------------------------------------------------------------------------
# Default BKT parameters — conservative defaults that generalise well
BKT_DEFAULTS = {
    "p_learn": 0.10,   # probability of learning after each attempt
    "p_guess": 0.25,   # probability of correct answer without mastery
    "p_slip": 0.10,    # probability of wrong answer despite mastery
    "forget_lambda": 0.01,  # per-day forgetting rate (exponential decay)
}


def bkt_update(
    p_mastery: float,
    is_correct: bool,
    p_learn: float = BKT_DEFAULTS["p_learn"],
    p_guess: float = BKT_DEFAULTS["p_guess"],
    p_slip: float = BKT_DEFAULTS["p_slip"],
    forget_lambda: float = BKT_DEFAULTS["forget_lambda"],
    delta_days: float = 0.0,
) -> float:
    """
    Single-step BKT update.

    1. Apply time-based forgetting (exponential decay):
       p = p * exp(-lambda * delta_days)
    2. Compute posterior after observing correctness:
       If correct:  p_obs = p*(1-slip) + (1-p)*guess
       If wrong:    p_obs = p*slip + (1-p)*(1-guess)
       Posterior:   p_new = P(L|obs) = P(obs|L)*p / p_obs
    3. Apply learning transition:
       p_final = p_new + (1-p_new)*p_learn
    Returns clamped float in [0.01, 0.99].
    """
    import math

    # Step 1: forgetting
    if delta_days > 0:
        p_mastery = p_mastery * math.exp(-forget_lambda * delta_days)

    # Step 2: posterior
    if is_correct:
        p_obs = p_mastery * (1 - p_slip) + (1 - p_mastery) * p_guess
        if p_obs == 0:
            p_obs = 1e-9
        p_posterior = (p_mastery * (1 - p_slip)) / p_obs
    else:
        p_obs = p_mastery * p_slip + (1 - p_mastery) * (1 - p_guess)
        if p_obs == 0:
            p_obs = 1e-9
        p_posterior = (p_mastery * p_slip) / p_obs

    # Step 3: learning
    p_final = p_posterior + (1 - p_posterior) * p_learn

    return max(0.01, min(0.99, p_final))


def update_mastery_after_attempt(
    db: Session,
    user_id: int,
    topic: str,
    is_correct: bool,
    time_taken_seconds: int = 60,
) -> float:
    """
    Load (or create) the UserTopicMastery row for this user+topic,
    apply BKT update, persist and return new p_mastery.

    time_taken_seconds is used as a mild confidence modifier:
    very slow correct answers slightly reduce the effective update.
    """
    row = db.query(models.UserTopicMastery).filter(
        models.UserTopicMastery.user_id == user_id,
        models.UserTopicMastery.topic == topic,
    ).first()

    now = datetime.utcnow()

    if row is None:
        row = models.UserTopicMastery(
            user_id=user_id,
            topic=topic,
            p_mastery=BKT_DEFAULTS["p_learn"],  # start with small prior
            p_learn=BKT_DEFAULTS["p_learn"],
            p_guess=BKT_DEFAULTS["p_guess"],
            p_slip=BKT_DEFAULTS["p_slip"],
            forget_lambda=BKT_DEFAULTS["forget_lambda"],
            updated_at=now,
        )
        db.add(row)
        db.flush()

    # Time since last update (for forgetting)
    delta_days = 0.0
    if row.updated_at:
        delta_days = (now - row.updated_at).total_seconds() / 86400.0

    # Slow correct answers (>2× expected time) modestly inflate slip
    effective_slip = row.p_slip
    if is_correct and time_taken_seconds > 120:
        effective_slip = min(0.35, row.p_slip * 1.5)

    new_p = bkt_update(
        p_mastery=row.p_mastery,
        is_correct=is_correct,
        p_learn=row.p_learn,
        p_guess=row.p_guess,
        p_slip=effective_slip,
        forget_lambda=row.forget_lambda,
        delta_days=delta_days,
    )

    row.p_mastery = new_p
    row.updated_at = now
    db.commit()

    # Invalidate cached weak topics for this user
    _cache_set(f"weak_topics:{user_id}", "", 1)  # TTL=1s effectively removes it
    _weak_topic_cache.pop(user_id, None)

    return new_p


# ---------------------------------------------------------------------------
# Weak-area detection — uses BKT mastery table, falls back to aggregates
# ---------------------------------------------------------------------------

def predict_weak_areas(db: Session, user_id: int, threshold: float = 60.0) -> List[str]:
    """Identify weak topics. Uses BKT mastery when available, else aggregate stats."""
    cached_topics = _get_cached_topics(user_id, ttl_seconds=600)
    if cached_topics is not None:
        return cached_topics

    # --- Try BKT mastery table first ---
    mastery_rows = db.query(models.UserTopicMastery).filter(
        models.UserTopicMastery.user_id == user_id
    ).all()

    if mastery_rows:
        mastery_threshold = threshold / 100.0  # e.g. 60% → 0.60
        weak_topics = [r.topic for r in mastery_rows if r.p_mastery < mastery_threshold]

        if not weak_topics:
            # All topics above threshold — return lowest mastery topics
            sorted_rows = sorted(mastery_rows, key=lambda r: r.p_mastery)
            weak_topics = [r.topic for r in sorted_rows[:3]]

        _set_cached_topics(user_id, weak_topics)
        return weak_topics

    # --- Fallback: aggregate stats for new users ---
    attempts = db.query(
        models.QuestionAttempt,
        models.Question.topic
    ).join(
        models.Question
    ).filter(
        models.QuestionAttempt.user_id == user_id
    ).all()

    if not attempts:
        all_topics = db.query(models.Question.topic).distinct().limit(5).all()
        topics = [t[0] for t in all_topics]
        _set_cached_topics(user_id, topics)
        return topics

    topic_stats: Dict[str, Dict[str, float]] = defaultdict(lambda: {"correct": 0, "total": 0})
    for attempt, topic in attempts:
        topic_stats[topic]["total"] += 1
        if attempt.is_correct:
            topic_stats[topic]["correct"] += 1

    acc_threshold = threshold / 100.0
    weak_topics = [
        topic for topic, stats in topic_stats.items()
        if stats["total"] > 0 and stats["correct"] / stats["total"] < acc_threshold
    ]

    if not weak_topics:
        sorted_topics = sorted(
            topic_stats.items(),
            key=lambda item: (item[1]["total"], -item[1]["correct"]),
        )
        weak_topics = [topic for topic, _ in sorted_topics[:3]]

    _set_cached_topics(user_id, weak_topics)
    return weak_topics


# Alias used by /weak-areas endpoint in main.py
def get_user_weak_areas(db: Session, user_id: int) -> List[str]:
    """Alias for predict_weak_areas — fixes broken /weak-areas endpoint."""
    return predict_weak_areas(db, user_id)


# ---------------------------------------------------------------------------
# Daily practice set generation
# ---------------------------------------------------------------------------

def generate_daily_practice_set(
    db: Session,
    user_id: int,
    num_questions: int = None
) -> List:
    """Generate personalized daily practice set. Returns list of Question objects."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if num_questions is None:
        num_questions = user.daily_practice_count if user else 10

    cached_ids = _get_cached_practice(user_id, num_questions, ttl_seconds=300)
    if cached_ids:
        questions = db.query(models.Question).filter(
            models.Question.id.in_(cached_ids)
        ).all()
        question_map = {q.id: q for q in questions}
        ordered = [question_map[qid] for qid in cached_ids if qid in question_map]
        if len(ordered) == len(cached_ids):
            return ordered

    weak_topics = predict_weak_areas(db, user_id)
    if not weak_topics:
        weak_topics_raw = db.query(models.Question.topic).distinct().limit(3).all()
        weak_topics = [t[0] for t in weak_topics_raw]

    selected: List = []

    # 70% from weak topics
    weak_count = int(num_questions * 0.7) or num_questions
    weak_qs = db.query(models.Question).filter(
        models.Question.topic.in_(weak_topics)
    ).order_by(func.random()).limit(weak_count).all()
    selected.extend(weak_qs)

    # Fill remaining with random
    remaining = num_questions - len(selected)
    if remaining > 0:
        exclude_ids = [q.id for q in selected]
        rand_qs = db.query(models.Question).filter(
            ~models.Question.id.in_(exclude_ids) if exclude_ids else True
        ).order_by(func.random()).limit(remaining).all()
        selected.extend(rand_qs)

    final = selected[:num_questions]
    _set_cached_practice(user_id, num_questions, [q.id for q in final])
    return final


# ---------------------------------------------------------------------------
# User stats update (synchronous path — also callable from Celery)
# ---------------------------------------------------------------------------

def update_user_stats_after_practice(
    db: Session,
    user_id: int,
    questions_solved: int,
    xp_earned: int
):
    """Update XP, level, streak and activity log after a practice answer."""
    from datetime import date

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return

    user.xp += xp_earned
    user.total_questions_solved += questions_solved
    user.level = (user.xp // 100) + 1

    today = date.today()
    if user.last_activity_date:
        last_date = user.last_activity_date.date()
        days_diff = (today - last_date).days
        if days_diff == 0:
            pass
        elif days_diff == 1:
            user.current_streak += 1
            if user.current_streak > user.longest_streak:
                user.longest_streak = user.current_streak
        else:
            user.current_streak = 1
    else:
        user.current_streak = 1
        user.longest_streak = 1

    user.last_activity_date = datetime.now()

    today_date = datetime.now().date()
    existing_activity = db.query(models.ActivityLog).filter(
        models.ActivityLog.user_id == user_id,
        func.date(models.ActivityLog.activity_date) == today_date
    ).first()

    if existing_activity:
        existing_activity.questions_solved += questions_solved
        existing_activity.xp_earned += xp_earned
    else:
        activity = models.ActivityLog(
            user_id=user_id,
            activity_date=datetime.now(),
            questions_solved=questions_solved,
            xp_earned=xp_earned
        )
        db.add(activity)

    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Badge checker
# ---------------------------------------------------------------------------

def check_and_award_badges(db: Session, user_id: int):
    """Check if user has earned any new badges."""
    import json as _json

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return []

    earned_badge_ids = [ub.badge_id for ub in user.user_badges]
    available_badges = db.query(models.Badge).filter(
        ~models.Badge.id.in_(earned_badge_ids) if earned_badge_ids else True
    ).all()

    newly_earned = []
    for badge in available_badges:
        criteria = badge.criteria
        if isinstance(criteria, str):
            criteria = _json.loads(criteria)

        earned = False
        if "current_streak" in criteria and user.current_streak >= criteria["current_streak"]:
            earned = True
        elif "total_questions_solved" in criteria and user.total_questions_solved >= criteria["total_questions_solved"]:
            earned = True
        elif "xp" in criteria and user.xp >= criteria["xp"]:
            earned = True
        elif "level" in criteria and user.level >= criteria["level"]:
            earned = True

        if earned:
            db.add(models.UserBadge(user_id=user_id, badge_id=badge.id))
            newly_earned.append(badge)

    if newly_earned:
        db.commit()

    return newly_earned
