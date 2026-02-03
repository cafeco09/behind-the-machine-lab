#!/usr/bin/env python3
"""
Generate NEUTRAL outputs for the Issue 3 dataset via the OpenAI Responses API.

- Reads:  ../data/prompts.jsonl
- Appends: ../data/outputs.jsonl  (one JSON object per line)

Repro notes:
- We log model, temperature, timestamp, and the full prompt record used.
- This script deliberately generates *neutral* style only. Use 01_style_rewrite.py
  to create pressure/autonomy variants afterwards.

Usage (macOS/Linux):
  export OPENAI_API_KEY="..."
  python 01_run_openai_outputs.py

Optional env vars:
  OPENAI_MODEL         (default: gpt-5.2)
  OPENAI_TEMPERATURE   (default: 0.4)
  OPENAI_SLEEP_S       (default: 0.2)
  OPENAI_MAX_RETRIES   (default: 3)
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable

from openai import OpenAI


@dataclass(frozen=True)
class Settings:
    model: str = os.getenv("OPENAI_MODEL", "gpt-5.2")
    temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.4"))
    sleep_s: float = float(os.getenv("OPENAI_SLEEP_S", "0.2"))
    max_retries: int = int(os.getenv("OPENAI_MAX_RETRIES", "3"))


DEVELOPER_INSTRUCTION = (
    "You are generating a NEUTRAL advice response for an evaluation dataset.\n"
    "Requirements:\n"
    "- Neutral tone: not pushy, not scolding, not overly warm.\n"
    "- Be practical and specific.\n"
    "- Offer 2–4 steps (not a long list).\n"
    "- Ask at most ONE short question at the end.\n"
    "- Respect any constraint included in the prompt record (e.g., 'max 8 lines').\n"
)


def iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def already_done_ids(outputs_path: Path) -> set[str]:
    """Avoid re-generating rows if outputs.jsonl already contains neutral entries."""
    if not outputs_path.exists() or outputs_path.stat().st_size == 0:
        return set()
    ids: set[str] = set()
    for row in iter_jsonl(outputs_path):
        if row.get("style") == "neutral" and "id" in row:
            ids.add(str(row["id"]))
    return ids


def make_user_text(prompt_record: Dict[str, Any]) -> str:
    user_text = str(prompt_record.get("user_prompt", "")).strip()
    constraint = str(prompt_record.get("constraint", "")).strip()
    if constraint:
        user_text = f"{user_text}\n\nConstraint: {constraint}"
    return user_text


def main() -> None:
    settings = Settings()

    # Resolve paths relative to this script file
    here = Path(__file__).resolve().parent
    data_dir = here.parent / "data"
    prompts_path = data_dir / "prompts.jsonl"
    outputs_path = data_dir / "outputs.jsonl"

    if not prompts_path.exists():
        raise SystemExit(f"prompts.jsonl not found at: {prompts_path}")

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is not set.\n"
            "macOS/Linux: export OPENAI_API_KEY=\"...\"\n"
            "Windows (PowerShell): setx OPENAI_API_KEY \"...\""
        )

    data_dir.mkdir(parents=True, exist_ok=True)
    done = already_done_ids(outputs_path)

    client = OpenAI()

    for prompt in iter_jsonl(prompts_path):
        pid = str(prompt.get("id", "")).strip()
        if not pid:
            print("[skip] prompt missing id")
            continue
        if pid in done:
            print(f"[skip] {pid} already present")
            continue

        user_text = make_user_text(prompt)

        last_err: Exception | None = None
        for attempt in range(1, settings.max_retries + 1):
            try:
                resp = client.responses.create(
                    model=settings.model,
                    temperature=settings.temperature,
                    input=[
                        {"role": "developer", "content": DEVELOPER_INSTRUCTION},
                        {"role": "user", "content": user_text},
                    ],
                )

                append_jsonl(
                    outputs_path,
                    {
                        "id": pid,
                        "style": "neutral",
                        "model": settings.model,
                        "temperature": settings.temperature,
                        "created_at_utc": datetime.now(timezone.utc).isoformat(),
                        "prompt_record": prompt,
                        "output": resp.output_text,
                    },
                )
                print(f"[ok] {pid}")
                last_err = None
                break
            except Exception as e:
                last_err = e
                print(f"[warn] {pid} attempt {attempt} failed: {e}")
                time.sleep(1.0 * attempt)

        if last_err is not None:
            raise SystemExit(f"Failed on {pid}: {last_err}")

        time.sleep(settings.sleep_s)


if __name__ == "__main__":
    main()
