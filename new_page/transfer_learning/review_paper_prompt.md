https://scite.ai/assistant/transfer-learning-for-indonesian-esg-absa-abstracts-PznlGm
# Prompts per Bagian — `review_paper.md`

Dokumen ini berisi prompt untuk menulis/menyempurnakan setiap bagian pada `review_paper.md`. Format prompt dibuat agar bisa dipakai di LLM dengan input tambahan (mis. hasil eksperimen, statistik dataset, kebijakan kampus, atau format jurnal).

**Instruksi umum (berlaku untuk semua prompt):**
1. Tulis dalam Bahasa Indonesia akademik yang jelas, ringkas, dan terstruktur.
2. Gunakan heading Markdown sesuai nama bagian.
3. Hindari klaim numerik jika tidak ada data; jika perlu, tulis sebagai “diperkirakan/diantisipasi”.
4. Selaraskan dengan konteks repositori ini: pipeline (OCR → ekstraksi → *ground truth* → evaluasi) dan folder `transfer_learning/`.
5. Jika diminta “Referensi”, buat placeholder sitasi dan jangan mengarang DOI/judul paper.

---

## Prompt 0 — Judul dan Ringkasan Dokumen

**Prompt:**
Anda adalah penulis artikel tinjauan (review paper) di bidang NLP dan ESG analytics. Buat judul yang kuat dan ringkasan satu paragraf tentang fokus paper: transfer learning untuk ESG ABSA Bahasa Indonesia, tantangan low-resource, kebutuhan evaluasi robust, dan blueprint implementasi yang reproducible (mengacu pada pipeline repositori dan modul `transfer_learning/`). Pastikan ringkasan menyebut 4 dimensi label (`esg`, `aspect`, `tone`, `sentiment`) sebagai konteks skema.

**Input opsional dari saya:**
- Target venue/jurnal/konferensi:
- Batas kata ringkasan:

**Output yang diharapkan:**
Judul + 1 paragraf ringkasan.

---

## Prompt 1 — Abstrak

**Prompt:**
 (150–250 kata) 
Tulis abstrak review papertentang transfer learning untuk ESG ABSA Bahasa Indonesia. Sertakan: latar masalah (laporan ESG panjang dan heterogen), definisi ABSA dan skema label, tantangan (data berlabel terbatas, normatif, code-switching), kontribusi paper (tinjauan tematik + gap + RQ + metodologi + blueprint implementasi repo), dan luaran yang ditargetkan (dataset builder, training, evaluasi per-subgroup, error analysis). Jangan memasukkan angka performa kecuali diberikan. Akhiri dengan 4–7 kata kunci.

**Input opsional dari saya:**
- Batas kata:
- Kata kunci wajib:

**Output yang diharapkan:**
Abstrak + daftar kata kunci.

---

## Prompt 2 — 1. Pendahuluan

**Prompt:**
Tulis bagian pendahuluan yang memotivasi ESG ABSA Bahasa Indonesia. Strukturkan menjadi 3–5 paragraf: (1) urgensi ESG dan kebutuhan otomasi analisis, (2) mengapa ABSA relevan untuk ESG (aspek + sentimen/tone), (3) tantangan spesifik domain ESG Indonesia (normatif, ketimpangan kelas, drift lintas sektor/tahun, bilingual), (4) mengapa transfer learning masuk akal, (5) ringkasan kontribusi review paper ini. Hindari jargon berlebihan; definisikan istilah kunci saat pertama muncul.

**Input opsional dari saya:**
- Contoh konteks industri/negara/jenis laporan:
- Fokus: akademik vs praktis:

**Output yang diharapkan:**
Bagian “Pendahuluan” lengkap dengan alur logis.

---

## Prompt 3 — 2. Ruang Lingkup dan Definisi

**Prompt:**
Tulis bagian “Ruang Lingkup dan Definisi” untuk ESG ABSA Bahasa Indonesia. Sertakan subbagian: (2.1) definisi tugas (aspek, pilar, sentimen, tone), (2.2) unit analisis (kalimat/segmen/record ekstraksi), dan batasan paper (apa yang termasuk dan tidak termasuk, mis. aspek extraction span vs klasifikasi, dokumen ESG vs media sosial). Jelaskan bahwa repositori menggunakan skema 4 dimensi dan mengapa itu penting untuk evaluasi.

