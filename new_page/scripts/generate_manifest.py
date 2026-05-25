#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import socket
import subprocess
from pathlib import Path
from typing import Dict, List


def now_utc_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def git_commit() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return "nogit"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_files(root: Path) -> List[Path]:
    files = []
    for p in root.rglob("*"):
        if p.is_file():
            files.append(p)
    return sorted(files)


def compute_summary(output_dir: Path) -> Dict:
    files = collect_files(output_dir)
    total_bytes = 0
    entries = []
    for f in files:
        rel = f.relative_to(output_dir).as_posix()
        size = f.stat().st_size
        total_bytes += size
        entries.append({
            "path": rel,
            "size_bytes": size,
            "sha256": sha256_file(f),
        })
    digest = hashlib.sha256("\n".join(f"{e['path']}:{e['sha256']}" for e in entries).encode()).hexdigest()
    return {
        "file_count": len(entries),
        "total_bytes": total_bytes,
        "tree_digest_sha256": digest,
        "files": entries,
    }


def detect_environment(explicit: str | None) -> str:
    if explicit:
        return explicit
    host = socket.gethostname().lower()
    if "vps" in host:
        return "vps"
    return "local"


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate run manifest with checksums")
    ap.add_argument("--project", required=True, help="Project name under outputs/")
    ap.add_argument("--output-dir", required=True, help="Output directory for this run")
    ap.add_argument("--dataset-version", default="unknown", help="Dataset version id")
    ap.add_argument("--params-file", default="", help="Path to params JSON/YAML used by run")
    ap.add_argument("--environment", default="", help="local or vps")
    ap.add_argument("--run-id", default="", help="Optional explicit run id")
    args = ap.parse_args()

    output_dir = Path(args.output_dir).resolve()
    if not output_dir.exists() or not output_dir.is_dir():
        raise SystemExit(f"Output directory does not exist: {output_dir}")

    commit = git_commit()
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = args.run_id or f"{ts}_{commit}"
    env = detect_environment(args.environment or None)

    summary = compute_summary(output_dir)

    manifest = {
        "run_id": run_id,
        "created_at_utc": now_utc_iso(),
        "project": args.project,
        "git_commit": commit,
        "dataset_version": args.dataset_version,
        "params_file": args.params_file,
        "machine": {
            "environment": env,
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "output": {
            "path": output_dir.as_posix(),
            **summary,
        },
    }

    manifest_path = output_dir / "run.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    latest_dir = Path("outputs") / args.project / "latest"
    latest_dir.parent.mkdir(parents=True, exist_ok=True)
    if latest_dir.exists() or latest_dir.is_symlink():
        latest_dir.unlink()
    latest_dir.symlink_to(output_dir)

    print(manifest_path.as_posix())


if __name__ == "__main__":
    main()
