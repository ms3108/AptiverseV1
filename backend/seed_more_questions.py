"""Seed more Linguistic and Quantitative questions"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Question

LINGUISTIC_QUESTIONS = [
    # Synonyms (5 questions)
    {
        "title": "Synonym - Abundant",
        "description": "Choose the word most similar in meaning to 'ABUNDANT':",
        "difficulty": "Easy",
        "topic": "Synonyms",
        "category": "Linguistic",
        "option_a": "Plentiful",
        "option_b": "Scarce",
        "option_c": "Limited",
        "option_d": "Rare",
        "correct_answer": "A",
        "explanation": "Abundant means existing in large quantities; plentiful. Plentiful is the synonym.",
        "xp_reward": 10
    },
    {
        "title": "Synonym - Benevolent",
        "description": "Choose the word most similar in meaning to 'BENEVOLENT':",
        "difficulty": "Medium",
        "topic": "Synonyms",
        "category": "Linguistic",
        "option_a": "Cruel",
        "option_b": "Kind",
        "option_c": "Selfish",
        "option_d": "Harsh",
        "correct_answer": "B",
        "explanation": "Benevolent means well-meaning and kindly. Kind is the closest synonym.",
        "xp_reward": 15
    },
    {
        "title": "Synonym - Eloquent",
        "description": "Choose the word most similar in meaning to 'ELOQUENT':",
        "difficulty": "Medium",
        "topic": "Synonyms",
        "category": "Linguistic",
        "option_a": "Silent",
        "option_b": "Confused",
        "option_c": "Articulate",
        "option_d": "Hesitant",
        "correct_answer": "C",
        "explanation": "Eloquent means fluent or persuasive in speaking or writing. Articulate is the synonym.",
        "xp_reward": 15
    },
    
    # Antonyms (5 questions)
    {
        "title": "Antonym - Brave",
        "description": "Choose the word most opposite in meaning to 'BRAVE':",
        "difficulty": "Easy",
        "topic": "Antonyms",
        "category": "Linguistic",
        "option_a": "Courageous",
        "option_b": "Bold",
        "option_c": "Cowardly",
        "option_d": "Fearless",
        "correct_answer": "C",
        "explanation": "Brave means courageous. Cowardly (lacking courage) is the antonym.",
        "xp_reward": 10
    },
    {
        "title": "Antonym - Ancient",
        "description": "Choose the word most opposite in meaning to 'ANCIENT':",
        "difficulty": "Easy",
        "topic": "Antonyms",
        "category": "Linguistic",
        "option_a": "Old",
        "option_b": "Modern",
        "option_c": "Historic",
        "option_d": "Aged",
        "correct_answer": "B",
        "explanation": "Ancient means very old. Modern (relating to present time) is the antonym.",
        "xp_reward": 10
    },
    {
        "title": "Antonym - Optimistic",
        "description": "Choose the word most opposite in meaning to 'OPTIMISTIC':",
        "difficulty": "Easy",
        "topic": "Antonyms",
        "category": "Linguistic",
        "option_a": "Hopeful",
        "option_b": "Confident",
        "option_c": "Pessimistic",
        "option_d": "Cheerful",
        "correct_answer": "C",
        "explanation": "Optimistic means hopeful about the future. Pessimistic is the antonym.",
        "xp_reward": 10
    },
    
    # Sentence Completion (5 questions)
    {
        "title": "Sentence Completion 1",
        "description": "The politician's speech was so _____ that even his opponents were impressed.",
        "difficulty": "Medium",
        "topic": "Sentence Completion",
        "category": "Linguistic",
        "option_a": "boring",
        "option_b": "compelling",
        "option_c": "confusing",
        "option_d": "lengthy",
        "correct_answer": "B",
        "explanation": "The word 'compelling' (convincing, persuasive) fits because opponents were impressed.",
        "xp_reward": 15
    },
    {
        "title": "Sentence Completion 2",
        "description": "Despite the heavy rain, the marathon runners _____ to complete the race.",
        "difficulty": "Easy",
        "topic": "Sentence Completion",
        "category": "Linguistic",
        "option_a": "refused",
        "option_b": "failed",
        "option_c": "managed",
        "option_d": "forgot",
        "correct_answer": "C",
        "explanation": "'Despite' indicates overcoming difficulty, so 'managed' (succeeded) is correct.",
        "xp_reward": 10
    },
    {
        "title": "Sentence Completion 3",
        "description": "The scientist's _____ research led to a breakthrough in cancer treatment.",
        "difficulty": "Medium",
        "topic": "Sentence Completion",
        "category": "Linguistic",
        "option_a": "careless",
        "option_b": "groundbreaking",
        "option_c": "superficial",
        "option_d": "ordinary",
        "correct_answer": "B",
        "explanation": "Since it led to a breakthrough, the research was 'groundbreaking' (innovative).",
        "xp_reward": 15
    },
    
    # Grammar (5 questions)
    {
        "title": "Grammar - Subject-Verb Agreement",
        "description": "Choose the correct sentence:",
        "difficulty": "Easy",
        "topic": "Grammar",
        "category": "Linguistic",
        "option_a": "The team are playing well.",
        "option_b": "The team is playing well.",
        "option_c": "The team were playing well.",
        "option_d": "The team have playing well.",
        "correct_answer": "B",
        "explanation": "'Team' is a collective noun treated as singular, so 'is' is correct.",
        "xp_reward": 10
    },
    {
        "title": "Grammar - Tense",
        "description": "She _____ to the market yesterday.",
        "difficulty": "Easy",
        "topic": "Grammar",
        "category": "Linguistic",
        "option_a": "go",
        "option_b": "goes",
        "option_c": "went",
        "option_d": "going",
        "correct_answer": "C",
        "explanation": "'Yesterday' indicates past tense, so 'went' (past tense of go) is correct.",
        "xp_reward": 10
    },
    {
        "title": "Grammar - Articles",
        "description": "He is _____ honest man.",
        "difficulty": "Easy",
        "topic": "Grammar",
        "category": "Linguistic",
        "option_a": "a",
        "option_b": "an",
        "option_c": "the",
        "option_d": "no article",
        "correct_answer": "B",
        "explanation": "'Honest' starts with a vowel sound (the 'h' is silent), so 'an' is used.",
        "xp_reward": 10
    },
    {
        "title": "Grammar - Preposition",
        "description": "The cat jumped _____ the table.",
        "difficulty": "Easy",
        "topic": "Grammar",
        "category": "Linguistic",
        "option_a": "in",
        "option_b": "at",
        "option_c": "onto",
        "option_d": "into",
        "correct_answer": "C",
        "explanation": "'Onto' indicates movement to the surface of something.",
        "xp_reward": 10
    },
    
    # Error Spotting (3 questions)
    {
        "title": "Error Spotting 1",
        "description": "Find the error: 'Each of the students have completed their assignments.'",
        "difficulty": "Medium",
        "topic": "Error Spotting",
        "category": "Linguistic",
        "option_a": "Each of",
        "option_b": "the students",
        "option_c": "have completed",
        "option_d": "their assignments",
        "correct_answer": "C",
        "explanation": "'Each' is singular, so it should be 'has completed' not 'have completed'.",
        "xp_reward": 15
    },
    {
        "title": "Error Spotting 2",
        "description": "Find the error: 'Neither the teacher nor the students was present.'",
        "difficulty": "Medium",
        "topic": "Error Spotting",
        "category": "Linguistic",
        "option_a": "Neither",
        "option_b": "the teacher",
        "option_c": "nor the students",
        "option_d": "was present",
        "correct_answer": "D",
        "explanation": "With 'neither...nor', the verb agrees with the nearest subject ('students'), so it should be 'were present'.",
        "xp_reward": 15
    },
]

QUANTITATIVE_QUESTIONS = [
    # Percentages (5 questions)
    {
        "title": "Percentage Increase",
        "description": "If a number is increased by 20% and then decreased by 20%, what is the net change?",
        "difficulty": "Easy",
        "topic": "Percentages",
        "category": "Quantitative",
        "option_a": "No change",
        "option_b": "4% decrease",
        "option_c": "4% increase",
        "option_d": "20% decrease",
        "correct_answer": "B",
        "explanation": "Let number be 100. After 20% increase: 120. After 20% decrease: 120 × 0.8 = 96. Net change = 4% decrease.",
        "xp_reward": 10
    },
    {
        "title": "Percentage Calculation",
        "description": "What is 25% of 80?",
        "difficulty": "Easy",
        "topic": "Percentages",
        "category": "Quantitative",
        "option_a": "15",
        "option_b": "20",
        "option_c": "25",
        "option_d": "30",
        "correct_answer": "B",
        "explanation": "25% of 80 = (25/100) × 80 = 20.",
        "xp_reward": 10
    },
    {
        "title": "Percentage Problem",
        "description": "If 40% of a number is 80, what is the number?",
        "difficulty": "Easy",
        "topic": "Percentages",
        "category": "Quantitative",
        "option_a": "160",
        "option_b": "180",
        "option_c": "200",
        "option_d": "220",
        "correct_answer": "C",
        "explanation": "Let the number be x. 40% of x = 80. So x = 80 × (100/40) = 200.",
        "xp_reward": 10
    },
    
    # Profit and Loss (5 questions)
    {
        "title": "Profit Calculation",
        "description": "A shopkeeper buys an article for ₹500 and sells it for ₹600. What is the profit percentage?",
        "difficulty": "Easy",
        "topic": "Profit and Loss",
        "category": "Quantitative",
        "option_a": "15%",
        "option_b": "20%",
        "option_c": "25%",
        "option_d": "30%",
        "correct_answer": "B",
        "explanation": "Profit = 600 - 500 = 100. Profit% = (100/500) × 100 = 20%.",
        "xp_reward": 10
    },
    {
        "title": "Loss Calculation",
        "description": "An item bought for ₹800 is sold for ₹720. What is the loss percentage?",
        "difficulty": "Easy",
        "topic": "Profit and Loss",
        "category": "Quantitative",
        "option_a": "8%",
        "option_b": "10%",
        "option_c": "12%",
        "option_d": "15%",
        "correct_answer": "B",
        "explanation": "Loss = 800 - 720 = 80. Loss% = (80/800) × 100 = 10%.",
        "xp_reward": 10
    },
    {
        "title": "Selling Price",
        "description": "Cost price is ₹400 and profit is 25%. What is the selling price?",
        "difficulty": "Easy",
        "topic": "Profit and Loss",
        "category": "Quantitative",
        "option_a": "₹450",
        "option_b": "₹475",
        "option_c": "₹500",
        "option_d": "₹525",
        "correct_answer": "C",
        "explanation": "SP = CP + Profit = 400 + (25% of 400) = 400 + 100 = ₹500.",
        "xp_reward": 10
    },
    
    # Simple Interest (4 questions)
    {
        "title": "Simple Interest",
        "description": "Find the simple interest on ₹5000 at 10% per annum for 2 years.",
        "difficulty": "Easy",
        "topic": "Simple Interest",
        "category": "Quantitative",
        "option_a": "₹500",
        "option_b": "₹800",
        "option_c": "₹1000",
        "option_d": "₹1200",
        "correct_answer": "C",
        "explanation": "SI = (P × R × T)/100 = (5000 × 10 × 2)/100 = ₹1000.",
        "xp_reward": 10
    },
    {
        "title": "Principal Amount",
        "description": "What principal will yield ₹600 as SI at 5% per annum in 4 years?",
        "difficulty": "Medium",
        "topic": "Simple Interest",
        "category": "Quantitative",
        "option_a": "₹2500",
        "option_b": "₹3000",
        "option_c": "₹3500",
        "option_d": "₹4000",
        "correct_answer": "B",
        "explanation": "P = (SI × 100)/(R × T) = (600 × 100)/(5 × 4) = 60000/20 = ₹3000.",
        "xp_reward": 15
    },
    
    # Ratio and Proportion (4 questions)
    {
        "title": "Ratio Problem",
        "description": "If A:B = 3:4 and B:C = 5:6, find A:C.",
        "difficulty": "Medium",
        "topic": "Ratio and Proportion",
        "category": "Quantitative",
        "option_a": "5:8",
        "option_b": "3:6",
        "option_c": "15:24",
        "option_d": "5:6",
        "correct_answer": "A",
        "explanation": "A:B = 3:4 = 15:20 and B:C = 5:6 = 20:24. So A:B:C = 15:20:24. A:C = 15:24 = 5:8.",
        "xp_reward": 15
    },
    {
        "title": "Divide in Ratio",
        "description": "Divide ₹630 between A and B in the ratio 2:5.",
        "difficulty": "Easy",
        "topic": "Ratio and Proportion",
        "category": "Quantitative",
        "option_a": "A=₹180, B=₹450",
        "option_b": "A=₹200, B=₹430",
        "option_c": "A=₹210, B=₹420",
        "option_d": "A=₹150, B=₹480",
        "correct_answer": "A",
        "explanation": "Total parts = 2+5 = 7. A = (2/7) × 630 = ₹180. B = (5/7) × 630 = ₹450.",
        "xp_reward": 10
    },
    
    # Time and Work (4 questions)
    {
        "title": "Work Problem 1",
        "description": "A can complete a work in 10 days and B in 15 days. How many days will they take together?",
        "difficulty": "Medium",
        "topic": "Time and Work",
        "category": "Quantitative",
        "option_a": "5 days",
        "option_b": "6 days",
        "option_c": "7 days",
        "option_d": "8 days",
        "correct_answer": "B",
        "explanation": "A's 1 day work = 1/10, B's = 1/15. Together = 1/10 + 1/15 = 5/30 = 1/6. Days = 6.",
        "xp_reward": 15
    },
    {
        "title": "Work Problem 2",
        "description": "If 5 workers can build a wall in 12 days, how many days will 10 workers take?",
        "difficulty": "Easy",
        "topic": "Time and Work",
        "category": "Quantitative",
        "option_a": "4 days",
        "option_b": "6 days",
        "option_c": "8 days",
        "option_d": "24 days",
        "correct_answer": "B",
        "explanation": "Workers and days are inversely proportional. 5 × 12 = 10 × x. x = 60/10 = 6 days.",
        "xp_reward": 10
    },
    
    # Time and Distance (4 questions)
    {
        "title": "Speed Calculation",
        "description": "A car travels 240 km in 4 hours. What is its speed?",
        "difficulty": "Easy",
        "topic": "Time and Distance",
        "category": "Quantitative",
        "option_a": "50 km/h",
        "option_b": "55 km/h",
        "option_c": "60 km/h",
        "option_d": "65 km/h",
        "correct_answer": "C",
        "explanation": "Speed = Distance/Time = 240/4 = 60 km/h.",
        "xp_reward": 10
    },
    {
        "title": "Distance Problem",
        "description": "A train running at 72 km/h crosses a pole in 15 seconds. Find the length of the train.",
        "difficulty": "Medium",
        "topic": "Time and Distance",
        "category": "Quantitative",
        "option_a": "200 m",
        "option_b": "250 m",
        "option_c": "300 m",
        "option_d": "350 m",
        "correct_answer": "C",
        "explanation": "Speed = 72 × (5/18) = 20 m/s. Length = Speed × Time = 20 × 15 = 300 m.",
        "xp_reward": 15
    },
    {
        "title": "Average Speed",
        "description": "A person travels from A to B at 40 km/h and returns at 60 km/h. What is the average speed?",
        "difficulty": "Medium",
        "topic": "Time and Distance",
        "category": "Quantitative",
        "option_a": "45 km/h",
        "option_b": "48 km/h",
        "option_c": "50 km/h",
        "option_d": "52 km/h",
        "correct_answer": "B",
        "explanation": "Average speed = 2×40×60/(40+60) = 4800/100 = 48 km/h.",
        "xp_reward": 15
    },
    
    # Averages (3 questions)
    {
        "title": "Average Problem",
        "description": "The average of 5 numbers is 20. If one number is excluded, the average becomes 18. Find the excluded number.",
        "difficulty": "Medium",
        "topic": "Averages",
        "category": "Quantitative",
        "option_a": "24",
        "option_b": "26",
        "option_c": "28",
        "option_d": "30",
        "correct_answer": "C",
        "explanation": "Sum of 5 numbers = 5 × 20 = 100. Sum of 4 numbers = 4 × 18 = 72. Excluded = 100 - 72 = 28.",
        "xp_reward": 15
    },
    {
        "title": "Weighted Average",
        "description": "Find the average of first 10 natural numbers.",
        "difficulty": "Easy",
        "topic": "Averages",
        "category": "Quantitative",
        "option_a": "5",
        "option_b": "5.5",
        "option_c": "6",
        "option_d": "6.5",
        "correct_answer": "B",
        "explanation": "Sum = n(n+1)/2 = 10×11/2 = 55. Average = 55/10 = 5.5.",
        "xp_reward": 10
    },
    
    # Number System (3 questions)
    {
        "title": "LCM Problem",
        "description": "Find the LCM of 12, 15, and 20.",
        "difficulty": "Easy",
        "topic": "Number System",
        "category": "Quantitative",
        "option_a": "40",
        "option_b": "60",
        "option_c": "80",
        "option_d": "120",
        "correct_answer": "B",
        "explanation": "12 = 2²×3, 15 = 3×5, 20 = 2²×5. LCM = 2²×3×5 = 60.",
        "xp_reward": 10
    },
    {
        "title": "HCF Problem",
        "description": "Find the HCF of 48 and 60.",
        "difficulty": "Easy",
        "topic": "Number System",
        "category": "Quantitative",
        "option_a": "6",
        "option_b": "8",
        "option_c": "10",
        "option_d": "12",
        "correct_answer": "D",
        "explanation": "48 = 2⁴×3, 60 = 2²×3×5. HCF = 2²×3 = 12.",
        "xp_reward": 10
    },
]

def seed_questions():
    db = SessionLocal()
    
    added = 0
    skipped = 0
    
    all_questions = LINGUISTIC_QUESTIONS + QUANTITATIVE_QUESTIONS
    
    for q_data in all_questions:
        # Check if question already exists
        existing = db.query(Question).filter(Question.title == q_data["title"]).first()
        if existing:
            print(f"⏭️ Skipped (exists): {q_data['title']}")
            skipped += 1
            continue
        
        question = Question(**q_data)
        db.add(question)
        added += 1
        print(f"✅ Added: {q_data['title']} [{q_data['category']} - {q_data['topic']}]")
    
    db.commit()
    
    print(f"\n📊 Summary:")
    print(f"  Added: {added} questions")
    print(f"  Skipped: {skipped} questions")
    
    # Show category breakdown
    print("\n📋 Category Summary:")
    for cat in ["Quantitative", "Logical", "Linguistic"]:
        count = db.query(Question).filter(Question.category == cat).count()
        topics = db.query(Question.topic).filter(Question.category == cat).distinct().all()
        print(f"  {cat}: {count} questions ({len(topics)} topics)")
    
    db.close()

if __name__ == "__main__":
    seed_questions()
