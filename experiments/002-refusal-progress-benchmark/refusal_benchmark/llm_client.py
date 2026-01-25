from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional, Protocol


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMClient(Protocol):
    def chat(self, messages: List[ChatMessage]) -> str:
        ...


def build_messages(system_prompt: str, user_prompt: str) -> List[ChatMessage]:
    return [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", content=user_prompt),
    ]
