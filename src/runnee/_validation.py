from __future__ import annotations
import json
import math
import re
from importlib.resources import files
from typing import Any
from .errors import RunneeResponseError, RunneeValidationError

CONTRACTS: dict[str, Any] = json.loads(files("runnee").joinpath("contracts.json").read_text(encoding="utf-8"))


def valid(value: Any, schema: dict[str, Any], depth: int = 0) -> bool:
    if depth > 40:
        return False
    if "$ref" in schema:
        return valid(value, CONTRACTS["schemas"][schema["$ref"].split("/")[-1]], depth + 1)
    if "anyOf" in schema:
        return any(valid(value, item, depth + 1) for item in schema["anyOf"])
    if "enum" in schema and value not in schema["enum"]:
        return False
    kind = schema.get("type")
    if kind == "null":
        return value is None
    if kind == "boolean":
        return isinstance(value, bool)
    if kind in ("number", "integer"):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            and (kind != "integer" or isinstance(value, int))
            and value >= schema.get("minimum", -math.inf)
            and value <= schema.get("maximum", math.inf)
        )
    if kind == "string":
        return (
            isinstance(value, str)
            and len(value) >= schema.get("minLength", 0)
            and len(value) <= schema.get("maxLength", math.inf)
            and ("pattern" not in schema or re.search(schema["pattern"], value) is not None)
            and (
                schema.get("format") != "uuid"
                or re.fullmatch(r"[a-fA-F0-9]{8}-(?:[a-fA-F0-9]{4}-){3}[a-fA-F0-9]{12}", value) is not None
            )
        )
    if kind == "array":
        return (
            isinstance(value, list)
            and len(value) >= schema.get("minItems", 0)
            and len(value) <= schema.get("maxItems", math.inf)
            and (
                not schema.get("uniqueItems")
                or len({json.dumps(v, sort_keys=True) for v in value}) == len(value)
            )
            and all(valid(item, schema.get("items", {}), depth + 1) for item in value)
        )
    if kind == "object":
        if not isinstance(value, dict) or len(value) < schema.get("minProperties", 0):
            return False
        if not all(key in value for key in schema.get("required", [])):
            return False
        for key, item in value.items():
            if key in schema.get("properties", {}):
                if not valid(item, schema["properties"][key], depth + 1):
                    return False
            elif schema.get("additionalProperties") is False:
                return False
            elif isinstance(schema.get("additionalProperties"), dict):
                if not valid(item, schema["additionalProperties"], depth + 1):
                    return False
    return True


def validate(value: Any, name: str, response: bool = False, request_id: str | None = None) -> None:
    if not valid(value, CONTRACTS["schemas"][name]):
        if response:
            raise RunneeResponseError("Runnee returned an unexpected response.", request_id=request_id)
        raise RunneeValidationError("Request does not match the Runnee API contract.")
