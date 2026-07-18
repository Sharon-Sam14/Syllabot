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
        db_progress = existing_record
    else:
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

    # Automatically check and trigger replanning if the student falls behind
    import datetime
    from app.backend.planners.replanner import Replanner

    # Collect all completed topic IDs across all check-ins for this plan
    all_progress = db.query(DailyProgress).filter(DailyProgress.plan_id == plan_id).all()
    completed_topic_ids = set()
    for p in all_progress:
        if p.completed_topics:
            completed_topic_ids.update(p.completed_topics)

    is_behind = Replanner.is_student_behind(
        plan.plan_json,
        completed_topic_ids,
        progress_in.date
    )

    if is_behind:
        # Schedule the remaining topics starting from tomorrow onwards
        tomorrow = progress_in.date + datetime.timedelta(days=1)
        try:
            new_schedule = Replanner.replan(
                plan.syllabus.parsed_tree_json or [],
                plan.plan_json,
                completed_topic_ids,
                tomorrow,
                plan.end_date
            )
            plan.plan_json = new_schedule
            db.commit()
            db.refresh(plan)
        except ValueError:
            # Fail gracefully if plan horizon is exceeded, leaving schedule as-is
            pass

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
