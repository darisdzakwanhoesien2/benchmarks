#!/usr/bin/env python3
import argparse
import datetime as dt
import subprocess
from pathlib import Path


def git_commit() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return "nogit"


def main() -> None:
    ap = argparse.ArgumentParser(description="Create a new run directory and print its path")
    ap.add_argument("--project", required=True)
    ap.add_argument("--run-id", default="")
    args = ap.parse_args()

    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = args.run_id or f"{ts}_{git_commit()}"
    run_dir = Path("outputs") / args.project / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    print(run_dir.as_posix())


if __name__ == "__main__":
    main()
