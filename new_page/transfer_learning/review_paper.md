# Review Paper: Transfer Learning untuk ESG Aspect-Based Sentiment Analysis (ABSA) Bahasa Indonesia

## Abstrak

ESG Aspect-Based Sentiment Analysis (ESG ABSA) bertujuan mengekstrak aspek-aspek ESG (Environmental, Social, Governance) dari teks, lalu mengklasifikasikan sentimen yang terkait dengan setiap aspek. Pada praktiknya, ESG ABSA di Bahasa Indonesia menghadapi tantangan berupa keterbatasan data berlabel, variasi gaya bahasa laporan keberlanjutan, dominasi kalimat normatif, serta fenomena *code-switching* (Indonesia–Inggris). Review paper ini menyajikan tinjauan terstruktur mengenai transfer learning untuk ESG ABSA Bahasa Indonesia, mencakup pemetaan riset, kesenjangan, pertanyaan penelitian, rancangan metodologi, dan arah kontribusi. Review ini juga mengusulkan rancangan implementasi yang *reproducible* dengan memanfaatkan pipeline yang sudah tersedia pada repositori ini (OCR → ekstraksi → *ground-truth workbench* → metrik/evaluasi → dashboard), serta modul transfer learning yang baru ditambahkan pada folder `transfer_learning/`. Luaran yang ditargetkan adalah kerangka eksperimen end-to-end yang dapat digunakan sebagai dasar tesis atau studi lanjutan: pembangunan dataset, pelatihan model transformer melalui *fine-tuning* atau strategi efisien parameter, evaluasi per-subgroup (pilar/aspek/tone/sektor), dan analisis error yang berorientasi pada validitas eksternal.

**Kata kunci:** ESG, ABSA, Bahasa Indonesia, transfer learning, domain adaptation, sustainability report, evaluasi robust.

---

## 1. Pendahuluan

Pelaporan ESG (Environmental, Social, Governance) semakin menjadi perhatian dalam penilaian kinerja perusahaan dan pengambilan keputusan investasi. Namun, laporan keberlanjutan umumnya panjang, heterogen, dan mengandung campuran narasi strategis, pernyataan kepatuhan, serta indikator kuantitatif. Kondisi ini mendorong kebutuhan otomatisasi analisis, termasuk identifikasi aspek ESG dan sentimen atau nada (*tone*) pengungkapan.

Secara metodologis, ESG ABSA dapat dilihat sebagai perluasan ABSA umum ke domain ESG. Perbedaan penting domain ESG adalah:

1. **Dominasi kalimat normatif** (komitmen/kebijakan) dibanding opini eksplisit.
2. **Ketimpangan distribusi kelas** (aspek tertentu jauh lebih sering muncul).
3. **Pergeseran domain lintas industri dan tahun** (terminologi dan fokus tema berubah).
4. **Bilingual** pada dokumen Indonesia (banyak istilah teknis Inggris).

Transfer learning (khususnya melalui model transformer *pretrained*) menawarkan pendekatan praktis untuk meningkatkan performa pada kondisi data berlabel terbatas, dengan mentransfer pengetahuan dari pretraining umum/multibahasa ke tugas spesifik ESG ABSA Bahasa Indonesia.

---

## 2. Ruang Lingkup dan Definisi

### 2.1 Definisi Tugas

**ESG ABSA** dalam konteks review ini mencakup minimal:

- **Aspek**: kategori topik spesifik (mis. emisi, limbah, keselamatan kerja, anti-korupsi).
- **Pilar ESG**: E/S/G.
- **Sentimen aspek**: umumnya 3 kelas (negatif, netral, positif), tetapi dapat diperluas.
- **Tone** (opsional): tipe pengungkapan seperti komitmen/aksi/hasil atau skema lain yang sepadan.

Repositori ini menggunakan skema label yang sering diperlakukan sebagai 4 dimensi: `esg`, `aspect`, `tone`, dan `sentiment`.

### 2.2 Unit Analisis

Unit yang umum digunakan pada pipeline adalah:

