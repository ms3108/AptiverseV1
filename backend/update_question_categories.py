"""
Update existing questions with category information
"""
from database import SessionLocal
import models

db = SessionLocal()

# Category mapping
category_mapping = {
    # Quantitative Aptitude
    "Averages": "Quants",
    "Percentages": "Quants",
    "Simple Interest": "Quants",
    "Compound Interest": "Quants",
    "Profit & Loss": "Quants",
    "Time & Work": "Quants",
    "Speed & Distance": "Quants",
    "Ratio & Proportion": "Quants",
    "Mixtures": "Quants",
    "Partnership": "Quants",
    "Ages": "Quants",
    "Probability": "Quants",
    "Permutations": "Quants",
    "Combinations": "Quants",
    "Calendar": "Quants",
    "Clocks": "Quants",
    "Data Interpretation": "Quants",
    
    # Logical Reasoning
    "Number Series": "Logical",
    "Coding-Decoding": "Logical",
    "Blood Relations": "Logical",
    "Direction Sense": "Logical",
    
    # Verbal/Language
    "Synonyms": "Language",
    "Antonyms": "Language",
    "Sentence Completion": "Language",
}

questions = db.query(models.Question).all()

for question in questions:
    if question.topic in category_mapping:
        question.category = category_mapping[question.topic]
        print(f"✅ Updated {question.title[:50]}... -> Category: {question.category}, Topic: {question.topic}")

db.commit()
print(f"\n✅ Updated {len(questions)} questions with category information!")

db.close()
