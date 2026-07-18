import datetime
import pytest
from app.backend.planners.replanner import Replanner


def test_is_student_behind():
    # Plan with 3 days
    schedule = [
        {
            "date": "2026-07-10",
            "topics": [{"id": "topic1", "title": "Topic 1"}]
        },
        {
            "date": "2026-07-11",
            "topics": [{"id": "topic2", "title": "Topic 2"}]
        },
        {
            "date": "2026-07-12",
            "topics": [{"id": "topic3", "title": "Topic 3"}]
        }
    ]

    # Current date is July 11.
    # Topic 1 completed, Topic 2 not completed -> Student is behind
    completed = {"topic1"}
    assert Replanner.is_student_behind(schedule, completed, datetime.date(2026, 7, 11)) is True

    # Topic 1 and Topic 2 completed -> Student is on track
    completed = {"topic1", "topic2"}
    assert Replanner.is_student_behind(schedule, completed, datetime.date(2026, 7, 11)) is False

    # Topic 1, Topic 2, and Topic 3 completed -> Student is ahead
    completed = {"topic1", "topic2", "topic3"}
    assert Replanner.is_student_behind(schedule, completed, datetime.date(2026, 7, 11)) is False

    # Current date is July 10, nothing completed -> On track for today's assignment until check-in fails
    # Wait, if topic1 is scheduled for July 10, and it is not completed on July 10:
    # is_student_behind checks if any topic on or before today is uncompleted.
    # So if they check in at the end of July 10, and topic1 is uncompleted, yes, they are behind.
    completed = set()
    assert Replanner.is_student_behind(schedule, completed, datetime.date(2026, 7, 10)) is True


def test_replan_behind():
    # 5-day plan, 5 topics.
    syllabus_tree = [
        {
            "title": "Unit 1",
            "children": [
                {"id": "t1", "title": "Topic 1", "importance_hint": 1.0},
                {"id": "t2", "title": "Topic 2", "importance_hint": 1.0},
                {"id": "t3", "title": "Topic 3", "importance_hint": 1.0},
                {"id": "t4", "title": "Topic 4", "importance_hint": 1.0},
                {"id": "t5", "title": "Topic 5", "importance_hint": 1.0}
            ]
        }
    ]

    original_schedule = [
        {"day_number": 1, "date": "2026-07-01", "topics": [{"id": "t1", "title": "Topic 1", "complexity": 1.0}], "is_review": False},
        {"day_number": 2, "date": "2026-07-02", "topics": [{"id": "t2", "title": "Topic 2", "complexity": 1.0}], "is_review": False},
        {"day_number": 3, "date": "2026-07-03", "topics": [{"id": "t3", "title": "Topic 3", "complexity": 1.0}], "is_review": False},
        {"day_number": 4, "date": "2026-07-04", "topics": [{"id": "t4", "title": "Topic 4", "complexity": 1.0}], "is_review": False},
        {"day_number": 5, "date": "2026-07-05", "topics": [{"id": "t5", "title": "Topic 5", "complexity": 1.0}], "is_review": False}
    ]

    # Student logs check-in on July 2 (Day 2).
    # Completed: Topic 1.
    # Missed: Topic 2.
    # We replan starting July 3 (Day 3).
    # Remaining topics to study are: Topic 2, Topic 3, Topic 4, Topic 5.
    # Remaining days are: July 3, July 4, July 5 (3 days).
    # Since there are 4 topics and 3 days, they will be grouped: 4 topics across 3 days.
    
    completed = {"t1"}
    new_schedule = Replanner.replan(
        syllabus_tree,
        original_schedule,
        completed,
        datetime.date(2026, 7, 3),
        datetime.date(2026, 7, 5)
    )

    # Output plan length should still be 5
    assert len(new_schedule) == 5

    # Day 1 & Day 2 (historical) must be preserved exactly as originally scheduled
    assert new_schedule[0]["date"] == "2026-07-01"
    assert new_schedule[0]["topics"][0]["id"] == "t1"
    
    assert new_schedule[1]["date"] == "2026-07-02"
    assert new_schedule[1]["topics"][0]["id"] == "t2" # History says t2 was scheduled here, and it is preserved!

    # Day 3, 4, 5 should represent the replanned schedule for remaining topics (t2, t3, t4, t5)
    assert new_schedule[2]["date"] == "2026-07-03"
    # Ensure they are re-routed. The total number of topics assigned to Day 3, 4, 5 should be 4 (t2, t3, t4, t5)
    remaining_assignments = []
    for day in new_schedule[2:]:
        remaining_assignments.extend([t["id"] for t in day["topics"]])
        
    assert set(remaining_assignments) == {"t2", "t3", "t4", "t5"}
    assert [d["day_number"] for d in new_schedule] == [1, 2, 3, 4, 5]
