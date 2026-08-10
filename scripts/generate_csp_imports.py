"""Generate structured CSP-J/S imports from local source papers.

The local ``CSP/题库`` tree is kept outside Git because it contains large source
documents. This script extracts the machine-readable parts into a small Python
module consumed by the exam app.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import pprint
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "online_exam" / "imported_csp_questions.py"
HKOI_ROOT = "CSP/题库/香港 hkoi-cspjs-past-problems"
CSP_X_ROOT = "CSP/题库/CSP-X(山东)"


def tool_path(name: str) -> Path:
    candidates = [
        Path.home() / f".cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/{name}",
        Path.home() / f".cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/bin/{name}",
        Path.home() / f".cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/{name}",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    found = shutil.which(name)
    return Path(found) if found else Path(name)


PDFTOTEXT = tool_path("pdftotext")
PDFTOPPM = tool_path("pdftoppm")
PDFINFO = tool_path("pdfinfo")
TESSERACT = tool_path("tesseract")
OCR_CACHE_DIR = Path(tempfile.gettempdir()) / "cpp_exam_csp_ocr_cache"


@dataclass(frozen=True)
class Round1Source:
    competition: str
    level_label: str
    year: int
    question_path: str
    answer_path: str | None
    difficulty: int


@dataclass(frozen=True)
class Round2Source:
    competition: str
    level_label: str
    year: int
    question_path: str
    difficulty: int


ROUND1_SOURCES = [
    Round1Source("csp_j_round1", "CSP-J", 2019, "CSP/题库/CSP-J/2019/Round1/cspjs2019hj_cpp.pdf", "CSP/题库/CSP-J/2019/Round1/cspjs2019hj_sol.pdf", 4),
    Round1Source("csp_j_round1", "CSP-J", 2020, "CSP/题库/CSP-J/2020/Round1/cspjs2020hj_cpp.pdf", "CSP/题库/CSP-J/2020/Round1/cspjs2020hj_sol.pdf", 4),
    Round1Source("csp_j_round1", "CSP-J", 2021, "CSP/题库/CSP-J/2021/Round1/cspjs2021hj_cpp.pdf", "CSP/题库/CSP-J/2021/Round1/cspjs2021hj_sol.pdf", 4),
    Round1Source("csp_j_round1", "CSP-J", 2022, "CSP/题库/CSP-J/2022/Round1/2022CSPJ1试题.pdf", "CSP/题库/CSP-J/2022/Round1/第一轮认证答案-入门级.pdf", 4),
    Round1Source("csp_j_round1", "CSP-J", 2023, "CSP/题库/CSP-J/2023/Round1/[全国卷]CSP-J1-2023.pdf", "CSP/题库/CSP-J/2023/Round1/solution.pdf", 4),
    Round1Source("csp_j_round1", "CSP-J", 2024, "CSP/题库/CSP-J/2024/Round1/CSP-J1-2024.pdf", "CSP/题库/CSP-J/2024/Round1/solution.pdf", 4),
    Round1Source("csp_s_round1", "CSP-S", 2019, "CSP/题库/CSP-S/2019/Round1/cspjs2019hs_cpp.pdf", "CSP/题库/CSP-S/2019/Round1/cspjs2019hs_sol.pdf", 5),
    Round1Source("csp_s_round1", "CSP-S", 2020, "CSP/题库/CSP-S/2020/Round1/cspjs2020hs_cpp.pdf", "CSP/题库/CSP-S/2020/Round1/cspjs2020hs_sol.pdf", 5),
    Round1Source("csp_s_round1", "CSP-S", 2021, "CSP/题库/CSP-S/2021/Round1/2021CSP-S1试题(C++).pdf", "CSP/题库/CSP-S/2021/Round1/2021CSP-S1试题及参考答案.pdf", 5),
    Round1Source("csp_s_round1", "CSP-S", 2022, "CSP/题库/CSP-S/2022/Round1/2022CSP-S1试题.pdf", "CSP/题库/CSP-S/2022/Round1/2022SCP-S1答案.pdf", 5),
    Round1Source("csp_s_round1", "CSP-S", 2023, "CSP/题库/CSP-S/2023/Round1/CSP-S1-2023.pdf", "CSP/题库/CSP-S/2023/Round1/solution.pdf", 5),
    Round1Source("csp_s_round1", "CSP-S", 2024, "CSP/题库/CSP-S/2024/Round1/CSP-S1-2024.pdf", "CSP/题库/CSP-S/2024/Round1/solution.pdf", 5),
    Round1Source("csp_s_round1", "CSP-S", 2025, "CSP/题库/CSP-S/2025/Round1/CSP-S 2025.md", None, 5),
]

ROUND2_SOURCES = [
    Round2Source("csp_j_round2", "CSP-J", 2019, "CSP/题库/CSP-J/2019/Round2/2019-CCF-CSP-J2.pdf", 5),
    Round2Source("csp_j_round2", "CSP-J", 2020, "CSP/题库/CSP-J/2020/Round2/csp-j2 2020.pdf", 5),
    Round2Source("csp_j_round2", "CSP-J", 2021, "CSP/题库/CSP-J/2021/Round2/2021 CSP-J2试题.pdf", 5),
    Round2Source("csp_j_round2", "CSP-J", 2022, "CSP/题库/CSP-J/2022/Round2/2022 CSP-J2试题.pdf", 5),
    Round2Source("csp_j_round2", "CSP-J", 2023, "CSP/题库/CSP-J/2023/Round2/CSP-J2-2023.pdf", 5),
    Round2Source("csp_j_round2", "CSP-J", 2024, "CSP/题库/CSP-J/2024/Round2/CSP-J2-2024.pdf", 5),
    Round2Source("csp_j_round2", "CSP-J", 2025, "CSP/题库/CSP-J/2025/Round2/CSP-J2-2025.pdf", 5),
    Round2Source("csp_s_round2", "CSP-S", 2019, "CSP/题库/CSP-S/2019/Round2/2019-CCF-CSP-S2-day1.pdf", 6),
    Round2Source("csp_s_round2", "CSP-S", 2019, "CSP/题库/CSP-S/2019/Round2/2019-CCF-CSP-S2-day2.pdf", 6),
    Round2Source("csp_s_round2", "CSP-S", 2020, "CSP/题库/CSP-S/2020/Round2/csp-s2 2020.pdf", 6),
    Round2Source("csp_s_round2", "CSP-S", 2021, "CSP/题库/CSP-S/2021/Round2/2021CSP-S2试题.pdf", 6),
    Round2Source("csp_s_round2", "CSP-S", 2022, "CSP/题库/CSP-S/2022/Round2/2022 CSP-S2.pdf", 6),
    Round2Source("csp_s_round2", "CSP-S", 2023, "CSP/题库/CSP-S/2023/Round2/2023-CCF-CSP-S2.pdf", 6),
    Round2Source("csp_s_round2", "CSP-S", 2024, "CSP/题库/CSP-S/2024/Round2/CSP-S2-2024.pdf", 6),
    Round2Source("csp_s_round2", "CSP-S", 2025, "CSP/题库/CSP-S/2025/Round2/CSP-S2-2025.pdf", 6),
]


HKOI_LEVELS = {
    "入门级-CSP-J1": ("csp_j_round1", "HKOI CSP-J", 4),
    "提高级-CSP-S1": ("csp_s_round1", "HKOI CSP-S", 5),
    "入门级-CSP-J2": ("csp_j_round2", "HKOI CSP-J", 5),
    "提高级-CSP-S2": ("csp_s_round2", "HKOI CSP-S", 6),
}


def discover_hkoi_sources() -> tuple[list[Round1Source], list[Round2Source]]:
    manifest = ROOT / HKOI_ROOT / "manifest.tsv"
    if not manifest.exists():
        return [], []

    grouped: dict[tuple[str, int, str], dict[str, str]] = {}
    with manifest.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            level = row.get("level", "")
            if level not in HKOI_LEVELS:
                continue
            try:
                year = int(row.get("year", ""))
            except ValueError:
                continue
            key = (row.get("section", ""), year, level)
            label = row.get("label", "")
            if label in {"題目", "C++", "參考答案", "試題"}:
                grouped.setdefault(key, {})[label] = row.get("path", "")

    round1_sources: list[Round1Source] = []
    round2_sources: list[Round2Source] = []
    for (section, year, level), files in sorted(grouped.items(), key=lambda item: item[0]):
        competition, level_label, difficulty = HKOI_LEVELS[level]
        if section == "第一輪":
            question_path = files.get("題目") or files.get("C++")
            answer_path = files.get("參考答案")
            if question_path and answer_path:
                round1_sources.append(
                    Round1Source(
                        competition,
                        level_label,
                        year,
                        f"{HKOI_ROOT}/{question_path}",
                        f"{HKOI_ROOT}/{answer_path}",
                        difficulty,
                    )
                )
        elif section == "第二輪" and files.get("試題"):
            round2_sources.append(
                Round2Source(
                    competition,
                    level_label,
                    year,
                    f"{HKOI_ROOT}/{files['試題']}",
                    difficulty,
                )
            )
    return round1_sources, round2_sources


def discover_csp_x_sources() -> tuple[list[Round1Source], list[Round2Source]]:
    base = ROOT / CSP_X_ROOT
    if not base.exists():
        return [], []

    round1_sources: list[Round1Source] = []
    round2_sources: list[Round2Source] = []
    for year_dir in sorted([path for path in base.iterdir() if path.is_dir() and path.name.isdigit()]):
        year = int(year_dir.name)
        round1_dir = year_dir / "Round1"
        if round1_dir.exists():
            pdfs = sorted(round1_dir.glob("*.pdf"))
            question_candidates = [
                path for path in pdfs
                if "试题" in path.name and not re.search(r"答案\.pdf$", path.name)
            ]
            answer_candidates = [path for path in pdfs if "答案" in path.name]
            question = question_candidates[0] if question_candidates else (pdfs[0] if pdfs else None)
            answer = answer_candidates[0] if answer_candidates else question
            if question:
                round1_sources.append(
                    Round1Source(
                        "csp_x_round1",
                        "CSP-X 山东小学组",
                        year,
                        str(question.relative_to(ROOT)),
                        str(answer.relative_to(ROOT)) if answer else None,
                        4,
                    )
                )

        round2_dir = year_dir / "Round2"
        if round2_dir.exists():
            for question in sorted(round2_dir.glob("*.pdf")):
                round2_sources.append(
                    Round2Source(
                        "csp_x_round2",
                        "CSP-X 山东小学组",
                        year,
                        str(question.relative_to(ROOT)),
                        5,
                    )
                )
    return round1_sources, round2_sources


def all_round1_sources() -> list[Round1Source]:
    hkoi_round1, _ = discover_hkoi_sources()
    csp_x_round1, _ = discover_csp_x_sources()
    return list(ROUND1_SOURCES) + hkoi_round1 + csp_x_round1


def all_round2_sources() -> list[Round2Source]:
    _, hkoi_round2 = discover_hkoi_sources()
    _, csp_x_round2 = discover_csp_x_sources()
    return list(ROUND2_SOURCES) + hkoi_round2 + csp_x_round2


def read_source(path: str, allow_ocr: bool = True) -> str:
    source = ROOT / path
    if not source.exists():
        return ""
    if source.suffix.lower() == ".md":
        return source.read_text(encoding="utf-8", errors="ignore")
    result = subprocess.run(
        [str(PDFTOTEXT), "-layout", str(source), "-"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    text = result.stdout
    if is_answer_source(path) and answer_text_is_useful(text):
        return text
    if pdf_text_is_useful(text) or not allow_ocr:
        return text
    return ocr_pdf(source, psm=11 if is_answer_source(path) else 6)


def is_answer_source(path: str) -> bool:
    return any(marker in path for marker in ("答案", "参考答案", "solution", "sol"))


def pdf_text_is_useful(text: str) -> bool:
    cleaned = compact_text(text).strip()
    chinese_count = sum("\u4e00" <= ch <= "\u9fff" for ch in cleaned)
    option_count = len(re.findall(r"(?m)^\s*[A-D]\s*[.、]", cleaned))
    return chinese_count >= 80 or option_count >= 20


def answer_text_is_useful(text: str) -> bool:
    cleaned = compact_text(text)
    numbered = re.findall(r"(?<!\d)(\d{1,2})\s*[.)]?\s*([A-D√×])(?=\s|$)", cleaned)
    tokens = re.findall(r"[A-D√×]", cleaned)
    return len(numbered) >= 15 or len(tokens) >= 30


def pdf_page_count(source: Path) -> int:
    result = subprocess.run(
        [str(PDFINFO), str(source)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, flags=re.M)
    return int(match.group(1)) if match else 0


def ocr_pdf(source: Path, psm: int) -> str:
    OCR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    stat = source.stat()
    cache_key = hashlib.sha1(f"{source}:{stat.st_mtime_ns}:{stat.st_size}:psm{psm}".encode()).hexdigest()
    cache_path = OCR_CACHE_DIR / f"{cache_key}.txt"
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8", errors="ignore")

    page_count = pdf_page_count(source)
    timeout = max(120, page_count * 30)
    with tempfile.TemporaryDirectory(prefix="csp-ocr-", dir=tempfile.gettempdir()) as tmp:
        prefix = Path(tmp) / "page"
        subprocess.run(
            [str(PDFTOPPM), "-r", "220", "-png", str(source), str(prefix)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        pages = []
        for image in sorted(Path(tmp).glob("page-*.png")):
            result = subprocess.run(
                [str(TESSERACT), str(image), "stdout", "-l", "chi_sim+eng", "--psm", str(psm)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=90,
            )
            pages.append(result.stdout)
    text = "\n\f\n".join(pages)
    cache_path.write_text(text, encoding="utf-8")
    return text


def remove_page_artifacts(value: str) -> str:
    value = re.sub(
        r"(?im)^\s*CCF\s+CSP[-－][JS].*$\n?",
        "",
        value,
    )
    value = re.sub(
        r"(?m)^\s*第\s*\d+\s*页\s*[，,]?\s*(?:共\s*)?\d+\s*页\s*$\n?",
        "",
        value,
    )
    return value


def compact_text(value: str) -> str:
    value = value.replace("\u3000", " ").replace("\uf06c", "")
    value = value.replace("（", "(").replace("）", ")")
    value = value.replace("．", ".").replace("：", ":")
    value = remove_page_artifacts(value)
    value = re.sub(r"(?m)^\s*香\s*港\s*$", "", value)
    value = re.sub(r"[ \t]+\n", "\n", value)
    return value


def split_section(text: str, start: str, end: str | None = None) -> str:
    start_index = text.find(start)
    if start_index < 0:
        return ""
    end_index = text.find(end, start_index + len(start)) if end else -1
    return text[start_index:end_index if end_index >= 0 else len(text)]


def answer_tokens_from_line(line: str) -> list[str]:
    if any(word in line for word in ("判断题", "单选题", "选择题", "完善程序", "阅读程序", "序号", "答案", "C++", "Pascal")):
        return []
    if re.search(r"[\u4e00-\u9fff]", line):
        return []
    return re.findall(r"[A-D√×]", line)


def parse_answer_sequence(text: str) -> dict[int, str]:
    text = compact_text(text)
    answer_start = -1
    for marker in ("参考答案", "认证答案"):
        pos = text.find(marker)
        if pos >= 0 and (answer_start < 0 or pos < answer_start):
            answer_start = pos
    if answer_start >= 0:
        text = text[answer_start:]
    numbered = {
        int(num): ans
        for num, ans in re.findall(r"(?<!\d)(\d{1,2})\s*[.)]?\s*([A-D√×])(?=\s|$)", text)
        if 1 <= int(num) <= 80
    }
    if len(numbered) >= 30:
        return numbered

    sections = [
        (1, split_section(text, "一、", "二、")),
        (16, split_section(text, "二、", "三、")),
        (34, split_section(text, "三、")),
    ]
    answers: dict[int, str] = {}
    for start, section in sections:
        tokens: list[str] = []
        for line in section.splitlines():
            tokens.extend(answer_tokens_from_line(line))
        for offset, token in enumerate(tokens):
            answers[start + offset] = token
    if len(answers) >= 30:
        return answers

    compact_tokens: list[str] = []
    in_answers = False
    for line in text.splitlines():
        if "参考答案" in line or "认证答案" in line:
            in_answers = True
            continue
        if not in_answers and re.search(r"^[A-D√×\s]+$", line.strip()):
            in_answers = True
        if in_answers:
            stripped = line.strip()
            if re.fullmatch(r"[A-D√×\s]+", stripped):
                compact_tokens.extend(re.findall(r"[A-D√×]", stripped))
    return {i + 1: token for i, token in enumerate(compact_tokens)}


def parse_markdown_answers(text: str) -> dict[int, str]:
    answer_part = split_section(text, "## 参考答案")
    if not answer_part:
        return {}
    answers: dict[int, str] = {}
    current = 1
    for line in answer_part.splitlines():
        match = re.match(r"\s*(?:\(\d+\)|\d+\.)\s*([A-D√×])\s*$", line)
        if match:
            answers[current] = match.group(1)
            current += 1
    return answers


def option_index(answer: str) -> int:
    if answer == "√":
        return 0
    if answer == "×":
        return 1
    return ord(answer) - ord("A")


def clean_block(value: str) -> str:
    value = re.sub(r"\n?\s*[\f]+", "\n", value)
    value = remove_page_artifacts(value)
    value = re.sub(r"(?m)^\s*香\s*港\s*$", "", value)
    value = re.sub(r"^\s*\d{1,2}[.)]\s*", "", value.strip())
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


OPTION_RE = re.compile(r"(?m)^\s*([A-D])\s*[.、]\s*")


def parse_options(block: str) -> tuple[str, list[str]] | None:
    block = re.sub(r"(?<![A-Za-z0-9])([A-D])\s*[.、]\s*", r"\n\1. ", block)
    block = re.sub(r"(?m)^\s*([A-D])\s+(?=\S)", r"\n\1. ", block)
    matches = list(OPTION_RE.finditer(block))
    if len(matches) < 2:
        return None
    stem = clean_block(block[: matches[0].start()])
    options = []
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(block)
        option = clean_block(block[match.end() : end])
        if option:
            options.append(option)
    if len(options) < 2:
        return None
    return stem, options


def question_type_for(number: int, answer: str, has_options: bool) -> str:
    if number <= 15:
        return "单项选择题"
    if answer in {"√", "×"} and not has_options:
        return "程序阅读判断题"
    if number >= 34:
        return "完善程序单选题"
    return "程序阅读单选题"


def code_context_before(text: str, position: int) -> str:
    starts = [m.start() for m in re.finditer(r"(?m)^\s*[(]\d+[)]\s*$", text[:position])]
    section_three = text.rfind("三、", 0, position)
    if section_three >= 0:
        starts.append(section_three)
    if not starts:
        return ""
    start = max(starts)
    first_question = re.search(r"(?m)^\s*\d{1,2}[.]\s*", text[start:position])
    if not first_question:
        return ""
    context = text[start : start + first_question.start()]
    context = re.sub(r"^[\s\S]*?(\d{2}\s+|#include|using namespace|int main|bool |void |long long |const )", r"\1", context, count=1)
    return clean_block(context)


def parse_pdf_round1(source: Round1Source, text: str, answers: dict[int, str]) -> list[dict]:
    text = compact_text(text)
    matches = list(re.finditer(r"(?m)^\s*(\d{1,2})[.]\s*", text))
    items = []
    for idx, match in enumerate(matches):
        number = int(match.group(1))
        if number not in answers:
            continue
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[match.start() : end]
        parsed = parse_options(block)
        answer = answers[number]
        if parsed:
            stem, options = parsed
        elif answer in {"√", "×"}:
            stem = clean_block(block)
            options = ["正确", "错误"]
        else:
            continue
        if option_index(answer) >= len(options):
            continue
        qtype = question_type_for(number, answer, bool(parsed))
        item = {
            "id": f"{source.competition}-{source.year}-q{number:02d}",
            "competition": source.competition,
            "category": qtype,
            "source_question_type": qtype,
            "display_type": qtype,
            "difficulty": source.difficulty,
            "source": source.question_path,
            "stem": stem,
            "code": code_context_before(text, match.start()) if number > 15 else "",
            "options": options,
            "answer": option_index(answer),
        }
        items.append(item)
    return items


def parse_markdown_round1(source: Round1Source, text: str) -> list[dict]:
    answers = parse_markdown_answers(text)
    body = text.split("## 参考答案", 1)[0]
    items = []

    single = split_section(body, "## 一、单项选择", "## 二、")
    for match in re.finditer(r"(?ms)^###\s+(\d+)\.\s+(.*?)(?=^###\s+\d+\.|^##\s|\Z)", single):
        number = int(match.group(1))
        parsed = parse_options(match.group(2).replace("- ", ""))
        if not parsed or number not in answers:
            continue
        stem, options = parsed
        items.append({
            "id": f"{source.competition}-{source.year}-q{number:02d}",
            "competition": source.competition,
            "category": "单项选择题",
            "source_question_type": "单项选择题",
            "display_type": "单项选择题",
            "difficulty": source.difficulty,
            "source": source.question_path,
            "stem": stem,
            "code": "",
            "options": options,
            "answer": option_index(answers[number]),
        })

    current_number = 16
    for section_title, qtype_base in (("## 二、程序阅读", "程序阅读"), ("## 三、程序填空", "程序填空")):
        section = split_section(body, section_title, "## " if section_title.startswith("## 二") else None)
        if section_title.startswith("## 二"):
            next_start = body.find("## 三、", body.find(section_title))
            section = body[body.find(section_title): next_start if next_start >= 0 else len(body)]
        code_blocks = list(re.finditer(r"```(?:cpp)?\n(.*?)```", section, flags=re.S))
        for sub in re.finditer(r"(?ms)^####\s+\((\d+)\)\.\s+(.*?)(?=^####\s+\(|^#{2,4}\s+|\Z)", section):
            code = ""
            previous_code = [block for block in code_blocks if block.start() < sub.start()]
            if previous_code:
                code = clean_block(previous_code[-1].group(1))
            text_block = sub.group(2).replace("- ", "")
            parsed = parse_options(text_block)
            answer = answers.get(current_number)
            if parsed and answer:
                stem, options = parsed
            elif answer in {"√", "×"}:
                stem = clean_block(text_block)
                options = ["正确", "错误"]
            else:
                current_number += 1
                continue
            qtype = f"{qtype_base}{'判断题' if answer in {'√', '×'} and not parsed else '单选题'}"
            items.append({
                "id": f"{source.competition}-{source.year}-q{current_number:02d}",
                "competition": source.competition,
                "category": qtype,
                "source_question_type": qtype,
                "display_type": qtype,
                "difficulty": source.difficulty,
                "source": source.question_path,
                "stem": stem,
                "code": code,
                "options": options,
                "answer": option_index(answer),
            })
            current_number += 1
    return items


def parse_round1() -> tuple[list[dict], list[str]]:
    questions: list[dict] = []
    report: list[str] = []
    for source in all_round1_sources():
        text = read_source(source.question_path)
        if source.question_path.endswith(".md"):
            items = parse_markdown_round1(source, text)
        else:
            answer_text = read_source(source.answer_path or source.question_path)
            answers = parse_answer_sequence(answer_text)
            items = parse_pdf_round1(source, text, answers)
        questions.extend(items)
        report.append(f"{source.level_label} {source.year} Round1: {len(items)}")
    return questions, report


def filter_unreadable_round1_questions(questions: list[dict]) -> tuple[list[dict], int]:
    """Drop OCR records that merged the next subquestion into the options.

    CSP first-round source questions are single-choice or true/false items, so
    more than four parsed options is evidence that the PDF parser crossed a
    question boundary. Keeping these records makes the exam page unreadable.
    """
    filtered = []
    skipped = 0
    for question in questions:
        if len(question.get("options", [])) > 4:
            skipped += 1
            continue
        filtered.append(question)
    return filtered, skipped


def clean_statement(value: str) -> str:
    value = remove_page_artifacts(value)
    value = re.sub(r"^\s*\d+\s{2,}", "", value, flags=re.M)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def section_between(text: str, start: str, *ends: str) -> str:
    start_index = text.find(start)
    if start_index < 0:
        return ""
    start_index += len(start)
    end_positions = [text.find(end, start_index) for end in ends if text.find(end, start_index) >= 0]
    end_index = min(end_positions) if end_positions else len(text)
    return clean_statement(text[start_index:end_index])


def clean_sample(value: str) -> str:
    lines = []
    for line in value.splitlines():
        line = re.sub(r"^\s*\d+\s{2,}", "", line.rstrip())
        if line.strip():
            lines.append(line)
    return "\n".join(lines).strip() + ("\n" if lines else "")


def parse_samples(section: str) -> list[dict[str, str]]:
    tests = []
    pattern = re.compile(
        r"【样例\s*\d*\s*输入】(?P<input>.*?)(?=【样例\s*\d*\s*输出】)"
        r"【样例\s*\d*\s*输出】(?P<output>.*?)(?=【样例|\n\s*【数据范围】|\n\s*【提示】|\Z)",
        re.S,
    )
    for match in pattern.finditer(section):
        test_input = clean_sample(match.group("input"))
        test_output = clean_sample(match.group("output"))
        if test_input or test_output:
            tests.append({"input": test_input, "output": test_output})
    return tests


def parse_round2_source(source: Round2Source, text: str) -> list[dict]:
    text = compact_text(text)
    starts = list(re.finditer(r"(?m)^\s*([^【】\n]{1,24})[（(]([a-z][a-z0-9_-]*)[）)]\s*$\n\s*【题目描述】", text))
    tasks = []
    used_ids: set[str] = set()
    for idx, match in enumerate(starts):
        title = clean_statement(match.group(1))
        slug = match.group(2)
        end = starts[idx + 1].start() if idx + 1 < len(starts) else len(text)
        section = text[match.start() : end]
        description = section_between(section, "【题目描述】", "【输入格式】")
        input_format = section_between(section, "【输入格式】", "【输出格式】")
        output_format = section_between(section, "【输出格式】", "【样例", "【数据范围】")
        constraints = section_between(section, "【数据范围】", "【提示】")
        tests = parse_samples(section)
        task_id = f"{source.competition}-{source.year}-{slug}"
        if task_id in used_ids:
            task_id = f"{task_id}-{idx + 1}"
        used_ids.add(task_id)
        if not description:
            continue
        tasks.append({
            "id": task_id,
            "competition": source.competition,
            "category": "传统型",
            "problem_type": "传统型",
            "difficulty": source.difficulty,
            "source": source.question_path,
            "title": f"{source.level_label} {source.year} {title}",
            "description": description,
            "input": input_format or "见原题面。",
            "output": output_format or "见原题面。",
            "constraints": constraints or "见原题面。",
            "tests": tests,
            "public_tests": tests[:1],
            "hidden_tests": tests,
            "allow_static_tests": True,
        })
    if tasks:
        return tasks

    title = f"{source.level_label} {source.year} 第二轮原始题面"
    return [{
        "id": f"{source.competition}-{source.year}-{Path(source.question_path).stem.lower().replace(' ', '-')}",
        "competition": source.competition,
        "category": "原始题面",
        "problem_type": "原始题面",
        "difficulty": source.difficulty,
        "source": source.question_path,
        "title": title,
        "description": "该原始资料为扫描版或暂未能自动拆分题面，请打开 source 字段对应文件查看完整题目。",
        "input": "见原始题面。",
        "output": "见原始题面。",
        "constraints": "见原始题面。",
        "tests": [],
        "public_tests": [],
        "hidden_tests": [],
        "allow_static_tests": True,
    }]


def parse_round2() -> tuple[list[dict], list[str]]:
    tasks: list[dict] = []
    report: list[str] = []
    for source in all_round2_sources():
        text = read_source(source.question_path, allow_ocr=False)
        items = parse_round2_source(source, text)
        tasks.extend(items)
        report.append(f"{source.level_label} {source.year} Round2 {source.question_path}: {len(items)}")
    return tasks, report


def normalize_signature_value(value: object) -> str:
    if isinstance(value, list):
        return "|".join(normalize_signature_value(item) for item in value)
    if isinstance(value, dict):
        return "|".join(f"{key}:{normalize_signature_value(value[key])}" for key in sorted(value))
    text = compact_text(str(value))
    text = re.sub(r"\s+", "", text)
    text = text.replace("：", ":").replace("；", ";")
    return text.lower()


def item_signature(item: dict, item_type: str) -> str:
    if item_type == "choice":
        payload = {
            "kind": item_type,
            "stem": item.get("stem", ""),
            "code": item.get("code", ""),
            "options": item.get("options", []),
            "answer": item.get("answer", ""),
        }
    elif item.get("problem_type") == "原始题面":
        payload = {
            "kind": item_type,
            "problem_type": item.get("problem_type", ""),
            "source": Path(str(item.get("source", ""))).name,
        }
    else:
        payload = {
            "kind": item_type,
            "description": item.get("description", ""),
            "input": item.get("input", ""),
            "output": item.get("output", ""),
            "constraints": item.get("constraints", ""),
        }
    normalized = normalize_signature_value(payload)
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()


def unique_item_id(item: dict, seen_ids: set[str]) -> str:
    item_id = str(item.get("id", "")).strip() or "imported-csp-question"
    if item_id not in seen_ids:
        return item_id
    source = str(item.get("source", item_id))
    suffix = hashlib.sha1(source.encode("utf-8")).hexdigest()[:8]
    candidate = f"{item_id}-{suffix}"
    counter = 2
    while candidate in seen_ids:
        candidate = f"{item_id}-{suffix}-{counter}"
        counter += 1
    return candidate


def dedupe_items(items: list[dict], item_type: str) -> tuple[list[dict], int, int]:
    deduped: list[dict] = []
    signatures: set[str] = set()
    ids: set[str] = set()
    skipped = 0
    renamed = 0
    for item in items:
        signature = item_signature(item, item_type)
        if signature in signatures:
            skipped += 1
            continue
        if item.get("id") in ids:
            skipped += 1
            continue
        item_id = unique_item_id(item, ids)
        if item_id != item.get("id"):
            item = dict(item)
            item["id"] = item_id
            renamed += 1
        signatures.add(signature)
        ids.add(item_id)
        deduped.append(item)
    return deduped, skipped, renamed


def write_module(questions: list[dict], tasks: list[dict], report: list[str]) -> None:
    content = [
        '"""Auto-generated CSP-J/S/CSP-X questions from local CSP/题库 source papers."""',
        "",
        "# Regenerate with: python3 scripts/generate_csp_imports.py",
        "",
        "CSP_ROUND1_CHOICE_QUESTIONS = " + pprint.pformat(questions, width=120, sort_dicts=False),
        "",
        "",
        "CSP_ROUND2_PROGRAMMING_TASKS = " + pprint.pformat(tasks, width=120, sort_dicts=False),
        "",
        "",
        "CSP_IMPORT_REPORT = " + pprint.pformat(report, width=120, sort_dicts=False),
        "",
    ]
    formatted = "\n".join(content)
    ast.parse(formatted)
    OUTPUT.write_text(formatted, encoding="utf-8")


def main() -> None:
    questions, round1_report = parse_round1()
    tasks, round2_report = parse_round2()
    questions, unreadable_questions = filter_unreadable_round1_questions(questions)
    questions, skipped_questions, renamed_questions = dedupe_items(questions, "choice")
    tasks, skipped_tasks, renamed_tasks = dedupe_items(tasks, "programming")
    report = round1_report + round2_report + [
        f"dedupe round1 skipped duplicates: {skipped_questions}, renamed id collisions: {renamed_questions}",
        f"filtered unreadable round1 OCR records: {unreadable_questions}",
        f"dedupe round2 skipped duplicates: {skipped_tasks}, renamed id collisions: {renamed_tasks}",
    ]
    write_module(questions, tasks, report)
    print(f"wrote {OUTPUT}")
    print(f"round1 questions: {len(questions)}")
    print(f"round2 tasks: {len(tasks)}")
    print(f"filtered unreadable round1 OCR records: {unreadable_questions}")
    print(f"round1 duplicates skipped: {skipped_questions}; id collisions renamed: {renamed_questions}")
    print(f"round2 duplicates skipped: {skipped_tasks}; id collisions renamed: {renamed_tasks}")
    for line in report:
        print(line)


if __name__ == "__main__":
    main()
