# Data Ops Workflow (Local + VPS)

This repo now separates code from run artifacts:
- Code/config/scripts: GitHub
- Analysis outputs: `outputs/<project>/<run_id>/` (tracked with manifest + optional DVC)

## 1) One-time setup

```bash
make setup-dirs
make dvc-init
```

Then configure DVC remote (example S3):

```bash
dvc remote add -d storage s3://YOUR_BUCKET/benchmarks
# if needed:
# dvc remote modify storage endpointurl https://<provider-endpoint>
# dvc remote modify storage access_key_id <key>
# dvc remote modify storage secret_access_key <secret>
```

## 2) Start a new run

```bash
make start-run PROJECT=esg_absa
```

This prints a new run folder like:
`outputs/esg_absa/20260524T101500Z_a1b2c3d`

Write your analysis outputs into that folder.

## 3) Generate manifest (required)

```bash
make manifest \
  PROJECT=esg_absa \
  RUN_DIR=outputs/esg_absa/20260524T101500Z_a1b2c3d \
  DATASET_VERSION=thesis_dataset_v1 \
  PARAMS_FILE=prompt/zero_shot_english.md \
  ENVIRONMENT=local
```

This writes `run.json` with:
- run id
- git commit
- dataset version
- params reference
- machine info (local/vps)
- checksum summary for every output file

## 4) Compare two runs

```bash
make compare \
  RUN_A=outputs/esg_absa/20260524T101500Z_a1b2c3d \
  RUN_B=outputs/esg_absa/20260524T130200Z_d4e5f6g
```

Shows added/removed/changed files with hashes and sizes.

## 5) Publish between local and VPS (rsync)

```bash
make publish \
  RUN_DIR=outputs/esg_absa/20260524T101500Z_a1b2c3d \
  REMOTE_URI=user@your-vps:/srv/benchmarks-archive
```

## 6) Track large outputs with DVC

```bash
make dvc-track-output RUN_DIR=outputs/esg_absa/20260524T101500Z_a1b2c3d
git add .
git commit -m "Track run metadata"
make dvc-push
```

On another machine:

```bash
git pull
make dvc-pull
```

## Suggested discipline

- Never overwrite existing run directories.
- Always create a new run id per execution.
- Always generate `run.json` immediately after a run.
- Keep raw inputs in `data/raw/` and transformed inputs in `data/processed/`.
