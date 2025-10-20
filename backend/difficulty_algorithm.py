"""
Skill-Weighted Difficulty Algorithm

This module calculates question difficulty based on user skill levels.
Questions solved by beginners are classified as Easy, while questions
only solved by experts are classified as Hard.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime
import models
import math


# Skill tier thresholds
SKILL_TIERS = {
    'beginner': {'xp_max': 1000, 'solved_max': 40, 'level_max': 4},
    'intermediate': {'xp_max': 2500, 'solved_max': 100, 'level_max': 10},
    'advanced': {'xp_max': 3750, 'solved_max': 150, 'level_max': 15},
    'expert': {'xp_max': float('inf'), 'solved_max': float('inf'), 'level_max': float('inf')}
}

# Weight each tier's performance (higher = more important for difficulty)
TIER_WEIGHTS = {
    'beginner': 10,      # Beginner performance is MOST important
    'intermediate': 7,
    'advanced': 4,
    'expert': 2          # Expert performance is LEAST important
}

# Difficulty thresholds (0-100 scale)
DIFFICULTY_THRESHOLDS = {
    'Easy': (0, 35),
    'Medium': (35, 65),
    'Hard': (65, 100)
}

# XP rewards per difficulty
XP_REWARDS = {
    'Easy': 10,
    'Medium': 15,
    'Hard': 20
}


def get_user_skill_tier(user_id: int, db: Session) -> str:
    """
    Categorizes user into skill level based on their stats
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        'beginner' | 'intermediate' | 'advanced' | 'expert'
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        return 'beginner'
    
    return get_user_skill_tier_from_stats(
        total_xp=user.xp,
        solved_count=user.total_questions_solved,
        level=user.level
    )


def get_user_skill_tier_from_stats(total_xp: int, solved_count: int, level: int) -> str:
    """
    Determines skill tier from user statistics
    
    Composite skill score based on:
    - 40% XP (capped at 5000)
    - 40% Questions solved (capped at 200)
    - 20% Level (capped at level 20)
    
    Args:
        total_xp: User's total XP
        solved_count: Total questions solved
        level: User's current level
        
    Returns:
        Skill tier string
    """
    # Calculate composite skill score (0-100)
    skill_score = (
        min(total_xp / 50, 100) * 0.4 +      # XP contribution (cap at 5000)
        min(solved_count / 2, 100) * 0.4 +   # Questions solved (cap at 200)
        min(level * 5, 100) * 0.2            # Level contribution (cap at level 20)
    )
    
    # Classify into tiers
    if skill_score < 20:
        return 'beginner'
    elif skill_score < 50:
        return 'intermediate'
    elif skill_score < 75:
        return 'advanced'
    else:
        return 'expert'


