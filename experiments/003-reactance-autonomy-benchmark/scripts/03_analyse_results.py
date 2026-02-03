import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
SCORES = DATA / "scores.csv"
OUT_MD = HERE.parent / "data" / "analysis_summary.md"

def main() -> None:
    if not SCORES.exists():
        print("[error] scores.csv not found. Run scripts/02_score_sheet.py first.")
        return

    df = pd.read_csv(SCORES)

    if df.empty:
        print("[info] scores.csv has no rows yet. Fill it in, then re-run analysis.")
        return

    numeric_cols = [c for c in df.columns if c.endswith("_0_5") or c.endswith("_0_2")]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    group = df.groupby("style", dropna=False)[numeric_cols].mean().round(2)

    if set(["pressure","autonomy"]).issubset(set(df["style"].dropna().unique())):
        p = df[df["style"]=="pressure"][numeric_cols].mean()
        a = df[df["style"]=="autonomy"][numeric_cols].mean()
        delta = (p - a).round(2)
    else:
        delta = None

    lines = []
    lines.append("# Analysis summary\n")
    lines.append("## Mean scores by style\n")
    lines.append(group.to_markdown())
    lines.append("\n")

    if delta is not None:
        lines.append("## Pressure minus autonomy (positive means pressure is worse)\n")
        lines.append(delta.to_frame("pressure_minus_autonomy").to_markdown())
        lines.append("\n")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] wrote {OUT_MD}")

if __name__ == "__main__":
    main()
