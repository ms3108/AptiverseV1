"""Remove coding/DSA questions - keep only aptitude questions"""
from database import SessionLocal
from models import Question

def remove_coding_questions():
    db = SessionLocal()
    
    # Topics that are coding/DSA related (to remove)
    coding_topics = [
        'Arrays', 'Strings', 'Linked Lists', 'Trees', 'Graphs',
        'Dynamic Programming', 'Sorting and Searching', 'Stacks and Queues',
        'Heaps', 'Bit Manipulation', 'Greedy Algorithms', 'Backtracking',
        'Hashing', 'Two Pointers', 'Sliding Window', 'Matrix', 'Recursion',
        'Stack', 'Queue', 'Heap', 'Sorting', 'Searching', 'Greedy'
    ]
    
    # Delete questions with coding topics
    deleted = 0
    for topic in coding_topics:
        count = db.query(Question).filter(Question.topic == topic).delete()
        if count > 0:
            print(f"Deleted {count} questions from topic: {topic}")
            deleted += count
    
    db.commit()
    
    print(f"\n✅ Total deleted: {deleted} coding questions")
    
    # Show remaining
    remaining = db.query(Question).count()
    print(f"📊 Remaining questions: {remaining}")
    
    cats = db.query(Question.category, Question.topic).distinct().all()
    print("\nRemaining categories and topics:")
    for cat, topic in cats:
        count = db.query(Question).filter(Question.topic == topic).count()
        print(f"  {cat} -> {topic}: {count} questions")
    
    db.close()

if __name__ == "__main__":
    remove_coding_questions()
