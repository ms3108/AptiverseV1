from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, Text, JSON, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    
    # Admin and ban fields
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    is_permanently_banned = Column(Boolean, default=False)
    ban_reason = Column(Text, nullable=True)
    banned_at = Column(DateTime(timezone=True), nullable=True)
    banned_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Gamification fields
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    total_questions_solved = Column(Integer, default=0)
    
    # User preferences
    daily_practice_count = Column(Integer, default=10)  # Number of questions per practice set
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    question_attempts = relationship("QuestionAttempt", back_populates="user", cascade="all, delete-orphan")
    user_badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String, nullable=False, index=True)  # Easy, Medium, Hard
    category = Column(String, nullable=True, index=True)  # Quants, Logical, Linguistics
    topic = Column(String, nullable=False, index=True)  # e.g., Arrays, Graphs, DP
    sub_topic = Column(String, nullable=True)
    
    # MCQ fields
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String, nullable=False)  # A, B, C, or D
    
    explanation = Column(Text, nullable=True)
    xp_reward = Column(Integer, default=10)
    
    # Vector DB reference
    vector_id = Column(String, nullable=True)  # ID in Weaviate
    
    # Difficulty tracking (Hybrid Approach)
    initial_difficulty = Column(String, nullable=True)  # Original heuristic-based difficulty
    heuristic_score = Column(Float, default=0.5)  # 0-1 scale from heuristics
    
    # Performance metrics
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    total_time_seconds = Column(Float, default=0)
    avg_time_seconds = Column(Float, default=0)
    
    # Dynamic difficulty calculation
    performance_difficulty = Column(Float, nullable=True)  # 0-1 calculated from user data
    alpha_weight = Column(Float, default=0.7)  # Weight for heuristic (starts high, decreases)
    last_difficulty_update = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Composite index for the question bank filter + sort queries
    __table_args__ = (
        Index("ix_questions_cat_topic_diff", "category", "topic", "difficulty"),
    )

    # Relationships
    attempts = relationship("QuestionAttempt", back_populates="question")


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    user_answer = Column(String, nullable=False)  # A, B, C, or D
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Integer, nullable=False)  # Time to answer
    attempt_count = Column(Integer, default=1)  # How many times attempted
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Composite index — powers the batch solved-status lookup on question bank load
    __table_args__ = (
        Index("ix_qa_user_question_correct", "user_id", "question_id", "is_correct"),
    )

    # Relationships
    user = relationship("User", back_populates="question_attempts")
    question = relationship("Question", back_populates="attempts")


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_date = Column(DateTime(timezone=True), server_default=func.now())
    questions_solved = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")


class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    icon = Column(String, nullable=True)  # Icon name or emoji
    criteria = Column(JSON, nullable=False)  # e.g., {"type": "streak", "value": 7}
    
    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    __tablename__ = "user_badges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_badges")
    badge = relationship("Badge", back_populates="user_badges")


class Discussion(Base):
    __tablename__ = "discussions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    question = relationship("Question", backref="discussions")
    user = relationship("User", backref="discussions")
    votes = relationship("DiscussionVote", back_populates="discussion", cascade="all, delete-orphan")


class DiscussionVote(Base):
    __tablename__ = "discussion_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vote_type = Column(Integer, nullable=False)  # 1 for upvote, -1 for downvote
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Unique constraint: one vote per user per discussion
    __table_args__ = (
        UniqueConstraint("discussion_id", "user_id", name="uq_discussion_vote"),
        {'sqlite_autoincrement': True},
    )
    
    # Relationships
    discussion = relationship("Discussion", back_populates="votes")
    user = relationship("User", backref="discussion_votes")


class BattleRoom(Base):
    __tablename__ = "battle_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    room_code = Column(String, unique=True, nullable=False, index=True)  # Shareable code
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    topic = Column(String, nullable=False)  # e.g., "Profit and Loss", "Time and Work"
    num_questions = Column(Integer, nullable=False)  # Number of questions in battle
    time_per_question = Column(Integer, default=60, nullable=False)  # Time limit per question in seconds
    
    status = Column(String, default="waiting")  # waiting, in_progress, completed
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User", backref="created_battles")
    participants = relationship("BattleParticipant", back_populates="battle_room", cascade="all, delete-orphan")
    questions = relationship("BattleQuestion", back_populates="battle_room", cascade="all, delete-orphan")


