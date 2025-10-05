from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional
from functools import lru_cache
import models
import schemas
import auth
from database import engine, get_db
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
import random
import admin_routes

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Aptiverse API")

# Add GZip compression middleware for faster responses (reduces payload size by 60-80%)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Simple in-memory cache with TTL
_cache = {}
_cache_time = {}

def cached_query(key: str, query_func, ttl_seconds: int = 300):
    """
    Simple in-memory cache with TTL
    Args:
        key: Cache key
        query_func: Function that returns data to cache
        ttl_seconds: Time to live in seconds (default 5 minutes)
    """
    now = datetime.now()
    
    if key in _cache:
        if now - _cache_time[key] < timedelta(seconds=ttl_seconds):
            return _cache[key]
    
    result = query_func()
    _cache[key] = result
    _cache_time[key] = now
    return result

# Include admin routes
app.include_router(admin_routes.router)

# CORS configuration - support multiple origins
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins = [
    "http://localhost:3000",  # Local development
    frontend_url,  # Production frontend (Vercel)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Aptiverse API"}


@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email is permanently banned
    banned_email = db.query(models.BannedEmail).filter(models.BannedEmail.email == user.email).first()
    if banned_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This email address has been banned from registration. Please contact support."
        )
    
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    verification_token = auth.create_verification_token(user.email)
    
    # Check if email verification should be skipped
    skip_email_verification = os.getenv("SKIP_EMAIL_VERIFICATION", "false").lower() == "true"
    
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        verification_token=verification_token if not skip_email_verification else None,
        is_verified=skip_email_verification  # Auto-verify if skipping email
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send verification email (or print to console)
    if not skip_email_verification:
        send_verification_email(user.email, verification_token)
    
    return db_user


@app.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    # Log the verification attempt
    print(f"\n🔍 Verification attempt with token: {token[:20]}...")
    
    db_user = db.query(models.User).filter(
        models.User.verification_token == token
    ).first()
    
    if not db_user:
        # Check if any user exists with this email pattern
        print(f"❌ No user found with this verification token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token. Please request a new verification email."
        )
    
    if db_user.is_verified:
        print(f"✅ User {db_user.email} is already verified")
        return {"message": "Email already verified. You can now log in."}
    
    # Verify the user
    print(f"✅ Verifying user: {db_user.email}")
    db_user.is_verified = True
    db_user.verification_token = None
    db.commit()
    
    return {"message": "Email verified successfully"}


@app.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_credentials.email
    ).first()
    
    if not user or not auth.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )
    
    access_token = auth.create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@app.get("/warnings")
