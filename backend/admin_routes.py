"""
Admin Routes for Aptiverse
Handles all admin functionality including user management, question management, and community moderation
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timezone
import json
import secrets
import string

from database import get_db
from auth import get_current_admin, get_password_hash, verify_password
import models
import schemas
from ml_service import get_weaviate_client

router = APIRouter(prefix="/admin", tags=["admin"])


# ==================== Helper Functions ====================

def log_admin_action(
    db: Session,
    admin_id: int,
    action_type: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    details: Optional[dict] = None
):
    """Log admin action for audit trail"""
    log = models.AdminActionLog(
        admin_id=admin_id,
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        details=details
    )
    db.add(log)
    db.commit()


def generate_random_password(length: int = 12) -> str:
    """Generate a random secure password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# ==================== User Management ====================

@router.get("/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Get all users with optional search filter"""
    query = db.query(models.User)
    
    if search:
        query = query.filter(
            (models.User.username.ilike(f"%{search}%")) |
            (models.User.email.ilike(f"%{search}%"))
        )
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "users": [{
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_verified": user.is_verified,
            "is_banned": user.is_banned,
            "is_permanently_banned": user.is_permanently_banned,
            "is_admin": user.is_admin,
            "level": user.level,
            "xp": user.xp,
            "current_streak": user.current_streak,
            "total_questions_solved": user.total_questions_solved,
            "created_at": user.created_at,
            "last_activity_date": user.last_activity_date
        } for user in users]
    }


@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Get detailed information about a specific user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's question attempts
    attempts = db.query(models.QuestionAttempt).filter(
        models.QuestionAttempt.user_id == user_id
    ).order_by(desc(models.QuestionAttempt.created_at)).limit(50).all()
    
    # Get user's battle participation
    battle_participations = db.query(models.BattleParticipant).filter(
        models.BattleParticipant.user_id == user_id
    ).count()
    
    # Get reported posts by this user
    reported_posts = db.query(models.ReportedPost).filter(
        models.ReportedPost.posted_by_user_id == user_id
    ).count()
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_verified": user.is_verified,
            "is_banned": user.is_banned,
            "is_permanently_banned": user.is_permanently_banned,
            "ban_reason": user.ban_reason,
            "banned_at": user.banned_at,
            "is_admin": user.is_admin,
            "level": user.level,
            "xp": user.xp,
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "total_questions_solved": user.total_questions_solved,
            "daily_practice_count": user.daily_practice_count,
            "created_at": user.created_at,
            "last_activity_date": user.last_activity_date
        },
        "stats": {
            "total_attempts": len(attempts),
            "battle_participations": battle_participations,
            "reported_posts": reported_posts
        },
        "recent_attempts": [{
            "question_id": attempt.question_id,
            "is_correct": attempt.is_correct,
            "time_taken": attempt.time_taken,
            "created_at": attempt.created_at
        } for attempt in attempts]
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Permanently delete a user and all their data"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot delete admin users")
    
    email = user.email
    username = user.username
    
    # Delete user (cascade will handle related records)
    db.delete(user)
    db.commit()
    
    # Log action
    log_admin_action(
        db=db,
        admin_id=current_admin.id,
        action_type="delete_user",
        target_type="user",
        target_id=user_id,
        details={"email": email, "username": username}
    )
    
    return {"message": f"User {username} deleted successfully"}


@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    reason: Optional[str] = None,
    permanent: bool = False,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Ban a user (soft ban or permanent ban)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot ban admin users")
    
    user.is_banned = True
    user.ban_reason = reason
    user.banned_at = datetime.now(timezone.utc)
    user.banned_by_admin_id = current_admin.id
    
    if permanent:
        user.is_permanently_banned = True
        # Add email to banned list
        banned_email = models.BannedEmail(
            email=user.email,
            reason=reason,
            banned_by_admin_id=current_admin.id
        )
        db.add(banned_email)
    
    db.commit()
    
    # Log action
    log_admin_action(
        db=db,
        admin_id=current_admin.id,
        action_type="ban_user_permanent" if permanent else "ban_user",
        target_type="user",
        target_id=user_id,
        details={"reason": reason, "permanent": permanent}
    )
    
    return {
        "message": f"User {user.username} banned {'permanently' if permanent else 'temporarily'}",
        "ban_type": "permanent" if permanent else "temporary"
    }


@router.post("/users/{user_id}/unban")
async def unban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Unban a user (removes soft ban only, not permanent ban)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_permanently_banned:
        raise HTTPException(
            status_code=400,
            detail="Cannot unban permanently banned user. Use remove-permanent-ban endpoint."
        )
    
    user.is_banned = False
    user.ban_reason = None
    user.banned_at = None
    user.banned_by_admin_id = None
    
    db.commit()
    
    # Log action
    log_admin_action(
        db=db,
        admin_id=current_admin.id,
        action_type="unban_user",
        target_type="user",
        target_id=user_id,
        details={}
    )
    
    return {"message": f"User {user.username} unbanned successfully"}


