import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.models.syllabus import Syllabus
from backend.models.plan import StudyPlan
from backend.models.progress import DailyProgress
from backend.planners.study_planner import StudyPlanner
from backend.planners.replanner import Replanner


class SyllabotTools:
    """
    Exposes existing backend functionality as AI tools.
    All operations are verified against the current authenticated user and database session.
    """

    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user

    def current_user_info(self) -> Dict[str, Any]:
        """
        Retrieve information about the currently logged-in user.
        """
        return {
            "id": self.current_user.id,
            "name": self.current_user.name,
            "email": self.current_user.email,
        }

    def get_topics(self, syllabus_id: int) -> Dict[str, Any]:
        """
        Retrieve all structured topics and hierarchy for a specific syllabus.
        """
        syllabus = (
            self.db.query(Syllabus)
            .filter(Syllabus.id == syllabus_id, Syllabus.user_id == self.current_user.id)
            .first()
        )
        if not syllabus:
            return {"error": f"Syllabus with ID {syllabus_id} not found."}

        return {
            "syllabus_id": syllabus.id,
            "parsed_tree": syllabus.parsed_tree_json or [],
        }

    def get_priority_topics(self, syllabus_id: int) -> Dict[str, Any]:
        """
        Get the most important or complex topics in the syllabus sorted by importance.
        """
        syllabus = (
            self.db.query(Syllabus)
            .filter(Syllabus.id == syllabus_id, Syllabus.user_id == self.current_user.id)
            .first()
        )
        if not syllabus:
            return {"error": f"Syllabus with ID {syllabus_id} not found."}

        tree = syllabus.parsed_tree_json or []
        leaves = StudyPlanner._get_leaf_nodes(tree)
        # Sort by importance descending
        priority_topics = sorted(leaves, key=lambda x: x.get("importance_hint", 1.0), reverse=True)
        return {
            "syllabus_id": syllabus_id,
            "priority_topics": priority_topics
        }

    def search_topic(self, syllabus_id: int, query: str) -> Dict[str, Any]:
        """
        Search for a topic in the syllabus by keyword match.
        """
        syllabus = (
            self.db.query(Syllabus)
            .filter(Syllabus.id == syllabus_id, Syllabus.user_id == self.current_user.id)
            .first()
        )
        if not syllabus:
            return {"error": f"Syllabus with ID {syllabus_id} not found."}

        tree = syllabus.parsed_tree_json or []
        leaves = StudyPlanner._get_leaf_nodes(tree)
        results = [
            t for t in leaves
            if query.lower() in t.get("title", "").lower() or query.lower() in t.get("full_path", "").lower()
        ]
        return {
            "syllabus_id": syllabus_id,
            "query": query,
            "matches": results
        }

    def generate_plan(self, syllabus_id: int, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate a study plan schedule for a syllabus between start_date and end_date.
        Dates must be in ISO format (YYYY-MM-DD).
        """
        syllabus = (
            self.db.query(Syllabus)
            .filter(Syllabus.id == syllabus_id, Syllabus.user_id == self.current_user.id)
            .first()
        )
        if not syllabus:
            return {"error": f"Syllabus with ID {syllabus_id} not found."}

        try:
            parsed_start = datetime.date.fromisoformat(start_date)
            parsed_end = datetime.date.fromisoformat(end_date)
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}

        try:
            plan_schedule = StudyPlanner.generate_plan(
                syllabus.parsed_tree_json or [],
                parsed_start,
                parsed_end
            )
        except ValueError as e:
            return {"error": str(e)}

        db_plan = StudyPlan(
            syllabus_id=syllabus_id,
            start_date=parsed_start,
            end_date=parsed_end,
            plan_json=plan_schedule,
            status="active"
        )
        self.db.add(db_plan)
        self.db.commit()
        self.db.refresh(db_plan)

        return {
            "plan_id": db_plan.id,
            "syllabus_id": db_plan.syllabus_id,
            "start_date": db_plan.start_date.isoformat(),
            "end_date": db_plan.end_date.isoformat(),
            "status": db_plan.status,
            "schedule": db_plan.plan_json
        }

    def replan_plan(self, plan_id: int, from_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Manually trigger recalculation/replanning of the study schedule from a specific date.
        If from_date is omitted, defaults to tomorrow. Date must be in YYYY-MM-DD.
        """
        plan = (
            self.db.query(StudyPlan)
            .join(Syllabus)
            .filter(StudyPlan.id == plan_id, Syllabus.user_id == self.current_user.id)
            .first()
        )
        if not plan:
            return {"error": f"Study plan with ID {plan_id} not found."}

        try:
            replan_start = (
                datetime.date.fromisoformat(from_date)
                if from_date else (datetime.date.today() + datetime.timedelta(days=1))
            )
        except ValueError:
            return {"error": "Invalid from_date format. Use YYYY-MM-DD."}

        # Gather all completed topics from all progress records
        all_progress = self.db.query(DailyProgress).filter(DailyProgress.plan_id == plan_id).all()
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
            self.db.commit()
            self.db.refresh(plan)
            return {
                "plan_id": plan.id,
                "status": plan.status,
                "start_date": plan.start_date.isoformat(),
                "end_date": plan.end_date.isoformat(),
                "schedule": plan.plan_json
            }
        except ValueError as e:
            return {"error": str(e)}

    def today_schedule(self, plan_id: int) -> Dict[str, Any]:
        """
        Get the scheduled topics and notes for today.
        """
        plan = (
            self.db.query(StudyPlan)
            .join(Syllabus)
            .filter(StudyPlan.id == plan_id, Syllabus.user_id == self.current_user.id)
            .first()
        )
        if not plan:
            return {"error": f"Study plan with ID {plan_id} not found."}

        today_str = datetime.date.today().isoformat()
        schedule = plan.plan_json or []
        for day in schedule:
            if day.get("date") == today_str:
                return {
                    "plan_id": plan_id,
                    "date": today_str,
                    "day_number": day.get("day_number"),
                    "topics": day.get("topics", []),
                    "is_review": day.get("is_review", False),
                    "notes": day.get("notes", "")
                }

        return {
            "plan_id": plan_id,
            "date": today_str,
            "message": "No scheduled study day found matching today's date."
        }

    def remaining_topics(self, plan_id: int) -> Dict[str, Any]:
        """
        Get a list of topics that are not yet marked as completed.
        """
        plan = (
            self.db.query(StudyPlan)
            .join(Syllabus)
            .filter(StudyPlan.id == plan_id, Syllabus.user_id == self.current_user.id)
            .first()
        )
        if not plan:
            return {"error": f"Study plan with ID {plan_id} not found."}

        all_leaves = StudyPlanner._get_leaf_nodes(plan.syllabus.parsed_tree_json or [])
        all_progress = self.db.query(DailyProgress).filter(DailyProgress.plan_id == plan_id).all()
        completed_topic_ids = set()
        for p in all_progress:
            if p.completed_topics:
                completed_topic_ids.update(p.completed_topics)

        remaining = [t for t in all_leaves if t["id"] not in completed_topic_ids]
        return {
            "plan_id": plan_id,
            "total_topics_count": len(all_leaves),
            "completed_topics_count": len(completed_topic_ids),
            "remaining_topics_count": len(remaining),
            "remaining_topics": remaining
        }

    def log_progress(
        self,
        plan_id: int,
        date: str,
        completed_hours: float,
        completed_topics: List[str],
        check_in_note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log study progress for a specific day. Automatically triggers a replan if the user is behind.
        Date must be YYYY-MM-DD.
        """
        plan = (
            self.db.query(StudyPlan)
            .join(Syllabus)
            .filter(StudyPlan.id == plan_id, Syllabus.user_id == self.current_user.id)
            .first()
        )
        if not plan:
            return {"error": f"Study plan with ID {plan_id} not found."}

        try:
            progress_date = datetime.date.fromisoformat(date)
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}

        # Check if a progress record already exists for this date and plan
        existing_record = (
            self.db.query(DailyProgress)
            .filter(DailyProgress.plan_id == plan_id, DailyProgress.date == progress_date)
            .first()
        )
        if existing_record:
            existing_record.completed_hours = completed_hours
            existing_record.completed_topics = completed_topics
            existing_record.check_in_note = check_in_note
            db_progress = existing_record
        else:
            db_progress = DailyProgress(
                plan_id=plan_id,
                date=progress_date,
                completed_hours=completed_hours,
                completed_topics=completed_topics,
                check_in_note=check_in_note,
            )
            self.db.add(db_progress)

        self.db.commit()
        self.db.refresh(db_progress)

        # Collect all completed topic IDs across all check-ins for this plan
        all_progress = self.db.query(DailyProgress).filter(DailyProgress.plan_id == plan_id).all()
        completed_topic_ids = set()
        for p in all_progress:
            if p.completed_topics:
                completed_topic_ids.update(p.completed_topics)

        # Re-evaluate logic for auto-replanning if student is behind
        is_behind = Replanner.is_student_behind(
            plan.plan_json,
            completed_topic_ids,
            progress_date
        )

        replanned_schedule = None
        if is_behind:
            tomorrow = progress_date + datetime.timedelta(days=1)
            try:
                new_schedule = Replanner.replan(
                    plan.syllabus.parsed_tree_json or [],
                    plan.plan_json,
                    completed_topic_ids,
                    tomorrow,
                    plan.end_date
                )
                plan.plan_json = new_schedule
                self.db.commit()
                self.db.refresh(plan)
                replanned_schedule = plan.plan_json
            except ValueError:
                # Fail gracefully if plan horizon is exceeded, leaving schedule as-is
                pass

        return {
            "progress_id": db_progress.id,
            "date": db_progress.date.isoformat(),
            "completed_hours": db_progress.completed_hours,
            "completed_topics": db_progress.completed_topics,
            "check_in_note": db_progress.check_in_note,
            "was_replanned": is_behind,
            "schedule": replanned_schedule if is_behind else plan.plan_json
        }

    def completion_percentage(self, plan_id: int) -> Dict[str, Any]:
        """
        Get the completion percentage and numerical metrics for the plan.
        """
        plan = (
            self.db.query(StudyPlan)
            .join(Syllabus)
            .filter(StudyPlan.id == plan_id, Syllabus.user_id == self.current_user.id)
            .first()
        )
        if not plan:
            return {"error": f"Study plan with ID {plan_id} not found."}

        all_leaves = StudyPlanner._get_leaf_nodes(plan.syllabus.parsed_tree_json or [])
        all_progress = self.db.query(DailyProgress).filter(DailyProgress.plan_id == plan_id).all()
        completed_topic_ids = set()
        for p in all_progress:
            if p.completed_topics:
                completed_topic_ids.update(p.completed_topics)

        total = len(all_leaves)
        completed = len(completed_topic_ids)
        percentage = (completed / total * 100.0) if total > 0 else 0.0

        return {
            "plan_id": plan_id,
            "total_topics": total,
            "completed_topics": completed,
            "completion_percentage": round(percentage, 2)
        }
