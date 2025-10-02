"""
Standardize topic names - merge "Profit & Loss" into "Profit and Loss"
"""
from database import get_db, engine
import models

models.Base.metadata.create_all(bind=engine)

def standardize_topics():
    db = next(get_db())
    
    print("🔄 Standardizing topic names...\n")
    
    # Topic mappings (old_name -> new_name)
    topic_mappings = {
        "Profit & Loss": "Profit and Loss",
        "Speed & Distance": "Speed and Distance",
        "Ratio & Proportion": "Ratio and Proportion",
        "Time & Work": "Time and Work"
    }
    
    total_updated = 0
    
    for old_topic, new_topic in topic_mappings.items():
        # Count questions with old topic name
        questions = db.query(models.Question).filter(
            models.Question.topic == old_topic
        ).all()
        
        if questions:
            count = len(questions)
            print(f"📝 Updating '{old_topic}' → '{new_topic}'")
            print(f"   Found {count} questions to update")
            
            # Update all questions
            for q in questions:
                q.topic = new_topic
            
            db.commit()
            total_updated += count
            print(f"   ✅ Updated successfully\n")
        else:
            print(f"⏭️  No questions found for '{old_topic}'\n")
    
    print("="*60)
    print(f"✅ Standardization complete!")
    print(f"📊 Total questions updated: {total_updated}")
    print("="*60)
    
    # Show final topic counts
    print("\n📊 Updated Question Count by Topic:")
    print("="*60)
    
    from sqlalchemy import func
    topics = db.query(
        models.Question.topic,
        func.count(models.Question.id)
    ).group_by(models.Question.topic).order_by(models.Question.topic).all()
    
    for topic, count in topics:
        print(f"   {topic}: {count} questions")
    
    print("="*60)
    
    db.close()

if __name__ == "__main__":
    try:
        standardize_topics()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
