# Question Difficulty Rating System

## 📊 Current System (Manual)

### How Difficulty is Currently Assigned:

Difficulty is **manually set** when questions are added via `seed_data.py`:

```python
{
    "title": "Average of Numbers",
    "difficulty": "Easy",    # <-- Manually assigned
    "xp_reward": 10         # <-- Based on difficulty
}
```

### Current Difficulty Levels:

| Difficulty | XP Reward | Criteria |
|------------|-----------|----------|
| **Easy** | 10 XP | Simple, direct application |
| **Medium** | 15 XP | Multi-step, moderate complexity |
| **Hard** | 20 XP | Complex, advanced concepts |

---

## 🎯 Manual Rating Guidelines

### For Quantitative Aptitude:

**Easy:**
- Direct formula application
- 1-2 calculation steps
- Basic arithmetic
- Example: "Find 20% of 500"

**Medium:**
- 2-3 steps required
- Combination of concepts
- Requires formula knowledge
- Example: "Cost price with successive discounts"

**Hard:**
- 3+ steps or complex logic
- Multiple concepts combined
- Requires strategic thinking
- Example: "Time-speed-distance with multiple travelers"

### For Verbal (Synonyms/Antonyms):

**Easy:**
- Common everyday words
- 5th-8th grade vocabulary
- Example: "Happy" → Joyful

**Medium:**
- College-level vocabulary
- Moderately uncommon words
- Example: "Ephemeral" → Temporary

**Hard:**
- Advanced/rare vocabulary
- GRE/GMAT level words
- Example: "Obfuscate" → Confuse, "Sagacious" → Wise

### For Logical Reasoning:

**Easy:**
- Simple pattern recognition
- 1-2 step logical deductions
- Example: Basic blood relations

**Medium:**
- 2-3 step deductions
- Requires careful analysis
- Example: Seating arrangements

**Hard:**
- Complex multi-step reasoning
- Multiple variables
- Example: Advanced puzzles with constraints

---

## 💡 Proposed: Dynamic Difficulty System

### Concept:
Adjust difficulty automatically based on **actual user performance**:

```python
# After 50+ users attempt a question:
success_rate = (correct_answers / total_attempts) * 100

if success_rate >= 70%:
    difficulty = "Easy"
elif success_rate >= 40%:
    difficulty = "Medium"
else:
    difficulty = "Hard"
```

### Benefits:
✅ Self-correcting (adjusts if question is mis-rated)
✅ Based on real data, not subjective opinion
✅ Accounts for user base skill level
✅ Automatically recalibrates over time

### Factors to Consider:
1. **Success Rate**: % of users who answered correctly
2. **Average Time**: How long users take to answer
3. **User Level**: What level of users are getting it right/wrong
4. **Attempts**: Users who need multiple tries

---

## 🔧 Implementation Options

### Option 1: Periodic Batch Update
Run a script weekly/monthly to recalculate difficulties:

```bash
# Update all question difficulties based on performance
python update_dynamic_difficulty.py
```

### Option 2: Real-Time Adjustment
Update difficulty after each N attempts:

```python
# In backend/main.py after recording answer:
if question.attempt_count >= 50 and question.attempt_count % 10 == 0:
    recalculate_difficulty(question.id)
```

### Option 3: Hybrid System
- Start with manual ratings
- Switch to dynamic after 50+ attempts
- Flag questions with unusual patterns for review

---

## 📈 Adding Performance Tracking

To enable dynamic difficulty, we need to track:

### Database Changes Needed:

```python
# Add to Question model:
class Question(Base):
    # ... existing fields ...
    
    # Performance tracking
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    avg_time_seconds = Column(Float, default=0)
    last_difficulty_update = Column(DateTime, nullable=True)
```

### Track Each Attempt:

```python
# When user answers a question:
question.total_attempts += 1
if is_correct:
    question.correct_attempts += 1

# Update average time
question.avg_time_seconds = (
    (question.avg_time_seconds * (question.total_attempts - 1) + time_taken)
    / question.total_attempts
)
```

---

## 🎮 Gamification: Personalized Difficulty

