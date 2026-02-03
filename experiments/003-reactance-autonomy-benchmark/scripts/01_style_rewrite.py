"""
Takes a neutral output and produces two rewrites:
- pressure
- autonomy

This script does NOT call any APIs by default.
It provides deterministic rewriting rules you can apply manually or extend later.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
OUT = DATA / "outputs.jsonl"

STYLE_RULES = {
    "pressure": [
        (r"\bmaybe\b", ""),
        (r"\byou can\b", "you should"),
        (r"\btry to\b", "do"),
        (r"\bif you want\b", ""),
        (r"\bconsider\b", "do"),
    ],
    "autonomy": [
        (r"\byou should\b", "you could"),
        (r"\byou need to\b", "it might help to"),
        (r"\bdo this\b", "one option is to do this"),
    ],
}

def normalise_spaces(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).strip()

def rewrite(text: str, style: str) -> str:
    out = text
    for pat, rep in STYLE_RULES.get(style, []):
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)
    out = normalise_spaces(out)

    if style == "pressure":
        if not re.match(r"^(do|start|stop|you should|you need)", out.strip(), flags=re.IGNORECASE):
            out = "Do this first: " + out
    elif style == "autonomy":
        if "option" not in out.lower():
            out = "If you want something lightweight, here are two options. " + out

    return out

def main() -> None:
    if not OUT.exists() or OUT.stat().st_size == 0:
        print("[info] outputs.jsonl is empty. Add neutral outputs first, then run this script.")
        return

    rows = []
    with OUT.open("r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    existing = {(r["id"], r["style"]) for r in rows if "id" in r and "style" in r}

    new_rows = []
    for r in rows:
        if r.get("style") != "neutral":
            continue

        base_text = r.get("output", "")
        for style in ("pressure", "autonomy"):
            key = (r["id"], style)
            if key in existing:
                continue
            new_rows.append({
                "id": r["id"],
                "style": style,
                "model": r.get("model", ""),
                "output": rewrite(base_text, style),
                "source": "rule_rewrite_v0"
            })

    if not new_rows:
        print("[ok] nothing to add (pressure/autonomy already present)")
        return

    with OUT.open("a", encoding="utf-8") as f:
        for r in new_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[ok] appended {len(new_rows)} rewrites to {OUT}")

if __name__ == "__main__":
    main()
