"""
Smart Practice ML Service
- Scikit-Learn Naive Bayes Classifier for Weak Area Detection
- Redis Caching for Performance
- RAG-based Question Selection
"""
import os
import json
import pickle
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

import models

# =============================================================================
# VECTOR DB - Using ChromaDB (free, local)
# =============================================================================

def get_weaviate_client():
    """Backwards compatibility - now uses ChromaDB via vector_service"""
    return None  # ChromaDB doesn't need a client object like Weaviate


def get_vector_service():
    """Get the vector service for semantic search"""
    try:
        import vector_service
        return vector_service
    except ImportError:
        return None

# =============================================================================
# TOPIC CONFIGURATION
# =============================================================================

TOPIC_TO_CATEGORY = {
    # Quantitative Aptitude Topics
    "Averages": "Quantitative",
    "Percentages": "Quantitative",
    "Profit and Loss": "Quantitative",
    "Simple Interest": "Quantitative",
    "Compound Interest": "Quantitative",
    "Ratio and Proportion": "Quantitative",
    "Time and Work": "Quantitative",
    "Time and Distance": "Quantitative",
    "Mixtures and Alligation": "Quantitative",
    "Numbers": "Quantitative",
    "Number System": "Quantitative",
    "Algebra": "Quantitative",
    "Geometry": "Quantitative",
    "Mensuration": "Quantitative",
    "Probability": "Quantitative",
    "Permutation and Combination": "Quantitative",
    "Data Interpretation": "Quantitative",
    "Age Problems": "Quantitative",
    "Partnership": "Quantitative",
    "Pipes and Cisterns": "Quantitative",
    "Boats and Streams": "Quantitative",
    "Trains": "Quantitative",
    "Clocks": "Quantitative",
    "Calendars": "Quantitative",
    
    # Logical Reasoning Topics
    "Blood Relations": "Logical",
    "Coding-Decoding": "Logical",
    "Direction Sense": "Logical",
    "Syllogisms": "Logical",
    "Seating Arrangement": "Logical",
    "Puzzles": "Logical",
    "Pattern Recognition": "Logical",
    "Series Completion": "Logical",
    "Analogies": "Logical",
    "Statement and Conclusions": "Logical",
    "Statement and Assumptions": "Logical",
    "Cause and Effect": "Logical",
    "Critical Reasoning": "Logical",
    "Data Sufficiency": "Logical",
    "Input-Output": "Logical",
    "Ranking and Order": "Logical",
    "Inequalities": "Logical",
    "Logic": "Logical",
    
    # Linguistic/Verbal Topics
    "Synonyms": "Linguistic",
    "Antonyms": "Linguistic",
    "Reading Comprehension": "Linguistic",
    "Sentence Completion": "Linguistic",
    "Grammar": "Linguistic",
    "Vocabulary": "Linguistic",
    "Verbal Reasoning": "Linguistic",
    "Para Jumbles": "Linguistic",
    "Fill in the Blanks": "Linguistic",
    "Error Spotting": "Linguistic",
    "Sentence Improvement": "Linguistic",
    "Cloze Test": "Linguistic",
    "Idioms and Phrases": "Linguistic",
    "One Word Substitution": "Linguistic",
    "Spellings": "Linguistic",
}

ALL_TOPICS = list(TOPIC_TO_CATEGORY.keys())
ALL_CATEGORIES = ["Quantitative", "Logical", "Linguistic"]

# =============================================================================
# REDIS CACHE MANAGER
# =============================================================================

