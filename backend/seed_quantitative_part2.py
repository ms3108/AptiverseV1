"""
Seed script for remaining quantitative aptitude questions (Part 2)
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

def seed_quantitative_questions_part2(db: Session):
    """Add remaining quantitative aptitude questions"""
    questions_data = [
        # More Pipes and Cisterns Questions
        {
            "title": "Three Pipes Problem",
            "description": "Two pipes A and B can fill a tank in 15 hours and 20 hours respectively while a third pipe C can empty the full tank in 25 hours. All three pipes are opened in the beginning. After 10 hours, C is closed. In how much time will the tank be full?",
            "difficulty": "Hard",
            "topic": "Time and Work",
            "option_a": "12 hrs",
            "option_b": "13 hrs",
            "option_c": "16 hrs",
            "option_d": "18 hrs",
            "correct_answer": "A",
            "explanation": "Part filled by (A+B-C) in 1 hour = (1/15) + (1/20) - (1/25) = 23/300. In 10 hours, part filled = 10 × (23/300) = 23/30. Remaining part = 1 - 23/30 = 7/30. Now C is closed. Part filled by (A+B) in 1 hour = (1/15) + (1/20) = 7/60. Time to fill remaining part = (7/30) / (7/60) = 2 hours. Total time = 10 + 2 = 12 hours.",
            "xp_reward": 20
        },
        {
            "title": "Three Pipes Cistern",
            "description": "Three pipes A, B, and C can fill a cistern in 6 hours. After working at it together for 2 hours, C is closed and A and B can fill the remaining part in 7 hours. The number of hours taken by C alone to fill the cistern is:",
            "difficulty": "Hard",
            "topic": "Time and Work",
            "option_a": "10",
            "option_b": "12",
            "option_c": "14",
            "option_d": "16",
            "correct_answer": "C",
            "explanation": "Part filled by A, B, C in 2 hours = 2/6 = 1/3. Remaining part = 2/3. This is filled by A and B in 7 hours. So, (A+B)'s 1 hour work = (2/3) / 7 = 2/21. (A+B+C)'s 1 hour work = 1/6. C's 1 hour work = (1/6) - (2/21) = 1/14. Therefore, C alone can fill the tank in 14 hours.",
            "xp_reward": 20
        },
        # More HCF and LCM Questions
        {
            "title": "Greatest Divisor with Remainder",
            "description": "Find the greatest number that will divide 43, 91 and 183 so as to leave the same remainder in each case.",
            "difficulty": "Medium",
            "topic": "Number System",
            "option_a": "4",
            "option_b": "7",
            "option_c": "9",
            "option_d": "13",
            "correct_answer": "A",
            "explanation": "Find the HCF of the differences between the numbers. Differences are: (91 - 43) = 48, (183 - 91) = 92, and (183 - 43) = 140. HCF of 48, 92, and 140 = 4.",
            "xp_reward": 15
        },
        {
            "title": "Bells Tolling Together",
            "description": "Six bells commence tolling together and toll at intervals of 2, 4, 6, 8, 10, and 12 seconds respectively. In 30 minutes, how many times do they toll together?",
            "difficulty": "Medium",
            "topic": "Number System",
            "option_a": "15",
            "option_b": "16",
            "option_c": "10",
            "option_d": "20",
            "correct_answer": "B",
            "explanation": "The bells will toll together at the LCM of their intervals. LCM of (2, 4, 6, 8, 10, 12) = 120 seconds = 2 minutes. In 30 minutes, they toll together (30 / 2) = 15 times. Adding the initial toll at 0th second = 15 + 1 = 16 times.",
            "xp_reward": 15
        },
        # More Profit and Loss Questions
        {
            "title": "Dishonest Dealer",
            "description": "A dishonest dealer professes to sell his goods at cost price but uses a weight of 950 gm instead of 1 kg. Find his gain percent.",
            "difficulty": "Medium",
            "topic": "Profit and Loss",
            "option_a": "5%",
            "option_b": "5.26%",
            "option_c": "5.5%",
            "option_d": "4.76%",
            "correct_answer": "B",
            "explanation": "The dealer sells 950 gm but charges for 1000 gm. Gain % = (Error / (True Value - Error)) × 100 = (50 / 950) × 100 = 5.26% (approx).",
            "xp_reward": 15
        },
        {
            "title": "Gain from Selling Cloth",
            "description": "By selling 33 meters of cloth, a person gains the cost price of 11 meters. Find the gain percent.",
            "difficulty": "Medium",
            "topic": "Profit and Loss",
            "option_a": "25%",
            "option_b": "33.33%",
            "option_c": "20%",
            "option_d": "40%",
            "correct_answer": "B",
            "explanation": "Let CP of 1 meter = Re. 1. CP of 33 meters = Rs. 33. Gain = CP of 11 meters = Rs. 11. Gain % = (11 / 33) × 100 = 33.33%.",
            "xp_reward": 15
        },
        {
            "title": "Marking and Discount",
            "description": "A trader marks his goods 40% above the cost price and allows a discount of 25%. What is his gain percent?",
            "difficulty": "Medium",
            "topic": "Profit and Loss",
            "option_a": "5%",
            "option_b": "10%",
            "option_c": "15%",
            "option_d": "12%",
            "correct_answer": "A",
            "explanation": "Let CP = Rs. 100. MP = 140. Discount = 25% of 140 = Rs. 35. SP = 140 - 35 = Rs. 105. Gain = 5. Gain % = 5%. Using formula: (+40) + (-25) + (40 × -25)/100 = 15 - 10 = 5%.",
            "xp_reward": 15
        },
        # More Percentage Questions
        {
            "title": "Election Votes",
            "description": "In an election, a candidate who gets 84% of the votes is elected by a majority of 476 votes. What is the total number of votes polled?",
            "difficulty": "Medium",
            "topic": "Percentages",
            "option_a": "600",
            "option_b": "700",
            "option_c": "800",
            "option_d": "900",
            "correct_answer": "B",
            "explanation": "Winner gets 84%, loser gets 16%. Majority = 84% - 16% = 68% = 476 votes. Total votes = 476 / 0.68 = 700.",
            "xp_reward": 15
        },
        {
            "title": "Population Growth",
            "description": "The population of a town increases by 5% annually. If its present population is 9261, what was it 3 years ago?",
            "difficulty": "Medium",
            "topic": "Percentages",
            "option_a": "8000",
            "option_b": "7500",
            "option_c": "7000",
            "option_d": "8500",
            "correct_answer": "A",
            "explanation": "Let the population 3 years ago be P. Present Population = P × (1.05)³. 9261 = P × (21/20)³ = P × (9261/8000). So, P = 8000.",
            "xp_reward": 15
        },
        {
            "title": "Passing Marks",
            "description": "A student has to secure 40% marks to pass. He gets 178 marks and fails by 22 marks. The maximum marks are:",
            "difficulty": "Easy",
            "topic": "Percentages",
            "option_a": "400",
            "option_b": "500",
            "option_c": "600",
            "option_d": "1000",
            "correct_answer": "B",
            "explanation": "Passing marks = 178 + 22 = 200. This is 40% of maximum marks. Let max = M. 0.40 × M = 200. M = 200 / 0.4 = 500.",
            "xp_reward": 10
        },
        # More Geometry and Trigonometry Questions
        {
            "title": "Triangle Angles",
            "description": "The angles of a triangle are in the ratio 2:3:4. What is the measure of the largest angle?",
            "difficulty": "Easy",
            "topic": "Geometry",
            "option_a": "60°",
            "option_b": "80°",
            "option_c": "90°",
            "option_d": "100°",
            "correct_answer": "B",
            "explanation": "Sum of angles = 180°. Let angles be 2x, 3x, 4x. So, 9x = 180°. x = 20°. Angles are 40°, 60°, 80°. Largest = 80°.",
            "xp_reward": 10
        },
        {
            "title": "Trigonometric Ratio",
            "description": "If sin(θ) = 5/13, and θ is an acute angle, find the value of tan(θ).",
            "difficulty": "Medium",
            "topic": "Trigonometry",
            "option_a": "5/12",
            "option_b": "12/13",
            "option_c": "12/5",
            "option_d": "13/12",
            "correct_answer": "A",
            "explanation": "sin(θ) = Perpendicular / Hypotenuse = 5/13. Using Pythagoras, Base² = 13² - 5² = 169 - 25 = 144. Base = 12. tan(θ) = Perpendicular / Base = 5/12.",
            "xp_reward": 15
        },
        {
            "title": "Equilateral Triangle Area",
            "description": "Find the area of an equilateral triangle with a side length of 4 cm.",
            "difficulty": "Medium",
            "topic": "Geometry",
            "option_a": "4√3 sq. cm",
            "option_b": "3√4 sq. cm",
            "option_c": "2√3 sq. cm",
            "option_d": "4√2 sq. cm",
            "correct_answer": "A",
            "explanation": "Formula for area of equilateral triangle: Area = (√3/4) × side². Area = (√3/4) × 16 = 4√3 sq. cm.",
            "xp_reward": 15
        },
        # Logarithms and Surds Questions
        {
            "title": "Logarithm Value",
            "description": "Find the value of log₃(81).",
            "difficulty": "Easy",
            "topic": "Logarithms",
            "option_a": "3",
            "option_b": "4",
            "option_c": "5",
            "option_d": "9",
            "correct_answer": "B",
            "explanation": "log₃(81) asks 'to what power must we raise 3 to get 81?'. 3⁴ = 81. Therefore, log₃(81) = 4.",
            "xp_reward": 10
        },
        {
            "title": "Simplify Surd",
            "description": "Simplify the surd: √125.",
            "difficulty": "Easy",
            "topic": "Surds",
            "option_a": "5√5",
            "option_b": "25√5",
            "option_c": "5√25",
            "option_d": "5√3",
            "correct_answer": "A",
            "explanation": "125 = 25 × 5. So, √125 = √(25 × 5) = √25 × √5 = 5√5.",
            "xp_reward": 10
        },
        {
            "title": "Logarithm Equation",
            "description": "If log(x) + log(y) = log(x + y), what is y in terms of x?",
            "difficulty": "Medium",
            "topic": "Logarithms",
            "option_a": "y = x/(x-1)",
            "option_b": "y = x/(x+1)",
            "option_c": "y = x",
            "option_d": "y = x+1",
            "correct_answer": "A",
            "explanation": "Using log(a) + log(b) = log(ab), we get log(xy) = log(x + y). So xy = x + y. xy - y = x. y(x - 1) = x. y = x / (x - 1).",
            "xp_reward": 15
        },
        {
            "title": "Rationalize Denominator",
            "description": "Rationalize the denominator of 2 / (√5 - 1).",
            "difficulty": "Medium",
            "topic": "Surds",
            "option_a": "(√5 + 1)/2",
            "option_b": "(√5 - 1)/2",
            "option_c": "√5 + 1",
            "option_d": "√5 - 1",
            "correct_answer": "A",
            "explanation": "Multiply numerator and denominator by (√5 + 1). [2(√5 + 1)] / [(√5)² - 1²] = [2(√5 + 1)] / 4 = (√5 + 1) / 2.",
            "xp_reward": 15
        },
        {
            "title": "Solve Logarithmic Equation",
            "description": "Solve for x: log₂(x) + log₂(x-2) = 3.",
            "difficulty": "Hard",
            "topic": "Logarithms",
            "option_a": "4",
            "option_b": "2",
            "option_c": "-2",
            "option_d": "6",
            "correct_answer": "A",
            "explanation": "Using log(a) + log(b) = log(ab): log₂(x(x-2)) = 3. So x(x-2) = 2³ = 8. x² - 2x - 8 = 0. (x-4)(x+2) = 0. x = 4 or x = -2. Since log of negative is undefined, x = 4.",
            "xp_reward": 20
        },
        # More Set Theory Questions
        {
            "title": "Union of Sets",
            "description": "If n(A) = 15, n(B) = 20, and n(A ∩ B) = 5, find n(A ∪ B).",
            "difficulty": "Easy",
            "topic": "Set Theory",
            "option_a": "35",
            "option_b": "30",
            "option_c": "25",
            "option_d": "40",
            "correct_answer": "B",
            "explanation": "Using the inclusion-exclusion principle: n(A ∪ B) = n(A) + n(B) - n(A ∩ B) = 15 + 20 - 5 = 30.",
            "xp_reward": 10
        },
        {
            "title": "Students Failing Subjects",
            "description": "Out of 100 students, 50 failed in English and 30 in Mathematics. If 12 students failed in both, how many passed in both subjects?",
            "difficulty": "Medium",
            "topic": "Set Theory",
            "option_a": "32",
            "option_b": "28",
            "option_c": "38",
            "option_d": "42",
            "correct_answer": "A",
            "explanation": "Students who failed in at least one subject = 50 + 30 - 12 = 68. Students who passed both = 100 - 68 = 32.",
            "xp_reward": 15
        },
        {
            "title": "Complement of Set",
            "description": "Let U = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10} be the universal set and A = {2, 4, 6, 8, 10}. Find the complement of A, denoted as A'.",
            "difficulty": "Easy",
            "topic": "Set Theory",
            "option_a": "{1, 3, 5, 7, 9}",
            "option_b": "{2, 4, 6, 8, 10}",
            "option_c": "{1, 2, 3, 4}",
            "option_d": "{}",
            "correct_answer": "A",
            "explanation": "The complement of A contains all elements of U that are not in A. So A' = {1, 3, 5, 7, 9}.",
            "xp_reward": 10
        },
        {
            "title": "Minimum Overlap",
            "description": "In a survey of 1000 consumers, 720 like product A and 450 like product B. What is the least number that must have liked both products?",
            "difficulty": "Medium",
            "topic": "Set Theory",
            "option_a": "170",
            "option_b": "270",
            "option_c": "50",
            "option_d": "220",
            "correct_answer": "A",
            "explanation": "Maximum n(A ∪ B) = 1000. So 1000 ≥ 720 + 450 - n(A ∩ B). n(A ∩ B) ≥ 1170 - 1000 = 170. Minimum overlap = 170.",
            "xp_reward": 15
        },
        # More Series and Patterns Questions
        {
            "title": "Number Pattern",
            "description": "Find the missing term in the series: 2, 5, 10, 17, ?, 37.",
            "difficulty": "Easy",
            "topic": "Series",
            "option_a": "24",
            "option_b": "25",
            "option_c": "26",
            "option_d": "27",
            "correct_answer": "C",
            "explanation": "Pattern is n² + 1. For n=1: 1²+1=2. n=2: 2²+1=5. n=3: 3²+1=10. n=4: 4²+1=17. n=5: 5²+1=26. n=6: 6²+1=37.",
            "xp_reward": 10
        },
        {
            "title": "Alpha-numeric Series",
            "description": "Find the next term in the series: F2, ?, D8, C16, B32.",
            "difficulty": "Medium",
            "topic": "Series",
            "option_a": "E4",
            "option_b": "E3",
            "option_c": "A16",
            "option_d": "G4",
            "correct_answer": "A",
            "explanation": "Letters are in reverse order: F, E, D, C, B. Numbers are in reverse geometric progression (×2): 32, 16, 8, 4, 2. Missing term is E4.",
            "xp_reward": 15
        },
        {
            "title": "Months Series",
            "description": "What comes next in the sequence: J, F, M, A, M, J, J, ?",
            "difficulty": "Medium",
            "topic": "Series",
            "option_a": "A",
            "option_b": "S",
            "option_c": "O",
            "option_d": "N",
            "correct_answer": "A",
            "explanation": "The series consists of first letters of months: January, February, March, April, May, June, July. Next is August, so the answer is A.",
            "xp_reward": 15
        }
    ]
    
    for question_data in questions_data:
        existing = db.query(models.Question).filter(models.Question.title == question_data["title"]).first()
        if not existing:
            question = models.Question(**question_data)
            db.add(question)
            print(f"✅ Created question: {question_data['title']}")
        else:
            print(f"⏭️  Question already exists: {question_data['title']}")
    
    db.commit()
    print(f"\n✅ Part 2 quantitative questions seeding complete! Total: {len(questions_data)} questions")


def main():
    print("🌱 Starting Part 2 quantitative questions seeding...\n")
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        seed_quantitative_questions_part2(db)
        print("\n" + "="*80)
        print("🎉 Seeding completed successfully!")
        print("="*80 + "\n")
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
