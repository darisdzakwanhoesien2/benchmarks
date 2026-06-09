#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

BODY_TEX="/tmp/thesis_body.tex"

echo "Flattening LaTeX..."
latexpand main.tex > thesis_flat.tex

echo "Preparing Pandoc input..."
awk '
  /\\chapter\{Introduction\}/ {in_body=1}
  /\\appendix/ {in_body=0}
  /\\startappendix/ {in_body=0}
  /\\end\{document\}/ {in_body=0}
  in_body
' thesis_flat.tex > "$BODY_TEX"
sed -i 's/\\printbibliography\[[^]]*\]/\\bibliography{citations.bib}/g; s/\\startappendix//g; s/\\alt{[^}]*}//g; s/\\providecommand{\\tightlist}{\\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}}//g' "$BODY_TEX"

python3 - <<'PY'
from pathlib import Path

p = Path("/tmp/thesis_body.tex")
text = p.read_text()
old = "\\caption{Executable system architecture of the repository, rewritten from the repository's Mermaid workflow documentation into a LaTeX-safe diagram.\n\n\\label{fig:system_architecture}"
new = "\\caption{Executable system architecture of the repository, rewritten from the repository's Mermaid workflow documentation into a LaTeX-safe diagram.}\n\\label{fig:system_architecture}"
text = text.replace(old, new, 1)

figure_names = {
    "03_01_overview",
    "03_01_01_system_architecture",
    "03_02_data_sources",
    "03_02_02",
    "03_04",
    "03_05",
    "03_06",
    "03_07_summary",
    "tone_distribution",
    "esg_by_tone",
    "aspect_by_tone_heatmap",
    "climatebert_label_by_tone",
    "failure_mode_pareto",
    "failure_mode_pie",
    "model_tradeoff_scatter",
    "prompt_strategy_comparison",
    "information_density_by_tone",
    "soft_language_ratio_by_tone",
    "greenwashing_gap_scatter",
    "commitment_outcome_ratio",
    "mermaid_flow_diagram_01",
    "mermaid_flow_diagram_02",
}

for name in figure_names:
    text = text.replace("{" + name + "}", "{Figures/" + name + ".png}")

p.write_text(text)
PY

echo "Generating DOCX..."
pandoc "$BODY_TEX" \
  --from=latex \
  --to=docx \
  --citeproc \
  --bibliography=citations.bib \
  --resource-path=.:Figures \
  -M title="Toward an Executable ESG Aspect-Based Sentiment Analysis Framework for Indonesian Sustainability Reports" \
  -M author="Daris Dzakwan Hoesien" \
  --output=thesis.docx

echo "Generating PDF..."
latexmk -pdf -interaction=nonstopmode main.tex

echo "Done: $ROOT_DIR/thesis.docx"
echo "Done: $ROOT_DIR/main.pdf"
