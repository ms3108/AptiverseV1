# Battle Room Feature - Setup and Usage Guide

## 🎮 Overview

The Battle Room feature enables real-time competitive quiz battles where multiple users can compete simultaneously on the same set of questions. The system uses WebSockets for real-time communication and provides live leaderboards, scoring based on correctness + speed, and comprehensive battle history.

## 📋 Features Implemented

### Backend (FastAPI + WebSocket)
- ✅ Real-time WebSocket connection management
- ✅ Battle room creation with shareable links
- ✅ Topic-based question selection
- ✅ Configurable number of questions (3-20)
- ✅ Live scoring system (100 base points + up to 50 speed bonus)
- ✅ Real-time leaderboard updates
- ✅ Battle history tracking
- ✅ PostgreSQL database tables for battles

### Frontend (React + WebSocket)
- ✅ Create Battle Room UI
- ✅ Join Battle via shareable link or code
- ✅ Waiting room with participant list
- ✅ Real-time battle interface
- ✅ Live leaderboard sidebar
- ✅ Timer and question progression
- ✅ Battle history with statistics
- ✅ Battle button in dashboard navigation

## 🗄️ Database Schema

### New Tables Created:
1. **battle_rooms** - Stores battle room configuration
   - room_code (unique 6-character code)
   - creator_id, topic, num_questions
   - status (waiting, in_progress, completed)
   - timestamps

2. **battle_participants** - Tracks participants in each battle
   - user_id, battle_room_id
   - score, correct_answers, total_time
   - rank (final ranking)

3. **battle_questions** - Links questions to battles
   - battle_room_id, question_id, question_order

4. **battle_answers** - Stores individual answers
   - participant_id, question_id
   - user_answer, is_correct, time_taken
   - points_earned

## 🚀 Setup Instructions

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install websockets
```

Already added to `requirements.txt`:
```
websockets==12.0
```

### 2. Run Database Migration

**Option A: Using Docker (Recommended)**
```bash
# Make sure containers are running
docker-compose up -d

# Run migration
docker-compose exec backend python migrate_battle_tables.py
```

**Option B: Local Python**
```bash
cd backend
python migrate_battle_tables.py
```

Expected output:
```
Starting battle room migration...
Creating battle_rooms table...
Creating battle_participants table...
Creating battle_questions table...
Creating battle_answers table...
Creating indexes...
✅ Battle room migration completed successfully!
```

### 3. Start the Application

```bash
# Start all services
docker-compose up -d

# Or restart to load new code
docker-compose restart backend frontend
```

## 📖 API Endpoints

### Battle Room Endpoints

1. **POST /battles/create**
   - Creates a new battle room
   - Body: `{ "topic": "Profit and Loss", "num_questions": 5 }`
   - Returns: `{ "room_code": "ABC123", "shareable_link": "..." }`

2. **GET /battles/{room_code}/info**
   - Get battle room information
   - Returns: room details, participants, status

3. **POST /battles/{room_code}/join**
   - Join an existing battle room
   - Requires: Authorization token

4. **POST /battles/{room_code}/start**
   - Start the battle (creator only)
   - Triggers question distribution

5. **GET /battles/history**
   - Get user's battle history
   - Returns: list of past battles with stats

6. **GET /battles/topics**
   - Get available topics with question counts
   - Returns: `[{ "topic": "...", "question_count": 23 }]`

7. **WebSocket /ws/battle/{room_code}?token={jwt_token}**
   - Real-time battle communication
   - Handles: question distribution, answer submission, leaderboard updates

## 🎯 Usage Flow

### Creating a Battle

1. User clicks "⚔️ Battles" button in dashboard
2. Navigate to "Battle History" page
3. Click "+ New Battle" button
4. Select topic from dropdown (shows available question count)
5. Adjust number of questions (3-20) using slider
6. Click "🚀 Create Battle Room"
7. Automatically redirected to waiting room
8. Share the room code or link with friends

### Joining a Battle

**Option 1: Direct Link**
- User clicks on shareable link (e.g., `http://localhost:3000/battle/ABC123`)
- Automatically joins if battle is still waiting

**Option 2: Room Code**
- Click "Join Battle" button
- Enter 6-character room code
- Joins the waiting room

### Battle Progression

