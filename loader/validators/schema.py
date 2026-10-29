"""
Validates parsed content objects before posting to the BE admin endpoints.
Exits non-zero on any failure.
"""
import json
import sys

REQUIRED_GOAL_FIELDS = ["id", "pillar", "lifeStage", "title"]
VALID_PILLARS = {
    "MONEY_WEALTH", "EDUCATION_LEARNING", "HEALTH_FITNESS",
    "RELATIONSHIPS_CONTRIBUTION", "SPIRITUALITY_INNER_LIFE", "OTHER",
}
VALID_LIFE_STAGES = {
    "EARLY_EXPLORER", "YOUNG_LEARNER", "EARLY_TEEN",
    "DEVELOPING_TEEN", "TRANSITION", "EMERGING_ADULT",
}
VALID_FREQUENCIES = {"DAILY", "WEEKLY", "MONTHLY"}
VALID_QUIZ_SETS = {"BASIC", "ADVANCED"}


def validate_goal(goal: dict) -> list:
    errors = []
    gid = goal.get("id", "<unknown>")
    for f in REQUIRED_GOAL_FIELDS:
        if not goal.get(f):
            errors.append(f"[{gid}] Missing required field: {f}")
    if goal.get("pillar") and goal["pillar"] not in VALID_PILLARS:
        errors.append(f"[{gid}] Invalid pillar: {goal['pillar']}")
    if goal.get("lifeStage") and goal["lifeStage"] not in VALID_LIFE_STAGES:
        errors.append(f"[{gid}] Invalid lifeStage: {goal['lifeStage']}")
    challenges = goal.get("challenges") or []
    if len(challenges) > 2:
        errors.append(f"[{gid}] Too many challenges: {len(challenges)} (max 2)")
    habits = goal.get("habits") or []
    if len(habits) != 5:
        errors.append(f"[{gid}] Expected 5 habits, got {len(habits)}")
    for h in habits:
        freq = (h.get("frequency") or "DAILY").upper()
        if freq not in VALID_FREQUENCIES:
            errors.append(f"[{gid}] Invalid habit frequency: {freq}")
    return errors


def validate_lesson(lesson: dict, slug_prefix: str = "") -> list:
    errors = []
    slug = f"{slug_prefix}/{lesson.get('lessonSlug', '<unknown>')}"
    if not lesson.get("title"):
        errors.append(f"[{slug}] Missing title")
    questions = lesson.get("quizQuestions") or []
    basic_qs = [q for q in questions if q.get("quizSet") == "BASIC"]
    advanced_qs = [q for q in questions if q.get("quizSet") == "ADVANCED"]
    if len(basic_qs) < 5:
        errors.append(f"[{slug}] Fewer than 5 BASIC questions ({len(basic_qs)})")
    if len(advanced_qs) < 5:
        errors.append(f"[{slug}] Fewer than 5 ADVANCED questions ({len(advanced_qs)})")
    for q in questions:
        if not q.get("hint"):
            errors.append(f"[{slug}] Question missing hint: {q.get('prompt', '')[:40]}")
        if not q.get("explanation"):
            errors.append(f"[{slug}] Question missing explanation: {q.get('prompt', '')[:40]}")
        try:
            opts = json.loads(q.get("options") or "[]")
            if len(opts) < 2:
                errors.append(f"[{slug}] Question has fewer than 2 options")
        except json.JSONDecodeError:
            errors.append(f"[{slug}] options is not valid JSON")
        if q.get("quizSet") not in VALID_QUIZ_SETS:
            errors.append(f"[{slug}] Invalid quizSet: {q.get('quizSet')}")
    return errors


def validate_all(goals: list, levels: list) -> bool:
    """
    Validates goals and levels. Prints per-file pass/fail table.
    Returns True if all pass, False if any fail.
    """
    all_errors = []

    print("\n── Goal Templates ──────────────────────────")
    for goal in goals:
        errs = validate_goal(goal)
        status = "PASS" if not errs else "FAIL"
        print(f"  {status}  {goal.get('id', '?'):<10}  {goal.get('title', '')[:50]}")
        all_errors.extend(errs)

    print("\n── Structured Lessons ──────────────────────")
    for level in levels:
        for chapter in level.get("chapters") or []:
            for lesson in chapter.get("lessons") or []:
                slug = lesson.get("lessonSlug", "?")
                errs = validate_lesson(lesson, chapter.get("moduleId", ""))
                status = "PASS" if not errs else "FAIL"
                print(f"  {status}  {slug:<40}")
                all_errors.extend(errs)

    if all_errors:
        print(f"\n✗ {len(all_errors)} validation error(s):")
        for e in all_errors:
            print(f"  • {e}")
        return False
    print(f"\n✓ All content valid.")
    return True
