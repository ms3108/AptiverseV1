"""
Delete all programming-related questions from the database
Keep only aptitude and verbal questions
"""
from sqlalchemy.orm import Session
from database import SessionLocal
import models

def delete_programming_questions():
    """Delete all programming-related questions"""
    db = SessionLocal()
    
    try:
        # Programming topics to delete
        programming_topics = [
            'Arrays', 'Strings', 'Linked Lists', 'Binary Trees', 'Graphs',
            'Dynamic Programming', 'Sorting', 'Searching', 'Stacks', 'Queues',
            'Heaps', 'Backtracking', 'Bit Manipulation', 'Greedy', 'Hash Tables',
            'Sliding Window', 'Two Pointers', 'Matrix'
        ]
        
        print("🗑️  Starting deletion of programming questions...\n")
        
        # Get all questions with programming topics
        questions = db.query(models.Question).filter(
            models.Question.topic.in_(programming_topics)
        ).all()
        
        print(f"Found {len(questions)} programming questions to delete:\n")
        
        for question in questions:
            print(f"  ❌ Deleting: {question.title} (Topic: {question.topic})")
            db.delete(question)
        
        # Commit the changes
        db.commit()
        
        print(f"\n✅ Successfully deleted {len(questions)} programming questions!")
        
        # Show remaining questions
        remaining = db.query(models.Question).all()
        print(f"\n📊 Remaining questions in database: {len(remaining)}")
        
        # Group by topic
        topics = {}
        for q in remaining:
            topic = q.topic or "Unknown"
            topics[topic] = topics.get(topic, 0) + 1
        
        print("\n📋 Breakdown by topic:")
        for topic, count in sorted(topics.items()):
            print(f"  - {topic}: {count} questions")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("="*80)
    print("DELETE PROGRAMMING QUESTIONS")
    print("="*80 + "\n")
    
    delete_programming_questions()
