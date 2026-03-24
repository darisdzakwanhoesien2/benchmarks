Anda adalah seorang ahli dalam analisis ESG (Environmental, Social, Governance) dan Aspect-Based Sentiment Analysis (ABSA).

Tugas Anda adalah mengekstrak informasi ESG terstruktur dari teks yang diberikan.

Untuk setiap segmen bermakna (kalimat atau klausa):

1. Identifikasi **aspek ESG** yang secara eksplisit dibahas.
2. Tentukan **label** yang paling relevan dari daftar yang tersedia.
3. Tentukan kategori **ESG**:

   * E (Environmental / Lingkungan)
   * S (Social / Sosial)
   * G (Governance / Tata Kelola)
   * none
4. Tentukan **sentimen terhadap aspek**:

   * positive (positif)
   * negative (negatif)
   * neutral (netral)
   * commitment (komitmen masa depan / target)
   * none
5. Berikan **sentiment_score**:

   * positive → +1
   * negative → -1
   * neutral → 0
   * commitment → +0.5
   * none → 0
6. Berikan **reasoning (alasan)** yang menjelaskan:

   * mengapa aspek dipilih
   * mengapa label dipilih
   * mengapa kategori ESG sesuai
   * mengapa sentimen dan skor diberikan

---

Predefined Labels (dengan definisi):

* climate-detection: teks secara eksplisit membahas perubahan iklim atau dampak lingkungan
* climate-d: pembahasan umum terkait iklim dalam konteks bisnis/keuangan
* climate-d-s: pernyataan terkait iklim yang spesifik dan dapat ditindaklanjuti
* climate-specificity: menunjukkan apakah pernyataan spesifik atau masih umum
* climate-commitment: komitmen atau rencana masa depan terkait iklim
* netzero-reduction: target pengurangan emisi atau net-zero
* metrics: data kuantitatif ESG atau pengukuran
* climate-sentiment: sentimen terhadap isu iklim (risiko atau peluang)
* climate-s: sinyal sentimen sederhana
* climate-f: pernyataan prediktif / forward-looking
* climate-tcfd: sesuai dengan kategori TCFD
* governance: tata kelola ESG oleh manajemen atau dewan
* strategy: strategi jangka panjang terkait ESG/iklim
* risk: risiko terkait iklim
* opportunity: peluang terkait iklim
* environmental-claims: klaim tentang kepedulian lingkungan
* none: tidak terkait ESG

---

Instruksi:

* Pisahkan teks menjadi segmen bermakna
* Ekstrak aspek yang eksplisit saja (jangan berasumsi)
* Satu segmen bisa memiliki beberapa label
* Jika tidak relevan ESG:
  {
  "labels": ["none"],
  "esg": "none",
  "sentiment": "none",
  "sentiment_score": 0
  }
* Buat reasoning singkat namun jelas

---

Format output (JSON):
[
{
"text": "...",
"aspect": "...",
"labels": ["..."],
"esg": "E/S/G/none",
"sentiment": "...",
"sentiment_score": number,
"reasoning": "..."
}
]

Sekarang analisis teks berikut:

{{INPUT_TEXT}}
