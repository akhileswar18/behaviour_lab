from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Protocol

import requests

from app.schemas.decision_engine import LlmConfig
from app.schemas.settings import get_settings


@dataclass
class ModelResponse:
    success: bool
    text: str
    latency_ms: int
    provider: str | None
    model: str | None
    error: str | None = None


class ModelAdapter(Protocol):
    def generate(self, prompt: str, config: LlmConfig) -> ModelResponse:
        ...


class OpenAICompatibleAdapter:
    def generate(self, prompt: str, config: LlmConfig) -> ModelResponse:
        settings = get_settings()
        endpoint = config.endpoint or settings.llm_endpoint
        model = config.model or settings.llm_model
        provider = config.provider or settings.llm_provider
        api_key = config.api_key or settings.llm_api_key
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "messages": [
                {"role": "system", "content": "Return only JSON for the requested decision schema."},
                {"role": "user", "content": prompt},
            ],
        }
        start = time.perf_counter()
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(payload),
                timeout=config.timeout_seconds,
            )
            response.raise_for_status()
            body = response.json()
            text = (
                body.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            return ModelResponse(
                success=True,
                text=text or "",
                latency_ms=int((time.perf_counter() - start) * 1000),
                provider=provider,
                model=model,
            )
        except requests.Timeout as exc:
            return ModelResponse(
                success=False,
                text="",
                latency_ms=int((time.perf_counter() - start) * 1000),
                provider=provider,
                model=model,
                error=f"timeout:{exc}",
            )
        except Exception as exc:  # noqa: BLE001
            return ModelResponse(
                success=False,
                text="",
                latency_ms=int((time.perf_counter() - start) * 1000),
                provider=provider,
                model=model,
                error=str(exc),
            )


class UnavailableAdapter:
    def generate(self, prompt: str, config: LlmConfig) -> ModelResponse:
        _ = prompt
        return ModelResponse(
            success=False,
            text="",
            latency_ms=0,
            provider=config.provider,
            model=config.model,
            error="provider_unavailable",
        )


def get_model_adapter(provider: str | None) -> ModelAdapter:
    if provider in {None, "", "openai_compatible"}:
        return OpenAICompatibleAdapter()
    return UnavailableAdapter()
