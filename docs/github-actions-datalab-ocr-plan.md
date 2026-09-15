# GitHub Actions Datalab OCR 后续开发建议

本文档定义后续将 OCR 任务迁移到 GitHub Actions 的实现方案。目标是：不依赖本机，使用 Datalab API 处理 `CSP/题库` 下的 PDF，并将结果按原目录结构保存到单独的 `ocr-results` 分支。

## 目标目录结构

输入 PDF 与 OCR 输出保持相同的相对路径：

```text
CSP/题库/CSP-J/2019/Round1/cspjs2019hj_cpp.pdf
CSP/题库OCR/CSP-J/2019/Round1/cspjs2019hj_cpp.md
CSP/题库OCR/CSP-J/2019/Round1/cspjs2019hj_cpp.json
CSP/题库OCR/CSP-J/2019/Round1/9ba3..._img.jpg
```

计算规则：

```python
relative = pdf_path.relative_to(repo_root / "CSP/题库")
output_base = repo_root / "CSP/题库OCR" / relative.with_suffix("")
```

`ocr-results` 分支只保存 `CSP/题库OCR/` 下的结果，不修改 `main` 中的原始 PDF。

## 推荐实现顺序

### 1. 先增强 OCR 客户端

在 `scripts/datalab_ocr.py` 中增加以下能力：

- 从环境变量 `DATALAB_API_KEY` 读取 Key；本机仍可兼容 `CSP/题库OCR/OCR_KEY`。
- 增加 `--dry-run`，只统计待处理 PDF、页数和预计费用，不提交 API。
- 增加 `--max-pages` 和 `--max-cost-usd`，达到预算后停止提交新任务。
- 将网络错误、HTTP 429、500、502、503、504 与不可重试错误分类。
- 对 429 使用 `Retry-After`，其他临时错误使用指数退避。
- 保存 `request_id`、`request_check_url`、文件 SHA-256 和提交时间，支持中断后继续轮询。
- 轮询间隔使用 5、10、20、30 秒退避，避免不必要的状态请求。
- 每完成一个文件立即原子写入 `.md`、`.json` 和图片，保证任务中断后可续跑。
- 继续保留现有的路径限制、图片解码、公式规范化、Key 脱敏和成功结果跳过逻辑。

### 2. 增加 GitHub Actions 工作流

建议新增 `.github/workflows/datalab-ocr.yml`，只允许手动触发：

```yaml
name: Datalab OCR

on:
  workflow_dispatch:
    inputs:
      scope:
        description: '要处理的目录，例如 CSP-J 或全部题库'
        required: true
        default: 'CSP-J'
      force:
        description: '是否重新处理已有成功结果'
        type: boolean
        default: false

permissions:
  contents: write

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
      - id: matrix
        run: python3 scripts/build_ocr_matrix.py "${{ inputs.scope }}"

  ocr:
    needs: prepare
    strategy:
      fail-fast: false
      max-parallel: 2
      matrix:
        shard: ${{ fromJson(needs.prepare.outputs.matrix) }}
    runs-on: ubuntu-latest
    timeout-minutes: 330
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: Run OCR shard
        env:
          DATALAB_API_KEY: ${{ secrets.DATALAB_API_KEY }}
        run: python3 scripts/datalab_ocr.py --input-dir "${{ matrix.shard }}" --retry 1 --poll-interval 10
      - name: Upload shard results
        uses: actions/upload-artifact@v4
        with:
          name: ocr-${{ strategy.job-index }}
          path: CSP/题库OCR/
          retention-days: 14

  publish:
    needs: ocr
    if: ${{ success() }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/download-artifact@v4
        with:
          pattern: ocr-*
          path: CSP/题库OCR/
          merge-multiple: true
      - name: Publish results branch
        run: |
          git switch --create ocr-results
          git config user.name github-actions[bot]
          git config user.email 41898282+github-actions[bot]@users.noreply.github.com
          git add CSP/题库OCR/
          git commit -m "chore: publish Datalab OCR results" || true
          git push origin ocr-results
```

