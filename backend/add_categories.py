from database import SessionLocal
from models import Question

# Category mapping based on topics
category_mapping = {
    'Averages': 'Quants',
    'Profit & Loss': 'Quants',
    'Simple Interest': 'Quants',
    'Compound Interest': 'Quants',
    'Time & Work': 'Quants',
    'Speed & Distance': 'Quants',
    'Ratio & Proportion': 'Quants',
    'Mixtures': 'Quants',
    'Partnership': 'Quants',
    'Number Series': 'Logical',
    'Coding-Decoding': 'Logical',
    'Blood Relations': 'Logical',
    'Direction Sense': 'Logical',
    'Synonyms': 'Language',
    'Antonyms': 'Language',
    'Sentence Completion': 'Language',
    'Data Interpretation': 'Quants',
    'Ages': 'Quants',
    'Probability': 'Quants',
    'Permutations': 'Quants',
    'Combinations': 'Quants',
    'Calendar': 'Logical',
    'Clocks': 'Logical'
}

db = SessionLocal()

try:
    # Get all questions without categories
    questions = db.query(Question).filter(Question.category == None).all()
    
    count = 0
    for question in questions:
        if question.topic in category_mapping:
            question.category = category_mapping[question.topic]
            count += 1
            print(f"✅ Updated: {question.title} → {question.category}")
    
    db.commit()
    print(f"\n🎉 Successfully updated {count} questions with categories!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    db.rollback()
finally:
    db.close()
