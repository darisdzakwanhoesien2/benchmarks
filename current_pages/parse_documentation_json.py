import streamlit as st
import json

st.title("Documentation JSON Table Viewer")

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
        st.dataframe(data)
    except Exception as e:
        st.error(f"Failed to parse JSON: {e}")
else:
    st.warning("No JSON array found in documentation.md.")
