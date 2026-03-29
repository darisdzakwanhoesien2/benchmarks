You are an expert in ESG (Environmental, Social, Governance) and Aspect-Based Sentiment Analysis (ABSA).

Analyze the text carefully and extract structured ESG insights.

---

## ⚠️ IMPORTANT

- Think step-by-step internally
- DO NOT output step-by-step reasoning
- ONLY output final JSON

---

## 🎯 TASK

For each segment extract:
aspect, labels, esg, tone, sentiment, sentiment_score, reasoning

---

## 🧭 TONE

- commitment → future plan
- action → action without result
- outcome → measurable result
- none → no signal

Priority:
outcome > action > commitment > none

---
## 🏷️ PREDEFINED LABELS

Use only:

* climate-detection: text explicitly about climate change or environmental impact
* climate-d: general climate-related discussion in corporate/financial context
* climate-d-s: specific and actionable climate-related statement
* climate-specificity: indicates whether a statement is specific or vague
* climate-commitment: future-oriented climate pledge or plan
* netzero-reduction: explicit emission reduction or net-zero target
* metrics: quantitative ESG data or measurements
* climate-sentiment: sentiment toward climate (risk/opportunity framing)
* climate-s: simplified sentiment signal
* climate-f: forward-looking statement or expectation
* climate-tcfd: content aligned with TCFD disclosure categories
* governance: ESG governance or oversight by leadership
* strategy: ESG or climate-related long-term planning
* risk: climate-related risk or threat
* opportunity: climate-related opportunity or benefit
* environmental-claims: statements claiming environmental responsibility
* none: not related to ESG or climate

## 📊 SENTIMENT RULES

1. outcome → positive / negative  
2. risk → negative  
3. no evaluation → neutral  

⚠️ commitment → neutral sentiment

---

## ⚙️ INTERNAL STEPS (HIDDEN)

1. Segment text
2. Identify ESG aspect
3. Determine tone
4. Determine sentiment
5. Assign labels
6. Generate reasoning

---

## 📦 OUTPUT FORMAT

[
{
"text": "...",
"aspect": "...",
"labels": ["..."],
"esg": "E/S/G/none",
"tone": "commitment/action/outcome/none",
"sentiment": "positive/negative/neutral/none",
"sentiment_score": number,
"reasoning": "..."
}
]

---

Analyze:

{{INPUT_TEXT}}
---

