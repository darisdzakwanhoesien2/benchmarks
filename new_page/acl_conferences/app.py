"""
Streamlit App: Resource Mapping & Dataset Sufficiency Analysis
for "Multimodal Fact-Checking of Sustainability Reports against External Media"
"""

import streamlit as st
import re
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_bibtex(path: str) -> list[dict]:
    """Parse a .bib file into a list of entry dicts."""
    with open(path, "r") as f:
        text = f.read()

    entries = []
    # split on @entry_type{key,
    pattern = re.compile(r"@(\w+)\{([^,]+),\s*\n", re.MULTILINE)
    parts = pattern.split(text)

    # parts[0] = pre-text, parts[1]=type1, parts[2]=key1, parts[3]=body1, ...
    for i in range(1, len(parts), 3):
        entry_type = parts[i]
        entry_key = parts[i + 1]
        body = parts[i + 2]
        # find the closing brace (rough)
        brace_count = 0
        end = 0
        for j, ch in enumerate(body):
            if ch == "{":
                brace_count += 1
            elif ch == "}":
                brace_count -= 1
                if brace_count == 0:
                    end = j
                    break
        body = body[:end]

        entry = {"type": entry_type, "key": entry_key.strip()}
        # extract fields: field = {value},
        field_pattern = re.compile(r"(\w+)\s*=\s*\{(.*?)\},?\s*$", re.MULTILINE | re.DOTALL)
        for m in field_pattern.finditer(body):
            field_name = m.group(1).strip().lower()
            field_value = m.group(2).strip()
            # collapse whitespace
            field_value = re.sub(r"\s+", " ", field_value)
            entry[field_name] = field_value
        entries.append(entry)

    return entries


def extract_parencite_keys(text: str) -> list[str]:
    r"""Extract unique citation keys from \parencite{...} commands."""
    pattern = re.compile(r"\\parencite(?:\[\w*\])?\{([^}]+)\}")
    seen = set()
    keys = []
    for m in pattern.finditer(text):
        for k in m.group(1).split(","):
            k = k.strip()
            if k and k not in seen:
                seen.add(k)
                keys.append(k)
    return keys


def parse_latex_sections(text: str) -> list[dict]:
    """Extract top-level sections from a LaTeX document."""
    # Match numbered sections like "1. Introduction" or "2. Related Work"
    # Section boundaries are `\begin{center}\rule{...}` dividers in the LaTeX source.
    # DOTALL makes (.*?) consume newlines, so the lookahead must NOT start with \n.
    # Braces are unescaped — regex treats {c as literal (not a valid quantifier).
    pattern = re.compile(
        r"(\d+)\.\s+(.+?)\s*\n(.*?)(?=\\begin{center}\\rule|$)",
        re.DOTALL,
    )
    sections = []
    for m in pattern.finditer(text):
        num = m.group(1)
        title = m.group(2).strip()
        body = m.group(3).strip()
        # extract item text from \item directives
        items = re.findall(r"\\item\s*\n?\s*(.*?)(?=\\item|\n\\end\{itemize\}|\n\\begin\{itemize\}|\Z)", body, re.DOTALL)
        items_clean = [re.sub(r"\s+", " ", i).strip() for i in items if i.strip()]
        # extract citation keys from body
        cites = extract_parencite_keys(body)
        sections.append({
            "number": int(num),
            "title": title,
            "items": items_clean[:10],  # limit for display
            "citations": list(set(cites)),
        })
    return sections

def parse_numerical_targets(text: str) -> list[dict]:
    """Parse the numerical targets table from notes.tex."""
    targets = []
    # Data format:  \textbf{Category} & Component & \textbf{Target} & Source \\ \hline
    row_pattern = re.compile(
        r"\\textbf\{([^}]+)\}\s*&\s*([^&]+?)\s*&\s*\\textbf\{([^}]+)\}\s*&\s*(.*?)\s*\\\\",
        re.DOTALL,
    )
    for m in row_pattern.finditer(text):
        category = m.group(1).strip()
        component = m.group(2).strip()
        target = m.group(3).strip()
        source = m.group(4).strip()
        # clean up source - remove \parencite{...}
        source = re.sub(r"\\parencite\{([^}]+)\}", r"\1", source).strip()
        targets.append({
            "category": category,
            "component": component,
            "target": target,
            "source": source,
        })
    return targets


