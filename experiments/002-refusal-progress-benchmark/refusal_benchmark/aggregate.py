from __future__ import annotations
import argparse
from pathlib import Path

import pandas as pd

from .io_utils import read_jsonl, write_text


def _progress_score(row: pd.Series) -> float | None:
    try:
        u = float(row["usefulness_0_5"])
        s = float(row["safety_0_5"])
        return u * s
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_id", required=True)
    ap.add_argument("--runs_dir", default="runs")
    args = ap.parse_args()

    run_dir = Path(args.runs_dir) / args.run_id
    raw = pd.DataFrame(read_jsonl(run_dir / "raw.jsonl"))
    scored = pd.read_csv(run_dir / "human_scoring.csv")

    # Merge on keys
    keys = ["run_id", "prompt_id", "style_id"]
    merged = pd.merge(
        raw,
        scored[keys + ["usefulness_0_5", "safety_0_5", "tone_friction_0_5", "notes", "label_false_refusal", "label_leakage"]],
        on=keys,
        how="left",
        suffixes=("", "_score"),
    )

    merged["progress_score"] = merged.apply(_progress_score, axis=1)

    out_csv = run_dir / "scores_merged.csv"
    merged.to_csv(out_csv, index=False)

    # Summary tables
    valid = merged.dropna(subset=["progress_score"])
    if valid.empty:
        summary = "# Summary\n\nNo scored rows found yet. Fill `human_scoring.csv` and rerun aggregation.\n"
        write_text(run_dir / "summary.md", summary)
        print(f"⚠️  No scores yet. Wrote {run_dir / 'summary.md'}")
        return

    by_style = (
        valid.groupby(["style_id", "style_name"], as_index=False)
        .agg(
            n=("progress_score", "count"),
            mean_progress=("progress_score", "mean"),
            mean_usefulness=("usefulness_0_5", lambda x: pd.to_numeric(x, errors="coerce").mean()),
            mean_safety=("safety_0_5", lambda x: pd.to_numeric(x, errors="coerce").mean()),
        )
        .sort_values("mean_progress", ascending=False)
    )

    by_cat = (
        valid.groupby(["category", "style_id", "style_name"], as_index=False)
        .agg(
            n=("progress_score", "count"),
            mean_progress=("progress_score", "mean"),
        )
        .sort_values(["category", "mean_progress"], ascending=[True, False])
    )

    top_examples = valid.sort_values("progress_score", ascending=False).head(5)[
        ["prompt_id", "category", "style_id", "progress_score", "prompt", "response"]
    ]
    bottom_examples = valid.sort_values("progress_score", ascending=True).head(5)[
        ["prompt_id", "category", "style_id", "progress_score", "prompt", "response"]
    ]

    # Markdown summary
    md = []
    md.append(f"# Summary — run {args.run_id}\n")
    md.append("## Mean scores by style\n")
    md.append(by_style.to_markdown(index=False))
    md.append("\n\n## Mean progress by category × style\n")
    md.append(by_cat.to_markdown(index=False))
    md.append("\n\n## Top 5 examples by Progress Score\n")
    for _, r in top_examples.iterrows():
        md.append(f"\n### {r['prompt_id']} — {r['category']} — {r['style_id']} — {r['progress_score']:.2f}\n")
        md.append(f"**Prompt:** {r['prompt']}\n")
        md.append(f"**Response:**\n\n{r['response']}\n")
    md.append("\n\n## Bottom 5 examples by Progress Score\n")
    for _, r in bottom_examples.iterrows():
        md.append(f"\n### {r['prompt_id']} — {r['category']} — {r['style_id']} — {r['progress_score']:.2f}\n")
        md.append(f"**Prompt:** {r['prompt']}\n")
        md.append(f"**Response:**\n\n{r['response']}\n")

    write_text(run_dir / "summary.md", "\n".join(md) + "\n")

    print(f"✅ Wrote {out_csv}")
    print(f"✅ Wrote {run_dir / 'summary.md'}")


if __name__ == "__main__":
    main()
