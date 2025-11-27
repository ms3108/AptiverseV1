# Question Upload Format

## JSON Structure

Upload an array of question objects with these **11 required fields**:

```json
[
  {
    "title": "Average of Numbers",
    "description": "The average of 5 consecutive odd numbers is 27. What is the largest number?",
    "difficulty": "Easy",
    "topic": "Averages",
    "option_a": "29",
    "option_b": "31",
    "option_c": "33",
    "option_d": "35",
    "correct_answer": "B",
    "explanation": "If average is 27, middle number is 27. For 5 consecutive odd numbers: 23, 25, 27, 29, 31. Largest is 31.",
    "xp_reward": 10
  },
  {
    "title": "Percentage Calculation",
    "description": "A shopkeeper marks his goods 40% above cost price but allows a discount of 20%. What is his profit percentage?",
    "difficulty": "Medium",
    "topic": "Percentages",
    "option_a": "10%",
    "option_b": "12%",
    "option_c": "15%",
    "option_d": "20%",
    "correct_answer": "B",
    "explanation": "Let CP = 100. Marked Price = 140. After 20% discount: 140 × 0.8 = 112. Profit = 12%.",
    "xp_reward": 15
  },
  {
    "title": "Compound Interest",
    "description": "Find the compound interest on Rs. 5000 at 10% p.a. for 2 years compounded annually.",
    "difficulty": "Easy",
    "topic": "Interest",
    "option_a": "Rs. 1000",
    "option_b": "Rs. 1050",
    "option_c": "Rs. 1100",
    "option_d": "Rs. 1150",
    "correct_answer": "B",
    "explanation": "CI = P(1 + r/100)^t - P = 5000(1.1)^2 - 5000 = 6050 - 5000 = 1050",
    "xp_reward": 10
  }
]
```

---

## Field Guidelines

### Difficulty Levels
- **Easy**: 10 XP reward (basic concepts, simple calculations)
- **Medium**: 15 XP reward (moderate complexity, multi-step problems)
- **Hard**: 20 XP reward (complex reasoning, advanced concepts)

### Topics (Examples)
You can use any topic name, but common topics include:
- **Quantitative Aptitude**: Averages, Percentages, Profit & Loss, Interest, Time & Work, Speed & Distance, Ratios, Mixtures, etc.
- **Logical Reasoning**: Puzzles, Series, Blood Relations, Directions, Coding-Decoding, etc.
- **Verbal Ability**: Synonyms, Antonyms, Sentence Completion, Reading Comprehension, etc.
- **Programming**: Arrays, Strings, Linked Lists, Trees, Graphs, Dynamic Programming, etc.

### Correct Answer Format
- Must be **exactly one uppercase letter**: "A", "B", "C", or "D"
- Corresponds to `option_a`, `option_b`, `option_c`, or `option_d`

### XP Reward
- Typically: 10 (Easy), 15 (Medium), 20 (Hard)
- Can be customized based on question complexity

---

## Upload Methods

### Method 1: Admin API Batch Upload
```bash
POST /admin/questions/batch
Content-Type: application/json
Authorization: Bearer {admin_token}

Body: {
  "questions": [...array of questions...],
  "merge_strategy": "merge"  # or "replace" or "append"
}
```

### Method 2: File Upload
```bash
POST /admin/questions/upload
Content-Type: multipart/form-data
Authorization: Bearer {admin_token}

Form Data:
  - file: questions.json
  - merge_strategy: "merge"
```

---

## Merge Strategies

### 1. **merge** (Recommended)
- Checks if question exists (by title + topic)
- Updates existing questions
- Adds new questions
- **Safe for regular updates**

### 2. **replace**
- Deletes ALL existing questions
- Adds all questions from the file
- **⚠️ Use with caution - loses all existing data**

### 3. **append**
- Adds all questions as new
- Doesn't check for duplicates
- **Fast but may create duplicates**

---

## Validation Rules

### ✅ Valid Example
```json
{
  "title": "Valid Question",
  "description": "This is a valid question?",
  "difficulty": "Easy",
  "topic": "Math",
  "option_a": "Option 1",
  "option_b": "Option 2",
  "option_c": "Option 3",
  "option_d": "Option 4",
  "correct_answer": "A",
  "explanation": "Detailed explanation here.",
  "xp_reward": 10
}
```

### ❌ Common Errors

**Missing Required Field:**
```json
{
  "title": "Question Title",
  "description": "Question text",
  // Missing difficulty, topic, options, etc.
}
```
Error: Field required

**Invalid Correct Answer:**
```json
{
  "correct_answer": "option_a"  // ❌ Wrong
}
```
Should be:
```json
{
  "correct_answer": "A"  // ✅ Correct
}
```

**Wrong Data Type:**
```json
{
  "xp_reward": "10"  // ❌ String
}
```
Should be:
```json
{
  "xp_reward": 10  // ✅ Integer
}
```

---

## Sample JSON Template

Copy this template to create your questions file:

```json
[
  {
    "title": "",
    "description": "",
    "difficulty": "Easy",
    "topic": "",
    "option_a": "",
    "option_b": "",
    "option_c": "",
    "option_d": "",
    "correct_answer": "A",
    "explanation": "",
    "xp_reward": 10
  }
]
```

---

## PowerShell Upload Example

```powershell
# 1. Login to get admin token
$loginResponse = Invoke-RestMethod -Uri "https://aptiverse-backend.fly.dev/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"misna5984@gmail.com","password":"Admin@123"}'

$token = $loginResponse.access_token

# 2. Upload questions
$questions = Get-Content -Path "questions.json" -Raw
$body = @{
  questions = (ConvertFrom-Json $questions)
  merge_strategy = "merge"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "https://aptiverse-backend.fly.dev/admin/questions/batch" `
  -Method POST `
  -Headers @{"Authorization"="Bearer $token"} `
  -ContentType "application/json" `
  -Body $body
```

---

## Reference Files

- **Example File**: `backend/starter_questions.json` (10 sample questions)
- **Schema Definition**: `backend/schemas.py` (QuestionCreate class)
- **Admin API**: `backend/admin_questions.py`

---

## Support

For questions or issues with the upload format:
1. Check the example file: `starter_questions.json`
2. Validate your JSON using an online JSON validator
3. Ensure all required fields are present
4. Check that data types match the schema

---

**Last Updated**: October 20, 2025
