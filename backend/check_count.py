from database import SessionLocal
from models import Question
db = SessionLocal()
print(f'Total questions: {db.query(Question).count()}')