def calculate_skill_weighted_difficulty(question_id: int, db: Session) -> dict:
    """
    Calculates question difficulty based on WHO solves it
    
    Algorithm:
    1. Get all attempts for this question
    2. Categorize each attempt by user's skill tier
    3. Calculate success rate per tier
    4. Apply weighted scoring (beginner success weighted 10x, expert 2x)
    5. Generate difficulty score (0-100) and classify
    
    Args:
        question_id: Question ID
        db: Database session
        
    Returns:
        {
            'difficulty': 'Easy' | 'Medium' | 'Hard',
            'difficulty_score': float (0-100),
            'confidence': float (0-1),
            'breakdown': {
                'total_attempts': int,
                'tier_stats': dict,
                'tier_success_rates': dict,
                'weighted_score': float
            }
        }
    """
    
    # Get all attempts with user stats
    attempts = db.query(models.QuestionAttempt, models.User)\
        .join(models.User, models.QuestionAttempt.user_id == models.User.id)\
        .filter(models.QuestionAttempt.question_id == question_id)\
        .all()
    
    if len(attempts) < 5:  # Need minimum sample size
        return {
            'difficulty': 'Medium',  # Default
            'difficulty_score': 50.0,
            'confidence': 0.0,
            'breakdown': {
                'message': 'Insufficient data (need at least 5 attempts)',
                'total_attempts': len(attempts)
            }
        }
    
    # Initialize tier statistics
    tier_stats = {
        'beginner': {'solved': 0, 'failed': 0, 'total_time': 0, 'count': 0},
        'intermediate': {'solved': 0, 'failed': 0, 'total_time': 0, 'count': 0},
        'advanced': {'solved': 0, 'failed': 0, 'total_time': 0, 'count': 0},
        'expert': {'solved': 0, 'failed': 0, 'total_time': 0, 'count': 0}
    }
    
    # Categorize attempts by tier
    for attempt, user in attempts:
        tier = get_user_skill_tier_from_stats(
            total_xp=user.xp,
            solved_count=user.total_questions_solved,
            level=user.level
        )
        
        tier_stats[tier]['count'] += 1
        tier_stats[tier]['total_time'] += attempt.time_taken_seconds
        
        if attempt.is_correct:
            tier_stats[tier]['solved'] += 1
        else:
            tier_stats[tier]['failed'] += 1
    
    # Calculate success rates and average times per tier
    tier_success_rates = {}
    for tier in tier_stats:
        total = tier_stats[tier]['solved'] + tier_stats[tier]['failed']
        if total > 0:
            tier_success_rates[tier] = tier_stats[tier]['solved'] / total
            tier_stats[tier]['success_rate'] = tier_success_rates[tier]
            tier_stats[tier]['avg_time'] = tier_stats[tier]['total_time'] / tier_stats[tier]['count']
        else:
            tier_success_rates[tier] = None
            tier_stats[tier]['success_rate'] = None
            tier_stats[tier]['avg_time'] = None
    
    # Calculate weighted difficulty score (0-100)
    difficulty_score = 0
    total_weight = 0
    
    for tier, weight in TIER_WEIGHTS.items():
        if tier_success_rates[tier] is not None:
            # Inverse of success rate (high success = low difficulty)
            tier_difficulty = (1 - tier_success_rates[tier]) * 100
            
            difficulty_score += tier_difficulty * weight
            total_weight += weight
    
    # Normalize score
    if total_weight > 0:
        difficulty_score = difficulty_score / total_weight
    else:
        difficulty_score = 50.0  # Default to Medium
    
    # Calculate confidence based on sample size and tier coverage
    total_attempts = len(attempts)
    active_tiers = sum(
        1 for tier in tier_stats 
        if (tier_stats[tier]['solved'] + tier_stats[tier]['failed']) > 0
    )
    
    # Confidence factors
    sample_confidence = min(total_attempts / 50, 1.0)  # Full confidence at 50+ attempts
    coverage_confidence = active_tiers / 4.0  # Full confidence when all 4 tiers have data
    
    # Combined confidence (average of both factors)
    confidence = (sample_confidence + coverage_confidence) / 2.0
    
    # Classify difficulty based on score
    if difficulty_score < DIFFICULTY_THRESHOLDS['Easy'][1]:
        difficulty = 'Easy'
    elif difficulty_score < DIFFICULTY_THRESHOLDS['Hard'][0]:
        difficulty = 'Medium'
    else:
        difficulty = 'Hard'
    
    return {
        'difficulty': difficulty,
        'difficulty_score': round(difficulty_score, 2),
        'confidence': round(confidence, 2),
        'breakdown': {
            'total_attempts': total_attempts,
            'active_tiers': active_tiers,
            'tier_stats': tier_stats,
            'tier_success_rates': tier_success_rates,
            'weighted_score': round(difficulty_score, 2)
        }
    }


