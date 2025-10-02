"""
Seed Profit and Loss questions to the database
"""
from sqlalchemy.orm import Session
from database import get_db, engine
import models

# Create all tables
models.Base.metadata.create_all(bind=engine)

profit_loss_questions = [
    {
        "title": "Profit/Loss Calculation - Article Sale",
        "description": "A man sold an article at a loss of 20%. If he has sold that article for Rs. 12 more he would have gained 10%. Find the cost price of that article.",
        "difficulty": "Medium",
        "category": "Quants",
        "topic": "Profit and Loss",
        "sub_topic": "Cost Price Calculation",
        "option_a": "Rs. 60",
        "option_b": "Rs. 40",
        "option_c": "Rs. 30",
        "option_d": "Rs. 22",
        "correct_answer": "B",
        "explanation": "Let cost price = x. At 20% loss, SP = 0.8x. If sold at Rs. 12 more with 10% gain: (0.8x + 12 - x)/x = 10/100. Solving: 12 - 0.2x = 0.1x, therefore 12 = 0.3x, x = 40.",
        "xp_reward": 15
    },
    {
        "title": "Discount and Profit Percentage",
        "description": "If on an item a company gives 25% discount, they earn 25% profit. If they now give 10% discount then what is the profit percentage?",
        "difficulty": "Medium",
        "category": "Quants",
        "topic": "Profit and Loss",
        "sub_topic": "Discount Problems",
        "option_a": "40%",
        "option_b": "55%",
        "option_c": "35%",
        "option_d": "30%",
        "correct_answer": "D",
        "explanation": "Let cost be Rs x. After 25% discount: 0.75x gives 25% profit. After 10% discount: 0.90x. Using the relationship: 0.90x gives (25 × 0.90x)/0.75x = 30% profit.",
        "xp_reward": 15
    },
    {
        "title": "False Weight Profit Calculation",
        "description": "Shopkeeper bought a product for Rs 1000 per kg and is selling that at the same price. However he uses a weighing scale that gives scale of 1kg for every 800gms. What is his profit?",
        "difficulty": "Easy",
        "category": "Quants",
        "topic": "Profit and Loss",
        "sub_topic": "False Weight",
        "option_a": "56% profit",
        "option_b": "55% loss",
        "option_c": "25% profit",
        "option_d": "None of these",
        "correct_answer": "C",
        "explanation": "Gain% = [(True weight - False weight)/False weight] × 100 = [(1000 - 800)/800] × 100 = (200/800) × 100 = 25% profit.",
        "xp_reward": 10
    },
    {
        "title": "Simple Profit Percentage",
        "description": "A shopkeeper bought a watch for Rs. 400 and sold it for Rs. 500. What is his profit percentage?",
        "difficulty": "Easy",
        "category": "Quants",
        "topic": "Profit and Loss",
        "sub_topic": "Basic Profit Calculation",
        "option_a": "35%",
        "option_b": "25%",
        "option_c": "30%",
        "option_d": "20%",
        "correct_answer": "B",
        "explanation": "Cost price = 400, Selling price = 500. Profit = 500 - 400 = 100. Profit% = (Total Profit/Cost Price) × 100 = (100/400) × 100 = 25%.",
        "xp_reward": 10
    },
    {
        "title": "Complex Cost Price Problem",
        "description": "A person bought an article and sold it at a loss of 10%. If he had bought it for 20% less and sold it for Rs. 55 more he would have had a profit of 40%. The cost price of the article is:",
        "difficulty": "Hard",
        "category": "Quants",
        "topic": "Profit and Loss",
        "sub_topic": "Cost Price with Conditions",
        "option_a": "125",
        "option_b": "150.5",
        "option_c": "112.5",
        "option_d": "250",
        "correct_answer": "D",
        "explanation": "Let CP = x. Sold at 10% loss = 9x/10. Bought 20% less = 4x/5. With 40% profit on 4x/5 = 56x/50. Equation: 56x/50 - 9x/10 = 55. Solving: (560x - 450x)/500 = 55, 110x = 27500, x = 250.",
        "xp_reward": 20
    },
    {
        "title": "Discount and Profit - Repeat Scenario",
        "description": "If on an item a company gives 25% discount, they earn 25% profit. If they now give 10% discount then what is the profit percentage?",
        "difficulty": "Medium",
        "category": "Quants",
        "topic": "Profit and Loss",
        "sub_topic": "Discount Problems",
        "option_a": "40%",
        "option_b": "55%",
        "option_c": "45%",
        "option_d": "30%",
        "correct_answer": "D",
        "explanation": "Let cost be Rs x. After 25% discount: 0.75x gives 25% profit. After 10% discount: 0.90x. From the relationship: 0.90x gives (25 × 0.90x)/0.75x = 30% profit.",
        "xp_reward": 15
    },
    {
        "title": "Cow and Horse Purchase",
        "description": "A cow and a horse are bought for Rs 200000. The cow is sold at profit of 20% and the horse at a loss of 10%. The overall gain is Rs 4000. The cost price of cow is?",
        "difficulty": "Hard",
        "category": "Quants",
        "topic": "Profit and Loss",
        "sub_topic": "Combined Profit/Loss",
        "option_a": "36000",
        "option_b": "80000",
        "option_c": "54000",
        "option_d": "45000",
        "correct_answer": "B",
        "explanation": "Let cow cost = c, horse cost = h. c + h = 200000. SP = (6c/5) + (9h/10) = 204000. Solving: 12c + 9h = 2040000 and 12c + 12h = 2400000. Therefore 3h = 360000, h = 120000, c = 80000.",
        "xp_reward": 20
    },
    {
        "title": "Wheat Mixture and Selling Price",
        "description": "A merchant buys 20 kg of wheat at Rs. 30 per kg and 40 kg wheat at Rs. 25 per kg. He mixed them and sells one third of the mixture at Rs. 26 per kg. The price at which the merchant should sell the remaining mixture, so that he may earn a profit of 25% in his whole outlay is?",
        "difficulty": "Hard",
        "category": "Quants",
        "topic": "Profit and Loss",
        "sub_topic": "Mixture Problems",
        "option_a": "Rs 30",
        "option_b": "Rs 36",
        "option_c": "Rs 37",
        "option_d": "Rs 40",
        "correct_answer": "C",
        "explanation": "Total CP = (20×30) + (40×25) = 1600. For 25% profit, total SP = 1600 × (5/4) = 2000. Total mixture = 60kg. One third (20kg) sold at 26 = 520. Remaining 40kg must sell at: (2000-520)/40 = 37.",
        "xp_reward": 20
    }
]

