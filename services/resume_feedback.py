import re
from html import unescape


_IMPROVEMENT_HEADING = re.compile(
    r"(?:prioritized\s+)?improvements?|ways\s+to\s+improve",
    re.IGNORECASE,
)
_PRIORITY = re.compile(r"^(?:P)?([1-5])$", re.IGNORECASE)
_NUMBERED_SUGGESTION = re.compile(
    r"^(?:[-*]\s*)?(?:P([1-5])|([1-5])[.)])\s*[:.)-]?\s*(.*)$",
    re.IGNORECASE,
)
_ANALYSIS_HEADING = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:\*\*)?"
    r"(?:(?:section\s+)?\d+[.)]?\s+)?"
    r"(?P<title>resume\s+ats\s+score|ats\s+score|skills|strengths|weaknesses|"
    r"(?:prioritized\s+)?improvements?(?:\s+to\s+increase[^:]*)?|"
    r"quick\s+checklist|overview)"
    r"(?:\s*\([^)]*\))?(?:\s+before\s+resubmission)?(?:\*\*)?\s*:?\s*$",
    re.IGNORECASE,
)
_ANALYSIS_SCORE = re.compile(
    r"(?:resume\s+)?ats\s+score\s*[:\-]?\s*(\d{1,3})\s*/\s*100",
    re.IGNORECASE,
)


def _clean_cell(value):
    value = unescape(value)
    value = re.sub(r"<br\s*/?>", " — ", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]*>", "", value)
    value = re.sub(r"\[(.*?)\]\([^)]*\)", r"\1", value)
    value = value.replace("**", "").replace("__", "").replace("`", "")
    value = re.sub(r"(?<!\w)\*(.*?)\*(?!\w)", r"\1", value)
    value = re.split(
        r"\s*(?:\|\s*)?(?:>\s*)?(?:\*\*)?Note:|"
        r"\s*(?:---\s*)?#{1,6}\s*\d*\.?\s*Quick Checklist|"
        r"\s*---\s*$",
        value,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    return re.sub(r"\s+", " ", value).strip(" |-*")


def parse_resume_improvements(feedback):
    """Extract prioritized resume edits from current or earlier AI review text."""
    if not feedback:
        return []

    suggestions = []
    in_improvements = False
    current = None

    def save_current():
        if current and current["improvement"].strip():
            suggestions.append(
                {
                    "priority": current["priority"],
                    "area": current["area"] or "Resume",
                    "improvement": current["improvement"].strip(),
                }
            )

    for raw_line in str(feedback).splitlines():
        if re.search(r"quick\s+checklist", raw_line, re.IGNORECASE):
            save_current()
            current = None
            in_improvements = False
            continue
        if re.match(r"\s*(?:>\s*)?(?:\*\*)?Note:", raw_line, re.IGNORECASE):
            save_current()
            current = None
            in_improvements = False
            continue

        line = _clean_cell(raw_line.strip().strip("`"))
        if not line:
            continue

        if _IMPROVEMENT_HEADING.search(line):
            save_current()
            current = None
            in_improvements = True
            continue

        if not in_improvements:
            continue

        cells = [_clean_cell(cell.strip()) for cell in line.strip("|").split("|")]
        if len(cells) >= 3:
            if (
                "priority" in cells[0].casefold()
                or all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells)
            ):
                continue
            priority = _PRIORITY.fullmatch(cells[0])
            if priority:
                save_current()
                current = {
                    "priority": f"P{priority.group(1)}",
                    "area": cells[1],
                    "improvement": _clean_cell(" — ".join(cells[2:])),
                }
                continue

        numbered = _NUMBERED_SUGGESTION.match(line)
        if numbered:
            save_current()
            priority_number = numbered.group(1) or numbered.group(2)
            suggestion = _clean_cell(numbered.group(3))
            area, separator, details = suggestion.partition(":")
            if separator and re.fullmatch(r"[A-Za-z][A-Za-z /&-]{1,30}", area.strip()):
                suggestion = details.strip()
                suggestion_area = area.strip()
            else:
                suggestion_area = ""
            if suggestion:
                current = {
                    "priority": f"P{priority_number}",
                    "area": suggestion_area,
                    "improvement": suggestion,
                }
            continue

        if current:
            current["improvement"] += " " + line
        elif line.startswith(("-", "*", "•")):
            current = {
                "priority": f"P{len(suggestions) + 1}",
                "area": "",
                "improvement": _clean_cell(line[1:].strip()),
            }

    save_current()
    return suggestions[:5]


def parse_resume_analysis(feedback, ats_score=None):
    """Return the full resume review as safe, table-ready analysis sections."""
    if not feedback:
        return []

    sections = []
    current_title = None
    current_lines = []

    def save_section():
        if current_title and current_lines:
            details = "\n".join(
                cleaned
                for line in current_lines
                if (cleaned := _clean_cell(line))
            ).strip()
            if details:
                sections.append({"area": current_title, "details": details})

    score = ats_score
    for line in str(feedback).splitlines():
        score_match = _ANALYSIS_SCORE.search(line)
        if score is None and score_match:
            score = max(0, min(int(score_match.group(1)), 100))

        heading = _ANALYSIS_HEADING.match(line)
        if heading:
            save_section()
            title = re.sub(r"\s+", " ", heading.group("title")).strip().casefold()
            if "improvement" in title:
                current_title = "Prioritized improvements"
            elif "quick checklist" in title:
                current_title = "Before resubmitting"
            elif "ats score" in title:
                current_title = "Resume ATS score"
            else:
                current_title = title.title()
            current_lines = []
            continue

        if current_title:
            current_lines.append(line)

    save_section()

    if score is not None:
        sections.insert(
            0,
            {"area": "Resume ATS score", "details": f"{max(0, min(int(score), 100))}/100"},
        )

    improvements = parse_resume_improvements(feedback)
    if improvements and not any(
        section["area"] == "Prioritized improvements" for section in sections
    ):
        sections.append(
            {
                "area": "Prioritized improvements",
                "details": "\n".join(
                    f"{item['priority']} — {item['area']} — {item['improvement']}"
                    for item in improvements
                ),
            }
        )

    return sections
