from typing import Any, List, Optional
from datetime import date
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.backend.core.database import get_db
from app.backend.api.v1.dependencies import get_current_user
from app.backend.models.user import User
from app.backend.models.plan import StudyPlan
from app.backend.models.syllabus import Syllabus
from app.backend.models.progress import DailyProgress
from app.backend.schemas.plan import StudyPlanCreate, StudyPlanResponse
from app.backend.planners.study_planner import StudyPlanner
from app.backend.planners.replanner import Replanner

router = APIRouter()


@router.post("/", response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan_in: StudyPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create a new study plan for a syllabus.
    """
    # Ensure the syllabus belongs to the current user
    syllabus = (
        db.query(Syllabus)
        .filter(Syllabus.id == plan_in.syllabus_id, Syllabus.user_id == current_user.id)
        .first()
    )
    if not syllabus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated syllabus not found for this user."
        )

    # Automatically generate study plan schedule
    parsed_tree = syllabus.parsed_tree_json or []
    try:
        plan_schedule = StudyPlanner.generate_plan(
            parsed_tree,
            plan_in.start_date,
            plan_in.end_date
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    db_plan = StudyPlan(
        syllabus_id=plan_in.syllabus_id,
        start_date=plan_in.start_date,
        end_date=plan_in.end_date,
        plan_json=plan_schedule,
        status="active",
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.get("/", response_model=List[StudyPlanResponse])
def read_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve all study plans for the active user.
    """
    plans = (
        db.query(StudyPlan)
        .join(Syllabus)
        .filter(Syllabus.user_id == current_user.id)
        .all()
    )
    return plans


@router.get("/{plan_id}", response_model=StudyPlanResponse)
def read_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get a study plan by ID if owned by active user.
    """
    plan = (
        db.query(StudyPlan)
        .join(Syllabus)
        .filter(StudyPlan.id == plan_id, Syllabus.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan not found"
        )
    return plan


@router.post("/{plan_id}/replan", response_model=StudyPlanResponse)
def trigger_manual_replan(
    plan_id: int,
    from_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Manually trigger a replan starting from a specified date.
    Defaults to tomorrow if from_date is not provided.
    """
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

    replan_start = from_date or (datetime.date.today() + datetime.timedelta(days=1))

    # Gather all completed topics from all progress records
    all_progress = db.query(DailyProgress).filter(DailyProgress.plan_id == plan_id).all()
    completed_topic_ids = set()
    for p in all_progress:
        if p.completed_topics:
            completed_topic_ids.update(p.completed_topics)

    try:
        new_schedule = Replanner.replan(
            plan.syllabus.parsed_tree_json or [],
            plan.plan_json,
            completed_topic_ids,
            replan_start,
            plan.end_date
        )
        plan.plan_json = new_schedule
        db.commit()
        db.refresh(plan)
        return plan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
