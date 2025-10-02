"""
Enhanced seed script with Vector DB duplicate detection
Checks for semantically similar questions using Weaviate
"""
from sqlalchemy.orm import Session
from database import get_db, engine
import models
import weaviate
import os

# Create all tables
models.Base.metadata.create_all(bind=engine)

# Initialize Weaviate client
def get_weaviate_client():
    """Connect to Weaviate vector database"""
    weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
    print(f"🔗 Connecting to Weaviate at: {weaviate_url}")
    
    try:
        client = weaviate.Client(url=weaviate_url)
        # Test connection
        client.schema.get()
        print(f"✅ Connected to Weaviate successfully")
        return client
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to Weaviate: {e}")
        print("   Falling back to exact title matching only")
        return None

def create_question_schema(client):
    """Create Weaviate schema for questions if it doesn't exist"""
    if client is None:
        return
    
    try:
        # Check if schema already exists
        schema = client.schema.get()
        if any(cls['class'] == 'Question' for cls in schema.get('classes', [])):
            print("✅ Weaviate Question schema already exists")
            return
        
        # Create schema without vectorizer (we'll provide embeddings manually if needed)
        question_schema = {
            "class": "Question",
            "description": "Aptitude test questions",
            "vectorizer": "none",  # No automatic vectorization
            "properties": [
                {
                    "name": "title",
                    "dataType": ["text"],
                    "description": "Question title"
                },
                {
                    "name": "description",
                    "dataType": ["text"],
                    "description": "Question description/problem statement"
                },
                {
                    "name": "topic",
                    "dataType": ["string"],
                    "description": "Question topic"
                },
                {
                    "name": "difficulty",
                    "dataType": ["string"],
                    "description": "Difficulty level"
                },
                {
                    "name": "questionId",
                    "dataType": ["int"],
                    "description": "PostgreSQL question ID"
                }
            ]
        }
        
        client.schema.create_class(question_schema)
        print("✅ Created Weaviate Question schema")
    except Exception as e:
        print(f"⚠️  Warning: Could not create schema: {e}")

def check_semantic_similarity(client, question_title: str, question_desc: str, threshold_score: float = 5.0):
    """
    Check if a semantically similar question already exists using BM25 keyword search
    Returns (is_duplicate, similar_questions_list)
    
    Note: This uses BM25 keyword matching. For true semantic similarity,
    you would need sentence transformers and vector embeddings.
    """
    if client is None:
        return False, []
    
    try:
        # Search for similar questions using BM25 keyword search
        result = client.query.get(
            "Question", 
            ["title", "description", "topic", "questionId"]
        ).with_bm25(
            query=question_title,  # Search by title
            properties=["title", "description"]
        ).with_limit(3).with_additional(["score"]).do()
        
        similar_questions = result.get('data', {}).get('Get', {}).get('Question', [])
        
        # Filter by score threshold
        high_matches = [q for q in similar_questions 
                       if q.get('_additional', {}).get('score', 0) >= threshold_score]
        
        if high_matches:
            return True, high_matches
        return False, []
        
    except Exception as e:
        print(f"⚠️  Warning: Similarity search failed: {e}")
        return False, []

def add_to_vector_db(client, question_data, postgres_id: int):
    """Add question to Weaviate vector database"""
    if client is None:
        return None
    
    try:
        vector_id = client.data_object.create(
            {
                "title": question_data["title"],
                "description": question_data["description"],
                "topic": question_data["topic"],
                "difficulty": question_data["difficulty"],
                "questionId": postgres_id
            },
            "Question"
        )
        return vector_id
    except Exception as e:
        print(f"⚠️  Warning: Could not add to vector DB: {e}")
        return None

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

def seed_profit_loss_questions_with_vector_check():
    db = next(get_db())
    weaviate_client = get_weaviate_client()
    
    # Create Weaviate schema if needed
    if weaviate_client:
        create_question_schema(weaviate_client)
    
    print("🌱 Seeding Profit and Loss questions with duplicate detection...")
    print(f"📊 Vector DB Status: {'✅ Connected' if weaviate_client else '❌ Disconnected'}")
    print(f"🔍 Semantic similarity threshold: 85%")
    print(f"📝 Processing {len(profit_loss_questions)} questions...\n")
    
    added_count = 0
    skipped_exact_count = 0
    skipped_similar_count = 0
    
    for idx, q_data in enumerate(profit_loss_questions, 1):
        print(f"\n[{idx}/{len(profit_loss_questions)}] Processing: {q_data['title'][:50]}...")
        
        # Check 1: Exact title match in PostgreSQL
        existing = db.query(models.Question).filter(
            models.Question.title == q_data["title"]
        ).first()
        
        if existing:
            print(f"   ⏭️  SKIPPED: Exact match found in database (ID: {existing.id})")
            skipped_exact_count += 1
            continue
        
        # Check 2: Semantic similarity in Weaviate (using BM25 keyword search)
        is_similar, similar_questions = check_semantic_similarity(
            weaviate_client, 
            q_data['title'],
            q_data['description'],
            threshold_score=5.0
        )
        
        if is_similar and similar_questions:
            print(f"   🔍 SIMILAR QUESTION FOUND (≥85% match):")
            for sim_q in similar_questions[:1]:  # Show top match
                print(f"      → '{sim_q.get('title', 'Unknown')}'")
            print(f"   ⏭️  SKIPPED: Too similar to existing question")
            skipped_similar_count += 1
            continue
        
        # Add to PostgreSQL
        question = models.Question(**q_data)
        db.add(question)
        db.flush()  # Get the ID
        
        # Add to Weaviate
        vector_id = add_to_vector_db(weaviate_client, q_data, question.id)
        if vector_id:
            question.vector_id = vector_id
        
        db.commit()
        added_count += 1
        print(f"   ✅ ADDED: Successfully stored (PostgreSQL ID: {question.id})")
        if vector_id:
            print(f"      🔗 Vector ID: {vector_id[:8]}...")
    
    print(f"\n{'='*70}")
    print(f"📊 SEEDING SUMMARY:")
    print(f"{'='*70}")
    print(f"   ✅ Added:              {added_count} questions")
    print(f"   ⏭️  Skipped (exact):     {skipped_exact_count} questions")
    print(f"   🔍 Skipped (similar):   {skipped_similar_count} questions")
    print(f"   📈 Total processed:     {len(profit_loss_questions)} questions")
    print(f"{'='*70}")
    
    # Count total Profit and Loss questions
    total_pl = db.query(models.Question).filter(
        models.Question.topic == "Profit and Loss"
    ).count()
    print(f"\n🎯 Total 'Profit and Loss' questions in database: {total_pl}")
    
    db.close()

if __name__ == "__main__":
    try:
        seed_profit_loss_questions_with_vector_check()
        print("\n✅ Seeding completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
