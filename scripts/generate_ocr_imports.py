"""Generate the exam bank from the locally regenerated CSP OCR results."""

from __future__ import annotations

import ast
import hashlib
import pprint
import re
import sys
from pathlib import Path

from generate_csp_imports import (
    Round1Source,
    Round2Source,
    dedupe_items,
    parse_answer_sequence,
    parse_pdf_round1,
    parse_round2_source,
)


ROOT = Path(__file__).resolve().parents[1]
OCR_ROOT = ROOT / "CSP" / "题库OCR"
OUTPUT = ROOT / "online_exam" / "imported_ocr_questions.py"


ROUND1_FILES = [
    ("csp_j_round1", "CSP-J", 2019, "CSP-J/2019/Round1/cspjs2019hj_cpp.md", "CSP-J/2019/Round1/cspjs2019hj_sol.md", 4),
    ("csp_j_round1", "CSP-J", 2020, "CSP-J/2020/Round1/cspjs2020hj_cpp.md", "CSP-J/2020/Round1/cspjs2020hj_sol.md", 4),
    ("csp_j_round1", "CSP-J", 2021, "CSP-J/2021/Round1/cspjs2021hj_cpp.md", "CSP-J/2021/Round1/cspjs2021hj_sol.md", 4),
    ("csp_j_round1", "CSP-J", 2022, "CSP-J/2022/Round1/2022CSPJ1试题.md", "CSP-J/2022/Round1/第一轮认证答案-入门级.md", 4),
    ("csp_j_round1", "CSP-J", 2023, "CSP-J/2023/Round1/CSP-J1-2023.md", "CSP-J/2023/Round1/2023-CSP-J1答案(无解析).md", 4),
    ("csp_j_round1", "CSP-J", 2024, "CSP-J/2024/Round1/CSP-J1-2024.md", "CSP-J/2024/Round1/solution.md", 4),
    ("csp_s_round1", "CSP-S", 2019, "CSP-S/2019/Round1/cspjs2019hs_cpp.md", "CSP-S/2019/Round1/cspjs2019hs_sol.md", 5),
    ("csp_s_round1", "CSP-S", 2020, "CSP-S/2020/Round1/cspjs2020hs_cpp.md", "CSP-S/2020/Round1/cspjs2020hs_sol.md", 5),
    ("csp_s_round1", "CSP-S", 2021, "CSP-S/2021/Round1/2021CSP-S1试题(C++).md", "CSP-S/2021/Round1/2021CSP-S1试题及参考答案.md", 5),
    ("csp_s_round1", "CSP-S", 2022, "CSP-S/2022/Round1/2022CSP-S1试题.md", "CSP-S/2022/Round1/2022SCP-S1答案.md", 5),
    ("csp_s_round1", "CSP-S", 2023, "CSP-S/2023/Round1/CSP-S1-2023.md", "CSP-S/2023/Round1/2023-CSP-S1答案.md", 5),
    ("csp_s_round1", "CSP-S", 2024, "CSP-S/2024/Round1/CSP-S1-2024.md", "CSP-S/2024/Round1/solution.md", 5),
]


def read(relative: str) -> str:
    return (OCR_ROOT / relative).read_text(encoding="utf-8")


def answer_map(text: str) -> dict[int, str]:
    """Read table answers and inline ``答案 A`` answers from OCR markdown."""
    text = re.sub(r"(?<![A-Za-z])\bT\b", "√", text)
    text = re.sub(r"(?<![A-Za-z])\bF\b", "×", text)
    answers: dict[int, str] = {}
    for number, answer in re.findall(r"\|\s*(\d{1,2})\s*\|\s*([A-D√×])\s*(?:\||$)", text):
        answers[int(number)] = answer

    inline = list(re.finditer(r"(?mi)^\s*答案\s*[:：]?\s*([A-D√×])\s*$", text))
    if inline:
        for index, match in enumerate(inline, 1):
            answers.setdefault(index, match.group(1))

    # Some answer sheets use one answer per numbered line instead of a table.
    for number, answer in re.findall(r"(?m)^\s*(\d{1,2})\s*[.)、]\s*([A-D√×])\s*$", text):
        answers[int(number)] = answer
    lines = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in text.splitlines()
        if "|" in line
    ]
    for index, row in enumerate(lines[:-1]):
        if not row or not all(re.fullmatch(r"\d{1,2}", cell or "") for cell in row):
            continue
        next_row = lines[index + 1]
        for number, answer in zip(row, next_row):
            if re.fullmatch(r"[A-D√×]", answer or ""):
                answers[int(number)] = answer
    if len(answers) < 30:
        answers.update(parse_answer_sequence(text))
    return answers


