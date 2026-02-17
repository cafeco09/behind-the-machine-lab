# Approval Mode Effect (Retail AI A/B experiment)

This repo tests a simple behavioural question in retail AI:

> When an AI assembles a basket/trolley for you, do you shift from *choosing* to *approving* — and does a tiny “review prompt” reduce slips?

This is not a critique of any retailer. It’s a small, reproducible A/B test about decision-making under delegation.

## A/B Design

### A (Control): “Build the basket”
The assistant generates a complete basket from a shopping goal.

### B (Treatment): “Build + micro-pause”
Same basket-building, but you must choose your top 2 constraints before you see the basket:
- Budget / Health / Taste / Convenience / Ethics

Hypothesis: the micro-pause lowers **constraint slips** with minimal time cost.

## What you measure
For each run:
- Acceptance rate (items accepted unchanged)
- Constraint slips (items breaking stated constraints)
- Total cost
- Time-to-checkout (self-reported seconds)

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python src/run_experiment.py
```

## How it works (synthetic but useful)
We generate a synthetic grocery catalogue with:
- category, price, “health score”, “ethics score”
- plus a user goal (e.g., high-protein vegetarian, budget cap)

We then generate baskets with two “assistant styles”:
- Control: immediate basket
- Treatment: asks you to pick constraints first, then basket

You can run it as a simulation (no real retailer data), or use the included score sheet and run it manually with any retail AI cart tool.

## Why this matters
Retail AI is increasingly “agentic” (it drafts the basket). The key question becomes:
- Are customers still the author of decisions, or just the approver of defaults?

Small UI prompts can change behaviour more than people expect.

## Licence
MIT
