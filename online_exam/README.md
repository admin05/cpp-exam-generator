# C++ 竞赛训练平台应用

`online_exam/` 是本地在线考试应用代码和结构化题库目录。平台按题库 profile 组卷，
目前内置：

- `literacy`：素养大赛，范围以 `素养大赛/复赛 决赛考点大纲.pdf` 的 C++ 考点为准。
- `csp_j_round1`：CSP-J 第一轮，来自 `CSP/题库/CSP-J` 中可结构化导入的第一轮资料，默认只抽客观题，并保留原始细分题型。
- `csp_j_round2`：CSP-J 第二轮，来自 `CSP/题库/CSP-J` 中可结构化导入的第二轮资料，默认只抽编程题，并保留原始题目类型。
- `csp_s_round1`：CSP-S 第一轮，来自 `CSP/题库/CSP-S` 中可结构化导入的第一轮资料，默认只抽客观题。
- `csp_s_round2`：CSP-S 第二轮，来自 `CSP/题库/CSP-S` 中可结构化导入的第二轮资料，默认只抽编程题。
- `gesp`、`fuzhou`、`all`：保留已有导入题库和全量练习入口。

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

CSP-J/S 本地资料导入文件为 `imported_csp_questions.py`，由仓库根目录执行
`python3 scripts/generate_csp_imports.py` 生成。扫描 PDF 如果不能抽出中文文本，会先
保留为来源引用，待 OCR 或人工规范化后再导入为完整小题。

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
