import json
import os
from typing import Any, Dict, Optional

import httpx

from .contracts import LLMClientProtocol, get_llm_stub


class LLMClient(LLMClientProtocol):
    """LLM client using an OpenAI compatible API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.base_url = base_url or os.getenv("VLLM_BASE_URL")
        self.model = model or os.getenv("VLLM_MODEL", "Qwen/Qwen2.5-14B-Instruct")
        self.api_key = api_key or os.getenv("VLLM_API_KEY")
        self._stub = get_llm_stub()

    def _post(
        self,
        messages: list[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        headers: Dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        resp = httpx.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def generate_json(
        self,
        prompt: str,
        json_schema: Dict[str, Any],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        if not self.base_url:
            return self._stub.generate_json(prompt, json_schema, temperature, max_tokens)

        schema_str = json.dumps(json_schema, ensure_ascii=False)
        base_messages = [
            {"role": "system", "content": "верни ТОЛЬКО валидный JSON строго по схеме"},
            {
                "role": "user",
                "content": f"{prompt}\n\nJSON schema:\n{schema_str}",
            },
        ]
        try:
            content = self._post(base_messages, temperature, max_tokens)
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                messages = base_messages + [
                    {"role": "assistant", "content": content},
                    {"role": "user", "content": "почини JSON"},
                ]
                content = self._post(messages, temperature, max_tokens)
                return json.loads(content)
        except (httpx.HTTPError, json.JSONDecodeError, KeyError, ValueError):
            pass
        return self._stub.generate_json(prompt, json_schema, temperature, max_tokens)
