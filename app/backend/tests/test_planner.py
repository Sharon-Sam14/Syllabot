import datetime
import pytest
from app.backend.planners.study_planner import StudyPlanner


def test_planner_invalid_dates():
    # End date before start date
    start = datetime.date(2026, 7, 18)
    end = datetime.date(2026, 7, 17)
    with pytest.raises(ValueError) as excinfo:
        StudyPlanner.generate_plan([], start, end)
    assert "End date must be greater than or equal to start_date" in str(excinfo.value)


def test_planner_spaced_out():
    # 3 topics, 5 days. Should generate 3 study days and 2 review/catch-up days
    tree = [
        {
            "title": "Unit 1",
            "level": 0,
            "children": [
                {"title": "Topic A", "level": 1, "importance_hint": 1.0},
                {"title": "Topic B", "level": 1, "importance_hint": 1.0},
                {"title": "Topic C", "level": 1, "importance_hint": 1.0}
            ]
        }
    ]
    
    start = datetime.date(2026, 7, 1)
    end = datetime.date(2026, 7, 5)
    
    plan = StudyPlanner.generate_plan(tree, start, end)
    
    assert len(plan) == 5
    
    # Check days
    assigned_days = [d for d in plan if not d["is_review"]]
    review_days = [d for d in plan if d["is_review"]]
    
    assert len(assigned_days) == 3
    assert len(review_days) == 2
    
    # Check assignment dates
    assert plan[0]["topics"][0]["title"] == "Topic A"
    assert plan[0]["is_review"] is False
    
    # Day 2 gets Topic B (due to float spacing assignment)
    assert plan[1]["topics"][0]["title"] == "Topic B"
    assert plan[1]["is_review"] is False
    
    # Day 3 is a review day
    assert plan[2]["is_review"] is True
    assert "Topic B" in plan[2]["notes"]
    
    # Assert correct day numbers
    assert [d["day_number"] for d in plan] == [1, 2, 3, 4, 5]


def test_planner_compact():
    # 5 topics, 3 days. Topics must be grouped.
    tree = [
        {
            "title": "Unit 1",
            "level": 0,
            "children": [
                {"title": "Topic 1", "level": 1, "importance_hint": 1.0},
                {"title": "Topic 2", "level": 1, "importance_hint": 1.0},
                {"title": "Topic 3", "level": 1, "importance_hint": 1.0},
                {"title": "Topic 4", "level": 1, "importance_hint": 1.0},
                {"title": "Topic 5", "level": 1, "importance_hint": 1.0}
            ]
        }
    ]
    
    start = datetime.date(2026, 7, 1)
    end = datetime.date(2026, 7, 3)
    
    plan = StudyPlanner.generate_plan(tree, start, end)
    
    assert len(plan) == 3
    
    # All days should have study items, no review days
    assert all(not d["is_review"] for d in plan)
    
    # Total topics across all days should equal 5
    total_assigned_topics = sum(len(d["topics"]) for d in plan)
    assert total_assigned_topics == 5
    
    # Ensure they are distributed (e.g. roughly 2-2-1 or 2-1-2)
    assert len(plan[0]["topics"]) > 0
    assert len(plan[1]["topics"]) > 0
    assert len(plan[2]["topics"]) > 0
