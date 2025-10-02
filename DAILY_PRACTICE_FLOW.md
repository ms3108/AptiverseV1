# 📚 Daily Practice Set - Complete User Flow

## Overview
Users can now **customize their daily practice question count** and see exactly how many questions they'll get, all powered by AI recommendations.

---

## 🎯 Complete User Journey

### **Step 1: Set Your Preference** ⚙️

**Location**: Settings Page (`/settings`)

**Access**: Click the **⚙️ Settings** button in the navigation bar

**What You See**:
```
┌─────────────────────────────────────────────────┐
│  ⚙️ Settings                                     │
├─────────────────────────────────────────────────┤
│                                                 │
│  📚 Practice Settings                           │
│                                                 │
│  Daily Practice Questions                       │
│  ━━━━━━━━━━━━━━━●━━━━━━━━━━━━                  │
│  5            25            50                  │
│                                                 │
│             [  20  ]                            │
│           questions                             │
│                                                 │
│  💡 Recommendation:                             │
│  Great balance between challenge                │
│  and consistency!                               │
│                                                 │
│  🤖 AI-Powered Recommendations                  │
│  Your practice set is personalized using:       │
│  ✨ Machine Learning - Weak areas               │
│  🎯 Vector Similarity - Similar questions       │
│  📊 Performance Analysis - Adaptive learning    │
│                                                 │
│  [       💾 Save Settings       ]               │
└─────────────────────────────────────────────────┘
```

**What Happens**:
1. Adjust slider (5-50 questions)
2. See real-time recommendations
3. Click "Save Settings"
4. Preference stored in database (`users.daily_practice_count`)

---

### **Step 2: Start Daily Practice** 📖

**Location**: Practice Set Page (`/practice`)

**Access**: Click **"Today's Practice Set"** button (pink gradient)

**What You See**:
```
┌─────────────────────────────────────────────────┐
│  Navigation Bar                                 │
│  [Dashboard] [Practice Set] [Question Bank]    │
│  [Battles] [⚙️ Settings] [Welcome, User!]      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  🤖 AI-Powered Practice Set    [⚙️ Change Count]│
│  20 personalized questions based on your        │
│  performance                                    │
│                                                 │
│  [✨ ML Weak Areas] [🎯 Vector Similarity]      │
│  [📊 Adaptive Learning]                         │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Question 1 of 20            Score: 0/0         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  [5% filled with gradient]                      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  [Profit & Loss] [Medium]                       │
│                                                 │
│  A shopkeeper marks his goods 25% above...     │
│  What is his actual profit percentage?          │
│                                                 │
│  ○ A. 10%                                       │
│  ○ B. 12.5%                                     │
│  ○ C. 15%                                       │
│  ○ D. 20%                                       │
│                                                 │
│  [     Submit Answer     ]                      │
└─────────────────────────────────────────────────┘
```

**Features**:
- **AI Badge**: Shows questions are AI-curated
- **Question Count**: Displays your preference (e.g., "20 questions")
- **Change Count Button**: Quick link to Settings
- **AI Tags**: ML Weak Areas, Vector Similarity, Adaptive Learning
- **Progress Bar**: Gradient fill (blue to pink)
- **Score Tracker**: Real-time accuracy

---

### **Step 3: Backend Processing** 🧠

**What Happens Behind the Scenes**:

```
User clicks "Today's Practice Set"
         ↓
Frontend: GET /daily-practice
         ↓
Backend: ml_service.generate_daily_practice_set()
         ↓
┌─────────────────────────────────────────────┐
│  1. Get User Preference                     │
│     FROM users.daily_practice_count         │
│     → e.g., 20 questions                    │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│  2. ML Weak Area Detection (Naive Bayes)    │
│     Analyze:                                │
│     - Accuracy per topic                    │
│     - Time taken per question               │
│     - Attempt counts                        │
│     → e.g., Weak in "Profit & Loss"         │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│  3. Find Recent Struggles                   │
│     - Incorrect answers                     │
│     - Time > 3 minutes                      │
│     → e.g., Question IDs: [45, 67, 89]      │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│  4. Weaviate Vector Similarity Search       │
│     For each struggle question:             │
│     - Query Weaviate with 70% certainty     │
│     - Find semantically similar questions   │
│     → 30% of set (e.g., 6 questions)        │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│  5. Fill with Weak Topic Questions          │
│     - From ML-detected weak topics          │
│     - Randomized selection                  │
│     → 70% of set (e.g., 14 questions)       │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│  6. Return Personalized Set                 │
│     {                                       │
│       "questions": [20 questions],          │
│       "total_questions": 20,                │
│       "user_preference": 20,                │
│       "already_completed": false            │
│     }                                       │
└─────────────────────────────────────────────┘
         ↓
Frontend displays questions with AI badges
```

