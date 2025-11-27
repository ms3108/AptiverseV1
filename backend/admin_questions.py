"""
Admin endpoints for question management
Supports batch uploads, updates, and deletion
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import models
import schemas
import auth
from database import get_db
import json

router = APIRouter()

# Cache management - import from cache module
from cache import _cache, _cache_time


@router.post("/admin/questions/create", response_model=schemas.AdminQuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: schemas.AdminQuestionCreate,
    current_user: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new question in the database
    Requires admin privileges
    """
    
    # Check if question with same title already exists
    existing_question = db.query(models.Question).filter(
        models.Question.title == question_data.title
    ).first()
    
    if existing_question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A question with this title already exists"
        )
    
    # Create new question
    new_question = models.Question(
        title=question_data.title,
        description=question_data.description,
        category=None,  # Not in schema
        topic=question_data.topic,
        sub_topic=question_data.subtopic,  # Map subtopic to sub_topic
        difficulty=question_data.difficulty,
        option_a=question_data.option_a,
        option_b=question_data.option_b,
        option_c=question_data.option_c,
        option_d=question_data.option_d,
        correct_answer=question_data.correct_answer,
        explanation=question_data.explanation,
        xp_reward=question_data.xp_reward,
        initial_difficulty=question_data.difficulty,
        heuristic_score=0.5 if question_data.difficulty == "Medium" else (0.3 if question_data.difficulty == "Easy" else 0.7)
    )
    
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    
    # Create admin action log
    admin_log = models.AdminActionLog(
        admin_id=current_user.id,
        action_type="create_question",
        target_type="question",
        target_id=new_question.id,
        details={
            "title": new_question.title,
            "category": new_question.category,
            "topic": new_question.topic,
            "difficulty": new_question.difficulty
        }
    )
    db.add(admin_log)
    db.commit()
    
    # Invalidate category cache
    if "question_categories" in _cache:
        del _cache["question_categories"]
        del _cache_time["question_categories"]
    
    return schemas.AdminQuestionResponse(
        id=new_question.id,
        title=new_question.title,
        category=new_question.category,
        topic=new_question.topic,
        difficulty=new_question.difficulty,
        created_at=new_question.created_at,
        message="Question created successfully"
    )

