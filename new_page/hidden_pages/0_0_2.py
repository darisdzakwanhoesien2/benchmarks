# ...existing code...
import re
import json
from typing import Dict, Any

def parse_prediction_str(s: str) -> Dict[str, Any]:
    """Parse prediction strings like:
       - 'Label: 1.00'
       - 'Label\\n1.00'
       - 'Predictions for ...:\\nLabel: 1.00'
       - JSON arrays/dicts
    Returns structured dict: {'labels_scores': {...}, 'top_label': ..., 'top_score': ...} or {'raw': s}.
    """
    if not s or not str(s).strip():
        return {"raw": ""}
    s = str(s).strip()

    # Try JSON first
    try:
        j = json.loads(s)
        if isinstance(j, dict):
            # assume dict label->score or nested predictions
            out = {k: float(v) for k, v in j.items() if _is_number_like(v)}
            if out:
                top = max(out.items(), key=lambda x: x[1])
                return {"labels_scores": out, "top_label": top[0], "top_score": top[1]}
            return {"raw_json": j}
        if isinstance(j, list):
            out = {}
            for item in j:
                if isinstance(item, dict):
                    # try common keys
                    label = item.get("label") or item.get("text") or item.get("aspect")
                    score = item.get("score") or item.get("sentiment_score") or item.get("prob") or item.get("confidence")
                    if label and _is_number_like(score):
                        out[str(label)] = float(score)
            if out:
                top = max(out.items(), key=lambda x: x[1])
                return {"labels_scores": out, "top_label": top[0], "top_score": top[1]}
            return {"raw_json": j}
    except Exception:
        pass

    # Remove leading "Predictions for ..." prefix
    s2 = re.sub(r"^Predictions for[\s\S]*?:\s*", "", s, flags=re.IGNORECASE).strip()

    # 1) label: score pairs
    pairs = re.findall(r"([^\n:]+?)\s*:\s*([0-9]*\.?[0-9]+)", s2)
    if pairs:
        out = {lab.strip(): float(sc) for lab, sc in pairs}
        top = max(out.items(), key=lambda x: x[1])
        return {"labels_scores": out, "top_label": top[0], "top_score": top[1]}

    # 2) label newline score pairs
    lines = [ln.strip() for ln in s2.splitlines() if ln.strip()]
    out = {}
    for i in range(len(lines) - 1):
        if re.fullmatch(r"[0-9]*\.?[0-9]+", lines[i+1]):
            out[lines[i]] = float(lines[i+1])
    if out:
        top = max(out.items(), key=lambda x: x[1])
        return {"labels_scores": out, "top_label": top[0], "top_score": top[1]}

    # 3) trailing numeric score -> treat preceding text as label
    m = re.search(r"([0-9]*\.?[0-9]+)\s*$", s2)
    if m:
        score = float(m.group(1))
        label = s2[:m.start()].strip().rstrip(":").strip()
        if label:
            return {"labels_scores": {label: score}, "top_label": label, "top_score": score}

    # fallback
    return {"raw": s}

def _is_number_like(v):
    try:
        float(v)
        return True
    except Exception:
        return False

# Example usage: parse and attach to loaded dataset
# for item in data:
#     pred_text = item.get("result", {}).get("prediction") or ""
#     parsed = parse_prediction_str(pred_text)
#     item.setdefault("parsed_prediction", parsed)