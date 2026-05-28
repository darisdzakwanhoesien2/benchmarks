# Documentation API

Simple HTTP API to fetch project markdown documentation files.

## Run

```bash
python3 api/documentation_api.py --host 0.0.0.0 --port 8010
```

## Endpoints

- `GET /health`
- `GET /docs` -> list indexed docs
- `GET /docs/{doc_id}` -> JSON payload with markdown content
- `GET /docs/{doc_id}/raw` -> raw markdown
- `GET /docs/content?path=documentation_llm.md` -> fetch by relative path

## Notes

- `doc_id` is path-based with `/` replaced by `__`.
  - Example: `documentation/section_reports/README.md` -> `documentation__section_reports__README.md`
- Scope is restricted to documentation markdown files (root `documentation*.md`, `research_documentation.md`, `docs/*.md`, and `documentation/**/*.md`).
