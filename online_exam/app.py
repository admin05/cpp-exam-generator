from __future__ import annotations

import hashlib
import html
import json
import os
import random
import re
import shutil
import sqlite3
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .csp_j_explanations import CSP_J_ROUND1_EXPLANATIONS
from .question_bank import CHOICE_QUESTIONS, PROGRAMMING_TASKS, sanitize_csp_imported_text
from .question_generators import build_generated_tests, has_generator, missing_generator_ids


ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("EXAM_DB", "/data/exam.db"))
JUDGE_DIR = Path(os.environ.get("JUDGE_DIR", "/judge"))
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
BEIJING_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")
PLATFORM_NAME = "C++ 竞赛训练平台"
EXAM_FORM_SETTINGS_KEY = "admin_exam_form_defaults"
DEFAULT_EXAM_FORM = {
    "title": "素养大赛 C++ 模拟训练",
    "question_bank": "literacy",
    "choice_count": 10,
    "program_count": 4,
    "duration": 90,
}

CSP_J_ROUND1_FORMAT = "csp_j_round1"
CSP_J_ROUND1_TOTAL_QUESTIONS = 43
CSP_J_ROUND1_TOTAL_SCORE = 100.0
CSP_S_ROUND1_FORMAT = "csp_s_round1"
CSP_S_ROUND1_TOTAL_SCORE = 100.0
CSP_S_ROUND1_FIRST_COUNT = 15
CSP_S_ROUND1_READING_TYPE_RANGES = {
    2019: ((16, 21), (22, 27), (28, 33)),
    2020: ((16, 21), (22, 27), (28, 33)),
    2021: ((16, 21), (22, 27), (28, 33)),
    2022: ((16, 21), (22, 27), (28, 33)),
    2023: ((16, 21), (22, 27), (28, 33)),
    2024: ((16, 20), (21, 26), (27, 32)),
    2025: ((16, 21), (22, 27), (28, 33)),
}
CSP_S_ROUND1_COMPLETION_START = {
    2019: 34,
    2020: 34,
    2021: 34,
    2022: 34,
    2023: 34,
    2024: 33,
    2025: 34,
}
CSP_FIXED_ROUND1_FORMATS = {CSP_J_ROUND1_FORMAT, CSP_S_ROUND1_FORMAT}
CSP_J_READING_JUDGMENT_TYPE = "程序阅读判断题"
CSP_J_READING_CHOICE_TYPE = "程序阅读单选题"
CSP_J_COMPLETION_TYPE = "完善程序单选题"
CSP_CORRECTED_QUESTION_SNAPSHOT_RULES = {
    # The 2022 CSP-J PDF places the second reading-program code immediately
    # before question 22. Older OCR output left q22 blank, so saved papers
    # need the canonical snapshot backfilled as well.
    "csp_j_round1-2022-q22": {"target_id": "csp_j_round1-2022-q22"},
    "csp_j_round1-2024-q15": {"target_id": "csp_j_round1-2024-q15"},
    "csp_j_round1-2019-q12": {"target_id": "csp_j_round1-2019-q12"},
    "csp_j_round1-2020-q05": {
        "target_id": "csp_j_round1-2020-q06",
        "stem_contains": "else return A[n]",
    },
    "csp_j_round1-2022-q13": {
        "target_id": "csp_j_round1-2022-q13",
        "explanation": "32.1(8) = 3 * 8 + 2 + 1 / 8 = 26.125，因此选择 C。",
    },
    "csp_j_round1-2019-q12": {"target_id": "csp_j_round1-2019-q12"},
    "csp_s_round1-2020-q15": {"target_id": "csp_s_round1-2020-q15"},
    "csp_s_round1-2021-q18": {"target_id": "csp_s_round1-2021-q18"},
    "csp_s_round1-2021-q19": {"target_id": "csp_s_round1-2021-q19"},
    "csp_s_round1-2023-q15": {"target_id": "csp_s_round1-2023-q15"},
    "csp_s_round1-2024-q06": {"target_id": "csp_s_round1-2024-q06"},
    "csp_s_round1-2021-q34": {"target_id": "csp_s_round1-2021-q34", "stem_contains": "①处"},
    "csp_s_round1-2021-q35": {"target_id": "csp_s_round1-2021-q35", "stem_contains": "②处"},
    "csp_s_round1-2021-q36": {"target_id": "csp_s_round1-2021-q36", "stem_contains": "③处"},
    "csp_s_round1-2021-q37": {"target_id": "csp_s_round1-2021-q37", "stem_contains": "④处"},
    "csp_s_round1-2021-q38": {"target_id": "csp_s_round1-2021-q38", "stem_contains": "①处"},
    "csp_s_round1-2021-q39": {"target_id": "csp_s_round1-2021-q39", "stem_contains": "②处"},
    "csp_s_round1-2021-q40": {"target_id": "csp_s_round1-2021-q40", "stem_contains": "③处"},
    "csp_s_round1-2021-q41": {"target_id": "csp_s_round1-2021-q41", "stem_contains": "④处"},
    "csp_s_round1-2021-q42": {"target_id": "csp_s_round1-2021-q42", "stem_contains": "⑤处"},
    "csp_s_round1-2021-q43": {"target_id": "csp_s_round1-2021-q43", "stem_contains": "⑥处"},
    **{
        f"csp_j_round1-2021-q{number:02d}": {"target_id": f"csp_j_round1-2021-q{number:02d}"}
        for number in range(39, 44)
    },
    **{
        f"csp_j_round1-2023-q{number:02d}": {"target_id": f"csp_j_round1-2023-q{number:02d}"}
        for number in range(38, 43)
    },
    **{
        f"csp_j_round1-2024-q{number:02d}": {"target_id": f"csp_j_round1-2024-q{number:02d}"}
        for number in range(38, 43)
    },
    **{
        f"csp_s_round1-2024-q{number:02d}": {"target_id": f"csp_s_round1-2024-q{number:02d}"}
        for number in range(38, 43)
    },
}
CORRECTED_QUESTION_SNAPSHOT_FIELDS = ("id", "stem", "code", "options", "answer")
CHOICE_QUESTIONS_BY_ID = {
    str(question.get("id", "")): question for question in CHOICE_QUESTIONS
}

QUESTION_BANK_PROFILES = {
    "all": {
        "label": "全部题库",
        "competitions": None,
        "item_types": {"choice", "programming"},
        "principle": "通用 C++ 竞赛训练：混合抽取客观题和编程题，覆盖语法基础、程序阅读、模拟枚举、数论、排序二分、搜索、递推、STL 与综合应用。",
    },
    "literacy": {
        "label": "素养大赛",
        "competitions": {"general", "literacy"},
        "item_types": {"choice", "programming"},
        "principle": "素养大赛复赛 / 决赛 C++：依据《复赛 决赛考点大纲.pdf》的 C++ 范围，覆盖程序基础、数组、字符串、结构体、排序去重、函数递归、数学库、文件入门、数理知识、模拟、枚举、高精度、分治、贪心、递推、归并 / 快排、二分、前缀和、DFS/BFS、set/map/pair、栈/队列和链表基础。",
    },
    "csp_j_round1": {
        "label": "CSP-J 第一轮",
        "competitions": {"general", "csp", "csp_j", "csp_j_round1"},
        "item_types": {"choice"},
        "principle": "CSP-J 第一轮 C++：依据《NOI竞赛大纲_Syllabus_Edition_2025.pdf》中 CSP-J 要求，面向基础知识、C++ 语法、程序阅读、计算机与信息学常识、数学基础、数据结构与算法概念等客观题训练。",
    },
    "csp_j_round2": {
        "label": "CSP-J 第二轮",
        "competitions": {"general", "csp", "csp_j", "csp_j_round2"},
        "item_types": {"programming"},
        "principle": "CSP-J 第二轮 C++：依据《NOI竞赛大纲_Syllabus_Edition_2025.pdf》中 CSP-J 要求，面向 C++ 程序设计、模拟、枚举、排序、字符串、基础数据结构、搜索、递推等上机编程题训练。",
    },
    "csp_s_round1": {
        "label": "CSP-S 第一轮",
        "competitions": {"csp_s", "csp_s_round1"},
        "item_types": {"choice"},
        "principle": "CSP-S 第一轮 C++：来自本项目 CSP/题库/CSP-S 第一轮资料，保留单项选择、程序阅读判断、程序阅读选择、完善程序等原始题型。",
    },
    "csp_s_round2": {
        "label": "CSP-S 第二轮",
        "competitions": {"csp_s", "csp_s_round2"},
        "item_types": {"programming"},
        "principle": "CSP-S 第二轮 C++：来自本项目 CSP/题库/CSP-S 第二轮资料，按原题面题目类型导入编程题。",
    },
    "csp_x_round1": {
        "label": "CSP-X(山东) 第一轮",
        "competitions": {"csp_x_round1"},
        "item_types": {"choice"},
        "principle": "CSP-X(山东) 小学组第一轮：来自本项目 CSP/题库/CSP-X(山东) 第一轮资料，保留单项选择、程序阅读判断、程序阅读选择、完善程序等原始题型。",
    },
    "csp_x_round2": {
        "label": "CSP-X(山东) 第二轮",
        "competitions": {"csp_x_round2"},
        "item_types": {"programming"},
        "principle": "CSP-X(山东) 小学组第二轮：来自本项目 CSP/题库/CSP-X(山东) 第二轮资料，按原题面题目类型导入编程题；暂未能拆分的旧试卷保留为原始题面。",
    },
    "gesp": {
        "label": "GESP",
        "competitions": {"general", "gesp"},
        "item_types": {"choice", "programming"},
        "principle": "GESP C++：围绕等级认证常见知识点进行训练，覆盖语法基础、数组字符串、函数、递推递归、基础数据结构和简单算法实现。",
    },
    "fuzhou": {
        "label": "福州机器人赛",
        "competitions": {"general", "fuzhou"},
        "item_types": {"choice", "programming"},
        "principle": "福州机器人 C++ 编程挑战赛：结合导入题与通用基础题，训练小学提高级常见的阅读理解、模拟、枚举、搜索和综合编程能力。",
    },
}