def get_user_warnings(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all warnings for the current user"""
    warnings = db.query(models.UserWarning).filter(
        models.UserWarning.user_id == current_user.id
    ).order_by(models.UserWarning.created_at.desc()).all()
    
    return {
        "total": len(warnings),
        "unread": sum(1 for w in warnings if not w.is_read),
        "warnings": [{
            "id": w.id,
            "reason": w.reason,
            "issued_by": w.issued_by.username if w.issued_by else "Admin",
            "is_read": w.is_read,
            "created_at": w.created_at.isoformat()
        } for w in warnings]
    }


@app.post("/warnings/{warning_id}/mark-read")
def mark_warning_read(
    warning_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a warning as read"""
    warning = db.query(models.UserWarning).filter(
        models.UserWarning.id == warning_id,
        models.UserWarning.user_id == current_user.id
    ).first()
    
    if not warning:
        raise HTTPException(status_code=404, detail="Warning not found")
    
    warning.is_read = True
    db.commit()
    
    return {"message": "Warning marked as read"}


@app.get("/dashboard/stats")
def get_dashboard_stats(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard statistics including XP, level, streaks, badges, and activity data"""
    from datetime import datetime, timedelta
    
    # Get user badges
    user_badges = db.query(models.UserBadge).filter(
        models.UserBadge.user_id == current_user.id
    ).all()
    
    badges_data = []
    for user_badge in user_badges:
        badge = db.query(models.Badge).filter(models.Badge.id == user_badge.badge_id).first()
        if badge:
            badges_data.append({
                "name": badge.name,
                "description": badge.description,
                "icon": badge.icon,
                "earned_at": user_badge.earned_at.isoformat() if user_badge.earned_at else None
            })
    
    # Get activity data for heatmap (last 365 days)
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=365)
    
    activity_logs = db.query(models.ActivityLog).filter(
        models.ActivityLog.user_id == current_user.id,
        models.ActivityLog.activity_date >= start_date,
        models.ActivityLog.activity_date <= end_date
    ).all()
    
    activity_data = {}
    for log in activity_logs:
        # Extract just the date portion (YYYY-MM-DD) for frontend compatibility
        if hasattr(log.activity_date, 'date'):
            date_str = log.activity_date.date().isoformat()
        else:
            date_str = str(log.activity_date).split('T')[0] if 'T' in str(log.activity_date) else str(log.activity_date).split()[0]
        
        activity_data[date_str] = {
            "questions_solved": log.questions_solved,
            "xp_earned": log.xp_earned
        }
    
    # Calculate XP needed for next level
    xp_for_next_level = (current_user.level + 1) * 100
    current_level_xp = current_user.level * 100
    xp_progress = current_user.xp - current_level_xp
    
    return {
        "username": current_user.username,
        "xp": current_user.xp,
        "level": current_user.level,
        "xp_for_next_level": xp_for_next_level,
        "xp_progress": xp_progress,
        "current_streak": current_user.current_streak,
        "longest_streak": current_user.longest_streak,
        "total_questions_solved": current_user.total_questions_solved,
        "badges": badges_data,
        "activity_data": activity_data
    }


@app.get("/daily-practice")
def get_daily_practice_set(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a personalized daily practice set using ML-based weak area prediction and Weaviate vector similarity"""
    import ml_service
    
    # Check if user has already completed practice today
    today = datetime.utcnow().date()
    today_activity = db.query(models.ActivityLog).filter(
        models.ActivityLog.user_id == current_user.id,
        func.date(models.ActivityLog.activity_date) == today
    ).first()
    
    if today_activity and today_activity.questions_solved > 0:
        return {
            "already_completed": True,
            "message": "You've already completed your practice for today! Come back tomorrow for a new set.",
            "questions_solved_today": today_activity.questions_solved,
            "xp_earned_today": today_activity.xp_earned
        }
    
    # Use user's preferred question count (defaults to 10)
    questions = ml_service.generate_daily_practice_set(db, current_user.id)
    
    # Format questions for frontend
    questions_data = []
    for q in questions:
        questions_data.append({
            "id": q.id,
            "title": q.title,
            "description": q.description,
            "difficulty": q.difficulty,
            "topic": q.topic,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "xp_reward": q.xp_reward
        })
    
    return {
        "already_completed": False,
        "questions": questions_data,
        "total_questions": len(questions_data),
        "user_preference": current_user.daily_practice_count
    }


@app.get("/user/preferences")
def get_user_preferences(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's practice preferences"""
    return {
        "daily_practice_count": current_user.daily_practice_count,
        "username": current_user.username,
        "email": current_user.email
    }


@app.put("/user/preferences")
def update_user_preferences(
    daily_practice_count: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's practice preferences"""
    # Validate range (5-50 questions)
    if daily_practice_count < 5 or daily_practice_count > 50:
        raise HTTPException(
            status_code=400,
            detail="Daily practice count must be between 5 and 50 questions"
        )
    
    current_user.daily_practice_count = daily_practice_count
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Preferences updated successfully",
        "daily_practice_count": current_user.daily_practice_count
    }


@app.post("/submit-answer")
def submit_answer(
    answer_data: schemas.AnswerSubmission,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Submit an answer to a question, log the attempt, and update user stats"""
    from datetime import datetime
    import ml_service
    
    # Get the question
    question = db.query(models.Question).filter(models.Question.id == answer_data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if answer is correct
    is_correct = answer_data.user_answer.upper() == question.correct_answer.upper()
    
    # Get attempt count for this question by this user
    previous_attempts = db.query(models.QuestionAttempt).filter(
        models.QuestionAttempt.user_id == current_user.id,
        models.QuestionAttempt.question_id == answer_data.question_id
    ).count()
    
    # Create question attempt record
    attempt = models.QuestionAttempt(
        user_id=current_user.id,
        question_id=answer_data.question_id,
        user_answer=answer_data.user_answer.upper(),
        is_correct=is_correct,
        time_taken_seconds=int(answer_data.time_taken_seconds),
        attempt_count=previous_attempts + 1
    )
    db.add(attempt)
    
    # Calculate XP earned (full XP only on first correct attempt)
    xp_earned = 0
    if is_correct and previous_attempts == 0:
        xp_earned = question.xp_reward
    
    # Update user stats
    if is_correct:
        ml_service.update_user_stats_after_practice(db, current_user.id, 1, xp_earned)
        
        # Check and award badges
        newly_earned_badges = ml_service.check_and_award_badges(db, current_user.id)
        
        # Get badge details for newly earned badges
        new_badges_data = []
        for badge in newly_earned_badges:
            new_badges_data.append({
                "name": badge.name,
                "description": badge.description,
                "icon": badge.icon
            })
    else:
        newly_earned_badges = []
        new_badges_data = []
    
    db.commit()
    
    # Refresh user to get updated stats
    db.refresh(current_user)
    
    return {
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
        "explanation": question.explanation,
        "xp_earned": xp_earned,
        "total_xp": current_user.xp,
        "current_level": current_user.level,
        "current_streak": current_user.current_streak,
        "new_badges": new_badges_data
    }


def send_verification_email(email: str, token: str):
    """Send verification email using Gmail SMTP or print to console"""
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    verification_link = f"{frontend_url}/verify?token={token}"
    
    # Check if we should skip email verification entirely
    skip_email_verification = os.getenv("SKIP_EMAIL_VERIFICATION", "false").lower() == "true"
    
    if skip_email_verification:
        print(f"\n{'='*80}")
        print(f"📧 EMAIL VERIFICATION SKIPPED (auto-verified)")
        print(f"User: {email}")
        print(f"{'='*80}\n")
        return
    
    # Get Gmail SMTP credentials
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    # Try to send via Gmail SMTP if configured
    if gmail_user and gmail_password and gmail_password != "your-gmail-app-password":
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Verify Your Email - Aptiverse"
            message["From"] = gmail_user
            message["To"] = email
            
            # HTML content
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <h2 style="color: #2563eb;">Welcome to Aptiverse! 🎉</h2>
                        <p>Thank you for registering. Please verify your email address by clicking the button below:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{verification_link}" 
                               style="background-color: #2563eb; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;"
                            >Verify Email</a>
                        </div>
                        <p>Or copy and paste this link into your browser:</p>
                        <p style="background-color: #f3f4f6; padding: 10px; border-radius: 5px; word-break: break-all;">
                            {verification_link}
                        </p>
                        <p style="color: #6b7280; font-size: 14px;">This link will expire in 24 hours.</p>
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                        <p style="color: #6b7280; font-size: 12px;">If you didn't create an account, please ignore this email.</p>
                    </div>
                </body>
            </html>
            """
            
            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email via Gmail SMTP
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(gmail_user, gmail_password)
                server.send_message(message)
            
            print(f"✅ Email sent successfully to {email} via Gmail!")
            return
            
        except Exception as e:
            print(f"⚠️  Error sending email via Gmail: {str(e)}")
            print(f"    Make sure you're using an App Password, not your regular Gmail password.")
    
    # Fallback: Print verification link to console
    print(f"\n{'='*80}")
    print(f"📧 VERIFICATION EMAIL (Console Mode)")
    print(f"{'='*80}")
    print(f"To: {email}")
    print(f"Subject: Verify Your Email - Aptiverse")
    print(f"\nVerification Link:")
    print(f"👉 {verification_link}")
    print(f"\nCopy this link and paste it in your browser to verify the account.")
    print(f"{'='*80}\n")


# ============================================================================
# QUESTION BANK ENDPOINTS
# ============================================================================

@app.get("/question-bank/categories")
def get_categories(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all question categories with topic counts (cached for 10 minutes)"""
    from sqlalchemy import distinct
    
    # Use cache to avoid repeated database queries (10 minute TTL)
    def query_categories():
        categories_data = []
        
        categories = db.query(models.Question.category).distinct().filter(
            models.Question.category.isnot(None)
        ).all()
        
        for (category,) in categories:
            # Get topics for this category
            topics = db.query(models.Question.topic).filter(
                models.Question.category == category
            ).distinct().all()
            
            topic_list = []
            for (topic,) in topics:
                count = db.query(models.Question).filter(
                    models.Question.category == category,
                    models.Question.topic == topic
                ).count()
                topic_list.append({"name": topic, "count": count})
            
            # Sort topics alphabetically
            topic_list.sort(key=lambda x: x["name"])
            
            total_count = db.query(models.Question).filter(
                models.Question.category == category
            ).count()
            
            categories_data.append({
                "name": category,
                "total_questions": total_count,
                "topics": topic_list
            })
        
        # Sort categories: Quants, Logical, Language
        category_order = {"Quants": 0, "Logical": 1, "Language": 2}
        categories_data.sort(key=lambda x: category_order.get(x["name"], 99))
        
        return {"categories": categories_data}
    
    # Cache the expensive query (10 minute TTL)
    return cached_query("question_categories", query_categories, ttl_seconds=600)


@app.get("/question-bank/questions")
def get_questions_by_filters(
    category: Optional[str] = None,
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    sort_by: str = "created_at",  # created_at, difficulty, title
    sort_order: str = "desc",  # asc, desc
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get questions with filters and sorting"""
    
    query = db.query(models.Question)
    
    # Apply filters
    if category:
        query = query.filter(models.Question.category == category)
    if topic:
        query = query.filter(models.Question.topic == topic)
    if difficulty:
        query = query.filter(models.Question.difficulty == difficulty)
    
    # Apply sorting
    if sort_by == "difficulty":
        # Custom sort: Easy -> Medium -> Hard
        difficulty_order = {"Easy": 1, "Medium": 2, "Hard": 3}
        questions = query.all()
        questions.sort(
            key=lambda q: difficulty_order.get(q.difficulty, 99),
            reverse=(sort_order == "desc")
        )
    elif sort_by == "title":
        if sort_order == "asc":
            questions = query.order_by(models.Question.title.asc()).all()
        else:
            questions = query.order_by(models.Question.title.desc()).all()
    else:  # created_at (default)
        if sort_order == "asc":
            questions = query.order_by(models.Question.created_at.asc()).all()
        else:
            questions = query.order_by(models.Question.created_at.desc()).all()
    
    # Get user's attempt status for each question
    question_attempts = {}
    for q in questions:
        # Check if solved (correct answer)
        solved_attempt = db.query(models.QuestionAttempt).filter(
            models.QuestionAttempt.user_id == current_user.id,
            models.QuestionAttempt.question_id == q.id,
            models.QuestionAttempt.is_correct == True
        ).first()
        
        # Check if attempted (any attempt)
        any_attempt = db.query(models.QuestionAttempt).filter(
            models.QuestionAttempt.user_id == current_user.id,
            models.QuestionAttempt.question_id == q.id
        ).first()
        
        question_attempts[q.id] = {
            "solved": solved_attempt is not None,
            "attempted": any_attempt is not None
        }
    
    # Format response
    questions_data = []
    for q in questions:
        questions_data.append({
            "id": q.id,
            "title": q.title,
            "description": q.description,
            "difficulty": q.difficulty,
            "category": q.category,
            "topic": q.topic,
            "xp_reward": q.xp_reward,
            "solved": question_attempts[q.id]["solved"],
            "attempted": question_attempts[q.id]["attempted"]
        })
    
    return {
        "questions": questions_data,
        "total": len(questions_data)
    }


@app.get("/question-bank/question/{question_id}")
def get_question_detail(
    question_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get full question details including options"""
    
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if user has solved it
    solved_attempt = db.query(models.QuestionAttempt).filter(
        models.QuestionAttempt.user_id == current_user.id,
        models.QuestionAttempt.question_id == question_id,
        models.QuestionAttempt.is_correct == True
    ).first()
    
    # Get all user attempts for this question
    attempts = db.query(models.QuestionAttempt).filter(
        models.QuestionAttempt.user_id == current_user.id,
        models.QuestionAttempt.question_id == question_id
    ).all()
    
    return {
        "id": question.id,
        "title": question.title,
        "description": question.description,
        "difficulty": question.difficulty,
        "category": question.category,
        "topic": question.topic,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
        "xp_reward": question.xp_reward,
        "solved": solved_attempt is not None,
        "attempt_count": len(attempts),
        "correct_answer": question.correct_answer if solved_attempt else None,
        "explanation": question.explanation if solved_attempt else None
    }


# ============================================================================
# DISCUSSION ENDPOINTS
# ============================================================================

@app.get("/discussions/{question_id}")
def get_discussions(
    question_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all discussions for a question"""
    
    discussions = db.query(models.Discussion).filter(
        models.Discussion.question_id == question_id
    ).order_by(models.Discussion.upvotes.desc(), models.Discussion.created_at.desc()).all()
    
    discussions_data = []
    for discussion in discussions:
        # Check if current user has voted
        user_vote = db.query(models.DiscussionVote).filter(
            models.DiscussionVote.discussion_id == discussion.id,
            models.DiscussionVote.user_id == current_user.id
        ).first()
        
        # Get username
        user = db.query(models.User).filter(models.User.id == discussion.user_id).first()
        
        discussions_data.append({
            "id": discussion.id,
            "question_id": discussion.question_id,
            "user_id": discussion.user_id,
            "username": user.username if user else "Unknown",
            "content": discussion.content,
            "upvotes": discussion.upvotes,
            "downvotes": discussion.downvotes,
            "user_vote": user_vote.vote_type if user_vote else 0,  # 1 for upvote, -1 for downvote, 0 for none
            "created_at": discussion.created_at.isoformat()
        })
    
    return {"discussions": discussions_data}


@app.post("/discussions")
def create_discussion(
    discussion_data: schemas.DiscussionCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new discussion post for a question"""
    
    # Verify question exists
    question = db.query(models.Question).filter(
        models.Question.id == discussion_data.question_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Create discussion
    discussion = models.Discussion(
        question_id=discussion_data.question_id,
        user_id=current_user.id,
        content=discussion_data.content,
        upvotes=0,
        downvotes=0
    )
    db.add(discussion)
    db.commit()
    db.refresh(discussion)
    
    return {
        "id": discussion.id,
        "question_id": discussion.question_id,
        "user_id": discussion.user_id,
        "username": current_user.username,
        "content": discussion.content,
        "upvotes": discussion.upvotes,
        "downvotes": discussion.downvotes,
        "user_vote": 0,
        "created_at": discussion.created_at.isoformat()
    }


@app.post("/discussions/{discussion_id}/vote")
def toggle_vote(
    discussion_id: int,
    vote_type: int,  # 1 for upvote, -1 for downvote
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle upvote or downvote on a discussion post"""
    
    if vote_type not in [1, -1]:
        raise HTTPException(status_code=400, detail="Invalid vote type. Use 1 for upvote, -1 for downvote")
    
    discussion = db.query(models.Discussion).filter(
        models.Discussion.id == discussion_id
    ).first()
    
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    
    # Check if user already voted
    existing_vote = db.query(models.DiscussionVote).filter(
        models.DiscussionVote.discussion_id == discussion_id,
        models.DiscussionVote.user_id == current_user.id
    ).first()
    
    if existing_vote:
        # If clicking the same vote type, remove it
        if existing_vote.vote_type == vote_type:
            # Remove vote
            if existing_vote.vote_type == 1:
                discussion.upvotes = max(0, discussion.upvotes - 1)
            else:
                discussion.downvotes = max(0, discussion.downvotes - 1)
            db.delete(existing_vote)
            new_vote_type = 0
        else:
            # Switch from upvote to downvote or vice versa
            if existing_vote.vote_type == 1:
                discussion.upvotes = max(0, discussion.upvotes - 1)
                discussion.downvotes += 1
            else:
                discussion.downvotes = max(0, discussion.downvotes - 1)
                discussion.upvotes += 1
            existing_vote.vote_type = vote_type
            new_vote_type = vote_type
    else:
        # Add new vote
        vote = models.DiscussionVote(
            discussion_id=discussion_id,
            user_id=current_user.id,
            vote_type=vote_type
        )
        db.add(vote)
        if vote_type == 1:
            discussion.upvotes += 1
        else:
            discussion.downvotes += 1
        new_vote_type = vote_type
    
    db.commit()
    db.refresh(discussion)
    
    return {
        "discussion_id": discussion.id,
        "upvotes": discussion.upvotes,
        "downvotes": discussion.downvotes,
        "user_vote": new_vote_type
    }


@app.delete("/discussions/{discussion_id}")
def delete_discussion(
    discussion_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a discussion post (only by the author)"""
    
    discussion = db.query(models.Discussion).filter(
        models.Discussion.id == discussion_id
    ).first()
    
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    
    if discussion.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")
    
    db.delete(discussion)
    db.commit()
    
    return {"message": "Discussion deleted successfully"}


@app.post("/discussions/{discussion_id}/report")
def report_discussion(
    discussion_id: int,
    reason: str = Body(..., embed=True),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Report a discussion post for violating community guidelines"""
    
    # Check if discussion exists
    discussion = db.query(models.Discussion).filter(
        models.Discussion.id == discussion_id
    ).first()
    
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    
    # Prevent self-reporting
    if discussion.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot report your own post")
    
    # Check if user already reported this post
    existing_report = db.query(models.ReportedPost).filter(
        models.ReportedPost.post_id == discussion_id,
        models.ReportedPost.reported_by_user_id == current_user.id
    ).first()
    
    if existing_report:
        raise HTTPException(status_code=400, detail="You have already reported this post")
    
    # Create report
    report = models.ReportedPost(
        post_id=discussion_id,
        post_content=discussion.content,
        posted_by_user_id=discussion.user_id,
        reported_by_user_id=current_user.id,
        reason=reason,
        status="pending"
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return {
        "message": "Post reported successfully. Our team will review it shortly.",
        "report_id": report.id
    }


# ==================== BATTLE ROOM ENDPOINTS ====================

from battle_manager import manager, generate_room_code, calculate_score


@app.post("/battles/create")
def create_battle_room(
    battle_data: schemas.BattleRoomCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new battle room"""
    
    # Validate topic exists and has questions
    questions_count = db.query(models.Question).filter(
        models.Question.topic == battle_data.topic
    ).count()
    
    if questions_count < battle_data.num_questions:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough questions available for topic '{battle_data.topic}'. Available: {questions_count}"
        )
    
    # Generate unique room code
    room_code = generate_room_code()
    while db.query(models.BattleRoom).filter(models.BattleRoom.room_code == room_code).first():
        room_code = generate_room_code()
    
    # Create battle room
    battle_room = models.BattleRoom(
        room_code=room_code,
        creator_id=current_user.id,
        topic=battle_data.topic,
        num_questions=battle_data.num_questions,
        time_per_question=battle_data.time_per_question,
        status="waiting"
    )
    
    db.add(battle_room)
    db.commit()
    db.refresh(battle_room)
    
    # Select random questions for this battle
    available_questions = db.query(models.Question).filter(
        models.Question.topic == battle_data.topic
    ).all()
    
    # Randomly select the required number of questions
    import random
    selected_questions = random.sample(available_questions, battle_data.num_questions)
    
    # Assign questions to battle with order
    for idx, question in enumerate(selected_questions, start=1):
        battle_question = models.BattleQuestion(
            battle_room_id=battle_room.id,
            question_id=question.id,
            question_order=idx
        )
        db.add(battle_question)
    
    # Creator automatically joins as participant
    participant = models.BattleParticipant(
        battle_room_id=battle_room.id,
        user_id=current_user.id
    )
    db.add(participant)
    db.commit()
    
    return {
        "room_code": room_code,
        "battle_id": battle_room.id,
        "topic": battle_data.topic,
        "num_questions": battle_data.num_questions,
        "time_per_question": battle_data.time_per_question,
        "shareable_link": f"http://localhost:3000/battle/{room_code}"
    }


@app.get("/battles/{room_code}/info")
def get_battle_info(
    room_code: str,
    db: Session = Depends(get_db)
):
    """Get battle room information"""
    
    battle = db.query(models.BattleRoom).filter(
        models.BattleRoom.room_code == room_code
    ).first()
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle room not found")
    
    participants = db.query(models.BattleParticipant).filter(
        models.BattleParticipant.battle_room_id == battle.id
    ).all()
    
    participant_list = []
    for p in participants:
        user = db.query(models.User).filter(models.User.id == p.user_id).first()
        participant_list.append({
            "user_id": p.user_id,
            "username": user.username if user else "Unknown",
            "score": p.score,
            "correct_answers": p.correct_answers,
            "rank": p.rank
        })
    
    return {
        "room_code": battle.room_code,
        "topic": battle.topic,
        "num_questions": battle.num_questions,
        "time_per_question": battle.time_per_question,
        "status": battle.status,
        "creator_id": battle.creator_id,
        "participants": participant_list,
        "started_at": battle.started_at,
        "completed_at": battle.completed_at
    }


@app.post("/battles/{room_code}/join")
def join_battle_room(
    room_code: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Join an existing battle room"""
    
    battle = db.query(models.BattleRoom).filter(
        models.BattleRoom.room_code == room_code
    ).first()
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle room not found")
    
    if battle.status != "waiting":
        raise HTTPException(status_code=400, detail="Battle has already started or completed")
    
    # Check if already joined
    existing = db.query(models.BattleParticipant).filter(
        models.BattleParticipant.battle_room_id == battle.id,
        models.BattleParticipant.user_id == current_user.id
    ).first()
    
    if existing:
        return {"message": "Already joined", "battle_id": battle.id}
    
    # Add participant
    participant = models.BattleParticipant(
        battle_room_id=battle.id,
        user_id=current_user.id
    )
    db.add(participant)
    db.commit()
    
    return {
        "message": "Joined successfully",
        "battle_id": battle.id,
        "topic": battle.topic,
        "num_questions": battle.num_questions
    }


@app.post("/battles/{room_code}/start")
def start_battle(
    room_code: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Start the battle (only creator can start)"""
    
    battle = db.query(models.BattleRoom).filter(
        models.BattleRoom.room_code == room_code
    ).first()
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle room not found")
    
    if battle.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can start the battle")
    
    if battle.status != "waiting":
        raise HTTPException(status_code=400, detail="Battle already started or completed")
    
    # Get random questions from the topic
    questions = db.query(models.Question).filter(
        models.Question.topic == battle.topic
    ).all()
    
    if len(questions) < battle.num_questions:
        raise HTTPException(status_code=400, detail="Not enough questions available")
    
    # Randomly select questions
    selected_questions = random.sample(questions, battle.num_questions)
    
    # Store battle questions
    for i, question in enumerate(selected_questions):
        battle_question = models.BattleQuestion(
            battle_room_id=battle.id,
            question_id=question.id,
            question_order=i + 1
        )
        db.add(battle_question)
    
    # Update battle status
    battle.status = "in_progress"
    battle.started_at = datetime.now()
    db.commit()
    
    return {"message": "Battle started", "started_at": battle.started_at}


@app.get("/battles/history")
def get_battle_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's battle history"""
    
    participations = db.query(models.BattleParticipant).filter(
        models.BattleParticipant.user_id == current_user.id
    ).all()
    
    history = []
    for participation in participations:
        battle = db.query(models.BattleRoom).filter(
            models.BattleRoom.id == participation.battle_room_id
        ).first()
        
        if battle:
            # Get total participants
            total_participants = db.query(models.BattleParticipant).filter(
                models.BattleParticipant.battle_room_id == battle.id
            ).count()
            
            history.append({
                "battle_id": battle.id,
                "room_code": battle.room_code,
                "topic": battle.topic,
                "num_questions": battle.num_questions,
                "status": battle.status,
                "score": participation.score,
                "correct_answers": participation.correct_answers,
                "rank": participation.rank,
                "total_participants": total_participants,
                "created_at": battle.created_at,
                "completed_at": battle.completed_at
            })
    
    # Sort by created_at descending (most recent first)
    history.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {"battles": history}


@app.get("/battles/topics")
def get_available_topics(db: Session = Depends(get_db)):
    """Get list of available topics with question counts"""
    
    topics = db.query(
        models.Question.topic,
        func.count(models.Question.id).label('count')
    ).group_by(models.Question.topic).all()
    
    return {
        "topics": [{"topic": t[0], "question_count": t[1]} for t in topics]
    }


@app.websocket("/ws/battle/{room_code}")
async def battle_websocket(
    websocket: WebSocket,
    room_code: str,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time battle communication"""
    
    # Verify token and get user
    try:
        user = auth.get_current_user_from_token(token, db)
    except Exception:
        await websocket.close(code=1008)
        return
    
    # Verify battle room exists
    battle = db.query(models.BattleRoom).filter(
        models.BattleRoom.room_code == room_code
    ).first()
    
    if not battle:
        await websocket.close(code=1008)
        return
    
    # Verify user is a participant
    participant = db.query(models.BattleParticipant).filter(
        models.BattleParticipant.battle_room_id == battle.id,
        models.BattleParticipant.user_id == user.id
    ).first()
    
    if not participant:
        await websocket.close(code=1008)
        return
    
    # Connect to room
    await manager.connect(websocket, room_code, user.id, user.username)
    
    try:
        # If battle is in progress, send current state
        if battle.status == "in_progress":
            battle_state = manager.get_battle_state(room_code)
            
            # If state not initialized, initialize it
            if not battle_state:
                # Get battle questions in order
                battle_questions = db.query(models.BattleQuestion).filter(
                    models.BattleQuestion.battle_room_id == battle.id
                ).order_by(models.BattleQuestion.question_order).all()
                
                questions_data = []
                for bq in battle_questions:
                    q = db.query(models.Question).filter(models.Question.id == bq.question_id).first()
                    questions_data.append({
                        "id": q.id,
                        "title": q.title,
                        "description": q.description,
                        "option_a": q.option_a,
                        "option_b": q.option_b,
                        "option_c": q.option_c,
                        "option_d": q.option_d,
                        "correct_answer": q.correct_answer,
                        "difficulty": q.difficulty
                    })
                
                manager.initialize_battle_state(room_code, questions_data, battle.num_questions)
                battle_state = manager.get_battle_state(room_code)
            
            # Send current question
            if battle_state["current_question_index"] < len(battle_state["questions"]):
                current_q = battle_state["questions"][battle_state["current_question_index"]]
                await manager.send_personal_message(websocket, {
                    "type": "question",
                    "question": {
                        "id": current_q["id"],
                        "title": current_q["title"],
                        "description": current_q["description"],
                        "option_a": current_q["option_a"],
                        "option_b": current_q["option_b"],
                        "option_c": current_q["option_c"],
                        "option_d": current_q["option_d"],
                        "difficulty": current_q["difficulty"]
                    },
                    "question_number": battle_state["current_question_index"] + 1,
                    "total_questions": battle_state["num_questions"]
                })
            
            # Send current leaderboard
            leaderboard = manager.get_sorted_leaderboard(room_code)
            await manager.send_personal_message(websocket, {
                "type": "leaderboard",
                "leaderboard": leaderboard
            })
        
        # Listen for messages from client
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "start_battle":
                print(f"🚀 Start battle requested by user {user.id} (creator: {battle.creator_id})")
                # Only creator can start
                if battle.creator_id == user.id and battle.status == "waiting":
                    print(f"✅ Starting battle {room_code}")
                    # Get questions and initialize state
                    battle_questions = db.query(models.BattleQuestion).filter(
                        models.BattleQuestion.battle_room_id == battle.id
                    ).order_by(models.BattleQuestion.question_order).all()
                    print(f"📝 Found {len(battle_questions)} questions for battle")
                    
                    questions_data = []
                    for bq in battle_questions:
                        q = db.query(models.Question).filter(models.Question.id == bq.question_id).first()
                        questions_data.append({
                            "id": q.id,
                            "title": q.title,
                            "description": q.description,
                            "option_a": q.option_a,
                            "option_b": q.option_b,
                            "option_c": q.option_c,
                            "option_d": q.option_d,
                            "correct_answer": q.correct_answer,
                            "difficulty": q.difficulty
                        })
                    
                    manager.initialize_battle_state(room_code, questions_data, battle.num_questions)
                    
                    # Update battle status
                    battle.status = "in_progress"
                    battle.started_at = datetime.now()
                    db.commit()
                    
                    # Send first question to all participants
                    first_question = questions_data[0]
                    print(f"📢 Broadcasting battle_started to room {room_code}")
                    print(f"👥 Active connections in room: {len(manager.active_connections.get(room_code, []))}")
                    await manager.broadcast_to_room(room_code, {
                        "type": "battle_started",
                        "message": "Battle has started!"
                    })
                    
                    print(f"📢 Broadcasting first question to room {room_code}")
                    await manager.broadcast_to_room(room_code, {
                        "type": "question",
                        "question": {
                            "id": first_question["id"],
                            "title": first_question["title"],
                            "description": first_question["description"],
                            "option_a": first_question["option_a"],
                            "option_b": first_question["option_b"],
                            "option_c": first_question["option_c"],
                            "option_d": first_question["option_d"],
                            "difficulty": first_question["difficulty"]
                        },
                        "question_number": 1,
                        "total_questions": battle.num_questions
                    })
            
            elif message_type == "submit_answer":
                # Process answer submission
                question_id = data.get("question_id")
                user_answer = data.get("answer")
                time_taken = data.get("time_taken")
                
                # Get correct answer
                question = db.query(models.Question).filter(models.Question.id == question_id).first()
                is_correct = (user_answer == question.correct_answer)
                
                # Calculate score using battle room's time_per_question
                points = calculate_score(is_correct, time_taken, battle.time_per_question)
                
                # Save answer
                battle_answer = models.BattleAnswer(
                    participant_id=participant.id,
                    question_id=question_id,
                    user_answer=user_answer,
                    is_correct=is_correct,
                    time_taken_seconds=time_taken,
                    points_earned=points
                )
                db.add(battle_answer)
                
                # Update participant stats
                participant.score += points
                participant.total_time_seconds += time_taken
                if is_correct:
                    participant.correct_answers += 1
                
                db.commit()
                
                # Update leaderboard
                manager.update_leaderboard(room_code, user.id, user.username, is_correct, time_taken, points)
                
                # Send feedback to user
                await manager.send_personal_message(websocket, {
                    "type": "answer_result",
                    "is_correct": is_correct,
                    "correct_answer": question.correct_answer,
                    "points_earned": points,
                    "explanation": question.explanation
                })
                
                # Broadcast updated leaderboard
                leaderboard = manager.get_sorted_leaderboard(room_code)
                await manager.broadcast_to_room(room_code, {
                    "type": "leaderboard",
                    "leaderboard": leaderboard
                })
                
                # Check if all participants answered
                battle_state = manager.get_battle_state(room_code)
                current_q_index = battle_state["current_question_index"]
                
                # Count answers for current question
                answers_count = db.query(models.BattleAnswer).join(
                    models.BattleParticipant
                ).filter(
                    models.BattleParticipant.battle_room_id == battle.id,
                    models.BattleAnswer.question_id == question_id
                ).count()
                
                participants_count = db.query(models.BattleParticipant).filter(
                    models.BattleParticipant.battle_room_id == battle.id
                ).count()
                
                # Move to next question after short delay
                if answers_count >= participants_count:
                    await asyncio.sleep(3)  # 3 second delay to show results
                    
                    battle_state["current_question_index"] += 1
                    
                    if battle_state["current_question_index"] < len(battle_state["questions"]):
                        # Send next question
                        next_q = battle_state["questions"][battle_state["current_question_index"]]
                        await manager.broadcast_to_room(room_code, {
                            "type": "question",
                            "question": {
                                "id": next_q["id"],
                                "title": next_q["title"],
                                "description": next_q["description"],
                                "option_a": next_q["option_a"],
                                "option_b": next_q["option_b"],
                                "option_c": next_q["option_c"],
                                "option_d": next_q["option_d"],
                                "difficulty": next_q["difficulty"]
                            },
                            "question_number": battle_state["current_question_index"] + 1,
                            "total_questions": battle_state["num_questions"]
                        })
                    else:
                        # Battle completed
                        battle.status = "completed"
                        battle.completed_at = datetime.now()
                        
                        # Update ranks
                        final_leaderboard = manager.get_sorted_leaderboard(room_code)
                        for entry in final_leaderboard:
                            p = db.query(models.BattleParticipant).filter(
                                models.BattleParticipant.battle_room_id == battle.id,
                                models.BattleParticipant.user_id == entry["user_id"]
                            ).first()
                            if p:
                                p.rank = entry["rank"]
                        
                        db.commit()
                        
                        # Broadcast final results
                        await manager.broadcast_to_room(room_code, {
                            "type": "battle_completed",
                            "final_leaderboard": final_leaderboard
                        })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast_to_room(room_code, {
            "type": "user_left",
            "user_id": user.id,
            "username": user.username
        })
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
