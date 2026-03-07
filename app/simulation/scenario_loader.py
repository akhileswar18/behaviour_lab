from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_scenario_config(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def load_named_scenario_config(name: str) -> dict:
    config_dir = Path(__file__).resolve().parents[1] / "configs" / "scenarios"
    file_path = config_dir / f"{name}.yaml"
    if not file_path.exists():
        raise FileNotFoundError(f"Scenario config not found: {file_path}")
    return load_scenario_config(file_path)


def merge_persona_overrides(
    base_personas: dict[str, dict[str, Any]], overrides: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for agent_name, base_persona in base_personas.items():
        merged_persona = dict(base_persona)
        for key, value in overrides.get(agent_name, {}).items():
            merged_persona[key] = value
        merged[agent_name] = merged_persona
    return merged


def merge_agent_state_overrides(
    base_states: dict[str, dict[str, Any]], overrides: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for agent_name, base_state in base_states.items():
        state = dict(base_state)
        for key, value in overrides.get(agent_name, {}).items():
            state[key] = value
        merged[agent_name] = state
    return merged


def merge_world_overrides(
    base_world: dict[str, dict[str, Any]], overrides: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for key, value in base_world.items():
        merged[key] = dict(value)
        for override_key, override_value in overrides.get(key, {}).items():
            merged[key][override_key] = override_value
    for key, override_value in overrides.items():
        if key not in merged:
            merged[key] = dict(override_value)
    return merged


def build_variant_name(base_name: str, variant_name: str) -> str:
    suffix = variant_name.strip() or "variant"
    return f"{base_name}-{suffix}"
