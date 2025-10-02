"""
ML Service for predicting weak areas and generating personalized practice sets
"""
import numpy as np
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
import models


def get_user_performance_data(db: Session, user_id: int) -> pd.DataFrame:
    """
    Fetch user's question attempt history and convert to DataFrame
    """
    attempts = db.query(
        models.QuestionAttempt,
        models.Question.topic,
        models.Question.difficulty
    ).join(
        models.Question
    ).filter(
        models.QuestionAttempt.user_id == user_id
    ).all()
    
    if not attempts:
        return pd.DataFrame()
    
    data = []
    for attempt, topic, difficulty in attempts:
        data.append({
            'topic': topic,
            'difficulty': difficulty,
            'is_correct': int(attempt.is_correct),
            'time_taken': attempt.time_taken_seconds,
            'attempt_count': attempt.attempt_count
        })
    
    return pd.DataFrame(data)


def calculate_topic_accuracy(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate accuracy percentage for each topic
    """
    if df.empty:
        return {}
    
    topic_stats = df.groupby('topic').agg({
        'is_correct': ['sum', 'count']
    })
    
    accuracy = {}
    for topic in topic_stats.index:
        correct = topic_stats.loc[topic, ('is_correct', 'sum')]
        total = topic_stats.loc[topic, ('is_correct', 'count')]
        accuracy[topic] = (correct / total) * 100 if total > 0 else 0
    
    return accuracy


def predict_weak_areas(db: Session, user_id: int, threshold: float = 60.0) -> List[str]:
    """
    Use Naive Bayes to identify weak topics based on:
    - Accuracy
    - Time taken
    - Attempt count
    
    Returns list of weak topics
    """
    df = get_user_performance_data(db, user_id)
    
    if df.empty:
        # New user - return all topics for balanced practice
        all_topics = db.query(models.Question.topic).distinct().limit(5).all()
        return [topic[0] for topic in all_topics]
    
    # Calculate topic-level features
    topic_features = df.groupby('topic').agg({
        'is_correct': 'mean',  # Accuracy
        'time_taken': 'mean',   # Avg time
        'attempt_count': 'mean' # Avg attempts
    }).reset_index()
    
    # Identify weak areas (accuracy below threshold)
    weak_topics = topic_features[topic_features['is_correct'] < (threshold / 100)]['topic'].tolist()
    
    if not weak_topics:
        # If no weak areas, focus on least practiced topics
        topic_counts = df['topic'].value_counts()
        all_topics = db.query(models.Question.topic).distinct().all()
        all_topic_names = [t[0] for t in all_topics]
        
        # Find topics with least practice
        least_practiced = [t for t in all_topic_names if t not in topic_counts.index]
        if least_practiced:
            return least_practiced[:3]
        
        # Return topics with lowest count
        return topic_counts.tail(3).index.tolist()
    
    return weak_topics


def get_weaviate_client():
    """Get Weaviate client for vector similarity search"""
    import os
    try:
        import weaviate
        weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        client = weaviate.Client(url=weaviate_url)
        return client
    except Exception as e:
        print(f"⚠️ Weaviate connection failed: {e}")
        return None


def get_similar_questions_from_vector_db(
    db: Session,
    question_ids: List[int],
    limit: int = 5
) -> List[int]:
    """
    Use Weaviate to find semantically similar questions to ones user struggled with
    
    Args:
        question_ids: IDs of questions user got wrong or took too long on
        limit: Number of similar questions to return per input question
    
    Returns:
        List of similar question IDs
    """
    client = get_weaviate_client()
    if not client:
        return []
    
    similar_question_ids = set()
    
    try:
        for qid in question_ids[:3]:  # Limit to 3 base questions for performance
            # Get the question from DB
            question = db.query(models.Question).filter(models.Question.id == qid).first()
            if not question or not question.vector_id:
                continue
            
            # Search for similar questions in Weaviate
            result = client.query.get(
                "Question",
                ["question_id", "topic", "difficulty"]
            ).with_near_object({
                "id": question.vector_id,
                "certainty": 0.7  # 70% similarity threshold
            }).with_limit(limit).do()
            
            if result and "data" in result and "Get" in result["data"]:
                questions = result["data"]["Get"].get("Question", [])
                for q in questions:
                    if "question_id" in q and q["question_id"] != qid:
                        similar_question_ids.add(q["question_id"])
    
    except Exception as e:
        print(f"⚠️ Vector similarity search error: {e}")
    
    return list(similar_question_ids)


def generate_daily_practice_set(
    db: Session, 
    user_id: int, 
    num_questions: int = None
):
    """
    Generate personalized daily practice set using:
    1. ML prediction for weak areas
    2. Weaviate Vector DB for semantic similarity
    3. PostgreSQL for question selection
    
    Returns list of Question objects
    """
    from sqlalchemy import func as sql_func
    
    # Get user's preferred practice count
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if num_questions is None:
        num_questions = user.daily_practice_count if user else 10
    
    # Get weak topics using ML
    weak_topics = predict_weak_areas(db, user_id)
    
    if not weak_topics:
        weak_topics = db.query(models.Question.topic).distinct().limit(3).all()
        weak_topics = [t[0] for t in weak_topics]
    
    # Get recent incorrect or slow attempts (for semantic similarity)
    recent_struggles = db.query(models.QuestionAttempt.question_id).filter(
        models.QuestionAttempt.user_id == user_id
    ).filter(
        (models.QuestionAttempt.is_correct == False) |
        (models.QuestionAttempt.time_taken_seconds > 180)  # > 3 minutes
    ).order_by(
        models.QuestionAttempt.created_at.desc()
    ).limit(5).all()
    
    struggle_question_ids = [q[0] for q in recent_struggles]
    
    # Get semantically similar questions using Weaviate
    similar_question_ids = []
    if struggle_question_ids:
        similar_question_ids = get_similar_questions_from_vector_db(
            db, 
            struggle_question_ids, 
            limit=max(3, num_questions // 3)
        )
    
    # Build final question set
    selected_questions = []
    
    # 1. Add similar questions (30% of set)
    if similar_question_ids:
        similar_count = min(len(similar_question_ids), num_questions // 3)
        similar_qs = db.query(models.Question).filter(
            models.Question.id.in_(similar_question_ids[:similar_count])
        ).all()
        selected_questions.extend(similar_qs)
    
    # 2. Fill remaining with weak topic questions (70% of set)
    remaining_count = num_questions - len(selected_questions)
    if remaining_count > 0:
        # Exclude already selected questions
        exclude_ids = [q.id for q in selected_questions]
        
        weak_topic_qs = db.query(models.Question).filter(
            models.Question.topic.in_(weak_topics),
            ~models.Question.id.in_(exclude_ids) if exclude_ids else True
        ).order_by(
            sql_func.random()
        ).limit(remaining_count).all()
        
        selected_questions.extend(weak_topic_qs)
    
    # If still not enough questions, add random ones
    if len(selected_questions) < num_questions:
        exclude_ids = [q.id for q in selected_questions]
        random_qs = db.query(models.Question).filter(
            ~models.Question.id.in_(exclude_ids) if exclude_ids else True
        ).order_by(
            sql_func.random()
        ).limit(num_questions - len(selected_questions)).all()
        selected_questions.extend(random_qs)
    
    # Return Question objects directly (not dicts)
    return selected_questions[:num_questions]


def update_user_stats_after_practice(
    db: Session,
    user_id: int,
    questions_solved: int,
    xp_earned: int
):
    """
    Update user stats after completing practice session
    """
    from datetime import datetime, date
    from sqlalchemy import func as sql_func
    
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
            # Same day - no streak change
            pass
        elif days_diff == 1:
            # Consecutive day - increment streak
            user.current_streak += 1
            if user.current_streak > user.longest_streak:
                user.longest_streak = user.current_streak
        else:
            # Streak broken - reset to 1
            user.current_streak = 1
    else:
        # First activity
        user.current_streak = 1
        user.longest_streak = 1
    
    user.last_activity_date = datetime.now()
    
    # Log activity for today
    today = datetime.now().date()
    
    # Check if activity log for today already exists
    existing_activity = db.query(models.ActivityLog).filter(
        models.ActivityLog.user_id == user_id,
        func.date(models.ActivityLog.activity_date) == today
    ).first()
    
    if existing_activity:
        # Update existing activity log
        existing_activity.questions_solved += questions_solved
        existing_activity.xp_earned += xp_earned
    else:
        # Create new activity log
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
    """
    Check if user has earned any new badges
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return []
    
    # Get all badges user hasn't earned yet
    earned_badge_ids = [ub.badge_id for ub in user.user_badges]
    available_badges = db.query(models.Badge).filter(
        ~models.Badge.id.in_(earned_badge_ids)
    ).all()
    
    newly_earned = []
    
    for badge in available_badges:
        criteria = badge.criteria
        # Ensure criteria is a dict (SQLAlchemy JSON column should return dict)
        if isinstance(criteria, str):
            import json
            criteria = json.loads(criteria)
        
        earned = False
        
        # Check criteria based on field names
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


# Import func for random ordering
from sqlalchemy import func
