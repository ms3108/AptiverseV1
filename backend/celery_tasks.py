"""
Celery Tasks — Aptiverse
Covers:
  - Gap 3: Daily practice set pre-generation, practice reminders, inactivity nudge
  - Gap 5: Async XP/badge processing (event-driven gamification)
"""
import os
from datetime import datetime, timedelta

from celery_app import celery_app
import notifications


# ---------------------------------------------------------------------------
# DB session helper — tasks run outside FastAPI request context
# ---------------------------------------------------------------------------
def _get_db():
    from database import SessionLocal
    return SessionLocal()


# ===========================================================================
# Gap 3 — Practice generation & reminder tasks
# ===========================================================================

@celery_app.task(name="celery_tasks.generate_practice_sets_for_all_users", bind=True, max_retries=2)
def generate_practice_sets_for_all_users(self):
    """
    Pre-warm the practice set cache for all active users.
    Runs daily at 07:00 UTC so the first request of the day is instant.
    """
    import models
    import ml_service

    db = _get_db()
    try:
        # Active = logged in within the last 30 days
        cutoff = datetime.utcnow() - timedelta(days=30)
        active_users = db.query(models.User).filter(
            models.User.last_activity_date >= cutoff,
            models.User.is_banned == False,
        ).all()

        print(f"🎯 Pre-generating practice sets for {len(active_users)} active users")
        for user in active_users:
            try:
                ml_service.generate_daily_practice_set(db, user.id, user.daily_practice_count)
            except Exception as e:
                print(f"⚠️  Failed for user {user.id}: {e}")

        return {"status": "ok", "users_processed": len(active_users)}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()


@celery_app.task(name="celery_tasks.send_practice_reminders", bind=True, max_retries=2)
def send_practice_reminders(self):
    """
    Send a practice reminder email to users who haven't practiced today.
    Runs at 08:00 UTC daily.
    """
    import models
    from sqlalchemy import func

    db = _get_db()
    try:
        today = datetime.utcnow().date()

        # Users who were active in the last 7 days but NOT today
        active_users = db.query(models.User).filter(
            models.User.last_activity_date >= datetime.utcnow() - timedelta(days=7),
            models.User.is_banned == False,
        ).all()

        reminded = 0
        for user in active_users:
            # Check today's activity
            today_activity = db.query(models.ActivityLog).filter(
                models.ActivityLog.user_id == user.id,
                func.date(models.ActivityLog.activity_date) == today,
            ).first()

            if not today_activity:
                send_reminder_email.delay(user.id)
                reminded += 1

        return {"status": "ok", "reminders_sent": reminded}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()


@celery_app.task(name="celery_tasks.nudge_inactive_users", bind=True, max_retries=2)
def nudge_inactive_users(self):
    """
    Email users who have been completely inactive for 48 hours.
    Runs every 6 hours via Beat.
    """
    import models

    db = _get_db()
    try:
        cutoff_48h = datetime.utcnow() - timedelta(hours=48)
        cutoff_30d = datetime.utcnow() - timedelta(days=30)  # don't spam truly-gone users

        inactive_users = db.query(models.User).filter(
            models.User.last_activity_date <= cutoff_48h,
            models.User.last_activity_date >= cutoff_30d,
            models.User.is_banned == False,
        ).all()

        nudged = 0
        for user in inactive_users:
            send_reminder_email.delay(user.id, nudge=True)
            nudged += 1

        return {"status": "ok", "nudges_sent": nudged}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()