- segmen/kalimat dari dokumen (hasil OCR dan pemotongan teks),
- atau record ekstraksi dari model LLM yang menyertakan `text`, `aspect`, `esg`, `tone`, `sentiment`.

---

## 3. Tinjauan Literatur (Tematik)

Bagian ini menyusun literatur dalam 5 tema, dengan fokus pada implikasi untuk ESG ABSA Bahasa Indonesia.

### 3.1 Transfer Learning dalam NLP

Transfer learning pada NLP umumnya memanfaatkan model *pretrained* (misalnya transformer) yang kemudian diadaptasi ke tugas downstream. Adaptasi dapat berupa:

1. **Feature-based transfer**: encoder dibekukan, hanya melatih *classifier head*.
2. **Full fine-tuning**: semua parameter dilatih ulang pada data target.
3. **Parameter-efficient fine-tuning (PEFT)**: menyesuaikan sebagian parameter (mis. adaptor/LoRA) untuk efisiensi komputasi dan stabilitas eksperimen.

Relevansi ke ESG ABSA Bahasa Indonesia: strategi yang tepat bergantung pada ukuran dataset berlabel, risiko *overfitting*, serta kebutuhan replikasi hasil.

### 3.2 ABSA: Pipeline vs Joint Learning

ABSA dapat dibangun sebagai:

- **pipeline**: deteksi/klasifikasi aspek → klasifikasi sentimen per aspek,
- **joint learning**: model tunggal memprediksi aspek dan sentimen secara bersamaan,
- **sequence labeling**: menandai span aspek (lebih sulit, tetapi informatif).

Untuk ESG ABSA, pipeline sering lebih mudah diintegrasikan dan dievaluasi, tetapi rawan akumulasi error. Multi-task learning (aspek + sentimen + tone) dapat dilihat sebagai jalan tengah yang praktis.

### 3.3 Low-Resource dan Cross-Lingual/Multi-Lingual Adaptation

Bahasa Indonesia sering berada pada spektrum low-resource relatif terhadap English, terutama untuk domain khusus ESG. Pada dokumen ESG Indonesia, isu tambahan adalah:

- *code-switching*,
- istilah teknis,
- variasi penulisan perusahaan,
- struktur laporan yang tidak seragam.

Hal ini menguatkan argumentasi transfer learning dari model multilingual atau model yang dilatih khusus Bahasa Indonesia.

### 3.4 Domain Adaptation untuk Teks Keuangan/Keberlanjutan

Domain ESG memiliki karakteristik wacana yang berbeda dari ulasan produk atau media sosial. Model yang kuat pada ABSA umum belum tentu stabil di ESG. Adaptasi domain menuntut evaluasi yang menyorot:

- performa per pilar,
- performa per aspek,
- stabilitas lintas industri,
- generalisasi lintas tahun.

### 3.5 Evaluasi yang Reliabel dan Robust

Evaluasi ABSA yang hanya melaporkan satu metrik agregat sering menutupi masalah penting:

1. **Ketimpangan kelas**: aspek jarang akan “tenggelam” pada metrik global.
2. **Subgroup performance**: pilar Social (S) sering underrepresented.
3. **Kebocoran data**: kalimat dari dokumen yang sama masuk train dan test.
4. **Robustness**: performa turun tajam pada sektor/out-of-domain.

---

## 4. Kesenjangan Riset (Research Gap)

Berdasarkan kebutuhan domain dan kondisi pipeline yang sudah tersedia di repositori ini, kesenjangan yang menonjol adalah:

1. **Belum ada baseline transformer fine-tuning yang terstruktur** untuk ESG ABSA Bahasa Indonesia yang terhubung langsung ke artefak evaluasi yang sudah ada.
2. **Belum ada protokol benchmarking yang jelas** untuk memisahkan:
   - performa “in-domain” (dokumen yang mirip),
   - dari performa “out-of-domain” (sektor/tahun berbeda).
3. **Keterbatasan dataset berlabel** menghambat pengujian strategi transfer yang berbeda (feature-based vs full FT vs PEFT).
4. **Analisis error masih belum berorientasi keputusan**: apa konsekuensi kesalahan pada tiap pilar/aspek, dan bagaimana prioritas perbaikan.

