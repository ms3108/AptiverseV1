"""
Dynamic Difficulty Rating System
Adjusts question difficulty based on user performance
"""
from sqlalchemy import func
from database import SessionLocal
import models

def calculate_dynamic_difficulty(question_id):
    """
    Calculate difficulty based on:
    - Success rate (% of users who got it right)
    - Average time taken
    - User levels who attempted it
    """
    db = SessionLocal()
    
    try:
        # Get all attempts for this question
        attempts = db.query(models.UserActivity).filter(
            models.UserActivity.question_id == question_id,
            models.UserActivity.activity_type == 'practice'
        ).all()
        
        if len(attempts) < 10:  # Need minimum data
            return None
        
        # Calculate success rate
        correct_count = sum(1 for a in attempts if a.is_correct)
        success_rate = (correct_count / len(attempts)) * 100
        
        # Determine difficulty based on success rate
        if success_rate >= 70:
            return "Easy"
        elif success_rate >= 40:
            return "Medium"
        else:
            return "Hard"
            
    finally:
        db.close()


def update_all_difficulties():
    """Update difficulty ratings for all questions based on performance"""
    db = SessionLocal()
    
    try:
        questions = db.query(models.Question).all()
        updated = 0
        
        for question in questions:
            new_difficulty = calculate_dynamic_difficulty(question.id)
            
            if new_difficulty and new_difficulty != question.difficulty:
                old = question.difficulty
                question.difficulty = new_difficulty
                
                # Update XP reward accordingly
                xp_map = {"Easy": 10, "Medium": 15, "Hard": 20}
                question.xp_reward = xp_map[new_difficulty]
                
                print(f"Updated: {question.title}")
                print(f"  {old} → {new_difficulty} ({question.xp_reward} XP)")
                updated += 1
        
        db.commit()
        print(f"\n✅ Updated {updated} questions")
        
    finally:
        db.close()


if __name__ == "__main__":
    update_all_difficulties()