def normalize_round1_text(text: str) -> str:
    text = re.sub(r"(?m)^\s*\{\d+\}-+\s*$", "", text)
    # OCR pagination sometimes turns the next question into a Markdown list item.
    text = re.sub(r"(?m)^\s*-\s+(\d{1,2})[.]\s+", r"\n\1. ", text)
    return text


def source_round1(record: tuple) -> tuple[Round1Source, str, str]:
    competition, level, year, question_path, answer_path, difficulty = record
    source = Round1Source(competition, level, year, f"CSP/题库OCR/{question_path}", f"CSP/题库OCR/{answer_path}", difficulty)
    return source, normalize_round1_text(read(question_path)), read(answer_path)


def build_round1() -> tuple[list[dict], list[str]]:
    items: list[dict] = []
    report: list[str] = []
    for record in ROUND1_FILES:
        source, question_text, answer_text = source_round1(record)
        parsed = parse_pdf_round1(source, question_text, answer_map(answer_text))
        for question in parsed:
            question["stem"] = re.sub(r"\n\s*-\s*$", "", question.get("stem", "")).strip()
            question["options"] = [
                re.split(r"\n\s*(?:一、|二、|三、)\s*", option, maxsplit=1)[0]
                .rstrip(" -")
                .strip()
                for option in question.get("options", [])
            ]
        parsed = [question for question in parsed if 2 <= len(question.get("options", [])) <= 4]
        items.extend(parsed)
        report.append(f"{source.level_label} {source.year} Round1: {len(parsed)}")
    return items, report


def build_round2() -> tuple[list[dict], list[str]]:
    tasks: list[dict] = []
    report: list[str] = []
    for level, competition in (("CSP-J", "csp_j_round2"), ("CSP-S", "csp_s_round2")):
        for year_dir in sorted((OCR_ROOT / level).glob("*/Round2")):
            for path in sorted(year_dir.glob("*.md")):
                if "报告" in path.name or "知识构成" in path.name:
                    continue
                source = Round2Source(
                    competition,
                    level,
                    int(year_dir.parent.name),
                    str(path.relative_to(ROOT)),
                    5 if level == "CSP-J" else 6,
                )
                parsed = parse_round2_source(source, path.read_text(encoding="utf-8"))
                tasks.extend(parsed)
                report.append(f"{level} {source.year} Round2 {path.name}: {len(parsed)}")
    return tasks, report


def main() -> None:
    questions, round1_report = build_round1()
    tasks, round2_report = build_round2()
    questions, skipped_questions, renamed_questions = dedupe_items(questions, "choice")
    tasks, skipped_tasks, renamed_tasks = dedupe_items(tasks, "programming")
    report = round1_report + round2_report + [
        f"dedupe round1 skipped duplicates: {skipped_questions}, renamed id collisions: {renamed_questions}",
        f"dedupe round2 skipped duplicates: {skipped_tasks}, renamed id collisions: {renamed_tasks}",
    ]
    content = [
        '"""Auto-generated from CSP/题库OCR Markdown files."""',
        "",
        "# Regenerate with: python3 scripts/generate_ocr_imports.py",
        "",
        "OCR_ROUND1_CHOICE_QUESTIONS = " + pprint.pformat(questions, width=120, sort_dicts=False),
        "",
        "OCR_ROUND2_PROGRAMMING_TASKS = " + pprint.pformat(tasks, width=120, sort_dicts=False),
        "",
        "OCR_IMPORT_REPORT = " + pprint.pformat(report, width=120, sort_dicts=False),
        "",
    ]
    output = "\n".join(content)
    ast.parse(output)
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    print(f"round1 questions: {len(questions)}")
    print(f"round2 tasks: {len(tasks)}")
    for line in report:
        print(line)


if __name__ == "__main__":
    main()
