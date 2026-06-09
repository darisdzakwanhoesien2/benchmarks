We wanted to know if we could effectively show ESG information using a schema that includes aspects, ESG pillars, sentiment, and tone. The results in this chapter suggest that our schema works and can express what we need for this thesis.

First, our system for taking in and pulling out information works well with a lot of documents. We processed 23 documents, all done, totaling about 5,512 pages. Some of the biggest reports we handled were Bank Neo Commerce's 2024 report (694 pages), vktr_ar_sr_2024.pdf (548 pages), and alfamart_sustainability_2025.pdf (510 pages). This shows that we're testing the schema on long, complex company reports, not just short examples.

Second, the system created a useful set of structured information. Our thesis report shows 332 ESG records that have a specific tone, plus 2,074 T2 rows. Out of those 332 records, "commitment" was the most common tone (115 records), and "environmental" was the most common ESG area (179 records). "Governance" appeared 121 times, but "social" only showed up 4 times in our summary. This means the schema can tell the difference between tone, sentiment, and ESG area, but it also shows that our current data set isn't balanced.

We should put Figure 4.1 and Figure 4.2 here. They help visualize how the records are put together before we look at agreement and problems.

How the system extracted information for each prompt is shown in Table 4.1.

Table 4.1. Prompt-level extraction performance across the thesis-facing subset.

Prompt template | Runs | Parse success rate | Avg. records | Field completion rate | Missing-tone rate | Schema-drift rate
--- | ---: | ---: | ---: | ---: | ---: | ---:
data.md | 20 | 100.0% | 3.00 | 66.7% | 100.0% | 42.5%
tone_chain_of_thought_english.md | 16 | 100.0% | 6.25 | 37.4% | 0.0% | 0.4%
tone_chain_of_thought_indonesian.md | 15 | 100.0% | 4.07 | 33.1% | 0.3% | 0.3%
tone_few_shot_english.md | 15 | 100.0% | 0.00 | 0.0% | 0.0% | 0.0%
tone_few_shot_indonesian.md | 14 | 100.0% | 1.00 | 7.1% | 0.0% | 0.0%
tone_zero_shot_english.md | 14 | 100.0% | 3.93 | 35.7% | 0.0% | 0.0%
tone_zero_shot_indonesian.md | 16 | 100.0% | 2.62 | 12.5% | 0.0% | 0.0%

It's clear from these results that just successfully parsing the text isn't enough to say a prompt is good. All the prompts above parsed 100% of the time, but their actual usefulness varied a lot. For example, tone_chain_of_thought_english.md produced the most records on average. This means a prompt can follow all the grammar rules but still not be good for what we need to do in this thesis.

Looking closely at all the data helps us understand the problem with tone quality. Out of 5,444 pieces of text we extracted, we couldn't use 591 for tone analysis because they were missing tone information. This is a significant failure rate, not just a small error. It confirms that extracting tone is the weakest part of our schema. Because of this, we're treating missing tone as a major finding in Chapter 4, not just a small bug.

Figure 4.3 should go after Table 4.1. It adds to the overall tone distribution by showing how tone relates to specific aspects.

The ontology layer also makes the schema easier to understand. Our current ontology table tracks 52 aspects, and all 52 are connected to ontology paths. This doesn't mean everything is perfectly semantically correct, but it does show that our record schema isn't just structured by syntax; it can also be linked to a bigger layer of ESG concepts. In short, the schema allows us to extract information linked to specific pages, apply multiple labels, and interpret data using ontology, all within one structure.

In summary, for this thesis, the answer to RQ1 is yes. We can represent ESG information using a schema that combines aspect, ESG pillar, sentiment, and tone, and this schema works even with large reports. The main thing to note is that the data isn't balanced, and getting the tone information completely is harder than getting aspect or ontology coverage.

RQ2 asked how our AI-generated tone labels compare to those from specialized models like ClimateBERT, and what this tells us about how reliable automated ESG assessments are. The most important finding here is how well our disclosure tone matched ClimateBERT's commitment labels. Table 4.2 shows the main agreement.

Table 4.2. Tone-commitment versus ClimateBERT-style commitment comparison.

Compared labels | Records | Percent agreement | Cohen's kappa | Tone commitment rate | Climate-commitment label rate | Interpretation boundary
--- | ---: | ---: | ---: | ---: | ---: | ---
tone_commitment vs climate_commitment_label | 332 | 83.7% | 0.645 | 34.6% | 36.4% | Strong overlap, but not label equivalence

