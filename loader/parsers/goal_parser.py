"""
Parses goals-habits/<pillar>/<GOALID>_<slug>.md files into GoalTemplate JSON
matching the POST /admin/content/goal-templates/bulk-upsert contract.
"""
import re
from pathlib import Path
from typing import Optional

import frontmatter

_LIFE_STAGE_MAP = {
    "5-7": "EARLY_EXPLORER",
    "5–7": "EARLY_EXPLORER",
    "8-10": "YOUNG_LEARNER",
    "8–10": "YOUNG_LEARNER",
    "11-13": "EARLY_TEEN",
    "11–13": "EARLY_TEEN",
    "14-16": "DEVELOPING_TEEN",
    "14–16": "DEVELOPING_TEEN",
    "17-18": "TRANSITION",
    "17–18": "TRANSITION",
    "19-22": "EMERGING_ADULT",
    "19–22": "EMERGING_ADULT",
}

_PILLAR_MAP = {
    "money-wealth": "MONEY_WEALTH",
    "money_wealth": "MONEY_WEALTH",
    "education-learning": "EDUCATION_LEARNING",
    "education_learning": "EDUCATION_LEARNING",
    "health-fitness": "HEALTH_FITNESS",
    "health_fitness": "HEALTH_FITNESS",
    "relationships-contribution": "RELATIONSHIPS_CONTRIBUTION",
    "relationships_contribution": "RELATIONSHIPS_CONTRIBUTION",
    "spirituality-inner-life": "SPIRITUALITY_INNER_LIFE",
    "spirituality_inner_life": "SPIRITUALITY_INNER_LIFE",
    "other": "OTHER",
}


def _parse_life_stage(raw: str) -> str:
    raw = raw.strip()
    for prefix, enum_val in _LIFE_STAGE_MAP.items():
        if raw.startswith(prefix):
            return enum_val
    # Try extracting the age range
    m = re.search(r"(\d+)[–-](\d+)", raw)
    if m:
        key = f"{m.group(1)}-{m.group(2)}"
        if key in _LIFE_STAGE_MAP:
            return _LIFE_STAGE_MAP[key]
    raise ValueError(f"Cannot map life_stage: '{raw}'")


def _parse_pillar(raw: str) -> str:
    key = raw.strip().lower().replace(" ", "-")
    if key in _PILLAR_MAP:
        return _PILLAR_MAP[key]
    raise ValueError(f"Cannot map pillar: '{raw}'")


def _extract_challenges(body: str, goal_id: str) -> list:
    challenges = []
    section = re.search(r"## Goal Challenges\s*(.*?)(?=\n##|\Z)", body, re.DOTALL)
    if not section:
        return challenges
    lines = section.group(1).strip().splitlines()
    idx = 1
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^\d+\.\s*(.*)", line)
        if m:
            challenges.append({
                "id": f"{goal_id}-C{idx}",
                "title": m.group(1).strip(),
                "description": m.group(1).strip(),
                "defaultCoins": 100,
            })
            idx += 1
    return challenges


def _extract_habits(body: str, goal_id: str) -> list:
    habits = []
    section = re.search(r"## Habits\s*(.*?)(?=\n## (?!Habit)|\Z)", body, re.DOTALL)
    if not section:
        return habits
    blocks = re.findall(
        r"### Habit\s+\d+\s*-\s*(.+?)\n(.*?)(?=### Habit|\Z)",
        section.group(1), re.DOTALL)
    for i, (title, desc) in enumerate(blocks, start=1):
        habits.append({
            "id": f"{goal_id}-H{i}",
            "title": title.strip(),
            "frequency": "DAILY",
            "defaultCoins": 10,
            "defaultStreakTarget": 30,
        })
    return habits


def parse_goal_file(path: Path, module_id: Optional[str] = None) -> dict:
    post = frontmatter.load(str(path))
    meta = post.metadata
    body = post.content

    goal_id = str(meta.get("goal_id", "")).strip()
    if not goal_id:
        raise ValueError(f"Missing goal_id in {path}")

    raw_pillar = str(meta.get("pillar", "other"))
    raw_life_stage = str(meta.get("life_stage", "5-7"))

    return {
        "id": goal_id,
        "pillar": _parse_pillar(raw_pillar),
        "subDomain": str(meta.get("sub_domain", "")),
        "lifeStage": _parse_life_stage(raw_life_stage),
        "title": str(meta.get("standard_goal", meta.get("title", ""))),
        "goalVariable": str(meta.get("goal_variable", "")),
        "unit": str(meta.get("unit", "")),
        "targetPeriodMonths": _parse_period(str(meta.get("target_period", ""))),
        "moduleId": module_id,
        "defaultCompletionCoins": 300,
        "badgeId": None,
        "challenges": _extract_challenges(body, goal_id),
        "habits": _extract_habits(body, goal_id),
    }


def parse_goal_directory(root: Path, module_map: dict) -> list:
    items = []
    for md_file in sorted(root.rglob("*.md")):
        try:
            goal_id = md_file.stem.split("_")[0]
            module_id = module_map.get(goal_id)
            items.append(parse_goal_file(md_file, module_id))
        except Exception as e:
            raise ValueError(f"Error parsing {md_file}: {e}") from e
    return items


def _parse_period(raw: str) -> int:
    m = re.search(r"(\d+)", raw)
    return int(m.group(1)) if m else 6