@celery_app.task(name="celery_tasks.send_reminder_email", bind=True, max_retries=2)
def send_reminder_email(self, user_id: int):
    """
    Send practice reminder or inactivity nudge email using SendGrid.
    """
    import models

    db = _get_db()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            print(f"⚠️  User {user_id} not found")
            return {"status": "user_not_found"}

        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # Inactivity vs practice reminder logic
        days_inactive = (datetime.utcnow() - user.last_activity_date).days if user.last_activity_date else 999

        if days_inactive >= 3:
            # Inactivity nudge
            subject = f"👋 We miss you, {user.username}! — Aptiverse"
            body_html = f"""
            <html><body style="font-family:Arial,sans-serif;color:#333;">
            <div style="max-width:600px;margin:0 auto;padding:20px;border:1px solid #ddd;border-radius:10px;">
                <h2 style="color:#2563eb;">Hey {user.username}! It's been a while 😊</h2>
                <p>You haven't practised in a couple of days. Don't let your streak slip!</p>
                <p>Your current streak is <strong>{user.current_streak} day(s)</strong> and you're at level <strong>{user.level}</strong>.</p>
                <div style="text-align:center;margin:30px 0;">
                    <a href="{frontend_url}" style="background-color:#2563eb;color:white;padding:12px 30px;
                       text-decoration:none;border-radius:5px;display:inline-block;">Resume Practice</a>
                </div>
            </div></body></html>"""
            
            # Send inactivity email
            result = notifications.send_email_sendgrid(
                to_email=user.email,
                subject=subject,
                html_content=body_html,
                text_content=f"Hey {user.username}! It's been a while. Your current streak is {user.current_streak} day(s) and you're at level {user.level}. Resume practice at {frontend_url}"
            )
        else:
            # Daily practice reminder
            result = notifications.send_practice_reminder_email(
                to_email=user.email,
                username=user.username,
                streak_days=user.current_streak,
                practice_url=f"{frontend_url}/practice"
            )

        if result["success"]:
            print(f"✅ Reminder email sent to {user.email}")
        else:
            print(f"❌ Failed to send email to {user.email}: {result.get('message', 'Unknown error')}")

        return {"status": "sent" if result["success"] else "failed", "user_id": user_id, "result": result}

    except Exception as exc:
        raise self.retry(exc=exc, countdown=120)
    finally:
        db.close()


@celery_app.task(name="celery_tasks.send_reminder_sms", bind=True, max_retries=2)
def send_reminder_sms(self, user_id: int):
    """
    Send practice reminder SMS using Twilio.
    """
    import models

    db = _get_db()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            print(f"⚠️  User {user_id} not found")
            return {"status": "user_not_found"}

        # Only send SMS if user has phone number
        if not user.phone_number:
            print(f"⚠️  User {user_id} has no phone number")
            return {"status": "no_phone_number"}

        # Send SMS reminder
        result = notifications.send_practice_reminder_sms(
            to_phone=user.phone_number,
            username=user.username,
            streak_days=user.current_streak
        )

        if result["success"]:
            print(f"✅ Reminder SMS sent to {user.phone_number}")
        else:
            print(f"❌ Failed to send SMS to {user.phone_number}: {result.get('message', 'Unknown error')}")

        return {"status": "sent" if result["success"] else "failed", "user_id": user_id, "result": result}

    except Exception as exc:
        raise self.retry(exc=exc, countdown=120)
    finally:
        db.close()


# ===========================================================================
# Gap 5 — Event-driven gamification tasks
# ===========================================================================

@celery_app.task(name="celery_tasks.process_attempt_submitted", bind=True, max_retries=3)
def process_attempt_submitted(self, user_id: int, question_id: int, is_correct: bool, xp_earned: int):
    """
    Async XP + badge processing after an answer is submitted.
    Decouples the reward computation from the HTTP request path.
    """
    import ml_service

    db = _get_db()
    try:
        if is_correct:
            ml_service.update_user_stats_after_practice(db, user_id, 1, xp_earned)
            newly_earned = ml_service.check_and_award_badges(db, user_id)
            badge_names = [b.name for b in newly_earned]
            print(f"🏅 User {user_id} earned {xp_earned} XP. New badges: {badge_names}")
            return {"status": "ok", "xp_earned": xp_earned, "new_badges": badge_names}
        return {"status": "ok", "xp_earned": 0}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()


@celery_app.task(name="celery_tasks.process_battle_completed", bind=True, max_retries=3)
def process_battle_completed(self, room_code: str, results: list):
    """
    Async XP + badge processing for all participants when a battle ends.
    `results` is a list of dicts: [{user_id, score, correct_answers}, ...]
    """
    import models
    import ml_service

    db = _get_db()
    try:
        xp_per_correct = 15  # battle XP per correct answer
        winner_bonus = 50

        # Sort by score to determine winner
        sorted_results = sorted(results, key=lambda r: -r.get("score", 0))

        for rank, result in enumerate(sorted_results):
            user_id = result["user_id"]
            correct = result.get("correct_answers", 0)
            xp = correct * xp_per_correct + (winner_bonus if rank == 0 else 0)

            ml_service.update_user_stats_after_practice(db, user_id, 0, xp)
            newly_earned = ml_service.check_and_award_badges(db, user_id)
            print(f"⚔️ Battle user {user_id} rank {rank+1}: +{xp} XP, badges: {[b.name for b in newly_earned]}")

        return {"status": "ok", "participants_processed": len(results)}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()