The results show a strong but not perfect match. Our tone system seems to pick up on something very similar to what ClimateBERT identifies as climate commitment, but they aren't exactly the same. This is helpful because it supports the idea that tone gives us more information about how mature a disclosure is, beyond just recognizing climate topics.

Figure 4.4 should go with Table 4.2 because it's easier to see the cross-tabulation visually than just reading about it.

The cross-tabulation of tone by ClimateBERT gives us a closer look. Even though there are more labels than just a simple climate commitment yes/no, the table shows that records categorized as "commitment" group differently from "action" and "outcome" records. In our notes, commitment is most closely tied to climate-commitment, climate-d, and environmental claims. Action and outcome, however, spread out more across governance and other types of labels. This suggests that language about commitment is very common in environmental claims, even when a document doesn't yet talk about actual results.

So, this comparison partly supports the validity of our tone labels. Tone labels and ClimateBERT-style labels are strongly related when it comes to commitment, which means our tone categories aren't random. However, the two systems answer different questions. ClimateBERT focuses on whether something is about a climate topic or a climate commitment. Our tone schema, on the other hand, asks if a disclosure is a promise, an action, or a completed outcome. So, it's better to see this as a partial match between two concepts, rather than them being interchangeable.

In short, RQ2 gets a positive answer, but with a clear limit. Our AI-generated tone labels match up well with results from specialized climate models, especially for language about commitment. But you shouldn't use them interchangeably with classifying climate topics. This comparison confirms that our tone categories are a useful extra layer for analysis, not a replacement for specialized climate models.

RQ3 asked what specific problems occur when we automatically pull out ESG records, such as losing data during OCR, issues with the schema, or gaps in the ontology. In this chapter, the evidence for this question is more about identifying problems than comparing things.

Table 4.3 shows the different ways the system failed.

Table 4.3. Failure-mode count table.

Failure mode | Count | Share of reviewed failures | Likely cause | Representative example type
--- | ---: | ---: | --- | ---
missing_tone | 61 | 61.0% | Output omitted the central tone field despite otherwise parseable extraction | Record with populated text/aspect fields but empty tone
schema_drift | 20 | 20.0% | Model produced values in the wrong field or changed schema semantics | Tone-like content placed in sentiment or free-text slots
hedged_or_modal_language | 10 | 10.0% | Commitment/action boundary blurred by future-oriented or hedged phrasing | “will”, “target”, “intend”, “berkomitmen” mixed with current actions
regulatory_or_indonesian_domain_terms | 3 | 3.0% | Domain-specific Indonesian ESG terminology not handled consistently | Governance/regulatory phrasing with weak tone cues
table_or_numeric_layout | 3 | 3.0% | Table-heavy or numeric formatting disrupted semantic extraction | KPI/table rows detached from narrative context
passive_voice | 3 | 3.0% | Passive construction weakened action/outcome detection | Statement describes achievement without explicit actor
bilingual_or_code_switched | 1 | 1.0% | Language switching complicated cue interpretation | Mixed Indonesian-English ESG statement
schema_drift with action prediction | 1 | 1.0% | Structural mismatch in otherwise action-like output | Action record with malformed output fields
hedged_or_modal_language with action prediction | 1 | 1.0% | Action phrasing mixed with promise language | Agreement/plan statement straddling action and commitment
passive_voice with action prediction | 1 | 1.0% | Passive form weakened event interpretation | Passive wording treated as action rather than outcome

The biggest problem is clearly the 61 cases where the tone was missing. After that, schema drift and unclear language (hedged or modal) were the next most common issues. This means our system struggles more with vague language and odd formatting than with simple parsing errors. So, the problem isn't just technical; it's partly about language itself.

Two more graphs directly support this failure analysis by showing how often errors happen versus what types of errors they are.

On the positive side, our ontology coverage is good. The current ontology table shows we track 52 aspects, and all 52 are mapped to ontology paths. The most common mapped aspects are climate-detection (79 records), governance (66), missing (60), and none (23). Beyond these, specific terms like "roadmap karbon" (carbon roadmap), "pelatihan antikorupsi" (anti-corruption training), "komitmen net zero" (net zero commitment), and "implementasi eco-mechanized mining" (eco-mechanized mining implementation) are all linked to structured paths related to GRI, governance, or climate. This tells us that our ontology layer is more stable in terms of what it covers than our tone layer is in terms of consistency.

