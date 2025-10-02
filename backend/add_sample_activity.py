"""
Add sample activity data for testing heatmap visualization
"""
from database import SessionLocal
import models
from datetime import datetime, timedelta
import random

db = SessionLocal()

# Get user ID 2 (misna)
user = db.query(models.User).filter(models.User.id == 2).first()

if not user:
    print("User not found!")
    exit()

print(f"Adding sample activity for user: {user.username}")

# Add activity for random days in the past 12 weeks
today = datetime.now().date()

for i in range(84):  # 12 weeks
    date = today - timedelta(days=i)
    
    # Random chance of activity (70% chance)
    if random.random() < 0.7:
        questions = random.randint(1, 15)
        xp = questions * random.randint(10, 20)
        
        # Check if activity already exists for this date
        existing = db.query(models.ActivityLog).filter(
            models.ActivityLog.user_id == user.id,
            models.ActivityLog.activity_date >= date,
            models.ActivityLog.activity_date < date + timedelta(days=1)
        ).first()
        
        if not existing:
            activity = models.ActivityLog(
                user_id=user.id,
                activity_date=datetime.combine(date, datetime.min.time()),
                questions_solved=questions,
                xp_earned=xp
            )
            db.add(activity)
            print(f"✅ Added activity for {date}: {questions} questions, {xp} XP")
        else:
            print(f"⏭️  Activity already exists for {date}")

db.commit()
print("\n✅ Sample activity data added successfully!")
print("\nRefresh your dashboard to see the heatmap!")

db.close()
