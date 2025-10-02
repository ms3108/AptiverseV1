"""
Database seeding script for APTITUDE questions and badges
Run this script to populate the database with aptitude MCQs
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import json

def seed_badges(db: Session):
    """Create initial badge definitions"""
    badges_data = [
        {
            "name": "First Steps",
            "description": "Solve your first question",
            "icon": "🎯",
            "criteria": json.dumps({"total_questions": 1})
        },
        {
            "name": "Getting Started",
            "description": "Solve 10 questions",
            "icon": "🌟",
            "criteria": json.dumps({"total_questions": 10})
        },
        {
            "name": "Half Century",
            "description": "Solve 50 questions",
            "icon": "💯",
            "criteria": json.dumps({"total_questions": 50})
        },
        {
            "name": "Centurion",
            "description": "Solve 100 questions",
            "icon": "🏆",
            "criteria": json.dumps({"total_questions": 100})
        },
        {
            "name": "On Fire",
            "description": "Maintain a 7-day streak",
            "icon": "🔥",
            "criteria": json.dumps({"current_streak": 7})
        },
        {
            "name": "Consistent Learner",
            "description": "Maintain a 30-day streak",
            "icon": "⚡",
            "criteria": json.dumps({"current_streak": 30})
        },
        {
            "name": "Streak Master",
            "description": "Maintain a 100-day streak",
            "icon": "🎖️",
            "criteria": json.dumps({"current_streak": 100})
        },
        {
            "name": "Level 5",
            "description": "Reach Level 5",
            "icon": "🥉",
            "criteria": json.dumps({"level": 5})
        },
        {
            "name": "Level 10",
            "description": "Reach Level 10",
            "icon": "🥈",
            "criteria": json.dumps({"level": 10})
        },
        {
            "name": "Level 20",
            "description": "Reach Level 20",
            "icon": "🥇",
            "criteria": json.dumps({"level": 20})
        },
        {
            "name": "XP Hunter",
            "description": "Earn 1000 XP",
            "icon": "💎",
            "criteria": json.dumps({"xp": 1000})
        },
        {
            "name": "XP Master",
            "description": "Earn 5000 XP",
            "icon": "💠",
            "criteria": json.dumps({"xp": 5000})
        }
    ]
    
    for badge_data in badges_data:
        # Check if badge already exists
        existing = db.query(models.Badge).filter(models.Badge.name == badge_data["name"]).first()
        if not existing:
            badge = models.Badge(**badge_data)
            db.add(badge)
            print(f"✅ Created badge: {badge_data['name']}")
        else:
            print(f"⏭️  Badge already exists: {badge_data['name']}")
    
    db.commit()
    print(f"\n✅ Badge seeding complete!")


def seed_aptitude_questions(db: Session):
    """Create aptitude question bank"""
    questions_data = [
        # Quantitative Aptitude - Percentages & Averages
        {
            "title": "Average of Consecutive Odd Numbers",
            "description": "The average of 5 consecutive odd numbers is 27. What is the largest number?",
            "difficulty": "Easy",
            "topic": "Averages",
            "option_a": "29",
            "option_b": "31",
            "option_c": "33",
            "option_d": "35",
            "correct_answer": "B",
            "explanation": "If average is 27, middle number is 27. For 5 consecutive odd numbers: 23, 25, 27, 29, 31. Largest is 31.",
            "xp_reward": 10
        },
        {
            "title": "Profit Calculation with Discount",
            "description": "A shopkeeper marks his goods 40% above cost price but allows a discount of 20%. What is his profit percentage?",
            "difficulty": "Medium",
            "topic": "Profit & Loss",
            "option_a": "10%",
            "option_b": "12%",
            "option_c": "15%",
            "option_d": "20%",
            "correct_answer": "B",
            "explanation": "Let CP = 100. Marked Price = 140. After 20% discount: 140 × 0.8 = 112. Profit = 12%.",
            "xp_reward": 15
        },
        {
            "title": "Simple Interest Problem",
            "description": "What is the simple interest on Rs. 4000 at 8% per annum for 3 years?",
            "difficulty": "Easy",
            "topic": "Simple Interest",
            "option_a": "Rs. 800",
            "option_b": "Rs. 960",
            "option_c": "Rs. 1000",
            "option_d": "Rs. 1200",
            "correct_answer": "B",
            "explanation": "Simple Interest = (P × R × T) / 100 = (4000 × 8 × 3) / 100 = Rs. 960",
            "xp_reward": 10
        },
        {
            "title": "Compound vs Simple Interest",
            "description": "The difference between compound interest and simple interest on a sum at 10% per annum for 2 years is Rs. 50. What is the sum?",
            "difficulty": "Medium",
            "topic": "Compound Interest",
            "option_a": "Rs. 4000",
            "option_b": "Rs. 5000",
            "option_c": "Rs. 6000",
            "option_d": "Rs. 8000",
            "correct_answer": "B",
            "explanation": "Difference = P(R/100)² = 50. So P(10/100)² = 50, therefore P × 0.01 = 50, P = Rs. 5000",
            "xp_reward": 15
        },
        {
            "title": "Profit Percentage Problem",
            "description": "If selling price is doubled, the profit triples. What is the profit percentage?",
            "difficulty": "Hard",
            "topic": "Profit & Loss",
            "option_a": "66.67%",
            "option_b": "100%",
            "option_c": "150%",
            "option_d": "200%",
            "correct_answer": "B",
            "explanation": "Let CP=100, SP1=x, Profit1=x-100. SP2=2x, Profit2=3(x-100). Solving: 2x-100=3(x-100), x=200. Profit%=(200-100)/100=100%",
            "xp_reward": 20
        },
        
        # Time and Work
        {
            "title": "Combined Work Rate",
            "description": "A can complete a work in 12 days and B in 18 days. If they work together, in how many days will the work be completed?",
            "difficulty": "Easy",
            "topic": "Time & Work",
            "option_a": "6 days",
            "option_b": "7.2 days",
            "option_c": "8 days",
            "option_d": "9 days",
            "correct_answer": "B",
            "explanation": "A's 1 day work = 1/12, B's 1 day work = 1/18. Together = 1/12 + 1/18 = 5/36. Days = 36/5 = 7.2 days",
            "xp_reward": 10
        },
        {
            "title": "Pipes and Cisterns",
            "description": "A pipe can fill a tank in 6 hours. Another pipe can empty it in 12 hours. If both are opened, in how many hours will the tank be filled?",
            "difficulty": "Medium",
            "topic": "Time & Work",
            "option_a": "8 hours",
            "option_b": "10 hours",
            "option_c": "12 hours",
            "option_d": "18 hours",
            "correct_answer": "C",
            "explanation": "Net work per hour = 1/6 - 1/12 = 2/12 - 1/12 = 1/12. Time to fill = 12 hours",
            "xp_reward": 15
        },
        {
            "title": "Work Efficiency",
            "description": "If 6 men can do a work in 10 days, how many men are required to do the same work in 5 days?",
            "difficulty": "Easy",
            "topic": "Time & Work",
            "option_a": "8",
            "option_b": "10",
            "option_c": "12",
            "option_d": "15",
            "correct_answer": "C",
            "explanation": "Using M1×D1 = M2×D2: 6×10 = M2×5, M2 = 60/5 = 12 men",
            "xp_reward": 10
        },
        
        # Speed, Time & Distance
        {
            "title": "Average Speed Calculation",
            "description": "A car travels 300 km in 5 hours. What is its average speed in km/h?",
            "difficulty": "Easy",
            "topic": "Speed & Distance",
            "option_a": "50 km/h",
            "option_b": "60 km/h",
            "option_c": "70 km/h",
            "option_d": "80 km/h",
            "correct_answer": "B",
            "explanation": "Speed = Distance / Time = 300 / 5 = 60 km/h",
            "xp_reward": 10
        },
        {
            "title": "Trains Crossing Problem",
            "description": "Two trains 120m and 180m long are running in opposite directions at 40 km/h and 50 km/h. In how many seconds will they cross each other?",
            "difficulty": "Medium",
            "topic": "Speed & Distance",
            "option_a": "10 seconds",
            "option_b": "12 seconds",
            "option_c": "15 seconds",
            "option_d": "18 seconds",
            "correct_answer": "B",
            "explanation": "Relative speed = 40+50 = 90 km/h = 25 m/s. Total distance = 120+180 = 300m. Time = 300/25 = 12 seconds",
            "xp_reward": 15
        },
        {
            "title": "Harmonic Mean Speed",
            "description": "A person covers half distance at 40 km/h and remaining half at 60 km/h. What is the average speed?",
            "difficulty": "Medium",
            "topic": "Speed & Distance",
            "option_a": "48 km/h",
            "option_b": "50 km/h",
            "option_c": "52 km/h",
            "option_d": "55 km/h",
            "correct_answer": "A",
            "explanation": "For equal distances: Average speed = 2xy/(x+y) = 2(40)(60)/(40+60) = 4800/100 = 48 km/h",
            "xp_reward": 15
        },
        
        # Ratio and Proportion
        {
            "title": "Compounded Ratio",
            "description": "If A:B = 2:3 and B:C = 4:5, then A:B:C = ?",
            "difficulty": "Easy",
            "topic": "Ratio & Proportion",
            "option_a": "2:3:5",
            "option_b": "8:12:15",
            "option_c": "6:9:15",
            "option_d": "4:6:10",
            "correct_answer": "B",
            "explanation": "To make B equal, multiply first ratio by 4 and second by 3: A:B = 8:12 and B:C = 12:15. So A:B:C = 8:12:15",
            "xp_reward": 10
        },
        {
            "title": "Mixture and Alligation",
            "description": "In what ratio must water be mixed with milk costing Rs. 12 per litre to get a mixture worth Rs. 8 per litre?",
            "difficulty": "Medium",
            "topic": "Mixtures",
            "option_a": "1:2",
            "option_b": "1:3",
            "option_c": "2:1",
            "option_d": "3:1",
            "correct_answer": "C",
            "explanation": "Using alligation: Milk(12) - Mean(8) = 4, Mean(8) - Water(0) = 8. Ratio Milk:Water = 8:4 = 2:1",
            "xp_reward": 15
        },
        {
            "title": "Partnership Problem",
            "description": "A, B and C invest Rs. 3000, Rs. 4000 and Rs. 5000 respectively. If the profit is Rs. 2400, what is B's share?",
            "difficulty": "Medium",
            "topic": "Partnership",
            "option_a": "Rs. 600",
            "option_b": "Rs. 800",
            "option_c": "Rs. 1000",
            "option_d": "Rs. 1200",
            "correct_answer": "B",
            "explanation": "Ratio = 3:4:5. Total parts = 12. B's share = (4/12) × 2400 = Rs. 800",
            "xp_reward": 15
        },
        
        # Logical Reasoning - Number Series
        {
            "title": "Arithmetic Series",
            "description": "Find the next number in the series: 2, 6, 12, 20, 30, ?",
            "difficulty": "Easy",
            "topic": "Number Series",
            "option_a": "40",
            "option_b": "42",
            "option_c": "44",
            "option_d": "46",
            "correct_answer": "B",
            "explanation": "Differences: 4, 6, 8, 10, 12 (arithmetic sequence). Next number = 30 + 12 = 42",
            "xp_reward": 10
        },
        {
            "title": "Geometric Progression",
            "description": "Find the missing number: 3, 9, 27, ?, 243",
            "difficulty": "Easy",
            "topic": "Number Series",
            "option_a": "54",
            "option_b": "72",
            "option_c": "81",
            "option_d": "108",
            "correct_answer": "C",
            "explanation": "Each number is multiplied by 3: 3, 9, 27, 81, 243 (powers of 3)",
            "xp_reward": 10
        },
        {
            "title": "Perfect Squares Series",
            "description": "Find the next term: 1, 4, 9, 16, 25, ?",
            "difficulty": "Easy",
            "topic": "Number Series",
            "option_a": "30",
            "option_b": "32",
            "option_c": "36",
            "option_d": "40",
            "correct_answer": "C",
            "explanation": "Pattern: 1², 2², 3², 4², 5², 6² = 36",
            "xp_reward": 10
        },
        {
            "title": "Prime Number Series",
            "description": "Find the next prime number: 2, 3, 5, 7, 11, 13, ?",
            "difficulty": "Easy",
            "topic": "Number Series",
            "option_a": "15",
            "option_b": "16",
            "option_c": "17",
            "option_d": "19",
            "correct_answer": "C",
            "explanation": "Sequence of prime numbers. After 13, next prime is 17.",
            "xp_reward": 10
        },
        
        # Logical Reasoning - Coding-Decoding
        {
            "title": "Reverse Coding",
            "description": "If CLOCK is coded as KCOLC, how is BOARD coded?",
            "difficulty": "Easy",
            "topic": "Coding-Decoding",
            "option_a": "DRAOB",
            "option_b": "BOADR",
            "option_c": "DBROA",
            "option_d": "ARBOD",
            "correct_answer": "A",
            "explanation": "Pattern: Reverse the word. BOARD reversed = DRAOB",
            "xp_reward": 10
        },
        {
            "title": "Letter Position Coding",
            "description": "If A=1, B=2, C=3... then what is the sum of letters in the word 'BAD'?",
            "difficulty": "Easy",
            "topic": "Coding-Decoding",
            "option_a": "6",
            "option_b": "7",
            "option_c": "8",
            "option_d": "9",
            "correct_answer": "B",
            "explanation": "B=2, A=1, D=4. Sum = 2+1+4 = 7",
            "xp_reward": 10
        },
        
        # Logical Reasoning - Blood Relations
        {
            "title": "Father-Son Relation",
            "description": "Pointing to a photograph, a man said, 'I have no brother or sister but that man's father is my father's son.' Who is in the photograph?",
            "difficulty": "Medium",
            "topic": "Blood Relations",
            "option_a": "His son",
            "option_b": "His father",
            "option_c": "His nephew",
            "option_d": "Himself",
            "correct_answer": "A",
            "explanation": "My father's son = Me (since no brother/sister). That man's father = Me. So that man = My son.",
            "xp_reward": 15
        },
        {
            "title": "Generational Relation",
            "description": "A is B's sister. C is B's mother. D is C's father. E is D's mother. How is A related to D?",
            "difficulty": "Easy",
            "topic": "Blood Relations",
            "option_a": "Granddaughter",
            "option_b": "Grandmother",
            "option_c": "Daughter",
            "option_d": "Great granddaughter",
            "correct_answer": "D",
            "explanation": "A→B (sister), B→C (child), C→D (child). So A is D's great granddaughter (3 generations down).",
            "xp_reward": 10
        },
        
        # Logical Reasoning - Direction Sense
        {
            "title": "U-Shaped Path",
            "description": "A man walks 5 km North, then turns right and walks 3 km, then turns right and walks 5 km. How far is he from the starting point?",
            "difficulty": "Easy",
            "topic": "Direction Sense",
            "option_a": "3 km",
            "option_b": "5 km",
            "option_c": "8 km",
            "option_d": "13 km",
            "correct_answer": "A",
            "explanation": "Movement: 5km N, 3km E, 5km S. Net: 0km N/S, 3km E. Distance = 3 km East.",
            "xp_reward": 10
        },
        {
            "title": "Rectangular Path",
            "description": "Starting from point P, Suresh walked 40m North, turned right and walked 30m, then turned right and walked 40m. In which direction is he from P?",
            "difficulty": "Easy",
            "topic": "Direction Sense",
            "option_a": "North",
            "option_b": "South",
            "option_c": "East",
            "option_d": "West",
            "correct_answer": "C",
            "explanation": "Movements: 40m N, 30m E, 40m S. Net displacement: 30m East, 0m North. He is due East of P.",
            "xp_reward": 10
        },
        
        # Verbal Ability - Synonyms
        {
            "title": "Synonym - Meticulous",
            "description": "Choose the word closest in meaning to METICULOUS:",
            "difficulty": "Easy",
            "topic": "Synonyms",
            "option_a": "Careless",
            "option_b": "Precise",
            "option_c": "Fast",
            "option_d": "Lazy",
            "correct_answer": "B",
            "explanation": "Meticulous means showing great attention to detail; very careful and precise.",
            "xp_reward": 10
        },
        {
            "title": "Synonym - Ephemeral",
            "description": "Choose the word closest in meaning to EPHEMERAL:",
            "difficulty": "Medium",
            "topic": "Synonyms",
            "option_a": "Permanent",
            "option_b": "Temporary",
            "option_c": "Beautiful",
            "option_d": "Mysterious",
            "correct_answer": "B",
            "explanation": "Ephemeral means lasting for a very short time; temporary or transient.",
            "xp_reward": 15
        },
        
        # Verbal Ability - Antonyms
        {
            "title": "Antonym - Abundant",
            "description": "Choose the word opposite in meaning to ABUNDANT:",
            "difficulty": "Easy",
            "topic": "Antonyms",
            "option_a": "Plentiful",
            "option_b": "Scarce",
            "option_c": "Rich",
            "option_d": "Available",
            "correct_answer": "B",
            "explanation": "Abundant means existing in large quantities. Its opposite is scarce (insufficient/rare).",
            "xp_reward": 10
        },
        {
            "title": "Antonym - Benevolent",
            "description": "Choose the word opposite in meaning to BENEVOLENT:",
            "difficulty": "Medium",
            "topic": "Antonyms",
            "option_a": "Kind",
            "option_b": "Generous",
            "option_c": "Malevolent",
            "option_d": "Helpful",
            "correct_answer": "C",
            "explanation": "Benevolent means well-meaning and kind. Its opposite is malevolent (having evil/harmful intentions).",
            "xp_reward": 15
        },
        
        # Verbal Ability - Sentence Completion
        {
            "title": "Sentence Completion - Investigation",
            "description": "The detective's ____ investigation revealed the truth behind the mystery.",
            "difficulty": "Easy",
            "topic": "Sentence Completion",
            "option_a": "careless",
            "option_b": "thorough",
            "option_c": "incomplete",
            "option_d": "random",
            "correct_answer": "B",
            "explanation": "Thorough (detailed and careful) fits best as it led to revealing the truth.",
            "xp_reward": 10
        },
        
        # Data Interpretation
        {
            "title": "Percentage to Count",
            "description": "In a class of 50 students, 60% are boys. How many girls are there?",
            "difficulty": "Easy",
            "topic": "Data Interpretation",
            "option_a": "15",
            "option_b": "20",
            "option_c": "25",
            "option_d": "30",
            "correct_answer": "B",
            "explanation": "Boys = 60% of 50 = 30. Girls = 50 - 30 = 20",
            "xp_reward": 10
        },
        {
            "title": "Excluded Number from Average",
            "description": "The average of 5 numbers is 30. If one number is excluded, the average becomes 28. What is the excluded number?",
            "difficulty": "Medium",
            "topic": "Averages",
            "option_a": "36",
            "option_b": "38",
            "option_c": "40",
            "option_d": "42",
            "correct_answer": "B",
            "explanation": "Sum of 5 numbers = 5×30 = 150. Sum of 4 numbers = 4×28 = 112. Excluded = 150 - 112 = 38",
            "xp_reward": 15
        },
        
        # Ages
        {
            "title": "Age Ratio Problem",
            "description": "The ratio of ages of A and B is 3:5. After 5 years, the ratio will be 2:3. What is A's present age?",
            "difficulty": "Medium",
            "topic": "Ages",
            "option_a": "15 years",
            "option_b": "20 years",
            "option_c": "25 years",
            "option_d": "30 years",
            "correct_answer": "A",
            "explanation": "Let ages be 3x and 5x. After 5 years: (3x+5)/(5x+5) = 2/3. Cross multiply: 9x+15=10x+10, x=5. A's age = 3×5 = 15",
            "xp_reward": 15
        },
        
        # Probability
        {
            "title": "Basic Ball Probability",
            "description": "A bag contains 3 red balls and 5 blue balls. What is the probability of drawing a red ball?",
            "difficulty": "Easy",
            "topic": "Probability",
            "option_a": "3/8",
            "option_b": "5/8",
            "option_c": "3/5",
            "option_d": "5/3",
            "correct_answer": "A",
            "explanation": "Probability = Favorable outcomes / Total outcomes = 3 / (3+5) = 3/8",
            "xp_reward": 10
        },
        {
            "title": "Two Dice Sum",
            "description": "What is the probability of getting a sum of 7 when two dice are thrown?",
            "difficulty": "Medium",
            "topic": "Probability",
            "option_a": "1/6",
            "option_b": "1/9",
            "option_c": "1/12",
            "option_d": "1/18",
            "correct_answer": "A",
            "explanation": "Favorable outcomes: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1) = 6 ways. Total outcomes = 36. P = 6/36 = 1/6",
            "xp_reward": 15
        },
        
        # Permutations and Combinations
        {
            "title": "Linear Arrangement",
            "description": "In how many ways can 5 people be arranged in a row?",
            "difficulty": "Easy",
            "topic": "Permutations",
            "option_a": "20",
            "option_b": "60",
            "option_c": "120",
            "option_d": "720",
            "correct_answer": "C",
            "explanation": "Number of arrangements = 5! = 5 × 4 × 3 × 2 × 1 = 120 ways",
            "xp_reward": 10
        },
        {
            "title": "Selection Problem",
            "description": "In how many ways can 3 books be selected from 7 different books?",
            "difficulty": "Medium",
            "topic": "Combinations",
            "option_a": "21",
            "option_b": "28",
            "option_c": "35",
            "option_d": "42",
            "correct_answer": "C",
            "explanation": "Combinations = ⁷C₃ = 7!/(3!×4!) = (7×6×5)/(3×2×1) = 210/6 = 35 ways",
            "xp_reward": 15
        },
        
        # Calendar Problems
        {
            "title": "Day of the Week",
            "description": "If January 1, 2020 was a Wednesday, what day was January 1, 2021?",
            "difficulty": "Medium",
            "topic": "Calendar",
            "option_a": "Thursday",
            "option_b": "Friday",
            "option_c": "Saturday",
            "option_d": "Sunday",
            "correct_answer": "B",
            "explanation": "2020 was a leap year (366 days). Odd days = 366 mod 7 = 2. Wednesday + 2 = Friday",
            "xp_reward": 15
        },
        
        # Clocks
        {
            "title": "Clock Angle",
            "description": "At what time between 3 and 4 o'clock will the hands of a clock be together?",
            "difficulty": "Hard",
            "topic": "Clocks",
            "option_a": "3:16:22",
            "option_b": "3:15:00",
            "option_c": "3:12:00",
            "option_d": "3:20:00",
            "correct_answer": "A",
            "explanation": "At 3:00, minute hand is 15 min behind. It gains 5.5 min every hour. Time = 15/(11/12) = 180/11 ≈ 16.36 min after 3",
            "xp_reward": 20
        }
    ]
    
    for question_data in questions_data:
        # Check if question already exists
        existing = db.query(models.Question).filter(models.Question.title == question_data["title"]).first()
        if not existing:
            question = models.Question(**question_data)
            db.add(question)
            print(f"✅ Created question: {question_data['title']}")
        else:
            print(f"⏭️  Question already exists: {question_data['title']}")
    
    db.commit()
    print(f"\n✅ Aptitude question seeding complete! Total: {len(questions_data)} questions")


def main():
    """Main seeding function"""
    print("🌱 Starting database seeding with APTITUDE questions...\n")
    
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed badges
        print("📛 Seeding badges...")
        seed_badges(db)
        
        print("\n" + "="*80 + "\n")
        
        # Seed aptitude questions
        print("❓ Seeding aptitude questions...")
        seed_aptitude_questions(db)
        
        print("\n" + "="*80)
        print("🎉 Database seeding completed successfully!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
