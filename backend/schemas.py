from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_verified: bool
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Dashboard and Practice Schemas

class BadgeResponse(BaseModel):
    name: str
    description: str
    icon: str
    earned_at: Optional[str] = None

    class Config:
        from_attributes = True


class DashboardStatsResponse(BaseModel):
    username: str
    xp: int
    level: int
    xp_for_next_level: int
    xp_progress: int
    current_streak: int
    longest_streak: int
    total_questions_solved: int
    badges: List[BadgeResponse]
    activity_data: Dict[str, Dict[str, int]]


class QuestionResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    topic: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    xp_reward: int

    class Config:
        from_attributes = True


class PracticeSetResponse(BaseModel):
    questions: List[QuestionResponse]
    total_questions: int


class AnswerSubmission(BaseModel):
    question_id: int
    user_answer: str = Field(..., min_length=1, max_length=1)
    time_taken_seconds: float = Field(..., ge=0)


class AnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str
    xp_earned: int
    total_xp: int
    current_level: int
    current_streak: int
    new_badges: List[BadgeResponse]


# Discussion Schemas

class DiscussionCreate(BaseModel):
    question_id: int
    content: str = Field(..., min_length=10, max_length=5000)


class DiscussionResponse(BaseModel):
    id: int
    question_id: int
    user_id: int
    username: str
    content: str
    upvotes: int
    downvotes: int = 0
    user_vote: int = 0  # 1 for upvote, -1 for downvote, 0 for no vote
    created_at: datetime
    
    class Config:
        from_attributes = True


# Battle Room Schemas

class BattleRoomCreate(BaseModel):
    topic: str = Field(..., min_length=1, max_length=100)
    num_questions: int = Field(..., ge=1, le=50)
    time_per_question: int = Field(default=60, ge=10, le=300)  # 10 seconds to 5 minutes


class BattleRoomResponse(BaseModel):
    room_code: str
    battle_id: int
    topic: str
    num_questions: int
    time_per_question: int
    shareable_link: str


# Admin Report Schemas

class ReportResolveRequest(BaseModel):
    action: str  # delete_post, warn_user, ban_user, no_action
    ban_permanent: bool = False
