"""Optional, local HC3 research baseline. Not a commercial detector or authorship proof.

Dependencies: research/requirements.txt. Raw corpora and model caches stay outside
the skill package. Only load joblib models you created yourself and trust.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import re
import sys
import urllib.request

import joblib
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import StandardScaler

REVISION = "4d0ff18143b5a7e1b1e79beb540c04549d1e59d3"
FILES = {
    "finance": "72e3a439714c4693e115f8ad0b917988688abc07acba8de812198cb13cd5d72e",
    "wiki_csai": "4f78105c72e7edd3b619b3b44abac1e6f8bdb42211f22e43191d4dae889e1968",
    "medicine": "7141b0f5b3477543e95e24a2b268f46c375b08703a390e9a04ff69f5193caa28",
    "open_qa": "4d968e1e1473cbdf5978024872768f0c6f27dacf681f35166dc191733dccd664",
}
TRAIN_DOMAINS = ("finance", "wiki_csai")
OOD_DOMAINS = ("medicine", "open_qa")
SEED = 20261025
MIN_WORDS = 40


def digest(value: str | bytes) -> str:
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def canonical(text: str) -> str:
    return " ".join(text.casefold().split())


def split_group(group: str) -> str:
    value = int(digest(f"{SEED}:{group}")[:16], 16) / 2**64
    return "train" if value < 0.6 else "calibration" if value < 0.8 else "test"


@dataclass(frozen=True)
class Record:
    text: str
    label: int  # 0: source-labeled human, 1: source-labeled ChatGPT
    domain: str
    group: str
    split: str


def fetch(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    for domain, expected in FILES.items():
        dest = data_dir / f"{domain}.jsonl"
        if dest.is_file() and digest(dest.read_bytes()) == expected:
            continue
        url = f"https://huggingface.co/datasets/Hello-SimpleAI/HC3/resolve/{REVISION}/{domain}.jsonl"
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read(30_000_001)
        if len(data) > 30_000_000 or digest(data) != expected:
            raise ValueError(f"Dataset size/hash mismatch: {domain}")
        temporary = dest.with_suffix(".jsonl.part")
        temporary.write_bytes(data)
        temporary.replace(dest)


def load_records(data_dir: Path, cap: int) -> tuple[list[Record], dict]:
    if cap < 10:
        raise ValueError("Use at least 10 question pairs per domain.")
    records, audit = [], {"missing_or_short": 0, "duplicate_question_or_answer": 0}
    seen_questions, seen_answers = set(), set()
    for domain, expected in FILES.items():
        source = data_dir / f"{domain}.jsonl"
        raw = source.read_bytes()
        if digest(raw) != expected:
            raise ValueError(f"Dataset hash mismatch: {source}")
        candidates = []
        for line_number, line in enumerate(raw.splitlines(), 1):
            row = json.loads(line)
            question = row.get("question")
            if not isinstance(question, str) or not canonical(question):
                raise ValueError(f"Missing question at {source}:{line_number}")
            answers = []
            for field in ("human_answers", "chatgpt_answers"):
                values = row.get(field)
                if not isinstance(values, list):
                    raise ValueError(f"Invalid {field} at {source}:{line_number}")
                answer = next((x for x in values if isinstance(x, str) and len(x.split()) >= MIN_WORDS), None)
                answers.append(answer)
            if any(x is None for x in answers):
                audit["missing_or_short"] += 1
                continue
            group = digest(canonical(question))
            candidates.append((digest(f"sample:{SEED}:{group}"), group, answers))
        used = 0
        for _, group, answers in sorted(candidates):
            hashes = [digest(canonical(x)) for x in answers]
            if group in seen_questions or len(set(hashes)) < 2 or any(h in seen_answers for h in hashes):
                audit["duplicate_question_or_answer"] += 1
                continue
            seen_questions.add(group)
            seen_answers.update(hashes)
            split = split_group(group) if domain in TRAIN_DOMAINS else "out_of_domain"
            for label, answer in enumerate(answers):
                records.append(Record(answer, label, domain, group, split))
            used += 1
            if used >= cap:
                break
        audit[domain] = {"question_pairs": used, "source_sha256": expected}
    assert_disjoint(records)
    return records, audit


def assert_disjoint(records: list[Record]) -> None:
    group_split, text_split = {}, {}
    for row in records:
        text_hash = digest(canonical(row.text))
        if row.group in group_split and group_split[row.group] != row.split:
            raise ValueError("Question group crossed a split.")
        if text_hash in text_split and text_split[text_hash] != row.split:
            raise ValueError("Identical normalized text crossed a split.")
        group_split[row.group] = row.split
        text_split[text_hash] = row.split


class SurfaceFeatures(BaseEstimator, TransformerMixin):
    """Deliberately limited features for an ablation, not a writing-quality test."""
    names = ("log_words", "mean_word_length", "mean_sentence_words", "sd_sentence_words",
             "unique_word_ratio", "punctuation_per_character", "newline_per_character", "digit_ratio")

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        result = []
        for text in X:
            words = re.findall(r"\b\w+\b", text.lower())
            lengths = [len(s.split()) for s in re.split(r"[.!?]+", text) if s.strip()]
            n = max(len(text), 1)
            result.append([math.log1p(len(words)), np.mean([len(w) for w in words]) if words else 0,
                           np.mean(lengths) if lengths else 0, np.std(lengths) if lengths else 0,
                           len(set(words)) / max(len(words), 1),
                           sum(c in ",;:!?—()" for c in text) / n,
                           text.count("\n") / n, sum(c.isdigit() for c in text) / n])
        return np.asarray(result, dtype=float)


def build_models() -> dict[str, Pipeline]:
    return {
        "surface": Pipeline([("features", SurfaceFeatures()), ("scale", StandardScaler()),
                             ("classifier", LogisticRegression(C=1, max_iter=1000, random_state=SEED))]),
        "word_char": Pipeline([
            ("features", FeatureUnion([
                ("word", TfidfVectorizer(ngram_range=(1, 2), max_features=15000, min_df=2, sublinear_tf=True)),
                ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=25000,
                                        min_df=2, sublinear_tf=True)),
            ])),
            ("classifier", LogisticRegression(C=1, solver="liblinear", max_iter=1000, random_state=SEED)),
        ]),
    }


def choose_threshold(human_scores, target_fpr=0.01) -> float:
    values = np.asarray(human_scores, dtype=float)
    if values.size == 0 or not np.isfinite(values).all() or not 0 <= target_fpr < 1:
        raise ValueError("Need finite human scores and a target false-positive rate in [0,1).")
    allowed = int(math.floor(len(values) * target_fpr))
    boundary = sorted(values, reverse=True)[allowed]
    # Strictly above this observed boundary; ties must not inflate the FPR.
    return float(np.nextafter(boundary, math.inf))


def wilson(successes: int, total: int) -> list[float] | None:
    if total == 0:
        return None
    p, z = successes / total, 1.959963984540054
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [max(0.0, center - half), min(1.0, center + half)]


def metrics(labels, scores, threshold) -> dict:
    y, score = np.asarray(labels), np.asarray(scores, dtype=float)
    if len(y) != len(score) or not np.isin(y, [0, 1]).all() or not np.isfinite(score).all():
        raise ValueError("Invalid binary labels or scores.")
    predicted = score >= threshold
    human, ai = y == 0, y == 1
    fp, tp = int((predicted & human).sum()), int((predicted & ai).sum())
    nh, na = int(human.sum()), int(ai.sum())
    return {"documents": len(y), "human": nh, "ai": na,
            "auroc": float(roc_auc_score(y, score)) if nh and na else None,
            "average_precision": float(average_precision_score(y, score)) if nh and na else None,
            "brier_balanced_dataset": float(brier_score_loss(y, score)) if len(y) else None,
            "false_positives": fp, "true_positives": tp,
            "fpr": fp / nh if nh else None, "tpr": tp / na if na else None,
            "fpr_wilson95": wilson(fp, nh), "tpr_wilson95": wilson(tp, na)}


def paired_minimum(rows, words):
    """Select complete question pairs that both satisfy a length condition."""
    eligible = {}
    for row in rows:
        if len(row.text.split()) >= words:
            eligible.setdefault(row.group, set()).add(row.label)
    paired = {group for group, labels in eligible.items() if labels == {0, 1}}
    return [row for row in rows if row.group in paired]


def evaluate(model, rows, threshold, words=None):
    selected = rows if words is None else paired_minimum(rows, words)
    texts = [r.text if words is None else " ".join(r.text.split()[:words]) for r in selected]
    if not texts:
        return metrics([], [], threshold)
    return metrics([r.label for r in selected], model.predict_proba(texts)[:, 1], threshold)


def run(args):
    if args.download:
        fetch(args.data_dir)
    records, audit = load_records(args.data_dir, args.pairs_per_domain)
    train = [r for r in records if r.split == "train"]
    cal = [r for r in records if r.split == "calibration"]
    if len({r.label for r in train}) < 2 or len({r.label for r in cal}) < 2:
        raise ValueError("Not enough training/calibration data; increase the pair cap.")
    cases_raw = args.rewrite_cases.read_bytes() if args.rewrite_cases else None
    cases = json.loads(cases_raw) if cases_raw else []
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "scope": "Historical English HC3 baseline; not Turnitin, not authorship proof, no commercial tests.",
        "config": {"seed": SEED, "dataset_revision": REVISION, "pairs_cap": args.pairs_per_domain,
                   "minimum_original_words": MIN_WORDS, "train_domains": TRAIN_DOMAINS,
                   "out_of_domain": OOD_DOMAINS, "calibration_target_fpr": 0.01,
                   "length_evaluation": "matched human/AI question pairs; both originals must meet the prefix length",
                   "rewrite_cases_sha256": digest(cases_raw) if cases_raw else None},
        "environment": {"python": platform.python_version(), **{k: importlib.metadata.version(k) for k in ["numpy", "scipy", "scikit-learn", "joblib"]}},
        "data_audit": audit,
        "splits": {s: sum(r.split == s for r in records) for s in ["train", "calibration", "test", "out_of_domain"]},
        "models": {},
    }
    groups = {"in_domain_test": [r for r in records if r.split == "test"]}
    groups.update({d: [r for r in records if r.domain == d] for d in OOD_DOMAINS})
    groups["in_domain_common_200_word_cohort"] = paired_minimum(groups["in_domain_test"], 200)
    for name, model in build_models().items():
        print("Training", name, "on", len(train), "documents", flush=True)
        model.fit([r.text for r in train], [r.label for r in train])
        cal_scores = model.predict_proba([r.text for r in cal])[:, 1]
        threshold = choose_threshold(cal_scores[np.asarray([r.label == 0 for r in cal])])
        entry = {"threshold": threshold, "calibration": metrics([r.label for r in cal], cal_scores, threshold),
                 "evaluations": {}, "rewrite_probes": []}
        for domain, rows in groups.items():
            entry["evaluations"][domain] = {"full": evaluate(model, rows, threshold)}
            for length in (50, 100, 200):
                entry["evaluations"][domain][f"first_{length}_words"] = evaluate(model, rows, threshold, length)
        for case in cases:
            pair_scores = model.predict_proba([case["before"], case["after"]])[:, 1]
            entry["rewrite_probes"].append({"id": case["id"], "provenance": case["provenance"],
                                           "before_score": float(pair_scores[0]), "after_score": float(pair_scores[1]),
                                           "delta": float(pair_scores[1] - pair_scores[0]),
                                           "before_flag": bool(pair_scores[0] >= threshold),
                                           "after_flag": bool(pair_scores[1] >= threshold)})
        joblib.dump({"model": model, "threshold": threshold, "scope": result["scope"]}, args.output_dir / f"{name}.joblib")
        result["models"][name] = entry
    # Reproducibility ledger contains hashes and groups, never the source answer text.
    manifest = [{"group": r.group, "split": r.split, "label": r.label, "domain": r.domain,
                 "text_sha256": digest(r.text)} for r in records]
    (args.output_dir / "split_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (args.output_dir / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print("Saved results.json, split_manifest.json and local-only models to", args.output_dir, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    fetch_parser = sub.add_parser("fetch", help="Download hash-pinned public HC3 subsets.")
    fetch_parser.add_argument("--data-dir", type=Path, required=True)
    run_parser = sub.add_parser("run", help="Train and evaluate fixed models; no test-set tuning.")
    run_parser.add_argument("--data-dir", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--pairs-per-domain", type=int, default=700)
    run_parser.add_argument("--rewrite-cases", type=Path)
    run_parser.add_argument("--download", action="store_true")
    score_parser = sub.add_parser("score", help="Score locally with a trusted model created by this script.")
    score_parser.add_argument("--model", type=Path, required=True)
    score_parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "fetch":
            fetch(args.data_dir)
        elif args.command == "run":
            run(args)
        else:
            text = args.input.read_text()
            if not text.strip():
                raise ValueError("Input text is empty.")
            bundle = joblib.load(args.model)
            score = float(bundle["model"].predict_proba([text])[0, 1])
            print(json.dumps({"research_score": score, "flag_at_calibration_threshold": score >= bundle["threshold"],
                              "threshold": bundle["threshold"], "words": len(text.split()), "scope": bundle["scope"]}))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    # Keep persisted custom-transformer paths stable between run and score CLIs.
    sys.modules.setdefault("detector_lab", sys.modules[__name__])
    SurfaceFeatures.__module__ = "detector_lab"
    main()
