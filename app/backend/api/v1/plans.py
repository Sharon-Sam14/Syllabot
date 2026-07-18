from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.backend.core.database import get_db
from app.backend.api.v1.dependencies import get_current_user
from app.backend.models.user import User
from app.backend.models.plan import StudyPlan
from app.backend.models.syllabus import Syllabus
from app.backend.schemas.plan import StudyPlanCreate, StudyPlanResponse
from app.backend.planners.study_planner import StudyPlanner

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
