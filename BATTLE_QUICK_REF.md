# 🎮 Battle Room - Quick Reference

## 🚀 Setup in 3 Steps

### Windows (PowerShell)
```powershell
cd "c:\Users\misna\PycharmProjects\Aptiverse V1"
docker-compose up -d
docker-compose exec backend python migrate_battle_tables.py
```

Then open: **http://localhost:3000**

---

## 📱 User Flow

### Create Battle
1. Login → Click "⚔️ Battles"
2. Click "+ New Battle"
3. Select topic (e.g., "Profit and Loss")
4. Set number of questions (3-20)
5. Click "Create Battle Room"
6. Share room code or link

### Join Battle
- **Via Link**: Click shareable link
- **Via Code**: Enter 6-character code

### Play Battle
1. **Wait**: Creator starts when ready
2. **Answer**: 60s per question
3. **Submit**: Get instant feedback
4. **Compete**: Watch live leaderboard
5. **Win**: View final rankings

---

## 🏆 Scoring

| Action | Points |
|--------|--------|
| Correct (fast) | 100 + up to 50 bonus |
| Correct (slow) | 100 + 0 bonus |
| Wrong | 0 |

**Speed Bonus**: `50 × (1 - seconds/60)`

---

## 🎯 API Quick Reference

```bash
# Create Battle
POST /battles/create
Body: { "topic": "Profit and Loss", "num_questions": 5 }

# Get Battle Info
GET /battles/{room_code}/info

# Join Battle
POST /battles/{room_code}/join

# Start Battle (Creator Only)
POST /battles/{room_code}/start

# Get History
GET /battles/history

# WebSocket
ws://localhost:8000/ws/battle/{room_code}?token={jwt_token}
```

---

## 📊 Database Tables

1. **battle_rooms** - Configuration & status
2. **battle_participants** - Users & scores
3. **battle_questions** - Question selection
4. **battle_answers** - Individual responses

---

## 🎨 UI Components

| Component | Purpose |
|-----------|---------|
| `CreateBattle` | Battle setup UI |
| `BattleRoom` | Real-time game interface |
| `JoinBattle` | Join handler |
| `BattleHistory` | Past battles list |

---

## 🐛 Troubleshooting

### Backend not running?
```bash
docker-compose up -d
docker-compose logs backend
```

### Migration failed?
```bash
docker-compose restart backend
docker-compose exec backend python migrate_battle_tables.py
```

### WebSocket error?
- Check token is valid
- Verify backend is running
- Check browser console

### Can't join battle?
- Battle may have started
- Check room code is correct
- Verify you're logged in

---

## 📂 Key Files

### Backend
- `battle_manager.py` - WebSocket logic
- `models.py` - Database tables
- `main.py` - API endpoints

### Frontend
- `BattleRoom.js` - Main game UI
- `CreateBattle.js` - Setup form
- `BattleHistory.js` - History view

---

## 🎯 Testing Checklist

- [ ] Create battle room
- [ ] Copy shareable link
- [ ] Join from another browser
- [ ] Start battle as creator
- [ ] Answer questions
- [ ] View live leaderboard
- [ ] Complete battle
- [ ] Check battle history

---

## 💡 Tips

- **Fast Answers Win**: Speed bonus up to 50 points
- **Share Links**: Easier than typing codes
- **Check History**: View past performance
- **Creator Powers**: Only creator can start
- **Live Updates**: No refresh needed

---

## 🔗 Resources

- Full Guide: `BATTLE_ROOM_GUIDE.md`
- Implementation: `BATTLE_IMPLEMENTATION_SUMMARY.md`
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/docs`

---

**Status**: ✅ Ready to Battle!

**Need Help?** Check the full guide or API documentation.
