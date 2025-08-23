from typing import Any, Dict

import httpx
from pydantic import BaseModel

from app.llm_client import LLMClient


class FooModel(BaseModel):
    foo: str


def test_generate_json(monkeypatch):
    def fake_post(url: str, headers: Dict[str, str] | None = None, json: Any | None = None, timeout: int | None = None):
        class Resp:
            def json(self) -> Dict[str, Any]:
                return {"choices": [{"message": {"content": '{"foo": "bar"}'}}]}

            def raise_for_status(self) -> None:
                return None

        return Resp()

    monkeypatch.setattr(httpx, "post", fake_post)

    client = LLMClient(base_url="http://example.com", model="test-model")
    schema = {"type": "object", "properties": {"foo": {"type": "string"}}}
    result = client.generate_json("give foo", schema)

    assert result == {"foo": "bar"}
    FooModel.model_validate(result)
