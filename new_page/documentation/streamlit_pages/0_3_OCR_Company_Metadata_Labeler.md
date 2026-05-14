# 0.3 OCR Company Metadata Labeler

## Purpose

This page labels every OCR document folder with the company it belongs to, then stores reusable company metadata such as sector, subsector, industry, and subindustry in JSON.

## Main Features

- Scans `new_page/data/thesis_dataset/*/pages/` to find OCR document folders.
- Labels each OCR folder with company name, ticker, report year, country, exchange, notes, and IDX-style classification metadata.
- Maintains a reusable company metadata library so the same company can be applied across multiple reports.
- Previews the first OCR markdown page to help verify the selected document before saving a label.
- Tracks labeled and unlabeled folders, total pages, sectors, years, and company coverage.
- Exports and displays the saved JSON label store.

## Inputs

- `new_page/data/thesis_dataset/<document>/pages/*.md`
- Optional existing `new_page/data/ocr_company_metadata.json`

## Outputs

- `new_page/data/ocr_company_metadata.json`

## JSON Structure

The JSON has two main collections:

- `documents`: one entry per OCR folder, storing the chosen company label and metadata snapshot for that document.
- `companies`: reusable company metadata records that can be applied to many OCR folders.

Example company metadata:

```json
{
  "company_name": "PT Aspirasi Hidup Indonesia Tbk.",
  "sector": "Barang Konsumen Non-Primer",
  "subsector": "Perdagangan Ritel",
  "industry": "Ritel Khusus",
  "subindustry": "Ritel Barang Rumah Tangga",
  "country": "Indonesia",
  "exchange": "IDX"
}
```

## Thesis Use

- RQ1: documents which company each OCR source belongs to before extraction and analysis.
- RQ5: creates auditable provenance from OCR folder to company metadata and downstream visualizations.
