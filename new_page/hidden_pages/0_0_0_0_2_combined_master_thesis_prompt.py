import streamlit as st
from pathlib import Path
import re

import re
from pathlib import Path
import streamlit as st

DATA_DIR = Path(__file__).parents[2] / "data" / "master_thesis_prompt_esg_greenwashing"

def list_markdown_files():
    return sorted(DATA_DIR.glob("*.md"))

def strip_html_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()

def extract_title_from_file(text, fallback_name):
    m = re.search(r"Section Title:\s*(.+)", text)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"^#\s*(.+)$", text, flags=re.M)
    if m2:
        return m2.group(1).strip()
    return fallback_name

def make_latex_skeleton(title, body_text):
    return f"\\subsection{{{title}}}\n\n{body_text.strip()}\n"

def highlight_matches(text, query):
    if not query:
        return text
    esc = re.escape(query)
    return re.sub(esc, lambda m: f"<mark>{m.group(0)}</mark>", text, flags=re.I)

st.set_page_config(page_title="ESG Prompts — Combined Viewer", layout="wide")

def main():
    st.sidebar.title("Controls")
    files = list_markdown_files()
    if not files:
        st.warning("No markdown files found in data folder.")
        return

    filename_query = st.sidebar.text_input("Filter filenames (substring)")
    content_query = st.sidebar.text_input("Filter content (substring)")
    show_raw = st.sidebar.checkbox("Show raw markdown preview", value=True)
    show_latex_area = st.sidebar.checkbox("Show per-file LaTeX editor", value=True)
    select_all = st.sidebar.button("Select all files")
    st.sidebar.markdown("Selected files will be combined for export.")

    # Build list of file entries with checkboxes
    st.title("Combined ESG Prompt Viewer")
    st.write("Browse all prompts below. Use the sidebar to filter and export a combined LaTeX/Markdown file.")

    selected_map = {}
    latex_fragments = {}
    cleaned_fragments = {}

    cols = st.columns([3,1])
    with cols[1]:
        st.markdown("### Export")
        if st.button("Generate combined export"):
            pass  # placeholder to keep UI consistent

    for p in files:
        if filename_query and filename_query.lower() not in p.name.lower():
            continue
        raw = p.read_text(encoding="utf8")
        cleaned = strip_html_comments(raw)
        if content_query and content_query.lower() not in cleaned.lower():
            continue

        title = extract_title_from_file(raw, p.stem)
        with st.expander(f"{p.name} — {title}", expanded=False):
            if show_raw:
                preview = highlight_matches(cleaned, content_query)
                st.markdown(preview, unsafe_allow_html=True)
            # per-file selection
            key_select = f"select_{p.stem}"
            selected = st.checkbox("Include in combined export", value=True, key=key_select)
            selected_map[p] = selected

            if show_latex_area:
                key_area = f"latex_{p.stem}"
                latex_prefill = make_latex_skeleton(title, cleaned)
                latex_text = st.text_area(f"LaTeX for {p.name}", value=latex_prefill, height=250, key=key_area)
            else:
                latex_text = make_latex_skeleton(title, cleaned)

            # store fragments for combined export
            latex_fragments[p] = latex_text
            cleaned_fragments[p] = cleaned

    # Combine selected fragments
    combined_latex = ""
    combined_md = ""
    include_count = 0
    ordered_files = [p for p in files if p in latex_fragments]
    for p in ordered_files:
        if selected_map.get(p, True):
            include_count += 1
            combined_latex += latex_fragments[p].rstrip() + "\n\n"
            combined_md += cleaned_fragments[p].rstrip() + "\n\n"

    st.sidebar.markdown(f"Files included: **{include_count}**")

    if include_count == 0:
        st.info("No files selected for combined export.")
    else:
        st.subheader("Combined Export Preview")
        st.markdown("You can download the combined LaTeX (.tex) and combined Markdown (.md) files.")
        st.code(combined_latex[:1000] + ("...\n\n(truncated)" if len(combined_latex) > 1000 else ""), language="text")
        st.download_button("Download combined .tex", data=combined_latex, file_name="combined_prompts.tex", mime="text/plain")
        st.download_button("Download combined .md", data=combined_md, file_name="combined_prompts.md", mime="text/markdown")

if __name__ == "__main__":
    main()