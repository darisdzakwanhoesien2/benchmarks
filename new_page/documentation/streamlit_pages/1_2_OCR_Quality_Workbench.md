# 1.2 OCR Quality Workbench

## Purpose

This page measures OCR quality using Character Error Rate and Word Error Rate. It exists because the revision feedback correctly notes that the pipeline cannot claim OCR reliability without measuring OCR fidelity.

The page does not automatically know the correct text. A human must provide reference text from the original report or manually corrected OCR.

## Data Used

Input:

- manually pasted reference text,
- OCR text for the same page, paragraph, or table snippet.

Saved output:

- `results/revision_analysis/ocr_quality_samples.csv`

Optional processing summary:

- `results/revision_analysis/ocr_processing_summary.csv`

## Metrics

### Character Error Rate

```text
CER = edit_distance(reference_characters, ocr_characters) / reference_character_count
```

### Word Error Rate

```text
WER = edit_distance(reference_words, ocr_words) / reference_word_count
```

Lower values indicate better OCR quality.

## Workflow Steps

1. Open the page.
2. Select or type document/source name.
3. Enter page or batch identifier.
4. Choose layout type:
   - narrative,
   - table,
   - bilingual columns,
   - infographic,
   - mixed,
   - unknown.
5. Choose language:
   - Indonesian,
   - English,
   - mixed,
   - unknown.
6. Paste manually corrected reference text.
7. Paste OCR text.
8. Save.
9. Review CER/WER across saved samples.

## How To Interpret

High CER/WER indicates that OCR noise may affect:

- tokenization,
- sentiment classification,
- tone detection,
- aspect extraction,
- schema stability.

For the thesis, compare OCR error rates across layout types. Bilingual columns and tables are expected to produce higher error rates than normal narrative paragraphs.

## Thesis Use

- Chapter III: preprocessing and OCR methodology.
- Chapter IV: OCR quality evidence.
- Chapter V: limitations and layout-induced error discussion.

