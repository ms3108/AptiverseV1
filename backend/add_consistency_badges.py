"""
Add new consistency badges for 50 and 100-day streaks
Run this script to add the new badges to the database
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import json

def add_consistency_badges():
    """Add new consistency badges"""
    db = SessionLocal()
    
    try:
        # New badges to add
        new_badges = [
            {
                "name": "Dedication Champion",
                "description": "Practice consistently for 50 days in a row",
                "icon": "🏆",
                "criteria": json.dumps({"current_streak": 50})
            }
        ]
        
        for badge_data in new_badges:
            # Check if badge already exists
            existing = db.query(models.Badge).filter(models.Badge.name == badge_data["name"]).first()
            if not existing:
                badge = models.Badge(**badge_data)
                db.add(badge)
                print(f"✅ Created badge: {badge_data['name']}")
            else:
                print(f"ℹ️  Badge already exists: {badge_data['name']}")
        
        # Update the 100-day badge description to be more specific
        streak_master = db.query(models.Badge).filter(models.Badge.name == "Streak Master").first()
        if streak_master:
            streak_master.description = "Practice consistently for 100 days in a row - Ultimate dedication!"
            print("✅ Updated 'Streak Master' badge description")
        
        db.commit()
        print(f"\n✅ Consistency badges update complete!")
        
    except Exception as e:
        print(f"❌ Error adding badges: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Adding new consistency badges...")
    add_consistency_badges()