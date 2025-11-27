# Design Document

## Overview

The Question Bank feature is a hierarchical browsing system that allows users to explore questions organized by categories (Quants, Logical, Linguistics), topics, and sub-topics. The feature includes filtering and sorting capabilities, and provides administrators with the ability to add new questions directly through the interface.

The system leverages the existing Question model in the database and builds upon the current QuestionBank component that already exists in the frontend. The design focuses on enhancing the existing implementation with admin question creation capabilities and ensuring a smooth, performant user experience through caching and optimized queries.

## Architecture

### System Components

1. **Backend API Layer** (FastAPI)
   - Existing endpoints for category browsing and question retrieval
   - New admin endpoint for question creation
   - Caching layer for category data (10-minute TTL)
   - Query optimization for filtering and sorting

2. **Frontend Application Layer** (React)
   - Existing QuestionBank component with category/topic navigation
   - New AdminQuestionForm component for question creation
   - State management using React hooks
   - Client-side caching for categories and questions
   - URL parameter synchronization for deep linking

3. **Database Layer** (PostgreSQL)
   - Existing Question model with category, topic, sub_topic fields
   - Indexed columns for efficient querying (category, topic)
   - User model with is_admin flag for authorization

### Data Flow

```
User Action → Frontend Component → API Request → Backend Validation → Database Query → Response → UI Update
```

For admin question creation:
```
Admin Form Submit → Validation → API Request → Admin Check → Database Insert → Admin Action Log → Success Response → UI Refresh
```

## Components and Interfaces

### Backend Components

#### 1. Question Bank Endpoints (Existing - Enhanced)

**GET /question-bank/categories**
- Returns all categories with topic counts
- Implements server-side caching (10-minute TTL)
- Response format:
```json
{
  "categories": [
    {
      "name": "Quants",
      "total_questions": 150,
      "topics": [
        {"name": "Profit and Loss", "count": 25},
        {"name": "Time and Work", "count": 30}
      ]
    }
  ]
}
```

**GET /question-bank/questions**
- Query parameters: category, topic, difficulty, sort_by, sort_order
- Returns filtered and sorted questions with user attempt status
- Response includes: id, title, description, difficulty, category, topic, xp_reward, solved, attempted

**GET /question-bank/question/{question_id}**
- Returns full question details including options
- Shows correct answer and explanation only if user has solved it

#### 2. Admin Question Creation Endpoint (New)

**POST /admin/questions/create**
- Protected route (requires is_admin = true)
- Request body schema:
```json
{
  "title": "string",
  "description": "string",
  "category": "Quants | Logical | Language",
  "topic": "string",
  "sub_topic": "string (optional)",
  "difficulty": "Easy | Medium | Hard",
  "option_a": "string",
  "option_b": "string",
  "option_c": "string",
  "option_d": "string",
  "correct_answer": "A | B | C | D",
  "explanation": "string",
  "xp_reward": "integer (default: 10)"
}
```
- Validation rules:
  - All required fields must be present
  - Category must be one of: Quants, Logical, Language
  - Difficulty must be one of: Easy, Medium, Hard
  - Correct answer must be A, B, C, or D
  - XP reward must be between 5 and 100
  - Title must be unique
- Creates AdminActionLog entry for audit trail
- Invalidates category cache after successful creation

### Frontend Components

#### 1. QuestionBank Component (Existing - Enhanced)

**Current Features:**
- Three-level navigation: Categories → Topics → Questions
- Breadcrumb navigation and back buttons
- Filtering by difficulty
- Sorting by date, difficulty, or title
- Question status indicators (solved, attempted, not attempted)
- Client-side caching for performance
- URL parameter synchronization

**Enhancements:**
- Add "Add Question" button for admin users (conditionally rendered)
- Modal or separate page for question creation form
- Cache invalidation after question creation

#### 2. AdminQuestionForm Component (New)

**Purpose:** Form for administrators to create new questions

**Features:**
- Form fields for all question attributes
- Category dropdown (Quants, Logical, Language)
- Topic input with autocomplete suggestions based on existing topics
- Sub-topic input (optional)
- Difficulty radio buttons (Easy, Medium, Hard)
- Four option text areas (A, B, C, D)
- Correct answer radio buttons
- Explanation textarea
- XP reward number input (default: 10)
- Real-time validation feedback
- Submit and cancel buttons

**Validation:**
- Client-side validation before submission
- Display server-side validation errors
- Prevent duplicate submissions
- Show success message and redirect to question view

**UI/UX Considerations:**
- Modal overlay for quick access from Question Bank
- Alternatively, dedicated /admin/questions/create route
- Auto-save draft to localStorage (optional enhancement)
- Preview mode to see question before submission

