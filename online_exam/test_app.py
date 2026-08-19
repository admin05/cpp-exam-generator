import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from online_exam import app
from scripts.generate_csp_imports import parse_options


class ResultPageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = app.DB_PATH
        app.DB_PATH = Path(self.temp_dir.name) / "exam.db"
        app.init_db()

    def tearDown(self) -> None:
        app.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_now_text_uses_beijing_time(self) -> None:
        fixed_beijing_time = datetime(2026, 8, 4, 15, 30, 45, tzinfo=app.BEIJING_TZ)
        with patch.object(app, "datetime") as datetime_mock:
            datetime_mock.now.return_value = fixed_beijing_time

            self.assertEqual(app.now_text(), "2026-08-04 15:30:45")
            datetime_mock.now.assert_called_once_with(app.BEIJING_TZ)

    def test_result_page_distinguishes_correct_and_wrong_answers(self) -> None:
        exam_payload = {
            "question_bank": "csp_j_round1",
            "choice_questions": [
                {"id": "c-arith-001"},
                {
                    "id": "c-array-001",
                    "stem": "下面程序片段的输出结果是？",
                    "code": "int a[5] = {2, 4, 6, 8, 10};\ncout << a[1] + a[3];",
                    "options": ["6", "10", "12", "14"],
                    "answer": 2,
                },
            ],
            "programming_tasks": [],
        }
        detail = {
            "choices": [
                {"index": 1, "selected": "A", "answer": "A", "ok": True, "type": "单选题"},
                {"index": 2, "selected": "B", "answer": "C", "ok": False, "type": "单选题"},
            ],
            "programs": [],
        }
        with app.db() as conn:
            exam_cursor = conn.execute(
                "INSERT INTO exams(title, duration_minutes, payload, created_at) VALUES (?, ?, ?, ?)",
                ("CSP-J 第一轮测试", 60, json.dumps(exam_payload, ensure_ascii=False), app.now_text()),
            )
            exam_id = int(exam_cursor.lastrowid)
            cursor = conn.execute(
                """
                INSERT INTO submissions(
                    exam_id, student_name, choice_score, choice_total,
                    program_score, program_total, detail, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (exam_id, "测试考生", 1, 2, 0, 0, json.dumps(detail, ensure_ascii=False), app.now_text()),
            )
            submission_id = int(cursor.lastrowid)

        page = app.result_page(submission_id).decode("utf-8")

        self.assertIn('class="answer-selected correct">A</td>', page)
        self.assertIn('class="answer-selected wrong">B</td>', page)
        self.assertIn('class="answer-correct">C</td>', page)
        self.assertIn('class="answer-status correct">正确</span>', page)
        self.assertIn('class="answer-status wrong">错误</span>', page)
        self.assertEqual(page.count("查看答案解析"), 1)
        self.assertIn("<h3>题目</h3>", page)
        self.assertIn("下面程序片段的输出结果是？", page)
        self.assertIn("cout &lt;&lt; a[1] + a[3];", page)
        self.assertIn("<b>A.</b> 6", page)
        self.assertIn("<b>B.</b> 10", page)
        self.assertIn("<b>C.</b> 12", page)
        self.assertIn("<b>D.</b> 14", page)
        self.assertIn("<b>正确答案：</b>C", page)
        self.assertIn("a[1]=4、a[3]=8", page)
        self.assertIn("提交时间（北京时间）", page)

    def test_all_csp_j_round1_choices_have_explanations(self) -> None:
        questions = app.filter_bank_items(app.CHOICE_QUESTIONS, "csp_j_round1", "choice")
        question_ids = {question["id"] for question in questions}
        missing = [question["id"] for question in questions if not app.csp_j_choice_explanation(question)]

        self.assertTrue(set(app.CSP_J_ROUND1_EXPLANATIONS).issubset(question_ids))
        self.assertEqual(missing, [])

        prepared = [
            app.prepare_choice_question(question, "csp_j_round1")
            for question in questions
        ]
        self.assertTrue(all(question.get("explanation") for question in prepared))

    def test_existing_csp_j_round1_papers_are_backfilled_with_explanations(self) -> None:
        payload = {
            "question_bank": "csp_j_round1",
            "choice_questions": [
                {
                    "id": "csp_j_round1-2022-q01",
                    "source_question_type": "单项选择题",
                    "stem": "以下哪种功能没有涉及 C++语言的面向对象特性支持？",
                    "options": ["调用 printf", "调用成员函数", "构造 class", "构造派生类"],
                    "answer": 0,
                }
            ],
            "programming_tasks": [],
        }
        with app.db() as conn:
            cursor = conn.execute(
                "INSERT INTO exams(title, duration_minutes, payload, created_at) VALUES (?, ?, ?, ?)",
                ("旧 CSP-J 试卷", 60, json.dumps(payload, ensure_ascii=False), app.now_text()),
            )
            exam_id = int(cursor.lastrowid)
            cursor = conn.execute(
                """
                INSERT INTO submissions(
                    exam_id, student_name, choice_score, choice_total,
                    program_score, program_total, detail, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    exam_id,
                    "旧卷考生",
                    0,
                    2,
                    0,
                    0,
                    json.dumps(
                        {
                            "choices": [
                                {
                                    "index": 1,
                                    "selected": "B",
                                    "answer": "A",
                                    "ok": False,
                                    "type": "单项选择题",
                                }
                            ],
                            "programs": [],
                        },
                        ensure_ascii=False,
                    ),
                    app.now_text(),
                ),
            )
            submission_id = int(cursor.lastrowid)

        app.init_db()
        saved = json.loads(app.load_exam(exam_id)["payload"])
        page = app.result_page(submission_id).decode("utf-8")

        self.assertIn("explanation", saved["choice_questions"][0])
        self.assertIn("A（调用 printf）", saved["choice_questions"][0]["explanation"])
        self.assertIn("查看答案解析", page)
        self.assertIn("调用 printf", page)
        self.assertEqual(app.backfill_csp_j_round1_explanations(), 0)

    def test_existing_papers_sync_corrected_question_snapshots(self) -> None:
        payload = {
            "question_bank": "csp_j_round1",
            "choice_questions": [
                {
                    "id": "csp_j_round1-2022-q13",
                    "stem": "八进制数 32.1 对应的十进制数是(           )。",
                    "options": ["125", "250", "125", "250"],
                    "answer": 2,
                    "explanation": "根据题目给出的定义与条件逐项核对，只有 C（125）符合题意。",
                }
            ],
            "programming_tasks": [],
        }
        with app.db() as conn:
            cursor = conn.execute(
                "INSERT INTO exams(title, duration_minutes, payload, created_at) VALUES (?, ?, ?, ?)",
                ("含错误八进制题目的旧试卷", 60, json.dumps(payload, ensure_ascii=False), app.now_text()),
            )
            exam_id = int(cursor.lastrowid)

        app.init_db()
        saved = json.loads(app.load_exam(exam_id)["payload"])
        question = saved["choice_questions"][0]

        self.assertEqual(question["options"], ["24.125", "24.250", "26.125", "26.250"])
        self.assertEqual(question["answer"], 2)
        self.assertIn("26.125", question["explanation"])
        self.assertEqual(app.backfill_csp_j_round1_explanations(), 0)

    def test_csp_import_preserves_decimal_option_prefixes(self) -> None:
        parsed = parse_options(
            """13. 八进制数 32.1 对应的十进制数是（ ）。
              A. 24.125
              B. 24.250
              C. 26.125
              D. 26.250"""
        )

        self.assertIsNotNone(parsed)
        stem, options = parsed
        self.assertEqual(stem, "八进制数 32.1 对应的十进制数是（ ）。")
        self.assertEqual(options, ["24.125", "24.250", "26.125", "26.250"])

    def test_new_csp_j_round1_papers_store_explanations(self) -> None:
        exam = app.build_exam("CSP-J 解析测试", 10, 4, 120, "csp_j_round1")

        self.assertTrue(all(question.get("explanation") for question in exam["choice_questions"]))

    def test_new_papers_do_not_repeat_an_existing_question_set(self) -> None:
        first = app.build_exam("去重测试 1", 10, 4, 120, "literacy")
        first_id = app.save_exam(first)

        second = app.build_exam("去重测试 2", 10, 4, 120, "literacy")

        self.assertNotEqual(app.exam_signature(first), app.exam_signature(second))
        with self.assertRaises(app.DuplicateExamError):
            app.save_exam(first)
        self.assertIsNotNone(app.load_exam(first_id))

    def test_csp_j_round1_does_not_repeat_an_existing_template(self) -> None:
        first = app.build_exam("CSP-J 去重测试 1", 10, 4, 120, "csp_j_round1")
        app.save_exam(first)

        second = app.build_exam("CSP-J 去重测试 2", 10, 4, 120, "csp_j_round1")

        self.assertNotEqual(app.exam_signature(first), app.exam_signature(second))
        self.assertEqual(len(second["choice_questions"]), 43)

    def test_csp_j_s_import_profiles_have_source_questions(self) -> None:
        self.assertGreaterEqual(len(app.filter_bank_items(app.CHOICE_QUESTIONS, "csp_j_round1", "choice")), 250)
        self.assertGreaterEqual(len(app.filter_bank_items(app.PROGRAMMING_TASKS, "csp_j_round2", "programming")), 35)
        self.assertGreaterEqual(len(app.filter_bank_items(app.CHOICE_QUESTIONS, "csp_s_round1", "choice")), 120)
        self.assertGreaterEqual(len(app.filter_bank_items(app.PROGRAMMING_TASKS, "csp_s_round2", "programming")), 15)
        self.assertGreaterEqual(len(app.filter_bank_items(app.CHOICE_QUESTIONS, "csp_x_round1", "choice")), 40)
        self.assertGreaterEqual(len(app.filter_bank_items(app.PROGRAMMING_TASKS, "csp_x_round2", "programming")), 15)

    def test_csp_j_round1_builds_fixed_100_point_paper(self) -> None:
        exam = app.build_exam("CSP-J 固定结构", 10, 4, 120, "csp_j_round1")
        questions = exam["choice_questions"]

        self.assertEqual(len(questions), 43)
        self.assertEqual(exam["total_score"], 100.0)
        self.assertEqual(
            [len(section["question_indices"]) for section in exam["sections"]],
            [15, 18, 10],
        )
        self.assertEqual(
            [len(section.get("programs", [])) for section in exam["sections"]],
            [0, 3, 2],
        )
        self.assertEqual(
            {question["source_question_type"] for question in questions[:15]},
            {"单项选择题"},
        )
        self.assertEqual(
            sum(question["source_question_type"] == "程序阅读判断题" for question in questions),
            12,
        )
        self.assertEqual(
            sum(question["source_question_type"] == "程序阅读单选题" for question in questions),
            6,
        )
        self.assertEqual(
            sum(question["source_question_type"] == "完善程序单选题" for question in questions),
            10,
        )

    def test_csp_j_round1_all_correct_scores_100(self) -> None:
        exam = app.build_exam("CSP-J 全对测试", 10, 4, 120, "csp_j_round1")
        exam_id = app.save_exam(exam)
        params = {"student_name": ["满分考生"]}
        for index, question in enumerate(exam["choice_questions"], 1):
            params[f"choice_{index}"] = [
                str(answer_index)
                for answer_index in app.answer_indices(question["answer"])
            ]

        response = app.handle_submit(exam_id, params)
        submission_id = int(response.decode().rsplit("/", 1)[1])
        with app.db() as conn:
            row = conn.execute("SELECT choice_score, choice_total FROM submissions WHERE id = ?", (submission_id,)).fetchone()

        self.assertEqual(float(row["choice_score"]), 100.0)
        self.assertEqual(float(row["choice_total"]), 100.0)

    def test_imported_csp_choice_options_are_not_merged(self) -> None:
        competitions = {"csp_j_round1", "csp_s_round1", "csp_x_round1"}
        imported = [
            question
            for question in app.CHOICE_QUESTIONS
            if question.get("competition") in competitions
        ]
        self.assertTrue(imported)
        self.assertTrue(all(len(question.get("options", [])) <= 4 for question in imported))

    def test_imported_csp_choice_options_have_no_following_program_text(self) -> None:
        competitions = {"csp_j_round1", "csp_s_round1", "csp_x_round1"}
        imported = [
            question
            for question in app.CHOICE_QUESTIONS
            if question.get("competition") in competitions
        ]
        polluted = [
            question["id"]
            for question in imported
            if any(
                marker in str(option)
                for option in question.get("options", [])
                for marker in ("#include", "\n(2)", "\n(3)", "三、完善程序")
            )
        ]
        self.assertEqual(polluted, [])

    def test_imported_csp_questions_have_no_pdf_page_artifacts(self) -> None:
        competitions = {
            "csp_j_round1",
            "csp_s_round1",
            "csp_x_round1",
        }
        imported = [
            question
            for question in app.CHOICE_QUESTIONS
            if question.get("competition") in competitions
        ]
        page_artifacts = [
            question["id"]
            for question in imported
            if "CCF CSP" in "\n".join(
                [
                    str(question.get("stem", "")),
                    str(question.get("code", "")),
                    *[str(option) for option in question.get("options", [])],
                ]
            )
            or "语言试题" in "\n".join(
                [
                    str(question.get("stem", "")),
                    str(question.get("code", "")),
                    *[str(option) for option in question.get("options", [])],
                ]
            )
        ]
        self.assertEqual(page_artifacts, [])

    def test_result_answer_font_is_larger(self) -> None:
        css = (app.ROOT / "static" / "style.css").read_text(encoding="utf-8")

        self.assertRegex(
            css,
            r"\.answer-selected,\s*\.answer-correct\s*\{[^}]*font-size: 18px;",
        )
        self.assertRegex(css, r"\.answer-status\s*\{[^}]*font-size: 18px;")
        self.assertRegex(css, r"\.answer-explanation summary\s*\{[^}]*font-size: 16px;")
        self.assertRegex(css, r"\.answer-explanation-content\s*\{[^}]*font-size: 17px;")
        self.assertRegex(css, r"\.answer-explanation-content h3\s*\{[^}]*font-size: 18px;")

    def test_admin_score_page_labels_exam_time_as_beijing_time(self) -> None:
        payload = {"choice_questions": [], "programming_tasks": []}
        with app.db() as conn:
            cursor = conn.execute(
                "INSERT INTO exams(title, duration_minutes, payload, created_at) VALUES (?, ?, ?, ?)",
                ("时区测试", 60, json.dumps(payload), app.now_text()),
            )
            exam_id = int(cursor.lastrowid)

        page = app.admin_exam_detail(exam_id).decode("utf-8")

        self.assertIn("考试时间（北京时间）", page)


if __name__ == "__main__":
    unittest.main()