def seed_profit_loss_questions():
    db = next(get_db())
    
    print("🌱 Seeding Profit and Loss questions...")
    print(f"Adding {len(profit_loss_questions)} questions...")
    
    added_count = 0
    skipped_count = 0
    
    for q_data in profit_loss_questions:
        # Check if question already exists (by title)
        existing = db.query(models.Question).filter(
            models.Question.title == q_data["title"]
        ).first()
        
        if existing:
            print(f"⏭️  Skipped (already exists): {q_data['title'][:50]}...")
            skipped_count += 1
            continue
        
        question = models.Question(**q_data)
        db.add(question)
        added_count += 1
        print(f"✅ Added: {q_data['title'][:60]}...")
    
    db.commit()
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Added: {added_count} questions")
    print(f"   ⏭️  Skipped: {skipped_count} questions")
    print(f"   📈 Total: {len(profit_loss_questions)} questions processed")
    
    # Count total Profit and Loss questions
    total_pl = db.query(models.Question).filter(
        models.Question.topic == "Profit and Loss"
    ).count()
    print(f"\n🎯 Total 'Profit and Loss' questions in database: {total_pl}")
    
    db.close()

if __name__ == "__main__":
    try:
        seed_profit_loss_questions()
        print("\n✅ Seeding completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
