"""
Compatibility shim for Streamlit pages that import `climatebert_background_worker`.

The canonical ClimateBERT background worker lives at:
`new_page/code/climatebert_background_worker.py`

Some pages do:

    sys.path.insert(0, str(ROOT / "code"))
    from climatebert_background_worker import read_json

…but this repository's `code/` package is mostly ABSA helpers and may not include the
ClimateBERT worker. This shim provides a stable import path by loading the canonical
worker module from disk and re-exporting the small set of helpers pages rely on.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_CANONICAL = _ROOT / "new_page" / "code" / "climatebert_background_worker.py"
if not _CANONICAL.exists():  # pragma: no cover
    raise ModuleNotFoundError(
        "Missing canonical ClimateBERT worker at `new_page/code/climatebert_background_worker.py`."
    )

_spec = spec_from_file_location("_canonical_climatebert_background_worker", _CANONICAL)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise ImportError(f"Failed to load spec for: {_CANONICAL}")

_mod = module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

# Re-export helpers used by Streamlit pages.
utc_now = _mod.utc_now
read_json = _mod.read_json
write_json = _mod.write_json
append_jsonl = _mod.append_jsonl