@router.post("/admin/questions/upload", status_code=status.HTTP_201_CREATED)
async def upload_questions_simple(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Simple question upload from JSON file
    Expected format: [{"title": "...", "description": "...", "difficulty": "Hard", "topic": "...", "option_a": "...", ...}]
    """
    
    # Validate file type
    if not file.filename.endswith('.json'):
        raise HTTPException(
            status_code=400,
            detail="Only JSON files are supported"
        )
    
    try:
        # Read and parse JSON
        content = await file.read()
        questions_data = json.loads(content)
        
        if not isinstance(questions_data, list):
            raise HTTPException(
                status_code=400,
                detail="JSON must be an array of questions"
            )
        
        # Required fields for each question
        required_fields = ["title", "description", "difficulty", "category", "topic", 
                          "option_a", "option_b", "option_c", "option_d", 
                          "correct_answer", "explanation", "xp_reward"]
        
        added = 0
        errors = []
        
        for idx, q_data in enumerate(questions_data):
            try:
                # Check required fields
                missing_fields = [f for f in required_fields if f not in q_data or not q_data[f]]
                if missing_fields:
                    errors.append(f"Question {idx+1}: Missing fields: {missing_fields}")
                    continue
                
                # Validate difficulty
                if q_data["difficulty"] not in ["Easy", "Medium", "Hard"]:
                    errors.append(f"Question {idx+1}: Invalid difficulty. Must be Easy, Medium, or Hard")
                    continue
                
                # Validate category
                if q_data["category"] not in ["Quants", "Logical", "Linguistics"]:
                    errors.append(f"Question {idx+1}: Invalid category. Must be Quants, Logical, or Linguistics")
                    continue
                
                # Validate correct_answer
                if q_data["correct_answer"] not in ["A", "B", "C", "D"]:
                    errors.append(f"Question {idx+1}: Invalid correct_answer. Must be A, B, C, or D")
                    continue
                
                # Create question
                question = models.Question(
                    title=q_data["title"],
                    description=q_data["description"],
                    difficulty=q_data["difficulty"],
                    category=q_data["category"],  # Required: Quants, Logical, or Linguistics
                    topic=q_data["topic"],
                    sub_topic=q_data.get("subtopic") or q_data.get("sub_topic"),  # Optional subtopic
                    option_a=q_data["option_a"],
                    option_b=q_data["option_b"],
                    option_c=q_data["option_c"],
                    option_d=q_data["option_d"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"],
                    xp_reward=int(q_data["xp_reward"]),
                    initial_difficulty=q_data["difficulty"],
                    heuristic_score=0.3 if q_data["difficulty"] == "Easy" else (0.5 if q_data["difficulty"] == "Medium" else 0.7)
                )
                
                db.add(question)
                added += 1
                
            except Exception as e:
                errors.append(f"Question {idx+1}: {str(e)}")
        
        # Commit all successful additions
        if added > 0:
            db.commit()
        
        # Log admin action
        admin_log = models.AdminActionLog(
            admin_id=current_user.id,
            action_type="upload_questions",
            target_type="question",
            details={
                "total_in_file": len(questions_data),
                "added": added,
                "errors_count": len(errors)
            }
        )
        db.add(admin_log)
        db.commit()
        
        # Clear cache
        if "question_categories" in _cache:
            del _cache["question_categories"]
            del _cache_time["question_categories"]
        
        return {
            "message": "Upload completed",
            "stats": {
                "total_in_file": len(questions_data),
                "added": added,
                "errors_count": len(errors)
            },
            "errors": errors[:10] if errors else []  # Show first 10 errors
        }
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing upload: {str(e)}"
        )


@router.post("/admin/questions/batch", status_code=status.HTTP_201_CREATED)
async def create_questions_batch(
    questions: List[schemas.QuestionCreate],
    current_user: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create multiple questions at once via JSON payload
    Useful for programmatic batch creation
    """
    try:
        created = []
        skipped = []
        
        for q_data in questions:
            # Check if question already exists
            existing = db.query(models.Question).filter(
                models.Question.title == q_data.title
            ).first()
            
            if existing:
                skipped.append(q_data.title)
            else:
                # Convert Pydantic model to dict and map subtopic to sub_topic
                q_dict = q_data.dict()
                if "subtopic" in q_dict:
                    q_dict["sub_topic"] = q_dict.pop("subtopic")
                
                question = models.Question(**q_dict)
                db.add(question)
                created.append(q_data.title)
        
        db.commit()
        
        return {
            "message": "Batch creation complete",
            "stats": {
                "created": len(created),
                "skipped": len(skipped),
                "total": len(questions)
            },
            "created_titles": created[:10],  # Show first 10
            "skipped_titles": skipped[:10]   # Show first 10
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating questions: {str(e)}"
        )


@router.get("/admin/questions/export")
async def export_questions(
    topic: str = None,
    difficulty: str = None,
    current_user: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Export questions to JSON format
    Useful for backup or editing externally
    """
    query = db.query(models.Question)
    
    if topic:
        query = query.filter(models.Question.topic == topic)
    if difficulty:
        query = query.filter(models.Question.difficulty == difficulty)
    
    questions = query.all()
    
    questions_data = []
    for q in questions:
        questions_data.append({
            "title": q.title,
            "description": q.description,
            "difficulty": q.difficulty,
            "topic": q.topic,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "xp_reward": q.xp_reward
        })
    
    return {
        "count": len(questions_data),
        "filters": {
            "topic": topic,
            "difficulty": difficulty
        },
        "questions": questions_data
    }


@router.delete("/admin/questions/{question_id}")
async def delete_question(
    question_id: int,
    current_user: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a specific question"""
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    
    return {"message": f"Question '{question.title}' deleted successfully"}


@router.delete("/admin/questions/bulk-delete")
async def bulk_delete_questions(
    question_ids: List[int],
    current_user: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete multiple questions at once"""
    deleted = db.query(models.Question).filter(
        models.Question.id.in_(question_ids)
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {
        "message": f"Deleted {deleted} questions",
        "deleted_count": deleted
    }


@router.get("/admin/questions/stats")
async def get_questions_stats(
    current_user: models.User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Get statistics about questions in the database"""
    from sqlalchemy import func
    
    total = db.query(func.count(models.Question.id)).scalar()
    
    by_difficulty = db.query(
        models.Question.difficulty,
        func.count(models.Question.id)
    ).group_by(models.Question.difficulty).all()
    
    by_topic = db.query(
        models.Question.topic,
        func.count(models.Question.id)
    ).group_by(models.Question.topic).all()
    
    return {
        "total_questions": total,
        "by_difficulty": dict(by_difficulty),
        "by_topic": dict(by_topic)
    }
