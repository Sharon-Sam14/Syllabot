import re
from typing import List, Dict, Any, Optional

# Regular expression patterns for hierarchy parsing
UNIT_PATTERN = re.compile(r"^\s*(Unit|Module|Part)\s+(\w+)(?:\s*[:-]\s*|\s+)?(.*)$", re.IGNORECASE)
CHAPTER_PATTERN = re.compile(r"^\s*(Chapter|Section|Topic)\s+(\w+)(?:\s*[:-]\s*|\s+)?(.*)$", re.IGNORECASE)
DECIMAL_PATTERN = re.compile(r"^\s*(\d+(?:\.\d+)+)(?:\s*[:-]\s*|\s+)?(.*)$")
BULLET_PATTERN = re.compile(r"^\s*([-*+•])\s*(.*)$")


class SyllabusParser:
    """
    Syllabus ingestion parser that converts unstructured free-text syllabus input
    into a structured hierarchical tree using a stack-based shift-reduce approach.
    """

    @staticmethod
    def _infer_importance(title: str) -> float:
        """
        Estimate importance weighting based on keywords found in the title.
        """
        title_lower = title.lower()
        low_importance_keywords = ["intro", "overview", "basic", "revision", "preliminary", "welcome", "history"]
        high_importance_keywords = ["advanced", "complex", "implementation", "design", "analysis", "exam", "core", "theory", "database"]

        if any(kw in title_lower for kw in low_importance_keywords):
            return 0.6
        if any(kw in title_lower for kw in high_importance_keywords):
            return 1.4
        return 1.0

    @staticmethod
    def parse(raw_text: str) -> List[Dict[str, Any]]:
        """
        Parse raw syllabus text and return a tree representation of topics.
        """
        lines = raw_text.splitlines()
        root_nodes: List[Dict[str, Any]] = []
        stack: List[Dict[str, Any]] = []
        node_id_counter = 1

        for line_idx, raw_line in enumerate(lines):
            stripped = raw_line.strip()
            if not stripped:
                continue

            # Calculate leading spaces to measure indentation
            leading_spaces = len(raw_line) - len(raw_line.lstrip())
            indent_level = leading_spaces // 2  # assume 2 spaces per indentation level

            # Identify token category and establish level and confidence
            title = stripped
            level = 2  # default level
            confidence = 1.0

            # Match patterns
            unit_match = UNIT_PATTERN.match(stripped)
            chapter_match = CHAPTER_PATTERN.match(stripped)
            decimal_match = DECIMAL_PATTERN.match(stripped)
            bullet_match = BULLET_PATTERN.match(stripped)

            if unit_match:
                prefix, identifier, rest = unit_match.groups()
                title = f"{prefix} {identifier}: {rest}" if rest else f"{prefix} {identifier}"
                level = 0
                confidence = 1.0
            elif chapter_match:
                prefix, identifier, rest = chapter_match.groups()
                title = f"{prefix} {identifier}: {rest}" if rest else f"{prefix} {identifier}"
                level = 1
                confidence = 1.0
            elif decimal_match:
                num_prefix, rest = decimal_match.groups()
                title = f"{num_prefix} {rest}" if rest else num_prefix
                # Level matches decimal count: 1.1 -> Level 2; 1.1.1 -> Level 3
                level = num_prefix.count(".") + 1
                confidence = 1.0
            elif bullet_match:
                bullet_char, rest = bullet_match.groups()
                title = rest
                # Level relies on indentation
                level = 2 + indent_level
                confidence = 0.8
            else:
                # No clear structural prefix; treat as sub-details or free text
                level = 3 + indent_level
                confidence = 0.4

            importance = SyllabusParser._infer_importance(title)

            # Create structured node object
            node = {
                "id": f"node_{node_id_counter}",
                "title": title,
                "parent_id": None,
                "level": level,
                "raw_text": raw_line,
                "confidence": confidence,
                "children": [],
                "importance_hint": importance
            }
            node_id_counter += 1

            # Shift-reduce parser logic:
            # Pop items from the stack that are deeper or equal in level to make space
            while stack and stack[-1]["level"] >= node["level"]:
                stack.pop()

            if stack:
                node["parent_id"] = stack[-1]["id"]
                stack[-1]["children"].append(node)
            else:
                root_nodes.append(node)

            stack.append(node)

        return root_nodes