### Concept: Adjust for each user's skill level

```python
# User A (Beginner): 
# - "Easy" questions are standard
# - "Medium" feels challenging
# - "Hard" is very difficult

# User B (Advanced):
# - "Easy" questions are too simple
# - "Medium" is comfortable
# - "Hard" is appropriately challenging

# Solution: Personalized difficulty modifiers
user.difficulty_modifier = calculate_from_performance()
effective_difficulty = base_difficulty * user.difficulty_modifier
```

---

## 📊 Current Question Distribution

Let's check the current distribution in your database:

```bash
docker exec aptiverse_backend python -c "
from database import SessionLocal
import models

db = SessionLocal()
questions = db.query(models.Question).all()

easy = sum(1 for q in questions if q.difficulty == 'Easy')
medium = sum(1 for q in questions if q.difficulty == 'Medium')
hard = sum(1 for q in questions if q.difficulty == 'Hard')

print(f'Easy: {easy}')
print(f'Medium: {medium}')
print(f'Hard: {hard}')
print(f'Total: {len(questions)}')

db.close()
"
```

---

## 🛠️ Quick Commands

### View Questions by Difficulty:
```bash
# Easy questions
docker exec aptiverse_backend python -c "
from database import SessionLocal; import models
db = SessionLocal()
questions = db.query(models.Question).filter(models.Question.difficulty == 'Easy').all()
[print(f'{q.title} - {q.topic}') for q in questions]
db.close()
"
```

### Change a Question's Difficulty:
```bash
# Update specific question
docker exec aptiverse_backend python -c "
from database import SessionLocal; import models
db = SessionLocal()
question = db.query(models.Question).filter(models.Question.title == 'Your Question Title').first()
if question:
    question.difficulty = 'Hard'
    question.xp_reward = 20
    db.commit()
    print(f'Updated to {question.difficulty}')
db.close()
"
```

---

## 🎯 Recommendations

### For Now (Manual System):
1. **Be consistent** with difficulty criteria
2. **Review periodically** - ask users for feedback
3. **Compare similar questions** - maintain consistency within topics
4. **Test yourself** - solve questions to gauge difficulty

### For Future (Dynamic System):
1. **Implement attempt tracking** (add fields to Question model)
2. **Collect data** for 1-2 months
3. **Run batch update** to recalibrate
4. **Monitor changes** and validate against manual ratings
5. **Iterate** on the algorithm

### Hybrid Approach (Recommended):
- ✅ Start with manual ratings (current)
- ✅ Track performance data in background
- ✅ After 50+ attempts, flag questions for review
- ✅ Admin reviews flagged questions
- ✅ Gradually trust the algorithm more

---

## 📝 When Adding New Questions

Follow this checklist:

```python
{
    "title": "Question Title",
    "description": "Problem statement",
    "difficulty": "???",  # How to decide:
    
    # 1. Solve it yourself - how many steps?
    # 2. Compare with similar questions
    # 3. Consider target audience
    # 4. When in doubt, start with Medium
    # 5. Can adjust later based on performance
    
    "xp_reward": 15,  # Easy=10, Medium=15, Hard=20
}
```

---

## 🔍 Quality Control

### Signs a Question is Mis-Rated:

**Too Easy (should be harder):**
- 90%+ success rate
- Avg time < 30 seconds
- Beginners solving easily

**Too Hard (should be easier):**
- <20% success rate
- Users giving up
- Even advanced users struggling

**Just Right:**
- 40-70% success rate for level
- Appropriate time investment
- Mix of correct/incorrect answers

---

## 📚 Resources for Rating

### Competitive Exam Standards:
- **Easy**: School/College level
- **Medium**: Bank PO, SSC, CAT basics
- **Hard**: CAT advanced, GRE, GMAT

### Vocabulary Levels:
- **Easy**: 3000 most common English words
- **Medium**: 5000-10,000 word range
- **Hard**: 10,000+ word range (GRE words)

---

**Current Status**: ✅ Manual rating system in place
**Future Goal**: 🎯 Hybrid manual + dynamic system
**Next Step**: 📊 Start collecting performance data

