#!/usr/bin/env python3
"""Batch OCR PDFs in the CSP question bank with Datalab's Convert API."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import mimetypes
import os
import stat
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
QUESTION_BANK_DIR = ROOT / "CSP" / "题库"
OUTPUT_DIR = ROOT / "CSP" / "题库OCR"
API_KEY_PATH = OUTPUT_DIR / "OCR_KEY"
CONVERT_URL = "https://www.datalab.to/api/v1/convert"
DEFAULT_POLL_INTERVAL = 5.0
REQUEST_TIMEOUT = 120
MAX_POLL_SECONDS = 24 * 60 * 60


class DatalabError(RuntimeError):
    """An API or response validation error that is safe to show to the user."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _redact(value: Any, secret: str) -> Any:
    """Remove the API key from metadata before it is logged or persisted."""
    if isinstance(value, str):
        return value.replace(secret, "[REDACTED]")
    if isinstance(value, dict):
        return {key: _redact(item, secret) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item, secret) for item in value]
    return value


def read_api_key(path: Path) -> str:
    if not path.exists():
        raise DatalabError(f"OCR_KEY 不存在: {path}")
    if not path.is_file():
        raise DatalabError(f"OCR_KEY 不是普通文件: {path}")

    try:
        key = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as exc:
        raise DatalabError(f"无法读取 OCR_KEY: {path} ({exc})") from exc
    if not key:
        raise DatalabError(f"OCR_KEY 为空: {path}")

    try:
        mode = stat.S_IMODE(path.stat().st_mode)
    except OSError as exc:
        print(f"警告: 无法检查 OCR_KEY 权限: {exc}", file=sys.stderr)
    else:
        if mode & 0o077:
            print(
                f"警告: OCR_KEY 权限为 {mode:03o}，建议执行 chmod 600 {path}",
                file=sys.stderr,
            )
    return key


