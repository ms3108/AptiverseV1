from database import SessionLocal
from models import Question

db = SessionLocal()
qs = db.query(Question).limit(5).all()
for q in qs:
    print(f"Title: {q.title}, Category: {q.category}, Topic: {q.topic}")

# Check unique categories
cats = db.query(Question.category).distinct().all()
print(f"\nUnique categories: {[c[0] for c in cats]}")
