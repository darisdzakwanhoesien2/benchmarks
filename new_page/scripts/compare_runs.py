#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Dict, Tuple


def load_manifest(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def index_files(manifest: Dict) -> Dict[str, Tuple[str, int]]:
    out = {}
    for item in manifest["output"].get("files", []):
        out[item["path"]] = (item["sha256"], item["size_bytes"])
    return out


def resolve_manifest(p: str) -> Path:
    path = Path(p)
    if path.is_dir():
        cand = path / "run.json"
        if cand.exists():
            return cand
    if path.is_file():
        return path
    raise SystemExit(f"Cannot resolve manifest from: {p}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Compare two run manifests")
    ap.add_argument("run_a")
    ap.add_argument("run_b")
    args = ap.parse_args()

    a_path = resolve_manifest(args.run_a)
    b_path = resolve_manifest(args.run_b)

    a = load_manifest(a_path)
    b = load_manifest(b_path)

    ai = index_files(a)
    bi = index_files(b)

    added = sorted(set(bi) - set(ai))
    removed = sorted(set(ai) - set(bi))
    changed = sorted(k for k in set(ai) & set(bi) if ai[k][0] != bi[k][0])

    print(f"A: {a['run_id']} ({a_path})")
    print(f"B: {b['run_id']} ({b_path})")
    print("")
    print(f"A digest: {a['output']['tree_digest_sha256']}")
    print(f"B digest: {b['output']['tree_digest_sha256']}")
    print(f"A files : {a['output']['file_count']} ({a['output']['total_bytes']} bytes)")
    print(f"B files : {b['output']['file_count']} ({b['output']['total_bytes']} bytes)")
    print("")
    print(f"Added   : {len(added)}")
    for p in added[:100]:
        print(f"  + {p}")
    if len(added) > 100:
        print(f"  ... ({len(added)-100} more)")

    print(f"Removed : {len(removed)}")
    for p in removed[:100]:
        print(f"  - {p}")
    if len(removed) > 100:
        print(f"  ... ({len(removed)-100} more)")

    print(f"Changed : {len(changed)}")
    for p in changed[:100]:
        a_sha, a_sz = ai[p]
        b_sha, b_sz = bi[p]
        print(f"  * {p} ({a_sz}->{b_sz})")
        print(f"    A {a_sha}")
        print(f"    B {b_sha}")
    if len(changed) > 100:
        print(f"  ... ({len(changed)-100} more)")


if __name__ == "__main__":
    main()
