"""
Seed script for adding quantitative aptitude questions
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

def seed_quantitative_questions(db: Session):
    """Add quantitative aptitude questions"""
    questions_data = [
        # Algebra Questions
        {
            "title": "Simple Equation",
            "description": "If 5x + 9 = 34, what is the value of x?",
            "difficulty": "Easy",
            "topic": "Algebra",
            "option_a": "3",
            "option_b": "4",
            "option_c": "5",
            "option_d": "6",
            "correct_answer": "C",
            "explanation": "Given: 5x + 9 = 34. Subtract 9 from both sides: 5x = 34 - 9 => 5x = 25. Divide by 5: x = 25 / 5 = 5.",
            "xp_reward": 10
        },
        {
            "title": "Quadratic Equation",
            "description": "Find the roots of the quadratic equation x² - 8x + 15 = 0.",
            "difficulty": "Easy",
            "topic": "Algebra",
            "option_a": "(3, 5)",
            "option_b": "(3, -5)",
            "option_c": "(-3, 5)",
            "option_d": "(-3, -5)",
            "correct_answer": "A",
            "explanation": "We need to find two numbers that multiply to 15 and add up to -8. These numbers are -3 and -5. So, the equation can be factored as (x - 3)(x - 5) = 0. The roots are x = 3 and x = 5.",
            "xp_reward": 10
        },
        {
            "title": "Inequality",
            "description": "Solve the inequality: 3x - 7 < 8.",
            "difficulty": "Easy",
            "topic": "Algebra",
            "option_a": "x > 5",
            "option_b": "x < 5",
            "option_c": "x > 15",
            "option_d": "x < 15",
            "correct_answer": "B",
            "explanation": "Given: 3x - 7 < 8. Add 7 to both sides: 3x < 8 + 7 => 3x < 15. Divide by 3: x < 5.",
            "xp_reward": 10
        },
        {
            "title": "Linear Equations",
            "description": "If 2x + 3y = 11 and 3x + 2y = 9, what are the values of x and y?",
            "difficulty": "Medium",
            "topic": "Algebra",
            "option_a": "x=1, y=3",
            "option_b": "x=3, y=1",
            "option_c": "x=2, y=2",
            "option_d": "x=4, y=1",
            "correct_answer": "A",
            "explanation": "Multiply the first equation by 3 and the second by 2: (1) 6x + 9y = 33, (2) 6x + 4y = 18. Subtract (2) from (1): 5y = 15 => y = 3. Substitute y=3 into the first equation: 2x + 9 = 11 => x = 1.",
            "xp_reward": 15
        },
        {
            "title": "Age Problem",
            "description": "The sum of the ages of a father and his son is 60 years. Six years ago, the father's age was five times the age of the son. What will be the son's age after 6 years?",
            "difficulty": "Medium",
            "topic": "Algebra",
            "option_a": "14 years",
            "option_b": "20 years",
            "option_c": "22 years",
            "option_d": "18 years",
            "correct_answer": "B",
            "explanation": "Let F and S be present ages. F + S = 60. Six years ago: F-6 = 5(S-6) => F = 5S - 24. Substitute: 5S - 24 + S = 60 => 6S = 84 => S = 14. After 6 years: 14 + 6 = 20 years.",
            "xp_reward": 15
        },
        # Mensuration Questions
        {
            "title": "Rectangle Area",
            "description": "The length of a rectangular plot is 20 meters and its breadth is 15 meters. What is the area of the plot?",
            "difficulty": "Easy",
            "topic": "Mensuration",
            "option_a": "300 sq. m",
            "option_b": "350 sq. m",
            "option_c": "400 sq. m",
            "option_d": "250 sq. m",
            "correct_answer": "A",
            "explanation": "Area of a rectangle = Length × Breadth. Area = 20 m × 15 m = 300 sq. m.",
            "xp_reward": 10
        },
        {
            "title": "Circle Area",
            "description": "Find the area of a circle whose radius is 7 cm. (Use π = 22/7)",
            "difficulty": "Easy",
            "topic": "Mensuration",
            "option_a": "154 sq. cm",
            "option_b": "144 sq. cm",
            "option_c": "164 sq. cm",
            "option_d": "174 sq. cm",
            "correct_answer": "A",
            "explanation": "Area of a circle = πr². Area = (22/7) × 7 × 7 = 22 × 7 = 154 sq. cm.",
            "xp_reward": 10
        },
        {
            "title": "Cube Volume",
            "description": "What is the volume of a cube whose side is 6 cm?",
            "difficulty": "Easy",
            "topic": "Mensuration",
            "option_a": "180 cubic cm",
            "option_b": "216 cubic cm",
            "option_c": "256 cubic cm",
            "option_d": "196 cubic cm",
            "correct_answer": "B",
            "explanation": "Volume of a cube = (side)³. Volume = 6³ = 6 × 6 × 6 = 216 cubic cm.",
            "xp_reward": 10
        },
        {
            "title": "Cylinder Volume",
            "description": "The height of a cylinder is 14 cm and its curved surface area is 264 sq. cm. Find the volume of the cylinder. (Use π = 22/7)",
            "difficulty": "Medium",
            "topic": "Mensuration",
            "option_a": "396 cubic cm",
            "option_b": "308 cubic cm",
            "option_c": "412 cubic cm",
            "option_d": "352 cubic cm",
            "correct_answer": "A",
            "explanation": "CSA = 2πrh. 264 = 2 × (22/7) × r × 14 => r = 3 cm. Volume = πr²h = (22/7) × 9 × 14 = 396 cubic cm.",
            "xp_reward": 15
        },
        {
            "title": "Hemisphere Surface Area",
            "description": "Find the total surface area of a hemisphere of radius 7 cm. (Use π = 22/7)",
            "difficulty": "Medium",
            "topic": "Mensuration",
            "option_a": "308 sq. cm",
            "option_b": "462 sq. cm",
            "option_c": "616 sq. cm",
            "option_d": "154 sq. cm",
            "correct_answer": "B",
            "explanation": "TSA of hemisphere = 3πr² = 3 × (22/7) × 49 = 462 sq. cm.",
            "xp_reward": 15
        },
        # Time and Distance Questions
        {
            "title": "Train Crossing Platform",
            "description": "A train 120m long is running at a speed of 90 km/h. How long will it take to cross a platform 230m long?",
            "difficulty": "Easy",
            "topic": "Time and Distance",
            "option_a": "10 seconds",
            "option_b": "12 seconds",
            "option_c": "14 seconds",
            "option_d": "16 seconds",
            "correct_answer": "C",
            "explanation": "Total distance = 120 + 230 = 350m. Speed = 90 × (5/18) = 25 m/s. Time = 350 / 25 = 14 seconds.",
            "xp_reward": 10
        },
        {
            "title": "Two Trains Crossing",
            "description": "Two trains of length 100m and 150m are moving in opposite directions at 72 km/h and 78 km/h. In how much time will they cross?",
            "difficulty": "Medium",
            "topic": "Time and Distance",
            "option_a": "5 seconds",
            "option_b": "6 seconds",
            "option_c": "7 seconds",
            "option_d": "8 seconds",
            "correct_answer": "B",
            "explanation": "Relative speed = 72 + 78 = 150 km/h = 125/3 m/s. Distance = 250m. Time = 250 / (125/3) = 6 seconds.",
            "xp_reward": 15
        },
        {
            "title": "Boat Distance Problem",
            "description": "A man can row at 5 km/h in still water. Current is 1 km/h. He takes 1 hour total to row to a place and back. How far is the place?",
            "difficulty": "Medium",
            "topic": "Boats and Streams",
            "option_a": "2.4 km",
            "option_b": "2.5 km",
            "option_c": "3 km",
            "option_d": "3.2 km",
            "correct_answer": "A",
            "explanation": "Downstream = 6 km/h, Upstream = 4 km/h. (d/6) + (d/4) = 1. 5d/12 = 1. d = 2.4 km.",
            "xp_reward": 15
        },
        {
            "title": "Boat Speed in Still Water",
            "description": "A boat goes 40 km upstream in 8 hours and 36 km downstream in 6 hours. The speed in still water is:",
            "difficulty": "Easy",
            "topic": "Boats and Streams",
            "option_a": "5.5 km/h",
            "option_b": "6 km/h",
            "option_c": "6.5 km/h",
            "option_d": "5 km/h",
            "correct_answer": "A",
            "explanation": "Upstream speed = 40/8 = 5 km/h. Downstream = 36/6 = 6 km/h. Still water = (5+6)/2 = 5.5 km/h.",
            "xp_reward": 10
        },
        # Pipes and Cisterns
        {
            "title": "Two Pipes Filling Tank",
            "description": "Pipe A fills a tank in 20 minutes and Pipe B in 30 minutes. Together they fill it in:",
            "difficulty": "Easy",
            "topic": "Time and Work",
            "option_a": "10 minutes",
            "option_b": "12 minutes",
            "option_c": "15 minutes",
            "option_d": "25 minutes",
            "correct_answer": "B",
            "explanation": "Combined work = 1/20 + 1/30 = 1/12. Time = 12 minutes.",
            "xp_reward": 10
        },
        {
            "title": "Tank with Additional Taps",
            "description": "A tap fills a tank in 6 hours. After half is filled, 3 more similar taps open. Total time to fill completely?",
            "difficulty": "Medium",
            "topic": "Time and Work",
            "option_a": "3 hrs 15 min",
            "option_b": "3 hrs 45 min",
            "option_c": "4 hrs",
            "option_d": "4 hrs 15 min",
            "correct_answer": "B",
            "explanation": "Half filled in 3 hrs. 4 taps fill remaining 1/2 in (1/2)/(2/3) = 3/4 hr = 45 min. Total = 3:45.",
            "xp_reward": 15
        },
        {
            "title": "Tank with Leak",
            "description": "A pump fills tank in 2 hours. With leak it takes 2 hrs 20 min. Leak empties tank in:",
            "difficulty": "Medium",
            "topic": "Time and Work",
            "option_a": "14 hours",
            "option_b": "12 hours",
            "option_c": "10 hours",
            "option_d": "8 hours",
            "correct_answer": "A",
            "explanation": "Pump work = 1/2. With leak = 3/7. Leak work = 1/2 - 3/7 = 1/14. Leak empties in 14 hours.",
            "xp_reward": 15
        },
        # HCF and LCM
        {
            "title": "HCF of Two Numbers",
            "description": "Find the Highest Common Factor (HCF) of 72 and 90.",
            "difficulty": "Easy",
            "topic": "Number System",
            "option_a": "9",
            "option_b": "12",
            "option_c": "18",
            "option_d": "36",
            "correct_answer": "C",
            "explanation": "72 = 2³ × 3². 90 = 2 × 3² × 5. HCF = 2 × 9 = 18.",
            "xp_reward": 10
        },
        {
            "title": "LCM of Three Numbers",
            "description": "Find the Lowest Common Multiple (LCM) of 24, 36, and 40.",
            "difficulty": "Easy",
            "topic": "Number System",
            "option_a": "120",
            "option_b": "240",
            "option_c": "360",
            "option_d": "480",
            "correct_answer": "C",
            "explanation": "LCM = 2³ × 3² × 5 = 8 × 9 × 5 = 360.",
            "xp_reward": 10
        },
        {
            "title": "HCF and LCM Relation",
            "description": "HCF of two numbers is 11 and LCM is 693. If one number is 77, find the other.",
            "difficulty": "Easy",
            "topic": "Number System",
            "option_a": "66",
            "option_b": "99",
            "option_c": "88",
            "option_d": "121",
            "correct_answer": "B",
            "explanation": "Product = HCF × LCM. 77 × x = 11 × 693. x = 99.",
            "xp_reward": 10
        },
        # Profit and Loss
        {
            "title": "Cost Price Calculation",
            "description": "A shopkeeper sells for Rs. 540 with 20% profit. What is the cost price?",
            "difficulty": "Easy",
            "topic": "Profit and Loss",
            "option_a": "Rs. 450",
            "option_b": "Rs. 480",
            "option_c": "Rs. 500",
            "option_d": "Rs. 440",
            "correct_answer": "A",
            "explanation": "CP = SP × (100/(100+Profit%)) = 540 × (100/120) = 450.",
            "xp_reward": 10
        },
        {
            "title": "Successive Discounts",
            "description": "MP is Rs. 1600. After two discounts (first 10%), sold for Rs. 1152. What is second discount?",
            "difficulty": "Medium",
            "topic": "Profit and Loss",
            "option_a": "15%",
            "option_b": "20%",
            "option_c": "25%",
            "option_d": "30%",
            "correct_answer": "B",
            "explanation": "After first discount = 1440. Second discount = (1440-1152)/1440 × 100 = 20%.",
            "xp_reward": 15
        },
        # Percentages
        {
            "title": "Price and Consumption Change",
            "description": "Price decreases 20%, consumption increases 20%. Change in expenditure?",
            "difficulty": "Easy",
            "topic": "Percentages",
            "option_a": "4% increase",
            "option_b": "4% decrease",
            "option_c": "8% increase",
            "option_d": "No change",
            "correct_answer": "B",
            "explanation": "New expenditure = 0.8 × 1.2 = 0.96. This is 4% decrease.",
            "xp_reward": 10
        },
        {
            "title": "Salary Comparison",
            "description": "A's salary is 50% more than B's. By what percent is B's salary less than A's?",
            "difficulty": "Easy",
            "topic": "Percentages",
            "option_a": "50%",
            "option_b": "33.33%",
            "option_c": "25%",
            "option_d": "40%",
            "correct_answer": "B",
            "explanation": "B=100, A=150. Difference = 50. (50/150) × 100 = 33.33%.",
            "xp_reward": 10
        },
        # Geometry
        {
            "title": "Pythagorean Theorem",
            "description": "In right triangle ABC, AB = 8 cm and BC = 15 cm. Find hypotenuse AC.",
            "difficulty": "Easy",
            "topic": "Geometry",
            "option_a": "16 cm",
            "option_b": "17 cm",
            "option_c": "18 cm",
            "option_d": "20 cm",
            "correct_answer": "B",
            "explanation": "AC² = 8² + 15² = 64 + 225 = 289. AC = 17 cm.",
            "xp_reward": 10
        },
        {
            "title": "Circle Circumference",
            "description": "Circumference of circle with diameter 28 cm? (Use π = 22/7)",
            "difficulty": "Easy",
            "topic": "Geometry",
            "option_a": "44 cm",
            "option_b": "88 cm",
            "option_c": "66 cm",
            "option_d": "110 cm",
            "correct_answer": "B",
            "explanation": "Circumference = πd = (22/7) × 28 = 88 cm.",
            "xp_reward": 10
        },
        # Set Theory
        {
            "title": "Set Operations",
            "description": "In 50 students, 30 like Math, 25 like Science, 10 like both. How many like neither?",
            "difficulty": "Easy",
            "topic": "Set Theory",
            "option_a": "5",
            "option_b": "10",
            "option_c": "15",
            "option_d": "0",
            "correct_answer": "A",
            "explanation": "n(M ∪ S) = 30 + 25 - 10 = 45. Neither = 50 - 45 = 5.",
            "xp_reward": 10
        },
        # Series
        {
            "title": "Letter Series",
            "description": "Find next in series: A, C, F, J, O, ?",
            "difficulty": "Easy",
            "topic": "Series",
            "option_a": "U",
            "option_b": "V",
            "option_c": "T",
            "option_d": "S",
            "correct_answer": "A",
            "explanation": "Positions: 1, 3, 6, 10, 15. Differences: +2, +3, +4, +5. Next: +6. 15+6=21=U.",
            "xp_reward": 10
        },
        {
            "title": "Prime Number Squares",
            "description": "Find next: 4, 9, 25, 49, 121, ?",
            "difficulty": "Easy",
            "topic": "Series",
            "option_a": "144",
            "option_b": "169",
            "option_c": "196",
            "option_d": "100",
            "correct_answer": "B",
            "explanation": "Squares of primes: 2², 3², 5², 7², 11². Next prime is 13. 13² = 169.",
            "xp_reward": 10
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
    print(f"\n✅ Quantitative questions seeding complete! Total: {len(questions_data)} questions")


def main():
    print("🌱 Starting quantitative questions seeding...\n")
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        seed_quantitative_questions(db)
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
