from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


def render_attachment_cards(attachments: list[dict[str, Any]] | pd.DataFrame, root: str | Path | None = None) -> None:
    """
    Minimal template: render a simple table/list of artifact attachments.
    The thesis integration page can pass either a list of dicts or a dataframe.
    """
    if attachments is None:
        st.info("No attachments provided.")
        return

    if isinstance(attachments, pd.DataFrame):
        df = attachments.copy()
    else:
        try:
            df = pd.DataFrame(list(attachments))
        except Exception:
            st.info("Attachments could not be rendered.")
            return

    if df.empty:
        st.info("No attachments found.")
        return

    if root is not None:
        df["root"] = str(root)
    st.dataframe(df, use_container_width=True, hide_index=True, height=320)

