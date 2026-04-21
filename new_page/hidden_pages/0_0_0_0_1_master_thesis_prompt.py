import streamlit as st
from pathlib import Path
import re

import re
from pathlib import Path
import streamlit as st

# DATA_DIR = Path(__file__).parent / "data" / "master_thesis_prompt_esg_greenwashing"
DATA_DIR = Path(__file__).parents[2] / "data" / "master_thesis_prompt_esg_greenwashing"

def list_markdown_files():
    return sorted(DATA_DIR.glob("*.md"))

def strip_html_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()

def extract_title_from_file(text, fallback_name):
    # try to find "Section Title:" or first heading or filename
    m = re.search(r"Section Title:\s*(.+)", text)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"^#\s*(.+)$", text, flags=re.M)
    if m2:
        return m2.group(1).strip()
    return fallback_name

def make_latex_skeleton(title, body_text):
    # Prepend requested LaTeX section header if not already present
    return f"\\subsection{{{title}}}\n\n{body_text.strip()}\n"

def highlight_matches(text, query):
    if not query:
        return text
    # simple HTML highlight
    esc = re.escape(query)
    return re.sub(esc, lambda m: f"<mark>{m.group(0)}</mark>", text, flags=re.I)

def main():
    st.set_page_config(page_title="ESG Thesis Prompt Browser", layout="wide")
    st.sidebar.title("ESG Prompt Browser")
    files = list_markdown_files()
    names = [p.name for p in files]
    query = st.sidebar.text_input("Filter files (substring)")
    filtered = [p for p in files if (not query) or query.lower() in p.name.lower()]
    selected = st.sidebar.selectbox("Select file", filtered, format_func=lambda p: p.name)
    if not selected:
        st.warning("No files found in data folder.")
        return

    raw = selected.read_text(encoding="utf8")
    cleaned = strip_html_comments(raw)
    title = extract_title_from_file(raw, selected.stem)

    st.title(title)
    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("Markdown Preview")
        search_in_file = st.text_input("Highlight matches in preview", key="preview_search")
        preview_text = highlight_matches(cleaned, search_in_file)
        st.markdown(preview_text, unsafe_allow_html=True)

        st.download_button("Download original .md", data=raw, file_name=selected.name, mime="text/markdown")
    with col2:
        st.subheader("LaTeX Editor & Export")
        latex_prefill = make_latex_skeleton(title, cleaned)
        latex_text = st.text_area("LaTeX-ready text (editable)", value=latex_prefill, height=400)
        st.download_button("Download .tex", data=latex_text, file_name=f"{selected.stem}.tex", mime="text/plain")
        st.info("You can edit the LaTeX text before download. This skeleton wraps the body with a \\subsection{} header.")

    st.markdown("---")
    st.caption(f"Source file: {selected}")

# if __name__ == "__main__":
#     main()

# DATA_DIR = Path(__file__).parents[3] / "data" / "master_thesis_prompt_esg_greenwashing"

def strip_html_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()

def main():
    st.title("ESG Prompt - Quick Viewer")
    md_files = sorted(DATA_DIR.glob("*.md"))
    if not md_files:
        st.warning("No markdown files found.")
        return
    choice = st.selectbox("Choose a prompt file", md_files, format_func=lambda p: p.name)
    raw = choice.read_text(encoding="utf8")
    cleaned = strip_html_comments(raw)
    st.subheader(choice.name)
    st.markdown(cleaned)

    if st.button("Copy LaTeX skeleton to clipboard"):
        # prepare a minimal LaTeX skeleton
        title_line = choice.stem.replace("_", " ").title()
        latex = f"\\subsection{{{title_line}}}\n\n{cleaned}"
        st.write("LaTeX prepared below — copy manually (Streamlit cannot access clipboard reliably).")
        st.code(latex)

if __name__ == "__main__":
    main()