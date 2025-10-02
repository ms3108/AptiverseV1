# Battle Room Time Per Question Feature

## Overview

Battle room creators can now **customize the time limit per question** when creating a battle room. This allows for more flexibility based on question difficulty and battle type.

## Feature Details

### Time Range
- **Minimum**: 10 seconds (for quick-fire battles)
- **Maximum**: 300 seconds (5 minutes for complex problems)
- **Default**: 60 seconds
- **Step**: 10 seconds increments

### What Changed

#### 1. Database Schema
**New Column**: `battle_rooms.time_per_question`
- Type: INTEGER
- Default: 60
- NOT NULL
- Unit: seconds

#### 2. Backend Updates

**Models** (`backend/models.py`):
```python
class BattleRoom(Base):
    # ... other fields
    time_per_question = Column(Integer, default=60, nullable=False)
```

**Schemas** (`backend/schemas.py`):
```python
class BattleRoomCreate(BaseModel):
    topic: str
    num_questions: int
    time_per_question: int = Field(default=60, ge=10, le=300)
```

**API Changes** (`backend/main.py`):
- `/battles/create` - Accepts `time_per_question` parameter
- `/battles/{room_code}/info` - Returns `time_per_question` in response
- Score calculation uses dynamic time limit for speed bonus

#### 3. Frontend Updates

**CreateBattle Component**:
- New slider for time selection (10-300 seconds)
- Dynamic estimated time calculation
- Battle rules display shows selected time
- Pink accent color for time slider

**BattleRoom Component**:
- Timer uses dynamic `time_per_question` from battle settings
- Waiting room displays time per question
- Warning threshold adapts based on time limit (16% of total time)
- Score bonus calculation uses battle-specific time limit

## User Interface

### Create Battle Room Screen

```
📚 Select Topic
┌─────────────────────────────────────────────────┐
│ Profit and Loss (10 questions available)  ▼    │
└─────────────────────────────────────────────────┘

🎯 Number of Questions
[═══════●═════════] 10

⏱️ Time Per Question
[═════●═══════════] 60s
Total estimated time: ~10 minutes

⚡ Battle Rules
• All participants receive the same questions simultaneously
• 60 seconds per question  ← Dynamic based on your selection
• Correct answer: 100 points + speed bonus (up to 50 points)
• Real-time leaderboard updates
• Winner is determined by highest score
```

### Waiting Room Display

```
Battle Configuration
┌─────────────┬─────────────┬──────────────┐
│ Topic       │ Questions   │ Time/Question│
│ Profit and  │ 10          │ 60s         │
│ Loss        │             │             │
└─────────────┴─────────────┴──────────────┘
```

### In-Progress Timer

```
┌────────────────────────────┐
│ Question 5 of 10           │
│                         60s │  ← Dynamic countdown
└────────────────────────────┘
```

## Score Calculation

The speed bonus is calculated relative to the time limit:

```python
base_points = 100
speed_bonus = 50 * (1 - time_taken / time_per_question)
total_points = base_points + speed_bonus  # Max 150 points
```

### Examples

**With 60-second limit:**
- Answer in 0s → 100 + 50 = 150 points
- Answer in 30s → 100 + 25 = 125 points
- Answer in 60s → 100 + 0 = 100 points

**With 120-second limit:**
- Answer in 0s → 100 + 50 = 150 points
- Answer in 60s → 100 + 25 = 125 points
- Answer in 120s → 100 + 0 = 100 points

**With 30-second limit:**
- Answer in 0s → 100 + 50 = 150 points
- Answer in 15s → 100 + 25 = 125 points
- Answer in 30s → 100 + 0 = 100 points

The speed bonus is **always proportional** to the time limit, ensuring fairness regardless of the time setting.

## Migration

A migration script was run to add the column to existing databases:

```bash
docker-compose exec backend python migrate_time_per_question.py
```

**Result:**
- ✅ Column added successfully
- ✅ Existing battle rooms updated with default value (60s)
- ✅ No data loss or downtime

## Use Cases

### 1. Quick-Fire Battles (10-30 seconds)
Perfect for:
- Simple true/false questions
- Basic arithmetic
- Vocabulary/synonyms
- Rapid-fire general knowledge

### 2. Standard Battles (60 seconds) - DEFAULT
Ideal for:
- Multiple choice aptitude questions
- Logical reasoning
- Basic problem-solving
- Standard competitive format

### 3. Deep-Thinking Battles (120-180 seconds)
Best for:
- Complex word problems
- Multi-step calculations
- Data interpretation
- Analytical reasoning

