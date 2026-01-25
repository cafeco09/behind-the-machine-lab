from refusal_benchmark.schema import PromptItem, StyleItem


def test_prompt_item_roundtrip():
    d = {
        "id": "p001",
        "category": "A",
        "risk_level": 5,
        "expected_action": "refuse",
        "user_intent": "malicious",
        "prompt": "Test",
    }
    p = PromptItem.from_dict(d)
    assert p.to_dict()["id"] == "p001"


def test_style_item_roundtrip():
    d = {"id": "hard_stop", "name": "Hard stop", "system_prompt": "X"}
    s = StyleItem.from_dict(d)
    assert s.id == "hard_stop"
