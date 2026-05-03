"""
Database seeding script for questions and badges
Run this script to populate the database with initial data
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import json

def seed_badges(db: Session):
    """Create initial badge definitions"""
    badges_data = [
        {
            "name": "First Steps",
            "description": "Solve your first question",
            "icon": "≡ƒÄ»",
            "criteria": json.dumps({"total_questions": 1})
        },
        {
            "name": "Getting Started",
            "description": "Solve 10 questions",
            "icon": "≡ƒîƒ",
            "criteria": json.dumps({"total_questions": 10})
        },
        {
            "name": "Half Century",
            "description": "Solve 50 questions",
            "icon": "≡ƒÆ»",
            "criteria": json.dumps({"total_questions": 50})
        },
        {
            "name": "Centurion",
            "description": "Solve 100 questions",
            "icon": "≡ƒÅå",
            "criteria": json.dumps({"total_questions": 100})
        },
        {
            "name": "On Fire",
            "description": "Maintain a 7-day streak",
            "icon": "≡ƒöÑ",
            "criteria": json.dumps({"current_streak": 7})
        },
        {
            "name": "Consistent Learner",
            "description": "Maintain a 30-day streak",
            "icon": "⭐",
            "criteria": json.dumps({"current_streak": 30})
        },
        {
            "name": "Dedication Champion",
            "description": "Practice consistently for 50 days in a row",
            "icon": "🏆",
            "criteria": json.dumps({"current_streak": 50})
        },
        {
            "name": "Streak Master",
            "description": "Practice consistently for 100 days in a row - Ultimate dedication!",
            "icon": "👑💪",
            "criteria": json.dumps({"current_streak": 100})
        },
        {
            "name": "Level 5",
            "description": "Reach Level 5",
            "icon": "≡ƒÑë",
            "criteria": json.dumps({"level": 5})
        },
        {
            "name": "Level 10",
            "description": "Reach Level 10",
            "icon": "≡ƒÑê",
            "criteria": json.dumps({"level": 10})
        },
        {
            "name": "Level 20",
            "description": "Reach Level 20",
            "icon": "≡ƒÑç",
            "criteria": json.dumps({"level": 20})
        },
        {
            "name": "XP Hunter",
            "description": "Earn 1000 XP",
            "icon": "≡ƒÆÄ",
            "criteria": json.dumps({"xp": 1000})
        },
        {
            "name": "XP Master",
            "description": "Earn 5000 XP",
            "icon": "≡ƒÆá",
            "criteria": json.dumps({"xp": 5000})
        }
    ]
    
    for badge_data in badges_data:
        # Check if badge already exists
        existing = db.query(models.Badge).filter(models.Badge.name == badge_data["name"]).first()
        if not existing:
            badge = models.Badge(**badge_data)
            db.add(badge)
            print(f"Γ£à Created badge: {badge_data['name']}")
        else:
            print(f"ΓÅ¡∩╕Å  Badge already exists: {badge_data['name']}")
    
    db.commit()
    print(f"\nΓ£à Badge seeding complete!")


def seed_questions(db: Session):
    """Create initial question bank with aptitude MCQs"""
    questions_data = [
        # Quantitative Aptitude - Numbers
        {
            "title": "Average of Numbers",
            "description": "The average of 5 consecutive odd numbers is 27. What is the largest number?",
            "difficulty": "Easy",
            "topic": "Averages",
            "option_a": "29",
            "option_b": "31",
            "option_c": "33",
            "option_d": "35",
            "correct_answer": "B",
            "explanation": "If average is 27, middle number is 27. For 5 consecutive odd numbers: 23, 25, 27, 29, 31. Largest is 31.",
            "xp_reward": 10
        },
        
        # Verbal Aptitude - Synonyms (Hard)
        {
            "title": "Synonym: Obfuscate",
            "description": "Choose the word that is closest in meaning to 'obfuscate':",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Clarify",
            "option_b": "Confuse",
            "option_c": "Illuminate",
            "option_d": "Simplify",
            "correct_answer": "B",
            "explanation": "'Obfuscate' means to make something unclear or confusing, often intentionally. The correct synonym is 'confuse'.",
            "xp_reward": 20
        },
        {
            "title": "Synonym: Sagacious",
            "description": "Select the synonym for 'sagacious':",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Foolish",
            "option_b": "Wise",
            "option_c": "Hasty",
            "option_d": "Weak",
            "correct_answer": "B",
            "explanation": "'Sagacious' means having keen judgment or wisdom. It describes someone who is perceptive and wise.",
            "xp_reward": 20
        },
        {
            "title": "Synonym: Inimical",
            "description": "Which of the following is most similar in meaning to 'inimical'?",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Friendly",
            "option_b": "Hostile",
            "option_c": "Favorable",
            "option_d": "Neutral",
            "correct_answer": "B",
            "explanation": "'Inimical' means harmful, unfriendly, or hostile. It describes something that is damaging or antagonistic.",
            "xp_reward": 20
        },
        {
            "title": "Synonym: Pulchritude",
            "description": "Pick the word that best matches the meaning of 'pulchritude':",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Beauty",
            "option_b": "Strength",
            "option_c": "Cruelty",
            "option_d": "Wisdom",
            "correct_answer": "A",
            "explanation": "'Pulchritude' is a formal or literary word meaning physical beauty or attractiveness.",
            "xp_reward": 20
        },
        {
            "title": "Synonym: Perfunctory",
            "description": "Choose the synonym for 'perfunctory':",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Thorough",
            "option_b": "Superficial",
            "option_c": "Enthusiastic",
            "option_d": "Deliberate",
            "correct_answer": "B",
            "explanation": "'Perfunctory' describes something done with minimal effort, care, or interest - merely as a routine duty. It is superficial or cursory.",
            "xp_reward": 20
        },
        {
            "title": "Synonym: Recalcitrant",
            "description": "Identify the word closest in meaning to 'recalcitrant':",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Obedient",
            "option_b": "Stubborn",
            "option_c": "Passive",
            "option_d": "Flexible",
            "correct_answer": "B",
            "explanation": "'Recalcitrant' means resistant to authority, difficult to manage, or stubbornly uncooperative.",
            "xp_reward": 20
        },
        {
            "title": "Synonym: Lachrymose",
            "description": "Select the synonym for 'lachrymose':",
            "difficulty": "Hard",
            "topic": "Synonyms",
            "option_a": "Tearful",
            "option_b": "Joyful",
            "option_c": "Angry",
            "option_d": "Calm",
            "correct_answer": "A",
            "explanation": "'Lachrymose' means given to tears or weeping; tearful or very sad. It can also describe something that induces tears.",
            "xp_reward": 20
        }
    ]
    
    for question_data in questions_data:
        # Check if question already exists
        existing = db.query(models.Question).filter(models.Question.title == question_data["title"]).first()
        if not existing:
            question = models.Question(**question_data)
            db.add(question)
            print(f"Γ£à Created question: {question_data['title']}")
        else:
            print(f"ΓÅ¡∩╕Å  Question already exists: {question_data['title']}")
    
    db.commit()
    print(f"\nΓ£à Question seeding complete! Total: {len(questions_data)} questions")


def main():
    """Main seeding function"""
    print("≡ƒî▒ Starting database seeding...\n")
    
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed badges
        print("≡ƒô¢ Seeding badges...")
        seed_badges(db)
        
        print("\n" + "="*80 + "\n")
        
        # Seed questions
        print("Γ¥ô Seeding questions...")
        seed_questions(db)
        
        print("\n" + "="*80 + "\n")
        print("Indexing seeded questions into ChromaDB...")
        try:
            from vector_service import index_all_questions

            index_all_questions()
        except ImportError as e:
            print(
                "Skipping ChromaDB indexing (chromadb not installed or import failed): "
                f"{e}\nInstall backend requirements, then run: python vector_service.py index"
            )
        
        print("\n" + "="*80)
        print("≡ƒÄë Database seeding completed successfully!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\nΓ¥î Error during seeding: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