### 4. Challenge Mode (240-300 seconds)
Designed for:
- Advanced mathematics
- Complex case studies
- Comprehensive analysis
- Expert-level problems

## API Reference

### Create Battle Room

**Endpoint**: `POST /battles/create`

**Request Body**:
```json
{
  "topic": "Profit and Loss",
  "num_questions": 10,
  "time_per_question": 90
}
```

**Response**:
```json
{
  "room_code": "ABC123",
  "battle_id": 42,
  "topic": "Profit and Loss",
  "num_questions": 10,
  "time_per_question": 90,
  "shareable_link": "http://localhost:3000/battle/ABC123"
}
```

### Get Battle Info

**Endpoint**: `GET /battles/{room_code}/info`

**Response**:
```json
{
  "room_code": "ABC123",
  "topic": "Profit and Loss",
  "num_questions": 10,
  "time_per_question": 90,
  "status": "waiting",
  "creator_id": 1,
  "participants": [...],
  "started_at": null,
  "completed_at": null
}
```

## Testing

### Manual Testing Steps

1. **Create Battle with Custom Time**:
   - Navigate to Create Battle Room
   - Select topic and number of questions
   - Adjust time slider to desired value (e.g., 120 seconds)
   - Click "Create Battle Room"
   - ✅ Verify time is shown in waiting room

2. **Join and Start Battle**:
   - Share room code with another user
   - Wait for participant to join
   - Creator clicks "Start Battle"
   - ✅ Verify timer counts down from selected time

3. **Answer Question**:
   - Select an answer before time runs out
   - Submit answer
   - ✅ Verify speed bonus calculated correctly

4. **Check Different Time Settings**:
   - Create battles with 10s, 60s, 120s, 300s
   - ✅ Verify timer accuracy for each setting
   - ✅ Verify speed bonus scales proportionally

### Database Verification

```sql
-- Check time_per_question column exists
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'battle_rooms' 
AND column_name = 'time_per_question';

-- Check battle rooms have time settings
SELECT id, room_code, topic, num_questions, time_per_question 
FROM battle_rooms 
ORDER BY created_at DESC 
LIMIT 10;
```

## Benefits

✅ **Flexibility**: Adapt battle difficulty to question complexity  
✅ **Fairness**: Speed bonus scales with time limit  
✅ **Variety**: Create different battle types (quick-fire, standard, deep-thinking)  
✅ **User Control**: Creators decide pace of their battles  
✅ **Accessibility**: Longer times accommodate different skill levels  
✅ **Strategy**: Players can optimize speed vs accuracy differently  

## Future Enhancements

### Potential Features:
1. **Preset Battle Templates**:
   - "Lightning Round" (10s per question)
   - "Standard Battle" (60s per question)
   - "Thinker's Challenge" (120s per question)
   - "Marathon Mode" (180s per question)

2. **Time Warnings**:
   - Audio/visual alerts at 50%, 25%, 10% remaining time
   - Different alert styles based on time limit

3. **Adaptive Timing**:
   - Adjust time based on question difficulty
   - Easy questions: -20 seconds
   - Hard questions: +30 seconds

4. **Statistics**:
   - Track average solve time per user
   - Show optimal time recommendations
   - Compare performance across different time settings

5. **Tournament Mode**:
   - Progressive time reduction each round
   - Survival mode: fail if time runs out

## Troubleshooting

### Issue: Timer shows 60s regardless of setting
**Solution**: Refresh browser or restart frontend container

### Issue: Speed bonus incorrect
**Solution**: Backend may need restart. Run:
```bash
docker-compose restart backend
```

### Issue: Migration failed
**Solution**: 
```bash
# Check if column exists
docker-compose exec backend python -c "from database import engine; from sqlalchemy import text; conn = engine.connect(); result = conn.execute(text('SELECT * FROM battle_rooms LIMIT 1')); print(result.keys())"

# Re-run migration if needed
docker-compose exec backend python migrate_time_per_question.py
```

## Summary

The **Time Per Question** feature gives battle room creators full control over the pace and intensity of their battles. Whether you want fast-paced lightning rounds or thoughtful deep-dive sessions, you can now customize the experience to match your needs.

**Default Behavior**: If not specified, battles use the standard 60-second timer, maintaining backward compatibility with the original design.

---

**Feature Status**: ✅ Implemented and Tested  
**Version**: 1.1.0  
**Date**: October 2, 2025
