# Impromptu Note: Which Prompt To Use In This Folder

## Current Thesis Shape To Assume Before Running Any Prompt

Use the actual non-`_v1` thesis files in `converted_markdown/` as the working source:

- `foreword.md`
- `abstract.md`
- `tiivistelma.md`
- `abbreviations.md`
- `introduction.md`
- `relatedwork.md`
- `implementation.md`
- `experiments.md`
- `discussion.md`
- `summary.md`
- `appendices.md`

Current declared research questions are the four RQs in `introduction.md`.

Current structural reality:

- Chapter 3 is methodology and implementation-oriented.
- Chapter 4 is the main evaluation and results chapter.
- Chapter 5 contains discussion, limitations, future work, and broader impact.
- Chapter 6 is the conclusion.
- `abstract.md`, `tiivistelma.md`, and `appendices.md` currently appear to be placeholders and should be flagged as incomplete rather than reviewed as finished scientific chapters.
- There is no separate standalone "results" chapter outside `experiments.md`.
- Any prompt that assumes six research questions, a train/validation/test benchmark thesis, or a fully completed abstract should explicitly verify those assumptions before criticizing the text.

Use `02_Part_B2.md` first if the immediate concern is missing **ablation studies** and other experimental-rigor gaps.

Why:
- `02_Part_B2.md` is the most direct prompt for methodological completeness.
- It explicitly checks `baseline selection`, `ablation studies`, `hyperparameter selection`, `statistical significance or uncertainty analysis`, `error analysis`, `robustness checks`, `reproducibility`, and `limitations and threats to validity`.
- It is therefore the best prompt for answering: "Besides missing ablation studies, what else is weak or missing in the experiments?"

Recommended prompt order in this folder:

1. `02_Part_B2.md`

Use this to inspect whether the thesis has missing or weak:
- baselines;
- ablation studies;
- train/validation/test protocol;
- leakage control;
- prompt-selection discipline;
- seed/model-version/reporting details;
- metric justification;
- class-level results;
- significance or uncertainty analysis;
- qualitative analysis;
- robustness checks;
- validity and reproducibility discussion.

2. `02_Part_B1.md`

Use this next to check whether the experiments actually support the stated objectives and research questions.

Why:
- It builds a traceability matrix from research question -> method -> evidence -> result -> conclusion.
- This catches cases where experiments exist but do not actually answer the thesis questions.

3. `01_Part_A.md`

Use this if you suspect contradictions across chapters.

Why:
- It is the thesis-wide consistency audit.
- It catches mismatched dataset sizes, model names, split descriptions, metrics, claimed improvements, and conclusion-strengthening without evidence.

4. `10_Page_J.md`

Use this last as the **master synthesis prompt**.

Why:
- It pulls together the earlier checks into a full assessment.
- It includes critical issues, scientific-rigor assessment, chapter-by-chapter revision checklist, submission-readiness checklist, and final revision plan.
- This is the best prompt if you want not only "what is missing" but also "how serious is it and what should be fixed first."

## Best Single Prompt

If you want only one prompt to run, use `10_Page_J.md`.

Why:
- It already requires a `Scientific-Rigor Assessment` covering research design, data, baselines, experimental setup, metrics, statistical validity, error analysis, reproducibility, and generalizability.
- It also forces prioritization, so missing ablation studies will be evaluated in context rather than in isolation.

## Best Two-Prompt Workflow

If the goal is practical diagnosis:

1. Run `02_Part_B2.md` to detect methodological gaps.
2. Run `10_Page_J.md` to rank those gaps by severity and turn them into a revision plan.

## Likely Things To Check Besides Ablation Studies

Based on the prompts in this folder, the other high-value checks are:
- weak or missing baselines;
- unclear train/validation/test separation;
- possible data leakage;
- missing hyperparameter-selection explanation;
- missing statistical significance or uncertainty reporting;
- lack of error analysis;
- lack of robustness checks;
- incomplete reproducibility details such as seeds, model versions, dates, and decoding settings;
- conclusions that are stronger than the actual evidence;
- research questions that are only partially answered.

## Thesis-Specific Likely Failure Modes

For this thesis in particular, expect to verify:

- mismatch between the four declared research questions in Chapter 1 and any later references to additional RQs;
- claims about ablation studies in the chapter outline that may not be matched by actual Chapter 4 content;
- methodology claims of reproducibility without full reporting of prompts, model versions, dates, seeds, and decoding settings;
- partial human annotation being described too strongly as validation or ground truth;
- comparison between tone labels and ClimateBERT-style labels being overstated as equivalence;
- dataset and subset counts changing across chapters without enough explanation;
- placeholder front matter causing weak alignment between abstract, conclusion, and body chapters;
- discussion claims that exceed the evidence scope of the Indonesian thesis-facing subset.

## Recommendation

For the specific concern you mentioned, start with `02_Part_B2.md`.

Then run `10_Page_J.md` if you want the complete answer to:
"Ablation studies seem missing. What else is missing, how serious is each issue, and what should be fixed before submission?"
