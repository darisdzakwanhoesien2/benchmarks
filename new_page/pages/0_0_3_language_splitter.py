import json
from pathlib import Path
import re
from datetime import datetime

import streamlit as st
from langdetect import detect, detect_langs, DetectorFactory

# Make results deterministic
DetectorFactory.seed = 0

# ---------------------
# CONFIG
# ---------------------
st.set_page_config(page_title="Language Splitter (Langdetect)", layout="wide")
st.title("🌐 Language Splitter — English / Indonesian (Langdetect)")

# ---------------------
# TEXT UTILITIES
# ---------------------
def clean_text(text: str) -> str:
    # Remove YAML frontmatter
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    return text.strip()


def split_paragraphs(text: str):
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def split_sentences(text: str):
    return re.split(r'(?<=[.!?])\s+', text)


# ---------------------
# LANGUAGE DETECTION
# ---------------------
def detect_lang(text: str):
    try:
        langs = detect_langs(text)
        best = langs[0]

        return {
            "lang": best.lang,
            "confidence": best.prob
        }
    except:
        return {"lang": "unknown", "confidence": 0.0}


# ---------------------
# SMART SPLITTER
# ---------------------
def smart_split(text: str):
    paragraphs = split_paragraphs(text)

    results = []

    for p in paragraphs:
        det = detect_lang(p)

        # If confidence is high → accept paragraph
        if det["confidence"] > 0.85:
            results.append({
                "text": p,
                "lang": det["lang"],
                "confidence": det["confidence"],
                "level": "paragraph"
            })
        else:
            # fallback → sentence-level split
            sentences = split_sentences(p)

            for s in sentences:
                s = s.strip()
                if not s:
                    continue

                det_s = detect_lang(s)

                results.append({
                    "text": s,
                    "lang": det_s["lang"],
                    "confidence": det_s["confidence"],
                    "level": "sentence"
                })

    return results


# ---------------------
# FILE LOADING
# ---------------------
DATA_ROOT = Path(__file__).resolve().parents[1] / "data"

if not DATA_ROOT.exists():
    st.error(f"Data directory not found: {DATA_ROOT}")
    st.stop()

subdirs = [p for p in sorted(DATA_ROOT.iterdir()) if p.is_dir()]

if not subdirs:
    st.error("No dataset folders found")
    st.stop()

chosen = st.sidebar.selectbox("Dataset folder", subdirs, format_func=lambda p: p.name)

md_files = list(chosen.rglob("*.md"))
st.sidebar.write(f"Found {len(md_files)} markdown files")

if not md_files:
    st.warning("No markdown files found")
    st.stop()

file_sel = st.selectbox("Select file", md_files, format_func=lambda p: p.name)


# ---------------------
# READ FILE
# ---------------------
def read_text(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except:
        return path.read_text(encoding="latin-1")


# ---------------------
# PROCESS (CACHED)
# ---------------------
@st.cache_data
def process_file(path_str):
    path = Path(path_str)
    raw = read_text(path)
    cleaned = clean_text(raw)
    return smart_split(cleaned)


# ---------------------
# RUN
# ---------------------
if file_sel:
    split_data = process_file(str(file_sel))

    # Filter EN / ID
    en_blocks = [x for x in split_data if x["lang"] == "en"]
    id_blocks = [x for x in split_data if x["lang"] == "id"]
    unknown_blocks = [x for x in split_data if x["lang"] not in ["en", "id"]]

    # ---------------------
    # SUMMARY
    # ---------------------
    st.markdown("### 📊 Summary")
    st.write(f"🇬🇧 English: {len(en_blocks)}")
    st.write(f"🇮🇩 Indonesian: {len(id_blocks)}")
    st.write(f"❓ Others: {len(unknown_blocks)}")

    # ---------------------
    # DISPLAY
    # ---------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🇮🇩 Indonesian")
        for i, b in enumerate(id_blocks):
            with st.expander(f"{b['level']} {i+1} (conf: {b['confidence']:.2f})"):
                st.write(b["text"])

    with col2:
        st.subheader("🇬🇧 English")
        for i, b in enumerate(en_blocks):
            with st.expander(f"{b['level']} {i+1} (conf: {b['confidence']:.2f})"):
                st.write(b["text"])

    # ---------------------
    # UNKNOWN
    # ---------------------
    if unknown_blocks:
        st.subheader("❓ Other Languages")
        for b in unknown_blocks:
            st.write(f"[{b['lang']}] ({b['confidence']:.2f}) → {b['text']}")

    # ---------------------
    # EXPORT
    # ---------------------
    export = {
        "file": str(file_sel),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "english": en_blocks,
        "indonesian": id_blocks,
        "others": unknown_blocks
    }

    st.download_button(
        "📥 Download JSON",
        data=json.dumps(export, ensure_ascii=False, indent=2),
        file_name=f"{file_sel.stem}_langdetect_split.json",
        mime="application/json"
    )