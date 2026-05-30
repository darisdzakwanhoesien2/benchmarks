https://chatgpt.com/c/6a180071-0cc4-83ec-b6e1-ad81d6d348c9

Looking at **all four sources together**:

1. Thesis Draft (Ch 1–3 scaffold) 
2. Thesis Action Plan / Architecture Map 
3. Chapter 4–6 Benchmark Mapping 
4. ClimateBERT Multi-Model Runner results 

I think there are several **higher-level gaps** beyond the evaluation issues I already mentioned.

---

# 1. You Still Need a Stronger Experimental Baseline Section

Right now you compare:

* LLM prompts
* ClimateBERT
* Tone taxonomy
* Ontology mapping

But there is no clear benchmark hierarchy.

A reviewer will ask:

> Is your system actually better than simpler approaches?

You need at least:

| Method         | Purpose            |
| -------------- | ------------------ |
| VADER          | sentiment baseline |
| FinBERT        | financial baseline |
| ClimateBERT    | climate baseline   |
| LLM ABSA       | proposed           |
| LLM + Ontology | proposed enhanced  |

Then report:

* agreement
* coverage
* robustness
* interpretability

---

# 2. Missing Statistical Significance Testing

Currently I see:

* counts
* distributions
* agreement
* kappa

But I don't see:

* McNemar test
* Chi-square
* Bootstrap confidence intervals
* Confidence bands

A thesis examiner may ask:

> How do you know differences are not random?

You need at least:

* confidence intervals
* significance tests

for:

* prompt comparisons
* model comparisons
* ClimateBERT agreement

---

# 3. Missing Error Taxonomy

You already mention:

* OCR loss
* schema drift
* bilingual failures
* missing tone

But they need formal categorization.

For example:

| Error Type        | Example                     |
| ----------------- | --------------------------- |
| OCR Error         | broken numbers              |
| Translation Error | Indonesian ambiguity        |
| Ontology Error    | unmapped aspect             |
| Tone Error        | commitment→action confusion |
| ClimateBERT Error | false climate detection     |
| Prompt Error      | inconsistent extraction     |

This becomes a dedicated chapter section.

Currently these appear scattered.

---

# 4. Missing Greenwashing Validation

This is the largest research risk.

Your thesis claims:

> tone taxonomy can help identify greenwashing.

But:

Do you actually validate greenwashing?

Not yet.

You currently validate:

* tone
* sentiment
* ESG labels
* ClimateBERT agreement

But not:

* greenwashing labels

You need:

### Option A

Expert-labeled greenwashing examples



---

# 6. Missing Ontology Contribution Analysis

Your ontology mapping is one of the most unique parts.

You currently show:

* mapped aspects
* ontology coverage
* 52/52 mapped 

But you do not yet show:

### What new ESG vocabulary did you discover?

Example:

| Standard GRI     | Indonesian Variant |
| ---------------- | ------------------ |
| Emissions        | emisi              |
| Carbon           | karbon             |
| Renewable energy | energi terbarukan  |

This could become an actual contribution.

---

# 7. Missing Bilingual Analysis

This is a surprisingly large gap.

Your thesis repeatedly says:

> Indonesian-English ESG disclosures

Yet I do not see a dedicated chapter discussing:

* Indonesian-only results
* English-only results
* mixed-language results

Questions reviewers may ask:

* Is English easier?
* Does Indonesian reduce performance?
* Does translation improve results?

Need at least one comparison table.

---

# 8. Missing Temporal Analysis

You already have:

> Aspect evolution graphs planned. 

But I don't see them integrated into the thesis.

Potential contribution:

### 2023 vs 2024 vs 2025

How ESG language evolves.

For example:

* more commitments
* more outcomes
* new ESG themes

This strengthens novelty.

---

# 9. Missing Threats-to-Validity Section

A mature thesis needs:

## Internal Validity

Prompt sensitivity.

## Construct Validity

Tone ≠ ESG quality.

## External Validity

Indonesian companies only.

## Conclusion Validity

Limited annotation sample.

Many examiners specifically look for this.

---

# 10. Missing Ablation Study

Ablation studies are common in NLP theses.

Example:

| Configuration         | Performance |
| --------------------- | ----------- |
| LLM only              | X           |
| LLM + ontology        | Y           |
| LLM + ontology + tone | Z           |
| Full pipeline         | Best        |

This shows which component matters.

Without it:

reviewers may ask:

> Why do we need the ontology?
>
> Why do we need the tone taxonomy?
>
> Why do we need ClimateBERT?

---

# 11. Missing Research Artifact Package

You already have:

* dashboards
* Streamlit
* benchmark pages
* job runners
* ClimateBERT pipelines  

But you need a formal appendix listing:

## Artifact Inventory

* source code
* prompts
* datasets
* annotations
* ontology
* benchmark outputs
* Docker setup
* Streamlit dashboards

This becomes very valuable during defense.

---

# 12. Missing "Why ClimateBERT Failed or Succeeded"

The new ClimateBERT runner provides something interesting:

* 5,444 rows
* multiple models
* multiple prompts
* 13 companies
* 0 processing errors  

This enables a deeper question:

> Why do ClimateBERT labels diverge from tone labels?

That discussion could become one of the strongest sections in Chapter 5.

Because:

* ClimateBERT measures climate relevance.
* Tone measures disclosure behavior.

Those are fundamentally different constructs.

Showing this distinction is potentially publishable.

---

# If I Were Preparing for Defense Next Week

My final priorities would be:

### Must Have

1. Human annotation protocol
2. Inter-annotator agreement
3. OCR validation
4. Greenwashing validation
5. RQ answer tables
6. Threats to validity

---

### Strongly Recommended

7. Error taxonomy
8. Case studies
9. Bilingual analysis
10. Ablation study

---

### Nice to Have

11. Temporal ESG evolution
12. Statistical significance testing
13. Ontology vocabulary contribution section

---

At this stage, your biggest weakness is no longer implementation. The implementation is already extensive. The remaining weaknesses are **scientific rigor, validation, and defensible evidence for the greenwashing claims**. Those are the areas most likely to be challenged during examination.