1. **Waiting Room:**
   - Shows battle configuration (topic, # of questions)
   - Displays all participants
   - Creator can click "Start Battle" when ready
   - Shareable link available to copy

2. **Battle In Progress:**
   - All participants receive questions simultaneously
   - 60-second timer per question
   - Select answer (A, B, C, or D)
   - Submit answer to get instant feedback
   - View correct answer and explanation
   - Live leaderboard updates after each answer
   - Automatic progression to next question

3. **Battle Completed:**
   - Final leaderboard with rankings (🥇🥈🥉)
   - Detailed stats: score, correct answers, accuracy, total time
   - Option to return to dashboard

## 🏆 Scoring System

### Points Calculation
- **Correct Answer**: 100 base points
- **Speed Bonus**: Up to 50 points
  - Calculated as: `50 × (1 - time_taken / 60)`
  - Faster answers = higher bonus
  - After 60 seconds = 0 bonus
- **Wrong Answer**: 0 points

### Leaderboard Ranking
1. **Primary**: Total score (descending)
2. **Tiebreaker**: Total time (ascending - faster is better)

### Example Scores
- Answer in 10 seconds (correct): 100 + 41 = **141 points**
- Answer in 30 seconds (correct): 100 + 25 = **125 points**
- Answer in 55 seconds (correct): 100 + 4 = **104 points**
- Answer after 60 seconds (correct): 100 + 0 = **100 points**

## 🎨 Frontend Components

### 1. CreateBattle.js
- Topic selection dropdown
- Number of questions slider
- Battle rules display
- Join existing battle option

### 2. BattleRoom.js
- Three states: waiting, in_progress, completed
- Waiting room with participant list
- Real-time question interface
- Live leaderboard sidebar
- Timer with visual countdown
- Answer submission and feedback

### 3. BattleHistory.js
- List of all past battles
- Filter by status (all, completed, in_progress)
- Detailed statistics display
- Rank badges (🥇🥈🥉)
- Quick rejoin for in-progress battles

### 4. JoinBattle.js
- Handles joining via room code
- Loading state and error handling
- Redirects to battle room on success

## 🔌 WebSocket Messages

### Client → Server

**Start Battle** (Creator only)
```json
{
  "type": "start_battle"
}
```

**Submit Answer**
```json
{
  "type": "submit_answer",
  "question_id": 123,
  "answer": "A",
  "time_taken": 15.5
}
```

### Server → Client

**User Joined**
```json
{
  "type": "user_joined",
  "user_id": 456,
  "username": "john_doe",
  "participant_count": 3
}
```

**Battle Started**
```json
{
  "type": "battle_started",
  "message": "Battle has started!"
}
```

**Question**
```json
{
  "type": "question",
  "question": {
    "id": 123,
    "title": "...",
    "description": "...",
    "option_a": "...",
    "option_b": "...",
    "option_c": "...",
    "option_d": "...",
    "difficulty": "Medium"
  },
  "question_number": 2,
  "total_questions": 5
}
```

**Answer Result**
```json
{
  "type": "answer_result",
  "is_correct": true,
  "correct_answer": "A",
  "points_earned": 135,
  "explanation": "..."
}
```

**Leaderboard Update**
```json
{
  "type": "leaderboard",
  "leaderboard": [
    {
      "user_id": 1,
      "username": "player1",
      "score": 450,
      "correct_answers": 3,
      "total_time": 45.5,
      "rank": 1
    }
  ]
}
```

**Battle Completed**
```json
{
  "type": "battle_completed",
  "final_leaderboard": [...]
}
```

## 🧪 Testing Instructions

### Test Scenario 1: Create and Play Solo
1. Login to the application
2. Navigate to "Battles" from dashboard
3. Click "Create Battle"
4. Select topic: "Profit and Loss"
5. Set questions: 3
6. Create battle room
7. As creator, start the battle
8. Answer all 3 questions
9. View final results

### Test Scenario 2: Multiplayer Battle
1. **User 1**: Create battle room
2. **User 1**: Copy shareable link
3. **User 2**: Open link in different browser/incognito
4. **User 2**: Login and join battle
5. **User 3**: Join via room code
6. **User 1**: Start battle when all ready
7. All users answer questions
8. Watch live leaderboard update
9. View final rankings

### Test Scenario 3: Battle History
1. Complete multiple battles
2. Navigate to "Battle History"
3. Filter by "completed"
4. View detailed statistics
5. Check rank badges and scores

## 🎨 Design System

### Color Scheme
- **Primary Blue**: `#1E88E5` (buttons, headings, scores)
- **Accent Pink**: `#EC4899` (gradients, highlights)
- **Background**: `#F8FAFF` (light blue tint)
- **Cards**: `#FFFFFF` with neumorphic shadows

### Key UI Elements
- Neumorphic cards with soft shadows
- Gradient buttons (blue → pink)
- Hover lift animations
- Real-time timer with color change (blue → red at 10s)
- Medal-based ranking (🥇🥈🥉)

## 🔧 Troubleshooting

### WebSocket Connection Fails
- Check if backend is running: `docker ps`
- Verify JWT token is valid
- Check browser console for errors

### Battle Not Starting
- Ensure you're the creator
- Check if all participants are connected
- Verify questions exist for selected topic

### Leaderboard Not Updating
- Check WebSocket connection status
- Verify answer submission is successful
- Look for errors in browser console

## 📊 Performance Considerations

- WebSocket connections are persistent (one per participant)
- Battle state is stored in memory for active battles
- Database writes happen on answer submission
- Leaderboard calculations are in-memory (fast)
- Auto-cleanup of disconnected clients

## 🚦 Future Enhancements

Potential improvements:
- Private vs public battles
- Tournament brackets
- Time limits per battle
- Power-ups and bonuses
- Team-based battles
- Battle replay feature
- Spectator mode
- ELO rating system

## 📝 Notes

- Battle rooms expire after 24 hours of inactivity
- Maximum 50 participants per battle
- Questions are randomized from selected topic
- WebSocket timeout: 5 minutes of inactivity
- Room codes are 6 characters (uppercase + digits)

---

**Status**: ✅ Feature Complete - Ready for Testing!
