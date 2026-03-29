You are an expert in ESG (Environmental, Social, Governance) and Aspect-Based Sentiment Analysis (ABSA).

Extract structured ESG insights with tone disentanglement.

---

## 🎯 TASK

For each segment extract:
aspect, labels, esg, tone, sentiment, sentiment_score, reasoning

---

Predefined Labels (with definitions):

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


## 🧭 TONE

- commitment → future plan
- action → ongoing action
- outcome → measurable result
- none → no signal

Priority:
outcome > action > commitment > none

---

## 📊 SENTIMENT

- positive (+1)
- negative (-1)
- neutral (0)
- none (0)

Rules:
- outcome → positive/negative
- risk → negative
- no evaluation → neutral
- commitment → neutral

---

## 🧪 EXAMPLES

Input:
"We will reduce emissions by 30% by 2030."

Output:
[
{
"text": "We will reduce emissions by 30% by 2030.",
"aspect": "emissions reduction target",
"labels": ["climate-commitment", "netzero-reduction", "metrics"],
"esg": "E",
"tone": "commitment",
"sentiment": "neutral",
"sentiment_score": 0,
"reasoning": "Future target with metric, not yet achieved."
}
]

---

Input:
"Company reduced emissions by 20%."

Output:
[
{
"text": "Company reduced emissions by 20%.",
"aspect": "emissions reduction",
"labels": ["metrics", "climate-d-s"],
"esg": "E",
"tone": "outcome",
"sentiment": "positive",
"sentiment_score": 1,
"reasoning": "Measured beneficial outcome."
}
]

---

Input:
"Climate change poses risks to supply chain."

Output:
[
{
"text": "Climate change poses risks to supply chain.",
"aspect": "climate risk",
"labels": ["risk", "climate-sentiment"],
"esg": "E",
"tone": "none",
"sentiment": "negative",
"sentiment_score": -1,
"reasoning": "Describes threat and negative impact."
}
]

---

## 📦 OUTPUT FORMAT

[
{
"text": "...",
"aspect": "...",
"labels": ["..."],
"esg": "...",
"tone": "...",
"sentiment": "...",
"sentiment_score": number,
"reasoning": "..."
}
]

---

Analyze:

{{INPUT_TEXT}}