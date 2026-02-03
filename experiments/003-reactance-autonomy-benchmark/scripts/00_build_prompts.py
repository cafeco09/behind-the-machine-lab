import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
PROMPTS = DATA / "prompts.jsonl"

def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)

    # Idempotent: won't overwrite if prompts already exist and are non-empty.
    if PROMPTS.exists() and PROMPTS.stat().st_size > 0:
        print(f"[skip] {PROMPTS} already exists and is non-empty")
        return

    seed = [
        {"id":"RXT_001","domain":"productivity","constraint":"max 8 lines",
         "user_prompt":"I keep procrastinating on my portfolio. I work 9–6 and I’m exhausted. Give me a plan I’ll actually follow."},
        {"id":"RXT_002","domain":"career","constraint":"max 10 lines",
         "user_prompt":"I’m applying for jobs and I’m tired of advice that assumes I have endless energy. Give me a realistic weekly plan."},
    ]

    with PROMPTS.open("w", encoding="utf-8") as f:
        for row in seed:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"[ok] wrote {len(seed)} prompts to {PROMPTS}")

if __name__ == "__main__":
    main()
