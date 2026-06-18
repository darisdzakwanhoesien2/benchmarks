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
if ! command -v dvc >/dev/null 2>&1; then
  echo "Installing DVC..."
  pip install dvc[s3]
fi

if [[ ! -d .dvc ]]; then
  dvc init
fi

echo "DVC ready. Configure remote with:"
echo "  dvc remote add -d storage <REMOTE_URL>"
echo "  dvc remote modify storage <key> <value>   # if needed"
