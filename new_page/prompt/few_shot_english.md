You are an expert in ESG and Aspect-Based Sentiment Analysis (ABSA).

Extract ESG insights with explanation.

---

Sentiment scoring:

* positive = +1
* negative = -1
* neutral = 0
* commitment = +0.5
* none = 0

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

---

### Examples:

Input:
"We aim to reduce carbon emissions by 40% by 2030."

Output:
[
{
"text": "We aim to reduce carbon emissions by 40% by 2030.",
"aspect": "carbon emissions reduction target",
"labels": ["climate-commitment", "netzero-reduction", "metrics"],
"esg": "E",
"sentiment": "commitment",
"sentiment_score": 0.5,
"reasoning": "Future-oriented emission reduction target with measurable metric (40% by 2030), indicating a concrete climate commitment under environmental category."
}
]

Input:
"Climate change poses significant risks to our supply chain."

Output:
[
{
"text": "Climate change poses significant risks to our supply chain.",
"aspect": "climate risk to supply chain",
"labels": ["risk", "climate-sentiment"],
"esg": "E",
"sentiment": "negative",
"sentiment_score": -1,
"reasoning": "Describes potential harm caused by climate change, clearly indicating environmental risk with negative sentiment."
}
]

Input:
"The board oversees sustainability strategy."

Output:
[
{
"text": "The board oversees sustainability strategy.",
"aspect": "sustainability governance oversight",
"labels": ["governance", "strategy"],
"esg": "G",
"sentiment": "neutral",
"sentiment_score": 0,
"reasoning": "Describes governance responsibility without evaluative tone, hence neutral sentiment in governance category."
}
]

---

### Task:

For each segment:

* Extract aspect
* Assign labels
* Assign ESG category
* Assign sentiment + score
* Provide reasoning

---

### Output format:

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

Now analyze:

{{INPUT_TEXT}}
