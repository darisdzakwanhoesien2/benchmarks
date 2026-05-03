import streamlit as st
import pandas as pd
from utils.data_loader import load_and_parse
from utils.aspect_clustering import cluster_aspect

st.set_page_config(layout="wide")
st.title("🔍 Aspect Mapping — Before vs After")

df = load_and_parse()

if df.empty or "aspect" not in df.columns:
    st.warning("No aspect data available.")
    st.stop()

df = df.copy()
df["aspect_cluster"] = df["aspect"].apply(cluster_aspect)

comparison = (
    df[["aspect", "aspect_cluster"]]
    .value_counts()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)


# Dropdown for aspect cluster selection
aspect_clusters = ["All"] + sorted(df["aspect_cluster"].unique())
selected_cluster = st.selectbox("Select Aspect Cluster", aspect_clusters)

# Filter data based on selection
if selected_cluster != "All":
    filtered_df = comparison[comparison["aspect_cluster"] == selected_cluster]
else:
    filtered_df = comparison

# Show filtered table
st.dataframe(filtered_df, use_container_width=True)

# Show bar chart for visualization
if not filtered_df.empty:
    # sort by 'count' descending and use 'aspect' as index for plotting
    plot_series = (
        filtered_df.sort_values("count", ascending=False)
        .set_index("aspect")["count"]
    )
    st.bar_chart(
        plot_series,
        use_container_width=True
    )
else:
    st.info("No data for selected cluster.")


# import streamlit as st
# import pandas as pd
# from utils.aspect_clustering import cluster_aspect

# st.set_page_config(layout="wide")
# st.title("🔍 Aspect Mapping — Before vs After")

# df = st.session_state["filtered_df"].copy()

# df["aspect_cluster"] = df["aspect"].apply(cluster_aspect)

# comparison = (
#     df[["aspect", "aspect_cluster"]]
#     .value_counts()
#     .reset_index(name="count")
#     .sort_values("count", ascending=False)
# )

# st.dataframe(
#     comparison,
#     use_container_width=True
# )