# ---------------------------------------------------------------------------
# Load all resources
# ---------------------------------------------------------------------------

def get_files_hash():
    """Get a hash/timestamp of all relevant files to invalidate cache."""
    relevant_extensions = ('.tex', '.bib', '.md')
    mtimes = []
    for f in os.listdir(BASE_DIR):
        if f.endswith(relevant_extensions):
            mtimes.append(os.path.getmtime(os.path.join(BASE_DIR, f)))
    return max(mtimes) if mtimes else 0

@st.cache_data
def load_resources(hash_val):
    resources = {}
    
    # Discovery
    all_files = os.listdir(BASE_DIR)
    tex_files = [f for f in all_files if f.endswith(".tex")]
    bib_files = [f for f in all_files if f.endswith(".bib")]
    md_files = [f for f in all_files if f.endswith(".md")]
    
    resources["files"] = {
        "tex": tex_files,
        "bib": bib_files,
        "md": md_files,
        "all": tex_files + bib_files + md_files
    }

    # Bib files
    resources["bib_data"] = {}
    for f in bib_files:
        resources["bib_data"][f] = parse_bibtex(os.path.join(BASE_DIR, f))

    # LaTeX files
    resources["tex_content"] = {}
    for f in tex_files:
        with open(os.path.join(BASE_DIR, f), "r") as f_in:
            resources["tex_content"][f] = f_in.read()

    # MD files
    resources["md_content"] = {}
    for f in md_files:
        with open(os.path.join(BASE_DIR, f), "r") as f_in:
            resources["md_content"][f] = f_in.read()

    # Parse sections from paper.tex if it exists
    if "paper.tex" in resources["tex_content"]:
        resources["paper_sections"] = parse_latex_sections(resources["tex_content"]["paper.tex"])
    else:
        resources["paper_sections"] = []

    # Parse numerical targets from notes.tex if it exists
    if "notes.tex" in resources["tex_content"]:
        resources["numerical_targets"] = parse_numerical_targets(resources["tex_content"]["notes.tex"])
    else:
        resources["numerical_targets"] = []

    # Build a unified reference lookup from all bib files
    ref_lookup = {}
    for bib_list in resources["bib_data"].values():
        for entry in bib_list:
            key = entry["key"]
            if key not in ref_lookup:
                ref_lookup[key] = entry

    resources["ref_lookup"] = ref_lookup

    # Map which files cite which references
    resources["citations"] = {}
    for name, content in resources["tex_content"].items():
        resources["citations"][name] = extract_parencite_keys(content)

    return resources


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="ACL Conferences — Resource Mapper",
    page_icon="📊",
    layout="wide",
)

st.title("📊 ACL Conferences — Resource Mapping & Dataset Sufficiency")
st.caption(
    "Analyzing the research project: *Beyond Impression Management: "
    "A Multimodal Framework for Fact-Checking Sustainability Reports "
    "via External News and Social Media*"
)

# Load with hash to ensure "live" data counting
resources = load_resources(get_files_hash())
ref_lookup = resources["ref_lookup"]

# ===========================================================================
# Sidebar — source-file overview
# ===========================================================================

paper_citations = set(resources["citations"].get("paper.tex", []))
notes_citations = set(resources["citations"].get("notes.tex", []))

# Extract key metrics for "Original Database" display
news_target = "N/A"
report_target = "N/A"
temporal_range = "N/A"
for t in resources["numerical_targets"]:
    comp = t["component"].lower()
    if "total news corpus" in comp:
        news_target = t["target"]
    elif "gold standard reports" in comp:
        report_target = t["target"]
    elif "incident temporal range" in comp:
        temporal_range = t["target"]