def ensure_within(path: Path, parent: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(parent.resolve())
    except ValueError as exc:
        raise DatalabError(f"{label} 必须位于 {parent} 内: {path}") from exc
    return resolved


def discover_pdfs(input_dir: Path) -> list[Path]:
    pdfs = []
    for path in input_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() != ".pdf":
            continue
        try:
            path.resolve().relative_to(QUESTION_BANK_DIR.resolve())
        except ValueError:
            continue
        pdfs.append(path.resolve())
    return sorted(pdfs, key=lambda item: str(item).casefold())


def _multipart_body(file_path: Path) -> tuple[bytes, str]:
    boundary = f"----datalab-ocr-{uuid.uuid4().hex}"
    chunks: list[bytes] = []

    def add_field(name: str, value: str) -> None:
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                value.encode(),
                b"\r\n",
            ]
        )

    add_field("output_format", "markdown")
    add_field("mode", "balanced")
    add_field("paginate", "true")
    filename = file_path.name.encode("utf-8")
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/pdf"
    chunks.extend(
        [
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="file"; filename="',
            filename,
            b'"\r\n',
            f"Content-Type: {content_type}\r\n\r\n".encode(),
            file_path.read_bytes(),
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def _decode_response(data: bytes) -> Any:
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return data.decode("utf-8", errors="replace")


def _request(
    url: str,
    api_key: str,
    *,
    method: str = "GET",
    body: bytes | None = None,
    content_type: str | None = None,
) -> Any:
    parsed = urlparse(url)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise DatalabError("Datalab 返回了无效的请求 URL")
    headers = {
        "Accept": "application/json, text/markdown, text/plain",
        "X-API-Key": api_key,
        "User-Agent": "cpp-exam-generator-datalab-ocr/1.0",
    }
    if content_type:
        headers["Content-Type"] = content_type
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return _decode_response(response.read())
    except HTTPError as exc:
        try:
            detail = _decode_response(exc.read())
        except OSError:
            detail = "无法读取错误响应"
        if isinstance(detail, dict):
            detail = detail.get("error") or detail.get("detail") or detail.get("message")
        if not isinstance(detail, str) or not detail.strip():
            detail = "无详细错误信息"
        raise DatalabError(f"Datalab HTTP {exc.code}: {detail[:500]}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise DatalabError(f"无法连接 Datalab: {exc}") from exc


def _response_error(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    error = payload.get("error")
    if error:
        return str(error)
    if payload.get("success") is False:
        return str(payload.get("message") or "API 返回 success=false")
    return None


def _status(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    return str(payload.get("status") or "").strip().lower()


def _find_string(payload: Any, names: Iterable[str]) -> str | None:
    wanted = set(names)
    if isinstance(payload, dict):
        for name in wanted:
            value = payload.get(name)
            if isinstance(value, str) and value.strip():
                return value
        for value in payload.values():
            found = _find_string(value, names)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _find_string(value, names)
            if found is not None:
                return found
    return None


def extract_markdown(*payloads: Any) -> str | None:
    for payload in payloads:
        if isinstance(payload, str) and payload.strip():
            return payload
        value = _find_string(payload, ("markdown", "content", "text"))
        if value is not None:
            return value
    return None


def normalize_display_math(markdown: str) -> str:
    """Put one-line $$...$$ blocks into the form Mark Text recognizes reliably."""
    normalized: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if (
            stripped.startswith("$$")
            and stripped.endswith("$$")
            and stripped != "$$"
            and stripped.count("$$") == 2
        ):
            content = stripped[2:-2].strip()
            normalized.extend(["$$", content, "$$"])
        else:
            normalized.append(line)
    return "\n".join(normalized)


def _find_images(payload: Any) -> dict[str, Any] | None:
    if isinstance(payload, dict):
        images = payload.get("images")
        if isinstance(images, dict):
            return images
        for value in payload.values():
            found = _find_images(value)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _find_images(value)
            if found is not None:
                return found
    return None


def _decode_image(value: Any) -> bytes | None:
    if isinstance(value, dict):
        for key in ("data", "base64", "content"):
            decoded = _decode_image(value.get(key))
            if decoded is not None:
                return decoded
        return None
    if not isinstance(value, str):
        return None
    encoded = value.strip()
    if encoded.startswith("data:"):
        try:
            encoded = encoded.split(",", 1)[1]
        except IndexError:
            return None
    encoded = "".join(encoded.split())
    try:
        return base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        return None


def extract_images(*payloads: Any) -> dict[str, bytes]:
    for payload in payloads:
        images = _find_images(payload)
        if images is None:
            continue
        decoded: dict[str, bytes] = {}
        for name, value in images.items():
            if not isinstance(name, str) or not name.strip():
                raise DatalabError("Datalab 返回了无效的图片文件名")
            content = _decode_image(value)
            if content is None:
                raise DatalabError(f"无法解码图片资源: {name}")
            decoded[name] = content
        return decoded
    return {}


def extract_metadata(*payloads: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    fields = (
        "request_id",
        "versions",
        "parse_quality_score",
        "cost_breakdown",
        "page_count",
        "success",
        "error",
    )
    metadata.update({field: None for field in fields})
    for field in fields:
        for payload in payloads:
            value = _find_value(payload, field)
            if value is not None:
                metadata[field] = value
                break
    return metadata


def _find_value(payload: Any, name: str) -> Any:
    if isinstance(payload, dict):
        if name in payload:
            return payload[name]
        for value in payload.values():
            found = _find_value(value, name)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _find_value(value, name)
            if found is not None:
                return found
    return None


def submit_and_poll(
    pdf_path: Path,
    api_key: str,
    poll_interval: float,
) -> tuple[str, dict[str, Any]]:
    body, content_type = _multipart_body(pdf_path)
    submitted = _request(
        CONVERT_URL,
        api_key,
        method="POST",
        body=body,
        content_type=content_type,
    )
    if not isinstance(submitted, dict):
        raise DatalabError("提交接口返回的不是 JSON 对象")
    if _response_error(submitted):
        raise DatalabError(f"提交失败: {_response_error(submitted)}")
    check_url = submitted.get("request_check_url")
    if not isinstance(check_url, str) or not check_url.strip():
        raise DatalabError("提交响应缺少 request_check_url")

    polls: list[Any] = []
    started = time.monotonic()
    while True:
        if time.monotonic() - started > MAX_POLL_SECONDS:
            raise DatalabError("轮询超过 24 小时，已停止等待")
        payload = _request(check_url, api_key)
        polls.append(payload)
        status = _status(payload)
        if status == "complete":
            if _response_error(payload):
                raise DatalabError(f"Datalab 处理失败: {_response_error(payload)}")
            if isinstance(payload, dict) and payload.get("success") is False:
                raise DatalabError("Datalab 处理失败: success=false")
            break
        if status in {"failed", "error", "cancelled", "canceled"}:
            raise DatalabError(f"Datalab 处理失败: {_response_error(payload) or status}")
        if not status:
            raise DatalabError("轮询响应缺少 status")
        print(f"    status={status}，{poll_interval:g}s 后继续轮询")
        time.sleep(poll_interval)

    result_payload: Any = None
    result_url = payload.get("result_url") if isinstance(payload, dict) else None
    if result_url:
        if not isinstance(result_url, str):
            raise DatalabError("result_url 不是字符串")
        result_payload = _request(result_url, api_key)
        if isinstance(result_payload, dict) and _response_error(result_payload):
            raise DatalabError(f"读取 result_url 失败: {_response_error(result_payload)}")

    markdown = extract_markdown(result_payload, payload)
    if markdown is None:
        raise DatalabError("完成响应中没有找到 Markdown 结果")

    metadata = {
        "request_id": _find_value(submitted, "request_id"),
        "request_parameters": {
            "output_format": "markdown",
            "mode": "balanced",
            "paginate": True,
        },
        "completed_at": utc_now(),
        "submit_response": submitted,
        "poll_responses": polls,
        "result_url_response": result_payload,
        "final_response": payload,
    }
    metadata.update(extract_metadata(submitted, payload, result_payload))
    metadata["success"] = True
    metadata["error"] = None
    return markdown, metadata


def is_successful_output(markdown_path: Path, json_path: Path) -> bool:
    if not markdown_path.is_file() or markdown_path.stat().st_size == 0:
        return False
    if not json_path.is_file() or json_path.stat().st_size == 0:
        return False
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    return data.get("success") is True


def atomic_write(path: Path, content: str) -> None:
    if path.resolve() == API_KEY_PATH.resolve():
        raise DatalabError("拒绝覆盖 OCR_KEY")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            temporary = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def atomic_write_bytes(path: Path, content: bytes) -> None:
    if path.resolve() == API_KEY_PATH.resolve():
        raise DatalabError("拒绝覆盖 OCR_KEY")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            temporary = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def materialize_images(images: dict[str, bytes], markdown_path: Path) -> list[str]:
    written: list[str] = []
    output_root = markdown_path.parent.resolve()
    for name, content in images.items():
        image_path = (markdown_path.parent / name).resolve()
        try:
            image_path.relative_to(output_root)
        except ValueError as exc:
            raise DatalabError(f"图片路径超出 OCR 输出目录: {name}") from exc
        atomic_write_bytes(image_path, content)
        written.append(name)
    return written


def restore_images_from_json(json_path: Path, markdown_path: Path) -> list[str]:
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DatalabError(f"无法读取已有 OCR JSON: {json_path} ({exc})") from exc
    return materialize_images(extract_images(data), markdown_path)


def output_paths(pdf_path: Path, output_dir: Path) -> tuple[Path, Path]:
    relative = pdf_path.resolve().relative_to(QUESTION_BANK_DIR.resolve())
    output_base = (output_dir / relative).with_suffix("")
    return output_base.with_suffix(".md"), output_base.with_suffix(".json")


def write_error_metadata(pdf_path: Path, output_dir: Path, error: str, secret: str) -> None:
    _, json_path = output_paths(pdf_path, output_dir)
    error_path = json_path.with_suffix(".error.json")
    payload = {
        "source": str(pdf_path.relative_to(QUESTION_BANK_DIR)),
        "success": False,
        "error": error,
        "recorded_at": utc_now(),
    }
    atomic_write(error_path, json.dumps(_redact(payload, secret), ensure_ascii=False, indent=2) + "\n")


def process_pdf(pdf_path: Path, output_dir: Path, api_key: str, poll_interval: float, force: bool) -> bool:
    markdown_path, json_path = output_paths(pdf_path, output_dir)
    if not force and is_successful_output(markdown_path, json_path):
        try:
            markdown = markdown_path.read_text(encoding="utf-8")
            normalized = normalize_display_math(markdown)
            if normalized != markdown:
                atomic_write(markdown_path, normalized)
                print("已规范化块级公式格式")
        except (OSError, UnicodeError) as exc:
            print(f"警告: 无法规范化已有 Markdown 公式: {exc}", file=sys.stderr)
        try:
            image_files = restore_images_from_json(json_path, markdown_path)
            if image_files:
                print(f"恢复图片资源: {len(image_files)} 个")
        except DatalabError as exc:
            print(f"警告: 无法恢复已有图片资源: {exc}", file=sys.stderr)
        print(f"跳过（已完成）: {pdf_path.relative_to(QUESTION_BANK_DIR)}")
        return True

    print(f"处理: {pdf_path.relative_to(QUESTION_BANK_DIR)}")
    try:
        markdown, metadata = submit_and_poll(pdf_path, api_key, poll_interval)
        markdown = normalize_display_math(markdown)
        metadata["source"] = str(pdf_path.relative_to(QUESTION_BANK_DIR))
        metadata["output_format"] = "markdown"
        metadata["mode"] = "balanced"
        metadata["paginate"] = True
        metadata["image_files"] = materialize_images(extract_images(metadata), markdown_path)
        safe_metadata = _redact(metadata, api_key)
        atomic_write(markdown_path, markdown)
        atomic_write(json_path, json.dumps(safe_metadata, ensure_ascii=False, indent=2) + "\n")
        print(f"完成: {markdown_path}；{json_path}")
        return True
    except (DatalabError, OSError) as exc:
        message = str(_redact(str(exc), api_key))
        print(f"失败: {pdf_path.relative_to(QUESTION_BANK_DIR)}: {message}", file=sys.stderr)
        try:
            write_error_metadata(pdf_path, output_dir, message, api_key)
        except OSError as write_exc:
            print(f"警告: 无法写入失败记录: {write_exc}", file=sys.stderr)
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=QUESTION_BANK_DIR, help="题库目录（必须位于 CSP/题库 内）")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="OCR 输出目录")
    parser.add_argument("--file", type=Path, help="只处理一个位于题库目录内的 PDF")
    parser.add_argument("--retry", type=int, default=2, help="每个 PDF 失败后的重试次数（默认 2）")
    parser.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL, help="轮询间隔秒数（默认 5）")
    parser.add_argument("--force", action="store_true", help="强制重新处理已完成的 PDF")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.retry < 0:
        print("错误: --retry 不能为负数", file=sys.stderr)
        return 2
    if args.poll_interval <= 0:
        print("错误: --poll-interval 必须大于 0", file=sys.stderr)
        return 2

    try:
        input_dir = ensure_within(args.input_dir, QUESTION_BANK_DIR, "--input-dir")
        output_dir = args.output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        api_key = read_api_key(API_KEY_PATH)
        if args.file:
            file_path = ensure_within(args.file, QUESTION_BANK_DIR, "--file")
            if file_path.suffix.lower() != ".pdf" or not file_path.is_file():
                raise DatalabError(f"--file 必须是存在的 PDF: {args.file}")
            file_path.relative_to(input_dir)
            pdfs = [file_path]
        else:
            pdfs = discover_pdfs(input_dir)
    except (DatalabError, OSError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 2

    if not pdfs:
        print(f"未找到 PDF: {input_dir}")
        return 0

    succeeded = 0
    for pdf_path in pdfs:
        completed = False
        for attempt in range(args.retry + 1):
            if attempt:
                print(f"重试 {attempt}/{args.retry}: {pdf_path.relative_to(QUESTION_BANK_DIR)}")
            if process_pdf(pdf_path, output_dir, api_key, args.poll_interval, args.force):
                completed = True
                break
        if completed:
            succeeded += 1

    print(f"处理结束: {succeeded}/{len(pdfs)} 个文件成功")
    return 0 if succeeded == len(pdfs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
