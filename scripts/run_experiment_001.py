#!/usr/bin/env python3
"""
Run Experiment 001: Human Review Controls vs Baseline

Reads:
  experiments/001-human-review-controls/data/prompts.csv
  experiments/001-human-review-controls/prompts/baseline_prompt.md
  experiments/001-human-review-controls/prompts/controlled_prompt.md

Writes:
  experiments/001-human-review-controls/data/outputs_baseline.csv
  experiments/001-human-review-controls/data/outputs_controlled.csv
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from datetime import datetime, timezone

from openai import OpenAI


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def load_prompts(prompts_csv: Path, only_ids: set[str] | None = None) -> list[dict]:
    rows = []
    with prompts_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if only_ids and r["id"] not in only_ids:
                continue
            rows.append(r)
    return rows


def load_existing_outputs(outputs_csv: Path) -> dict[str, str]:
    if not outputs_csv.exists():
        return {}
    existing = {}
    with outputs_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            existing[r["id"]] = r.get("output", "") or ""
    return existing


def write_outputs(outputs_csv: Path, rows: list[dict[str, str]]) -> None:
    outputs_csv.parent.mkdir(parents=True, exist_ok=True)
    with outputs_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "output", "model", "timestamp_utc"],
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerows(rows)


def call_model(client: OpenAI, model: str, instructions: str, user_prompt: str, max_output_tokens: int) -> str:
    # Responses API: separate instructions and input is supported. :contentReference[oaicite:2]{index=2}
    resp = client.responses.create(
        model=model,
        instructions=instructions,
        input=user_prompt,
        max_output_tokens=max_output_tokens,
    )
    return (resp.output_text or "").strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", default="experiments/001-human-review-controls", help="Experiment folder path")
    ap.add_argument("--model", default="gpt-5.2", help="Model name (e.g., gpt-5.2)")
    ap.add_argument("--max_output_tokens", type=int, default=500)
    ap.add_argument("--ids", default="", help="Comma-separated prompt IDs to run (e.g., 001,006,008)")
    ap.add_argument("--force", action="store_true", help="Re-run even if output already exists")
    ap.add_argument("--only", choices=["A", "B", "AB"], default="AB", help="Which conditions to run")
    args = ap.parse_args()

    exp_dir = Path(args.exp)
    prompts_csv = exp_dir / "data" / "prompts.csv"
    baseline_md = exp_dir / "prompts" / "baseline_prompt.md"
    controlled_md = exp_dir / "prompts" / "controlled_prompt.md"

    out_a = exp_dir / "data" / "outputs_baseline.csv"
    out_b = exp_dir / "data" / "outputs_controlled.csv"

    only_ids = set(x.strip() for x in args.ids.split(",") if x.strip()) or None

    prompts = load_prompts(prompts_csv, only_ids=only_ids)
    if not prompts:
        raise SystemExit(f"No prompts found in {prompts_csv} (or IDs filter removed all).")

    instructions_a = read_text(baseline_md)
    instructions_b = read_text(controlled_md)

    client = OpenAI()

    now_utc = datetime.now(timezone.utc).isoformat()

    # Load existing to support resume
    existing_a = load_existing_outputs(out_a)
    existing_b = load_existing_outputs(out_b)

    rows_a: list[dict[str, str]] = []
    rows_b: list[dict[str, str]] = []

    run_a = args.only in ("A", "AB")
    run_b = args.only in ("B", "AB")

    for r in prompts:
        pid = r["id"]
        user_prompt = r["prompt"]

        if run_a:
            if (not args.force) and existing_a.get(pid, "").strip():
                output_a = existing_a[pid]
            else:
                output_a = call_model(client, args.model, instructions_a, user_prompt, args.max_output_tokens)
            rows_a.append({"id": pid, "output": output_a, "model": args.model, "timestamp_utc": now_utc})

        if run_b:
            if (not args.force) and existing_b.get(pid, "").strip():
                output_b = existing_b[pid]
            else:
                output_b = call_model(client, args.model, instructions_b, user_prompt, args.max_output_tokens)
            rows_b.append({"id": pid, "output": output_b, "model": args.model, "timestamp_utc": now_utc})

    if run_a:
        write_outputs(out_a, rows_a)
        print(f"Wrote {len(rows_a)} rows -> {out_a}")
    if run_b:
        write_outputs(out_b, rows_b)
        print(f"Wrote {len(rows_b)} rows -> {out_b}")


if __name__ == "__main__":
    # Safety: fail fast if API key missing
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Export it first (e.g., export OPENAI_API_KEY='...').")
    main()