Looking at all the data again really highlights these diagnostic findings. Out of 5,444 extracted pieces of text, we couldn't use 591 for analyzing tone because they were missing tone information. This isn't just a small problem to clean up. It means the system can keep running, but it fails on the main tone field often enough that it could mess up later interpretations if we ignore these cases.

These findings show a clear contradiction. The system is organized well enough to link different ESG aspects to ontology paths, but it still struggles to consistently tell the difference between commitment, action, and outcome, especially when the text is complex or talks a lot about governance. This contradiction is a key takeaway from this chapter.

In conclusion, the diagnostic evidence directly answers RQ3. The biggest problems are missing tone, schema drift, unclear language, and confusion caused by layout or specific terms. While OCR works fine for whole documents, the main weakness further down the line is consistently identifying tone, not covering the ontology.

RQ4 asked how consistent the ESG extraction results stay when we use different prompts, AI models, and service providers. We answered this by looking at how stable prompts and models were, as well as checking our stored work and how repeatable our system is.

Our system is very good at reproducibility from an engineering standpoint. The saved report for this thesis lists 1,220 result files and 184 AI background tasks. We've already exported five standard figures for the thesis: tone_distribution.png, esg_by_tone.png, aspect_by_tone_heatmap.png, climatebert_label_by_tone.png, and climatebert_remote_top_scores.png. Plus, the Chapter 4 Streamlit pages show live versions of the same results tables, so the written chapter and the interactive dashboard always match up.

This evidence for reproducibility is important because it means our research isn't just based on a temporary setup. Our file system keeps both the in-between and final results. So, we can re-run the process, check it, and add to it without having to start the thesis reporting from scratch. However, this isn't the same as saying that all AI model outputs from different providers will be exactly the same every time. This thesis claims that the way we work and store files is repeatable, more so than saying the exact output will always be the same.

The most consistent results were found in how models and prompts performed. Table 4.4 shows the current model comparison.

Table 4.4. Model-level extraction performance.

Model | Runs | Parse success rate | Avg. records | Missing-tone rate | Schema-drift rate | Source | Short interpretation
--- | ---: | ---: | ---: | ---: | ---: | --- | ---
arcee-ai/trinity-large-preview:free | 90 | 100.0% | 3.02 | 0.05% | 0.11% | revision_analysis | Best stable thesis-facing baseline: high schema obedience and near-zero tone omission
openai/gpt-oss-120b:free | 20 | 100.0% | 3.00 | 100.0% | 42.5% | revision_analysis | Formally parseable but practically unusable for tone analysis
arcee-ai/trinity-large-thinking:free | 89 | 89.9% | 12.52 | 0.0% | 0.0% | live_reprocess | Very high extraction yield, but lower formal stability than the preview model
minimax/minimax-m2.5:free | 776 | 56.6% | 4.94 | 0.05% | 0.26% | live_reprocess | High-volume live usage with weak parse reliability
openai/gpt-oss-20b:free | 145 | 95.9% | 1.13 | 0.0% | 0.0% | live_reprocess | Structurally stable but low extraction yield
qwen3.5:0.8b | 2 | 0.0% | 0.00 | 0.0% | 0.0% | live_reprocess | No usable extraction in the current slice

The most important comparison for our thesis's stable data comes from arcee-ai/trinity-large-preview:free and openai/gpt-oss-120b:free. Both successfully parsed everything in our summary. However, gpt-oss-120b completely missed the tone in 100% of cases and had a 42.5% schema-drift rate for that specific prompt-model combination. This clearly warns us not to assume a model is good for a task just because it's big or well-known. For our work, it's more important that a model follows the schema and provides complete tone information than its raw ability to generate text.

Figure 4.7 goes well with Table 4.4 because it makes it easier to see the balance between how stable the system is and how useful its output actually is.

Prompt stability followed a similar trend. Prompts using a "chain-of-thought" approach, especially in English, gave us the most records per run. On the other hand, the data.md prompt parsed successfully but gave us tone outputs that weren't useful. Few-shot prompts were inconsistent: the English few-shot prompt didn't produce any records in our current summary, while the Indonesian one completed very few. This suggests that just giving examples doesn't guarantee better extraction. For our system, clearly defining the tone and telling the model to stick to the schema seems more important.

You should look at Figure 4.8 alongside the table of prompt results. The trends for prompt families are key to our argument that how you design a prompt matters more than just calling it a certain style.

