import streamlit as st
from _page_explanations import add_page_explanation, add_section_explanation
import json

st.title("Documentation JSON Table Viewer")
add_page_explanation(__file__)

# Read the documentation.md file
with open("documentation.md", "r") as f:
    content = f.read()

# Find the first JSON array in the file
start = content.find("[")
end = content.find("]", start)

if start != -1 and end != -1:
    json_str = content[start:end+1]
    try:
        data = json.loads(json_str)
        st.subheader("Parsed JSON Table")
        add_section_explanation("Parsed JSON Table")
        st.dataframe(data)
    except Exception as e:
        st.error(f"Failed to parse JSON: {e}")
else:
    st.warning("No JSON array found in documentation.md.")
