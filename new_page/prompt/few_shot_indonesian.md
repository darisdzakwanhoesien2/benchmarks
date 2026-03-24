Anda adalah ahli ESG dan ABSA.

Ekstrak informasi ESG secara terstruktur beserta penjelasan.

---

Skor sentimen:

* positive = +1
* negative = -1
* neutral = 0
* commitment = +0.5
* none = 0

---

Predefined Labels (dengan definisi):

* climate-detection: teks membahas perubahan iklim
* climate-d: pembahasan umum iklim
* climate-d-s: pernyataan spesifik dan konkret
* climate-specificity: tingkat spesifik vs umum
* climate-commitment: komitmen masa depan
* netzero-reduction: target pengurangan emisi
* metrics: data kuantitatif
* climate-sentiment: sentimen risiko/peluang
* climate-s: sentimen sederhana
* climate-f: pernyataan prediksi
* climate-tcfd: sesuai kerangka TCFD
* governance: tata kelola
* strategy: strategi
* risk: risiko
* opportunity: peluang
* environmental-claims: klaim lingkungan
* none: tidak relevan

---

### Contoh:

Input:
"Kami menargetkan pengurangan emisi karbon sebesar 40% pada tahun 2030."

Output:
[
{
"text": "Kami menargetkan pengurangan emisi karbon sebesar 40% pada tahun 2030.",
"aspect": "target pengurangan emisi karbon",
"labels": ["climate-commitment", "netzero-reduction", "metrics"],
"esg": "E",
"sentiment": "commitment",
"sentiment_score": 0.5,
"reasoning": "Kalimat menunjukkan target masa depan yang terukur (40% pada 2030), sehingga merupakan komitmen lingkungan dengan data kuantitatif."
}
]

Input:
"Perubahan iklim menimbulkan risiko besar terhadap rantai pasok kami."

Output:
[
{
"text": "Perubahan iklim menimbulkan risiko besar terhadap rantai pasok kami.",
"aspect": "risiko iklim terhadap rantai pasok",
"labels": ["risk", "climate-sentiment"],
"esg": "E",
"sentiment": "negative",
"sentiment_score": -1,
"reasoning": "Kalimat menekankan dampak negatif dari perubahan iklim terhadap operasi bisnis, sehingga termasuk risiko dengan sentimen negatif."
}
]

---

### Tugas:

Untuk setiap segmen:

* Ekstrak aspek
* Tentukan label
* Tentukan kategori ESG
* Tentukan sentimen + skor
* Berikan reasoning

---

Format output:
[
{
"text": "...",
"aspect": "...",
"labels": ["..."],
"esg": "...",
"sentiment": "...",
"sentiment_score": number,
"reasoning": "..."
}
]

Sekarang analisis:

{{INPUT_TEXT}}
