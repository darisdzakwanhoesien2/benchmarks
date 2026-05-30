from __future__ import annotations

from pathlib import Path

import streamlit as st


def apply_page_runtime_controls(page_ref: str | None = None) -> None:
    """Adds per-page Freeze/Refresh controls in the sidebar.

    Behavior:
    - Refresh button clears Streamlit caches and allows one full rerun.
    - Freeze mode stops expensive page execution after controls render,
      until user explicitly clicks Refresh.
    """

    page_name = Path(page_ref or "page").stem
    ns = f"runtime::{page_name}"
    freeze_key = f"{ns}::freeze"
    init_key = f"{ns}::init"
    allow_once_key = f"{ns}::allow_once"

    with st.sidebar.expander("Runtime Controls", expanded=False):
        st.caption("Control heavy data reload behavior for this page.")
        freeze = st.checkbox(
            "Freeze page (skip heavy reloads)",
            key=freeze_key,
            help="When enabled, this page stops before heavy loading until you click Refresh.",
        )
        if st.button("Refresh data now", key=f"{ns}::refresh", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.session_state[allow_once_key] = True
            st.rerun()

    initialized = bool(st.session_state.get(init_key, False))
    allow_once = bool(st.session_state.get(allow_once_key, False))

    if freeze and initialized and not allow_once:
        st.info("Page is frozen. Click 'Refresh data now' in Runtime Controls to load new data.")
        st.stop()

    st.session_state[init_key] = True
    st.session_state[allow_once_key] = False
