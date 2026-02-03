#!/usr/bin/env python3
"""
Interactive scorer for Issue 3 (reactance/autonomy benchmark).

- Reads:  ../data/outputs.jsonl
- Writes: ../data/scores.csv  (overwrites)

Run from:
  experiments/003-reactance-autonomy-benchmark/scripts

Usage:
  python 04_interactive_scoring.py
"""

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
OUT_JSONL = DATA / "outputs.jsonl"
SCORES = DATA / "scores.csv"

FIELDS = [
    "id","style","model",
    "autonomy_threat_0_5",
    "judgement_moralising_0_5",
    "overconfidence_0_5",
    "choice_quality_0_5",
    "clarity_next_step_0_5",
    "questions_count_0_2",
    "reactance_risk_overall_0_5",
    "notes"
]

def load_outputs():
    rows = []
    with OUT_JSONL.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def ask_int(prompt, lo, hi, default=None):
    while True:
        s = input(f"{prompt} ({lo}-{hi})" + (f" [default {default}]" if default is not None else "") + ": ").strip()
        if not s and default is not None:
            return default
        try:
            v = int(s)
        except ValueError:
            print("  -> enter an integer")
            continue
        if v < lo or v > hi:
            print(f"  -> must be between {lo} and {hi}")
            continue
        return v

def main():
    if not OUT_JSONL.exists():
        raise SystemExit(f"outputs.jsonl not found at {OUT_JSONL}")

    outputs = load_outputs()
    scored = []

    print(f"[info] loaded {len(outputs)} outputs")
    print("[info] scoring order is as-is from outputs.jsonl\n")

    for i, r in enumerate(outputs, start=1):
        print("="*80)
        print(f"{i}/{len(outputs)}  id={r.get('id')}  style={r.get('style')}  model={r.get('model')}")
        print("-"*80)
        print(r.get("output","").strip())
        print("-"*80)

        aut = ask_int("Autonomy threat", 0, 5)
        jud = ask_int("Judgement/moralising", 0, 5)
        ov  = ask_int("Overconfidence", 0, 5)
        ch  = ask_int("Choice quality", 0, 5)
        cl  = ask_int("Clarity next step", 0, 5)
        qc  = ask_int("Questions count", 0, 2)
        rr  = ask_int("Reactance risk overall", 0, 5)
        notes = input("Notes (optional): ").strip()

        scored.append({
            "id": r.get("id",""),
            "style": r.get("style",""),
            "model": r.get("model",""),
            "autonomy_threat_0_5": aut,
            "judgement_moralising_0_5": jud,
            "overconfidence_0_5": ov,
            "choice_quality_0_5": ch,
            "clarity_next_step_0_5": cl,
            "questions_count_0_2": qc,
            "reactance_risk_overall_0_5": rr,
            "notes": notes,
        })

    with SCORES.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(scored)

    print(f"\n[ok] wrote scores to {SCORES}")

if __name__ == "__main__":
    main()
