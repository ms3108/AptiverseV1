"""
Demo script to test duplicate detection with Vector DB
Shows how similar questions are detected even with different wording
"""
from sqlalchemy.orm import Session
from database import get_db, engine
import models
import weaviate
import os

models.Base.metadata.create_all(bind=engine)

def get_weaviate_client():
    weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
    try:
        client = weaviate.Client(url=weaviate_url)
        client.schema.get()
        return client
    except Exception as e:
        print(f"❌ Could not connect to Weaviate: {e}")
        return None

def add_existing_questions_to_vector_db():
    """Add existing questions from PostgreSQL to Weaviate for comparison"""
    db = next(get_db())
    client = get_weaviate_client()
    
    if not client:
        return
    
    print("🔄 Syncing existing questions to Weaviate...")
    
    # Get all Profit and Loss questions
    questions = db.query(models.Question).filter(
        models.Question.topic == "Profit and Loss"
    ).all()
    
    synced = 0
    for q in questions:
        if not q.vector_id:  # Only sync if not already in Weaviate
            try:
                vector_id = client.data_object.create(
                    {
                        "title": q.title,
                        "description": q.description,
                        "topic": q.topic,
                        "difficulty": q.difficulty,
                        "questionId": q.id
                    },
                    "Question"
                )
                q.vector_id = vector_id
                synced += 1
            except Exception as e:
                print(f"⚠️  Failed to sync question {q.id}: {e}")
    
    db.commit()
    db.close()
    print(f"✅ Synced {synced} questions to Weaviate\n")

def test_similarity_search(client, title, description):
    """Search for similar questions"""
    print(f"🔍 Searching for similar questions to:")
    print(f"   Title: {title[:60]}...")
    print(f"   Desc:  {description[:60]}...\n")
    
    try:
        result = client.query.get(
            "Question", 
            ["title", "description", "topic", "questionId"]
        ).with_bm25(
            query=title,
            properties=["title", "description"]
        ).with_limit(5).with_additional(["score"]).do()
        
        similar = result.get('data', {}).get('Get', {}).get('Question', [])
        
        if similar:
            print(f"📊 Found {len(similar)} similar questions:\n")
            for idx, q in enumerate(similar, 1):
                score = q.get('_additional', {}).get('score', 0)
                score_value = float(score) if score else 0.0
                print(f"   {idx}. Score: {score_value:.2f}")
                print(f"      Title: {q['title'][:70]}...")
                print(f"      Topic: {q['topic']}")
                if score_value >= 5.0:
                    print(f"      ⚠️  HIGH SIMILARITY - LIKELY DUPLICATE")
                print()
        else:
            print("✅ No similar questions found\n")
            
    except Exception as e:
        print(f"❌ Search failed: {e}\n")

if __name__ == "__main__":
    print("="*70)
    print(" DUPLICATE DETECTION DEMO - Vector DB")
    print("="*70)
    print()
    
    # Sync existing questions
    add_existing_questions_to_vector_db()
    
    client = get_weaviate_client()
    if not client:
        print("❌ Cannot proceed without Weaviate connection")
        exit(1)
    
    print("-" * 70)
    print(" TEST 1: Exact duplicate (same title)")
    print("-" * 70)
    test_similarity_search(
        client,
        "Simple Profit Percentage",
        "A shopkeeper bought a watch for Rs. 400 and sold it for Rs. 500."
    )
    
    print("-" * 70)
    print(" TEST 2: Paraphrased question (similar meaning, different words)")
    print("-" * 70)
    test_similarity_search(
        client,
        "Basic Profit Calculation",
        "A merchant purchased a timepiece for 400 rupees and sold it at 500 rupees."
    )
    
    print("-" * 70)
    print(" TEST 3: Same topic but different problem")
    print("-" * 70)
    test_similarity_search(
        client,
        "Profit Loss on Electronics",
        "A TV was bought for Rs 10000 and sold at 15% profit. Find selling price."
    )
    
    print("-" * 70)
    print(" TEST 4: Completely different topic")
    print("-" * 70)
    test_similarity_search(
        client,
        "Train Speed Problem",
        "A train travels 200 km in 4 hours. What is its speed?"
    )
    
    print("="*70)
    print("✅ Demo completed!")
    print()
    print("💡 KEY INSIGHTS:")
    print("   • Score ≥ 5.0 = High similarity (likely duplicate)")
    print("   • Score 2-5   = Moderate similarity (review recommended)")
    print("   • Score < 2   = Low similarity (probably unique)")
    print("="*70)
