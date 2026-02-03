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

def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)

    rows = []
    if OUT_JSONL.exists() and OUT_JSONL.stat().st_size > 0:
        with OUT_JSONL.open("r", encoding="utf-8") as f:
            for line in f:
                x = json.loads(line)
                rows.append({
                    "id": x.get("id",""),
                    "style": x.get("style",""),
                    "model": x.get("model",""),
                    "autonomy_threat_0_5": "",
                    "judgement_moralising_0_5": "",
                    "overconfidence_0_5": "",
                    "choice_quality_0_5": "",
                    "clarity_next_step_0_5": "",
                    "questions_count_0_2": "",
                    "reactance_risk_overall_0_5": "",
                    "notes": ""
                })
    else:
        rows = []

    with SCORES.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"[ok] wrote {SCORES} with {len(rows)} rows")

if __name__ == "__main__":
    main()
