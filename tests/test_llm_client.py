import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from unittest.mock import Mock, patch

from pydantic import BaseModel

from app.llm_client import LLMClient


def test_generate_json_strict_retries(monkeypatch):
    monkeypatch.setenv("VLLM_BASE_URL", "http://mock")
    monkeypatch.setenv("VLLM_MODEL", "test-model")

    client = LLMClient.from_env()

    schema = {
        "type": "object",
        "properties": {"value": {"type": "integer"}},
        "required": ["value"],
        "additionalProperties": False,
    }

    class Result(BaseModel):
        value: int

    bad = Mock()
    bad.json.return_value = {"choices": [{"message": {"content": "oops {\"value\":1}"}}]}
    bad.raise_for_status.return_value = None

    good = Mock()
    good.json.return_value = {"choices": [{"message": {"content": '{"value":1}'}}]}
    good.raise_for_status.return_value = None

    with patch("app.llm_client.requests.post", side_effect=[bad, good]) as mpost:
        data = client.generate_json("prompt", schema)

    Result(**data)
    assert mpost.call_count == 2
