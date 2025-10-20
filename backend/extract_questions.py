"""
Script to extract all valid question dictionaries from seed_data.py
"""
import re
import ast

# Read the file
with open('seed_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all question dictionaries by looking for patterns
# Each question starts with { and has certain fields
questions = []

# Try to find all dict-like structures
pattern = r'\{[^{}]*"title"[^{}]*"description"[^{}]*"difficulty"[^{}]*\}'
matches = re.findall(pattern, content, re.DOTALL)

print(f"Found {len(matches)} potential question dictionaries")

# Try to parse each match
for i, match in enumerate(matches):
    try:
        # Try to evaluate the string as a Python dict
        q = ast.literal_eval(match)
        questions.append(q)
        print(f"✅ Question {i+1}: {q.get('title', 'Unknown')[:50]}")
    except:
        print(f"❌ Failed to parse question {i+1}")

print(f"\nTotal valid questions extracted: {len(questions)}")

# Save to new file
with open('extracted_questions.py', 'w', encoding='utf-8') as f:
    f.write('questions_data = [\n')
    for q in questions:
        f.write('    ' + repr(q) + ',\n')
    f.write(']\n')

print(f"Saved {len(questions)} questions to extracted_questions.py")
