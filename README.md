# C++ Contest Exam Generator

A lightweight local training and exam platform for C++ contests. It can build
random papers from multiple question-bank profiles, including the existing
Algorithm Application / literacy contest bank and separate CSP-J first-round and
second-round profiles.

The platform is designed for small-scale teaching and NAS deployment. Admins can
create randomized papers by question-bank scope, students can answer
single-choice and multiple-choice objective questions, submit C++17 programming
solutions, and the system records scores in SQLite.

## Features

- Admin paper creation with configurable question-bank scope, objective-question
  count, programming-task count, and exam duration.
- Built-in question-bank profiles: all questions, literacy contest, CSP-J first
  round, CSP-J second round, CSP-S first round, CSP-S second round, GESP, and
  Fuzhou robot contest.
- Objective-question bank covering C++ fundamentals, mathematical reasoning,
  simulation, enumeration, divide-and-conquer, greedy methods, recurrence,
  recursion, sorting, binary search, prefix sums, DFS/BFS, STL containers,
  stacks, queues, linked-list basics, high-precision arithmetic, bit operations,
  and base conversion.
- Single-choice and multiple-choice rendering, scoring, and result review.
- Balanced random selection across C++ topic categories.
- Online student exam page with timer and answer progress markers.
- C++17 compile-and-run judging for programming tasks against bundled tests.
- Submission result pages and admin score overview.
- Docker Compose deployment with persistent SQLite data.

## Question Bank Layout

- `online_exam/`: application code, static styles, and structured question bank.
- `scripts/`: local extraction/import helper scripts for source materials.
- `CSP/` and `素养大赛/`: local raw source-material folders. These are ignored
  by Git by default because they contain large PDFs, PPTs, DOCX files, archives,
  and other non-code assets.

The literacy contest profile follows the C++ section of
`素养大赛/复赛 决赛考点大纲.pdf`. CSP-J/S profiles include structured imports from
`CSP/题库/CSP-J` and `CSP/题库/CSP-S`: first-round papers are modeled as objective
questions while preserving source subtypes such as single-choice, program
reading judgment, program reading choice, and program completion. Selecting
CSP-J first round creates its fixed 15 + 18 + 10, 43-question, 100-point paper;
CSP-S first round also creates a fixed-format 100-point paper: 15 basic
single-choice questions, three program-reading blocks worth 40 points, and two
program-completion blocks with 10 blanks worth 30 points. Depending on the
source year, it contains 42 or 43 subquestions and preserves year-specific
reading-program and scoring differences;
second-round
papers are modeled as programming tasks while preserving the paper's problem
type, such as `传统型`.

To add a new competition source, normalize questions into the same dictionaries
used by `online_exam/question_bank.py`. Set `competition` to a short key such as
`"literacy"`, `"csp_j_round1"`, `"csp_j_round2"`, `"csp_s_round1"`,
`"csp_s_round2"`, `"csp_x_round1"`, or `"csp_x_round2"` so the admin page can
include the question in the matching profile. The CSP import module is generated with
`python3 scripts/generate_csp_imports.py`; the generator falls back to local
Tesseract OCR for first-round papers and answer sheets whose PDF text is not
extractable. It scans the local CSP-J/CSP-S folders, the HKOI mirror manifest,
and CSP-X(山东) folders, then skips duplicate question signatures or duplicate
generated IDs. Large scanned second-round PDFs are kept as source references
until they are OCR-normalized or manually split into full programming tasks.

### Datalab PDF OCR

`scripts/datalab_ocr.py` uses Datalab's official Convert API in `balanced` mode
with Markdown output and pagination. It only scans PDFs under `CSP/题库`; it
does not scan `CSP/学习资料`, `CSP/题库OCR`, or other directories.

Create the API key file at `CSP/题库OCR/OCR_KEY` with only the key and no other
configuration. Restrict it to the owner, for example:

```bash
chmod 600 CSP/题库OCR/OCR_KEY
```

Process one PDF first:

```bash
python3 scripts/datalab_ocr.py \
  --file "CSP/题库/CSP-J/2019/Round1/cspjs2019hj_cpp.pdf"
```

Process all PDFs in the question bank with the default retry and polling
settings:

```bash
python3 scripts/datalab_ocr.py
```

Use `--force` to process files whose successful `.md` and `.json` outputs
already exist. Results are written under `CSP/题库OCR` with the same relative
directory structure as `CSP/题库`. OCR output and temporary failure records are
ignored by Git. Embedded image resources returned by the API are also saved
beside the Markdown file so its relative image links remain usable. `OCR_KEY`
is never included in source code or logs.

Mark Text must have its math expression/KaTeX support enabled to render the
LaTeX formulas. The script writes display formulas with standalone `$$` lines
for compatibility with Mark Text.

The Convert API is asynchronous: the script submits a PDF, polls the returned
`request_check_url` until `status=complete`, and fetches `result_url` when one
is provided. API quota and charges depend on the current Datalab account and
service limits; each submitted PDF may consume quota, so avoid unnecessary
batch or forced runs. The public API does not guarantee a fixed Chandra version
or a stable `model=chandra` parameter, so this script does not send that
parameter and uses the official `balanced` Convert API mode.

