from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.schemas.decision_engine import DecisionContext


@dataclass
class PromptBuildResult:
    prompt: str
    prompt_hash: str
    summary: dict[str, Any]


def _trim_text(value: str, limit: int = 160) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def _top_events(rows: list[dict[str, Any]], limit: int = 6) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: int(row.get("tick_number", 0)), reverse=True)
    return ordered[:limit]


def _top_memories(rows: list[dict[str, Any]], limit: int = 6) -> list[dict[str, Any]]:
    ordered = sorted(
        rows,
        key=lambda row: (float(row.get("relevance_score", 0.0)), int(row.get("tick_number", 0))),
        reverse=True,
    )
    return ordered[:limit]


def _top_relationships(rows: list[dict[str, Any]], limit: int = 6) -> list[dict[str, Any]]:
    ordered = sorted(
        rows,
        key=lambda row: (
            abs(float(row.get("trust", 0.0))),
            abs(float(row.get("affinity", 0.0))),
        ),
        reverse=True,
    )
    return ordered[:limit]


def build_prompt(context: DecisionContext) -> PromptBuildResult:
    events = _top_events(context.observed_events)
    memories = _top_memories(context.recalled_memories)
    relationships = _top_relationships(context.relationships)
    resources = context.local_resources[:6]
    nearby_agents = (context.spatial_context.nearby_agents if context.spatial_context else [])[:6]
    nearby_objects = (context.spatial_context.nearby_objects if context.spatial_context else [])[:6]
    visible_resources = (context.spatial_context.visible_resources if context.spatial_context else [])[:6]
    pathfinding_costs = dict(sorted((context.spatial_context.pathfinding_costs if context.spatial_context else {}).items()))

    compact = {
        "agent": {
            "name": context.agent_name,
            "mood": context.mood,
            "persona": context.persona,
        },
        "needs": context.needs,
        "goal": context.active_goal or {},
        "intention": context.active_intention or {},
        "planning_context": context.planning_context,
        "zone": context.zone or {},
        "resources": resources,
        "spatial_context": {
            "current_room": context.spatial_context.current_room if context.spatial_context else None,
            "current_tile": (
                context.spatial_context.current_tile.model_dump()
                if context.spatial_context and context.spatial_context.current_tile
                else None
            ),
            "nearby_agents": [
                {
                    "agent_name": item.agent_name,
                    "tile_distance": item.tile_distance,
                    "zone_name": item.zone_name,
                }
                for item in nearby_agents
            ],
            "nearby_objects": [
                {
                    "name": item.name,
                    "zone_name": item.zone_name,
                    "affordance_type": item.affordance_type,
                    "resource_type": item.resource_type,
                    "tile_position": item.tile_position.model_dump(),
                }
                for item in nearby_objects
            ],
            "visible_resources": visible_resources,
            "pathfinding_costs": pathfinding_costs,
            "door_connections": list(context.spatial_context.door_connections if context.spatial_context else []),
        },
        "recent_world_events": [
            {
                "tick_number": int(item.get("tick_number", context.tick_number)),
                "event_type": item.get("event_type"),
                "content": _trim_text(str(item.get("content", ""))),
                "payload": item.get("payload", {}),
            }
            for item in events
        ],
        "relationships": [
            {
                "target_agent_id": str(item.get("target_agent_id") or item.get("source_agent_id") or ""),
                "trust": float(item.get("trust", 0.0)),
                "affinity": float(item.get("affinity", 0.0)),
                "stance": item.get("stance"),
            }
            for item in relationships
        ],
        "recalled_memories": [
            {
                "tick_number": int(item.get("tick_number", context.tick_number)),
                "memory_type": item.get("memory_type", "observation"),
                "content": _trim_text(str(item.get("content", ""))),
                "relevance_score": float(item.get("relevance_score", 0.0)),
                "salience": float(item.get("salience", 0.0)),
            }
            for item in memories
        ],
    }

    schema_instructions = (
        "Return only JSON with fields: "
        "action, intent, emotional_tone, rationale, confidence, "
        "target_agent_id (optional), target_zone_id (optional), target_resource_id (optional). "
        "Do not include markdown."
    )
    prompt = (
        f"Simulation tick {context.tick_number}. "
        f"Select one action for agent {context.agent_name}. "
        f"{schema_instructions}\n"
        f"Context JSON:\n{json.dumps(compact, ensure_ascii=True, sort_keys=True)}"
    )
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
    summary = {
        "tick_number": context.tick_number,
        "event_count": len(events),
        "memory_count": len(memories),
        "relationship_count": len(relationships),
        "resource_count": len(resources),
        "spatial_count": {
            "nearby_agents": len(nearby_agents),
            "nearby_objects": len(nearby_objects),
            "visible_resources": len(visible_resources),
            "pathfinding_targets": len(pathfinding_costs),
        },
        "truncated": {
            "events": max(0, len(context.observed_events) - len(events)),
            "memories": max(0, len(context.recalled_memories) - len(memories)),
            "relationships": max(0, len(context.relationships) - len(relationships)),
            "resources": max(0, len(context.local_resources) - len(resources)),
        },
    }
    return PromptBuildResult(prompt=prompt, prompt_hash=digest, summary=summary)