---

## 🔄 Question Composition

Your practice set is **intelligently composed**:

```
Total Questions: Based on your setting (5-50)
├── 30% → Semantically Similar Questions
│         └── Found by Weaviate based on your struggles
│             Example: If you got a "work rate" problem wrong,
│             you'll get similar "work rate" variations
│
└── 70% → Weak Topic Questions
          └── Found by ML based on accuracy < 60%
              Example: If you have 50% accuracy in "Profit & Loss",
              you'll get more of those questions
```

**Example for 20 Questions**:
- **6 questions** (30%): Similar to ones you struggled with
- **14 questions** (70%): From your weak topics

---

## 📊 Data Flow

### **Database Tables Used**:

**1. `users` table**:
```sql
- daily_practice_count (INTEGER, default 10)
  → Stores user's preference
```

**2. `question_attempts` table**:
```sql
- user_id, question_id, is_correct, time_taken_seconds
  → ML analyzes this for weak areas
```

**3. `questions` table**:
```sql
- id, topic, difficulty, vector_id
  → vector_id links to Weaviate
```

**4. Weaviate Vector Database**:
```
- Semantic embeddings of all questions
- Similarity search with 70% certainty threshold
```

---

## 🎨 Visual Indicators

### **In Settings Page**:
✅ Interactive slider with gradient fill
✅ Large number display (e.g., "20")
✅ Real-time recommendations
✅ AI feature explanation box

### **In Practice Page**:
✅ AI-Powered badge (🤖)
✅ Question count display ("20 personalized questions")
✅ Quick "Change Count" button → links to Settings
✅ AI feature tags (ML, Vector Similarity, Adaptive)
✅ Gradient progress bar (blue to pink)

---

## 🚀 User Benefits

| Feature | Benefit |
|---------|---------|
| **Customizable Count** | Choose 5-50 questions based on available time |
| **AI Recommendations** | Get exactly what you need to improve |
| **Vector Similarity** | Practice similar concepts you struggled with |
| **ML Weak Areas** | Focus on topics where you're below 60% accuracy |
| **Visual Feedback** | See AI at work with badges and tags |
| **Flexible Learning** | Adjust anytime via Settings |

---

## 🎯 Example Scenarios

### **Scenario 1: Busy Day** 🏃
**User Action**: Set 5 questions in Settings
**Result**: 
- 2 questions similar to recent struggles
- 3 questions from weak topics
- Quick 10-minute practice session

### **Scenario 2: Deep Practice** 📚
**User Action**: Set 50 questions in Settings
**Result**:
- 15 questions similar to recent struggles
- 35 questions from weak topics
- Comprehensive 90-minute practice session

### **Scenario 3: Balanced Learning** ⚖️
**User Action**: Keep default 10 questions
**Result**:
- 3 questions similar to recent struggles
- 7 questions from weak topics
- Perfect 20-minute daily routine

---

## 🔧 Technical Architecture

```
┌──────────────────────────────────────────────────┐
│                  FRONTEND                        │
│  ┌────────────┐         ┌─────────────────┐     │
│  │ Settings.js│ ←─────→ │ PracticeSet.js  │     │
│  │ (Set count)│         │ (Show AI badge) │     │
│  └────────────┘         └─────────────────┘     │
└──────────────────────────────────────────────────┘
         ↕ API                    ↕ API
┌──────────────────────────────────────────────────┐
│                  BACKEND                         │
│  ┌─────────────────────────────────────────┐    │
│  │ main.py (FastAPI)                       │    │
│  │ - PUT /user/preferences                 │    │
│  │ - GET /daily-practice                   │    │
│  └─────────────────────────────────────────┘    │
│         ↕                                        │
│  ┌─────────────────────────────────────────┐    │
│  │ ml_service.py                           │    │
│  │ - predict_weak_areas() → Naive Bayes    │    │
│  │ - get_similar_questions() → Weaviate    │    │
│  │ - generate_daily_practice_set()         │    │
│  └─────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
         ↕                    ↕
┌──────────────┐    ┌──────────────────────┐
│  PostgreSQL  │    │  Weaviate Vector DB  │
│  - users     │    │  - Semantic search   │
│  - questions │    │  - 70% certainty     │
│  - attempts  │    │  - Embeddings        │
└──────────────┘    └──────────────────────┘
```

---

## ✨ Summary

**The Complete Flow**:
1. **Set preference** → Settings page (5-50 questions)
2. **See AI badge** → Practice page shows count + AI features
3. **Get smart questions** → 30% similar + 70% weak areas
4. **Practice & improve** → Adaptive system learns from you
5. **Repeat daily** → Consistent, personalized learning

**Result**: You get exactly the number of questions you want, intelligently selected by AI to maximize your improvement! 🎯
