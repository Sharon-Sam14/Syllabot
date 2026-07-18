from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.backend.core.database import get_db
from app.backend.api.v1.dependencies import get_current_user
from app.backend.models.user import User
from app.backend.models.syllabus import Syllabus
from app.backend.schemas.syllabus import SyllabusCreate, SyllabusResponse

from app.backend.parsers.syllabus_parser import SyllabusParser

router = APIRouter()


@router.post("/", response_model=SyllabusResponse, status_code=status.HTTP_201_CREATED)
def create_syllabus(
    syllabus_in: SyllabusCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Ingest a new raw syllabus.
    """
    parsed_tree = SyllabusParser.parse(syllabus_in.raw_text)
    db_syllabus = Syllabus(
        user_id=current_user.id,
        raw_text=syllabus_in.raw_text,
        parsed_tree_json=parsed_tree,
    )
    db.add(db_syllabus)
    db.commit()
    db.refresh(db_syllabus)
    return db_syllabus


@router.get("/", response_model=List[SyllabusResponse])
def read_syllabi(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve all syllabi for the active user.
    """
    syllabi = db.query(Syllabus).filter(Syllabus.user_id == current_user.id).all()
    return syllabi


@router.get("/{syllabus_id}", response_model=SyllabusResponse)
def read_syllabus(
    syllabus_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get a syllabus by ID if owned by active user.
    """
    syllabus = (
        db.query(Syllabus)
        .filter(Syllabus.id == syllabus_id, Syllabus.user_id == current_user.id)
        .first()
    )
    if not syllabus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Syllabus not found"
        )
    return syllabus
