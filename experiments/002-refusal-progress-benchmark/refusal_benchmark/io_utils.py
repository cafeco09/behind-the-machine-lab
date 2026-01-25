from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

from .schema import PromptItem, StyleItem


def read_jsonl(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path)
    rows: List[Dict[str, Any]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def write_jsonl(path: str | Path, rows: Iterable[Dict[str, Any]]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def read_prompts(path: str | Path) -> List[PromptItem]:
    return [PromptItem.from_dict(r) for r in read_jsonl(path)]


def read_styles(path: str | Path) -> List[StyleItem]:
    d = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    styles = d.get("styles", [])
    return [StyleItem.from_dict(s) for s in styles]


def write_text(path: str | Path, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
