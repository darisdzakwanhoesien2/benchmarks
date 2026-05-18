from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import altair as alt
import pandas as pd
import requests
import streamlit as st


st.set_page_config(page_title="Sustainable Framework API Reader", layout="wide")

DEFAULT_BASE_URL = "https://sustainable-framework-api.darisdzakwanhoesien.site"
DEFAULT_TIMEOUT = 30
ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "results" / "api_reader"


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


def api_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/") + "/"
    return urljoin(base, path.lstrip("/"))


def request_json(base_url: str, path: str, api_key: str = "", params: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any]]:
    headers = {}
    if api_key.strip():
        headers["x-api-key"] = api_key.strip()
    url = api_url(base_url, path)
    response = requests.get(url, headers=headers, params=params or {}, timeout=DEFAULT_TIMEOUT)
    meta = {
        "url": response.url,
        "status_code": response.status_code,
        "content_type": response.headers.get("content-type", ""),
        "elapsed_ms": round(response.elapsed.total_seconds() * 1000, 1),
    }
    response.raise_for_status()
    return response.json(), meta


@st.cache_data(ttl=300, show_spinner=False)
def cached_catalog(base_url: str, api_key: str) -> tuple[Any, dict[str, Any]]:
    return request_json(base_url, "/api/v1/catalog", api_key)


@st.cache_data(ttl=300, show_spinner=False)
def cached_openapi(base_url: str, api_key: str) -> tuple[Any, dict[str, Any]]:
    return request_json(base_url, "/openapi.json", api_key)


@st.cache_data(ttl=120, show_spinner=False)
def cached_endpoint(base_url: str, path: str, api_key: str, params_items: tuple[tuple[str, Any], ...]) -> tuple[Any, dict[str, Any]]:
    return request_json(base_url, path, api_key, dict(params_items))


def catalog_datasets(catalog: Any) -> list[dict[str, Any]]:
    if not isinstance(catalog, dict):
        return []
    datasets = catalog.get("datasets")
    if not isinstance(datasets, list):
        return []
    return [item for item in datasets if isinstance(item, dict) and clean(item.get("id"))]


def shortcut_paths(openapi: Any) -> list[str]:
    if not isinstance(openapi, dict) or not isinstance(openapi.get("paths"), dict):
        return []
    paths = []
    for path, methods in openapi["paths"].items():
        if not path.startswith("/api/v1/"):
            continue
        if "{" in path or not isinstance(methods, dict) or "get" not in methods:
            continue
        if path in {"/api/v1/catalog"}:
            continue
        paths.append(path)
    return sorted(paths)


def extract_records(data: Any) -> tuple[pd.DataFrame, str]:
    if not isinstance(data, dict):
        return pd.DataFrame(), "non-object response"

    if isinstance(data.get("records"), list):
        return pd.json_normalize(data["records"]), "records"

    payload = data.get("payload")
    if isinstance(payload, dict):
        if isinstance(payload.get("records"), list):
            return pd.json_normalize(payload["records"]), "payload.records"
        for key, value in payload.items():
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                return pd.json_normalize(value), f"payload.{key}"

    for key, value in data.items():
        if isinstance(value, list) and all(isinstance(item, dict) for item in value):
            return pd.json_normalize(value), key

    return pd.DataFrame(), "no record list found"


def short_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    view = df.copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].map(lambda value: clean(value)[:500] if not isinstance(value, (dict, list)) else json.dumps(value, ensure_ascii=False)[:500])
    return view


def id_columns(df: pd.DataFrame) -> list[str]:
    preferred = [
        "id",
        "source_id",
        "group_id",
        "Code",
        "code",
        "paper_id",
        "question_id",
        "title",
        "Title",
        "group_name",
        "filename",
    ]
    return [col for col in preferred if col in df.columns] + [col for col in df.columns if col not in preferred]


def record_label(row: pd.Series, id_col: str) -> str:
    value = clean(row.get(id_col))
    for fallback in ["title", "Title", "group_name", "filename", "source_id", "Code"]:
        if fallback != id_col and fallback in row and clean(row.get(fallback)):
            return f"{value} | {clean(row.get(fallback))[:90]}" if value else clean(row.get(fallback))[:120]
    return value or f"row_{row.name}"