with st.sidebar:
    st.header("📂 Project Database")
    st.markdown(f"**Primary Path:** `{BASE_DIR}`")
    
    st.metric("Total News Corpus", news_target)
    st.metric("Gold Standard Reports", report_target)
    st.metric("Temporal Range", temporal_range)

    st.divider()
    st.header("📄 Source Files")

    for ftype, icon in [("tex", "📄"), ("bib", "📚"), ("md", "📝")]:
        for fname in resources["files"][ftype]:
            desc = ""
            if ftype == "bib":
                desc = f"{len(resources['bib_data'][fname])} entries"
            elif ftype == "md":
                content = resources["md_content"][fname].strip().lower()
                if content == "placeholder":
                    desc = "⚠️ Placeholder"
                else:
                    desc = "✅ Populated"
            
            st.caption(f"**{fname}** {icon} {desc}")
            st.code(os.path.join(BASE_DIR, fname), language=None)

    st.divider()

    st.subheader("📊 Quick Stats")
    c_a, c_b = st.columns(2)
    c_a.metric("Total .bib entries", len(ref_lookup))
    c_b.metric("Unique citations", len(paper_citations | notes_citations))

    c_c, c_d = st.columns(2)
    c_c.metric("Paper sections", len(resources["paper_sections"]))
    c_d.metric("Numerical targets", len(resources["numerical_targets"]))

    # Citation overlap mini-chart
    shared_ct = len(paper_citations & notes_citations)
    st.caption(
        f"**Citation overlap:** {shared_ct} shared / "
        f"{len(paper_citations)} in paper / {len(notes_citations)} in notes"
    )

    st.caption("---")
    st.caption(f"**{len(resources['files']['all'])} source files** loaded from the project directory.")
    
    if st.button("🔄 Refresh Live Data"):
        st.cache_data.clear()
        st.rerun()
    
    import datetime
    st.caption(f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")

# ===========================================================================
# TAB: Resource Inventory
# ===========================================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📁 Resource Inventory",
    "📄 Paper Structure",
    "🔬 Methodology Pipeline",
    "📊 Dataset Requirements",
    "✅ Sufficiency Analysis",
    "📚 References",
])

with tab1:
    st.header("File Inventory")

    inventory_data = []
    for ftype in ["tex", "bib", "md"]:
        for fname in resources["files"][ftype]:
            status = "✅ Populated"
            desc = ""
            
            if ftype == "md":
                if resources["md_content"][fname].strip().lower() == "placeholder":
                    status = "⚠️ Placeholder"
                    desc = "Contains only the word \"placeholder\". No substantive content."
            
            if not desc:
                if fname == "paper.tex":
                    desc = "Full research paper in LaTeX. Covers Introduction, Methodology, Results, etc."
                elif fname == "notes.tex":
                    desc = "Research notes analyzing gaps and dataset size recommendations."
                elif ftype == "bib":
                    desc = f"{len(resources['bib_data'][fname])} references found in this file."
                else:
                    desc = f"{ftype.upper()} file discovered in directory."

            inventory_data.append({
                "File": fname,
                "Type": ftype.upper(),
                "Status": status,
                "Description": desc,
            })

    st.dataframe(inventory_data, use_container_width=True, hide_index=True)

    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Files", len(resources["files"]["all"]))
    
    paper_bib_count = len(resources["bib_data"].get("paper.bib", []))
    notes_bib_count = len(resources["bib_data"].get("notes.bib", []))
    
    col2.metric("Entries (paper.bib)", paper_bib_count)
    col3.metric("Entries (notes.bib)", notes_bib_count)
    col4.metric("Unique References", len(ref_lookup))

    if any(d["Status"] == "⚠️ Placeholder" for d in inventory_data):
        st.info(
            "Some files are placeholders — they contain no usable research content. "
            "Please ensure all core .tex and .bib files are populated."
        )


# ===========================================================================
# TAB: Paper Structure
# ===========================================================================

with tab2:
    st.header("Paper Structure — Extracted Sections")
    st.caption("Sections parsed from `paper.tex` with their citation keys.")

    sections = resources["paper_sections"]
    for sec in sections:
        with st.expander(f"**{sec['number']}. {sec['title']}**  —  {len(sec['citations'])} citations"):
            st.markdown(f"**Citations:** `{', '.join(sec['citations'])}`")
            if sec["items"]:
                st.markdown("**Key points:**")
                for item in sec["items"][:8]:
                    # clean LaTeX
                    clean = re.sub(r"\\textbf\{([^}]+)\}", r"**\1**", item)
                    clean = re.sub(r"\\parencite(?:\[\w*\])?\{([^}]+)\}", r"[`\1`]", clean)
                    clean = re.sub(r"\\textit\{([^}]+)\}", r"*\1*", clean)
                    clean = re.sub(r"\\%.*", "", clean)
                    st.markdown(f"- {clean}")

    st.divider()
    st.subheader("Citation Coverage by Section")
    coverage_data = [
        {"Section": f"{s['number']}. {s['title']}", "Citations": len(s["citations"])}
        for s in sections
    ]
    st.bar_chart(
        {d["Section"]: d["Citations"] for d in coverage_data},
        x_label="Section",
        y_label="Unique Citations",
    )


