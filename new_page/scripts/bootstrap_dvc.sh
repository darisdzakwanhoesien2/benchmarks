#!/usr/bin/env bash
set -euo pipefail

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