def update_question_difficulty(question_id: int, db: Session, force: bool = False) -> dict:
    """
    Updates a question's difficulty based on latest attempt data
    
    Args:
        question_id: Question ID
        db: Database session
        force: Force update even if confidence is low
        
    Returns:
        Result dictionary with update status
    """
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    
    if not question:
        return {'success': False, 'error': 'Question not found'}
    
    # Calculate new difficulty
    result = calculate_skill_weighted_difficulty(question_id, db)
    
    # Only update if confidence threshold met (unless forced)
    MIN_CONFIDENCE = 0.3
    if not force and result['confidence'] < MIN_CONFIDENCE:
        return {
            'success': False,
            'reason': f'Confidence too low ({result["confidence"]:.2f} < {MIN_CONFIDENCE})',
            'result': result
        }
    
    # Track old values for history
    old_difficulty = question.difficulty
    old_score = question.difficulty_score
    
    # Update question fields
    question.difficulty = result['difficulty']
    question.difficulty_score = result['difficulty_score']
    question.difficulty_confidence = result['confidence']
    question.last_difficulty_update = datetime.utcnow()
    question.xp_reward = XP_REWARDS[result['difficulty']]
    
    # Update tier stats (store in database for quick access)
    question.tier_stats = result['breakdown']['tier_stats']
    
    # Track history
    if not question.difficulty_history:
        question.difficulty_history = []
    
    question.difficulty_history.append({
        'timestamp': datetime.utcnow().isoformat(),
        'difficulty': result['difficulty'],
        'score': result['difficulty_score'],
        'confidence': result['confidence'],
        'total_attempts': result['breakdown']['total_attempts']
    })
    
    # Keep only last 50 history entries
    if len(question.difficulty_history) > 50:
        question.difficulty_history = question.difficulty_history[-50:]
    
    db.commit()
    
    # Check if difficulty changed
    difficulty_changed = old_difficulty != result['difficulty']
    
    return {
        'success': True,
        'difficulty_changed': difficulty_changed,
        'old_difficulty': old_difficulty,
        'new_difficulty': result['difficulty'],
        'old_score': old_score,
        'new_score': result['difficulty_score'],
        'confidence': result['confidence'],
        'breakdown': result['breakdown']
    }


def recalculate_all_difficulties(db: Session, min_confidence: float = 0.3) -> dict:
    """
    Background job to recalculate all question difficulties
    
    Args:
        db: Database session
        min_confidence: Minimum confidence to apply updates
        
    Returns:
        Summary statistics
    """
    questions = db.query(models.Question).all()
    
    stats = {
        'total_questions': len(questions),
        'updated': 0,
        'skipped_low_confidence': 0,
        'skipped_no_data': 0,
        'reclassified': 0,
        'changes': []
    }
    
    for question in questions:
        result = update_question_difficulty(question.id, db, force=False)
        
        if result['success']:
            stats['updated'] += 1
            
            if result['difficulty_changed']:
                stats['reclassified'] += 1
                stats['changes'].append({
                    'question_id': question.id,
                    'title': question.title,
                    'old': result['old_difficulty'],
                    'new': result['new_difficulty'],
                    'confidence': result['confidence']
                })
        else:
            if 'Confidence too low' in result.get('reason', ''):
                stats['skipped_low_confidence'] += 1
            else:
                stats['skipped_no_data'] += 1
    
    return stats


def get_personalized_difficulty(question_id: int, user_id: int, db: Session) -> str:
    """
    Returns question difficulty relative to user's skill level
    
    A Hard question for a beginner might be Medium for an expert.
    
    Args:
        question_id: Question ID
        user_id: User ID
        db: Database session
        
    Returns:
        Personalized difficulty: 'Easy' | 'Medium' | 'Hard'
    """
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    user_tier = get_user_skill_tier(user_id, db)
    
    if not question or not question.tier_stats:
        return question.difficulty if question else 'Medium'
    
    # Get user's tier success rate for this question type
    tier_data = question.tier_stats.get(user_tier, {})
    user_tier_success_rate = tier_data.get('success_rate', 0.5)
    
    # Personalized difficulty based on expected success rate
    if user_tier_success_rate > 0.7:
        return 'Easy'  # User's tier has >70% success
    elif user_tier_success_rate > 0.4:
        return 'Medium'  # User's tier has 40-70% success
    else:
        return 'Hard'  # User's tier has <40% success
