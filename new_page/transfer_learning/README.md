codex resume 019e785c-4a9f-7313-aebe-2b4f3081e7f3
# Transfer Learning — ESG ABSA (Bahasa Indonesia)

Folder ini mengimplementasikan *end-to-end* eksperimen **transfer learning** untuk **ESG ABSA Bahasa Indonesia** menggunakan artefak yang sudah ada di repositori ini.

## Isi

- `data_builder.py` — membangun dataset training dari `results/esg_records.json` dan/atau file label manual.
- `train.py` — melatih model transformer untuk prediksi `aspect`, `sentiment`, dan opsional `tone`.
- `evaluate.py` — evaluasi + ekspor metrik & confusion matrix.
- `streamlit_transfer_learning.py` — viewer Streamlit untuk melihat metrik & contoh error.
- `schemas.py` — skema dan utilitas normalisasi label.

## Prasyarat

Bagian training/evaluasi membutuhkan `torch` + `transformers`.

- Jika Anda menjalankan dari Python sistem yang “externally managed” (PEP 668), buat *virtual environment* terlebih dahulu.
- Pastikan ruang disk cukup. Instalasi `torch` (terutama yang membawa CUDA wheels) bisa sangat besar.

Contoh (di root repo):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Quickstart

1) Bangun dataset (otomatis dari ekstraksi LLM):

```bash
python3 transfer_learning/data_builder.py \
  --esg-records results/esg_records.json \
  --out results/transfer_learning/dataset.jsonl
```

2) Latih model (baseline sederhana, multi-task heads):

```bash
python3 transfer_learning/train.py \
  --train results/transfer_learning/dataset.jsonl \
  --model bert-base-multilingual-cased \
  --out results/transfer_learning/run_001
```

3) Evaluasi:

```bash
python3 transfer_learning/evaluate.py \
  --data results/transfer_learning/dataset.jsonl \
  --run results/transfer_learning/run_001 \
  --out results/transfer_learning/run_001/metrics
```

4) Lihat di Streamlit:

```bash
streamlit run transfer_learning/streamlit_transfer_learning.py
```

## Catatan Dataset

- Dataset builder default memakai **pseudo-label** dari output LLM (`aspect`, `sentiment`, `tone`) sebagai *starting point*.
- Untuk tesis/publikasi, Anda sebaiknya ganti/augment dengan label manusia dari *Ground Truth Workbench* dan gunakan split berbasis dokumen untuk menghindari leakage.
