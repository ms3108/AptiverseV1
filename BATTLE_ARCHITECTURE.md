# Battle Room Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           BATTLE ROOM SYSTEM                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │  Dashboard   │  │   Create     │  │    Battle    │            │
│  │              │─>│   Battle     │─>│    History   │            │
│  │ + Battles    │  │              │  │              │            │
│  │   Button     │  │  • Topic     │  │  • Filter    │            │
│  └──────────────┘  │  • # Qs      │  │  • Stats     │            │
│                    │  • Rules     │  │  • Rejoin    │            │
│                    └──────┬───────┘  └──────────────┘            │
│                           │                                        │
│                           v                                        │
│                    ┌──────────────┐                               │
│                    │  Join Battle │                               │
│                    │              │                               │
│                    │  • Via Link  │                               │
│                    │  • Via Code  │                               │
│                    └──────┬───────┘                               │
│                           │                                        │
│                           v                                        │
│  ┌────────────────────────────────────────────────────┐           │
│  │            BATTLE ROOM (BattleRoom.js)             │           │
│  ├────────────────────────────────────────────────────┤           │
│  │                                                    │           │
│  │  WAITING ROOM          IN PROGRESS           COMPLETED         │
│  │  ─────────────         ───────────           ─────────         │
│  │  • Participants        • Timer               • Rankings        │
│  │  • Share Link          • Questions           • Medals          │
│  │  • Start Button        • Live Board          • Stats           │
│  │                        • Submit              • Results         │
│  └────────────┬───────────────────────┬─────────────┬────────────┘
│               │                       │             │              │
│               │    WebSocket          │             │              │
│               └───────────────────────┘             │              │
│                         │                           │              │
└─────────────────────────┼───────────────────────────┼──────────────┘
                          │                           │
                          │ ws://                     │ HTTP
                          │                           │
┌─────────────────────────┼───────────────────────────┼──────────────┐
│                         v                           v              │
│                   BACKEND (FastAPI)                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │               CONNECTION MANAGER                             │  │
│  │              (battle_manager.py)                             │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │  • WebSocket connections per room                           │  │
│  │  • Battle state (in-memory)                                 │  │
│  │  • Leaderboard updates                                      │  │
│  │  • Message broadcasting                                     │  │
│  │  • Score calculation                                        │  │
│  └────────────┬─────────────────────────────────┬───────────────┘  │
│               │                                 │                  │
│               v                                 v                  │
│  ┌────────────────────┐            ┌────────────────────┐         │
│  │  WebSocket         │            │  REST API          │         │
│  │  /ws/battle/{code} │            │  Endpoints         │         │
│  ├────────────────────┤            ├────────────────────┤         │
│  │ • user_joined      │            │ POST /create       │         │
│  │ • start_battle     │            │ GET  /info         │         │
│  │ • submit_answer    │            │ POST /join         │         │
│  │ • question         │            │ POST /start        │         │
│  │ • leaderboard      │            │ GET  /history      │         │
│  │ • answer_result    │            │ GET  /topics       │         │
│  │ • battle_completed │            └────────┬───────────┘         │
│  └────────┬───────────┘                     │                     │
│           │                                 │                     │
│           └─────────────────────────────────┘                     │
│                           │                                        │
│                           v                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    DATABASE MODELS                           │  │
│  │                    (models.py)                               │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │  • BattleRoom         (config & status)                     │  │
│  │  • BattleParticipant  (users & scores)                      │  │
│  │  • BattleQuestion     (question selection)                  │  │
│  │  • BattleAnswer       (responses & points)                  │  │
│  └────────────┬─────────────────────────────────────────────────┘  │
│               │                                                    │
└───────────────┼────────────────────────────────────────────────────┘
                │
                v
┌───────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                            │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  battle_rooms              battle_participants                   │
│  ├─ id                     ├─ id                                 │
│  ├─ room_code (unique)     ├─ battle_room_id (FK)               │
│  ├─ creator_id (FK)        ├─ user_id (FK)                      │
│  ├─ topic                  ├─ score                             │
│  ├─ num_questions          ├─ correct_answers                   │
│  ├─ status                 ├─ total_time_seconds                │
│  ├─ started_at             ├─ rank                              │
│  ├─ completed_at           └─ joined_at                         │
│  └─ created_at                                                  │
│                                                                   │
│  battle_questions          battle_answers                        │
│  ├─ id                     ├─ id                                │
│  ├─ battle_room_id (FK)    ├─ participant_id (FK)              │
│  ├─ question_id (FK)       ├─ question_id (FK)                 │
│  └─ question_order         ├─ user_answer                       │
│                            ├─ is_correct                        │
│                            ├─ time_taken_seconds                │
│                            ├─ points_earned                     │
│                            └─ answered_at                       │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════

                        DATA FLOW DIAGRAM