#### 3. Navigation Component (Enhanced)

**Current Features:**
- Dashboard link
- User profile dropdown
- Logout functionality

**Enhancement:**
- Add "Question Bank" button in header
- Highlight active route

## Data Models

### Question Model (Existing)

```python
class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String, nullable=False)  # Easy, Medium, Hard
    category = Column(String, nullable=True, index=True)  # Quants, Logical, Language
    topic = Column(String, nullable=False, index=True)
    sub_topic = Column(String, nullable=True)
    
    # MCQ fields
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String, nullable=False)  # A, B, C, or D
    
    explanation = Column(Text, nullable=True)
    xp_reward = Column(Integer, default=10)
    
    # Additional fields for difficulty tracking
    vector_id = Column(String, nullable=True)
    initial_difficulty = Column(String, nullable=True)
    heuristic_score = Column(Float, default=0.5)
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    total_time_seconds = Column(Float, default=0)
    avg_time_seconds = Column(Float, default=0)
    performance_difficulty = Column(Float, nullable=True)
    alpha_weight = Column(Float, default=0.7)
    last_difficulty_update = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    attempts = relationship("QuestionAttempt", back_populates="question")
```

**Key Fields for Question Bank:**
- category: Primary grouping (Quants, Logical, Language)
- topic: Secondary grouping (e.g., "Profit and Loss", "Syllogisms")
- sub_topic: Optional tertiary grouping
- difficulty: Filter/sort criterion
- All fields are required for proper categorization

### AdminActionLog Model (Existing)

```python
class AdminActionLog(Base):
    __tablename__ = "admin_action_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String, nullable=False)  # "create_question"
    target_type = Column(String, nullable=True)  # "question"
    target_id = Column(Integer, nullable=True)  # question.id
    details = Column(JSON, nullable=True)  # {"title": "...", "category": "..."}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    admin = relationship("User", foreign_keys=[admin_id])
```

**Usage for Question Creation:**
- Log every question creation with admin_id
- Store question details in JSON for audit trail
- Enable tracking of who added which questions

### Pydantic Schemas (New)

```python
class AdminQuestionCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10, max_length=5000)
    category: str = Field(..., regex="^(Quants|Logical|Language)$")
    topic: str = Field(..., min_length=2, max_length=100)
    sub_topic: Optional[str] = Field(None, max_length=100)
    difficulty: str = Field(..., regex="^(Easy|Medium|Hard)$")
    option_a: str = Field(..., min_length=1, max_length=1000)
    option_b: str = Field(..., min_length=1, max_length=1000)
    option_c: str = Field(..., min_length=1, max_length=1000)
    option_d: str = Field(..., min_length=1, max_length=1000)
    correct_answer: str = Field(..., regex="^[A-D]$")
    explanation: str = Field(..., min_length=10, max_length=5000)
    xp_reward: int = Field(default=10, ge=5, le=100)

class AdminQuestionResponse(BaseModel):
    id: int
    title: str
    category: str
    topic: str
    difficulty: str
    created_at: datetime
    message: str
```

## Error Handling

### Backend Error Scenarios

1. **Unauthorized Access (Non-Admin)**
   - Status: 403 Forbidden
   - Message: "Admin privileges required"
   - Action: Redirect to dashboard

2. **Validation Errors**
   - Status: 422 Unprocessable Entity
   - Message: Detailed field-level errors
   - Action: Display errors next to form fields

3. **Duplicate Question Title**
   - Status: 400 Bad Request
   - Message: "A question with this title already exists"
   - Action: Highlight title field with error

4. **Database Connection Error**
   - Status: 500 Internal Server Error
   - Message: "Unable to save question. Please try again."
   - Action: Show retry button

5. **Invalid Category/Topic**
   - Status: 400 Bad Request
   - Message: "Invalid category or topic"
   - Action: Reset form field to valid value

### Frontend Error Handling

1. **Network Errors**
   - Display: "Unable to connect. Check your internet connection."
   - Action: Retry button

2. **Form Validation Errors**
   - Display: Inline error messages below each field
   - Action: Prevent submission until resolved

3. **Session Expiration**
   - Display: "Your session has expired. Please log in again."
   - Action: Redirect to login page

4. **Loading States**
   - Display: Skeleton loaders for categories and questions
   - Display: Spinner for form submission
   - Prevent: Multiple simultaneous submissions

## Testing Strategy

### Backend Testing

#### Unit Tests

1. **Admin Question Creation Endpoint**
   - Test successful question creation with valid data
   - Test validation errors for each field
   - Test unauthorized access (non-admin user)
   - Test duplicate title prevention
   - Test admin action log creation
   - Test cache invalidation after creation