class BattleParticipant(Base):
    __tablename__ = "battle_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    battle_room_id = Column(Integer, ForeignKey("battle_rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    score = Column(Integer, default=0)  # Total score (correctness + speed bonus)
    correct_answers = Column(Integer, default=0)
    total_time_seconds = Column(Float, default=0.0)  # Total time taken
    
    rank = Column(Integer, nullable=True)  # Final rank in battle
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    battle_room = relationship("BattleRoom", back_populates="participants")
    user = relationship("User", backref="battle_participations")
    answers = relationship("BattleAnswer", back_populates="participant", cascade="all, delete-orphan")


class BattleQuestion(Base):
    __tablename__ = "battle_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    battle_room_id = Column(Integer, ForeignKey("battle_rooms.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    question_order = Column(Integer, nullable=False)  # Order in battle (1, 2, 3...)
    
    # Relationships
    battle_room = relationship("BattleRoom", back_populates="questions")
    question = relationship("Question", backref="battle_questions")


class BattleAnswer(Base):
    __tablename__ = "battle_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("battle_participants.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    user_answer = Column(String, nullable=False)  # A, B, C, or D
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Float, nullable=False)
    points_earned = Column(Integer, default=0)  # Score for this question
    
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    participant = relationship("BattleParticipant", back_populates="answers")
    question = relationship("Question", backref="battle_answers")


class AdminActionLog(Base):
    """Log all admin actions for accountability"""
    __tablename__ = "admin_action_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String, nullable=False)  # ban_user, delete_question, push_question, etc.
    target_type = Column(String, nullable=True)  # user, question, post
    target_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)  # Store additional details like reason, changes, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    admin = relationship("User", foreign_keys=[admin_id])


class BannedEmail(Base):
    """Track permanently banned emails to prevent re-registration"""
    __tablename__ = "banned_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    reason = Column(Text, nullable=True)
    banned_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    banned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    banned_by = relationship("User", foreign_keys=[banned_by_admin_id])


class ReportedPost(Base):
    """Track reported community posts"""
    __tablename__ = "reported_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, nullable=False)  # Reference to discussion post
    post_content = Column(Text, nullable=False)
    posted_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reported_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, reviewed, resolved
    resolved_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_action = Column(String, nullable=True)  # delete_post, warn_user, ban_user, no_action
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    posted_by = relationship("User", foreign_keys=[posted_by_user_id])
    reported_by = relationship("User", foreign_keys=[reported_by_user_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_admin_id])


class UserWarning(Base):
    """Track warnings issued to users"""
    __tablename__ = "user_warnings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("reported_posts.id"), nullable=True)
    reason = Column(Text, nullable=False)
    issued_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="warnings")
    issued_by = relationship("User", foreign_keys=[issued_by_admin_id])
    report = relationship("ReportedPost", foreign_keys=[report_id])


# =============================================================================
# BKT Mastery State (Gap 4)
# =============================================================================

class UserTopicMastery(Base):
    """Bayesian Knowledge Tracing state per user per topic."""
    __tablename__ = "user_topic_mastery"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False, index=True)

    # BKT latent mastery probability [0, 1]
    p_mastery = Column(Float, default=0.1, nullable=False)

    # Per-topic BKT parameters (can be tuned over time)
    p_learn = Column(Float, default=0.10)     # learning rate
    p_guess = Column(Float, default=0.25)     # guess probability
    p_slip = Column(Float, default=0.10)      # slip probability
    forget_lambda = Column(Float, default=0.01)  # forgetting rate per day

    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Unique: one mastery record per (user, topic)
    __table_args__ = (
        UniqueConstraint("user_id", "topic", name="uq_user_topic_mastery"),
    )

    # Relationships
    user = relationship("User", backref="topic_mastery")


# =============================================================================
# Knowledge Hub (Gap 6)
# =============================================================================

class KnowledgeContent(Base):
    """User-generated knowledge articles for the Knowledge Hub."""
    __tablename__ = "knowledge_content"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(20), default="published")  # published, archived
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)

    # ChromaDB vector ID for semantic search
    vector_id = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("User", backref="knowledge_articles")
    votes = relationship("KnowledgeVote", back_populates="content", cascade="all, delete-orphan")


class KnowledgeVote(Base):
    """Upvote/downvote on a KnowledgeContent article."""
    __tablename__ = "knowledge_votes"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("knowledge_content.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vote_type = Column(Integer, nullable=False)  # 1 = upvote, -1 = downvote
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("content_id", "user_id", name="uq_knowledge_vote"),
    )

    # Relationships
    content = relationship("KnowledgeContent", back_populates="votes")
    user = relationship("User", backref="knowledge_votes")
