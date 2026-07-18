import datetime
from typing import List, Dict, Any


class StudyPlanner:
    """
    Planning engine that takes a parsed syllabus hierarchy tree and distributes
    study topics across a specific date range, balancing workload by complexity.
    """

    @classmethod
    def _get_leaf_nodes(cls, nodes: List[Dict[str, Any]], current_prefix: str = "") -> List[Dict[str, Any]]:
        """
        Recursively extract all leaf nodes (topics with no children) from the tree.
        Preserves the full hierarchical path in 'full_path'.
        """
        leaves = []
        for node in nodes:
            # Build breadcrumb pathway prefix
            path_title = node.get("title", "")
            new_prefix = f"{current_prefix} > {path_title}" if current_prefix else path_title
            
            if not node.get("children"):
                # Leaf node: estimate its base complexity
                leaf = {
                    "id": node.get("id"),
                    "title": path_title,
                    "full_path": new_prefix,
                    "importance_hint": node.get("importance_hint", 1.0),
                    "complexity": node.get("importance_hint", 1.0) * (1.2 if len(path_title) > 30 else 1.0)
                }
                leaves.append(leaf)
            else:
                leaves.extend(cls._get_leaf_nodes(node["children"], new_prefix))
        return leaves

    @classmethod
    def generate_plan(cls, parsed_tree: List[Dict[str, Any]], start_date: datetime.date, end_date: datetime.date) -> List[Dict[str, Any]]:
        """
        Generates a daily study schedule distributing leaf topics across start_date to end_date.
        """
        # 1. Calculate total available days
        total_days = (end_date - start_date).days + 1
        if total_days <= 0:
            raise ValueError("End date must be greater than or equal to start_date.")

        # 2. Extract leaf nodes
        leaf_nodes = cls._get_leaf_nodes(parsed_tree)
        if not leaf_nodes:
            # Fallback if tree is empty
            return [
                {
                    "day_number": i + 1,
                    "date": (start_date + datetime.timedelta(days=i)).isoformat(),
                    "topics": [],
                    "is_review": True,
                    "notes": "No syllabus topics available. General study review session."
                }
                for i in range(total_days)
            ]

        num_topics = len(leaf_nodes)
        schedule = []

        # Case A: More days than topics (Spaced planning with automatic review/catch-up days)
        if total_days >= num_topics:
            # Calculate integer spacing index
            spacing = total_days / num_topics
            topic_assignments = {}
            for idx, topic in enumerate(leaf_nodes):
                assigned_day = int(idx * spacing)
                topic_assignments[assigned_day] = topic

            last_assigned_topic = None
            for day_idx in range(total_days):
                current_date = start_date + datetime.timedelta(days=day_idx)
                day_num = day_idx + 1

                if day_idx in topic_assignments:
                    topic = topic_assignments[day_idx]
                    last_assigned_topic = topic
                    schedule.append({
                        "day_number": day_num,
                        "date": current_date.isoformat(),
                        "topics": [topic],
                        "is_review": False,
                        "notes": f"Primary focus: {topic['title']}"
                    })
                else:
                    if last_assigned_topic:
                        notes = f"Revision and catch-up session for: {last_assigned_topic['title']}"
                    else:
                        notes = "Initial reading and study alignment."
                    
                    schedule.append({
                        "day_number": day_num,
                        "date": current_date.isoformat(),
                        "topics": [],
                        "is_review": True,
                        "notes": notes
                    })

        # Case B: More topics than days (Grouping topics into days based on complexity limits)
        else:
            total_complexity = sum(t["complexity"] for t in leaf_nodes)
            target_daily_complexity = total_complexity / total_days

            days_topics = [[] for _ in range(total_days)]
            current_day_idx = 0
            current_day_complexity = 0.0

            for idx, topic in enumerate(leaf_nodes):
                days_topics[current_day_idx].append(topic)
                current_day_complexity += topic["complexity"]

                # Check if we should advance to the next day
                remaining_topics = num_topics - 1 - idx
                remaining_days = total_days - 1 - current_day_idx

                # If remaining days matches remaining topics, we must advance to ensure no empty days
                if remaining_topics <= remaining_days:
                    current_day_idx += 1
                    current_day_complexity = 0.0
                elif current_day_complexity >= target_daily_complexity and remaining_days > 0:
                    current_day_idx += 1
                    current_day_complexity = 0.0

            for day_idx in range(total_days):
                current_date = start_date + datetime.timedelta(days=day_idx)
                day_num = day_idx + 1
                assigned_topics = days_topics[day_idx]
                
                if assigned_topics:
                    topics_list = ", ".join([t["title"] for t in assigned_topics])
                    notes = f"Cover: {topics_list}"
                else:
                    notes = "General study review session."

                schedule.append({
                    "day_number": day_num,
                    "date": current_date.isoformat(),
                    "topics": assigned_topics,
                    "is_review": False,
                    "notes": notes
                })

        return schedule