def db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class DuplicateExamError(RuntimeError):
    """Raised when an identical question paper already exists."""


def _question_signature(question: dict, item_type: str) -> dict:
    fields = (
        ("stem", "code", "content_html", "options", "answer")
        if item_type == "choice"
        else ("title", "description", "input", "output", "constraints", "code")
    )
    values = {field: question.get(field) for field in fields}
    if not any(value not in (None, "", []) for value in values.values()):
        values = {"id": question.get("id", "")}
    return values


def exam_signature(payload: dict) -> str:
    """Return a stable signature for the question set in a generated paper."""
    signature_data = {
        "question_bank": payload.get("question_bank", ""),
        "choice_questions": sorted(
            (
                _question_signature(question, "choice")
                for question in payload.get("choice_questions", [])
            ),
            key=lambda question: json.dumps(question, ensure_ascii=False, sort_keys=True),
        ),
        "programming_tasks": sorted(
            (
                _question_signature(task, "programming")
                for task in payload.get("programming_tasks", [])
            ),
            key=lambda task: json.dumps(task, ensure_ascii=False, sort_keys=True),
        ),
    }
    encoded = json.dumps(signature_data, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def existing_exam_signatures(question_bank: str) -> set[str]:
    """Load signatures for papers in the same question-bank profile."""
    try:
        with db() as conn:
            rows = conn.execute("SELECT signature, payload FROM exams").fetchall()
    except sqlite3.OperationalError:
        return set()

    signatures = set()
    for row in rows:
        try:
            payload = json.loads(row["payload"])
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        if payload.get("question_bank") != question_bank:
            continue
        signatures.add(row["signature"] or exam_signature(payload))
    return signatures


def init_db() -> None:
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                signature TEXT
            )
            """
        )
        exam_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(exams)").fetchall()
        }
        if "signature" not in exam_columns:
            conn.execute("ALTER TABLE exams ADD COLUMN signature TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_exams_signature ON exams(signature)")
        legacy_exams = conn.execute(
            "SELECT id, payload FROM exams WHERE signature IS NULL"
        ).fetchall()
        for exam in legacy_exams:
            try:
                signature = exam_signature(json.loads(exam["payload"]))
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            conn.execute(
                "UPDATE exams SET signature = ? WHERE id = ?",
                (signature, exam["id"]),
            )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL,
                student_name TEXT NOT NULL,
                choice_score INTEGER NOT NULL,
                choice_total INTEGER NOT NULL,
                program_score INTEGER NOT NULL,
                program_total INTEGER NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(exam_id) REFERENCES exams(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                name TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
    backfill_round1_explanations()


def now_text() -> str:
    return datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S")


def h(value: object) -> str:
    return html.escape(str(value), quote=True)


def normalize_output(value: str) -> str:
    lines = value.replace("\r\n", "\n").replace("\r", "\n").strip().split("\n")
    return "\n".join(line.rstrip() for line in lines).strip()


def balanced_pick(items: list[dict], count: int) -> list[dict]:
    if count <= 0:
        return []
    pool = list(items)
    limit = min(count, len(pool))
    grouped: dict[str, list[dict]] = {}
    for item in pool:
        grouped.setdefault(item["category"], []).append(item)

    rng = random.SystemRandom()
    for bucket in grouped.values():
        rng.shuffle(bucket)

    selected: list[dict] = []
    categories = list(grouped)
    rng.shuffle(categories)
    while len(selected) < limit and categories:
        remaining_categories = []
        for category in categories:
            bucket = grouped[category]
            if bucket and len(selected) < limit:
                selected.append(bucket.pop())
            if bucket:
                remaining_categories.append(category)
        categories = remaining_categories
        rng.shuffle(categories)
    rng.shuffle(selected)
    return selected


def format_score(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.1f}".rstrip("0").rstrip(".")


def question_score(question: dict) -> float:
    try:
        return float(question.get("score", 1))
    except (TypeError, ValueError):
        return 1.0


def question_number(question: dict) -> int:
    match = re.search(r"q(\d+)$", str(question.get("id", "")))
    return int(match.group(1)) if match else 0


def _reading_program_groups(questions: list[dict]) -> list[list[dict]]:
    """Recover the three reading-program blocks from imported code context."""
    ordered = sorted(questions, key=question_number)
    groups: list[list[dict]] = []
    current_key = None
    pending: list[dict] = []
    for question in ordered:
        code = str(question.get("code", "")).strip()
        if code:
            if current_key is None or code != current_key:
                if pending and groups:
                    groups[-1].extend(pending)
                    pending = []
                current_key = code
                groups.append([])
            groups[-1].extend(pending)
            pending = []
            groups[-1].append(question)
        else:
            pending.append(question)
    if pending:
        if groups:
            groups[-1].extend(pending)
        else:
            groups.append(pending)
    return [sorted(group, key=question_number) for group in groups if group]


def _completion_program_groups(questions: list[dict]) -> list[list[dict]]:
    """Recover completion blocks from the circled blank number resetting to ①."""
    ordered = sorted(questions, key=question_number)
    groups: list[list[dict]] = []
    current: list[dict] = []
    for question in ordered:
        marker = re.search(r"[①②③④⑤⑥⑦⑧⑨⑩]", str(question.get("stem", "")))
        if not marker:
            continue
        if marker.group(0) == "①" and current:
            groups.append(current)
            current = []
        current.append(question)
    if current:
        groups.append(current)
    return groups


def _copy_program_questions(
    questions: list[dict],
    section_id: str,
    section_title: str,
    program_index: int | None,
    scores: list[float],
) -> list[dict]:
    prepared = []
    fallback_code = next((str(q.get("code", "")) for q in questions if q.get("code")), "")
    for offset, question in enumerate(sorted(questions, key=question_number)):
        item = dict(question)
        if not item.get("code") and fallback_code:
            item["code"] = fallback_code
        item["section_id"] = section_id
        item["section_title"] = section_title
        item["program_index"] = program_index
        item["score"] = scores[offset]
        prepared.append(item)
    return prepared


def _csp_j_reading_scores(questions: list[dict]) -> list[float]:
    judgment_scores = [
        1.5 for question in questions
        if question.get("source_question_type") == CSP_J_READING_JUDGMENT_TYPE
    ]
    choice_questions = [
        question for question in questions
        if question.get("source_question_type") == CSP_J_READING_CHOICE_TYPE
    ]
    if len(judgment_scores) != 12 or len(choice_questions) != 6:
        raise RuntimeError("CSP-J 第一轮阅读程序小题数量校验失败。")
    choice_score = (40.0 - sum(judgment_scores)) / len(choice_questions)
    scores = []
    for question in questions:
        if question.get("source_question_type") == CSP_J_READING_JUDGMENT_TYPE:
            scores.append(1.5)
        else:
            scores.append(choice_score)
    return scores


def build_csp_j_round1_exam(title: str, duration: int) -> dict:
    """Build a fixed-format 15 + 18 + 10 CSP-J first-round paper."""
    imported = [
        question
        for question in CHOICE_QUESTIONS
        if question.get("competition") == CSP_J_ROUND1_FORMAT
    ]
    by_source: dict[str, list[dict]] = {}
    for question in imported:
        by_source.setdefault(str(question.get("source", "")), []).append(question)

    first_pool = []
    reading_templates = []
    completion_templates = []
    for source, source_questions in by_source.items():
        first = [
            q for q in source_questions
            if question_number(q) <= 15 and q.get("source_question_type") == "单项选择题"
        ]
        first_pool.extend(first)
        reading = [
            q for q in source_questions
            if 16 <= question_number(q) <= 33
            and q.get("source_question_type") in {
                CSP_J_READING_JUDGMENT_TYPE,
                CSP_J_READING_CHOICE_TYPE,
            }
        ]
        reading_groups = _reading_program_groups(reading)
        completion = [
            q for q in source_questions
            if question_number(q) >= 34 and q.get("source_question_type") == CSP_J_COMPLETION_TYPE
        ]
        completion_groups = _completion_program_groups(completion)
        reading_judgments = sum(
            q.get("source_question_type") == CSP_J_READING_JUDGMENT_TYPE
            for q in reading
        )
        reading_choices = sum(
            q.get("source_question_type") == CSP_J_READING_CHOICE_TYPE
            for q in reading
        )
        if (
            len(reading_groups) == 3
            and reading_judgments == 12
            and reading_choices == 6
        ):
            reading_templates.append((source, reading, reading_groups))
        if len(completion_groups) == 2 and all(len(group) == 5 for group in completion_groups):
            completion_templates.append((source, completion_groups))

    if not first_pool or not reading_templates or not completion_templates:
        raise RuntimeError(
            "CSP-J 第一轮题库缺少足够的题目，无法组成 15+18+10 固定结构。"
        )

    rng = random.SystemRandom()
    first = rng.sample(first_pool, 15)
    reading_source, reading, reading_groups = rng.choice(reading_templates)
    completion_source, completion_groups = rng.choice(completion_templates)
    source = (
        f"混合题库（单选题：{len(first_pool)} 道；"
        f"阅读程序：{reading_source}；完善程序：{completion_source}）"
    )
    reading_questions = []
    reading_section_title = "二、阅读程序（12 道判断题 + 6 道单选题，共 40 分）"
    reading_score_by_id = {
        question["id"]: score
        for question, score in zip(reading, _csp_j_reading_scores(reading))
    }
    for program_index, group in enumerate(reading_groups, 1):
        reading_questions.extend(
            _copy_program_questions(
                group,
                "part2",
                reading_section_title,
                program_index,
                [reading_score_by_id[question["id"]] for question in group],
            )
        )

    completion_questions = []
    completion_section_title = "三、完善程序（2 段程序、10 道单选题，共 30 分）"
    for program_index, group in enumerate(completion_groups, 1):
        completion_questions.extend(
            _copy_program_questions(
                group,
                "part3",
                completion_section_title,
                program_index,
                [3.0] * len(group),
            )
        )

    part1_title = "一、单项选择题（15 题，共 30 分）"
    first_questions = _copy_program_questions(
        first,
        "part1",
        part1_title,
        None,
        [2.0] * len(first),
    )
    questions = [
        *first_questions,
        *reading_questions,
        *completion_questions,
    ]
    questions = [
        prepare_choice_question(question, CSP_J_ROUND1_FORMAT)
        for question in questions
    ]
    sections = [
        {
            "id": "part1",
            "title": part1_title,
            "score": 30.0,
            "question_indices": list(range(0, 15)),
        },
        {
            "id": "part2",
            "title": reading_section_title,
            "score": 40.0,
            "question_indices": list(range(15, 33)),
            "programs": [
                {"index": i, "question_indices": list(range(start, end))}
                for i, (start, end) in enumerate(
                    zip(
                        [15, 15 + len(reading_groups[0]), 15 + len(reading_groups[0]) + len(reading_groups[1])],
                        [15 + len(reading_groups[0]), 15 + len(reading_groups[0]) + len(reading_groups[1]), 33],
                    ),
                    1,
                )
            ],
        },
        {
            "id": "part3",
            "title": completion_section_title,
            "score": 30.0,
            "question_indices": list(range(33, 43)),
            "programs": [
                {"index": i, "question_indices": list(range(start, end))}
                for i, (start, end) in enumerate(
                    zip(
                        [33, 33 + len(completion_groups[0])],
                        [33 + len(completion_groups[0]), 43],
                    ),
                    1,
                )
            ],
        },
    ]
    total_score = sum(question_score(question) for question in questions)
    if len(questions) != CSP_J_ROUND1_TOTAL_QUESTIONS or total_score != CSP_J_ROUND1_TOTAL_SCORE:
        raise RuntimeError("CSP-J 第一轮固定结构校验失败，请检查导入题库。")
    return {
        "title": title,
        "duration_minutes": duration,
        "question_bank": CSP_J_ROUND1_FORMAT,
        "question_bank_label": "CSP-J 第一轮",
        "principle": "CSP-J 第一轮固定结构：15 道单选题；3 段阅读程序共 18 道小题；2 段完善程序共 10 道小题；满分 100 分。",
        "exam_format": CSP_J_ROUND1_FORMAT,
        "total_score": CSP_J_ROUND1_TOTAL_SCORE,
        "sections": sections,
        "source_template": source,
        "choice_questions": questions,
        "programming_tasks": [],
    }


def _csp_s_year(question: dict) -> int:
    match = re.search(r"csp_s_round1-(\d{4})-q\d+$", str(question.get("id", "")))
    return int(match.group(1)) if match else 0


def _is_program_reading_judgment(question: dict) -> bool:
    options = [str(option).strip() for option in question.get("options", [])]
    return len(options) == 2 and set(options) == {"正确", "错误"}


def _csp_s_normalize_question(question: dict, section_id: str) -> dict:
    prepared = dict(question)
    if section_id == "part1":
        question_type = "单项选择题"
    elif section_id == "part2":
        question_type = (
            CSP_J_READING_JUDGMENT_TYPE
            if _is_program_reading_judgment(question)
            else CSP_J_READING_CHOICE_TYPE
        )
    else:
        question_type = CSP_J_COMPLETION_TYPE
    prepared["category"] = question_type
    prepared["source_question_type"] = question_type
    prepared["display_type"] = question_type
    return prepared


def _explicit_question_score(question: dict) -> float | None:
    match = re.match(r"^\s*[（(]\s*(\d+(?:\.\d+)?)\s*分", str(question.get("stem", "")))
    return float(match.group(1)) if match else None


def _csp_s_reading_score(question: dict, year: int) -> float:
    explicit = _explicit_question_score(question)
    if explicit is not None:
        return explicit
    if question.get("source_question_type") == CSP_J_READING_JUDGMENT_TYPE:
        return 1.5
    return 4.0 if year == 2019 else 3.0


def _csp_s_program_ranges(year: int) -> tuple[tuple[int, int], ...]:
    ranges = CSP_S_ROUND1_READING_TYPE_RANGES.get(year)
    if ranges:
        return ranges
    raise RuntimeError(f"CSP-S 第一轮暂未配置 {year} 年阅读程序分组。")


def _csp_s_round1_templates() -> tuple[list[dict], list[dict]]:
    imported = [
        question
        for question in CHOICE_QUESTIONS
        if question.get("competition") == CSP_S_ROUND1_FORMAT
    ]
    by_year: dict[int, list[dict]] = {}
    for question in imported:
        by_year.setdefault(_csp_s_year(question), []).append(question)

    first_pool_by_id: dict[str, dict] = {}
    templates: list[dict] = []
    for year, year_questions in sorted(by_year.items()):
        if year not in CSP_S_ROUND1_COMPLETION_START:
            continue
        ordered = sorted(year_questions, key=question_number)
        first = [
            _csp_s_normalize_question(question, "part1")
            for question in ordered
            if (
                1 <= question_number(question) <= CSP_S_ROUND1_FIRST_COUNT
                and question.get("source_question_type") == "单项选择题"
            )
        ]
        # The first section is made of independent questions.  A year may have
        # incomplete program blocks but still contribute its parsed first-section
        # questions to the common pool.
        for question in first:
            first_pool_by_id[str(question.get("id", ""))] = question
        completion_start = CSP_S_ROUND1_COMPLETION_START[year]
        reading_groups = [
            [
                _csp_s_normalize_question(question, "part2")
                for question in ordered
                if start <= question_number(question) <= end
            ]
            for start, end in _csp_s_program_ranges(year)
        ]
        completion = [
            question
            for question in ordered
            if question_number(question) >= completion_start
        ]
        completion_groups = _completion_program_groups(completion)
        if (
            len(first) < CSP_S_ROUND1_FIRST_COUNT
            or len(reading_groups) != 3
            or any(not group for group in reading_groups)
            or len(completion_groups) != 2
            or sum(len(group) for group in completion_groups) != 10
            or any(not group for group in completion_groups)
        ):
            continue

        normalized_completion_groups = [
            [_csp_s_normalize_question(question, "part3") for question in group]
            for group in completion_groups
        ]
        reading_questions = [question for group in reading_groups for question in group]
        reading_score = [
            _csp_s_reading_score(question, year)
            for question in reading_questions
        ]
        if round(sum(reading_score), 5) != 40.0:
            continue
        templates.append(
            {
                "year": year,
                "reading_groups": reading_groups,
                "reading_scores": reading_score,
                "completion_groups": normalized_completion_groups,
            }
        )
    return list(first_pool_by_id.values()), templates


def _section_program_ranges(start: int, groups: list[list[dict]]) -> list[dict]:
    programs = []
    cursor = start
    for index, group in enumerate(groups, 1):
        end = cursor + len(group)
        programs.append({"index": index, "question_indices": list(range(cursor, end))})
        cursor = end
    return programs


def build_csp_s_round1_exam(title: str, duration: int) -> dict:
    """Build a CSP-S first-round paper close to the real paper structure."""
    first_pool, templates = _csp_s_round1_templates()
    if len(first_pool) < CSP_S_ROUND1_FIRST_COUNT or not templates:
        raise RuntimeError(
            "CSP-S 第一轮题库缺少完整试卷模板，当前可用资料至少需要 15 道基础单选、"
            "3 个阅读程序和 2 个完善程序。"
        )

    rng = random.SystemRandom()
    first = rng.sample(first_pool, CSP_S_ROUND1_FIRST_COUNT)
    template = rng.choice(templates)
    reading_groups = template["reading_groups"]
    completion_groups = template["completion_groups"]
    reading_questions = [question for group in reading_groups for question in group]
    reading_score_by_id = {
        question["id"]: score
        for question, score in zip(reading_questions, template["reading_scores"])
    }

    part1_title = "一、单项选择题（15 题，共 30 分）"
    reading_title = "二、阅读程序（3 个程序，共 40 分）"
    completion_title = "三、完善程序（2 个程序、10 个空，共 30 分）"
    first_questions = _copy_program_questions(
        first,
        "part1",
        part1_title,
        None,
        [2.0] * len(first),
    )
    prepared_reading = []
    for program_index, group in enumerate(reading_groups, 1):
        prepared_reading.extend(
            _copy_program_questions(
                group,
                "part2",
                reading_title,
                program_index,
                [reading_score_by_id[question["id"]] for question in group],
            )
        )
    prepared_completion = []
    for program_index, group in enumerate(completion_groups, 1):
        prepared_completion.extend(
            _copy_program_questions(
                group,
                "part3",
                completion_title,
                program_index,
                [3.0] * len(group),
            )
        )

    questions = [
        prepare_choice_question(question, CSP_S_ROUND1_FORMAT)
        for question in [*first_questions, *prepared_reading, *prepared_completion]
    ]
    reading_start = len(first_questions)
    completion_start = reading_start + len(prepared_reading)
    sections = [
        {
            "id": "part1",
            "title": part1_title,
            "score": 30.0,
            "question_indices": list(range(0, reading_start)),
        },
        {
            "id": "part2",
            "title": reading_title,
            "score": 40.0,
            "question_indices": list(range(reading_start, completion_start)),
            "programs": _section_program_ranges(reading_start, reading_groups),
        },
        {
            "id": "part3",
            "title": completion_title,
            "score": 30.0,
            "question_indices": list(range(completion_start, len(questions))),
            "programs": _section_program_ranges(completion_start, completion_groups),
        },
    ]
    total_score = sum(question_score(question) for question in questions)
    if len(questions) not in {42, 43} or total_score != CSP_S_ROUND1_TOTAL_SCORE:
        raise RuntimeError("CSP-S 第一轮固定结构校验失败，请检查导入题库。")
    return {
        "title": title,
        "duration_minutes": duration,
        "question_bank": CSP_S_ROUND1_FORMAT,
        "question_bank_label": "CSP-S 第一轮",
        "principle": (
            "CSP-S 第一轮固定结构：15 道单选题；3 个阅读程序共 "
            f"{len(prepared_reading)} 道小题；2 个完善程序共 10 个空；满分 100 分。"
        ),
        "exam_format": CSP_S_ROUND1_FORMAT,
        "total_score": CSP_S_ROUND1_TOTAL_SCORE,
        "sections": sections,
        "source_template": f"混合基础单选题；阅读/完善程序模板：CSP-S {template['year']}",
        "choice_questions": questions,
        "programming_tasks": [],
    }


def question_competition(item: dict) -> str:
    explicit = item.get("competition")
    if explicit:
        return str(explicit)

    source = str(item.get("source", ""))
    item_id = str(item.get("id", ""))
    haystack = f"{source} {item_id}".lower()
    if any(keyword in source for keyword in ("信息素养", "丝路新程", "复赛", "总决赛")) or "fusai" in haystack:
        return "literacy"
    if any(keyword in source for keyword in ("CSP", "NOI", "HKOI", "CCF")):
        return "csp"
    if "GESP" in source or "gesp" in haystack:
        return "gesp"
    if "福州" in source or item_id.startswith("fz-"):
        return "fuzhou"
    return "general"


def question_bank_profile(key: str) -> dict:
    return QUESTION_BANK_PROFILES.get(key, QUESTION_BANK_PROFILES["all"])


def filter_bank_items(items: list[dict], bank_key: str, item_type: str) -> list[dict]:
    profile = question_bank_profile(bank_key)
    if item_type not in profile["item_types"]:
        return []
    competitions = profile["competitions"]
    if competitions is None:
        return list(items)
    return [item for item in items if question_competition(item) in competitions]


def bank_counts(bank_key: str) -> tuple[int, int]:
    return (
        len(filter_bank_items(CHOICE_QUESTIONS, bank_key, "choice")),
        len(filter_bank_items(PROGRAMMING_TASKS, bank_key, "programming")),
    )


def bank_label(bank_key: str) -> str:
    return question_bank_profile(bank_key)["label"]


def form_int(value: object, default: int) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def normalize_exam_form_defaults(values: dict | None = None) -> dict:
    merged = dict(DEFAULT_EXAM_FORM)
    if values:
        merged.update(values)

    question_bank = str(merged.get("question_bank", DEFAULT_EXAM_FORM["question_bank"]))
    if question_bank not in QUESTION_BANK_PROFILES:
        question_bank = DEFAULT_EXAM_FORM["question_bank"]

    choice_total, program_total = bank_counts(question_bank)
    if question_bank in CSP_FIXED_ROUND1_FORMATS:
        choice_count = CSP_J_ROUND1_TOTAL_QUESTIONS
        program_count = 0
    else:
        choice_count = max(
            0,
            min(form_int(merged.get("choice_count"), DEFAULT_EXAM_FORM["choice_count"]), choice_total),
        )
        program_count = max(
            0,
            min(form_int(merged.get("program_count"), DEFAULT_EXAM_FORM["program_count"]), program_total),
        )
    title = str(merged.get("title", DEFAULT_EXAM_FORM["title"])).strip()[:80] or DEFAULT_EXAM_FORM["title"]
    return {
        "title": title,
        "question_bank": question_bank,
        "choice_count": choice_count,
        "program_count": program_count,
        "duration": max(1, min(form_int(merged.get("duration"), DEFAULT_EXAM_FORM["duration"]), 240)),
    }


def defaults_from_latest_exam() -> dict | None:
    with db() as conn:
        exam = conn.execute("SELECT * FROM exams ORDER BY id DESC LIMIT 1").fetchone()
    if not exam:
        return None
    payload = json.loads(exam["payload"])
    return {
        "title": exam["title"],
        "question_bank": payload.get("question_bank", DEFAULT_EXAM_FORM["question_bank"]),
        "choice_count": len(payload.get("choice_questions", [])),
        "program_count": len(payload.get("programming_tasks", [])),
        "duration": exam["duration_minutes"],
    }


def load_exam_form_defaults() -> dict:
    with db() as conn:
        row = conn.execute(
            "SELECT value FROM app_settings WHERE name = ?",
            (EXAM_FORM_SETTINGS_KEY,),
        ).fetchone()
    if row:
        try:
            return normalize_exam_form_defaults(json.loads(row["value"]))
        except (TypeError, ValueError, json.JSONDecodeError):
            pass

    return normalize_exam_form_defaults(defaults_from_latest_exam())


def save_exam_form_defaults(values: dict) -> None:
    defaults = normalize_exam_form_defaults(values)
    with db() as conn:
        conn.execute(
            """
            INSERT INTO app_settings(name, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
            """,
            (EXAM_FORM_SETTINGS_KEY, json.dumps(defaults, ensure_ascii=False), now_text()),
        )


def prepare_programming_task(task: dict) -> dict:
    prepared = dict(task)
    if not has_generator(task["id"]):
        public_tests = prepared.get("public_tests") or prepared["tests"][:1]
        hidden_tests = prepared.get("hidden_tests") or prepared["tests"]
        prepared["public_tests"] = public_tests
        prepared["hidden_tests"] = hidden_tests
        prepared["tests"] = hidden_tests
        return prepared
    generated = build_generated_tests(task)
    prepared["public_tests"] = generated["public_tests"]
    prepared["hidden_tests"] = generated["hidden_tests"]
    prepared["tests"] = generated["hidden_tests"]
    return prepared


def build_exam(
    title: str,
    choice_count: int,
    program_count: int,
    duration: int,
    question_bank: str = "literacy",
    used_signatures: set[str] | None = None,
) -> dict:
    if used_signatures is None:
        used_signatures = existing_exam_signatures(question_bank)

    for _ in range(100):
        if question_bank == CSP_J_ROUND1_FORMAT:
            exam = build_csp_j_round1_exam(title, duration)
        elif question_bank == CSP_S_ROUND1_FORMAT:
            exam = build_csp_s_round1_exam(title, duration)
        else:
            choice_pool = filter_bank_items(CHOICE_QUESTIONS, question_bank, "choice")
            programming_pool = filter_bank_items(PROGRAMMING_TASKS, question_bank, "programming")
            missing_generators = missing_generator_ids(programming_pool)
            if missing_generators:
                raise RuntimeError("以下编程题缺少测试生成器：" + ", ".join(missing_generators))
            choice_questions = [
                prepare_choice_question(question, question_bank)
                for question in balanced_pick(choice_pool, choice_count)
            ]
            programming_tasks = [
                prepare_programming_task(task)
                for task in balanced_pick(programming_pool, program_count)
            ]
            profile = question_bank_profile(question_bank)
            exam = {
                "title": title,
                "duration_minutes": duration,
                "question_bank": question_bank,
                "question_bank_label": profile["label"],
                "principle": profile["principle"],
                "choice_questions": choice_questions,
                "programming_tasks": programming_tasks,
            }
        if exam_signature(exam) not in used_signatures:
            return exam

    raise RuntimeError("当前题库可生成的题目组合已与历史试卷重复，请增加题库或调整题目数量。")


def run_cpp_judge(code: str, tests: list[dict]) -> dict:
    if not tests:
        return {
            "status": "NO_TESTS",
            "message": "原始资料未提供可自动测评的样例或测试数据。",
            "passed": 0,
            "total": 0,
            "cases": [],
        }

    if not shutil.which("g++"):
        return {
            "status": "NO_COMPILER",
            "message": "容器内没有找到 g++。",
            "passed": 0,
            "total": len(tests),
            "cases": [],
        }

    JUDGE_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gesp-judge-", dir=JUDGE_DIR) as td:
        workdir = Path(td)
        src = workdir / "main.cpp"
        exe = workdir / "main"
        src.write_text(code, encoding="utf-8")

        compile_cmd = ["g++", "-std=c++17", "-O2", "-pipe", str(src), "-o", str(exe)]
        compiled = subprocess.run(
            compile_cmd,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=8,
        )
        if compiled.returncode != 0:
            return {
                "status": "COMPILE_ERROR",
                "message": compiled.stderr[-2000:],
                "passed": 0,
                "total": len(tests),
                "cases": [],
            }
        exe.chmod(0o755)

        cases = []
        passed = 0
        for index, test in enumerate(tests, 1):
            try:
                result = subprocess.run(
                    [str(exe)],
                    input=test["input"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
            except subprocess.TimeoutExpired:
                cases.append(
                    {
                        "index": index,
                        "status": "TLE",
                        "input": test["input"],
                        "expected": test["output"],
                        "actual": "",
                    }
                )
                continue
            except PermissionError as exc:
                return {
                    "status": "SYSTEM_ERROR",
                    "message": f"判题程序无法执行：{exc}",
                    "passed": passed,
                    "total": len(tests),
                    "cases": cases,
                }

            actual = result.stdout
            ok = result.returncode == 0 and normalize_output(actual) == normalize_output(test["output"])
            if ok:
                passed += 1
            cases.append(
                {
                    "index": index,
                    "status": "AC" if ok else ("RE" if result.returncode != 0 else "WA"),
                    "input": test["input"],
                    "expected": test["output"],
                    "actual": actual if result.returncode == 0 else result.stderr[-1000:],
                }
            )

        return {
            "status": "DONE",
            "message": "",
            "passed": passed,
            "total": len(tests),
            "cases": cases,
        }


def layout(title: str, body: str) -> bytes:
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{h(title)}</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="/">{h(PLATFORM_NAME)}</a>
    <nav>
      <a href="/">考试入口</a>
      <a href="/admin">管理后台</a>
    </nav>
  </header>
  <main>{body}</main>
</body>
</html>"""
    return page.encode("utf-8")


def render_code(code: str) -> str:
    if not code:
        return ""
    return f"<pre class=\"code\"><code>{h(code)}</code></pre>"


def answer_indices(answer: object) -> list[int]:
    if isinstance(answer, list):
        return sorted(int(x) for x in answer)
    return [int(answer)]


def answer_label(indices: list[int]) -> str:
    if not indices:
        return "未作答"
    return ", ".join(LETTERS[i] for i in indices if 0 <= i < len(LETTERS))


def csp_j_choice_explanation(question: dict) -> str:
    explicit = str(question.get("explanation", "")).strip()
    if explicit:
        return explicit
    curated = CSP_J_ROUND1_EXPLANATIONS.get(str(question.get("id", "")), "")
    if curated:
        return curated
    return generated_csp_j_choice_explanation(question)


def generated_csp_s_choice_explanation(question: dict) -> str:
    """Provide a structured explanation for imported CSP-S round-one questions.

    The source bank contains official answers but not a consistent solution
    paragraph for every imported question.  Keep the explanation useful and
    honest: identify the question type, show the correct option, and give the
    appropriate verification method for the question's algorithm or code.
    """
    options = question.get("options", [])
    try:
        correct_indices = answer_indices(question.get("answer"))
    except (TypeError, ValueError):
        return ""
    correct_labels = answer_label(correct_indices)
    correct_options = [
        " ".join(str(options[index]).split())
        for index in correct_indices
        if 0 <= index < len(options)
    ]
    correct_text = "、".join(correct_options)
    answer_text = f"{correct_labels}（{correct_text}）" if correct_text else correct_labels
    question_type = str(question.get("source_question_type") or question.get("type") or "")
    stem = str(question.get("stem", ""))
    code = str(question.get("code", ""))
    searchable = f"{stem} {code}".lower()

    hints = [
        (("kmp", "next", "前后缀"), "逐个位置求模式串的最长相等真前缀和真后缀，并按定义核对 next 数组。"),
        (("线段树", "区间"), "把查询区间按线段树结点区间拆分，分别统计完全包含的结点和沿途访问的父结点。"),
        (("trie", "前缀树"), "按字符逐层插入并合并公共前缀，最后把根结点和所有不同前缀结点相加。"),
        (("拓扑", "dag"), "拓扑序数量取决于当前入度为零结点的选择，不能只由顶点数和边数决定。"),
        (("哈希", "hash", "闭散列", "线性探查"), "先计算哈希地址，再按线性探查顺序跳过已占位置，直到找到第一个空槽。"),
        (("最小生成树", "kruskal", "prim"), "生成树必须连通全部顶点且不形成环，按边权从小到大或按 Prim 的最小切边逐步累加。"),
        (("二叉搜索树", "后序遍历", "前序遍历"), "后序序列最后一个元素是根；利用二叉搜索树的大小关系递归划分左右子树，再得到前序序列。"),
        (("背包", "动态规划"), "设容量状态并逐件转移，比较选择当前物品和不选择当前物品的最优值，同时检查总重量不超过容量。"),
        (("lca", "最近公共祖先"), "公共祖先必须同时位于所有指定结点的祖先链上，并取其中最深的结点逐项排除不可能情况。"),
        (("递归关系", "主定理", "时间复杂度"), "按递归树或主定理比较各层的子问题规模与合并代价，取总量的最高阶。"),
        (("最小堆", "delete-min", "堆顶"), "每次删除堆顶后把末尾元素移到堆顶并向下调整，重复两次即可得到新的最小元素。"),
        (("斐波那契", "重叠子问题"), "朴素递归会重复计算相同子问题；记忆化或自底向上保存已算结果后，每个状态只需计算一次。"),
        (("最短路径", "dijkstra", "bellman"), "从起点开始维护当前最短距离，每次选取可确定的最小距离并松弛相关边，最后核对目标距离。"),
        (("二叉树", "遍历", "前序", "中序", "后序"), "按照遍历定义记录访问顺序，并结合左右子树的结构逐项重建或验证序列。"),
        (("贪心", "greedy"), "每一步选择当前满足条件且最有利的方案，再检查该选择是否保持后续可行性和题目要求的最优性。"),
        (("容斥", "整除", "集合"), "先分别计数，再减去两两交集、加回三者交集，避免同一个对象被重复统计。"),
        (("二分", "binary search"), "维护有序区间和循环不变量，根据中点与目标的关系排除一半区间，并检查边界是否包含答案。"),
        (("动态规划", "dp", "状态转移"), "明确状态含义、初始值和转移来源，按依赖顺序计算后再核对目标状态。"),
        (("深度优先", "dfs", "回溯"), "沿当前分支继续搜索，返回时撤销选择和标记，保证每种状态只在正确的路径上计数。"),
        (("广度优先", "bfs"), "使用队列按层扩展状态；在无权图中第一次到达某点时的层数就是最短距离。"),
        (("排序", "稳定", "插入排序", "冒泡", "归并"), "根据算法的比较和交换方式判断复杂度或稳定性，等值元素是否保持原相对顺序是稳定性的关键。"),
    ]
    method = ""
    for keywords, description in hints:
        if any(keyword.lower() in searchable for keyword in keywords):
            method = description
            break
    if not method:
        method = (
            "把题目条件逐项代入定义或程序执行过程，核对边界、下标、循环次数和数据类型，"
            "再比较各选项，排除与条件不符的结果。"
        )

    if question_type == CSP_J_READING_JUDGMENT_TYPE:
        return f"正确答案为 {answer_text}。{method}本题结论应判为“{correct_text or correct_labels}”。"
    if question_type == CSP_J_READING_CHOICE_TYPE:
        return f"正确答案为 {answer_text}。{method}按程序的实际执行顺序计算，得到的结果与该选项一致。"
    if question_type == CSP_J_COMPLETION_TYPE:
        return f"正确答案为 {answer_text}。{method}将该选项代入空缺后，程序的控制流程、边界和输出满足题目要求。"
    return f"正确答案为 {answer_text}。{method}其余选项不满足题目给出的定义、数据条件或计算结果。"


def csp_s_choice_explanation(question: dict) -> str:
    explicit = str(question.get("explanation", "")).strip()
    return explicit or generated_csp_s_choice_explanation(question)


def generated_csp_j_choice_explanation(question: dict) -> str:
    """Provide a useful fallback for imported CSP-J first-round questions."""
    options = question.get("options", [])
    try:
        correct_indices = answer_indices(question.get("answer"))
    except (TypeError, ValueError):
        return ""
    correct_labels = answer_label(correct_indices)
    correct_options = [
        str(options[index]).strip()
        for index in correct_indices
        if 0 <= index < len(options)
    ]
    correct_text = "、".join(" ".join(option.split()) for option in correct_options)
    answer_text = f"{correct_labels}（{correct_text}）" if correct_text else correct_labels
    question_type = str(question.get("source_question_type") or question.get("type") or "")

    if question_type == CSP_J_READING_JUDGMENT_TYPE:
        return (
            f"这是程序阅读判断题。应按代码执行顺序代入题目条件，重点核对变量取值、"
            f"循环边界和表达式类型；题干结论应判为“{correct_text or correct_labels}”。"
        )
    if question_type == CSP_J_READING_CHOICE_TYPE:
        return (
            f"这是程序阅读单选题。逐句跟踪程序中的变量、循环和输出结果，"
            f"可得到正确选项为 {answer_text}。"
        )
    if question_type == CSP_J_COMPLETION_TYPE:
        return (
            f"将 {answer_text} 代入空缺后，程序才能保持题目要求的控制流程和输出。"
            "检查时可分别代入各选项，重点确认循环条件、下标范围和边界情况。"
        )
    return (
        f"根据题目给出的定义与条件逐项核对，只有 {answer_text} 符合题意；"
        "其余选项与题目条件或相关概念不符。"
    )


def is_csp_j_round1_payload(payload: dict) -> bool:
    if payload.get("question_bank") == CSP_J_ROUND1_FORMAT:
        return True
    if payload.get("exam_format") == CSP_J_ROUND1_FORMAT:
        return True
    return any(
        str(question.get("id", "")).startswith("csp_j_round1-")
        for question in payload.get("choice_questions", [])
    )


def is_csp_s_round1_payload(payload: dict) -> bool:
    if payload.get("question_bank") == CSP_S_ROUND1_FORMAT:
        return True
    if payload.get("exam_format") == CSP_S_ROUND1_FORMAT:
        return True
    return any(
        str(question.get("id", "")).startswith("csp_s_round1-")
        for question in payload.get("choice_questions", [])
    )


def sync_corrected_question_snapshots(payload: dict) -> bool:
    """Update saved paper snapshots for questions whose source data was corrected."""
    changed = False
    for question in payload.get("choice_questions", []):
        rule = CSP_CORRECTED_QUESTION_SNAPSHOT_RULES.get(str(question.get("id", "")))
        if not rule:
            continue
        stem_marker = str(rule.get("stem_contains", ""))
        if stem_marker and stem_marker not in str(question.get("stem", "")):
            continue
        canonical = CHOICE_QUESTIONS_BY_ID.get(str(rule["target_id"]))
        if not canonical:
            continue
        for field in CORRECTED_QUESTION_SNAPSHOT_FIELDS:
            value = canonical.get(field, "")
            if question.get(field) != value:
                question[field] = value
                changed = True
        explanation = str(rule.get("explanation", ""))
        explanation_source = dict(question)
        explanation_source.pop("explanation", None)
        if not explanation and str(question.get("id", "")).startswith("csp_j_round1-"):
            explanation = csp_j_choice_explanation(explanation_source)
        elif not explanation:
            explanation = csp_s_choice_explanation(explanation_source)
        if explanation and question.get("explanation") != explanation:
            question["explanation"] = explanation
            changed = True
    return changed


def sanitize_saved_question_artifacts(payload: dict) -> bool:
    """Remove standalone OCR watermark and section-label lines from saved papers."""
    changed = False
    for question in payload.get("choice_questions", []):
        for field in ("stem", "code"):
            value = sanitize_csp_imported_text(question.get(field, ""))
            if question.get(field, "") != value:
                question[field] = value
                changed = True
        options = [sanitize_csp_imported_text(option) for option in question.get("options", [])]
        if question.get("options", []) != options:
            question["options"] = options
            changed = True
    return changed


def enrich_csp_j_round1_payload(payload: dict) -> bool:
    if not is_csp_j_round1_payload(payload):
        return False
    changed = False
    for question in payload.get("choice_questions", []):
        if str(question.get("explanation", "")).strip():
            continue
        explanation = csp_j_choice_explanation(question)
        if explanation:
            question["explanation"] = explanation
            changed = True
    return changed


def enrich_csp_s_round1_payload(payload: dict) -> bool:
    if not is_csp_s_round1_payload(payload):
        return False
    changed = False
    for question in payload.get("choice_questions", []):
        if str(question.get("explanation", "")).strip():
            continue
        explanation = csp_s_choice_explanation(question)
        if explanation:
            question["explanation"] = explanation
            changed = True
    return changed


def backfill_csp_j_round1_explanations() -> int:
    """Persist corrected question snapshots and missing explanations into saved papers."""
    updated = 0
    with db() as conn:
        rows = conn.execute("SELECT id, payload FROM exams").fetchall()
        for row in rows:
            try:
                payload = json.loads(row["payload"])
            except (TypeError, json.JSONDecodeError):
                continue
            if not is_csp_j_round1_payload(payload):
                continue
            changed = sanitize_saved_question_artifacts(payload)
            if sync_corrected_question_snapshots(payload):
                changed = True
            if enrich_csp_j_round1_payload(payload):
                changed = True
            if not changed:
                continue
            conn.execute(
                "UPDATE exams SET payload = ?, signature = ? WHERE id = ?",
                (json.dumps(payload, ensure_ascii=False), exam_signature(payload), row["id"]),
            )
            updated += 1
    return updated


def backfill_csp_s_round1_explanations() -> int:
    """Persist corrected question snapshots and missing explanations into saved papers."""
    updated = 0
    with db() as conn:
        rows = conn.execute("SELECT id, payload FROM exams").fetchall()
        for row in rows:
            try:
                payload = json.loads(row["payload"])
            except (TypeError, json.JSONDecodeError):
                continue
            if not is_csp_s_round1_payload(payload):
                continue
            changed = sanitize_saved_question_artifacts(payload)
            if sync_corrected_question_snapshots(payload):
                changed = True
            if enrich_csp_s_round1_payload(payload):
                changed = True
            if not changed:
                continue
            conn.execute(
                "UPDATE exams SET payload = ?, signature = ? WHERE id = ?",
                (json.dumps(payload, ensure_ascii=False), exam_signature(payload), row["id"]),
            )
            updated += 1
    return updated


def backfill_round1_explanations() -> int:
    """Backfill explanations for every supported fixed-format first-round paper."""
    return backfill_csp_j_round1_explanations() + backfill_csp_s_round1_explanations()


def prepare_choice_question(question: dict, question_bank: str) -> dict:
    prepared = dict(question)
    if question_bank == "csp_j_round1":
        prepared["explanation"] = csp_j_choice_explanation(question)
    elif question_bank == CSP_S_ROUND1_FORMAT:
        prepared["explanation"] = csp_s_choice_explanation(question)
    return prepared


def is_multiple_choice(question: dict) -> bool:
    return isinstance(question.get("answer"), list) or question.get("type") == "multiple_choice"


def objective_type_label(question: dict) -> str:
    explicit = str(question.get("display_type", "")).strip()
    if explicit:
        return explicit
    return "多选题" if is_multiple_choice(question) else "单选题"


def objective_counts(questions: list[dict]) -> tuple[int, int]:
    multi_count = sum(1 for question in questions if is_multiple_choice(question))
    return len(questions) - multi_count, multi_count


def exam_total_score(payload: dict) -> float:
    if payload.get("total_score") is not None:
        return float(payload["total_score"])
    return sum(question_score(question) for question in payload.get("choice_questions", []))


def exam_summary(payload: dict) -> str:
    if payload.get("exam_format") == CSP_J_ROUND1_FORMAT:
        return "43 道小题 · 满分 100 分 · 15 单选 + 3 段阅读程序 + 2 段完善程序"
    if payload.get("exam_format") == CSP_S_ROUND1_FORMAT:
        return (
            f"{len(payload.get('choice_questions', []))} 道小题 · 满分 100 分 · "
            "15 单选 + 3 段阅读程序 + 2 段完善程序"
        )
    single_count, multi_count = objective_counts(payload.get("choice_questions", []))
    return (
        f"{len(payload.get('choice_questions', []))} 道客观题（单选 {single_count} / 多选 {multi_count}）"
        f" · {len(payload.get('programming_tasks', []))} 道编程题"
    )


def csp_j_section_questions(payload: dict, section_id: str) -> list[dict]:
    return [
        question
        for question in payload.get("choice_questions", [])
        if question.get("section_id") == section_id
    ]


def render_question_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    content = raw_html
    content = re.sub(r"\sstyle=\"[^\"]*\"", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\sclass=\"[^\"]*\"", "", content, flags=re.IGNORECASE)
    content = re.sub(r"<script\b[^>]*>.*?</script>", "", content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r"<(?!/?(?:p|br|span|strong|b|em|i|code|pre|img)\b)[^>]+>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"<img\b([^>]*)>", _sanitize_img_tag, content, flags=re.IGNORECASE)
    content = re.sub(r"<(p|br|span|strong|b|em|i|code|pre)\b[^>]*>", r"<\1>", content, flags=re.IGNORECASE)
    return f"<div class=\"richtext\">{content}</div>"


def _sanitize_img_tag(match: re.Match[str]) -> str:
    src_match = re.search(r"\bsrc=[\"']([^\"']+)[\"']", match.group(1), flags=re.IGNORECASE)
    if not src_match:
        return ""
    src = src_match.group(1)
    if not src.startswith(("https://cdn2.1717youxue.com/", "https://study.1717youxue.com/")):
        return ""
    return f"<img src=\"{h(src)}\" alt=\"题目图片\" loading=\"lazy\">"


def render_choice_explanation(question: dict, explanation: str) -> str:
    options = "".join(
        f'<li><b>{LETTERS[index]}.</b> {h(option)}</li>'
        for index, option in enumerate(question.get("options", []))
        if index < len(LETTERS)
    )
    correct_answer = answer_label(answer_indices(question["answer"])) if "answer" in question else ""
    return f"""
    <div class="answer-explanation-content">
      <section class="answer-explanation-question">
        <h3>题目</h3>
        <p>{h(question.get("stem", ""))}</p>
        {render_question_html(question.get("content_html", ""))}
        {render_code(question.get("code", ""))}
      </section>
      <section>
        <h3>选项</h3>
        <ol class="answer-explanation-options">{options}</ol>
      </section>
      <p class="answer-explanation-correct"><b>正确答案：</b>{h(correct_answer)}</p>
      <section>
        <h3>解析</h3>
        <p>{h(explanation)}</p>
      </section>
    </div>
    """


def load_exam(exam_id: int) -> sqlite3.Row | None:
    with db() as conn:
        return conn.execute("SELECT * FROM exams WHERE id = ?", (exam_id,)).fetchone()


def save_exam(payload: dict) -> int:
    signature = exam_signature(payload)
    with db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        duplicate = conn.execute(
            "SELECT id FROM exams WHERE signature = ? LIMIT 1",
            (signature,),
        ).fetchone()
        if duplicate:
            raise DuplicateExamError(f"试卷题目组合已存在：#{duplicate['id']}")
        cur = conn.execute(
            """
            INSERT INTO exams(title, duration_minutes, payload, created_at, signature)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload["title"],
                payload["duration_minutes"],
                json.dumps(payload, ensure_ascii=False),
                now_text(),
                signature,
            ),
        )
        return int(cur.lastrowid)


def public_home() -> bytes:
    with db() as conn:
        exams = conn.execute("SELECT * FROM exams ORDER BY id DESC").fetchall()

    cards = []
    for exam in exams:
        payload = json.loads(exam["payload"])
        label = payload.get("question_bank_label", "素养大赛")
        cards.append(
            f"""
            <article class="exam-card">
              <div>
                <h2>{h(exam["title"])}</h2>
                <p>{h(label)} · {h(exam_summary(payload))} · {exam["duration_minutes"]} 分钟</p>
              </div>
              <a class="button" href="/exam/{exam["id"]}">开始考试</a>
            </article>
            """
        )

    empty = "<p class=\"muted\">还没有试卷。先进入管理后台创建一份。</p>" if not cards else ""
    return layout(
        "考试入口",
        f"""
        <section class="hero compact">
          <h1>{h(PLATFORM_NAME)}</h1>
          <p>按题库来源和竞赛方向自动组卷，考生在线作答，编程题提交 C++17 代码后即时测评。</p>
        </section>
        <section class="panel">
          <div class="section-title">
            <h2>可参加考试</h2>
            <a class="ghost" href="/admin">创建试卷</a>
          </div>
          <div class="exam-list">{''.join(cards)}{empty}</div>
        </section>
        """,
    )


def admin_page(message: str = "") -> bytes:
    with db() as conn:
        exams = conn.execute("SELECT * FROM exams ORDER BY id DESC LIMIT 20").fetchall()

    rows = []
    for exam in exams:
        payload = json.loads(exam["payload"])
        label = payload.get("question_bank_label", "素养大赛")
        rows.append(
            f"""
            <tr>
              <td>#{exam["id"]}</td>
              <td>{h(exam["title"])}</td>
              <td>{h(label)}</td>
              <td>{h(exam_summary(payload))}</td>
              <td>{h(exam["created_at"])}</td>
              <td class="actions">
                <a href="/exam/{exam["id"]}">考试页</a>
                <a href="/admin/exams/{exam["id"]}">成绩</a>
                <form method="post" action="/admin/exams/{exam["id"]}/delete" onsubmit="return confirm('确定删除这份试卷和所有提交记录吗？');">
                  <button class="link-danger" type="submit">删除</button>
                </form>
              </td>
            </tr>
            """
        )

    notice = f"<div class=\"notice\">{h(message)}</div>" if message else ""
    form_defaults = load_exam_form_defaults()
    bank_options = []
    bank_summary = []
    for key, profile in QUESTION_BANK_PROFILES.items():
        choice_total, program_total = bank_counts(key)
        selected = " selected" if key == form_defaults["question_bank"] else ""
        count_label = (
            "固定 43 题 / 100 分"
            if key == CSP_J_ROUND1_FORMAT
            else "固定 42～43 题 / 100 分"
            if key == CSP_S_ROUND1_FORMAT
            else f"客观 {choice_total} / 编程 {program_total}"
        )
        bank_options.append(
            f"<option value=\"{h(key)}\"{selected}>{h(profile['label'])}（{count_label}）</option>"
        )
        bank_summary.append(f"{h(profile['label'])}: {count_label}")
    return layout(
        "管理后台",
        f"""
        <section class="admin-grid">
          <form class="panel form-panel" method="post" action="/admin/exams">
            <h1>创建试卷</h1>
            {notice}
            <label>试卷标题
              <input name="title" value="{h(form_defaults['title'])}" required>
            </label>
            <label>题库范围
              <select name="question_bank">
                {''.join(bank_options)}
              </select>
            </label>
            <div class="two">
              <label>客观题数量
                <input name="choice_count" type="number" min="0" max="{len(CHOICE_QUESTIONS)}" value="{form_defaults['choice_count']}"{' readonly' if form_defaults['question_bank'] in CSP_FIXED_ROUND1_FORMATS else ''}>
              </label>
              <label>编程题数量
                <input name="program_count" type="number" min="0" max="{len(PROGRAMMING_TASKS)}" value="{form_defaults['program_count']}"{' readonly' if form_defaults['question_bank'] in CSP_FIXED_ROUND1_FORMATS else ''}>
              </label>
            </div>
            <label>考试时长（分钟）
              <input name="duration" type="number" min="1" max="240" value="{form_defaults['duration']}">
            </label>
            <button class="button primary" type="submit">生成试卷</button>
            <p class="hint">当前题库：{'; '.join(bank_summary)}。选择 CSP-J/S 第一轮时自动按真实卷面结构生成试卷，题目数量无需设置。</p>
          </form>
          <section class="panel">
            <h2>最近试卷</h2>
            <table>
              <thead><tr><th>ID</th><th>标题</th><th>题库</th><th>客观/编程</th><th>创建时间（北京时间）</th><th>操作</th></tr></thead>
              <tbody>{''.join(rows) or '<tr><td colspan="6">暂无试卷</td></tr>'}</tbody>
            </table>
          </section>
        </section>
        """,
    )


def exam_page(exam_id: int) -> bytes:
    exam = load_exam(exam_id)
    if not exam:
        return not_found()
    payload = json.loads(exam["payload"])
    label = payload.get("question_bank_label", "素养大赛")
    is_fixed_round1 = payload.get("exam_format") in CSP_FIXED_ROUND1_FORMATS

    nav = []
    choice_html = []
    last_program_key = None
    last_section_id = None
    for i, q in enumerate(payload["choice_questions"], 1):
        nav.append(f"<a href=\"#q{i}\" data-target=\"q{i}\">{i}</a>")
        opts = []
        multi = is_multiple_choice(q)
        input_type = "checkbox" if multi else "radio"
        type_label = objective_type_label(q)
        section_html = ""
        if q.get("section_id") != last_section_id:
            section_html = f'<h1>{h(q.get("section_title", "一、客观题"))}</h1>'
            last_section_id = q.get("section_id")
            last_program_key = None
        program_key = (q.get("section_id"), q.get("program_index"))
        if is_fixed_round1 and q.get("program_index") and program_key != last_program_key:
            section_html += f'<h2>程序 {q["program_index"]}</h2>'
            last_program_key = program_key
        code_html = render_code(q["code"])
        if is_fixed_round1 and q.get("program_index") and program_key == last_program_key and i > 1:
            previous = payload["choice_questions"][i - 2]
            if (
                previous.get("section_id") == q.get("section_id")
                and previous.get("program_index") == q.get("program_index")
            ):
                code_html = ""
        for oi, opt in enumerate(q["options"]):
            opts.append(
                f"""
                <label class="option">
                  <input type="{input_type}" name="choice_{i}" value="{oi}">
                  <span>{LETTERS[oi]}. {h(opt)}</span>
                </label>
                """
            )
        choice_html.append(
            f"""
            {section_html}
            <section class="question-card" id="q{i}">
              <div class="q-head"><span>{type_label} {i}</span><small>{h(q["category"])} · {format_score(question_score(q))} 分</small></div>
              <p>{h(q["stem"])}</p>
              {render_question_html(q.get("content_html", ""))}
              {code_html}
              <div class="options">{''.join(opts)}</div>
            </section>
            """
        )

    program_html = []
    for pi, task in enumerate(payload["programming_tasks"], 1):
        nav.append(f"<a href=\"#p{pi}\" data-target=\"p{pi}\">P{pi}</a>")
        public_tests = task.get("public_tests") or task["tests"][:1]
        hidden_tests = task.get("hidden_tests") or task["tests"]
        test_label = f"公开样例 {len(public_tests)} 组 · 隐藏测试 {len(hidden_tests)} 组"
        sample_note = (
            "页面仅显示公开样例，提交后使用隐藏测试评分。"
            if hidden_tests
            else "原始资料未提供可抽取样例，本题仅展示题面用于练习讲解。"
        )
        samples = "".join(
            f"<tr><td>{idx}</td><td><pre>{h(t['input'])}</pre></td><td><pre>{h(t['output'])}</pre></td></tr>"
            for idx, t in enumerate(public_tests, 1)
        )
        program_html.append(
            f"""
            <section class="question-card" id="p{pi}">
              <div class="q-head"><span>编程题 {pi}. {h(task["title"])}</span><small>{h(task["category"])} · {h(test_label)}</small></div>
              <p>{h(task["description"])}</p>
              <div class="io-grid">
                <div><b>输入格式</b><p>{h(task["input"])}</p></div>
                <div><b>输出格式</b><p>{h(task["output"])}</p></div>
              </div>
              <p class="hint">数据范围：{h(task["constraints"])}</p>
              <p class="hint">{h(sample_note)}</p>
              <table class="samples"><thead><tr><th>#</th><th>公开输入</th><th>公开输出</th></tr></thead><tbody>{samples}</tbody></table>
              <label class="code-label">提交 C++17 代码
                <textarea name="code_{pi}" spellcheck="false">#include &lt;iostream&gt;
#include &lt;vector&gt;
#include &lt;algorithm&gt;
#include &lt;string&gt;
using namespace std;

int main() {{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    return 0;
}}</textarea>
              </label>
            </section>
            """
        )

    return layout(
        payload["title"],
        f"""
        <form class="exam-shell" method="post" action="/exam/{exam_id}/submit">
          <aside class="exam-side">
            <h2>{h(payload["title"])}</h2>
            <p>{h(label)} · {h(exam_summary(payload))} · {exam["duration_minutes"]} 分钟</p>
            <div class="timer-box" data-duration-minutes="{exam["duration_minutes"]}">
              <span>剩余时间</span>
              <strong id="examTimer">--:--</strong>
            </div>
            <input type="hidden" name="auto_submitted" value="0">
            <label>考生姓名
              <input name="student_name" required placeholder="请输入姓名">
            </label>
            <div class="nav-grid">{''.join(nav)}</div>
            <button class="button primary full" type="submit">提交试卷</button>
          </aside>
          <section class="exam-main">
            <div class="principle">{h(payload["principle"])}</div>
            {'' if is_fixed_round1 else '<h1>一、客观题</h1>'}
            {''.join(choice_html)}
            {'' if is_fixed_round1 else '<h1>二、编程题</h1>'}
            {''.join(program_html)}
          </section>
        </form>
        <script>
        (() => {{
          const form = document.querySelector(".exam-shell");
          if (!form) return;
          const timerBox = form.querySelector(".timer-box");
          const timerText = form.querySelector("#examTimer");
          const submitButton = form.querySelector('button[type="submit"]');
          const autoSubmitted = form.querySelector('input[name="auto_submitted"]');
          const studentName = form.querySelector('input[name="student_name"]');
          let submitted = false;

          const defaultCodes = new Map();
          form.querySelectorAll('textarea[name^="code_"]').forEach((textarea) => {{
            defaultCodes.set(textarea.name, textarea.value.trim());
          }});

          const setAnswered = (targetId, answered) => {{
            const link = form.querySelector(`.nav-grid a[data-target="${{targetId}}"]`);
            if (link) link.classList.toggle("answered", answered);
          }};

          const updateChoice = (input) => {{
            const index = input.name.replace("choice_", "");
            const checked = form.querySelectorAll(`input[name="${{input.name}}"]:checked`).length > 0;
            setAnswered(`q${{index}}`, checked);
          }};

          const updateCode = (textarea) => {{
            const index = textarea.name.replace("code_", "");
            const original = defaultCodes.get(textarea.name) || "";
            setAnswered(`p${{index}}`, textarea.value.trim() !== original);
          }};

          form.querySelectorAll('input[name^="choice_"]').forEach((input) => {{
            input.addEventListener("change", () => updateChoice(input));
            updateChoice(input);
          }});

          form.querySelectorAll('textarea[name^="code_"]').forEach((textarea) => {{
            textarea.addEventListener("input", () => updateCode(textarea));
            updateCode(textarea);
          }});

          form.addEventListener("submit", () => {{
            submitted = true;
            if (submitButton) submitButton.disabled = true;
          }});

          const durationMinutes = Number(timerBox?.dataset.durationMinutes || 0);
          if (timerBox && timerText && durationMinutes > 0) {{
            const deadline = Date.now() + durationMinutes * 60 * 1000;
            const renderTimer = () => {{
              const remaining = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
              const minutes = Math.floor(remaining / 60);
              const seconds = remaining % 60;
              timerText.textContent = `${{String(minutes).padStart(2, "0")}}:${{String(seconds).padStart(2, "0")}}`;
              timerBox.classList.toggle("warning", remaining <= 5 * 60);
              timerBox.classList.toggle("danger", remaining <= 60);
              if (remaining <= 0 && !submitted) {{
                submitted = true;
                if (autoSubmitted) autoSubmitted.value = "1";
                if (studentName && !studentName.value.trim()) {{
                  studentName.value = "未填写姓名";
                }}
                form.requestSubmit ? form.requestSubmit() : form.submit();
              }}
            }};
            renderTimer();
            setInterval(renderTimer, 1000);
          }}
        }})();
        </script>
        """,
    )


def result_page(submission_id: int) -> bytes:
    with db() as conn:
        row = conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()
    if not row:
        return not_found()
    detail = json.loads(row["detail"])
    exam = load_exam(row["exam_id"])
    exam_payload = json.loads(exam["payload"]) if exam else {}
    exam_choices = exam_payload.get("choice_questions", [])
    has_round1_explanations = (
        is_csp_j_round1_payload(exam_payload)
        or is_csp_s_round1_payload(exam_payload)
    )

    choice_rows = []
    for item in detail["choices"]:
        status = "正确" if item["ok"] else "错误"
        result_class = "correct" if item["ok"] else "wrong"
        question_index = int(item["index"]) - 1
        question = exam_choices[question_index] if 0 <= question_index < len(exam_choices) else {}
        if is_csp_j_round1_payload(exam_payload):
            explanation = csp_j_choice_explanation(question)
        elif is_csp_s_round1_payload(exam_payload):
            explanation = csp_s_choice_explanation(question)
        else:
            explanation = ""
        explanation_cell = '<span class="muted">—</span>'
        if not item["ok"] and has_round1_explanations and explanation:
            explanation_cell = (
                '<details class="answer-explanation">'
                '<summary>查看答案解析</summary>'
                f'{render_choice_explanation(question, explanation)}'
                '</details>'
            )
        choice_rows.append(
            f"<tr class=\"answer-row {result_class}\"><td>{item['index']}</td><td>{h(item.get('type', '客观题'))}</td><td class=\"answer-selected {result_class}\">{h(item['selected'])}</td><td class=\"answer-correct\">{h(item['answer'])}</td><td><span class=\"answer-status {result_class}\">{status}</span></td><td class=\"answer-explanation-cell\">{explanation_cell}</td></tr>"
        )

    program_blocks = []
    for item in detail["programs"]:
        case_rows = []
        for case in item["result"]["cases"]:
            test_input = case.get("input", "旧记录未保存输入")
            case_rows.append(
                f"<tr><td>{case['index']}</td><td><span class=\"badge {h(case['status']).lower()}\">{h(case['status'])}</span></td><td><pre>{h(test_input)}</pre></td><td><pre>{h(case['expected'])}</pre></td><td><pre>{h(case['actual'])}</pre></td></tr>"
            )
        msg = f"<pre class=\"compile-msg\">{h(item['result']['message'])}</pre>" if item["result"]["message"] else ""
        program_blocks.append(
            f"""
            <section class="question-card">
              <div class="q-head"><span>{h(item["title"])}</span><small>{item["result"]["passed"]}/{item["result"]["total"]}</small></div>
              {msg}
              <table class="samples result-cases"><thead><tr><th>#</th><th>状态</th><th>隐藏测试输入</th><th>正确输出</th><th>考生输出</th></tr></thead><tbody>{''.join(case_rows) or '<tr><td colspan="5">未运行测试</td></tr>'}</tbody></table>
            </section>
            """
        )

    return layout(
        "提交结果",
        f"""
        <section class="panel result-head">
          <h1>{h(row["student_name"])} 的提交结果</h1>
          <div class="score">
            <b>客观题 {format_score(row["choice_score"])}/{format_score(row["choice_total"])} 分</b>
            <b>编程测试 {row["program_score"]}/{row["program_total"]}</b>
          </div>
          <p class="muted">提交时间（北京时间）：{h(row["created_at"])}</p>
        </section>
        <section class="panel">
          <h2>客观题明细</h2>
          <table><thead><tr><th>题号</th><th>题型</th><th>作答</th><th>答案</th><th>结果</th><th>答案解析</th></tr></thead><tbody>{''.join(choice_rows)}</tbody></table>
        </section>
        <section>{''.join(program_blocks)}</section>
        """,
    )


def admin_exam_detail(exam_id: int) -> bytes:
    exam = load_exam(exam_id)
    if not exam:
        return not_found()
    with db() as conn:
        rows = conn.execute("SELECT * FROM submissions WHERE exam_id = ? ORDER BY id DESC", (exam_id,)).fetchall()

    body_rows = []
    for row in rows:
        body_rows.append(
            f"""
            <tr>
              <td>#{row["id"]}</td>
              <td>{h(row["student_name"])}</td>
              <td>{format_score(row["choice_score"])}/{format_score(row["choice_total"])} 分</td>
              <td>{row["program_score"]}/{row["program_total"]}</td>
              <td>{h(row["created_at"])}</td>
              <td><a href="/result/{row["id"]}">查看</a></td>
            </tr>
            """
        )
    return layout(
        "成绩",
        f"""
        <section class="panel">
          <div class="section-title">
            <h1>{h(exam["title"])}</h1>
            <a class="ghost" href="/exam/{exam_id}">考试页</a>
          </div>
          <table>
            <thead><tr><th>ID</th><th>姓名</th><th>客观题</th><th>编程测试</th><th>考试时间（北京时间）</th><th>详情</th></tr></thead>
            <tbody>{''.join(body_rows) or '<tr><td colspan="6">暂无提交</td></tr>'}</tbody>
          </table>
        </section>
        """,
    )


def handle_create_exam(params: dict[str, list[str]]) -> bytes:
    current_defaults = load_exam_form_defaults()
    form_defaults = normalize_exam_form_defaults(
        {
            "title": params.get("title", [current_defaults["title"]])[0],
            "question_bank": params.get("question_bank", [current_defaults["question_bank"]])[0],
            "choice_count": params.get("choice_count", [current_defaults["choice_count"]])[0],
            "program_count": params.get("program_count", [current_defaults["program_count"]])[0],
            "duration": params.get("duration", [current_defaults["duration"]])[0],
        }
    )
    used_signatures = existing_exam_signatures(form_defaults["question_bank"])
    for _ in range(100):
        try:
            payload = build_exam(
                form_defaults["title"],
                form_defaults["choice_count"],
                form_defaults["program_count"],
                form_defaults["duration"],
                form_defaults["question_bank"],
                used_signatures=used_signatures,
            )
            exam_id = save_exam(payload)
            break
        except DuplicateExamError:
            used_signatures.add(exam_signature(payload))
        except RuntimeError as exc:
            return admin_page(str(exc))
    else:
        return admin_page("当前题库可生成的题目组合已用尽，请增加题库或调整题目数量。")
    save_exam_form_defaults(form_defaults)
    return redirect(f"/admin/exams/{exam_id}")


def handle_delete_exam(exam_id: int) -> bytes:
    with db() as conn:
        exam = conn.execute("SELECT id FROM exams WHERE id = ?", (exam_id,)).fetchone()
        if exam:
            conn.execute("DELETE FROM submissions WHERE exam_id = ?", (exam_id,))
            conn.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
    return redirect("/admin")


def handle_submit(exam_id: int, params: dict[str, list[str]]) -> bytes:
    exam = load_exam(exam_id)
    if not exam:
        return not_found()
    payload = json.loads(exam["payload"])
    student_name = params.get("student_name", ["匿名"])[0].strip()[:40] or "匿名"

    choice_details = []
    choice_score = 0.0
    for i, q in enumerate(payload["choice_questions"], 1):
        selected_values = params.get(f"choice_{i}", [])
        selected = sorted(int(value) for value in selected_values if value.isdigit())
        correct = answer_indices(q["answer"])
        ok = selected == correct
        earned_score = question_score(q) if ok else 0.0
        if ok:
            choice_score += earned_score
        choice_details.append(
            {
                "index": i,
                "selected": answer_label(selected),
                "answer": answer_label(correct),
                "ok": ok,
                "score": question_score(q),
                "earned_score": earned_score,
                "type": objective_type_label(q),
                "question_id": q.get("id", ""),
            }
        )

    program_details = []
    program_score = 0
    program_total = 0
    for i, task in enumerate(payload["programming_tasks"], 1):
        code = params.get(f"code_{i}", [""])[0]
        judge_tests = task.get("hidden_tests") or task["tests"]
        result = run_cpp_judge(code, judge_tests)
        program_score += result["passed"]
        program_total += result["total"]
        program_details.append({"index": i, "title": task["title"], "result": result})

    detail = {"choices": choice_details, "programs": program_details}
    with db() as conn:
        cur = conn.execute(
            """
            INSERT INTO submissions(exam_id, student_name, choice_score, choice_total, program_score, program_total, detail, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                exam_id,
                student_name,
                choice_score,
                exam_total_score(payload),
                program_score,
                program_total,
                json.dumps(detail, ensure_ascii=False),
                now_text(),
            ),
        )
        submission_id = int(cur.lastrowid)
    return redirect(f"/result/{submission_id}")


def redirect(path: str) -> bytes:
    return f"REDIRECT:{path}".encode()


def not_found() -> bytes:
    return layout("未找到", "<section class=\"panel\"><h1>页面不存在</h1><p>请检查链接是否正确。</p></section>")


class Handler(BaseHTTPRequestHandler):
    server_version = "CppContestExam/0.2"

    def send_html(self, data: bytes, status: int = 200) -> None:
        if data.startswith(b"REDIRECT:"):
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", data.decode().split(":", 1)[1])
            self.end_headers()
            return
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/static/style.css":
            css = (ROOT / "static" / "style.css").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.send_header("Content-Length", str(len(css)))
            self.end_headers()
            self.wfile.write(css)
            return
        if path == "/":
            self.send_html(public_home())
            return
        if path == "/admin":
            self.send_html(admin_page())
            return
        match = re.fullmatch(r"/exam/(\d+)", path)
        if match:
            self.send_html(exam_page(int(match.group(1))))
            return
        match = re.fullmatch(r"/result/(\d+)", path)
        if match:
            self.send_html(result_page(int(match.group(1))))
            return
        match = re.fullmatch(r"/admin/exams/(\d+)", path)
        if match:
            self.send_html(admin_exam_detail(int(match.group(1))))
            return
        self.send_html(not_found(), 404)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(min(length, 2_000_000)).decode("utf-8", errors="replace")
        params = parse_qs(raw, keep_blank_values=True)
        path = urlparse(self.path).path
        if path == "/admin/exams":
            self.send_html(handle_create_exam(params))
            return
        match = re.fullmatch(r"/admin/exams/(\d+)/delete", path)
        if match:
            self.send_html(handle_delete_exam(int(match.group(1))))
            return
        match = re.fullmatch(r"/exam/(\d+)/submit", path)
        if match:
            self.send_html(handle_submit(int(match.group(1)), params))
            return
        self.send_html(not_found(), 404)


def main() -> None:
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Listening on http://{HOST}:{PORT}, db={DB_PATH}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
