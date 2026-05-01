"""
Event schemas for Kafka-based gamification system.
Each event is serialized to JSON for Kafka transport.
"""
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


# ============================================================================
# Event Schemas
# ============================================================================

class AttemptSubmitted(BaseModel):
    """Published when a user submits an answer to a question."""
    user_id: int
    question_id: int
    is_correct: bool
    xp_earned: int
    topic: str
    time_taken_seconds: int
    timestamp: datetime = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def __init__(self, **data):
        if data.get('timestamp') is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class BattleCompleted(BaseModel):
    """Published when a battle room finishes."""
    room_code: str
    results: List[Dict[str, Any]]
    timestamp: datetime = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def __init__(self, **data):
        if data.get('timestamp') is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class DiscussionVoted(BaseModel):
    """Published when a discussion post is voted on."""
    discussion_id: int
    user_id: int
    vote_type: int
    timestamp: datetime = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def __init__(self, **data):
        if data.get('timestamp') is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


# ============================================================================
# Kafka Topic Configuration
# ============================================================================

KAFKA_TOPICS = {
    'attempt_submitted': 'attempt-submitted',
    'battle_completed': 'battle-completed',
    'discussion_voted': 'discussion-voted',
}

KAFKA_CONSUMER_GROUP = 'aptiverse-gamification'
