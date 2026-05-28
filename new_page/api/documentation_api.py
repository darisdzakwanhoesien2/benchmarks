from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from fnmatch import fnmatch
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]

# Keep scope focused on documentation markdown, not OCR/page corpora.
INCLUDE_PATTERNS = [
    "documentation*.md",
    "research_documentation.md",
    "docs/*.md",
    "documentation/**/*.md",
]
EXCLUDE_PATTERNS = [
    "data/**",
    "results/**",
    "pages/**",
    "pages_non_ocr/**",
    "past_pages/**",
    "hidden_pages/**",
    "topic_modelling/**",
    "summarization/**",
    "social_network_analysis/**",
    "about_climatebert/**",
]


@dataclass(frozen=True)
class DocItem:
    doc_id: str
    relative_path: str
    size_bytes: int
    updated_at: str


def iso_utc(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).replace(microsecond=0).isoformat()


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch(path, pat) for pat in patterns)


def build_index() -> dict[str, DocItem]:
    index: dict[str, DocItem] = {}
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        if not matches_any(rel, INCLUDE_PATTERNS):
            continue
        if matches_any(rel, EXCLUDE_PATTERNS):
            continue

        # Stable URL-safe id from path.
        doc_id = rel.replace("/", "__")
        stat = path.stat()
        index[doc_id] = DocItem(
            doc_id=doc_id,
            relative_path=rel,
            size_bytes=stat.st_size,
            updated_at=iso_utc(stat.st_mtime),
        )
    return index


class DocumentationAPIHandler(BaseHTTPRequestHandler):
    server_version = "DocumentationAPI/1.0"

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, content: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = content.encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "text/markdown; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _not_found(self, message: str) -> None:
        self._send_json({"ok": False, "error": message}, status=HTTPStatus.NOT_FOUND)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)

        if path == "/health":
            self._send_json({"ok": True, "service": "documentation_api"})
            return

        if path == "/docs":
            docs = [
                {
                    "doc_id": item.doc_id,
                    "path": item.relative_path,
                    "size_bytes": item.size_bytes,
                    "updated_at": item.updated_at,
                }
                for item in self.server.docs_index.values()  # type: ignore[attr-defined]
            ]
            self._send_json({"ok": True, "count": len(docs), "docs": docs})
            return

        if path.startswith("/docs/"):
            # /docs/{doc_id} -> json with markdown content
            # /docs/{doc_id}/raw -> markdown text
            remainder = path[len("/docs/"):]
            raw = False
            if remainder.endswith("/raw"):
                raw = True
                remainder = remainder[: -len("/raw")]
            doc_id = remainder.strip()

            item = self.server.docs_index.get(doc_id)  # type: ignore[attr-defined]
            if item is None:
                self._not_found(f"Unknown doc_id: {doc_id}")
                return

            file_path = ROOT / item.relative_path
            if not file_path.exists():
                self._not_found(f"File not found on disk: {item.relative_path}")
                return

            content = file_path.read_text(encoding="utf-8", errors="ignore")
            if raw:
                self._send_text(content)
                return

            self._send_json(
                {
                    "ok": True,
                    "doc": {
                        "doc_id": item.doc_id,
                        "path": item.relative_path,
                        "size_bytes": item.size_bytes,
                        "updated_at": item.updated_at,
                        "content": content,
                    },
                }
            )
            return

        if path == "/docs/content":
            # Optional path-based access, e.g. /docs/content?path=documentation_llm.md
            requested = (qs.get("path") or [""])[0].strip()
            if not requested:
                self._send_json({"ok": False, "error": "Missing query param: path"}, status=HTTPStatus.BAD_REQUEST)
                return

            rel = requested.lstrip("/")
            doc_id = rel.replace("/", "__")
            item = self.server.docs_index.get(doc_id)  # type: ignore[attr-defined]
            if item is None:
                self._not_found(f"Path not indexed: {rel}")
                return

            file_path = ROOT / item.relative_path
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            self._send_json(
                {
                    "ok": True,
                    "doc": {
                        "doc_id": item.doc_id,
                        "path": item.relative_path,
                        "content": content,
                    },
                }
            )
            return

        self._not_found(f"Unknown endpoint: {path}")


def run_server(host: str, port: int) -> None:
    docs_index = build_index()
    server = ThreadingHTTPServer((host, port), DocumentationAPIHandler)
    server.docs_index = docs_index  # type: ignore[attr-defined]
    print(f"Documentation API listening on http://{host}:{port}")
    print(f"Indexed markdown docs: {len(docs_index)}")
    print("Endpoints:")
    print("  GET /health")
    print("  GET /docs")
    print("  GET /docs/{doc_id}")
    print("  GET /docs/{doc_id}/raw")
    print("  GET /docs/content?path=<relative_path>")
    server.serve_forever()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve markdown documentation via HTTP API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8010, help="Port to bind (default: 8010)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_server(host=args.host, port=args.port)