These results show a real-world compromise. Some settings pull out the most information, while others make sure the structure is very clean. So, the best setup for this thesis isn't the most complex one. Instead, it's the one that balances successful parsing, complete tone information, and acceptable drift. This is exactly the kind of practical validation this chapter needs to talk about.

To sum up, RQ4 gets an answer with an important caveat. Our process is reproducible and stable from an engineering point of view. This is because we permanently store prompts, outputs, logs, and other generated files, and we can recreate the same evaluation views. However, the meaning of the outputs isn't consistently stable across different prompts, models, or providers. Stability relies heavily on how prompts are designed and how well models follow the schema. So, this thesis can more confidently claim a reproducible workflow structure than universally stable model behavior.

The explainability part helps us understand why the system works the way it does. For example, our code/rule_based.py file uses specific words to identify commitment, action, and outcome. Meanwhile, code/classical_ml.py provides tables of TF-IDF coefficients and local explanations. Our lexicon file has words like "berkomitmen," "commitment," "will," "menargetkan," "target," "aim to," and "dedicated to" for commitment language. For outcome language, it uses words like "telah," "achieved," "has been," and "successfully."

A summary of how often these trigger words appeared confirms that they really do influence predictions. Words indicating commitment appeared 53 times with commitment predictions, but also 30 times with action predictions and 36 times with missing predictions. Outcome words appeared 18 times with outcome predictions, but also 19 times with missing predictions and 17 times with commitment predictions. This helps explain why it's hard to draw clear lines: many parts of a report use both future-focused and past-achievement language at the same time, especially in narrative sections that mix different kinds of reporting.

Two more figures are particularly relevant here. They expand on the explanation without needing a new way to evaluate things.

We can also understand the ontology path evidence. For environmental and climate examples, we have "roadmap karbon" (carbon roadmap), "komitmen net zero" (net zero commitment), "kerja sama energi bersih" (clean energy cooperation), and "teknologi ramah lingkungan" (environmentally friendly technology). Governance examples include "pelatihan antikorupsi" (anti-corruption training), "kebijakan konflik kepentingan" (conflict of interest policy), and "sertifikasi smap" (SMAP certification). These links show that the system can turn raw terms from reports into structured topics that we can use for later analysis in this chapter.

Here are some examples to show the difference between commitment, action, and outcome:
1. Commitment example: “As a pioneer among industrial estate developers in Indonesia, BeFa is at the forefront of creating a green and eco-friendly industrial zone...” This example is categorized as commitment, talks about environmental claims, and is strongly predicted as a climate-commitment.
2. Outcome example: “Keberhasilan pembangunan fasilitas perakitan kendaraan listrik di Magelang menjadi tonggak penting...” (The successful construction of the electric vehicle assembly facility in Magelang is an important milestone...). This is labeled as an outcome with a positive feeling because it describes a finished infrastructure project.
3. Action example: “Pada tanggal 10 Oktober 2023, Perusahaan dan MB menandatangani perjanjian kerja sama...” (On October 10, 2023, the Company and MB signed a cooperation agreement...). This is labeled as an action because it describes a specific agreement, but not yet a completed result.
These examples show that our tone categories actually make sense. The real challenge isn't whether we can understand the categories, but whether the extraction system can consistently assign them, no matter the prompt, model, or way the information is presented.

We're not using a complete, expert-labeled benchmark for evaluation right now. Instead, we have a layered reference system made up of extracted records, ClimateBERT-style comparison labels, weak word suggestions, and early human annotations. So, we need to evaluate this reference system itself.

The best comparison we have is the ClimateBERT proxy agreement table, which covers 332 records. It offers good coverage and acceptable agreement, but it's still just a proxy. Our own records show that a full, direct ClimateBERT benchmark isn't ready yet. The initial human annotations are in files like pilot_ground_truth_seed.csv and pilot_ground_truth_annotations.csv. Our report currently shows 70 such labels. While these are helpful for reviewing and finding disagreements, they're not enough to be considered a perfect standard.

When we look at the quality, the reference data is somewhat trustworthy but still has a lot of noise. Many initial rows are marked "needs_review," which is correct and something we should openly report. Several examples show that the predicted tone doesn't match the suggested tone. For example, some records about governance or signing agreements are predicted as actions, but they get suggestions for commitment because the text uses words that indicate future plans or possibilities. This isn't just an annotation mistake; it shows how hard it is to tell the difference between an action and a commitment in sustainability reports, especially when they focus on governance.

