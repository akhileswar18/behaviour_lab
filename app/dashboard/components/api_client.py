import os
from typing import Any

import requests


def api_base() -> str:
    return os.getenv("BEHAVIOR_LAB_API", "http://127.0.0.1:8000")


def fetch_json(path: str, params: dict[str, Any] | None = None) -> Any:
    # Dashboard intentionally depends on persisted API state; no in-memory fallback is allowed.
    response = requests.get(f"{api_base()}{path}", params=params, timeout=5)
    response.raise_for_status()
    return response.json()


def post_json(path: str, payload: dict[str, Any]) -> Any:
    response = requests.post(f"{api_base()}{path}", json=payload, timeout=15)
    response.raise_for_status()
    return response.json()
