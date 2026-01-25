from __future__ import annotations
import random
from typing import List
from ..llm_client import ChatMessage, LLMClient


class MockClient:
    """Deterministic-ish fake model for smoke tests.

    It *does not* implement safety; it just returns patterned text so the pipeline works.
    """

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)

    def chat(self, messages: List[ChatMessage]) -> str:
        user = next((m.content for m in messages if m.role == "user"), "")
        tag = self.rng.choice(["REFUSE", "CLARIFY", "PROCEED"])
        return f"[MOCK:{tag}] Response stub for: {user[:140]}"
