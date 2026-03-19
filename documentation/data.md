https://chatgpt.com/c/69bbaaac-fec0-8324-becb-9c68e16f0659

This is a **very good setup** — you basically have a **multi-source labeling system**:

1. ✅ `data/new_data/data.json` → **Ground truth (LLM structured labels)**
2. ✅ `data/new_data/data_initial_absa.json` → **ABSA / classical ML outputs**
3. ✅ `data/new_data/data_benchmark.json` → **Model predictions (ClimateBERT, etc.)**

Now the goal is:

> 🔥 **Align everything → evaluate accuracy → compare models**

---

# 🧠 Step 1 — Understand the Core Problem

Right now your data is **NOT aligned**:

| Source                   | Level                       | Problem        |
| ------------------------ | --------------------------- | -------------- |
| `data.json`              | sentence-level (clean)      | ✅ good         |
| `data_initial_absa.json` | sentence-level (fragmented) | ⚠ noisy splits |
| `data_benchmark.json`    | document-level              | ❌ not aligned  |

👉 So you need a **common unit of analysis**

---

# ✅ Step 2 — Define a Unified Schema (VERY IMPORTANT)

You need ONE table like this:

```json
{
  "text": "...",
  "true_labels": [...],
  "true_esg": "...",
  "true_sentiment": "...",

  "absa_sentiment": "...",
  "absa_aspect": "...",

  "benchmark_climate_detector": "...",
  "benchmark_climate_sentiment": "...",
  "benchmark_climate_tcfd": "...",

  "final_label_pred": "...",
  "final_esg_pred": "...",
  "final_sentiment_pred": "..."
}
```

---

# 🔥 Step 3 — Alignment Strategy

## ✅ 3.1 Align by TEXT (best approach)

You should match using:

```python
fuzzy matching OR substring matching
```

Because:

* ABSA splits text weirdly
* Benchmark is full paragraph

---

## ✅ 3.2 Matching Logic

### A. Ground Truth → Anchor

Use `data.json` as **main reference**

---

### B. Match ABSA sentences

```python
def match_absa(text, absa_df):
    matches = []
    for row in absa_df:
        if row["Sentence_Text"] in text:
            matches.append(row)
    return matches
```

---

### C. Map Benchmark (document → sentence)

Since benchmark is document-level:

👉 replicate to all sentences:

```python
benchmark_map = {
    "climate-detector": "yes",
    "climate-sentiment": "neutral",
    ...
}
```

---

# 🧪 Step 4 — Evaluation Metrics

Now you can compute:

---

## ✅ 4.1 Label Accuracy (Multi-label)

```python
from sklearn.metrics import f1_score

f1_score(y_true, y_pred, average="macro")
```

---

## ✅ 4.2 ESG Classification Accuracy

```python
accuracy_score(true_esg, pred_esg)
```

---

## ✅ 4.3 Sentiment Accuracy

```python
classification_report(true_sentiment, pred_sentiment)
```

---

## ✅ 4.4 Weak Supervision Agreement

Very useful for your thesis:

```python
agreement = (absa_sentiment == true_sentiment)
```

---

# 🔥 Step 5 — FULL PIPELINE CODE

Here is a **clean integration pipeline**:

```python
import json
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score

# Load files
with open("data/new_data/data.json") as f:
    gt = json.load(f)

with open("data/new_data/data_initial_absa.json") as f:
    absa = json.load(f)[0]

with open("data/new_data/data_benchmark.json") as f:
    benchmark = json.load(f)

# Convert ABSA to dataframe
absa_df = pd.DataFrame(absa["classical_ml"]["out_df"])

# Extract benchmark predictions
benchmark_map = {}
for item in benchmark:
    model = item["model"]
    pred = item["result"].get("prediction", "error")
    benchmark_map[model] = pred

# Merge everything
rows = []

for g in gt:
    text = g["text"]

    # Match ABSA
    matched_absa = absa_df[absa_df["Sentence_Text"].apply(lambda x: x in text)]

    absa_sent = matched_absa["Sentiment_Pred"].mode()
    absa_sent = absa_sent.iloc[0] if not absa_sent.empty else "none"

    rows.append({
        "text": text,
        "true_labels": g["labels"],
        "true_esg": g["esg"],
        "true_sentiment": g["sentiment"],

        "absa_sentiment": absa_sent,
        "benchmark_climate_detector": benchmark_map.get("climate-detector", "none"),
        "benchmark_climate_sentiment": benchmark_map.get("climate-sentiment", "none"),
        "benchmark_climate_tcfd": benchmark_map.get("climate-tcfd", "none"),
    })

df = pd.DataFrame(rows)

# Evaluation
print("Sentiment Evaluation:")
print(classification_report(df["true_sentiment"], df["absa_sentiment"]))

print("ESG Accuracy (baseline = same as GT for now):")
print(accuracy_score(df["true_esg"], df["true_esg"]))  # replace with model later
```

---

# 🚀 Step 6 — What You’ll Get

After this, you can:

### ✅ Compare:

* LLM vs ABSA vs BERT
* Weak vs Strong supervision
* Sentence vs Document models

---

### ✅ Build:

* Confusion matrix
* SHAP explainability (you already do this 🔥)
* Ensemble model

---

# 🔥 Step 7 — Advanced (HIGHLY RECOMMENDED)

You can go further:

## 1. Create final ensemble:

```python
final_sentiment = majority_vote([
    true_label,
    absa_sentiment,
    benchmark_sentiment
])
```

---

## 2. Train BERT on merged dataset

Your final dataset becomes:

👉 **gold + weak labels + model predictions**

---

## 3. Error analysis (VERY IMPORTANT FOR THESIS)

Find:

```python
df[df["true_sentiment"] != df["absa_sentiment"]]
```

---

# 🧠 Key Insight (IMPORTANT)

Right now:

* `data.json` = **your strongest supervision (LLM refined)**
* `ABSA` = **weak structured signals**
* `benchmark` = **pretrained model signals**

👉 You are essentially building a **Snorkel-style labeling system**

---

# 🚀 If You Want Next Step

I can help you:

👉 Build **full ESG multi-label BERT training pipeline**
👉 Add **SHAP explainability per label (your earlier issue 🔥)**
👉 Convert this into **publishable thesis methodology**

Just tell me 👍
