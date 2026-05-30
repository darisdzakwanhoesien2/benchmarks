from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
from torch.utils.data import DataLoader

from modeling import LabelVocab, MultiHeadAbsaModel, load_tokenizer
from train import JsonlAbsaDataset, collate_batch, read_jsonl


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def confusion_matrix(y_true: List[int], y_pred: List[int], n: int) -> List[List[int]]:
    m = [[0 for _ in range(n)] for __ in range(n)]
    for t, p in zip(y_true, y_pred):
        if 0 <= t < n and 0 <= p < n:
            m[t][p] += 1
    return m


def macro_f1(y_true: List[int], y_pred: List[int], n: int) -> float:
    f1s = []
    for c in range(n):
        tp = 0
        fp = 0
        fn = 0
        for t, p in zip(y_true, y_pred):
            if t == c and p == c:
                tp += 1
            elif t != c and p == c:
                fp += 1
            elif t == c and p != c:
                fn += 1
        if tp == 0 and (fp > 0 or fn > 0):
            f1s.append(0.0)
            continue
        if tp == 0 and fp == 0 and fn == 0:
            continue
        prec = tp / max(tp + fp, 1)
        rec = tp / max(tp + fn, 1)
        f1 = 0.0 if (prec + rec) == 0 else (2 * prec * rec / (prec + rec))
        f1s.append(float(f1))
    if not f1s:
        return 0.0
    return float(sum(f1s) / len(f1s))


@torch.no_grad()
def predict(
    model: MultiHeadAbsaModel,
    loader: DataLoader,
    device: torch.device,
    has_tone: bool,
) -> Dict[str, List[int]]:
    model.eval()
    out_aspect = []
    out_sent = []
    out_tone = []
    y_aspect = []
    y_sent = []
    y_tone = []

    for batch in loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        logits = model(input_ids=input_ids, attention_mask=attention_mask)

        out_aspect.extend(torch.argmax(logits["aspect"], dim=-1).cpu().tolist())
        out_sent.extend(torch.argmax(logits["sentiment"], dim=-1).cpu().tolist())
        y_aspect.extend(batch["y_aspect"].tolist())
        y_sent.extend(batch["y_sentiment"].tolist())

        if has_tone and "tone" in logits and "y_tone" in batch:
            out_tone.extend(torch.argmax(logits["tone"], dim=-1).cpu().tolist())
            y_tone.extend(batch["y_tone"].tolist())

    preds = {
        "aspect_pred": out_aspect,
        "sentiment_pred": out_sent,
        "aspect_true": y_aspect,
        "sentiment_true": y_sent,
    }
    if out_tone and y_tone:
        preds["tone_pred"] = out_tone
        preds["tone_true"] = y_tone
    return preds


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate transfer-learning run for ESG ABSA.")
    parser.add_argument("--data", type=str, required=True, help="Dataset jsonl")
    parser.add_argument("--run", type=str, required=True, help="Run directory produced by train.py")
    parser.add_argument("--out", type=str, required=True, help="Output metrics directory")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    data_path = Path(args.data)
    run_dir = Path(args.run)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    vocab_dict = config["label_vocab"]
    include_tone = bool(config.get("include_tone"))

    vocab = LabelVocab(
        aspect2id=vocab_dict["aspect2id"],
        sentiment2id=vocab_dict["sentiment2id"],
        tone2id=vocab_dict.get("tone2id"),
    )

    rows = read_jsonl(data_path)
    tokenizer = load_tokenizer(config["model"])
    pad_id = tokenizer.pad_token_id
    if pad_id is None:
        pad_id = tokenizer.eos_token_id or tokenizer.sep_token_id
    if pad_id is None:
        raise SystemExit("Tokenizer has no pad token id")

    ds = JsonlAbsaDataset(rows, vocab, tokenizer, max_len=int(config["max_len"]), include_tone=include_tone)
    dl = DataLoader(ds, batch_size=args.batch_size, shuffle=False, collate_fn=lambda b: collate_batch(b, pad_token_id=pad_id))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MultiHeadAbsaModel(
        base_model_name=config["model"],
        n_aspects=len(vocab.aspect2id),
        n_sentiments=len(vocab.sentiment2id),
        n_tones=(len(vocab.tone2id) if (include_tone and vocab.tone2id) else 0),
    ).to(device)
    state = torch.load(run_dir / "model.pt", map_location=device)
    model.load_state_dict(state)

    preds = predict(model, dl, device=device, has_tone=include_tone)

    aspect_true = preds["aspect_true"]
    aspect_pred = preds["aspect_pred"]
    sent_true = preds["sentiment_true"]
    sent_pred = preds["sentiment_pred"]

    def _acc(a: List[int], b: List[int]) -> float:
        if not a:
            return 0.0
        correct = sum(1 for x, y in zip(a, b) if x == y)
        return correct / len(a)

    metrics = {
        "n": int(len(rows)),
        "aspect": {
            "accuracy": _acc(aspect_true, aspect_pred),
            "macro_f1": macro_f1(aspect_true, aspect_pred, n=len(vocab.aspect2id)),
            "confusion_matrix": confusion_matrix(aspect_true, aspect_pred, n=len(vocab.aspect2id)),
            "labels": vocab.id2aspect,
        },
        "sentiment": {
            "accuracy": _acc(sent_true, sent_pred),
            "macro_f1": macro_f1(sent_true, sent_pred, n=len(vocab.sentiment2id)),
            "confusion_matrix": confusion_matrix(sent_true, sent_pred, n=len(vocab.sentiment2id)),
            "labels": vocab.id2sentiment,
        },
    }

    if include_tone and "tone_true" in preds and "tone_pred" in preds and vocab.tone2id:
        tone_true = preds["tone_true"]
        tone_pred = preds["tone_pred"]
        metrics["tone"] = {
            "accuracy": _acc(tone_true, tone_pred),
            "macro_f1": macro_f1(tone_true, tone_pred, n=len(vocab.tone2id)),
            "confusion_matrix": confusion_matrix(tone_true, tone_pred, n=len(vocab.tone2id)),
            "labels": vocab.id2tone,
        }

    write_json(out_dir / "metrics.json", metrics)
    print(f"wrote metrics to {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