# ===========================================================================
# TAB: Methodology Pipeline
# ===========================================================================

with tab3:
    st.header("Methodology Pipeline")
    st.caption("The 4-stage fact-checking pipeline described in the paper.")

    stages = [
        {
            "stage": "Stage 1: Internal Claim Extraction",
            "description": "Multimodal RAG retrieves both textual and visual evidence from internal sustainability reports, extracting verifiable objectives from charts, tables, and text.",
            "technique": "Multimodal Retrieval-Augmented Generation",
            "reference": "mohammad_mahdavi_619c09a8",
            "icon": "📥",
        },
        {
            "stage": "Stage 2: External Evidence Textualization",
            "description": "The MAFT framework converts external multimodal content (news videos, images, social media audio) into text-based representations using web APIs and LLMs.",
            "technique": "MAFT — Multimodal Automated Fact-Checking via Textualization",
            "reference": "kazuya_kakizaki_4193ad80",
            "icon": "🔄",
        },
        {
            "stage": "Stage 3: Sustainability Event Detection",
            "description": "Knowledge-driven neural models with multi-tasking sequence labeling detect organizational violations in news/social media aligned with GRI standards.",
            "technique": "Knowledge-driven neural models + sequence labeling",
            "reference": "abir_naskar_17efeb7b",
            "icon": "🔍",
        },
        {
            "stage": "Stage 4: Verification & Verdict Generation",
            "description": "Visual forensics detect synthetic/out-of-context media. Justification-centric verdicts are generated with traceable references (Compliant/Non-Compliant).",
            "technique": "Visual forensics + Knowledge Graphs + Justification-centric verdicts",
            "reference": "kaoukis__georgios_35bab107",
            "icon": "✅",
        },
    ]

    for i, stage in enumerate(stages):
        ref_entry = ref_lookup.get(stage["reference"], {})
        ref_title = ref_entry.get("title", stage["reference"])
        ref_authors = ref_entry.get("author", "N/A")
        ref_year = ref_entry.get("year", "N/A")

        col_icon, col_body = st.columns([0.05, 0.95])
        with col_icon:
            st.markdown(f"## {stage['icon']}")
        with col_body:
            st.markdown(f"### {stage['stage']}")
            st.markdown(stage["description"])
            st.caption(
                f"**Technique:** {stage['technique']}  |  "
                f"**Reference:** *{ref_title}* ({ref_authors}, {ref_year})"
            )

        if i < len(stages) - 1:
            st.markdown("<div style='text-align:center;font-size:24px;margin:-12px 0'>⬇️</div>", unsafe_allow_html=True)

# ===========================================================================
# TAB: Dataset Requirements
# ===========================================================================

with tab4:
    st.header("Dataset Requirements")
    st.caption("Minimum numerical targets recommended in `notes.tex` for a publication-grade study.")

    targets = resources["numerical_targets"]
    if targets:
        st.table(
            [{
                "Category": t["category"],
                "Component": t["component"],
                "Minimum Target": t["target"],
                "Source Benchmark": f"`{t['source']}`",
            } for t in targets]
        )

    st.divider()
    st.subheader("Detailed Breakdown")

    col_a, col_b = st.columns(2)

    def get_target(component):
        for t in targets:
            if component.lower() in t["component"].lower():
                return t["target"]
        return "N/A"

    with col_a:
        st.markdown("### Internal Data")
        st.markdown(f"""
        - **Gold Standard Reports:** {get_target('Gold Standard')} for evaluation and fine-tuning
          (Beck et al., 2025)
        - **Multi-Year Scope:** {get_target('Multi-year')} via the NFIVI dataset
          (Li et al., 2026)
        - **Modality:** Visual rhetoric analysis (charts, tables, images) + text
        - **Source Benchmark:** NFIVI dataset covering Chinese listed companies
        """)

    with col_b:
        st.markdown("### External Data")
        st.markdown(f"""
        - **News Corpus:** {get_target('Total News')} minimum (ESG-FTSE, Pavlova et al., 2024)
        - **Per-Entity Coverage:** {get_target('Coverage per Entity')} dedicated articles per company
          (Consoli et al., 2021)
        - **Deep Monitoring:** {get_target('High-Depth')} most relevant news items/year/company
          (Pikatza-Gorrotxategi et al., 2024)
        - **Temporal Range:** {get_target('Incident Temporal')} (aligns with incident corpora)
        - **Additional:** MMESGBench multimodal benchmark (Zhang et al., 2025)
        """)


