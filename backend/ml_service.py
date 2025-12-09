"""
Simple ML Service for Daily Practice Sets
Uses lightweight aggregates instead of heavy ML dependencies.
"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

import models

# Simple in-process caches
_weak_topic_cache: Dict[int, Tuple[datetime, List[str]]] = {}
_practice_set_cache: Dict[Tuple[int, int], Tuple[datetime, List[int]]] = {}


def _get_cached_topics(user_id: int, ttl_seconds: int) -> Optional[List[str]]:
    cached = _weak_topic_cache.get(user_id)
    if not cached:
        return None
    timestamp, topics = cached
    if datetime.utcnow() - timestamp > timedelta(seconds=ttl_seconds):
        _weak_topic_cache.pop(user_id, None)
        return None
    return topics


def _set_cached_topics(user_id: int, topics: List[str]) -> None:
    _weak_topic_cache[user_id] = (datetime.utcnow(), topics)


def _get_cached_practice(user_id: int, num_questions: int, ttl_seconds: int) -> Optional[List[int]]:
    cached = _practice_set_cache.get((user_id, num_questions))
    if not cached:
        return None
    timestamp, question_ids = cached
    if datetime.utcnow() - timestamp > timedelta(seconds=ttl_seconds):
        _practice_set_cache.pop((user_id, num_questions), None)
        return None
    return question_ids


def _set_cached_practice(user_id: int, num_questions: int, question_ids: List[int]) -> None:
    _practice_set_cache[(user_id, num_questions)] = (datetime.utcnow(), question_ids)


def predict_weak_areas(db: Session, user_id: int, threshold: float = 60.0) -> List[str]:
    """Identify weak topics using lightweight aggregates."""
    cached_topics = _get_cached_topics(user_id, ttl_seconds=600)
    if cached_topics is not None:
        return cached_topics

    attempts = db.query(
        models.QuestionAttempt,
        models.Question.topic
    ).join(
        models.Question
    ).filter(
        models.QuestionAttempt.user_id == user_id
    ).all()

    if not attempts:
        # New user - return a balanced sampling of topics
        all_topics = db.query(models.Question.topic).distinct().limit(5).all()
        topics = [topic[0] for topic in all_topics]
        _set_cached_topics(user_id, topics)
        return topics

    topic_stats: Dict[str, Dict[str, float]] = defaultdict(lambda: {
        "correct": 0,
        "total": 0,
    })

    for attempt, topic in attempts:
        stats = topic_stats[topic]
        stats["total"] += 1
        if attempt.is_correct:
            stats["correct"] += 1

    weak_topics: List[str] = []
    accuracy_threshold = threshold / 100.0

    for topic, stats in topic_stats.items():
        if stats["total"] == 0:
            continue
        accuracy = stats["correct"] / stats["total"]
        if accuracy < accuracy_threshold:
            weak_topics.append(topic)

    if not weak_topics:
        # Use least practiced topics
        sorted_topics = sorted(
            topic_stats.items(),
            key=lambda item: (item[1]["total"], -item[1]["correct"]),
        )
        weak_topics = [topic for topic, _ in sorted_topics[:3]]

    _set_cached_topics(user_id, weak_topics)
    return weak_topics


def generate_daily_practice_set(
    db: Session, 
    user_id: int, 
    num_questions: int = None
) -> List:
    """
    Generate personalized daily practice set.
    Returns list of Question objects.
    """
    # Get user's preferred practice count
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if num_questions is None:
        num_questions = user.daily_practice_count if user else 10

    # Check cache
    cached_question_ids = _get_cached_practice(user_id, num_questions, ttl_seconds=300)
    if cached_question_ids:
        questions = db.query(models.Question).filter(
            models.Question.id.in_(cached_question_ids)
        ).all()
        question_map = {q.id: q for q in questions}
        ordered_questions = [question_map[qid] for qid in cached_question_ids if qid in question_map]
        if len(ordered_questions) == len(cached_question_ids):
            return ordered_questions
    
    # Get weak topics
    weak_topics = predict_weak_areas(db, user_id)
    
    if not weak_topics:
        weak_topics = db.query(models.Question.topic).distinct().limit(3).all()
        weak_topics = [t[0] for t in weak_topics]
    
    # Build question set
    selected_questions = []
    
    # Get weak topic questions (70% of set)
    weak_count = int(num_questions * 0.7) or num_questions
    weak_topic_qs = db.query(models.Question).filter(
        models.Question.topic.in_(weak_topics)
    ).order_by(
        func.random()
    ).limit(weak_count).all()
    selected_questions.extend(weak_topic_qs)
    
    # Fill remaining with random questions
    remaining_count = num_questions - len(selected_questions)
    if remaining_count > 0:
        exclude_ids = [q.id for q in selected_questions]
        if exclude_ids:
            random_qs = db.query(models.Question).filter(
                ~models.Question.id.in_(exclude_ids)
            ).order_by(
                func.random()
            ).limit(remaining_count).all()
        else:
            random_qs = db.query(models.Question).order_by(
                func.random()
            ).limit(remaining_count).all()
        selected_questions.extend(random_qs)
    
    # Cache and return
    final_questions = selected_questions[:num_questions]
    _set_cached_practice(user_id, num_questions, [q.id for q in final_questions])
    return final_questions


def update_user_stats_after_practice(
    db: Session,
    user_id: int,
    questions_solved: int,
    xp_earned: int
):
    """Update user stats after completing practice session."""
    from datetime import date
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return
    
    # Update XP and total questions
    user.xp += xp_earned
    user.total_questions_solved += questions_solved
    
    # Calculate level (100 XP per level)
    user.level = (user.xp // 100) + 1
    
    # Update streak
    today = date.today()
    if user.last_activity_date:
        last_date = user.last_activity_date.date()
        days_diff = (today - last_date).days
        
        if days_diff == 0:
            pass  # Same day
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
    
    # Log activity for today
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


def check_and_award_badges(db: Session, user_id: int):
    """Check if user has earned any new badges."""
    import json
    
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
            criteria = json.loads(criteria)
        
        earned = False
        
        if 'current_streak' in criteria:
            if user.current_streak >= criteria['current_streak']:
                earned = True
        elif 'total_questions_solved' in criteria:
            if user.total_questions_solved >= criteria['total_questions_solved']:
                earned = True
        elif 'xp' in criteria:
            if user.xp >= criteria['xp']:
                earned = True
        elif 'level' in criteria:
            if user.level >= criteria['level']:
                earned = True
        
        if earned:
            user_badge = models.UserBadge(
                user_id=user_id,
                badge_id=badge.id
            )
            db.add(user_badge)
            newly_earned.append(badge)
    
    if newly_earned:
        db.commit()
    
    return newly_earned