═══════════════════════════════════════════════════════════════════


USER 1 (Creator)                    USER 2 (Participant)
     │                                      │
     │ 1. Create Battle                    │
     ├──────────────────>                  │
     │   [POST /battles/create]            │
     │   {topic, num_questions}            │
     │                                      │
     │ 2. Get Room Code                    │
     │   ABC123                             │
     │   Share Link                         │
     │────────────────────────────────────>│
     │                                      │
     │                                3. Join Battle
     │                                      ├──────────────>
     │                                      │ [POST /join]
     │                                      │
     │ 4. Connect WebSocket           5. Connect WebSocket
     ├──────────────────>                  ├──────────────>
     │   ws://...ABC123                    │   ws://...ABC123
     │                                      │
     │<────────────────────────────────────│
     │    {type: "user_joined", username: "User2"}
     │                                      │
     │ 6. Start Battle                     │
     ├──────────────────>                  │
     │   {type: "start_battle"}            │
     │                                      │
     │<────────────────────────────────────>
     │         {type: "battle_started"}     │
     │                                      │
     │<────────────────────────────────────>
     │    {type: "question", question: {...}}
     │                                      │
     │ 7. Submit Answer (15s)         8. Submit Answer (20s)
     ├──────────────────>                  ├──────────────>
     │   {answer: "A", time: 15}           │   {answer: "B", time: 20}
     │                                      │
     │ 9. Points: 100 + 37 = 137      10. Points: 100 + 33 = 133
     │<────────────────────────────────────>
     │       {type: "leaderboard", ...}     │
     │                                      │
     │    Rank 1: User1 - 137pts            │
     │    Rank 2: User2 - 133pts            │
     │                                      │
     │           ... Next Question ...       │
     │                                      │
     │<────────────────────────────────────>
     │    {type: "battle_completed"}        │
     │    Final Rankings & Stats            │
     │                                      │


═══════════════════════════════════════════════════════════════════

                        SCORING ALGORITHM

═══════════════════════════════════════════════════════════════════

    Answer Correct?
         │
         ├─ NO ──> 0 points
         │
         └─ YES
              │
              └─> Base Points: 100
                    │
                    └─> Speed Bonus Calculation:
                          │
                          ├─ Time ≤ 60s: bonus = 50 × (1 - time/60)
                          │
                          ├─ Examples:
                          │   • 10s: 50 × (1 - 10/60) = 41 points
                          │   • 30s: 50 × (1 - 30/60) = 25 points
                          │   • 50s: 50 × (1 - 50/60) = 8 points
                          │
                          └─> Total: 100 + Speed Bonus

    Leaderboard Sort:
        1. Score (descending)
        2. Total Time (ascending) - tiebreaker


═══════════════════════════════════════════════════════════════════

                    WEBSOCKET MESSAGE FLOW

═══════════════════════════════════════════════════════════════════

    CLIENT                          SERVER                     DATABASE
      │                               │                            │
      │──1. Connect (ws + token)─────>│                            │
      │                               ├──Verify JWT───────────────>│
      │                               │<──User validated───────────┤
      │<──2. user_joined──────────────┤                            │
      │                               │                            │
      │──3. start_battle──────────────>│                            │
      │                               ├──Get Questions────────────>│
      │                               │<──Questions List───────────┤
      │<──4. question─────────────────┤                            │
      │                               │                            │
      │──5. submit_answer─────────────>│                            │
      │                               ├──Calculate Score──────────>│
      │                               │<──Store Answer─────────────┤
      │<──6. answer_result────────────┤                            │
      │<──7. leaderboard──────────────┤                            │
      │                               │                            │
      │        (All participants)      │                            │
      │<──8. next question────────────┤                            │
      │                               │                            │
      │   ... repeat 5-8 ...           │                            │
      │                               │                            │
      │<──9. battle_completed─────────┤                            │
      │                               ├──Update ranks─────────────>│
      │                               │<──Rankings saved───────────┤
      │                               │                            │
      └───Disconnect─────────────────>│                            │
                                      ├──Cleanup──────────────────>│
                                      │                            │


═══════════════════════════════════════════════════════════════════
                        KEY FEATURES
═══════════════════════════════════════════════════════════════════

✅ Real-time          WebSocket connections
✅ Shareable         6-character room codes + links
✅ Topic-based       Questions from selected topics
✅ Configurable      3-20 questions per battle
✅ Live scoring      100 + speed bonus (0-50)
✅ Leaderboard       Updates after each answer
✅ History           Complete battle records
✅ Persistence       PostgreSQL storage
✅ Authentication    JWT token validation
✅ Responsive        Modern React UI

═══════════════════════════════════════════════════════════════════
