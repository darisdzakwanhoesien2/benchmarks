You are an expert in ESG and Aspect-Based Sentiment Analysis (ABSA).

Extract ESG insights with explanation.

### Sentiment scoring:

* positive = +1
* negative = -1
* neutral = 0
* commitment = +0.5
* none = 0

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
"reasoning": "The sentence describes a future pledge to reduce emissions with a specific target (40% by 2030), indicating a measurable climate commitment. This aligns with environmental (E) category and commitment sentiment."
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
"reasoning": "The sentence highlights potential harm caused by climate change, which is clearly a risk. This reflects negative sentiment and belongs to environmental (E) category."
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
"reasoning": "The sentence describes governance structure without positive or negative judgment. It is factual, thus neutral sentiment under governance (G)."
}
]

### Task:

For each segment:

* Extract aspect
* Assign labels
* Assign ESG category
* Assign sentiment + score
* Provide reasoning

Predefined Labels:

* climate-commitment
* climate-detection
* environmental-claims
* climate-d
* climate-d-s
* climate-f
* climate-s
* climate-sentiment
* climate-specificity
* climate-tcfd
* netzero-reduction
* opportunity
* risk
* governance
* metrics
* strategy
* none

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
