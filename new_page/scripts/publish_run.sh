#!/usr/bin/env bash
set -euo pipefail


usage() {
  cat <<EOF
Usage: $(basename "$0") [options]
[No description available]
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <run_dir> <remote_uri> [extra_rsync_args...]"
  echo "Example remote_uri: user@vps:/srv/benchmarks-archive"
  exit 1
fi

RUN_DIR="$1"
REMOTE_URI="$2"
shift 2

if [[ ! -d "$RUN_DIR" ]]; then
  echo "Run directory not found: $RUN_DIR"
  exit 1
fi

rsync -av --delete "$RUN_DIR" "$REMOTE_URI" "$@"

echo "Published $RUN_DIR to $REMOTE_URI"
