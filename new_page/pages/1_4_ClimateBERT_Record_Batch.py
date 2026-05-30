from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="ClimateBERT Record Batch", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "results" / "revision_analysis"
SILVER_PATH = ARTIFACTS / "silver_tone_ground_truth.csv"
PROXY_PATH = ARTIFACTS / "climatebert_proxy_agreement_records.csv"
IMPORTED_PATH = ARTIFACTS / "climatebert_record_batch_import.csv"


def load(path):
    if path.exists():
        return pd.read_csv(path).fillna("")
    return pd.DataFrame()


def cohen_kappa_bool(a, b):
    a = pd.Series(a).astype(bool)
    b = pd.Series(b).astype(bool)
    if len(a) == 0:
        return 0
    po = (a == b).mean()
    pya, pyb = a.mean(), b.mean()
    pe = pya * pyb + (1 - pya) * (1 - pyb)
    return (po - pe) / (1 - pe) if (1 - pe) else 0


def agreement_summary(df, pred_col):
    truth = df["tone_pred"].astype(str).eq("commitment")
    pred = df[pred_col].astype(bool)
    return {
        "n": len(df),
        "percent_agreement": (truth == pred).mean() if len(df) else 0,
        "cohen_kappa": cohen_kappa_bool(truth, pred),
        "tone_commitment_rate": truth.mean() if len(df) else 0,
        "climate_commitment_rate": pred.mean() if len(df) else 0,
    }


st.title("ClimateBERT Record Batch")
st.caption("Prepare the 332 extracted records for ClimateBERT validation, inspect current proxy labels, and import real ClimateBERT batch outputs when available.")

silver = load(SILVER_PATH)
proxy = load(PROXY_PATH)
imported = load(IMPORTED_PATH)

if silver.empty:
    st.error(f"Missing {SILVER_PATH}")
    st.stop()

tabs = st.tabs(["Batch Input", "Proxy Batch", "Import Real Outputs", "Agreement", "Export"])

with tabs[0]:
    st.subheader("Batch Input for ClimateBERT")
    st.write("Use this table as the one-to-one input list for a real ClimateBERT run. The `record_id` must be preserved in the output.")
    batch_cols = ["record_id", "company", "prompt", "model", "language", "tone_pred", "text"]
    st.dataframe(silver[batch_cols], use_container_width=True, height=560)
    st.download_button(
        "Download ClimateBERT batch input CSV",
        silver[batch_cols].to_csv(index=False).encode("utf-8"),
        file_name="climatebert_332_record_batch_input.csv",
        mime="text/csv",
    )

with tabs[1]:
    st.subheader("Current Proxy ClimateBERT Batch")
    st.write("This uses existing `labels` in `esg_records.json` as a weak ClimateBERT-style proxy. It is not equivalent to running ClimateBERT over every text.")
    if proxy.empty:
        st.warning("No proxy agreement records found.")
    else:
        summary = agreement_summary(proxy, "has_climate_commitment")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Records", f"{summary['n']:,}")
        c2.metric("Agreement", f"{summary['percent_agreement']:.3f}")
        c3.metric("Cohen kappa", f"{summary['cohen_kappa']:.3f}")
        c4.metric("Climate commitment rate", f"{summary['climate_commitment_rate']:.3f}")

        conf = (
            proxy.assign(tone_commitment=proxy["tone_pred"].astype(str).eq("commitment"))
            .groupby(["tone_commitment", "has_climate_commitment"])
            .size()
            .reset_index(name="count")
        )
        heat = (
            alt.Chart(conf)
            .mark_rect()
            .encode(
                x=alt.X("has_climate_commitment:N", title="Proxy climate-commitment"),
                y=alt.Y("tone_commitment:N", title="LLM tone is commitment"),
                color=alt.Color("count:Q", scale=alt.Scale(scheme="tealblues")),
                tooltip=["tone_commitment", "has_climate_commitment", "count"],
            )
            .properties(title="Proxy Commitment Agreement", height=260)
        )
        labels = alt.Chart(conf).mark_text().encode(x="has_climate_commitment:N", y="tone_commitment:N", text="count:Q")
        st.altair_chart(heat + labels, use_container_width=True)
        st.dataframe(proxy, use_container_width=True, height=420)

with tabs[2]:
    st.subheader("Import Real ClimateBERT Batch Outputs")
    st.write("Upload a CSV containing at least `record_id` and a commitment-like output column. Accepted columns include `climate_commitment`, `climate_commitment_label`, `label`, or `top_label`.")
    uploaded = st.file_uploader("Upload ClimateBERT record-level output CSV", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded).fillna("")
        if "record_id" not in df.columns:
            st.error("Uploaded CSV must include `record_id`.")
        else:
            possible = [c for c in ["climate_commitment", "climate_commitment_label", "label", "top_label"] if c in df.columns]
            if not possible:
                st.error("Could not find a commitment output column. Add one of: climate_commitment, climate_commitment_label, label, top_label.")
            else:
                label_col = st.selectbox("Commitment label column", possible)
                df["climatebert_commitment_pred"] = df[label_col].astype(str).str.lower().isin(["yes", "true", "1", "commitment", "climate-commitment", "label_1"])
                merged = silver.merge(df, on="record_id", how="left", suffixes=("", "_climatebert"))
                merged.to_csv(IMPORTED_PATH, index=False)
                st.success(f"Saved imported outputs to {IMPORTED_PATH}")
                st.dataframe(merged, use_container_width=True, height=420)

    if not imported.empty:
        st.markdown("**Saved imported output**")
        st.dataframe(imported.head(200), use_container_width=True, height=420)

with tabs[3]:
    st.subheader("Agreement With Real Imported Outputs")
    if imported.empty or "climatebert_commitment_pred" not in imported.columns:
        st.info("No imported real ClimateBERT batch output yet. Use the import tab.")
    else:
        valid = imported[imported["climatebert_commitment_pred"].astype(str).str.strip().ne("")]
        valid["climatebert_commitment_bool"] = valid["climatebert_commitment_pred"].astype(str).str.lower().isin(["true", "1", "yes"])
        summary = agreement_summary(valid, "climatebert_commitment_bool")
        c1, c2, c3 = st.columns(3)
        c1.metric("Matched records", f"{summary['n']:,}")
        c2.metric("Agreement", f"{summary['percent_agreement']:.3f}")
        c3.metric("Cohen kappa", f"{summary['cohen_kappa']:.3f}")
        st.dataframe(valid, use_container_width=True, height=520)

with tabs[4]:
    st.subheader("Export")
    st.download_button("Download proxy records", proxy.to_csv(index=False).encode("utf-8"), "climatebert_proxy_agreement_records.csv", "text/csv")
    if not imported.empty:
        st.download_button("Download imported real ClimateBERT outputs", imported.to_csv(index=False).encode("utf-8"), "climatebert_record_batch_import.csv", "text/csv")
