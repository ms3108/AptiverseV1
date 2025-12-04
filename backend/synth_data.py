import google.generativeai as genai
import json
import random
import time
import os
from tqdm import tqdm  # For the progress bar

# --- CONFIGURATION ---
API_KEY = "AIzaSyAKpI_hQgfh_r7pFw2nGpqYuNTftyiP9lE"
TARGET_COUNT = 2000
OUTPUT_FILE = "aptitude_dataset.jsonl"

# Topics mapped to categories for Aptiverse
TOPIC_CATEGORIES = {
    # Quantitative
    "Time and Work": "Quantitative",
    "Pipes and Cisterns": "Quantitative",
    "Probability": "Quantitative",
    "Permutations and Combinations": "Quantitative",
    "Geometry": "Quantitative",
    "Mensuration": "Quantitative",
    "Profit and Loss": "Quantitative",
    "Simple and Compound Interest": "Quantitative",
    "Speed, Time and Distance": "Quantitative",
    "Trains": "Quantitative",
    "Boats and Streams": "Quantitative",
    "Percentages": "Quantitative",
    "Ratio and Proportion": "Quantitative",
    "Mixtures and Allegations": "Quantitative",
    "Number Systems": "Quantitative",
    "Averages": "Quantitative",
    "Ages": "Quantitative",
    # Logical
    "Blood Relations": "Logical",
    "Coding-Decoding": "Logical",
    "Direction Sense": "Logical",
    "Series Completion": "Logical",
    "Analogies": "Logical",
    "Syllogisms": "Logical",
    "Ranking and Ordering": "Logical",
    "Puzzles": "Logical",
    "Statement and Conclusions": "Logical",
    "Seating Arrangement": "Logical",
    # Linguistic
    "Synonyms": "Linguistic",
    "Antonyms": "Linguistic",
    "Sentence Correction": "Linguistic",
    "Reading Comprehension": "Linguistic",
    "Fill in the Blanks": "Linguistic",
    "Idioms and Phrases": "Linguistic",
    "One Word Substitution": "Linguistic",
    "Para Jumbles": "Linguistic",
}

TOPICS = list(TOPIC_CATEGORIES.keys())
DIFFICULTY = ["Easy", "Medium", "Hard"]
DIFFICULTY_XP = {"Easy": 10, "Medium": 20, "Hard": 30}

# --- SETUP GEMINI ---
genai.configure(api_key=API_KEY)

# We use 'gemini-1.5-flash' for speed and low cost.
# The 'response_mime_type' forces strict JSON output.
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config={
        "temperature": 0.9,  # High creativity to avoid duplicates
        "response_mime_type": "application/json",
    }
)

def generate_batch(batch_size=10):
    """
    Generates a batch of questions in the Aptiverse database format.
    """
    selected_topic = random.choice(TOPICS)
    selected_diff = random.choice(DIFFICULTY)
    category = TOPIC_CATEGORIES[selected_topic]
    xp_reward = DIFFICULTY_XP[selected_diff]
    
    # Prompt Engineering for Aptiverse Question Format
    prompt = f"""
    You are an expert Aptitude Trainer. Generate {batch_size} unique, distinct, and high-quality aptitude questions on the topic '{selected_topic}' with '{selected_diff}' difficulty.
    
    CRITICAL RULES:
    1. Return a JSON List of objects.
    2. Each object must follow the EXACT structure below.
    3. Ensure the math/logic is 100% correct.
    4. The "correct_answer" must be exactly "A", "B", "C", or "D".
    5. Options should be distinct and plausible.
    6. The explanation should be detailed and step-by-step.
    
    Expected JSON Structure for each item:
    {{
        "title": "A short descriptive title for the question (5-10 words)",
        "description": "The full question text with all necessary details",
        "difficulty": "{selected_diff}",
        "category": "{category}",
        "topic": "{selected_topic}",
        "option_a": "First option text",
        "option_b": "Second option text",
        "option_c": "Third option text",
        "option_d": "Fourth option text",
        "correct_answer": "A or B or C or D (single letter)",
        "explanation": "Detailed step-by-step solution and reasoning",
        "xp_reward": {xp_reward}
    }}
    
    Generate exactly {batch_size} questions as a JSON array.
    """
    
    try:
        response = model.generate_content(prompt)
        # Parse the JSON response
        data = json.loads(response.text)
        
        # Validation: Ensure it's a list
        if isinstance(data, list):
            # Validate and clean each question
            valid_questions = []
            for q in data:
                # Ensure correct_answer is uppercase single letter
                if "correct_answer" in q:
                    q["correct_answer"] = q["correct_answer"].upper().strip()
                    if q["correct_answer"] not in ["A", "B", "C", "D"]:
                        # Try to extract letter from response like "Option A"
                        for letter in ["A", "B", "C", "D"]:
                            if letter in q["correct_answer"]:
                                q["correct_answer"] = letter
                                break
                
                # Ensure all required fields exist
                required_fields = ["title", "description", "difficulty", "category", "topic",
                                   "option_a", "option_b", "option_c", "option_d", 
                                   "correct_answer", "explanation", "xp_reward"]
                if all(field in q for field in required_fields):
                    valid_questions.append(q)
            
            return valid_questions
        else:
            # Sometimes model returns a single object instead of a list
            return [data] if isinstance(data, dict) else []
            
    except Exception as e:
        print(f"\n⚠️ Error generating batch: {e}")
        time.sleep(2)  # Backoff for rate limits
        return []

# --- MAIN LOOP ---
def main():
    if os.path.exists(OUTPUT_FILE):
        print(f"ℹ️  Appending to existing file: {OUTPUT_FILE}")
    
    generated_count = 0
    
    # Check if file exists to resume count (optional logic)
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            generated_count = sum(1 for _ in f)
    
    print(f"🚀 Starting generation. Target: {TARGET_COUNT} examples.")
    print(f"📊 Categories: Quantitative, Logical, Linguistic")
    print(f"📝 Topics: {len(TOPICS)} different topics")
    print(f"Current progress: {generated_count}/{TARGET_COUNT}")

    # Progress bar loop
    with tqdm(total=TARGET_COUNT, initial=generated_count, desc="Generating") as pbar:
        while generated_count < TARGET_COUNT:
            # Generate 5 at a time to be faster
            batch = generate_batch(batch_size=5)
            
            if not batch:
                continue
                
            with open(OUTPUT_FILE, "a") as f:
                for item in batch:
                    # Write as JSONL (one JSON object per line)
                    f.write(json.dumps(item) + "\n")
                    generated_count += 1
                    pbar.update(1)
                    
                    if generated_count >= TARGET_COUNT:
                        break
            
            # Respect Rate Limits (Free tier is generous but good to be safe)
            time.sleep(1) 

    print(f"\n✅ SUCCESS! Generated {generated_count} questions in '{OUTPUT_FILE}'")
    print("\n📋 Format ready for Aptiverse database import:")
    print("   - title, description, difficulty, category, topic")
    print("   - option_a, option_b, option_c, option_d")
    print("   - correct_answer (A/B/C/D), explanation, xp_reward")

if __name__ == "__main__":
    main()