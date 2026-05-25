SHELL := /bin/bash

PROJECT ?= default
RUN_ID ?=
DATASET_VERSION ?= unknown
PARAMS_FILE ?=
ENVIRONMENT ?=
RUN_DIR ?=
REMOTE_URI ?=
RUN_A ?=
RUN_B ?=

.PHONY: help setup-dirs start-run manifest compare publish dvc-init dvc-track-output dvc-push dvc-pull

help:
	@echo "Targets:"
	@echo "  make setup-dirs"
	@echo "  make start-run PROJECT=<name> [RUN_ID=<id>]"
	@echo "  make manifest PROJECT=<name> RUN_DIR=<outputs/...> [DATASET_VERSION=...] [PARAMS_FILE=...] [ENVIRONMENT=local|vps]"
	@echo "  make compare RUN_A=<outputs/...|run.json> RUN_B=<outputs/...|run.json>"
	@echo "  make publish RUN_DIR=<outputs/...> REMOTE_URI=<user@host:/path>"
	@echo "  make dvc-init"
	@echo "  make dvc-track-output RUN_DIR=<outputs/...>"
	@echo "  make dvc-push"
	@echo "  make dvc-pull"

setup-dirs:
	mkdir -p data/raw data/processed outputs reports

start-run:
	@python3 scripts/start_run.py --project "$(PROJECT)" $(if $(RUN_ID),--run-id "$(RUN_ID)",)

manifest:
	@test -n "$(RUN_DIR)" || (echo "RUN_DIR is required" && exit 1)
	python3 scripts/generate_manifest.py \
	  --project "$(PROJECT)" \
	  --output-dir "$(RUN_DIR)" \
	  --dataset-version "$(DATASET_VERSION)" \
	  --params-file "$(PARAMS_FILE)" \
	  --environment "$(ENVIRONMENT)" \
	  $(if $(RUN_ID),--run-id "$(RUN_ID)",)

compare:
	@test -n "$(RUN_A)" || (echo "RUN_A is required" && exit 1)
	@test -n "$(RUN_B)" || (echo "RUN_B is required" && exit 1)
	python3 scripts/compare_runs.py "$(RUN_A)" "$(RUN_B)"

publish:
	@test -n "$(RUN_DIR)" || (echo "RUN_DIR is required" && exit 1)
	@test -n "$(REMOTE_URI)" || (echo "REMOTE_URI is required" && exit 1)
	./scripts/publish_run.sh "$(RUN_DIR)" "$(REMOTE_URI)"

dvc-init:
	./scripts/bootstrap_dvc.sh

dvc-track-output:
	@test -n "$(RUN_DIR)" || (echo "RUN_DIR is required" && exit 1)
	dvc add "$(RUN_DIR)"

dvc-push:
	dvc push

dvc-pull:
	dvc pull
