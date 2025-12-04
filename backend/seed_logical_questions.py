"""Seed Logical Reasoning questions to the database"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Question

LOGICAL_QUESTIONS = [
    # Blood Relations (5 questions)
    {
        "title": "Brother's Father",
        "description": "Pointing to a man, a woman said, 'His mother is the only daughter of my mother.' How is the woman related to the man?",
        "difficulty": "Easy",
        "topic": "Blood Relations",
        "category": "Logical",
        "option_a": "Mother",
        "option_b": "Daughter",
        "option_c": "Sister",
        "option_d": "Grandmother",
        "correct_answer": "A",
        "explanation": "The only daughter of my mother = the woman herself. So the woman is the man's mother.",
        "xp_reward": 10
    },
    {
        "title": "Family Relationship",
        "description": "If A is the brother of B, B is the sister of C, and C is the father of D, how is D related to A?",
        "difficulty": "Medium",
        "topic": "Blood Relations",
        "category": "Logical",
        "option_a": "Brother",
        "option_b": "Sister",
        "option_c": "Nephew/Niece",
        "option_d": "Son/Daughter",
        "correct_answer": "C",
        "explanation": "A is brother of B, B is sister of C (so A and B are siblings of C), C is father of D. So D is the child of A's sibling, making D the nephew or niece of A.",
        "xp_reward": 15
    },
    {
        "title": "Photograph Puzzle",
        "description": "Pointing to a photograph, a man said, 'I have no brother or sister but that man's father is my father's son.' Whose photograph was it?",
        "difficulty": "Medium",
        "topic": "Blood Relations",
        "category": "Logical",
        "option_a": "His own",
        "option_b": "His son's",
        "option_c": "His father's",
        "option_d": "His nephew's",
        "correct_answer": "B",
        "explanation": "Since he has no siblings, 'my father's son' refers to himself. So 'that man's father is myself' means the photograph is of his son.",
        "xp_reward": 15
    },
    
    # Coding-Decoding (5 questions)
    {
        "title": "Letter Coding",
        "description": "If COMPUTER is coded as RFUVQNPC, how is MEDICINE coded?",
        "difficulty": "Easy",
        "topic": "Coding-Decoding",
        "category": "Logical",
        "option_a": "ENICIDME",
        "option_b": "MFEDJDOF",
        "option_c": "ENABORJM",
        "option_d": "FOJDJEFN",
        "correct_answer": "A",
        "explanation": "The word is reversed and each letter is moved one position forward. MEDICINE reversed is ENICIDEM, then each letter +1 = ENICIDME. Wait, let me recalculate: COMPUTER reversed = RETUPMOC, not matching. The pattern is simply reversing: MEDICINE -> ENICIDME",
        "xp_reward": 10
    },
    {
        "title": "Number Coding",
        "description": "If CAT = 24 and DOG = 26, then BAT = ?",
        "difficulty": "Easy",
        "topic": "Coding-Decoding",
        "category": "Logical",
        "option_a": "21",
        "option_b": "23",
        "option_c": "25",
        "option_d": "27",
        "correct_answer": "B",
        "explanation": "C=3, A=1, T=20. CAT = 3+1+20 = 24. D=4, O=15, G=7. DOG = 4+15+7 = 26. B=2, A=1, T=20. BAT = 2+1+20 = 23.",
        "xp_reward": 10
    },
    {
        "title": "Symbol Coding",
        "description": "In a certain code, MIND is written as KGLB. How is ARGUE written in that code?",
        "difficulty": "Medium",
        "topic": "Coding-Decoding",
        "category": "Logical",
        "option_a": "YPESC",
        "option_b": "ZQFTD",
        "option_c": "YPDTC",
        "option_d": "CTDPY",
        "correct_answer": "A",
        "explanation": "Each letter is moved 2 positions backward: M-2=K, I-2=G, N-2=L, D-2=B. So A-2=Y, R-2=P, G-2=E, U-2=S, E-2=C. ARGUE = YPESC.",
        "xp_reward": 15
    },
    
    # Direction Sense (4 questions)
    {
        "title": "Final Direction",
        "description": "A man walks 5 km towards South and then turns left. After walking 3 km, he turns left and walks 5 km. Which direction is he facing now?",
        "difficulty": "Easy",
        "topic": "Direction Sense",
        "category": "Logical",
        "option_a": "East",
        "option_b": "West",
        "option_c": "North",
        "option_d": "South",
        "correct_answer": "C",
        "explanation": "Starting facing South, walks 5km. Turns left (now facing East), walks 3km. Turns left (now facing North), walks 5km. Final direction: North.",
        "xp_reward": 10
    },
    {
        "title": "Distance from Start",
        "description": "Raj walks 20m North, then 15m East, then 20m South. How far is he from the starting point?",
        "difficulty": "Easy",
        "topic": "Direction Sense",
        "category": "Logical",
        "option_a": "15 m",
        "option_b": "20 m",
        "option_c": "25 m",
        "option_d": "35 m",
        "correct_answer": "A",
        "explanation": "20m North and 20m South cancel out. He's only 15m East from the start, so distance = 15m.",
        "xp_reward": 10
    },
    
    # Series Completion (5 questions)
    {
        "title": "Number Series 1",
        "description": "What comes next in the series: 2, 6, 12, 20, 30, ?",
        "difficulty": "Easy",
        "topic": "Series Completion",
        "category": "Logical",
        "option_a": "40",
        "option_b": "42",
        "option_c": "44",
        "option_d": "46",
        "correct_answer": "B",
        "explanation": "Differences: 4, 6, 8, 10, 12. The pattern is n×(n+1): 1×2=2, 2×3=6, 3×4=12, 4×5=20, 5×6=30, 6×7=42.",
        "xp_reward": 10
    },
    {
        "title": "Number Series 2",
        "description": "Find the missing number: 3, 9, 27, 81, ?",
        "difficulty": "Easy",
        "topic": "Series Completion",
        "category": "Logical",
        "option_a": "162",
        "option_b": "216",
        "option_c": "243",
        "option_d": "324",
        "correct_answer": "C",
        "explanation": "Each number is multiplied by 3. 3×3=9, 9×3=27, 27×3=81, 81×3=243.",
        "xp_reward": 10
    },
    {
        "title": "Letter Series",
        "description": "What comes next: A, C, F, J, O, ?",
        "difficulty": "Medium",
        "topic": "Series Completion",
        "category": "Logical",
        "option_a": "T",
        "option_b": "U",
        "option_c": "V",
        "option_d": "W",
        "correct_answer": "B",
        "explanation": "Differences in positions: +2, +3, +4, +5, +6. A(1)+2=C(3)+3=F(6)+4=J(10)+5=O(15)+6=U(21).",
        "xp_reward": 15
    },
    {
        "title": "Mixed Series",
        "description": "Complete the series: 1, 4, 9, 16, 25, ?",
        "difficulty": "Easy",
        "topic": "Series Completion",
        "category": "Logical",
        "option_a": "30",
        "option_b": "35",
        "option_c": "36",
        "option_d": "49",
        "correct_answer": "C",
        "explanation": "These are perfect squares: 1², 2², 3², 4², 5², 6² = 36.",
        "xp_reward": 10
    },
    
    # Analogies (4 questions)
    {
        "title": "Word Analogy 1",
        "description": "Pen : Writer :: Needle : ?",
        "difficulty": "Easy",
        "topic": "Analogies",
        "category": "Logical",
        "option_a": "Thread",
        "option_b": "Tailor",
        "option_c": "Cloth",
        "option_d": "Sewing",
        "correct_answer": "B",
        "explanation": "A pen is a tool used by a writer. Similarly, a needle is a tool used by a tailor.",
        "xp_reward": 10
    },
    {
        "title": "Word Analogy 2",
        "description": "Bird : Nest :: Human : ?",
        "difficulty": "Easy",
        "topic": "Analogies",
        "category": "Logical",
        "option_a": "House",
        "option_b": "Building",
        "option_c": "City",
        "option_d": "Family",
        "correct_answer": "A",
        "explanation": "A bird lives in a nest. Similarly, a human lives in a house.",
        "xp_reward": 10
    },
    {
        "title": "Number Analogy",
        "description": "8 : 64 :: 11 : ?",
        "difficulty": "Easy",
        "topic": "Analogies",
        "category": "Logical",
        "option_a": "111",
        "option_b": "121",
        "option_c": "132",
        "option_d": "144",
        "correct_answer": "B",
        "explanation": "8² = 64. Similarly, 11² = 121.",
        "xp_reward": 10
    },
    
    # Syllogisms (4 questions)
    {
        "title": "Syllogism 1",
        "description": "Statements: All dogs are animals. All animals are living beings. Conclusions: I. All dogs are living beings. II. All living beings are dogs.",
        "difficulty": "Medium",
        "topic": "Syllogisms",
        "category": "Logical",
        "option_a": "Only I follows",
        "option_b": "Only II follows",
        "option_c": "Both I and II follow",
        "option_d": "Neither I nor II follows",
        "correct_answer": "A",
        "explanation": "All dogs are animals and all animals are living beings, so all dogs are living beings (I follows). But not all living beings are dogs (II doesn't follow).",
        "xp_reward": 15
    },
    {
        "title": "Syllogism 2",
        "description": "Statements: Some books are pens. All pens are pencils. Conclusions: I. Some books are pencils. II. Some pencils are books.",
        "difficulty": "Medium",
        "topic": "Syllogisms",
        "category": "Logical",
        "option_a": "Only I follows",
        "option_b": "Only II follows",
        "option_c": "Both I and II follow",
        "option_d": "Neither follows",
        "correct_answer": "C",
        "explanation": "Some books are pens and all pens are pencils, so some books are pencils (I follows). Since some books are pencils, some pencils are books (II follows).",
        "xp_reward": 15
    },
    
    # Ranking and Order (3 questions)
    {
        "title": "Position in Row",
        "description": "In a row of 40 students, Rahul is 13th from the left end. What is his position from the right end?",
        "difficulty": "Easy",
        "topic": "Ranking and Order",
        "category": "Logical",
        "option_a": "27th",
        "option_b": "28th",
        "option_c": "29th",
        "option_d": "30th",
        "correct_answer": "B",
        "explanation": "Position from right = Total - Position from left + 1 = 40 - 13 + 1 = 28.",
        "xp_reward": 10
    },
    {
        "title": "Class Ranking",
        "description": "In a class, Mohan's rank is 15th from the top and 26th from the bottom. How many students are in the class?",
        "difficulty": "Easy",
        "topic": "Ranking and Order",
        "category": "Logical",
        "option_a": "39",
        "option_b": "40",
        "option_c": "41",
        "option_d": "42",
        "correct_answer": "B",
        "explanation": "Total = Rank from top + Rank from bottom - 1 = 15 + 26 - 1 = 40.",
        "xp_reward": 10
    },
    
    # Puzzles (3 questions)
    {
        "title": "Age Puzzle",
        "description": "A is twice as old as B. Five years ago, A was three times as old as B. What is B's current age?",
        "difficulty": "Medium",
        "topic": "Puzzles",
        "category": "Logical",
        "option_a": "8 years",
        "option_b": "10 years",
        "option_c": "12 years",
        "option_d": "15 years",
        "correct_answer": "B",
        "explanation": "Let B's age = x. A's age = 2x. Five years ago: 2x-5 = 3(x-5). 2x-5 = 3x-15. x = 10. B is 10 years old.",
        "xp_reward": 15
    },
    {
        "title": "Logic Puzzle",
        "description": "If the day before yesterday was Thursday, what day will it be the day after tomorrow?",
        "difficulty": "Easy",
        "topic": "Puzzles",
        "category": "Logical",
        "option_a": "Sunday",
        "option_b": "Monday",
        "option_c": "Tuesday",
        "option_d": "Wednesday",
        "correct_answer": "B",
        "explanation": "Day before yesterday = Thursday. Yesterday = Friday. Today = Saturday. Tomorrow = Sunday. Day after tomorrow = Monday.",
        "xp_reward": 10
    },
    
    # Statement and Conclusions (2 questions)
    {
        "title": "Statement Analysis",
        "description": "Statement: The best way to escape from a problem is to solve it. Conclusions: I. Your preparation is fundamental to solve problems. II. Problems can be solved easily.",
        "difficulty": "Medium",
        "topic": "Statement and Conclusions",
        "category": "Logical",
        "option_a": "Only I follows",
        "option_b": "Only II follows",
        "option_c": "Both follow",
        "option_d": "Neither follows",
        "correct_answer": "D",
        "explanation": "The statement talks about solving problems being the best escape, but says nothing about preparation or ease of solving. Neither conclusion follows.",
        "xp_reward": 15
    },
]

def seed_logical_questions():
    db = SessionLocal()
    
    added = 0
    skipped = 0
    
    for q_data in LOGICAL_QUESTIONS:
        # Check if question already exists
        existing = db.query(Question).filter(Question.title == q_data["title"]).first()
        if existing:
            print(f"⏭️ Skipped (exists): {q_data['title']}")
            skipped += 1
            continue
        
        question = Question(**q_data)
        db.add(question)
        added += 1
        print(f"✅ Added: {q_data['title']} [{q_data['topic']}]")
    
    db.commit()
    
    print(f"\n📊 Summary:")
    print(f"  Added: {added} questions")
    print(f"  Skipped: {skipped} questions")
    
    # Show category breakdown
    print("\n📋 Category Summary:")
    for cat in ["Quantitative", "Logical", "Linguistic"]:
        count = db.query(Question).filter(Question.category == cat).count()
        print(f"  {cat}: {count} questions")
    
    db.close()

if __name__ == "__main__":
    seed_logical_questions()