上面的 YAML 是结构示例，正式实现前必须补充：

- `build_ocr_matrix.py` 生成稳定、可复现的分片列表。
- `datalab_ocr.py` 的 `--input-dir` 校验要允许 `CSP/题库/CSP-J` 等子目录，但仍禁止越出 `CSP/题库`。
- `DATALAB_API_KEY` 环境变量优先级高于本机 Key 文件。
- 不要将 `OCR_KEY`、`DATALAB_API_KEY` 或任何 API 响应中的密钥提交到 Git。
- 生产工作流不要默认开启 `--force`。

## 分片和并发建议

首次批量建议按总页数而不是 PDF 数量分片，每个分片控制在约 300～500 页。Free 工作邮箱的 Datalab 速率限制和额度独立于 GitHub Actions 限制，因此建议：

- `max-parallel: 2` 起步。
- 每个任务 `--poll-interval 10`。
- 先运行一个 50～100 页的小分片观察实际费用和完成时间。
- 只有确认没有 429、费用符合预期后，再提高并发。
- 不要在多个工作流同时处理相同 PDF。

GitHub Actions 单个 Job 有运行时上限，因此不要把全部题库放入一个 Job。每个分片应能在上限前完成，并允许单独重跑。

## 费用和安全保护

运行前应打印但不提交以下摘要：

```text
待处理 PDF 数量
待处理总页数
已完成 PDF 数量
预计费用
预算上限
```

建议默认预算上限为 `$15`，给 Free 工作邮箱的 `$20/月` 额度保留余量。超过预算时停止提交新 PDF，并让 workflow 失败退出。

完整 API JSON 如果包含 Base64 图片，可能显著增大 Artifact 和 Git 分支体积。建议：

- `ocr-results` 分支保存 `.md`、图片和精简 JSON。
- 完整 API JSON 保存为短期 Artifact，例如 14 天。
- 上传 Artifact 前检查单文件大小和总目录大小。
- 不上传 `OCR_KEY`、临时文件、日志中的请求头或完整 API Key。

## 失败恢复

- 每个 PDF 使用 `.error.json` 记录失败原因，但不能把失败结果标记为成功。
- GitHub Actions 失败时保留失败分片 Artifact。
- 重跑失败分片时依靠 `.md` + `.json` 成功判断跳过已完成文件。
- 如果提交已成功但 Job 在轮询期间中断，必须使用持久化任务状态继续轮询，不能直接重新 POST。
- `--force` 只用于用户明确指定的 PDF 或分片。

## 换电脑后的同步方式

完成 GitHub Actions 后，在新电脑执行：

```bash
git clone https://github.com/admin05/cpp-exam-generator.git
cd cpp-exam-generator
git fetch origin ocr-results
git restore --source=origin/ocr-results -- CSP/题库OCR
```

如果只想查看结果分支：

```bash
git switch --track origin/ocr-results
```

如果不希望把 OCR 结果混入当前开发分支，推荐使用第一种 `git restore` 方式。结果会自动落到：

```text
CSP/题库OCR/<与 CSP/题库 相同的相对目录>/
```

## 发布前检查清单

- [ ] `DATALAB_API_KEY` 已添加到 GitHub Actions Secrets。
- [ ] workflow 只允许手动触发。
- [ ] matrix 分片没有目录重叠。
- [ ] `max-parallel` 已限制为 2 或更低。
- [ ] 已设置预算、页数和超时保护。
- [ ] 已用小分片验证费用和输出路径。
- [ ] `.md`、图片和精简 JSON 的相对路径正确。
- [ ] 完整 JSON 只放短期 Artifact。
- [ ] `OCR_KEY` 和 API Key 没有出现在提交、Artifact 名称或日志中。
- [ ] `ocr-results` 分支没有覆盖 `main`。