2. **Question Retrieval Endpoints**
   - Test category listing with correct counts
   - Test filtering by category, topic, difficulty
   - Test sorting by different fields
   - Test user attempt status inclusion
   - Test cache behavior (hit/miss)

#### Integration Tests

1. **End-to-End Question Creation Flow**
   - Admin logs in → Creates question → Question appears in bank
   - Verify database record creation
   - Verify admin action log entry
   - Verify cache invalidation

2. **Question Bank Navigation Flow**
   - User selects category → Selects topic → Views questions
   - Apply filters → Sort questions → View question detail
   - Verify correct data at each step

### Frontend Testing

#### Component Tests

1. **QuestionBank Component**
   - Test category rendering
   - Test topic navigation
   - Test question list rendering
   - Test filter and sort controls
   - Test back navigation
   - Test admin button visibility (admin vs non-admin)

2. **AdminQuestionForm Component**
   - Test form field rendering
   - Test validation messages
   - Test successful submission
   - Test error handling
   - Test cancel action

#### Integration Tests

1. **User Flow Tests**
   - Navigate from dashboard to question bank
   - Browse categories and topics
   - Apply filters and sorting
   - View question details

2. **Admin Flow Tests**
   - Admin opens question creation form
   - Fills out all fields
   - Submits form
   - Verifies question appears in bank

### Manual Testing Checklist

- [ ] Admin can access question creation form
- [ ] Non-admin users cannot see "Add Question" button
- [ ] Form validation works for all fields
- [ ] Question appears immediately after creation
- [ ] Category cache updates after question creation
- [ ] Filters work correctly (difficulty)
- [ ] Sorting works correctly (date, difficulty, title)
- [ ] Breadcrumb navigation works
- [ ] Back buttons work correctly
- [ ] Question status indicators display correctly (solved/attempted)
- [ ] Mobile responsive design works
- [ ] Loading states display properly
- [ ] Error messages are clear and helpful

## Performance Considerations

### Backend Optimizations

1. **Database Indexing**
   - Existing indexes on category and topic columns
   - Consider composite index on (category, topic) for faster filtering

2. **Query Optimization**
   - Use SELECT only required fields
   - Avoid N+1 queries with proper joins
   - Implement pagination for large question sets (future enhancement)

3. **Caching Strategy**
   - Server-side cache for categories (10-minute TTL)
   - Invalidate cache on question creation
   - Consider Redis for production (currently in-memory)

### Frontend Optimizations

1. **Client-Side Caching**
   - SessionStorage for category data (10-minute TTL)
   - In-memory Map for question lists (LRU cache with 20-item limit)
   - Prevent redundant API calls

2. **Lazy Loading**
   - Questions loaded only when topic is selected
   - Skeleton loaders for better perceived performance

3. **Debouncing**
   - Debounce filter/sort changes to reduce API calls
   - Currently implemented with useEffect dependencies

4. **Code Splitting**
   - AdminQuestionForm loaded lazily (React.lazy)
   - Reduces initial bundle size

## Security Considerations

1. **Authorization**
   - Admin-only endpoint protection via is_admin check
   - JWT token validation on all requests
   - Frontend button visibility based on user role

2. **Input Validation**
   - Server-side validation for all fields
   - Sanitize HTML in question text to prevent XSS
   - Limit field lengths to prevent DoS

3. **Audit Trail**
   - Log all admin actions with AdminActionLog
   - Include admin_id, timestamp, and action details
   - Enable accountability and troubleshooting

4. **Rate Limiting**
   - Consider rate limiting on question creation endpoint
   - Prevent abuse by malicious admins

## Future Enhancements

1. **Bulk Question Import**
   - CSV/Excel upload for multiple questions
   - Template download for proper formatting

2. **Question Editing**
   - Allow admins to edit existing questions
   - Track edit history in AdminActionLog

3. **Question Deletion**
   - Soft delete with is_deleted flag
   - Prevent deletion if question has attempts

4. **Advanced Filtering**
   - Filter by XP reward range
   - Filter by attempt count or success rate
   - Filter by date added

5. **Search Functionality**
   - Full-text search across question titles and descriptions
   - Search within specific categories or topics

6. **Question Preview**
   - Preview question before submission
   - Test question as a regular user would see it

7. **Topic Management**
   - Admin interface to manage topic hierarchy
   - Add/edit/delete topics and sub-topics
   - Reorder topics for better organization

8. **Analytics Dashboard**
   - View question performance metrics
   - Identify questions that are too easy/hard
   - Track which topics need more questions