---

## 5. Pertanyaan Penelitian (Research Questions)

RQ1. Apakah transfer learning menggunakan model transformer dapat meningkatkan performa ESG ABSA Bahasa Indonesia dibanding baseline non-transformer atau rule-based?

RQ2. Strategi adaptasi mana yang paling efektif dan efisien untuk kondisi data dan sumber daya komputasi yang tersedia: feature-based, full fine-tuning, atau PEFT?

RQ3. Seberapa robust performa model transfer learning terhadap variasi pilar ESG, aspek langka, tone, dan sektor industri?

RQ4. Berapa kebutuhan minimum data berlabel yang realistis agar transfer learning memberi peningkatan yang stabil dan dapat dipertanggungjawabkan secara ilmiah?

---

## 6. Tujuan Penelitian (Objectives)

1. Menyusun pipeline eksperimen transfer learning yang dapat direplikasi dari data mentah/artefak hingga laporan metrik.
2. Menghasilkan baseline transformer untuk ESG ABSA Bahasa Indonesia dan membandingkannya dengan baseline yang sudah ada di repositori.
3. Menyajikan evaluasi per-subgroup dan analisis error yang memadai untuk argumen ilmiah (tesis/paper).
4. Menghasilkan rekomendasi praktis tentang strategi adaptasi terbaik untuk kondisi low-resource ESG Indonesia.

---

## 7. Kontribusi yang Diharapkan (Expected Contributions)

1. Kerangka eksperimen end-to-end untuk ESG ABSA Bahasa Indonesia yang menyatukan ekstraksi, pelabelan, training, evaluasi, dan visualisasi.
2. Bukti empiris terkait kapan transfer learning efektif dan kapan tidak, khususnya pada aspek langka dan dokumen lintas sektor.
3. Artefak yang dapat digunakan ulang: dataset JSONL, label vocab, model checkpoint, dan metrik/diagnostik.
4. Basis untuk agenda riset lanjutan: perluasan taksonomi aspek, learning curve, dan validasi lintas tahun.

---

## 8. Metodologi yang Diusulkan (Proposed Methodology)

Bagian ini menekankan implementasi yang bisa langsung dijalankan pada repositori ini.

### 8.1 Sumber Data dan Pipeline Repositori

Repositori sudah menyediakan:

- OCR dan ingest dokumen (untuk membangun korpus),
- ekstraksi record ESG ABSA berbasis LLM yang menyertakan `text/aspect/esg/tone/sentiment`,
- *ground truth workbench* dan halaman metrik,
- baseline rule-based dan classical ML.

Dalam praktik, dataset awal yang paling cepat untuk transfer learning adalah `results/esg_records.json` (record ekstraksi), dengan catatan bahwa ini **pseudo-label** dan perlu ditingkatkan dengan label manusia untuk klaim ilmiah yang kuat.

### 8.2 Konstruksi Dataset

Tahapan konstruksi dataset yang disarankan:

1. Ekstrak record (text/aspect/sentiment/tone/esg) dari artefak hasil ekstraksi.
2. Normalisasi label:
   - sentimen ke skema 3 kelas,
   - tone ke skema yang konsisten,
   - pilar ESG ke E/S/G (opsional bila tersedia).
3. Buat split train/val/test:
   - **disarankan split berbasis dokumen/perusahaan**, bukan split acak per kalimat.
4. Audit kualitas label:
   - sampling manual,
   - cek distribusi kelas,
   - cek duplikasi teks.

### 8.3 Model dan Strategi Transfer Learning

Untuk baseline yang dapat dijalankan cepat:

- gunakan transformer pretrained,
- gunakan klasifier multi-head:
  - head aspek,
  - head sentimen,
  - head tone (opsional).

Strategi lanjutan:

1. Full fine-tuning vs feature-based transfer sebagai ablation awal.
2. PEFT untuk skenario terbatas GPU/memori (jika ingin diperluas).

### 8.4 Evaluasi dan Analisis

