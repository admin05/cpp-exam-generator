# C++ 竞赛训练平台应用

`online_exam/` 是本地在线考试应用代码和结构化题库目录。平台按题库 profile 组卷，
目前内置：

- `literacy`：素养大赛，范围以 `素养大赛/复赛 决赛考点大纲.pdf` 的 C++ 考点为准。
- `csp_j_round1`：CSP-J 第一轮，创建试卷时固定生成 15 道单选题、3 段阅读程序 18 道小题、2 段完善程序 10 道小题，共 43 题、100 分；题目来自 `CSP/题库/CSP-J` 中可结构化导入的完整真题模板。
- `csp_j_round2`：CSP-J 第二轮，来自 `CSP/题库/CSP-J` 中可结构化导入的第二轮资料，默认只抽编程题，并保留原始题目类型。
- `csp_s_round1`：CSP-S 第一轮，来自 `CSP/题库/CSP-S` 和 HKOI 镜像中的第一轮资料，按真实结构生成 15 道基础单选、3 个阅读程序、2 个完善程序，共 42～43 道小题、100 分；不再把所有客观题混合抽取。当前基础单选池包含 90 道可独立使用的题目，2019、2020 年不完整资料中的基础单选也会纳入；阅读和完善程序仍只使用能够恢复完整结构的程序块。
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

CSP-J/S/CSP-X 本地资料导入文件为 `imported_csp_questions.py`，由仓库根目录执行
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
