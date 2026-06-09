B3. State of the Art and Method Justification

Use `relatedwork.md` together with `implementation.md` when assessing method justification.

For this thesis, pay special attention to whether the literature review justifies:

- record-level ESG extraction rather than document-level scoring;
- the distinction between sentiment, tone, and climate-topic labels;
- the use of LLM prompting together with rule-based, classical ML, hybrid, and ontology-based components;
- the use of ClimateBERT-style comparison as an external semantic reference rather than a full substitute for tone labeling;
- the Indonesian and bilingual reporting context as a genuine methodological constraint rather than a vague motivation.

Assess whether the literature review and methodology:

establish the current state of science and technology;
distinguish established methods from emerging research;
cover both currently available solutions and ongoing research;
justify the selected methods against realistic alternatives;
explain why each model, baseline, metric, dataset, ontology, or tool was selected;
identify limitations of prior studies;
identify the precise research gap;
show how the thesis addresses that gap;
avoid presenting standard implementation work as a novel scientific contribution;
include recent and directly relevant research;
distinguish primary research papers from secondary or non-academic sources;
avoid unsupported statements such as “few studies exist” or “no previous study has addressed this.”

For every major method, determine:

What alternatives were available?
Were those alternatives discussed?
Was the final selection justified scientifically?
Was the selection based mainly on convenience, availability, or technical constraints?
Are those constraints disclosed?
Does the implementation correspond to the cited method?

Additional thesis-specific checks:

- whether claims about "state of the art" are attached to actual cited evaluation practices rather than just model names;
- whether the review explains why this thesis uses a pipeline-and-diagnostics design instead of a narrow benchmark setup;
- whether tables in Chapter 2 are still placeholders and therefore fail to justify later method choices adequately;
- whether claims of novelty are framed as engineering integration, methodological adaptation, or scientific contribution with the right level of caution.
