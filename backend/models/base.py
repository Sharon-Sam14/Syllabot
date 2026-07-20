# Import all models to ensure Base.metadata has registered them before Alembic runs migrations
from backend.core.database import Base
from backend.models.user import User
from backend.models.syllabus import Syllabus
from backend.models.plan import StudyPlan
from backend.models.progress import DailyProgress
from backend.models.user_memory import UserMemory