def count_chart(df: pd.DataFrame, column: str) -> None:
    if df.empty or column not in df.columns:
        st.info("No categorical column selected.")
        return
    chart_df = df[column].map(clean).replace("", "missing").value_counts().head(30).rename_axis(column).reset_index(name="count")
    chart = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X("count:Q", title="Rows"),
            y=alt.Y(f"{column}:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
            color=alt.value("#217c7e"),
            tooltip=[column, "count"],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)


def save_snapshot(name: str, data: Any) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name).strip("_") or "api_response"
    path = EXPORT_DIR / f"{safe_name}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


st.title("Sustainable Framework API Reader")
st.caption("Browse the live Sustainable Framework API catalog, call dataset endpoints, inspect records, and export response snapshots.")

with st.sidebar:
    st.header("Connection")
    base_url = st.text_input("Base URL", DEFAULT_BASE_URL)
    api_key = st.text_input("API key", value="", type="password")
    use_cache = st.checkbox("Use short cache", value=True)
    if st.button("Refresh API metadata", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

catalog: Any = {}
openapi: Any = {}
catalog_meta: dict[str, Any] = {}
openapi_meta: dict[str, Any] = {}

try:
    catalog, catalog_meta = cached_catalog(base_url, api_key) if use_cache else request_json(base_url, "/api/v1/catalog", api_key)
    openapi, openapi_meta = cached_openapi(base_url, api_key) if use_cache else request_json(base_url, "/openapi.json", api_key)
except Exception as exc:
    st.error(f"Could not load API metadata: {exc}")
    st.stop()

datasets = catalog_datasets(catalog)
dataset_by_id = {item["id"]: item for item in datasets}
shortcuts = shortcut_paths(openapi)

with st.sidebar:
    st.header("Endpoint")
    mode = st.radio("Reader mode", ["Catalog dataset", "Shortcut endpoint", "Custom path"], horizontal=False)
    params: dict[str, Any] = {}

    if mode == "Catalog dataset":
        dataset_ids = list(dataset_by_id)
        default_index = dataset_ids.index("patent-analysis") if "patent-analysis" in dataset_ids else 0
        selected_id = st.selectbox("Dataset", dataset_ids, index=default_index)
        selected_dataset = dataset_by_id[selected_id]
        endpoint_path = clean(selected_dataset.get("url")) or f"/api/v1/datasets/{selected_id}"
        shortcut_candidate = f"/api/v1/{selected_id}"
        if shortcut_candidate in shortcuts:
            use_shortcut = st.toggle("Use shortcut endpoint", value=True)
            if use_shortcut:
                endpoint_path = shortcut_candidate
        st.caption(clean(selected_dataset.get("description")))
    elif mode == "Shortcut endpoint":
        default_path = "/api/v1/patent-analysis" if "/api/v1/patent-analysis" in shortcuts else (shortcuts[0] if shortcuts else "/api/v1/catalog")
        endpoint_path = st.selectbox("Shortcut", shortcuts, index=shortcuts.index(default_path) if default_path in shortcuts else 0)
    else:
        endpoint_path = st.text_input("Path", "/api/v1/patent-analysis")

    if endpoint_path.startswith("/api/v1/extra-sources"):
        params["include_content"] = st.checkbox("include_content", value=False)
        params["max_chars"] = st.number_input("max_chars", min_value=1000, max_value=100000, value=12000, step=1000)
    if endpoint_path.startswith("/api/v1/research-framework-questions"):
        params["include_answers"] = st.checkbox("include_answers", value=False)

    table_limit = st.number_input("Table row limit", min_value=25, max_value=5000, value=500, step=25)
    search = st.text_input("Search records", "")
    call_button = st.button("Call endpoint", use_container_width=True)

params_items = tuple(sorted(params.items()))

try:
    data, response_meta = cached_endpoint(base_url, endpoint_path, api_key, params_items) if use_cache else request_json(base_url, endpoint_path, api_key, params)
except Exception as exc:
    st.error(f"Endpoint call failed: {exc}")
    st.stop()

records_df, record_source = extract_records(data)
if search.strip() and not records_df.empty:
    needle = search.strip().lower()
    mask = pd.Series(False, index=records_df.index)
    for col in records_df.columns:
        mask = mask | records_df[col].map(lambda value: needle in clean(value).lower())
    records_df = records_df[mask]

top = st.columns(5)
top[0].metric("Status", str(response_meta.get("status_code", "")))
top[1].metric("Rows", f"{len(records_df):,}")
top[2].metric("Columns", f"{len(records_df.columns):,}")
top[3].metric("Elapsed", f"{response_meta.get('elapsed_ms', 0):,.1f} ms")
top[4].metric("Datasets", f"{len(datasets):,}")

st.caption(f"Endpoint: `{response_meta.get('url', api_url(base_url, endpoint_path))}`")
st.caption(f"Record source: `{record_source}`")

tabs = st.tabs(["Catalog", "Table", "Record Detail", "Summary", "Raw JSON", "Export"])

with tabs[0]:
    st.subheader("Catalog datasets")
    catalog_df = pd.DataFrame(datasets)
    if catalog_df.empty:
        st.warning("No catalog datasets were returned.")
    else:
        st.dataframe(catalog_df, use_container_width=True, hide_index=True, height=420)
    st.subheader("GET shortcut endpoints")
    st.dataframe(pd.DataFrame({"path": shortcuts}), use_container_width=True, hide_index=True, height=260)

with tabs[1]:
    if records_df.empty:
        st.warning("No tabular record list found in this response.")
    else:
        st.dataframe(short_columns(records_df).head(int(table_limit)), use_container_width=True, height=620)
        st.download_button(
            "Download table CSV",
            records_df.to_csv(index=False).encode("utf-8"),
            "sustainable_framework_api_records.csv",
            "text/csv",
        )

with tabs[2]:
    if records_df.empty:
        st.warning("No records available for detail view.")
    else:
        options = id_columns(records_df)
        id_col = st.selectbox("Record label column", options)
        labels = [record_label(row, id_col) for _, row in records_df.iterrows()]
        selected_label = st.selectbox("Record", labels)
        selected_index = labels.index(selected_label)
        selected_record = records_df.iloc[selected_index].dropna().to_dict()
        st.json(selected_record, expanded=True)

        direct_path = ""
        if endpoint_path == "/api/v1/patent-analysis" and "Code" in selected_record:
            direct_path = f"/api/v1/patent-analysis/{selected_record['Code']}"
        if endpoint_path == "/api/v1/research-groups" and "group_id" in selected_record:
            direct_path = f"/api/v1/research-groups/{selected_record['group_id']}"
        if direct_path:
            if st.button("Call selected record endpoint", use_container_width=True):
                detail_data, detail_meta = request_json(base_url, direct_path, api_key)
                st.caption(f"Detail URL: `{detail_meta['url']}`")
                st.json(detail_data, expanded=True)

with tabs[3]:
    if records_df.empty:
        st.warning("No records available for summary.")
    else:
        candidate_cols = [col for col in records_df.columns if records_df[col].dtype == object or records_df[col].nunique(dropna=True) <= 50]
        selected_col = st.selectbox("Categorical summary column", candidate_cols or list(records_df.columns))
        count_chart(records_df, selected_col)
        st.dataframe(records_df.describe(include="all").transpose(), use_container_width=True, height=420)

with tabs[4]:
    st.json(data, expanded=False)

with tabs[5]:
    snapshot_name = endpoint_path.strip("/").replace("/", "_")
    if st.button("Save JSON snapshot to results/api_reader", use_container_width=True):
        saved_path = save_snapshot(snapshot_name, data)
        st.success(f"Saved `{saved_path}`")
    st.download_button(
        "Download raw JSON",
        json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
        f"{snapshot_name or 'api_response'}.json",
        "application/json",
    )
