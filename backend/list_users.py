"""List all users in the database"""
from database import SessionLocal
import models

db = SessionLocal()
users = db.query(models.User).all()

print("\n📋 Existing Users in Database:")
print("="*80)

if users:
    for u in users:
        print(f"\nEmail: {u.email}")
        print(f"Username: {u.username}")
        print(f"Verified: {'✅ Yes' if u.is_verified else '❌ No'}")
        print(f"Level: {u.level}")
        print(f"XP: {u.xp}")
        print(f"Current Streak: {u.current_streak} days")
        print(f"Total Questions Solved: {u.total_questions_solved}")
        print(f"Created: {u.created_at}")
        print("-"*80)
    print(f"\nTotal Users: {len(users)}")
else:
    print("\n❌ No users found in database")

print("\n⚠️  Note: Passwords are hashed and cannot be retrieved.")
print("   You'll need to create a new account or reset password.\n")

db.close()
