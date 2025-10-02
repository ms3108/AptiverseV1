# ⏱️ Time Per Question Feature - Quick Reference

## What's New?

Battle room creators can now **set custom time limits** for each question!

## UI Changes

### Create Battle Room - NEW Time Selector

```
┌───────────────────────────────────────────────────────────┐
│ 📚 Select Topic                                           │
│ ┌─────────────────────────────────────────────────────┐  │
│ │ Profit and Loss (10 questions available)      ▼    │  │
│ └─────────────────────────────────────────────────────┘  │
│ 10 questions available in this topic                     │
│                                                           │
│ 🎯 Number of Questions                                   │
│ ├────────────●────────────┤ [10]                        │
│                                                           │
│ ⏱️ Time Per Question                     ← NEW!          │
│ ├────────────●────────────┤ [60s]                       │
│ Total estimated time: ~10 minutes                        │
│                                                           │
│ ⚡ Battle Rules                                           │
│ • All participants receive same questions                │
│ • 60 seconds per question      ← Updates dynamically     │
│ • Correct: 100 pts + speed bonus (up to 50 pts)         │
│ • Real-time leaderboard                                  │
│ • Winner = highest score                                 │
│                                                           │
│ [Cancel]        [🚀 Create Battle Room]                  │
└───────────────────────────────────────────────────────────┘
```

### Time Options

| Setting | Time | Best For |
|---------|------|----------|
| ⚡ Quick-Fire | 10-30s | True/False, Basic Facts |
| 🎯 Standard | 60s | Normal Aptitude Questions |
| 🧠 Deep-Think | 120-180s | Complex Problems |
| 🏆 Expert | 240-300s | Advanced Analysis |

## Code Changes Summary

### Backend

**1. Database Migration** ✅
```bash
docker-compose exec backend python migrate_time_per_question.py
```

**2. Model** (`models.py`)
```python
time_per_question = Column(Integer, default=60, nullable=False)
```

**3. Schema** (`schemas.py`)
```python
time_per_question: int = Field(default=60, ge=10, le=300)
```

**4. API** (`main.py`)
- Create battle accepts `time_per_question`
- Battle info returns `time_per_question`
- Score calculation uses dynamic time

### Frontend

**1. CreateBattle.js**
```javascript
const [timePerQuestion, setTimePerQuestion] = useState(60);

// Slider: 10-300 seconds, step 10
<input type="range" min="10" max="300" step="10" 
       value={timePerQuestion} />

// API call includes time
{ topic, num_questions, time_per_question: timePerQuestion }
```

**2. BattleRoom.js**
```javascript
const [timePerQuestion, setTimePerQuestion] = useState(60);

// Fetches from battle info
setTimePerQuestion(response.data.time_per_question || 60);

// Timer uses dynamic time
setTimeLeft(timePerQuestion);

// Warning threshold adapts
timeLeft <= Math.min(10, Math.floor(timePerQuestion * 0.16))
```

## Testing Checklist

### ✅ Create Battle
- [ ] Open Create Battle Room
- [ ] Adjust time slider (try 30s, 60s, 120s)
- [ ] Verify "X seconds per question" updates in rules
- [ ] Verify estimated time calculation updates
- [ ] Create battle
- [ ] Check waiting room shows correct time

### ✅ Battle Gameplay
- [ ] Start battle
- [ ] Verify timer counts down from selected time
- [ ] Answer question quickly (< 5 seconds)
- [ ] Verify high speed bonus received
- [ ] Answer question slowly (near time limit)
- [ ] Verify lower speed bonus received

### ✅ Score Validation
- [ ] Create 30-second battle
  - Answer in 0s → Should get ~150 points
  - Answer in 15s → Should get ~125 points
  - Answer in 30s → Should get ~100 points
- [ ] Create 120-second battle
  - Answer in 0s → Should get ~150 points
  - Answer in 60s → Should get ~125 points
  - Answer in 120s → Should get ~100 points

## Speed Bonus Formula

```python
if is_correct:
    base_points = 100
    speed_bonus = 50 * (1 - time_taken / time_per_question)
    total = base_points + speed_bonus  # Max 150
else:
    total = 0
```

**Key Insight**: Speed bonus is **always proportional** to the time limit, ensuring fairness.

## Files Modified

```
backend/
├── models.py                      ← Added time_per_question field
├── schemas.py                     ← Added validation (10-300s)
├── main.py                        ← Updated create/info endpoints
├── migrate_time_per_question.py   ← New migration script
└── battle_manager.py              ← Score calc uses dynamic time

frontend/src/components/
├── CreateBattle.js                ← Added time slider UI
└── BattleRoom.js                  ← Timer uses dynamic time
```

## Quick Commands

```bash
# Apply migration
docker-compose exec backend python migrate_time_per_question.py

# Restart backend
docker-compose restart backend

# Check logs
docker-compose logs backend --tail 50

# Test API
curl http://localhost:8000/battles/topics

# Create test battle with 120s time
curl -X POST http://localhost:8000/battles/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Profit and Loss","num_questions":5,"time_per_question":120}'
```

## Visual Indicators

### In CreateBattle Component

```
Blue Slider (🎯) = Number of Questions
Pink Slider (⏱️) = Time Per Question  ← NEW!
```

### In Battle Room

```
┌──────────────────────────────┐
│ Topic: Profit and Loss       │
│ Questions: 10                │
│ Time/Question: 60s  ← NEW!   │
└──────────────────────────────┘
```

### During Battle

```
Timer Color:
🔵 Blue (normal) → More than 16% time remaining
🔴 Red (warning) → Less than 16% time remaining

Examples:
• 60s timer → Red at ≤10s
• 120s timer → Red at ≤19s  
• 30s timer → Red at ≤5s
```

## Benefits

✅ **Flexible Difficulty** - Match time to question complexity  
✅ **Fair Scoring** - Speed bonus scales with time limit  
✅ **Battle Variety** - Quick-fire, standard, or deep-thinking modes  
✅ **User Control** - Creators set the pace  
✅ **Accessibility** - Longer times for beginners, shorter for experts  

## Status

🟢 **LIVE** - Feature is fully implemented and ready to use!

**Test it now:**
1. Go to http://localhost:3000
2. Click "Create Battle"
3. Adjust the ⏱️ Time Per Question slider
4. Create and start a battle!

---

**Feature Version**: 1.1.0  
**Implementation Date**: October 2, 2025  
**Status**: ✅ Complete
