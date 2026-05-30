from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
from torch.utils.data import DataLoader, Dataset

from modeling import LabelVocab, MultiHeadAbsaModel, load_tokenizer


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def build_vocab(rows: List[Dict[str, Any]], include_tone: bool) -> LabelVocab:
    aspects = sorted({r["aspect"] for r in rows if r.get("aspect")})
    sentiments = sorted({r["sentiment"] for r in rows if r.get("sentiment")})
    tones = sorted({r.get("tone", "Unknown") for r in rows}) if include_tone else []
    return LabelVocab(
        aspect2id={a: i for i, a in enumerate(aspects)},
        sentiment2id={s: i for i, s in enumerate(sentiments)},
        tone2id=({t: i for i, t in enumerate(tones)} if include_tone else None),
    )


class JsonlAbsaDataset(Dataset):
    def __init__(self, rows: List[Dict[str, Any]], vocab: LabelVocab, tokenizer, max_len: int, include_tone: bool):
        self.rows = rows
        self.vocab = vocab
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.include_tone = include_tone

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        r = self.rows[idx]
        text = r["text"]
        enc = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_len,
            padding=False,
            return_tensors=None,
        )
        item = {
            "input_ids": enc["input_ids"],
            "attention_mask": enc["attention_mask"],
            "y_aspect": self.vocab.aspect2id[r["aspect"]],
            "y_sentiment": self.vocab.sentiment2id[r["sentiment"]],
        }
        if self.include_tone and self.vocab.tone2id is not None:
            item["y_tone"] = self.vocab.tone2id.get(r.get("tone", "Unknown"), 0)
        return item


def collate_batch(batch: List[Dict[str, Any]], pad_token_id: int) -> Dict[str, torch.Tensor]:
    max_len = max(len(x["input_ids"]) for x in batch)
    input_ids = []
    attention_mask = []
    y_aspect = []
    y_sentiment = []
    y_tone = []
    has_tone = "y_tone" in batch[0]

    for x in batch:
        ids = x["input_ids"]
        mask = x["attention_mask"]
        pad = max_len - len(ids)
        input_ids.append(ids + [pad_token_id] * pad)
        attention_mask.append(mask + [0] * pad)
        y_aspect.append(x["y_aspect"])
        y_sentiment.append(x["y_sentiment"])
        if has_tone:
            y_tone.append(x["y_tone"])

    out = {
        "input_ids": torch.tensor(input_ids, dtype=torch.long),
        "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
        "y_aspect": torch.tensor(y_aspect, dtype=torch.long),
        "y_sentiment": torch.tensor(y_sentiment, dtype=torch.long),
    }
    if has_tone:
        out["y_tone"] = torch.tensor(y_tone, dtype=torch.long)
    return out


@torch.no_grad()
def _accuracy(logits: torch.Tensor, y: torch.Tensor) -> float:
    pred = torch.argmax(logits, dim=-1)
    return (pred == y).float().mean().item()


def train_one_epoch(
    model: MultiHeadAbsaModel,
    loader: DataLoader,
    optim: torch.optim.Optimizer,
    device: torch.device,
    alpha_aspect: float,
    alpha_sentiment: float,
    alpha_tone: float,
) -> Dict[str, float]:
    model.train()
    ce = torch.nn.CrossEntropyLoss()
    total_loss = 0.0
    n = 0
    acc_a = 0.0
    acc_s = 0.0
    acc_t = 0.0
    has_tone = model.tone_head is not None

    for batch in loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        y_aspect = batch["y_aspect"].to(device)
        y_sentiment = batch["y_sentiment"].to(device)
        y_tone = batch.get("y_tone")
        if y_tone is not None:
            y_tone = y_tone.to(device)

        logits = model(input_ids=input_ids, attention_mask=attention_mask)
        loss = alpha_aspect * ce(logits["aspect"], y_aspect) + alpha_sentiment * ce(logits["sentiment"], y_sentiment)
        if has_tone and y_tone is not None and "tone" in logits:
            loss = loss + alpha_tone * ce(logits["tone"], y_tone)

        optim.zero_grad(set_to_none=True)
        loss.backward()
        optim.step()

        bs = input_ids.size(0)
        total_loss += loss.item() * bs
        n += bs
        acc_a += _accuracy(logits["aspect"], y_aspect) * bs
        acc_s += _accuracy(logits["sentiment"], y_sentiment) * bs
        if has_tone and y_tone is not None and "tone" in logits:
            acc_t += _accuracy(logits["tone"], y_tone) * bs

    return {
        "loss": total_loss / max(n, 1),
        "acc_aspect": acc_a / max(n, 1),
        "acc_sentiment": acc_s / max(n, 1),
        "acc_tone": (acc_t / max(n, 1)) if has_tone else 0.0,
    }


