from __future__ import annotations
import argparse
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv
from tqdm import tqdm

from .io_utils import read_prompts, read_styles, write_jsonl, write_text
from .llm_client import build_messages
from .schema import RunMeta


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:
        return None


def _make_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_utc")


def _get_env(name: str, default: str | None = None) -> str | None:
    v = os.environ.get(name)
    return v if v is not None else default


def main() -> None:
    load_dotenv()

    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="mock", choices=["mock", "openai_compat"])
    ap.add_argument("--prompts", default="prompts/prompt_suite_v0.jsonl")
    ap.add_argument("--styles", default="conditions/refusal_styles.yaml")
    ap.add_argument("--outdir", default="runs")
    ap.add_argument("--run_id", default="auto")
    ap.add_argument("--sample_n", type=int, default=0, help="0 means all prompts")
    ap.add_argument("--temperature", type=float, default=float(_get_env("LLM_TEMPERATURE", "0.2")))
    ap.add_argument("--max_tokens", type=int, default=int(_get_env("LLM_MAX_TOKENS", "600")))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    run_id = _make_run_id() if args.run_id == "auto" else args.run_id
    run_dir = Path(args.outdir) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    prompts = read_prompts(args.prompts)
    styles = read_styles(args.styles)

    if args.sample_n and args.sample_n > 0:
        prompts = prompts[: args.sample_n]

    # Client
    if args.provider == "mock":
        from .providers.mock import MockClient

        client = MockClient(seed=args.seed)
        model = "mock-model"
        base_url = None
    else:
        from .providers.openai_compat import OpenAICompatClient

        base_url = _get_env("LLM_BASE_URL", "http://localhost:8000/v1") or ""
        api_key = _get_env("LLM_API_KEY", "anything") or ""
        model = _get_env("LLM_MODEL", "model") or "model"
        client = OpenAICompatClient(
            base_url=base_url,
            api_key=api_key,
            model=model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )

    meta = RunMeta(
        run_id=run_id,
        created_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=_git_commit(),
        provider=args.provider,
        model=model,
        temperature=float(args.temperature),
        max_tokens=int(args.max_tokens),
        seed=int(args.seed),
        base_url=base_url,
    )
    write_jsonl(run_dir / "run_meta.jsonl", [meta.to_dict()])

    rows: List[Dict[str, Any]] = []
    for p in tqdm(prompts, desc="Prompts"):
        for s in styles:
            messages = build_messages(s.system_prompt, p.prompt)
            try:
                out = client.chat(messages)
                error = None
            except Exception as e:
                out = ""
                error = f"{type(e).__name__}: {e}"

            rows.append(
                {
                    "run_id": run_id,
                    "prompt_id": p.id,
                    "category": p.category,
                    "risk_level": p.risk_level,
                    "expected_action": p.expected_action,
                    "user_intent": p.user_intent,
                    "style_id": s.id,
                    "style_name": s.name,
                    "system_prompt": s.system_prompt,
                    "prompt": p.prompt,
                    "response": out,
                    "error": error,
                }
            )

    write_jsonl(run_dir / "raw.jsonl", rows)

    # Export a blank human scoring sheet
    from .export_human_sheet import export_human_sheet

    export_human_sheet(run_dir)

    write_text(
        run_dir / "README_run.md",
        f"""# Run {run_id}

Files:
- raw.jsonl — model outputs per prompt × style
- human_scoring.csv — fill this in with rubric scores
- run_meta.jsonl — run metadata (model, temperature, etc.)
""",
    )

    print(f"✅ Wrote {len(rows)} rows to {run_dir / 'raw.jsonl'}")
    print(f"➡️  Next: fill {run_dir / 'human_scoring.csv'} then run:")
    print(f"    python -m refusal_benchmark.aggregate --run_id {run_id}")


if __name__ == "__main__":
    main()
