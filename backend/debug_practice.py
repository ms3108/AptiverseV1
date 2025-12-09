"""Script to check and reset daily practice status for testing"""
import os
import sys
from datetime import datetime, date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database import Base
import models

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def check_activity_logs():
    """Check all activity logs"""
    print("\n📊 Activity Logs:")
    logs = db.query(models.ActivityLog).all()
    for log in logs:
        user = db.query(models.User).filter(models.User.id == log.user_id).first()
        print(f"  User: {user.username if user else 'Unknown'}, Date: {log.activity_date}, Solved: {log.questions_solved}, XP: {log.xp_earned}")

def check_today_for_user(username: str):
    """Check if user has activity for today"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        print(f"❌ User '{username}' not found")
        return
    
    today = datetime.utcnow().date()
    print(f"\n🔍 Checking for user: {username} (ID: {user.id})")
    print(f"   Today (UTC): {today}")
    
    today_activity = db.query(models.ActivityLog).filter(
        models.ActivityLog.user_id == user.id,
        func.date(models.ActivityLog.activity_date) == today
    ).first()
    
    if today_activity:
        print(f"   ✅ Found activity for today:")
        print(f"      Date: {today_activity.activity_date}")
        print(f"      Questions Solved: {today_activity.questions_solved}")
        print(f"      XP Earned: {today_activity.xp_earned}")
    else:
        print(f"   ❌ No activity found for today")

def reset_today_activity(username: str):
    """Reset today's activity for a user"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        print(f"❌ User '{username}' not found")
        return
    
    today = datetime.utcnow().date()
    deleted = db.query(models.ActivityLog).filter(
        models.ActivityLog.user_id == user.id,
        func.date(models.ActivityLog.activity_date) == today
    ).delete(synchronize_session=False)
    
    db.commit()
    print(f"✅ Deleted {deleted} activity log(s) for {username} today")

if __name__ == "__main__":
    print("=" * 50)
    print("Daily Practice Debug Tool")
    print("=" * 50)
    
    check_activity_logs()
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
        check_today_for_user(username)
        
        if len(sys.argv) > 2 and sys.argv[2] == "--reset":
            reset_today_activity(username)
    else:
        print("\nUsage: python debug_practice.py <username> [--reset]")

    db.close()
