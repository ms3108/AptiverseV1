from database import SessionLocal
from models import Question

db = SessionLocal()
total = db.query(Question).count()
print(f"Total questions in database: {total}")
db.close()
