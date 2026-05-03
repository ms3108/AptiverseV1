"""
Kafka producer for publishing gamification events.
Gracefully handles Kafka unavailability with logging.
"""
import json
import os
import logging
from typing import Optional, Dict, Any, List
try:
    from kafka import KafkaProducer
    from kafka.errors import KafkaError
    _KAFKA_AVAILABLE = True
except ImportError:
    KafkaProducer = None  # type: ignore
    KafkaError = Exception  # type: ignore
    _KAFKA_AVAILABLE = False
    logger.warning("kafka-python not installed — Kafka producer disabled")

try:
    from kafka_events import (
        KAFKA_TOPICS, AttemptSubmitted, BattleCompleted, DiscussionVoted
    )
    _EVENTS_AVAILABLE = True
except ImportError:
    _EVENTS_AVAILABLE = False
    KAFKA_TOPICS = {}
    logger.warning("kafka_events not importable — Kafka events disabled")

logger = logging.getLogger(__name__)


class GamificationProducer:
    """Kafka producer for gamification events with fallback handling."""

    _instance: Optional['GamificationProducer'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.producer = None
        self.available = False
        self._init_producer()

    def _init_producer(self):
        """Initialize Kafka producer with error handling."""
        if not _KAFKA_AVAILABLE:
            logger.warning("⚠️  kafka-python not installed, Kafka disabled")
            self.available = False
            return
        try:
            kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')
            self.producer = KafkaProducer(
                bootstrap_servers=[kafka_broker],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1,
                request_timeout_ms=10000,
            )
            self.available = True
            logger.info(f"✓ Kafka producer initialized (broker: {kafka_broker})")
        except Exception as e:
            logger.warning(f"⚠️  Kafka producer init failed: {e}")
            self.available = False
            self.producer = None

    def _publish(self, topic: str, key: Optional[str], value: Dict[str, Any]) -> bool:
        """
        Publish message to Kafka topic.
        Returns True if successful, False if Kafka unavailable.
        """
        if not self.available or self.producer is None:
            logger.warning(f"⚠️  Kafka unavailable, skipping publish to {topic}")
            return False

        try:
            future = self.producer.send(
                topic,
                key=key.encode('utf-8') if key else None,
                value=value
            )
            record_metadata = future.get(timeout=5)
            logger.debug(f"✓ Event published to {topic} (partition: {record_metadata.partition}, offset: {record_metadata.offset})")
            return True
        except KafkaError as e:
            logger.error(f"✗ Failed to publish to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Unexpected error publishing to {topic}: {e}")
            return False

    def publish_attempt_submitted(
        self,
        user_id: int,
        question_id: int,
        is_correct: bool,
        xp_earned: int,
        topic: str,
        time_taken_seconds: int
    ) -> bool:
        """Publish attempt-submitted event."""
        if not _EVENTS_AVAILABLE:
            return False
        event = AttemptSubmitted(
            user_id=user_id,
            question_id=question_id,
            is_correct=is_correct,
            xp_earned=xp_earned,
            topic=topic,
            time_taken_seconds=time_taken_seconds
        )
        return self._publish(
            KAFKA_TOPICS['attempt_submitted'],
            key=f"user-{user_id}",
            value=json.loads(event.json())
        )

    def publish_battle_completed(
        self,
        room_code: str,
        results: List[Dict[str, Any]]
    ) -> bool:
        """Publish battle-completed event."""
        event = BattleCompleted(room_code=room_code, results=results)
        return self._publish(
            KAFKA_TOPICS['battle_completed'],
            key=f"room-{room_code}",
            value=json.loads(event.json())
        )

    def publish_discussion_voted(
        self,
        discussion_id: int,
        user_id: int,
        vote_type: int
    ) -> bool:
        """Publish discussion-voted event."""
        event = DiscussionVoted(
            discussion_id=discussion_id,
            user_id=user_id,
            vote_type=vote_type
        )
        return self._publish(
            KAFKA_TOPICS['discussion_voted'],
            key=f"discussion-{discussion_id}",
            value=json.loads(event.json())
        )

    def close(self):
        """Close producer connection."""
        if self.producer:
            try:
                self.producer.flush(timeout=5)
                self.producer.close()
                logger.info("✓ Kafka producer closed")
            except Exception as e:
                logger.error(f"✗ Error closing producer: {e}")


def get_producer() -> GamificationProducer:
    """Get singleton producer instance."""
    return GamificationProducer()
