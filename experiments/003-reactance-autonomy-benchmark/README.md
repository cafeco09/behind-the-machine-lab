# 003 — Reactance / Autonomy Benchmark (When advice feels like pressure)

This experiment tests a simple idea: advice can be *correct* and still fail if the delivery threatens autonomy.

We compare **three styles** for the same scenario:
- **pressure**: controlling language (“you must”, “stop doing X”, “do this now”)
- **autonomy**: choice-preserving language (options, permission language, small steps)
- **neutral**: plain, informative baseline (not pushy, not overly warm)

The goal is not “nicer writing”. It’s to reduce **autonomy threat** while keeping the advice **actionable**.

## Why this matters
A common objection is: “people push back because the advice is generic or wrong.”
That’s often true. This benchmark tries to **isolate framing** by holding the *recommended action* roughly constant and varying the *delivery style*.

## What’s included
- Prompts: `data/prompts.jsonl`
- Outputs: `data/outputs.jsonl`
- Scoring sheet: `data/scores.csv`
- Rubric + examples: `rubrics/`
- Scripts to reproduce: `scripts/`

## Method (simple + reproducible)
1) Start with realistic prompts (constraints included).
2) Generate a **neutral** response for each prompt (from any model).
3) Rewrite the same response into **pressure** and **autonomy** styles.
4) Score each output using the rubric.

This design helps separate:
- **bad content** (wrong advice) from
- **bad framing** (controlling tone that triggers resistance)

## Quick start
From the repo root:
```bash
cd experiments/003-reactance-autonomy-benchmark
python -m venv .venv
source .venv/bin/activate
pip install pandas matplotlib tabulate
python scripts/00_build_prompts.py
python scripts/02_score_sheet.py
python scripts/03_analyse_results.py
```

## Data formats

### prompts.jsonl (one prompt per line)
```json
{"id":"RXT_001","domain":"productivity","constraint":"max 8 lines","user_prompt":"I keep procrastinating on my portfolio. I work 9–6 and I’m exhausted. Give me a plan I’ll actually follow."}
```

### outputs.jsonl (multiple lines per prompt)
```json
{"id":"RXT_001","style":"neutral","model":"<model_name>","output":"..."}
{"id":"RXT_001","style":"pressure","model":"<model_name>","output":"..."}
{"id":"RXT_001","style":"autonomy","model":"<model_name>","output":"..."}
```

### scores.csv
A human-readable scoring sheet that’s easy to audit.

## Notes on claims
This benchmark does **not** prove psychological causality.
It’s a practical evaluation tool: “Does this advice *sound* autonomy-threatening, and is there a clear next step without moralising?”