@torch.no_grad()
def eval_one_epoch(model: MultiHeadAbsaModel, loader: DataLoader, device: torch.device) -> Dict[str, float]:
    model.eval()
    ce = torch.nn.CrossEntropyLoss()
    total_loss = 0.0
    n = 0
    acc_a = 0.0
    acc_s = 0.0
    acc_t = 0.0
    has_tone = model.tone_head is not None

    for batch in loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        y_aspect = batch["y_aspect"].to(device)
        y_sentiment = batch["y_sentiment"].to(device)
        y_tone = batch.get("y_tone")
        if y_tone is not None:
            y_tone = y_tone.to(device)

        logits = model(input_ids=input_ids, attention_mask=attention_mask)
        loss = ce(logits["aspect"], y_aspect) + ce(logits["sentiment"], y_sentiment)
        if has_tone and y_tone is not None and "tone" in logits:
            loss = loss + ce(logits["tone"], y_tone)

        bs = input_ids.size(0)
        total_loss += loss.item() * bs
        n += bs
        acc_a += _accuracy(logits["aspect"], y_aspect) * bs
        acc_s += _accuracy(logits["sentiment"], y_sentiment) * bs
        if has_tone and y_tone is not None and "tone" in logits:
            acc_t += _accuracy(logits["tone"], y_tone) * bs

    return {
        "loss": total_loss / max(n, 1),
        "acc_aspect": acc_a / max(n, 1),
        "acc_sentiment": acc_s / max(n, 1),
        "acc_tone": (acc_t / max(n, 1)) if has_tone else 0.0,
    }


def split_rows(rows: List[Dict[str, Any]], seed: int, train_ratio: float = 0.8) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    rng = random.Random(seed)
    idx = list(range(len(rows)))
    rng.shuffle(idx)
    cut = int(len(idx) * train_ratio)
    train_idx = set(idx[:cut])
    train = [rows[i] for i in range(len(rows)) if i in train_idx]
    val = [rows[i] for i in range(len(rows)) if i not in train_idx]
    return train, val


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a transfer-learning model for ESG ABSA.")
    parser.add_argument("--train", type=str, required=True, help="Dataset jsonl (built by data_builder.py)")
    parser.add_argument("--model", type=str, default="bert-base-multilingual-cased", help="HF model name")
    parser.add_argument("--out", type=str, required=True, help="Output run directory")
    parser.add_argument("--include-tone", action="store_true", help="Also train a tone head (multi-task)")
    parser.add_argument("--max-len", type=int, default=192)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--alpha-aspect", type=float, default=1.0)
    parser.add_argument("--alpha-sentiment", type=float, default=1.0)
    parser.add_argument("--alpha-tone", type=float, default=0.5)
    args = parser.parse_args()

    set_seed(args.seed)

    data_path = Path(args.train)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_jsonl(data_path)
    if not rows:
        raise SystemExit("Empty dataset")

    train_rows, val_rows = split_rows(rows, seed=args.seed, train_ratio=0.8)
    vocab = build_vocab(train_rows, include_tone=args.include_tone)

    tokenizer = load_tokenizer(args.model)
    pad_id = tokenizer.pad_token_id
    if pad_id is None:
        # Some tokenizers have no pad token; reuse eos/sep if available.
        pad_id = tokenizer.eos_token_id or tokenizer.sep_token_id
        if pad_id is None:
            raise SystemExit("Tokenizer has no pad token id")

    ds_train = JsonlAbsaDataset(train_rows, vocab, tokenizer, max_len=args.max_len, include_tone=args.include_tone)
    ds_val = JsonlAbsaDataset(val_rows, vocab, tokenizer, max_len=args.max_len, include_tone=args.include_tone)

    dl_train = DataLoader(
        ds_train,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=lambda b: collate_batch(b, pad_token_id=pad_id),
    )
    dl_val = DataLoader(
        ds_val,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=lambda b: collate_batch(b, pad_token_id=pad_id),
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MultiHeadAbsaModel(
        base_model_name=args.model,
        n_aspects=len(vocab.aspect2id),
        n_sentiments=len(vocab.sentiment2id),
        n_tones=(len(vocab.tone2id) if (args.include_tone and vocab.tone2id) else 0),
    ).to(device)

    optim = torch.optim.AdamW(model.parameters(), lr=args.lr)

    config = {
        "model": args.model,
        "include_tone": args.include_tone,
        "max_len": args.max_len,
        "batch_size": args.batch_size,
        "epochs": args.epochs,
        "lr": args.lr,
        "seed": args.seed,
        "alpha_aspect": args.alpha_aspect,
        "alpha_sentiment": args.alpha_sentiment,
        "alpha_tone": args.alpha_tone,
        "n_train": len(train_rows),
        "n_val": len(val_rows),
        "label_vocab": {
            "aspect2id": vocab.aspect2id,
            "sentiment2id": vocab.sentiment2id,
            "tone2id": vocab.tone2id,
        },
    }
    write_json(out_dir / "config.json", config)

    best_val_loss = float("inf")
    history: List[Dict[str, Any]] = []
    for epoch in range(1, args.epochs + 1):
        tr = train_one_epoch(
            model,
            dl_train,
            optim,
            device=device,
            alpha_aspect=args.alpha_aspect,
            alpha_sentiment=args.alpha_sentiment,
            alpha_tone=args.alpha_tone,
        )
        va = eval_one_epoch(model, dl_val, device=device)
        row = {"epoch": epoch, "train": tr, "val": va}
        history.append(row)
        write_json(out_dir / "history.json", history)
        print(f"epoch {epoch} train_loss={tr['loss']:.4f} val_loss={va['loss']:.4f}")

        if va["loss"] < best_val_loss:
            best_val_loss = va["loss"]
            torch.save(model.state_dict(), out_dir / "model.pt")
            print(f"saved best model to {out_dir / 'model.pt'}")

    print("done")


if __name__ == "__main__":
    main()
