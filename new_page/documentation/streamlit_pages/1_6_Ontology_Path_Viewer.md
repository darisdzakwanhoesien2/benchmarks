# 1.6 Ontology Path Viewer

## Purpose

This page provides evidence for the ontology-based ABSA claim. It shows whether extracted aspects are mapped to a machine-readable ontology and allows record-level tracing from raw text to aspect to ontology path.

## Data Used

Inputs:

- `results/revision_analysis/ontology.json`
- `results/revision_analysis/ontology_coverage.csv`
- `results/revision_analysis/silver_tone_ground_truth.csv`

## Workflow Steps

1. Load the machine-readable ontology JSON.
2. Load aspect coverage statistics.
3. Load extracted records.
4. Display mapped and unmapped aspects.
5. Allow record-level inspection.
6. For each selected record, show:
   - raw text,
   - predicted aspect,
   - tone,
   - ESG pillar,
   - reasoning,
   - ontology path or suggested path.

## Outputs

The page displays:

- observed aspect count,
- mapped aspect count,
- ontology coverage percentage,
- aspect frequency chart,
- unmapped aspect table,
- full ontology JSON.

## Interpretation

Mapped aspects support the claim that the pipeline uses structured ESG categories. Unmapped aspects reveal ontology gaps and should guide ontology expansion.

Do not claim full ontology coverage if many aspects remain unmapped. Instead, use the unmapped list as evidence for future work and ontology refinement.

## Thesis Use

- Chapter III: model design and ontology encoding.
- Chapter IV: ontology coverage results.
- Chapter V: ontology scope limitation.
- Aspect 1 and 5 revision response: proof of machine-readable ontology integration.