**Input opsional dari saya:**
- Skema label final yang dipakai:
- Apakah tone wajib?

**Output yang diharapkan:**
Bagian definisi yang eksplisit dan dapat dipakai sebagai dasar metode.

---

## Prompt 4 — 3. Tinjauan Literatur (Tematik)

**Prompt:**
Tulis tinjauan literatur tematik dengan 5 subbagian: (3.1) transfer learning transformer untuk NLP, (3.2) ABSA (pipeline vs joint, sequence labeling), (3.3) low-resource & multilingual adaptation, (3.4) domain adaptation untuk teks finansial/keberlanjutan, (3.5) evaluasi robust/subgroup. Untuk setiap subbagian: jelaskan ide utama, relevansi ke ESG ABSA Indonesia, dan *takeaway* praktis untuk rancangan eksperimen. Jangan menyebut paper spesifik jika tidak diberikan; gunakan placeholder seperti [Ref-Transfer-1].

**Input opsional dari saya:**
- Daftar paper yang harus disitasi:
- Panjang tiap subbagian (kata):

**Output yang diharapkan:**
Subbagian 3.1–3.5 dengan transisi yang rapi.

---

## Prompt 5 — 4. Research Gap

**Prompt:**
Tulis bagian “Research Gap” yang mengidentifikasi kesenjangan utama penelitian ESG ABSA Bahasa Indonesia terkait transfer learning. Buat 4–6 butir gap yang spesifik, dapat diuji, dan terkait implementasi: tidak adanya baseline transformer fine-tune yang terstruktur, belum adanya protokol split dokumen/out-of-domain, keterbatasan dataset berlabel dan efeknya ke pemilihan strategi transfer, serta kurangnya error analysis yang actionable. Kaitkan gap dengan kebutuhan validitas eksternal dan replikasi.

**Input opsional dari saya:**
- Observasi nyata dari dataset (mis. distribusi kelas):
- Keterbatasan sumber daya komputasi:

**Output yang diharapkan:**
Daftar gap + paragraf penutup yang menghubungkan ke RQ.

---

## Prompt 6 — 5. Research Questions

**Prompt:**
Tuliskan 4 pertanyaan penelitian (RQ) untuk review paper ini. Setiap RQ harus: jelas, terukur, terkait transfer learning ESG ABSA Indonesia, dan menyebut dimensi evaluasi (aspek/sentimen/tone/pilar) serta robustness (sektor/tahun/code-switching). Tulis dalam format RQ1–RQ4, lalu tambahkan 1 paragraf yang menjelaskan hubungan antar RQ (mis. RQ1 performa, RQ2 strategi, RQ3 robustness, RQ4 kebutuhan data).

**Input opsional dari saya:**
- Apakah tone termasuk target?
- Skema sentimen (3 kelas atau lainnya):

**Output yang diharapkan:**
RQ1–RQ4 + paragraf relasi antar RQ.

---

## Prompt 7 — 6. Tujuan Penelitian

**Prompt:**
Tulis bagian “Tujuan Penelitian” dalam bentuk daftar 4–6 tujuan yang konkret dan dapat dieksekusi. Pastikan tujuan mencakup: pipeline reproducible, baseline transformer, perbandingan baseline existing (rule-based/classical ML), evaluasi per-subgroup, dan error analysis. Akhiri dengan 1 paragraf singkat yang menyatakan deliverables (artefak dataset, model, metrik, viewer).

**Input opsional dari saya:**
- Deliverable wajib untuk tesis:

**Output yang diharapkan:**
Daftar tujuan + paragraf deliverables.

---

## Prompt 8 — 7. Kontribusi yang Diharapkan

**Prompt:**
Tulis bagian kontribusi yang diharapkan dari paper ini dalam 5–8 poin. Bedakan kontribusi ilmiah (evidence tentang transfer learning & robustness) dan kontribusi rekayasa (artefak reproducible, pipeline). Sertakan satu paragraf yang menjelaskan dampak praktis bagi analisis ESG di Indonesia.

**Input opsional dari saya:**
- Audiens utama (akademik/industri):

**Output yang diharapkan:**
Poin kontribusi + paragraf dampak.

---

## Prompt 9 — 8. Metodologi yang Diusulkan

