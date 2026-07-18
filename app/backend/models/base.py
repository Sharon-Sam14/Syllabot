# Import all models to ensure Base.metadata has registered them before Alembic runs migrations
from app.backend.core.database import Base
from app.backend.models.user import User
from app.backend.models.syllabus import Syllabus
from app.backend.models.plan import StudyPlan
from app.backend.models.progress import DailyProgress
