"""
Parses learning/<level>/<chapter>/<lesson>.md files into the BulkUpsertLessonsRequest
JSON structure expected by POST /admin/content/lessons/bulk-upsert.
"""
import json
import re
from pathlib import Path

import frontmatter


def _section(body: str, heading: str) -> str:
    """Extracts text between ## {heading} and the next ## heading."""
    pattern = rf"## {re.escape(heading)}\s*(.*?)(?=\n##|\Z)"
    m = re.search(pattern, body, re.DOTALL)
    return m.group(1).strip() if m else ""


def _parse_key_concepts(body: str) -> str:
    raw = _section(body, "Key Concepts")
    concepts = [l.lstrip("-• ").strip() for l in raw.splitlines() if l.strip()]
    return json.dumps(concepts)


def _parse_spark(body: str) -> str:
    return _section(body, "Quick Spark")


def _parse_understand(body: str) -> str:
    raw = _section(body, "Understand It")
    points = []
    # Points are separated by • and Example: tags embedded inline
    for block in re.split(r"•\s+", raw):
        block = block.strip()
        if not block:
            continue
        example_m = re.search(r"Example:\s*(.*?)(?=•|\Z)", block, re.DOTALL)
        example = example_m.group(1).strip() if example_m else ""
        point_text = re.sub(r"Example:.*", "", block, flags=re.DOTALL).strip()
        points.append({"point": point_text, "example": example})
    return json.dumps(points)


def _parse_mistake(body: str) -> tuple:
    raw = _section(body, "Common Mistake")
    mistake_m = re.search(r"Common Mistake:\s*(.*?)Correction:\s*(.*)", raw, re.DOTALL)
    if mistake_m:
        return mistake_m.group(1).strip(), mistake_m.group(2).strip()
    return raw, ""


def _parse_try_it(body: str) -> tuple:
    raw = _section(body, "Try It in Real Life")
    return raw, None  # challengeTemplateId is None until content team links them


def _parse_quiz(body: str, heading: str, quiz_set: str) -> list:
    raw = _section(body, heading)
    questions = []
    # Each Q starts with "Q\d+."
    blocks = re.split(r"Q\d+\.\s+", raw)
    for sort_idx, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
        # Extract prompt (first line up to A.)
        option_split = re.split(r"\n[A-D]\.", block, maxsplit=1)
        prompt = option_split[0].strip()
        options_raw = "A." + option_split[1] if len(option_split) > 1 else ""

        options = []
        for opt in re.split(r"\n?[A-D]\.", options_raw):
            o = opt.strip()
            # Stop at Hint / Correct Answer lines
            o = re.split(r"\n(?:Hint|Correct Answer|Fact|Concept)", o)[0].strip()
            if o:
                options.append(o)

        hint_m = re.search(r"Hint:\s*(.*?)(?:\n|$)", block)
        hint = hint_m.group(1).strip() if hint_m else None

        correct_m = re.search(r"Correct Answer:\s*([A-D])", block)
        answer_index = ord(correct_m.group(1)) - ord("A") if correct_m else 0

        explanation_m = re.search(
            r"(?:Concept|Fact)[^:]*Explanation:\s*(.*?)(?:\n|$)", block)
        explanation = explanation_m.group(1).strip() if explanation_m else None

        questions.append({
            "quizSet": quiz_set,
            "prompt": prompt,
            "options": json.dumps(options),
            "answerIndex": answer_index,
            "hint": hint,
            "explanation": explanation,
            "sortOrder": sort_idx,
        })
    return questions


def parse_lesson_file(path: Path, chapter_module_id: str,
                      sort_order: int = 0) -> dict:
    post = frontmatter.load(str(path))
    meta = post.metadata
    body = post.content

    lesson_slug = path.stem
    title = str(meta.get("lesson", lesson_slug))
    topic_number = int(meta.get("topic", 0))

    mistake_text, mistake_correction = _parse_mistake(body)
    try_it_text, try_it_cid = _parse_try_it(body)

    basic_quiz = _parse_quiz(body, "Check Your Thinking", "BASIC")
    advanced_quiz = _parse_quiz(body, "Explore Further", "ADVANCED")

    return {
        "lessonSlug": lesson_slug,
        "title": title,
        "topicNumber": topic_number,
        "sortOrder": sort_order,
        "keyConcepts": _parse_key_concepts(body),
        "spark": _parse_spark(body),
        "understandPoints": _parse_understand(body),
        "fact": _section(body, "Real-Life Fact"),
        "mistakeText": mistake_text,
        "mistakeCorrection": mistake_correction,
        "takeaway": _section(body, "Key Takeaway"),
        "tryItText": try_it_text,
        "tryItChallengeTemplateId": try_it_cid,
        "quizQuestions": basic_quiz + advanced_quiz,
    }


def parse_learning_directory(learning_root: Path) -> list:
    """
    Returns a list of level dicts for BulkUpsertLessonsRequest.
    Structure: learning/<level-dir>/<chapter-dir>/<lesson>.md
    Level dir name = levelKey, chapter dir name = moduleId.
    """
    levels = []
    for level_dir in sorted(learning_root.iterdir()):
        if not level_dir.is_dir():
            continue
        level_key = level_dir.name
        level_title = level_key.replace("-", " ").title()
        chapters = []
        for chapter_dir in sorted(level_dir.iterdir()):
            if not chapter_dir.is_dir():
                continue
            module_id = f"{level_key}/{chapter_dir.name}"
            chapter_title = chapter_dir.name.replace("-", " ").title()
            chapter_number = _extract_number(chapter_dir.name)
            lessons = []
            for sort_idx, md_file in enumerate(sorted(chapter_dir.glob("*.md"))):
                lessons.append(
                    parse_lesson_file(md_file, module_id, sort_idx))
            chapters.append({
                "moduleId": module_id,
                "title": chapter_title,
                "chapterNumber": chapter_number,
                "sortOrder": _extract_number(chapter_dir.name),
                "lessons": lessons,
            })
        levels.append({
            "levelKey": level_key,
            "title": level_title,
            "sortOrder": _extract_number(level_key),
            "chapters": chapters,
        })
    return levels


def _extract_number(name: str) -> int:
    m = re.search(r"\d+", name)
    return int(m.group()) if m else 0