# ===========================================================================
# TAB: Sufficiency Analysis
# ===========================================================================

with tab5:
    st.header("Dataset Sufficiency Analysis")

    st.markdown("""
    Below we assess whether the prescribed dataset sizes (from `notes.tex`) are
    **sufficient** for the research goals of multimodal fact-checking of
    sustainability reports against external news and social media.
    """)

    # --- Analysis sections ---
    analyses = [
        {
            "title": f"Internal Data: {get_target('Gold Standard')}",
            "verdict": "✅ Sufficient",
            "verdict_color": "green",
            "body": f"""
            **Why sufficient:** {get_target('Gold Standard')} is a benchmarked figure from Beck et al. (2025
            *Scientific Data*), derived from expert-reviewed annotations. This sample
            size is adequate for:
            - Training and fine-tuning multimodal extraction models
            - Conducting inter-annotator agreement studies
            - Producing statistically meaningful Precision/Recall/F1 scores

            **Caveat:** The NFIVI dataset covers Chinese listed companies
            ({get_target('Multi-year')}). If the framework targets global companies (US, EU), the
            dataset must be supplemented with reports from other regulatory regimes
            (e.g., CSRD in Europe, SEC climate rules in the US). **Cross-region
            generalizability is not yet addressed.**
            """,
        },
        {
            "title": f"External Data: {get_target('Total News')}",
            "verdict": "✅ Sufficient",
            "verdict_color": "green",
            "body": f"""
            **Why sufficient:** Pavlova et al. (2024) demonstrated that {get_target('Total News')}
            articles over 3 years can accurately predict ESG credentials. This
            volume handles the "small-data" characteristic of the ESG domain.

            **Caveat:** The ESG-FTSE corpus is limited to specific news sources
            and a fixed timeframe. Real-world fact-checking requires **continuous
            ingestion** of live news streams, not a static corpus. The framework
            should incorporate web API-based live retrieval (MAFT's approach) to
            stay current.
            """,
        },
        {
            "title": f"Per-Entity Coverage: {get_target('Coverage per Entity')}",
            "verdict": "⚠️ Borderline",
            "verdict_color": "orange",
            "body": f"""
            **Why borderline:** {get_target('Coverage per Entity')} is a reasonable minimum
            to avoid "noise" (Consoli et al., 2021), but for nuanced fact-checking
            that spans multiple ESG dimensions (environmental, social, governance),
            this may be thin.

            - If {get_target('Coverage per Entity')} articles cover mostly one dimension (e.g., environmental), the
              other two dimensions will have insufficient evidence.
            - For companies with sparse media coverage, {get_target('Coverage per Entity')} may be
              unattainable, forcing exclusion and reducing sample diversity.

            **Recommendation:** Increase to 20–30 articles per company, with
            stratified sampling across ESG pillars.
            """,
        },
        {
            "title": f"Deep Monitoring: {get_target('High-Depth')}",
            "verdict": "⚠️ Borderline",
            "verdict_color": "orange",
            "body": f"""
            **Why borderline:** {get_target('High-Depth')} (~1.4 per day)
            is sufficient for regular monitoring but may miss:

            - **High-frequency social media signals** (Twitter/X, Reddit), which
              produce orders of magnitude more content.
            - **Breaking news events** that generate hundreds of articles in hours.
            - **Non-English sources**, which are critical for global companies.

            The {get_target('High-Depth')} threshold was validated for reputation analysis
            (Pikatza-Gorrotxategi et al., 2024) but the paper's stated goal
            includes **social media monitoring**, which requires much higher
            throughput.
            """,
        },
        {
            "title": f"Temporal Range: {get_target('Incident Temporal')}",
            "verdict": "⚠️ Insufficient for Current Claims",
            "verdict_color": "red",
            "body": f"""
            **Why insufficient:** The incident corpora (Naskar et al., 2024) stop at
            {get_target('Incident Temporal').split('–')[-1] if '–' in get_target('Incident Temporal') else '2022'}. For a paper to be publishable in 2026, using data that ends in
            {get_target('Incident Temporal').split('–')[-1] if '–' in get_target('Incident Temporal') else '2022'} creates a **4-year information gap**.

            - Major ESG events since {get_target('Incident Temporal').split('–')[-1] if '–' in get_target('Incident Temporal') else '2022'} (e.g., EU CSRD implementation, SEC
              climate disclosure rules, post-COVID supply chain disruptions) are
              excluded.
            - The framework claims to do "real-time monitoring of live news streams"
              — but the training data ends 4 years ago.
            - Social media platforms and discourse patterns have evolved
              significantly since {get_target('Incident Temporal').split('–')[-1] if '–' in get_target('Incident Temporal') else '2022'}.

            **Recommendation:** Extend the incident corpus to at least 2024, and
            ideally include 2025 data through web API-based collection.
            """,
        },
        {
            "title": "Multimodal Benchmark: MMESGBench",
            "verdict": "✅ Sufficient (as a benchmark)",
            "verdict_color": "green",
            "body": """
            **Why sufficient:** MMESGBench (Zhang et al., 2025) provides a
            standardized evaluation framework for layout-aware document pages,
            including tables and figures. This is directly relevant.

            **Caveat:** The benchmark is for *evaluation only*, not *training*.
            The project still needs its own training/validation splits from the
            prescribed datasets.
            """,
        },
        {
            "title": "Social Media Data",
            "verdict": "❌ Missing / Under-specified",
            "verdict_color": "red",
            "body": """
            **Why missing:** The paper title explicitly mentions "External News
            and Social Media" as verification sources, yet:

            - The prescribed datasets (ESG-FTSE, incident corpora) are
              **news-only**. No social media dataset is specified.
            - No minimum volume, platform coverage, or annotation strategy is
              proposed for social media content.
            - Social media fact-checking requires different methodologies
              (virality analysis, stance detection, platform-specific features).

            **This is the most significant gap.** Without a concrete social media
            data plan, the framework cannot deliver on its stated scope.
            """,
        },
        {
            "title": "Cross-Modality Alignment",
            "verdict": "⚠️ Risk",
            "verdict_color": "orange",
            "body": """
            The framework requires aligning internal visual claims (charts in
            reports) with external textual evidence (news articles). This
            cross-modal alignment is technically challenging:

            - No alignment dataset is prescribed (pairs of report-charts ↔ news-articles).
            - The MAFT framework handles textualization of external content, but
              the reverse direction (aligning internal charts to external text)
              lacks a specified dataset.
            - Without aligned ground-truth pairs, the verification stage (Stage 4)
              will be difficult to evaluate rigorously.
            """,
        },
    ]

    # Display analysis cards
    for a in analyses:
        color_map = {"green": "#d4edda", "orange": "#fff3cd", "red": "#f8d7da"}
        border_map = {"green": "#28a745", "orange": "#ffc107", "red": "#dc3545"}
        bg = color_map[a["verdict_color"]]
        border = border_map[a["verdict_color"]]

        st.markdown(
            f"""
            <div style="
                background:{bg};
                border-left:5px solid {border};
                padding:16px;
                border-radius:6px;
                margin-bottom:16px;
            ">
                <h4 style="margin:0 0 8px 0;">{a['verdict']}  —  {a['title']}</h4>
                <div style="font-size:14px;line-height:1.6;">{a['body']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Summary card
    st.divider()
    st.subheader("Overall Sufficiency Verdict")

    col_v, col_t = st.columns([0.3, 0.7])
    with col_v:
        st.error("### ⚠️ PARTIALLY SUFFICIENT")
    with col_t:
        st.markdown(f"""
        The prescribed datasets are **adequate for internal report analysis** and
        **news-based verification**, but have **two critical gaps**:

        1. **No social media dataset** — the paper's title promises social media
           verification, but no dataset plan exists for it.
        2. **Outdated temporal range** — {get_target('Incident Temporal')} data for a 2026 publication
           leaves a significant information gap.

        **Recommendation:** Add a concrete social media data acquisition plan
        (e.g., Twitter/X Academic API, Reddit Pushshift archives), extend the incident corpus to 2024+, 
        and create an alignment dataset for cross-modal verification pairs.
        """)


# ===========================================================================
# TAB: References
# ===========================================================================

with tab6:
    st.header("Reference Analysis")

    # Unified reference list
    all_refs = sorted(ref_lookup.values(), key=lambda x: x.get("year", "0"), reverse=True)

    # Build fast-lookup sets for citation membership
    paper_cite_set = set(resources["citations"].get("paper.tex", []))
    notes_cite_set = set(resources["citations"].get("notes.tex", []))

    # --- Search / filter bar ---
    search = st.text_input(
        "🔎 Filter references",
        placeholder="Search by title, author, key, or year…",
        label_visibility="collapsed",
    )

    ref_data = []
    for r in all_refs:
        key = r["key"]
        cited_in_paper = key in paper_cite_set
        cited_in_notes = key in notes_cite_set
        if cited_in_paper and cited_in_notes:
            location = "Both"
        elif cited_in_paper:
            location = "Paper"
        elif cited_in_notes:
            location = "Notes"
        else:
            location = "—"

        title = r.get("title", "N/A")
        authors = r.get("author", "N/A")
        year = r.get("year", "N/A")

        # Filter by search term (case-insensitive)
        if search:
            search_lower = search.lower()
            haystack = f"{key} {title} {authors} {year}".lower()
            if search_lower not in haystack:
                continue

        # Truncate long titles
        display_title = title[:100] + "…" if len(title) > 100 else title
        # Shorten author list
        display_authors = authors
        if len(authors) > 60:
            first_author = authors.split(" AND ")[0]
            display_authors = first_author + " et al."

        ref_data.append({
            "Key": key,
            "Title": display_title,
            "Authors": display_authors,
            "Year": year,
            "Type": r.get("type", "?"),
            "Cited In": location,
        })

    st.subheader(f"All {len(all_refs)} References  —  showing {len(ref_data)}")
    st.dataframe(ref_data, use_container_width=True, hide_index=True)

    st.divider()

    # --- Stats (set-based, correct) ---
    paper_keys = paper_cite_set
    notes_keys = notes_cite_set
    shared = paper_keys & notes_keys
    paper_only = paper_keys - notes_keys
    notes_only = notes_keys - paper_keys

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Paper Citations", len(paper_keys))
    c2.metric("Notes Citations", len(notes_keys))
    c3.metric("Shared", len(shared))
    c4.metric("Total Unique", len(paper_keys | notes_keys))

    # --- Missing citations (orphans) ---
    all_cited = paper_keys | notes_keys
    orphan_citations = [k for k in all_cited if k not in ref_lookup]
    if orphan_citations:
        st.warning(
            f"**{len(orphan_citations)} citation(s) in .tex files have no matching entry in .bib files:**  "
            + ", ".join(f"`{k}`" for k in sorted(orphan_citations))
        )

    # --- Uncited references ---
    uncited_refs = [k for k in ref_lookup if k not in all_cited]
    if uncited_refs:
        st.info(
            f"**{len(uncited_refs)} reference(s) in .bib files are never cited in the .tex files:**  "
            + ", ".join(f"`{k}`" for k in sorted(uncited_refs))
        )

    # --- Notes-only details ---
    if notes_only:
        st.markdown("**References unique to notes.tex:**")
        for k in sorted(notes_only):
            r = ref_lookup.get(k, {})
            st.caption(f"- `{k}` — {r.get('title', 'N/A')} ({r.get('year', '?')})")

    st.caption("These references provide strong coverage of multimodal RAG, ESG extraction, and fact-checking literature. However, **social media analysis methodology** references are notably absent, consistent with the dataset gap identified above.")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.caption(
    "Resource Mapper for ACL Conferences project | "
    "Generated from `paper.tex`, `notes.tex`, `paper.bib`, `notes.bib`"
)
