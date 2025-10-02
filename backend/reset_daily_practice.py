"""
Reset daily practice for specified users by deleting today's question attempts
"""
from database import SessionLocal
from models import User, QuestionAttempt
from datetime import datetime, timezone
import sys

def reset_daily_practice(email: str):
    """Reset today's daily practice for a user"""
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ User with email '{email}' not found")
            return False
        
        # Get today's start (midnight UTC)
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count attempts before deletion
        attempts_count = db.query(QuestionAttempt).filter(
            QuestionAttempt.user_id == user.id,
            QuestionAttempt.created_at >= today_start
        ).count()
        
        if attempts_count == 0:
            print(f"ℹ️  No practice attempts found today for {user.username} ({email})")
            return True
        
        # Delete today's attempts
        db.query(QuestionAttempt).filter(
            QuestionAttempt.user_id == user.id,
            QuestionAttempt.created_at >= today_start
        ).delete()
        
        db.commit()
        print(f"✅ Reset {attempts_count} practice attempts for {user.username} ({email})")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error resetting practice for {email}: {str(e)}")
        return False
    finally:
        db.close()

def main():
    print("🔄 Resetting Daily Practice for Accounts")
    print("=" * 70)
    print()
    
    # Reset for both main accounts
    accounts = [
        "22cs004@mgits.ac.in",  # misna
        "m3108204@gmail.com"     # user2
    ]
    
    success_count = 0
    for email in accounts:
        if reset_daily_practice(email):
            success_count += 1
        print()
    
    print("=" * 70)
    print(f"✅ Successfully reset {success_count}/{len(accounts)} accounts")
    print()
    print("💡 Users can now get fresh daily practice questions!")

if __name__ == "__main__":
    main()
