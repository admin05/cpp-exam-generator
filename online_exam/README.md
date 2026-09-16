# C++ 竞赛训练平台应用

`online_exam/` 是本地在线考试应用代码和结构化题库目录。平台按题库 profile 组卷，
当前考试内置：

- `csp_j_round1`：CSP-J 第一轮，固定生成 43 道、100 分试卷。
- `csp_j_round2`：CSP-J 第二轮，从 OCR 题库抽取编程题。
- `csp_s_round1`：CSP-S 第一轮，按真实结构生成 42～43 道、100 分试卷。
- `csp_s_round2`：CSP-S 第二轮，从 OCR 题库抽取编程题。
题目实际由 `CSP/题库OCR` 中的重新生成 OCR Markdown 文件构建，使用仓库根目录执行
`python3 scripts/generate_ocr_imports.py` 更新 `imported_ocr_questions.py`。

## 添加题目

结构化题目放在 `question_bank.py` 或其导入模块中。建议字段：

```python
{
    "id": "csp-j-r1-example-001",
    "competition": "csp_j_round1",
    "category": "程序阅读",
    "difficulty": 3,
    ...
}
```

编程题使用 `competition: "csp_j_round2"`、`"csp_s_round2"`。如果是通用 C++ 基础题，
可以使用 `competition: "general"`，它会进入素养大赛、CSP-J、GESP 等基础训练池。

旧版 CSP-J/S/CSP-X 本地资料导入文件为 `imported_csp_questions.py`，由仓库根目录执行
`python3 scripts/generate_csp_imports.py` 生成。脚本会扫描 CSP-J/CSP-S、HKOI 镜像
manifest 和 CSP-X(山东) 目录，对第一轮题面和答案 PDF 自动尝试本机 Tesseract OCR，
并跳过重复题目签名或重复生成 ID；大型扫描版第二轮 PDF 暂保留为来源引用，待 OCR
规范化或人工拆题后再导入为完整编程题。

原始 PDF、DOCX、PPT、压缩包等资料目录由仓库根目录 `.gitignore` 忽略，不要直接把
大体积原始资料提交进 Git。先提取、校验、规范化为结构化题目，再提交应用数据。

## 本地运行

```bash
python3 -m online_exam.app
```

默认监听 `0.0.0.0:8000`，可用环境变量覆盖：

- `EXAM_DB`
- `JUDGE_DIR`
- `HOST`
- `PORT`
