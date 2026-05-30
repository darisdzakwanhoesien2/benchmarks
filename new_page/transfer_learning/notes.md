codex resume 019e785c-4a9f-7313-aebe-2b4f3081e7f3
# Notes — Transfer Learning ESG ABSA

Tujuan folder ini: menyediakan implementasi minimal yang bisa dijalankan untuk eksperimen transfer learning ESG ABSA Bahasa Indonesia, terintegrasi dengan artefak repo (`results/esg_records.json`, `results/transfer_learning/`).

Checklist implementasi:
- Dataset builder: `transfer_learning/data_builder.py`
- Training: `transfer_learning/train.py`
- Evaluasi: `transfer_learning/evaluate.py`
- Viewer Streamlit: `transfer_learning/streamlit_transfer_learning.py`

Saran penelitian:
- Gunakan label manusia dari `Ground Truth Workbench` sebagai dataset utama; pseudo-label LLM hanya baseline awal.
- Terapkan split berbasis dokumen/perusahaan untuk menghindari leakage.

