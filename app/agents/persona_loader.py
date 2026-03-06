from pathlib import Path

import yaml

from app.agents.models import AgentConfig


def load_agent_configs(path: Path) -> list[AgentConfig]:
    payload = yaml.safe_load(path.read_text())
    return [AgentConfig.model_validate(item) for item in payload.get("agents", [])]