Rekomendasi evaluasi:

1. Metrik agregat:
   - accuracy, macro-F1 (lebih informatif untuk label tidak seimbang).
2. Confusion matrix untuk sentimen dan aspek.
3. Slice evaluation:
   - per pilar ESG,
   - per aspek top-k,
   - per tone,
   - per sektor.
4. Error analysis:
   - contoh kesalahan teratas,
   - kategori penyebab (ambigu, code-switching, normatif, data noise).

---

## 9. Implementasi di Repositori (Reproducible Blueprint)

Review ini merekomendasikan implementasi minimal berikut (sudah disediakan di folder `transfer_learning/`):

1. **Dataset builder**:
   - `transfer_learning/data_builder.py`
   - input: `results/esg_records.json`
   - output: `results/transfer_learning/dataset.jsonl` dan ringkasan distribusi.
2. **Training**:
   - `transfer_learning/train.py`
   - output run: `results/transfer_learning/run_XXX/` berisi `config.json`, `history.json`, `model.pt`.
3. **Evaluasi**:
   - `transfer_learning/evaluate.py`
   - output: `metrics.json` (termasuk confusion matrix).
4. **Viewer**:
   - `transfer_learning/streamlit_transfer_learning.py`
   - menampilkan metrik dan confusion matrix.

Catatan praktis: bagian training/evaluasi membutuhkan environment Python yang memiliki `torch` + `transformers`. Jika environment sistem mengikuti PEP 668, gunakan virtual environment dan pastikan ruang disk cukup.

---

## 10. Sintesis Temuan dan Implikasi (Synthesis)

Secara konseptual, transfer learning paling mungkin memberi keuntungan pada:

1. aspek yang cukup sering muncul,
2. kalimat yang eksplisit menyebut indikator atau program,
3. pola bahasa yang konsisten (tidak terlalu banyak code-switching),
4. kondisi ketika baseline rule-based/classical ML sulit menangkap variasi sinonim dan struktur kalimat.

Sebaliknya, tantangan yang kemungkinan tetap dominan:

1. aspek langka dan definisi aspek yang tumpang tindih,
2. kalimat normatif (komitmen) yang sulit dibedakan dari aksi/hasil tanpa konteks lebih luas,
3. pergeseran domain lintas sektor dan tahun,
4. bias label jika dataset awal berbasis pseudo-label.

---

## 11. Keterbatasan Review

1. Review ini berfokus pada rancangan dan implementasi *blueprint* yang terintegrasi dengan kode repositori; bukan meta-analisis kuantitatif dari studi-studi terdahulu.
2. Klaim performa numerik bergantung pada eksekusi eksperimen dan kualitas label; karena itu paper ini menekankan protokol evaluasi dan validitas.
3. Pseudo-label dapat membantu bootstrap, tetapi tidak boleh menjadi dasar satu-satunya untuk kesimpulan ilmiah.

---

## 12. Kesimpulan

Transfer learning merupakan pendekatan yang sangat relevan untuk ESG ABSA Bahasa Indonesia karena kondisi data berlabel terbatas dan kompleksitas wacana ESG. Untuk memastikan kontribusi ilmiah yang kuat, penelitian perlu menekankan: (i) kualitas dan standardisasi label, (ii) split evaluasi yang mencegah kebocoran dokumen, (iii) pelaporan metrik per-subgroup, dan (iv) analisis error yang memandu prioritas perbaikan. Dengan memanfaatkan pipeline yang sudah ada di repositori ini dan modul `transfer_learning/` yang disediakan, studi ESG ABSA Indonesia dapat dilakukan secara lebih terstruktur, transparan, dan dapat direplikasi.

---

## Referensi (Placeholder)

Dokumen ini tidak menyertakan sitasi formal per-paper. Untuk versi publikasi, tambahkan referensi primer pada tema:

1. Transfer learning transformer untuk NLP.
2. ABSA (pipeline dan joint learning).
3. Cross-lingual / multilingual adaptation.
4. Domain adaptation untuk teks finansial/ESG.
5. Metodologi evaluasi robust dan subgroup analysis.

