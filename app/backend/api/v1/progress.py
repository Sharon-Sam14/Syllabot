from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.backend.core.database import get_db
from app.backend.api.v1.dependencies import get_current_user
from app.backend.models.user import User
from app.backend.models.plan import StudyPlan
from app.backend.models.syllabus import Syllabus
from app.backend.models.progress import DailyProgress
from app.backend.schemas.progress import DailyProgressCreate, DailyProgressResponse

router = APIRouter()


@router.post("/{plan_id}", response_model=DailyProgressResponse, status_code=status.HTTP_201_CREATED)
def create_progress_record(
    plan_id: int,
    progress_in: DailyProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Log a daily check-in progress record for a plan.
    """
    # Verify the plan belongs to current user
    plan = (
        db.query(StudyPlan)
        .join(Syllabus)
        .filter(StudyPlan.id == plan_id, Syllabus.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan not found for this user."
        )

    # Check if a progress record already exists for this date and plan
    existing_record = (
        db.query(DailyProgress)
        .filter(DailyProgress.plan_id == plan_id, DailyProgress.date == progress_in.date)
        .first()
    )
    if existing_record:
        # Overwrite or update
        existing_record.completed_hours = progress_in.completed_hours
        existing_record.completed_topics = progress_in.completed_topics
        existing_record.check_in_note = progress_in.check_in_note
        db.commit()
        db.refresh(existing_record)
        return existing_record

    db_progress = DailyProgress(
        plan_id=plan_id,
        date=progress_in.date,
        completed_hours=progress_in.completed_hours,
        completed_topics=progress_in.completed_topics,
        check_in_note=progress_in.check_in_note,
    )
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress


@router.get("/{plan_id}", response_model=List[DailyProgressResponse])
def read_progress_records(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve all daily progress records logged for a study plan.
    """
    # Verify ownership
    plan = (
        db.query(StudyPlan)
        .join(Syllabus)
        .filter(StudyPlan.id == plan_id, Syllabus.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan not found for this user."
        )

    records = db.query(DailyProgress).filter(DailyProgress.plan_id == plan_id).all()
    return records