@router.post("/users/{user_id}/remove-permanent-ban")
async def remove_permanent_ban(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Remove permanent ban and allow user to re-register"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    email = user.email
    
    # Remove permanent ban flags
    user.is_banned = False
    user.is_permanently_banned = False
    user.ban_reason = None
    user.banned_at = None
    user.banned_by_admin_id = None
    
    # Remove email from banned list
    db.query(models.BannedEmail).filter(models.BannedEmail.email == email).delete()
    
    db.commit()
    
    # Log action
    log_admin_action(
        db=db,
        admin_id=current_admin.id,
        action_type="remove_permanent_ban",
        target_type="user",
        target_id=user_id,
        details={"email": email}
    )
    
    return {"message": f"Permanent ban removed for {user.username}"}


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Reset user password and return new password (to be emailed)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate new password
    new_password = generate_random_password()
    user.hashed_password = get_password_hash(new_password)
    
    db.commit()
    
    # Log action
    log_admin_action(
        db=db,
        admin_id=current_admin.id,
        action_type="reset_password",
        target_type="user",
        target_id=user_id,
        details={"email": user.email}
    )
    
    # TODO: Send email with new password
    
    return {
        "message": "Password reset successfully",
        "email": user.email,
        "new_password": new_password,
        "note": "Please send this password to the user via email"
    }


# ==================== Question Management ====================

@router.post("/questions/upload")
async def upload_questions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Upload questions from JSON file with duplicate detection via Vector DB"""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are allowed")
    
    try:
        content = await file.read()
        questions_data = json.loads(content)
        
        if not isinstance(questions_data, list):
            questions_data = [questions_data]
        
        results = {
            "total": len(questions_data),
            "added": 0,
            "duplicates": 0,
            "errors": []
        }
        
        weaviate_client = get_weaviate_client()
        
        for idx, q_data in enumerate(questions_data):
            try:
                # Validate schema
                required_fields = ["question", "options", "answer", "difficulty", "topic"]
                if not all(field in q_data for field in required_fields):
                    results["errors"].append(f"Question {idx+1}: Missing required fields")
                    continue
                
                # Check for duplicates in Vector DB
                if weaviate_client:
                    similar = weaviate_client.query.get(
                        "Question",
                        ["title", "description"]
                    ).with_near_text({
                        "concepts": [q_data["question"]]
                    }).with_limit(1).with_additional(["certainty"]).do()
                    
                    if similar and "data" in similar and "Get" in similar["data"]:
                        questions = similar["data"]["Get"]["Question"]
                        if questions and questions[0].get("_additional", {}).get("certainty", 0) > 0.95:
                            results["duplicates"] += 1
                            results["errors"].append(
                                f"Question {idx+1}: Duplicate detected (similarity > 95%)"
                            )
                            continue
                
                # Create question
                question = models.Question(
                    title=q_data["question"][:200],
                    description=q_data["question"],
                    difficulty=q_data["difficulty"].lower(),
                    category=q_data.get("topic", "general").capitalize(),
                    topic=q_data.get("topic", "general"),
                    sub_topic=q_data.get("subtopic", ""),
                    option_a=q_data["options"][0] if len(q_data["options"]) > 0 else "",
                    option_b=q_data["options"][1] if len(q_data["options"]) > 1 else "",
                    option_c=q_data["options"][2] if len(q_data["options"]) > 2 else "",
                    option_d=q_data["options"][3] if len(q_data["options"]) > 3 else "",
                    correct_answer=q_data["answer"],
                    explanation=q_data.get("solution", ""),
                    points=10 if q_data["difficulty"].lower() == "easy" else 20 if q_data["difficulty"].lower() == "medium" else 30
                )
                
                db.add(question)
                db.flush()
                
                # Add to Vector DB
                if weaviate_client:
                    weaviate_client.data_object.create(
                        class_name="Question",
                        data_object={
                            "question_id": question.id,
                            "title": question.title,
                            "description": question.description,
                            "difficulty": question.difficulty,
                            "topic": question.topic,
                            "sub_topic": question.sub_topic or ""
                        }
                    )
                
                results["added"] += 1
                
            except Exception as e:
                results["errors"].append(f"Question {idx+1}: {str(e)}")
        
        db.commit()
        
        # Log action
        log_admin_action(
            db=db,
            admin_id=current_admin.id,
            action_type="upload_questions",
            target_type="question",
            details=results
        )
        
        return results
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/questions")
async def get_all_questions(
    skip: int = 0,
    limit: int = 50,
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Get all questions with optional filters and search"""
    query = db.query(models.Question)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (models.Question.title.ilike(search_term)) |
            (models.Question.description.ilike(search_term)) |
            (models.Question.topic.ilike(search_term))
        )
    if topic:
        query = query.filter(models.Question.topic == topic)
    if difficulty:
        query = query.filter(models.Question.difficulty.ilike(difficulty))
    if category:
        query = query.filter(models.Question.category.ilike(category))
    
    total = query.count()
    questions = query.order_by(desc(models.Question.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "questions": [{
            "id": q.id,
            "title": q.title,
            "difficulty": q.difficulty,
            "topic": q.topic,
            "sub_topic": q.sub_topic,
            "category": q.category,
            "created_at": q.created_at
        } for q in questions]
    }


@router.put("/questions/{question_id}")
async def update_question(
    question_id: int,
    question_data: dict,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Update a question"""
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Update fields
    for field, value in question_data.items():
        if hasattr(question, field):
            setattr(question, field, value)
    
    db.commit()
    
    # Log action
    log_admin_action(
        db=db,
        admin_id=current_admin.id,
        action_type="update_question",
        target_type="question",
        target_id=question_id,
        details=question_data
    )
    
    return {"message": "Question updated successfully"}


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Delete a question"""
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    
    # Log action
    log_admin_action(
        db=db,
        admin_id=current_admin.id,
        action_type="delete_question",
        target_type="question",
        target_id=question_id,
        details={"title": question.title}
    )
    
    return {"message": "Question deleted successfully"}


# ==================== Community & Reports ====================

@router.get("/reports")
async def get_reported_posts(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Get all reported posts"""
    query = db.query(models.ReportedPost)
    
    if status:
        query = query.filter(models.ReportedPost.status == status)
    
    total = query.count()
    reports = query.order_by(desc(models.ReportedPost.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "reports": [{
            "id": report.id,
            "post_id": report.post_id,
            "post_content": report.post_content,
            "posted_by": {
                "id": report.posted_by.id,
                "username": report.posted_by.username,
                "email": report.posted_by.email
            },
            "reported_by": {
                "id": report.reported_by.id,
                "username": report.reported_by.username
            },
            "reason": report.reason,
            "status": report.status,
            "resolution_action": report.resolution_action,
            "created_at": report.created_at,
            "resolved_at": report.resolved_at
        } for report in reports]
    }


@router.post("/reports/{report_id}/resolve")
async def resolve_report(
    report_id: int,
    request: schemas.ReportResolveRequest,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Resolve a reported post"""
    report = db.query(models.ReportedPost).filter(models.ReportedPost.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.status = "resolved"
    report.resolution_action = request.action
    report.resolved_by_admin_id = current_admin.id
    report.resolved_at = datetime.now(timezone.utc)
    
    # Execute action
    if request.action == "ban_user":
        user = report.posted_by
        user.is_banned = True
        user.ban_reason = f"Posted inappropriate content (Report #{report_id})"
        user.banned_at = datetime.now(timezone.utc)
        user.banned_by_admin_id = current_admin.id
        
        if request.ban_permanent:
            user.is_permanently_banned = True
            banned_email = models.BannedEmail(
                email=user.email,
                reason=user.ban_reason,
                banned_by_admin_id=current_admin.id
            )
            db.add(banned_email)
    
    elif request.action == "warn_user":
        # Create a warning for the user
        warning = models.UserWarning(
            user_id=report.posted_by_user_id,
            report_id=report_id,
            reason=f"Your post was reported and found to violate community guidelines. Report reason: {report.reason}",
            issued_by_admin_id=current_admin.id,
            is_read=False
        )
        db.add(warning)
    
    # TODO: Implement delete_post action when discussion system is ready
    
    db.commit()
    
    # Log action
    log_admin_action(
        db=db,
        admin_id=current_admin.id,
        action_type="resolve_report",
        target_type="report",
        target_id=report_id,
        details={"action": request.action, "ban_permanent": request.ban_permanent}
    )
    
    return {"message": f"Report resolved with action: {request.action}"}


# ==================== Admin Action Logs ====================

@router.get("/logs")
async def get_admin_logs(
    skip: int = 0,
    limit: int = 100,
    action_type: Optional[str] = None,
    admin_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Get admin action logs for accountability"""
    query = db.query(models.AdminActionLog)
    
    if action_type:
        query = query.filter(models.AdminActionLog.action_type == action_type)
    if admin_id:
        query = query.filter(models.AdminActionLog.admin_id == admin_id)
    
    total = query.count()
    logs = query.order_by(desc(models.AdminActionLog.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "logs": [{
            "id": log.id,
            "admin": {
                "id": log.admin.id,
                "username": log.admin.username,
                "email": log.admin.email
            },
            "action_type": log.action_type,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "details": log.details,
            "created_at": log.created_at
        } for log in logs]
    }


# ==================== Dashboard Stats ====================

@router.get("/stats")
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Get overview statistics for admin dashboard"""
    total_users = db.query(models.User).count()
    banned_users = db.query(models.User).filter(models.User.is_banned == True).count()
    verified_users = db.query(models.User).filter(models.User.is_verified == True).count()
    
    total_questions = db.query(models.Question).count()
    
    pending_reports = db.query(models.ReportedPost).filter(
        models.ReportedPost.status == "pending"
    ).count()
    
    # Recent admin actions
    recent_actions = db.query(models.AdminActionLog).order_by(
        desc(models.AdminActionLog.created_at)
    ).limit(10).all()
    
    return {
        "users": {
            "total": total_users,
            "banned": banned_users,
            "verified": verified_users
        },
        "questions": {
            "total": total_questions
        },
        "reports": {
            "pending": pending_reports
        },
        "recent_actions": [{
            "action_type": action.action_type,
            "admin_username": action.admin.username,
            "created_at": action.created_at
        } for action in recent_actions]
    }
