from typing import Protocol, Any, Dict


class LLMClientProtocol(Protocol):
    def generate_json(
        self,
        prompt: str,
        json_schema: Dict[str, Any],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        ...


def _default_from_schema(schema: Dict[str, Any]) -> Any:
    if "default" in schema:
        return schema["default"]

    schema_type = schema.get("type")

    if schema_type == "object":
        properties = schema.get("properties", {})
        return {
            key: _default_from_schema(value)
            for key, value in properties.items()
        }

    if schema_type == "array":
        return []

    if schema_type == "string":
        return ""

    if schema_type == "number":
        return 0.0

    if schema_type == "integer":
        return 0

    if schema_type == "boolean":
        return False

    return None


class _LLMStub:
    def generate_json(
        self,
        prompt: str,
        json_schema: Dict[str, Any],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        result = _default_from_schema(json_schema)
        return result if isinstance(result, dict) else {}


def get_llm_stub() -> LLMClientProtocol:
    return _LLMStub()


__all__ = ["LLMClientProtocol", "get_llm_stub"]
