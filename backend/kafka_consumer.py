"""
Kafka consumer for gamification events.
Processes attempt-submitted, battle-completed, and discussion-voted events.
Updates user XP, streaks, levels, and badges.
"""
import json
import logging
import os
from typing import Dict, Any, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import ml_service
from kafka_events import KAFKA_TOPICS, KAFKA_CONSUMER_GROUP

logger = logging.getLogger(__name__)


class GamificationConsumer:
    """Kafka consumer for gamification events."""

    def __init__(self):
        self.consumer = None
        self.db_session_factory = None
        self._init_consumer()
        self._init_db()

    def _init_consumer(self):
        """Initialize Kafka consumer."""
        try:
            kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')
            self.consumer = KafkaConsumer(
                *KAFKA_TOPICS.values(),
                bootstrap_servers=[kafka_broker],
                group_id=KAFKA_CONSUMER_GROUP,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                session_timeout_ms=30000,
                max_poll_records=10,
            )
            logger.info(f"✓ Kafka consumer initialized (broker: {kafka_broker}, group: {KAFKA_CONSUMER_GROUP})")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Kafka consumer: {e}")
            raise

    def _init_db(self):
        """Initialize database session factory."""
        try:
            database_url = os.getenv(
                'DATABASE_URL',
                'sqlite:///./aptiverse.db'
            )
            engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False} if 'sqlite' in database_url else {}
            )
            self.db_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            logger.info(f"✓ Database initialized (URL: {database_url})")
        except Exception as e:
            logger.error(f"✗ Failed to initialize database: {e}")
            raise

    def run(self):
        """Start consumer loop."""
        logger.info("🚀 Gamification consumer started, listening for events...")
        try:
            for message in self.consumer:
                db = self.db_session_factory()
                try:
                    self._handle_message(message, db)
                except Exception as e:
                    logger.error(f"✗ Error handling message: {e}")
                finally:
                    db.close()
        except KeyboardInterrupt:
            logger.info("⏹️  Consumer interrupted by user")
        except Exception as e:
            logger.error(f"✗ Consumer error: {e}")
        finally:
            self.close()

    def _handle_message(self, message, db: Session):
        """Route message to appropriate handler based on topic."""
        topic = message.topic
        value = message.value

        if topic == KAFKA_TOPICS['attempt_submitted']:
            self._on_attempt_submitted(value, db)
        elif topic == KAFKA_TOPICS['battle_completed']:
            self._on_battle_completed(value, db)
        elif topic == KAFKA_TOPICS['discussion_voted']:
            self._on_discussion_voted(value, db)
        else:
            logger.warning(f"⚠️  Unknown topic: {topic}")

    def _on_attempt_submitted(self, event: Dict[str, Any], db: Session):
        """Handle attempt-submitted event."""
        user_id = event.get('user_id')
        question_id = event.get('question_id')
        is_correct = event.get('is_correct')
        xp_earned = event.get('xp_earned')
        topic = event.get('topic')
        time_taken = event.get('time_taken_seconds', 0)

        if not is_correct:
            logger.debug(f"⊘ Skipping incorrect attempt (user: {user_id}, question: {question_id})")
            return

        try:
            ml_service.update_user_stats_after_practice(db, user_id, 1, xp_earned)
            newly_earned_badges = ml_service.check_and_award_badges(db, user_id)

            if newly_earned_badges:
                badge_names = [b.name for b in newly_earned_badges]
                logger.info(f"🏆 User {user_id} earned badges: {badge_names}")
            else:
                logger.debug(f"✓ User {user_id} XP updated (+{xp_earned})")

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Failed to process attempt for user {user_id}: {e}")

    def _on_battle_completed(self, event: Dict[str, Any], db: Session):
        """Handle battle-completed event."""
        room_code = event.get('room_code')
        results = event.get('results', [])

        logger.info(f"⚔️  Processing battle completion (room: {room_code}, participants: {len(results)})")

        try:
            for result in results:
                user_id = result.get('user_id')
                correct_answers = result.get('correct_answers', 0)
                rank = result.get('rank', len(results))

                xp = (correct_answers * 15)
                if rank == 1:
                    xp += 50

                ml_service.update_user_stats_after_practice(db, user_id, 1, xp)
                newly_earned_badges = ml_service.check_and_award_badges(db, user_id)

                if newly_earned_badges:
                    badge_names = [b.name for b in newly_earned_badges]
                    logger.info(f"🏆 User {user_id} earned badges: {badge_names}")
                else:
                    logger.debug(f"✓ User {user_id} battle XP updated (+{xp})")

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Failed to process battle completion (room: {room_code}): {e}")

    def _on_discussion_voted(self, event: Dict[str, Any], db: Session):
        """Handle discussion-voted event."""
        discussion_id = event.get('discussion_id')
        user_id = event.get('user_id')
        vote_type = event.get('vote_type')

        logger.debug(f"💬 Discussion voted (discussion: {discussion_id}, user: {user_id}, vote: {vote_type})")

    def close(self):
        """Close consumer connection."""
        if self.consumer:
            try:
                self.consumer.close()
                logger.info("✓ Kafka consumer closed")
            except Exception as e:
                logger.error(f"✗ Error closing consumer: {e}")


def start_consumer():
    """Entry point for consumer."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    consumer = GamificationConsumer()
    consumer.run()