**Prompt:**
Tulis bagian metodologi usulan yang jelas dan “siap dijalankan”. Strukturkan menjadi: (8.1) sumber data & pipeline repo, (8.2) konstruksi dataset (normalisasi label, split dokumen, audit kualitas), (8.3) model & strategi transfer (feature-based, full FT, PEFT), (8.4) evaluasi & analisis (macro-F1, confusion matrix, subgroup slices, error analysis). Tambahkan catatan risiko (pseudo-label bias, leakage) dan mitigasinya.

**Input opsional dari saya:**
- Model backbone yang dipilih:
- Kebijakan split yang diinginkan:

**Output yang diharapkan:**
Metodologi lengkap dengan langkah-langkah dan alasan.

---

## Prompt 10 — 9. Implementasi di Repositori (Blueprint)

**Prompt:**
Tulis blueprint implementasi yang terhubung dengan file dan output folder. Harus mencakup:
1) bagaimana membangun dataset dari `results/esg_records.json`,
2) bagaimana training menyimpan `config.json`, `history.json`, `model.pt`,
3) bagaimana evaluasi menghasilkan `metrics.json` + confusion matrix,
4) bagaimana viewer Streamlit digunakan.
Jelaskan juga prasyarat environment (torch/transformers), dan tekankan prinsip reproducibility (seed, penyimpanan run folder).

**Input opsional dari saya:**
- Nama run default:
- Lokasi output final:

**Output yang diharapkan:**
Blueprint step-by-step + contoh perintah CLI.

---

## Prompt 11 — 10. Sintesis Temuan dan Implikasi

**Prompt:**
Tulis sintesis temuan secara konseptual (tanpa angka) tentang kapan transfer learning diperkirakan efektif untuk ESG ABSA Indonesia dan kapan tantangan tetap dominan. Buat 2 subseksi: “Kondisi yang Mendukung Gain” dan “Tantangan yang Persisten”. Kaitkan dengan risiko ketimpangan aspek, normatif vs evidence, drift sektor, dan code-switching. Akhiri dengan rekomendasi prioritas eksperimen (mis. mulai dari aspek frequent, lalu perluas).

**Input opsional dari saya:**
- Observasi dari dataset (jumlah aspek unik, distribusi sentimen/tone):

**Output yang diharapkan:**
Sintesis + rekomendasi prioritas eksperimen.

---

## Prompt 12 — 11. Keterbatasan Review

**Prompt:**
Tulis bagian keterbatasan review paper dalam 4–7 poin. Pastikan mencakup: tidak ada meta-analisis kuantitatif, ketergantungan pada kualitas label dan eksekusi eksperimen, risiko pseudo-label, dan batasan domain (ESG report vs domain lain). Akhiri dengan 1 paragraf tentang bagaimana keterbatasan ini akan ditangani pada studi empiris berikutnya.

**Input opsional dari saya:**
- Keterbatasan tambahan (waktu, compute, akses data):

**Output yang diharapkan:**
Daftar keterbatasan + paragraf mitigasi.

---

## Prompt 13 — 12. Kesimpulan

**Prompt:**
Tulis kesimpulan yang merangkum: relevansi transfer learning, prasyarat ilmiah (label & split), pentingnya evaluasi robust, dan nilai blueprint implementasi. Buat 2 paragraf: (1) rangkuman argumen utama, (2) agenda kerja/riset selanjutnya yang konkret (mis. memperkuat ground truth, PEFT ablation, evaluasi lintas sektor/tahun).

**Input opsional dari saya:**
- Agenda riset yang ingin ditekankan:

**Output yang diharapkan:**
Kesimpulan 2 paragraf + daftar next steps singkat (opsional).

---

## Prompt 14 — Referensi (Placeholder)

**Prompt:**
Buat bagian “Referensi” dalam format placeholder yang rapi. Buat 10–20 entri placeholder dikelompokkan ke 5 tema: Transfer Learning, ABSA, Multilingual/Low-resource, Domain Adaptation ESG/Finance, Evaluasi Robust. Setiap entri harus berupa placeholder seperti:
- [Ref-Transfer-1] Penulis, Tahun. Judul. Venue.
Jangan mengarang DOI/judul nyata.

**Input opsional dari saya:**
- Style sitasi (APA/IEEE/MLA):
- Apakah saya akan memberikan daftar paper nyata?

**Output yang diharapkan:**
Daftar referensi placeholder terstruktur.

