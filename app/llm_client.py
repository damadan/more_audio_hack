from __future__ import annotations

import json
import os
import logging
from typing import Any, Dict

import requests
from jsonschema import validate
import time
from prometheus_client import Histogram


LLM_LATENCY = Histogram("llm_latency", "LLM latency")


class LLMClient:
    """Minimal client for OpenAI-compatible chat completion API."""

    def __init__(self, base_url: str, api_key: str | None, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    @classmethod
    def from_env(cls) -> "LLMClient":
        """Create client configured via environment variables."""
        base_url = os.environ["VLLM_BASE_URL"]
        model = os.environ.get("VLLM_MODEL", "Qwen/Qwen2.5-14B-Instruct")
        api_key = os.environ.get("VLLM_API_KEY")
        return cls(base_url=base_url, api_key=api_key, model=model)

    def generate_json(
        self,
        prompt: str,
        json_schema: Dict[str, Any],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Generate JSON from the model and validate against ``json_schema``.

        The LLM is instructed via system prompt to return *only* JSON.  When the
        returned content cannot be parsed or does not validate against the
        provided schema, the request is retried once more.  On success a Python
        ``dict`` is returned.
        """

        url = f"{self.base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        schema_str = json.dumps(json_schema)
        system_prompt = (
            "верни ТОЛЬКО валидный JSON по схеме "
            f"{schema_str} без комментариев, без markdown"
        )

        for attempt in range(2):
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            start = time.time()
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            LLM_LATENCY.observe(time.time() - start)
            content = resp.json()["choices"][0]["message"]["content"]
            try:
                data = json.loads(content)
                validate(data, json_schema)
                return data
            except Exception:
                logging.debug("invalid LLM response: %s", content)
                if attempt == 1:
                    break
                continue

        raise ValueError("LLM did not return valid JSON")