## Project Structure

- `online_exam/`: application code, static styles, and bundled structured bank.
- `scripts/`: local extraction/import helper scripts for source materials.
- `Dockerfile`: container image for the platform and C++ judge runtime.
- `docker-compose.yml`: local build deployment.
- `docker-compose.github.yml`: build directly from the GitHub repository.
- `docker-compose.ghcr.yml`: run the prebuilt GHCR image.

## Docker Compose Deployment

Recommended local-build deployment:

```bash
git pull
docker compose up -d --build
```

Alternatively, build directly from GitHub:

```bash
docker compose -f docker-compose.github.yml up -d --build
```

If your NAS cannot access `github.com` reliably but can pull from GHCR, use the
prebuilt image compose file:

```bash
docker compose -f docker-compose.ghcr.yml up -d
```

Then open:

- Student entry: `http://NAS-IP:8088/`
- Admin panel: `http://NAS-IP:8088/admin`

The platform stores data in `data/exam.db` inside the named volume
`cpp_exam_data`, so NAS deployments do not need host-directory permission fixes.

## Runtime Notes

Programming submissions are compiled and executed inside the application
container using `g++`. The default Compose files run the app as a non-root user,
mount `/judge` as executable tmpfs, enable `no-new-privileges`, and set basic
process and memory limits.

This is suitable for local teaching and small trusted groups. It is not a strict
public online-judge sandbox. For untrusted public use, split judging into an
isolated sandbox service or use a dedicated OJ system.

---

# C++ 竞赛训练平台

这是一个轻量级本地在线考试平台，面向 C++ 竞赛训练，可按不同题库范围生成试卷。
当前已支持“全部题库”“素养大赛”“CSP-J 第一轮”“CSP-J 第二轮”“CSP-S 第一轮”
“CSP-S 第二轮”“GESP”“福州机器人赛”等题库范围。素养大赛题库范围以
`素养大赛/复赛 决赛考点大纲.pdf` 的 C++ 要求为准；CSP-J/S 题库来自
`CSP/题库/CSP-J` 与 `CSP/题库/CSP-S` 的本地原始资料，并拆分为第一轮客观题题库
和第二轮编程题题库。

CSP-S 第一轮会按真实试卷结构生成 15 道基础单选、3 个阅读程序和 2 个完善程序，
而不是从全部客观题中混合抽取。

平台适合小规模教学和 NAS 部署。管理员可以从内置题库随机组卷，考生可以在线完成
单选题、多选题等客观题，并提交 C++17 编程题代码；系统会将成绩和提交记录保存到
SQLite 数据库。

## 功能

- 管理员创建试卷：可设置题库范围、客观题数量、编程题数量和考试时长。
- 内置多题库范围：全部题库、素养大赛、CSP-J 第一轮、CSP-J 第二轮、
  CSP-S 第一轮、CSP-S 第二轮、GESP、福州机器人赛。
- 客观题题库覆盖 C++ 程序基础、数理知识、模拟、枚举、分治、贪心、递推、递归、
  排序、二分、前缀和、DFS/BFS、STL 容器、栈、队列、链表基础、高精度、位运算、
  进制转换等考点。
- 支持单选题和多选题展示、判分与结果回看。
- 按 C++ 知识点分类均衡随机抽题。
- 考生在线考试页包含倒计时和答题进度标记。
- 编程题使用 C++17 编译运行，并通过题目内置测试评分。
- 提交结果页和管理后台成绩总览。
- 支持 Docker Compose 部署，并使用 SQLite 持久化保存数据。

## 题库与资料

- `online_exam/`：应用代码、静态样式和结构化题库。
- `scripts/`：本地资料提取和导入辅助脚本。
- `CSP/`、`素养大赛/`：本地原始资料目录，默认被 Git 忽略，避免把大体积 PDF、
  PPT、DOCX、压缩包等资料误提交到仓库。

新增竞赛题库时，优先把题目规范化为 `online_exam/question_bank.py` 中相同的数据
结构，并设置 `competition` 字段，例如 `"literacy"`、`"csp_j_round1"`、
`"csp_j_round2"`、`"csp_s_round1"`、`"csp_s_round2"`、`"gesp"`。
`online_exam/imported_csp_questions.py` 由 `python3 scripts/generate_csp_imports.py`
从 `CSP/题库` 生成；生成器会对第一轮题面和答案 PDF 自动尝试本机 Tesseract OCR。
大型扫描版第二轮 PDF 暂作为来源保留，待 OCR 规范化或人工拆题后可重新生成。

### Datalab PDF OCR

`scripts/datalab_ocr.py` 使用 Datalab 官方 Convert API，以 `balanced` 模式输出
Markdown 并启用分页。脚本只会递归处理 `CSP/题库` 及其子目录中的 PDF，不会扫描
`CSP/学习资料`、`CSP/题库OCR` 或其他目录。

请在 `CSP/题库OCR/OCR_KEY` 中保存纯文本 API Key（文件中只放 Key），并限制权限：

