"""
Unit Tests for Jev System One Client ⚡
"""

import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).parent.parent / "src"))

from jev_system_one import JevClient, DecisionResponse, QuestionResult


def test_mock_decision_choice():
    client = JevClient(backend="mock")
    state = {"text": "Qarz daftari"}
    questions = [
        {"name": "intent", "type": "choice", "options": ["DEBT", "SALE"]}
    ]
    res = client.decide(state=state, questions=questions)
    assert isinstance(res, DecisionResponse)
    assert "intent" in res.results
    assert res.results["intent"].value == "DEBT"
    assert res.results["intent"].confidence > 0.90


def test_mock_decision_noul():
    client = JevClient(backend="mock")
    state = {"action": "delete_all"}
    questions = [
        {"name": "is_dangerous", "type": "noul"}
    ]
    res = client.decide(state=state, questions=questions)
    assert "is_dangerous" in res.results
    assert isinstance(res.results["is_dangerous"].value, bool)
    assert res.results["is_dangerous"].confidence > 0.90


def test_mock_decision_score():
    client = JevClient(backend="mock")
    state = {"rating": "excellent"}
    questions = [
        {"name": "score", "type": "score", "min": 0, "max": 100}
    ]
    res = client.decide(state=state, questions=questions)
    assert "score" in res.results
    assert res.results["score"].value == 50.0


@pytest.mark.asyncio
async def test_async_decision():
    client = JevClient(backend="mock")
    state = {"msg": "hello"}
    questions = [{"name": "is_greeting", "type": "noul"}]
    res = await client.decide_async(state=state, questions=questions)
    assert res.results["is_greeting"].value is True
