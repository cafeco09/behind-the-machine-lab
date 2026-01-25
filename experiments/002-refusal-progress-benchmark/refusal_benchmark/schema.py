from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class PromptItem:
    id: str
    category: str
    risk_level: int
    expected_action: str
    user_intent: str
    prompt: str

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PromptItem":
        return PromptItem(
            id=str(d["id"]),
            category=str(d["category"]),
            risk_level=int(d["risk_level"]),
            expected_action=str(d.get("expected_action", "")),
            user_intent=str(d.get("user_intent", "")),
            prompt=str(d["prompt"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StyleItem:
    id: str
    name: str
    system_prompt: str

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "StyleItem":
        return StyleItem(
            id=str(d["id"]),
            name=str(d.get("name", d["id"])),
            system_prompt=str(d["system_prompt"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RunMeta:
    run_id: str
    created_utc: str
    git_commit: Optional[str]
    provider: str
    model: str
    temperature: float
    max_tokens: int
    seed: int
    base_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
