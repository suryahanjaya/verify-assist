#!/usr/bin/env python3
"""
VerifyAssist Evaluation Script

Sends a labelled dataset of static analysis warnings to the /verify API,
compares predictions against expected labels, and prints accuracy, precision,
recall, F1, and a confusion matrix.

Usage:
    python evaluate.py                          # uses test_warnings.json
    python evaluate.py path/to/dataset.json     # custom dataset
"""

import json
import sys
import time
import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_URL = "http://localhost:8000/verify"
DEFAULT_DATASET = "test_warnings.json"
TIMEOUT = 60  # seconds per request

# Map TOLERABLE → TRUE_POSITIVE for binary evaluation
POSITIVE_LABELS = {"TRUE_POSITIVE", "TOLERABLE"}
NEGATIVE_LABELS = {"FALSE_POSITIVE"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_dataset(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or len(data) == 0:
        print("Error: dataset must be a non-empty JSON array.")
        sys.exit(1)
    for i, item in enumerate(data):
        for key in ("warning_message", "expected_label"):
            if key not in item:
                print(f"Error: item {i} missing required field '{key}'.")
                sys.exit(1)
    return data


def call_api(item: dict) -> dict | None:
    payload = {
        "warning_message": item["warning_message"],
        "category": item.get("category", "UNKNOWN"),
        "code_snippet": item.get("code_snippet", ""),
        "optional_context": item.get("optional_context", ""),
    }
    try:
        r = httpx.post(API_URL, json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        print(f"\n✖ Cannot connect to {API_URL}")
        print("  Start the backend: cd ../backend && uvicorn app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"\n✖ API error: {e}")
        return None


def to_binary(label: str) -> int:
    """1 = positive (real bug), 0 = negative (false positive)."""
    return 1 if label.upper() in POSITIVE_LABELS else 0


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

class ConfusionMatrix:
    def __init__(self):
        self.tp = 0  # predicted positive, actually positive
        self.fp = 0  # predicted positive, actually negative
        self.tn = 0  # predicted negative, actually negative
        self.fn = 0  # predicted negative, actually positive

    def update(self, predicted: int, actual: int):
        if predicted == 1 and actual == 1:
            self.tp += 1
        elif predicted == 1 and actual == 0:
            self.fp += 1
        elif predicted == 0 and actual == 0:
            self.tn += 1
        else:
            self.fn += 1

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.tn + self.fn

    @property
    def accuracy(self) -> float:
        return (self.tp + self.tn) / self.total if self.total else 0.0

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom else 0.0

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return self.tp / denom if denom else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_header():
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║        VerifyAssist  ·  Evaluation Script           ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()


def print_row(idx: int, total: int, item: dict, result: dict | None):
    expected = item["expected_label"]
    if result is None:
        predicted = "ERROR"
        match = "?"
        conf = "N/A"
    else:
        predicted = result["classification"]
        exp_bin = to_binary(expected)
        pred_bin = to_binary(predicted)
        match = "✔" if exp_bin == pred_bin else "✖"
        conf = f'{result["confidence"]:.2f}'

    tag = f"[{idx}/{total}]"
    status_colour = "\033[32m" if match == "✔" else "\033[31m" if match == "✖" else "\033[33m"
    reset = "\033[0m"

    category = item.get("category", "UNKNOWN")
    print(f"  {tag:>8}  {status_colour}{match}{reset}  "
          f"expected={expected:<16} predicted={predicted:<16} "
          f"conf={conf:<6} category={category}")


def print_results(cm: ConfusionMatrix, elapsed: float):
    print()
    print("━" * 56)
    print("  RESULTS")
    print("━" * 56)
    print()
    print(f"  Accuracy  : {cm.accuracy:.4f}  ({cm.tp + cm.tn}/{cm.total} correct)")
    print(f"  Precision : {cm.precision:.4f}")
    print(f"  Recall    : {cm.recall:.4f}")
    print(f"  F1 Score  : {cm.f1:.4f}")
    print()
    print("  ┌─────────────────────────────────────────┐")
    print("  │          Confusion Matrix                │")
    print("  │                                         │")
    print("  │               Predicted                 │")
    print("  │            Positive  Negative            │")
    print(f"  │  Actual  ┌─────────┬─────────┐          │")
    print(f"  │  Pos     │  TP={cm.tp:<4} │  FN={cm.fn:<4} │          │")
    print(f"  │  Neg     │  FP={cm.fp:<4} │  TN={cm.tn:<4} │          │")
    print(f"  │          └─────────┴─────────┘          │")
    print("  └─────────────────────────────────────────┘")
    print()
    print(f"  Total time    : {elapsed:.1f}s")
    print(f"  Avg per item  : {elapsed / max(cm.total, 1):.1f}s")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print_header()

    dataset_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATASET
    print(f"  Dataset : {dataset_path}")
    print(f"  API     : {API_URL}")

    dataset = load_dataset(dataset_path)
    total = len(dataset)
    print(f"  Items   : {total}")
    print()

    cm = ConfusionMatrix()
    start = time.perf_counter()

    for i, item in enumerate(dataset, 1):
        result = call_api(item)

        if result:
            pred_bin = to_binary(result["classification"])
            exp_bin = to_binary(item["expected_label"])
            cm.update(pred_bin, exp_bin)

        print_row(i, total, item, result)

        # Delay between requests to avoid Groq rate limits
        if i < total:
            time.sleep(1)

    elapsed = time.perf_counter() - start
    print_results(cm, elapsed)


if __name__ == "__main__":
    main()
