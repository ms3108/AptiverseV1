"""Fix categories for existing questions"""
from database import SessionLocal
from models import Question

# Map topics to categories
TOPIC_TO_CATEGORY = {
    # Quants
    "Averages": "Quants",
    "Percentages": "Quants",
    "Profit and Loss": "Quants",
    "Simple Interest": "Quants",
    "Compound Interest": "Quants",
    "Ratio and Proportion": "Quants",
    "Time and Work": "Quants",
    "Time and Distance": "Quants",
    "Algebra": "Quants",
    "Numbers": "Quants",
    "Geometry": "Quants",
    "Mensuration": "Quants",
    "Probability": "Quants",
    "Permutation and Combination": "Quants",
    
    # Logical
    "Arrays": "Logical",
    "Strings": "Logical",
    "Linked Lists": "Logical",
    "Trees": "Logical",
    "Graphs": "Logical",
    "Dynamic Programming": "Logical",
    "Sorting and Searching": "Logical",
    "Stacks and Queues": "Logical",
    "Heaps": "Logical",
    "Bit Manipulation": "Logical",
    "Greedy Algorithms": "Logical",
    "Backtracking": "Logical",
    "Hashing": "Logical",
    "Two Pointers": "Logical",
    "Sliding Window": "Logical",
    "Matrix": "Logical",
    "Recursion": "Logical",
    "Logic": "Logical",
    "Puzzles": "Logical",
    "Pattern Recognition": "Logical",
    
    # Language
    "Synonyms": "Language",
    "Antonyms": "Language",
    "Reading Comprehension": "Language",
    "Sentence Completion": "Language",
    "Grammar": "Language",
    "Vocabulary": "Language",
    "Verbal Reasoning": "Language",
    "Analogies": "Language",
}

def fix_categories():
    db = SessionLocal()
    
    questions = db.query(Question).all()
    updated = 0
    
    for q in questions:
        if q.category is None or q.category == "":
            # Try to find category from topic
            category = TOPIC_TO_CATEGORY.get(q.topic)
            
            # If not found, try to guess from topic name
            if not category:
                topic_lower = q.topic.lower()
                if any(x in topic_lower for x in ['array', 'string', 'tree', 'graph', 'stack', 'queue', 'heap', 'sort', 'search', 'dynamic', 'algorithm', 'hash', 'matrix', 'linked', 'bit', 'greedy', 'backtrack', 'pointer', 'window', 'recursion', 'logic', 'puzzle', 'pattern']):
                    category = "Logical"
                elif any(x in topic_lower for x in ['synonym', 'antonym', 'reading', 'grammar', 'vocabulary', 'verbal', 'sentence', 'comprehension', 'analogy']):
                    category = "Language"
                else:
                    category = "Quants"  # Default to Quants
            
            q.category = category
            updated += 1
            print(f"Updated: {q.title} -> {category}")
    
    db.commit()
    print(f"\n✅ Fixed {updated} questions with categories")
    
    # Show summary
    cats = db.query(Question.category).distinct().all()
    print(f"Unique categories now: {[c[0] for c in cats]}")
    
    db.close()

if __name__ == "__main__":
    fix_categories()
