"""Parses links/goal-to-lesson-map.yaml into a dict of goalId → moduleId."""
import yaml
from pathlib import Path


def load_goal_to_lesson_map(content_root: Path) -> dict:
    """
    Returns dict: { "MW01": "level-1-2-money-foundation/ch01-what-is-money", ... }
    Goals whose lesson_file is null are included with moduleId=None.
    """
    map_path = content_root / "links" / "goal-to-lesson-map.yaml"
    with open(map_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    result = {}
    for goal_id, entry in (raw.get("mappings") or {}).items():
        result[goal_id] = entry.get("lesson_file")
    return result