Our system also keeps problematic or weak reference cases instead of quietly removing them. Records with missing tone or schema drift are still visible in the review files. This is a good approach because it stops our evaluation data from looking artificially perfect. However, it also means that our current reference data should be called an early reference framework, not a finished benchmark.

All in all, our chosen reference system is reliable enough to explore the data, analyze disagreements, and make claims in this chapter about patterns and types of failures. But it's not yet reliable enough to make final claims about which model is absolutely the best.

Our system doesn't yet have a full, controlled study where we strictly remove one part at a time to see its effect, like in machine learning. However, our current results do allow us to compare different parts of the system, like prompts, models, and how we represent data. So, this section will carefully and clearly address that requirement.

The first comparison is about the prompts. If we consider prompt design as something we can change, then using "chain-of-thought" prompts specifically for tone is the most crucial part for getting useful T3 extractions. If we swap that out for the general data.md prompt, the JSON will still parse correctly, but the tone extraction will fail completely. This tells us that clear instructions about tone are more important than general extraction instructions for what we need to do in this thesis.

The second finding is about choosing a model. If we think of different model types as interchangeable parts, then not all large language models are the same. arcee-ai/trinity-large-preview:free provides stable parsing and tone results for our thesis data. In contrast, openai/gpt-oss-120b:free had unacceptable issues with missing tone and schema drift in the summarized group. This means our system relies more on models that follow the schema correctly than on simply using a bigger model.

The third finding is about how we represent the data. Our system's design suggests three ways to use features: hand-made word features, sparsely learned features, and features that blend context. The rule-based model is easiest to understand and helps explain errors, but it breaks down easily when things are unclear. The traditional TF-IDF model gives us reproducible statistical starting points and clear explanations of its coefficients, but it's limited because it depends on specific words. The hybrid contextual model is built to understand sentence meaning, section context, and ontology information all at once, making it the most complete design conceptually. However, the evidence in Chapter 4 shows more about how stable prompts and models are than about a full comparison of these three ABSA parts, because our thesis dashboard focuses on how the system works, not on strict classifier testing.

The fourth finding is about how the ontology is integrated. The ontology layer seems strong in what it covers, which means mapping aspects to paths isn't the weakest part right now. If anything is causing problems in the system, it's the step where tone labels are created, not the ontology layer.

Putting these comparisons together, a clear picture emerges. The most important part of our system is how we design the prompt and schema for extraction, followed by choosing a model that can reliably follow that schema. While understanding context and ontology is still important for clarity and future testing, the current evidence shows that a stable extraction process is necessary before we can make any other improvements.

Figure 4.11 should be included as a final overall visual if we create the Sankey diagram from the visualizer. It would neatly summarize how the most common aspects spread across commitment, action, and outcome in one compact view.

This chapter's main findings are five. First, our system successfully extracts ESG information from PDFs into a structured format for a significant number of documents: 23 reports and about 5,512 pages processed by OCR. Second, the extraction process creates a useful collection of data, including 332 records with tone information and 2,074 T2 rows. This confirms that our schema works in practice. Third, our "tone commitment" aligns well with ClimateBERT's commitment labels, showing 83.7% agreement and a Cohen's kappa of 0.645. This means our tone categories are relevant without just becoming climate topic classifications. Fourth, the system's biggest problem isn't parsing errors, but rather inconsistent tone extraction, especially missing tone information and schema drift with certain prompts. Fifth, the most important factor for getting useful output is how the prompt is designed and how well the model follows it, not just the model's size.

Based on our current data, the best setup for this thesis uses arcee-ai/trinity-large-preview:free with prompts designed for tone. This setup successfully parses everything, rarely misses tone, and has low schema drift. The most important part of the system is the prompt design that focuses on tone. The main challenge is balancing the flexibility of extraction with how reliably the schema works: systems that seem generally capable don't always produce structured outputs that are useful for this thesis.

These findings directly relate to Chapter 3. That chapter highlighted the importance of a modular design, clear origins, working well in two languages, and being easy to understand. Chapter 4 shows that those design choices were good. The system performs best when it keeps track of intermediate steps, tells tone apart from sentiment, and sees disagreements as useful information, not just errors. These results also set up the next chapter, where we can discuss things like the prevalence of commitment language, tone failures in governance contexts, model disagreements, and ontology coverage as real findings, not just technical details.
