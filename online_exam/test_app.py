import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from online_exam import app


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
                {"id": "c-array-001"},
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
        self.assertIn("a[1]=4、a[3]=8", page)
        self.assertIn("提交时间（北京时间）", page)

    def test_all_csp_j_round1_choices_have_explanations(self) -> None:
        questions = app.filter_bank_items(app.CHOICE_QUESTIONS, "csp_j_round1", "choice")
        missing = [question["id"] for question in questions if not app.csp_j_choice_explanation(question)]
        question_ids = {question["id"] for question in questions}

        self.assertEqual(question_ids, set(app.CSP_J_ROUND1_EXPLANATIONS))
        self.assertEqual(missing, [])

        exam = app.build_exam("解析覆盖测试", len(questions), 0, 60, "csp_j_round1")
        self.assertTrue(all(question.get("explanation") for question in exam["choice_questions"]))

    def test_result_answer_font_is_larger(self) -> None:
        css = (app.ROOT / "static" / "style.css").read_text(encoding="utf-8")

        self.assertRegex(
            css,
            r"\.answer-selected,\s*\.answer-correct\s*\{[^}]*font-size: 18px;",
        )

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
