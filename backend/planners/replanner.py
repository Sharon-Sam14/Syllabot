import datetime
from typing import List, Dict, Any, Set
from backend.planners.study_planner import StudyPlanner


class Replanner:
    """
    Replanning engine that evaluates progress and dynamically recalculates
    remaining topics across remaining days when a student falls behind.
    """

    @classmethod
    def is_student_behind(
        cls,
        schedule: List[Dict[str, Any]],
        completed_topic_ids: Set[str],
        current_date: datetime.date
    ) -> bool:
        """
        Evaluate if there are any topics scheduled for today or earlier
        that have not been completed.
        """
        for day in schedule:
            day_date = datetime.date.fromisoformat(day["date"])
            # Evaluate days up to and including today
            if day_date <= current_date:
                for topic in day.get("topics", []):
                    if topic["id"] not in completed_topic_ids:
                        return True
        return False

    @classmethod
    def replan(
        cls,
        original_syllabus_tree: List[Dict[str, Any]],
        schedule: List[Dict[str, Any]],
        completed_topic_ids: Set[str],
        current_date: datetime.date,
        end_date: datetime.date
    ) -> List[Dict[str, Any]]:
        """
        Preserve completed history and recalculate remaining workload across remaining days.
        """
        # 1. Extract all leaf topics from the original syllabus tree
        all_leaves = StudyPlanner._get_leaf_nodes(original_syllabus_tree)
        
        # 2. Filter out already completed topics
        remaining_topics = [t for t in all_leaves if t["id"] not in completed_topic_ids]

        # 3. Separate history from future plans
        # Days strictly before current_date are preserved
        current_date_str = current_date.isoformat()
        historical_days = [day for day in schedule if day["date"] < current_date_str]

        # Calculate remaining days from current_date to end_date
        remaining_days = (end_date - current_date).days + 1

        if remaining_days <= 0:
            if remaining_topics:
                raise ValueError("Cannot replan: the plan horizon has already passed, but there are uncompleted topics.")
            # If everything is completed, we just keep the history
            return schedule

        # 4. Generate schedule for the remaining workload
        if remaining_topics:
            remaining_schedule = StudyPlanner.generate_plan(
                remaining_topics,
                current_date,
                end_date
            )
        else:
            # Everything is completed: fill the remaining days with review sessions
            remaining_schedule = [
                {
                    "day_number": i + 1,
                    "date": (current_date + datetime.timedelta(days=i)).isoformat(),
                    "topics": [],
                    "is_review": True,
                    "notes": "All topics completed! Spaced review and recall practice."
                }
                for i in range(remaining_days)
            ]

        # 5. Combine history and future schedules
        combined_schedule = []
        combined_schedule.extend(historical_days)
        combined_schedule.extend(remaining_schedule)

        # 6. Re-number days sequentially
        for idx, day in enumerate(combined_schedule):
            day["day_number"] = idx + 1

        return combined_schedule