```bash
chmod 600 CSP/题库OCR/OCR_KEY
```

先处理一个 PDF：

```bash
python3 scripts/datalab_ocr.py \
  --file "CSP/题库/CSP-J/2019/Round1/cspjs2019hj_cpp.pdf"
```

批量处理题库目录：

```bash
python3 scripts/datalab_ocr.py
```

如果要重新处理已有成功结果，使用 `--force`。结果会写入 `CSP/题库OCR`，并保持
与 `CSP/题库` 相同的相对目录结构；成功时每个 PDF 生成同名 `.md` 和 `.json`。
如果 API 返回图片资源，脚本也会将图片保存到 Markdown 同目录，以保证相对图片链接
可用。Mark Text 需要开启数学公式/KaTeX 支持才能渲染 LaTeX；脚本会将块级公式
规范为独立的 `$$` 行，以提高兼容性。OCR 结果、临时失败记录和临时文件均被 Git
忽略，`OCR_KEY` 不会写入源码或日志。

Convert API 是异步接口：脚本先提交 PDF，再轮询返回的 `request_check_url` 直到
`status=complete`，如果存在 `result_url` 还会继续读取结果。额度和费用以当前
Datalab 账户及服务限制为准，每提交一个 PDF 都可能消耗额度，请避免不必要的批量或
`--force` 操作。当前公开 API 没有保证可以固定调用某个 Chandra 版本，也没有稳定的
`model=chandra` 参数，因此脚本不会发送该参数，而是使用官方 Convert API 的
`balanced` 模式。

### GitHub Actions OCR

仓库还提供了 `.github/workflows/datalab-ocr.yml`，用于在 GitHub Actions
运行 OCR，不依赖本机。该工作流只有 `workflow_dispatch`，不会因 push、PR 或
定时任务自动启动。使用前在 GitHub 仓库的 Settings → Secrets and variables →
Actions 中新增名为 `DATALAB_API_KEY` 的 Secret；不要把 Key 写入仓库文件。
手动运行时工作流固定从默认分支（当前为 `main`）读取题库 PDF。

在 Actions 页面手动运行 `Datalab OCR` 时：

1. 首次选择 `single`，在 `file` 中填写一个 PDF 的仓库相对路径，建议先使用默认的
   `CSP/题库/CSP-J/2019/Round1/cspjs2019hj_cpp.pdf`。
2. 如果该 PDF 已经有成功的 OCR 结果，勾选 `force` 才会真正重新调用 API；这会产生
   新费用。确认单文件链路正常后，再选择 `batch` 处理全部 `CSP/题库` 子目录。
3. `retry` 控制失败重试次数，`poll_interval` 控制异步状态轮询间隔。工作流会检查
   Secret 是否存在，并且不会将 Secret 打印到日志。

结果会按原 PDF 的相对目录写入单独的 `ocr-results` 分支，例如：

```text
CSP/题库/CSP-J/2019/Round1/cspjs2019hj_cpp.pdf
ocr-results: CSP/题库OCR/CSP-J/2019/Round1/cspjs2019hj_cpp.md
ocr-results: CSP/题库OCR/CSP-J/2019/Round1/cspjs2019hj_cpp.json
```

工作流会先恢复 `ocr-results` 分支已有结果，因此重复运行默认跳过已经成功的 PDF，
并保留已完成文件。OCR 失败时不会写入误导性的成功 JSON；工作流仍会尽量发布本次
运行中已经成功生成的结果，最后以失败状态结束，方便从失败处重跑。工作流需要仓库
`contents: write` 权限，且 GitHub Actions 的运行时、Artifact/仓库大小限制与
Datalab 的额度和速率限制是两套独立限制。Datalab Convert API 是异步处理，费用和
额度以当前账户页面及官方服务限制为准；批量运行前请先用单文件验证，并谨慎使用
`force`。

## Docker Compose 部署

推荐本地构建部署：

```bash
git pull
docker compose up -d --build
```

也可以直接从 GitHub 构建：

```bash
docker compose -f docker-compose.github.yml up -d --build
```

如果 NAS 访问 `github.com` 不稳定，但可以拉取 GHCR 镜像，推荐使用预构建镜像：

```bash
docker compose -f docker-compose.ghcr.yml up -d
```

访问地址：

- 考试入口：`http://NAS-IP:8088/`
- 管理后台：`http://NAS-IP:8088/admin`

平台会将数据保存到 Docker 命名卷 `cpp_exam_data` 内的 `/data/exam.db`，NAS 重启或
容器重建后不会丢失。

## 运行说明

编程题提交会在应用容器内使用 `g++` 编译并运行。默认 Compose 文件使用非 root 用户，
将 `/judge` 挂载为可执行 tmpfs，并启用 `no-new-privileges`、基础进程数限制和内存
限制。

当前测评器适合本地教学和小范围信任环境使用，不是严格的公网在线判题沙箱。若要面向
不可信用户公开使用，建议将判题服务拆分到独立沙箱容器或使用专门 OJ 判题系统。