class CacheManager:
    """Redis-based caching with fallback to in-memory cache"""
    
    def __init__(self):
        self._redis_client = None
        self._memory_cache: Dict[str, Tuple[datetime, Any]] = {}
        self._initialized = False
    
    def _get_redis(self):
        """Lazy initialization of Redis client"""
        if self._initialized:
            return self._redis_client
        
        self._initialized = True
        redis_url = os.getenv("REDIS_URL")
        
        if redis_url:
            try:
                import redis
                self._redis_client = redis.from_url(redis_url, decode_responses=False)
                self._redis_client.ping()
                print("✅ Redis cache connected")
            except Exception as e:
                print(f"⚠️ Redis connection failed, using memory cache: {e}")
                self._redis_client = None
        else:
            print("ℹ️ No REDIS_URL configured, using in-memory cache")
        
        return self._redis_client
    
    def get(self, key: str, ttl_seconds: int = 3600) -> Optional[Any]:
        """Get value from cache"""
        redis_client = self._get_redis()
        
        if redis_client:
            try:
                data = redis_client.get(key)
                if data:
                    return pickle.loads(data)
            except Exception as e:
                print(f"⚠️ Redis get error: {e}")
        
        # Fallback to memory cache with TTL check
        if key in self._memory_cache:
            timestamp, value = self._memory_cache[key]
            if datetime.utcnow() - timestamp < timedelta(seconds=ttl_seconds):
                return value
            else:
                del self._memory_cache[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set value in cache with TTL"""
        redis_client = self._get_redis()
        
        if redis_client:
            try:
                redis_client.setex(key, ttl_seconds, pickle.dumps(value))
                return
            except Exception as e:
                print(f"⚠️ Redis set error: {e}")
        
        # Fallback to memory cache
        self._memory_cache[key] = (datetime.utcnow(), value)
        
        # Clean old entries (simple LRU)
        if len(self._memory_cache) > 1000:
            oldest_key = min(self._memory_cache.keys(), 
                           key=lambda k: self._memory_cache[k][0])
            del self._memory_cache[oldest_key]
    
    def delete(self, key: str):
        """Delete key from cache"""
        redis_client = self._get_redis()
        
        if redis_client:
            try:
                redis_client.delete(key)
            except Exception:
                pass
        
        self._memory_cache.pop(key, None)


# Global cache instance
cache = CacheManager()

# =============================================================================
# WEAK AREA CLASSIFIER (Scikit-Learn Naive Bayes)
# =============================================================================

class WeakAreaClassifier:
    """
    ML-based classifier to identify weak topics for a user.
    Uses Naive Bayes classifier with features:
    - Topic Average Accuracy (0-1)
    - Topic Average Time (normalized)
    """
    
    # Thresholds for classifying weak/strong
    ACCURACY_THRESHOLD = 0.6  # Below 60% accuracy = weak
    TIME_THRESHOLD = 1.5  # More than 1.5x average time = weak
    
    def __init__(self):
        self._model = None
        self._sklearn_available = None
    
    def _check_sklearn(self):
        """Check if scikit-learn is available"""
        if self._sklearn_available is None:
            try:
                from sklearn.naive_bayes import GaussianNB
                import numpy as np
                self._sklearn_available = True
            except ImportError:
                print("⚠️ scikit-learn not available, using rule-based classification")
                self._sklearn_available = False
        return self._sklearn_available
    
    def get_user_topic_stats(self, db: Session, user_id: int) -> Dict[str, Dict[str, float]]:
        """
        Fetch user activity and calculate stats per topic.
        Returns: {topic: {accuracy: float, avg_time: float, total_attempts: int, category: str}}
        """
        # Check cache first (10 minute TTL)
        cache_key = f"user_topic_stats:{user_id}"
        cached = cache.get(cache_key, ttl_seconds=600)
        if cached:
            return cached
        
        # Query user attempts with question topics
        attempts = db.query(
            models.QuestionAttempt,
            models.Question.topic,
            models.Question.category
        ).join(
            models.Question, 
            models.QuestionAttempt.question_id == models.Question.id
        ).filter(
            models.QuestionAttempt.user_id == user_id
        ).all()
        
        if not attempts:
            return {}
        
        # Aggregate stats per topic
        topic_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "correct": 0,
            "total": 0,
            "total_time": 0.0,
            "category": None
        })
        
        for attempt, topic, category in attempts:
            stats = topic_stats[topic]
            stats["total"] += 1
            stats["category"] = category
            if attempt.is_correct:
                stats["correct"] += 1
            stats["total_time"] += float(attempt.time_taken_seconds or 0)
        
        # Calculate derived metrics
        result = {}
        for topic, stats in topic_stats.items():
            if stats["total"] > 0:
                result[topic] = {
                    "accuracy": stats["correct"] / stats["total"],
                    "avg_time": stats["total_time"] / stats["total"],
                    "total_attempts": stats["total"],
                    "category": stats["category"]
                }
        
        # Cache for 10 minutes
        cache.set(cache_key, result, ttl_seconds=600)
        
        return result
    
    def classify_topics_ml(self, topic_stats: Dict[str, Dict], global_avg_time: float) -> Tuple[List[str], List[str]]:
        """Use Naive Bayes to classify topics"""
        if not self._check_sklearn():
            return [], []
        
        from sklearn.naive_bayes import GaussianNB
        import numpy as np
        
        # Prepare training data
        X = []  # Features: [accuracy, normalized_time]
        y = []  # Labels: 0=strong, 1=weak
        topics_order = []
        
        for topic, stats in topic_stats.items():
            accuracy = stats["accuracy"]
            normalized_time = stats["avg_time"] / global_avg_time if global_avg_time > 0 else 1.0
            
            X.append([accuracy, normalized_time])
            topics_order.append(topic)
            
            # Generate labels based on thresholds
            is_weak = accuracy < self.ACCURACY_THRESHOLD or normalized_time > self.TIME_THRESHOLD
            y.append(1 if is_weak else 0)
        
        # Need at least 3 samples and both classes
        if len(X) < 3 or len(set(y)) < 2:
            return [], []
        
        try:
            X_array = np.array(X)
            y_array = np.array(y)
            
            model = GaussianNB()
            model.fit(X_array, y_array)
            predictions = model.predict(X_array)
            
            weak_topics = []
            strong_topics = []
            
            for i, topic in enumerate(topics_order):
                if predictions[i] == 1:
                    weak_topics.append(topic)
                else:
                    strong_topics.append(topic)
            
            return weak_topics, strong_topics
            
        except Exception as e:
            print(f"⚠️ ML classification error: {e}")
            return [], []
    
    def classify_topics(self, db: Session, user_id: int) -> Dict[str, List[str]]:
        """
        Classify all user's attempted topics as Weak or Strong.
        
        Returns: {
            "weak": [list of weak topics],
            "strong": [list of strong topics],
            "unattempted": [list of unattempted topics]
        }
        """
        # Check daily cache first
        cache_key = f"weak_areas:{user_id}:{datetime.utcnow().date()}"
        cached = cache.get(cache_key, ttl_seconds=86400)
        if cached:
            return cached
        
        topic_stats = self.get_user_topic_stats(db, user_id)
        
        if not topic_stats:
            # New user - return all topics as unattempted
            result = {
                "weak": [],
                "strong": [],
                "unattempted": ALL_TOPICS.copy()
            }
            cache.set(cache_key, result, ttl_seconds=86400)
            return result
        
        # Calculate global average time for normalization
        all_times = [s["avg_time"] for s in topic_stats.values() if s["avg_time"] > 0]
        global_avg_time = sum(all_times) / len(all_times) if all_times else 60.0
        
        # Try ML classification first
        weak_topics, strong_topics = self.classify_topics_ml(topic_stats, global_avg_time)
        
        # Fallback: Rule-based classification
        if not weak_topics and not strong_topics:
            weak_topics = []
            strong_topics = []
            
            for topic, stats in topic_stats.items():
                accuracy = stats["accuracy"]
                normalized_time = stats["avg_time"] / global_avg_time if global_avg_time > 0 else 1.0
                
                # Weak if: low accuracy OR too slow
                if accuracy < self.ACCURACY_THRESHOLD or normalized_time > self.TIME_THRESHOLD:
                    weak_topics.append(topic)
                else:
                    strong_topics.append(topic)
        
        # Find unattempted topics
        attempted_topics = set(topic_stats.keys())
        unattempted = [t for t in ALL_TOPICS if t not in attempted_topics]
        
        result = {
            "weak": weak_topics,
            "strong": strong_topics,
            "unattempted": unattempted
        }
        
        # Cache for 1 day
        cache.set(cache_key, result, ttl_seconds=86400)
        
        return result
    
    def get_weak_topics_for_practice(self, db: Session, user_id: int) -> List[str]:
        """
        Get prioritized list of topics for practice.
        Priority: Weak topics > Unattempted topics > Strong topics (for review)
        """
        classification = self.classify_topics(db, user_id)
        
        # Prioritize weak topics
        practice_topics = classification["weak"].copy()
        
        # Add some unattempted topics (exploration)
        if classification["unattempted"]:
            import random
            explore_count = min(2, len(classification["unattempted"]))
            explore_topics = random.sample(classification["unattempted"], explore_count)
            practice_topics.extend(explore_topics)
        
        # If still empty, add strong topics for review
        if not practice_topics and classification["strong"]:
            practice_topics = classification["strong"][:3]
        
        return practice_topics


# Global classifier instance
classifier = WeakAreaClassifier()

# =============================================================================
# SMART PRACTICE GENERATOR
# =============================================================================

def get_user_weak_areas(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Get user's weak areas for display.
    Returns: List of weak areas with topic and category info
    """
    classification = classifier.classify_topics(db, user_id)
    topic_stats = classifier.get_user_topic_stats(db, user_id)
    
    weak_areas = []
    for topic in classification["weak"]:
        stats = topic_stats.get(topic, {})
        weak_areas.append({
            "topic": topic,
            "category": TOPIC_TO_CATEGORY.get(topic, "Unknown"),
            "accuracy": round(stats.get("accuracy", 0) * 100, 1),
            "attempts": stats.get("total_attempts", 0)
        })
    
    # Sort by accuracy (worst first)
    weak_areas.sort(key=lambda x: x["accuracy"])
    
    return weak_areas


def generate_smart_practice_set(db: Session, user_id: int, num_questions: int = None) -> Dict[str, Any]:
    """
    Generate smart practice set with ML-based weak area detection.
    
    Returns: {
        "questions": List of Question objects,
        "weak_areas": List of weak areas detected,
        "classifier_used": bool,
        "selection_method": str
    }
    """
    # Get user's preferred practice count
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if num_questions is None:
        num_questions = user.daily_practice_count if user else 10  # type: ignore
    
    # Get classification
    classification = classifier.classify_topics(db, user_id)
    weak_areas = get_user_weak_areas(db, user_id)
    
    # Determine if ML classifier was actually used
    classifier_used = classifier._check_sklearn()
    
    # Generate practice questions
    questions = generate_daily_practice_set(db, user_id, num_questions)
    
    # Determine selection method
    if classification["weak"]:
        selection_method = "weak_area_focus"
    elif classification["unattempted"]:
        selection_method = "exploration"
    else:
        selection_method = "random_review"
    
    return {
        "questions": questions,
        "weak_areas": weak_areas,
        "classifier_used": classifier_used,
        "selection_method": selection_method
    }


def generate_daily_practice_set(db: Session, user_id: int, num_questions: int = None) -> List[models.Question]:
    """
    Generate personalized daily practice set using:
    1. ML-based weak area classification (Naive Bayes)
    2. Smart question selection by difficulty progression
    3. Redis caching for performance
    
    Returns: List of Question objects
    """
    # Get user's preferred practice count
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if num_questions is None:
        num_questions = user.daily_practice_count if user else 10
    
    # Check cache for today's practice set
    cache_key = f"daily_practice:{user_id}:{datetime.utcnow().date()}"
    cached_ids = cache.get(cache_key, ttl_seconds=86400)
    
    if cached_ids:
        questions = db.query(models.Question).filter(
            models.Question.id.in_(cached_ids)
        ).all()
        # Preserve order
        question_map = {q.id: q for q in questions}
        ordered = [question_map[qid] for qid in cached_ids if qid in question_map]
        if len(ordered) >= num_questions:
            return ordered[:num_questions]
    
    # Get weak topics from ML classifier
    weak_topics = classifier.get_weak_topics_for_practice(db, user_id)
    
    # Get questions the user hasn't attempted recently (last 7 days)
    recent_attempts = db.query(models.QuestionAttempt.question_id).filter(
        models.QuestionAttempt.user_id == user_id,
        models.QuestionAttempt.created_at > datetime.utcnow() - timedelta(days=7)
    ).all()
    recently_attempted_ids = [a[0] for a in recent_attempts]
    
    selected_questions = []
    
    # Strategy 1: Questions from weak topics (60% of set)
    weak_topic_count = int(num_questions * 0.6)
    if weak_topics:
        query = db.query(models.Question).filter(
            models.Question.topic.in_(weak_topics)
        )
        if recently_attempted_ids:
            query = query.filter(~models.Question.id.in_(recently_attempted_ids))
        
        # Order by difficulty: Easy -> Medium -> Hard
        weak_topic_qs = query.order_by(
            func.case(
                (models.Question.difficulty == 'Easy', 1),
                (models.Question.difficulty == 'Medium', 2),
                (models.Question.difficulty == 'Hard', 3),
                else_=4
            )
        ).limit(weak_topic_count).all()
        selected_questions.extend(weak_topic_qs)
    
    # Strategy 2: Mix in questions from other topics (40% of set)
    remaining_count = num_questions - len(selected_questions)
    if remaining_count > 0:
        exclude_ids = [q.id for q in selected_questions] + recently_attempted_ids
        
        query = db.query(models.Question)
        if exclude_ids:
            query = query.filter(~models.Question.id.in_(exclude_ids))
        
        other_qs = query.order_by(func.random()).limit(remaining_count).all()
        selected_questions.extend(other_qs)
    
    # If still not enough, include recently attempted ones
    if len(selected_questions) < num_questions:
        exclude_ids = [q.id for q in selected_questions]
        query = db.query(models.Question)
        if exclude_ids:
            query = query.filter(~models.Question.id.in_(exclude_ids))
        
        more_qs = query.order_by(func.random()).limit(num_questions - len(selected_questions)).all()
        selected_questions.extend(more_qs)
    
    # Final selection
    final_questions = selected_questions[:num_questions]
    
    # Cache the question IDs for today
    if final_questions:
        cache.set(cache_key, [q.id for q in final_questions], ttl_seconds=86400)
    
    return final_questions


def get_user_dashboard_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get comprehensive dashboard stats for user including:
    - Weak/Strong topic breakdown
    - Performance by category
    - Recommended focus areas
    """
    cache_key = f"dashboard_stats:{user_id}"
    cached = cache.get(cache_key, ttl_seconds=600)
    if cached:
        return cached
    
    # Get topic classification
    classification = classifier.classify_topics(db, user_id)
    topic_stats = classifier.get_user_topic_stats(db, user_id)
    
    # Group by category
    category_stats = {cat: {"weak": [], "strong": [], "accuracy": 0, "count": 0} 
                     for cat in ALL_CATEGORIES}
    
    for topic in classification["weak"]:
        cat = TOPIC_TO_CATEGORY.get(topic, "Quantitative")
        category_stats[cat]["weak"].append(topic)
        if topic in topic_stats:
            category_stats[cat]["accuracy"] += topic_stats[topic]["accuracy"]
            category_stats[cat]["count"] += 1
    
    for topic in classification["strong"]:
        cat = TOPIC_TO_CATEGORY.get(topic, "Quantitative")
        category_stats[cat]["strong"].append(topic)
        if topic in topic_stats:
            category_stats[cat]["accuracy"] += topic_stats[topic]["accuracy"]
            category_stats[cat]["count"] += 1
    
    # Calculate average accuracy per category
    for cat in category_stats:
        if category_stats[cat]["count"] > 0:
            category_stats[cat]["accuracy"] = round(
                category_stats[cat]["accuracy"] / category_stats[cat]["count"] * 100, 1
            )
    
    result = {
        "weak_topics": classification["weak"],
        "strong_topics": classification["strong"],
        "unattempted_topics": classification["unattempted"],
        "category_breakdown": category_stats,
        "total_topics_attempted": len(topic_stats),
        "recommended_focus": classification["weak"][:3] if classification["weak"] else classification["unattempted"][:3]
    }
    
    # Cache for 10 minutes
    cache.set(cache_key, result, ttl_seconds=600)
    
    return result


def invalidate_user_cache(user_id: int):
    """Invalidate all cached data for a user (call after practice completion)"""
    today = datetime.utcnow().date()
    cache.delete(f"user_topic_stats:{user_id}")
    cache.delete(f"weak_areas:{user_id}:{today}")
    cache.delete(f"daily_practice:{user_id}:{today}")
    cache.delete(f"dashboard_stats:{user_id}")


# =============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# =============================================================================

def predict_weak_areas(db: Session, user_id: int, threshold: float = 60.0) -> List[str]:
    """Legacy function - now uses ML classifier"""
    return classifier.get_weak_topics_for_practice(db, user_id)


def update_user_stats_after_practice(
    db: Session,
    user_id: int,
    questions_solved: int,
    xp_earned: int
):
    """Update user stats after completing practice session"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return
    
    # Update XP
    user.xp = (user.xp or 0) + xp_earned  # type: ignore
    user.total_questions_solved = (user.total_questions_solved or 0) + questions_solved  # type: ignore
    
    # Calculate level (100 XP per level)
    new_level = ((user.xp or 0) // 100) + 1
    user.level = new_level  # type: ignore
    
    # Update streak
    today = datetime.utcnow().date()
    last_activity = user.last_activity_date.date() if user.last_activity_date else None  # type: ignore
    
    if last_activity == today:
        pass  # Same day, no streak change
    elif last_activity == today - timedelta(days=1):
        user.current_streak = (user.current_streak or 0) + 1  # type: ignore
    else:
        user.current_streak = 1  # type: ignore
    
    # Update longest streak
    if (user.current_streak or 0) > (user.longest_streak or 0):  # type: ignore
        user.longest_streak = user.current_streak  # type: ignore
    
    user.last_activity_date = datetime.utcnow()  # type: ignore
    
    # Update activity log
    activity_log = db.query(models.ActivityLog).filter(
        models.ActivityLog.user_id == user_id,
        func.date(models.ActivityLog.activity_date) == today
    ).first()
    
    if activity_log:
        activity_log.questions_solved = (activity_log.questions_solved or 0) + questions_solved  # type: ignore
        activity_log.xp_earned = (activity_log.xp_earned or 0) + xp_earned  # type: ignore
    else:
        activity_log = models.ActivityLog(
            user_id=user_id,
            activity_date=datetime.utcnow(),
            questions_solved=questions_solved,
            xp_earned=xp_earned
        )
        db.add(activity_log)
    
    # Invalidate cache
    invalidate_user_cache(user_id)
    
    db.commit()


def check_and_award_badges(db: Session, user_id: int) -> List[models.Badge]:
    """Check and award any newly earned badges"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return []
    
    # Get all badges user doesn't have yet
    existing_badge_ids = db.query(models.UserBadge.badge_id).filter(
        models.UserBadge.user_id == user_id
    ).all()
    existing_badge_ids = [b[0] for b in existing_badge_ids]
    
    query = db.query(models.Badge)
    if existing_badge_ids:
        query = query.filter(~models.Badge.id.in_(existing_badge_ids))
    available_badges = query.all()
    
    newly_earned = []
    
    for badge in available_badges:
        try:
            criteria = json.loads(badge.criteria) if isinstance(badge.criteria, str) else badge.criteria
        except:
            continue
        
        earned = False
        
        # Check different criteria types
        if "total_questions" in criteria:
            if (user.total_questions_solved or 0) >= criteria["total_questions"]:  # type: ignore
                earned = True
        
        if "current_streak" in criteria:
            if (user.current_streak or 0) >= criteria["current_streak"]:  # type: ignore
                earned = True
        
        if "xp" in criteria:
            if (user.xp or 0) >= criteria["xp"]:  # type: ignore
                earned = True
        
        if "level" in criteria:
            if (user.level or 1) >= criteria["level"]:  # type: ignore
                earned = True
        
        if earned:
            user_badge = models.UserBadge(
                user_id=user_id,
                badge_id=badge.id,
                earned_at=datetime.utcnow()
            )
            db.add(user_badge)
            newly_earned.append(badge)
    
    if newly_earned:
        db.commit()
    
    return newly_earned
