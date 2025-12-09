"""Script to delete questions added on December 9, 2025"""
from database import SessionLocal
from models import Question
from datetime import datetime

db = SessionLocal()

# Find questions created on Dec 9, 2025
start_of_day = datetime(2025, 12, 9, 0, 0, 0)
end_of_day = datetime(2025, 12, 9, 23, 59, 59)

# Count first
count = db.query(Question).filter(
    Question.created_at >= start_of_day,
    Question.created_at <= end_of_day
).count()

print(f"Questions created on Dec 9, 2025: {count}")

if count > 0:
    # Delete them
    deleted = db.query(Question).filter(
        Question.created_at >= start_of_day,
        Question.created_at <= end_of_day
    ).delete()
    db.commit()
    print(f"✅ Deleted {deleted} questions")
else:
    print("No questions to delete")

# Show remaining count
remaining = db.query(Question).count()
print(f"Total questions remaining: {remaining}")

db.close()
