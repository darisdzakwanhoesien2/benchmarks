import streamlit as st
import pandas as pd
import json
import subprocess
import sys
from pathlib import Path

st.set_page_config(layout="wide")
st.title("🔗 Aspect Clusters Explorer")

BASE = Path(__file__).resolve().parents[1]
JSON_PATH = BASE / "data" / "aspect_cluster.json"

if not JSON_PATH.exists():
    st.warning("aspect_cluster.json not found. Run the clustering script first:")
    st.code(f"python3 {BASE / 'scripts' / 'create_aspect_cluster_json.py'}")
    st.stop()

# --- CHANGED: robust JSON load with helpful error + regenerate button ---
try:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
except json.decoder.JSONDecodeError as e:
    st.error(f"Failed to parse JSON: {e}")
    st.subheader("Preview of the JSON file (first 4000 chars)")
    txt = JSON_PATH.read_text(encoding="utf-8", errors="replace")
    st.code(txt[:4000])
    if st.button("Regenerate aspect_cluster.json from CSV"):
        script = BASE / "scripts" / "create_aspect_cluster_json.py"
        if script.exists():
            cmd = [sys.executable, str(script)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            st.subheader("Regeneration output")
            st.text(proc.stdout or "(no stdout)")
            if proc.stderr:
                st.text(proc.stderr)
            if proc.returncode == 0 and JSON_PATH.exists():
                st.success("Regenerated JSON successfully — reloading")
                try:
                    with open(JSON_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception as ee:
                    st.error(f"Still cannot parse regenerated JSON: {ee}")
                    st.stop()
            else:
                st.error("Regeneration failed — inspect output above or fix JSON manually.")
                st.stop()
        else:
            st.error(f"Regeneration script not found: {script}")
            st.stop()
    else:
        st.stop()
except Exception as e:
    st.error(f"Error loading JSON file: {e}")
    st.stop()
clusters = data.get("clusters", {})
if not clusters:
    st.info("No clusters found in JSON.")
    st.stop()

# summary table
summary = []
total_rows = 0
for k, v in clusters.items():
    total_rows += int(v.get("total_count", 0))
    summary.append({"cluster": k, "total_count": v.get("total_count", 0), "members": len(v.get("members", []))})
summary_df = pd.DataFrame(sorted(summary, key=lambda r: -r["total_count"]))

col1, col2 = st.columns([1, 3])
col1.metric("Clusters", len(clusters))
col2.metric("Total aspect mentions (sum counts)", total_rows)

st.subheader("Cluster summary")
st.dataframe(summary_df, use_container_width=True)

selected = st.selectbox("Select cluster", ["All"] + summary_df["cluster"].tolist())
if selected == "All":
    st.subheader("All clusters — top members")
    # show top member per cluster
    rows = []
    for k, v in clusters.items():
        top = v["members"][:10]
        for m in top:
            rows.append({"cluster": k, "aspect": m["aspect"], "count": m["count"]})
    all_df = pd.DataFrame(rows).sort_values(["cluster", "count"], ascending=[True, False])
    st.dataframe(all_df, use_container_width=True)
    st.download_button("Download clusters JSON", json.dumps(data, ensure_ascii=False, indent=2), "aspect_cluster.json")
else:
    meta = clusters[selected]
    members = pd.DataFrame(meta.get("members", []))
    st.subheader(f"Cluster: {selected} — total_count={meta.get('total_count')}, members={len(members)}")
    if members.empty:
        st.info("No members")
    else:
        top_n = st.slider("Top N members to show", 5, 200, 50)
        display_df = members.head(top_n).reset_index(drop=True)

        # --- CHANGED: sort by count descending before plotting and showing table ---
        display_df = display_df.sort_values("count", ascending=False).reset_index(drop=True)

        # Option A — simple st.bar_chart (respects index order if we set index)
        st.bar_chart(display_df.set_index("aspect")["count"])

        # Option B — more control / nicer labels with Plotly (uncomment to use)
        # import plotly.express as px
        # fig = px.bar(
        #     display_df,
        #     x="aspect",
        #     y="count",
        #     title=f"{selected} — Top {len(display_df)} members (sorted)",
        #     category_orders={"aspect": display_df["aspect"].tolist()}
        # )
        # fig.update_layout(xaxis_tickangle=-45)
        # st.plotly_chart(fig, use_container_width=True)

        st.dataframe(display_df, use_container_width=True)
        csv = display_df.to_csv(index=False)
        st.download_button("Download CSV for cluster", csv, f"{selected}_members.csv")