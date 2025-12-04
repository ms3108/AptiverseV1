"""Update categories to Quantitative, Logical, Linguistic with proper topics"""
from database import SessionLocal
from models import Question

# Map existing topics to new categories
TOPIC_TO_CATEGORY = {
    # Quantitative Aptitude Topics
    "Averages": "Quantitative",
    "Percentages": "Quantitative",
    "Profit and Loss": "Quantitative",
    "Simple Interest": "Quantitative",
    "Compound Interest": "Quantitative",
    "Ratio and Proportion": "Quantitative",
    "Time and Work": "Quantitative",
    "Time and Distance": "Quantitative",
    "Mixtures and Alligation": "Quantitative",
    "Numbers": "Quantitative",
    "Number System": "Quantitative",
    "Algebra": "Quantitative",
    "Geometry": "Quantitative",
    "Mensuration": "Quantitative",
    "Probability": "Quantitative",
    "Permutation and Combination": "Quantitative",
    "Data Interpretation": "Quantitative",
    "Age Problems": "Quantitative",
    "Partnership": "Quantitative",
    "Pipes and Cisterns": "Quantitative",
    "Boats and Streams": "Quantitative",
    "Trains": "Quantitative",
    "Clocks": "Quantitative",
    "Calendars": "Quantitative",
    
    # Logical Reasoning Topics
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
    "Blood Relations": "Logical",
    "Coding-Decoding": "Logical",
    "Direction Sense": "Logical",
    "Syllogisms": "Logical",
    "Seating Arrangement": "Logical",
    "Puzzles": "Logical",
    "Pattern Recognition": "Logical",
    "Series Completion": "Logical",
    "Analogies": "Logical",
    "Statement and Conclusions": "Logical",
    "Statement and Assumptions": "Logical",
    "Cause and Effect": "Logical",
    "Critical Reasoning": "Logical",
    "Data Sufficiency": "Logical",
    "Input-Output": "Logical",
    "Ranking and Order": "Logical",
    "Inequalities": "Logical",
    "Logic": "Logical",
    
    # Linguistic/Verbal Topics
    "Synonyms": "Linguistic",
    "Antonyms": "Linguistic",
    "Reading Comprehension": "Linguistic",
    "Sentence Completion": "Linguistic",
    "Grammar": "Linguistic",
    "Vocabulary": "Linguistic",
    "Verbal Reasoning": "Linguistic",
    "Para Jumbles": "Linguistic",
    "Fill in the Blanks": "Linguistic",
    "Error Spotting": "Linguistic",
    "Sentence Improvement": "Linguistic",
    "Cloze Test": "Linguistic",
    "Idioms and Phrases": "Linguistic",
    "One Word Substitution": "Linguistic",
    "Spellings": "Linguistic",
}

def fix_categories():
    db = SessionLocal()
    
    questions = db.query(Question).all()
    updated = 0
    
    for q in questions:
        # Determine the correct category
        category = TOPIC_TO_CATEGORY.get(q.topic)
        
        # If not found in mapping, try to guess
        if not category:
            topic_lower = q.topic.lower() if q.topic else ""
            
            # Logical reasoning patterns
            if any(x in topic_lower for x in ['array', 'string', 'tree', 'graph', 'stack', 'queue', 
                'heap', 'sort', 'search', 'dynamic', 'algorithm', 'hash', 'matrix', 'linked', 
                'bit', 'greedy', 'backtrack', 'pointer', 'window', 'recursion', 'logic', 'puzzle', 
                'pattern', 'blood', 'coding', 'direction', 'syllog', 'seating', 'series', 
                'analog', 'statement', 'critical', 'ranking', 'inequal', 'input', 'output']):
                category = "Logical"
            # Linguistic patterns
            elif any(x in topic_lower for x in ['synonym', 'antonym', 'reading', 'grammar', 
                'vocabulary', 'verbal', 'sentence', 'comprehension', 'para', 'fill', 'blank',
                'error', 'cloze', 'idiom', 'phrase', 'spelling', 'word']):
                category = "Linguistic"
            # Default to Quantitative
            else:
                category = "Quantitative"
        
        if q.category != category:
            old_cat = q.category
            q.category = category
            updated += 1
            print(f"Updated: {q.title} [{q.topic}]: {old_cat} -> {category}")
    
    db.commit()
    print(f"\n✅ Updated {updated} questions")
    
    # Show summary
    print("\n📊 Category Summary:")
    for cat in ["Quantitative", "Logical", "Linguistic"]:
        count = db.query(Question).filter(Question.category == cat).count()
        topics = db.query(Question.topic).filter(Question.category == cat).distinct().all()
        print(f"\n{cat}: {count} questions")
        print(f"  Topics: {[t[0] for t in topics]}")
    
    db.close()

if __name__ == "__main__":
    fix_categories()
