from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import cos, sin, tau
import re


AGENT_COLORS = [
    "#7F77DD",
    "#D85A30",
    "#D4537E",
    "#378ADD",
    "#639922",
    "#BA7517",
    "#1D9E75",
    "#E24B4A",
]

RESOURCE_OK = "#1D9E75"
RESOURCE_WARN = "#BA7517"
RESOURCE_CRITICAL = "#E24B4A"
RESOURCE_TRACK = "#D7DADF"
NODE_FILL = "#F8F6F1"
NODE_BORDER = "#264653"

MOVE_PATTERN = re.compile(r"^(?P<agent>.+?) moved to (?P<zone>.+?)$", re.IGNORECASE)


@dataclass
class ZoneNode:
    zone_id: str
    zone_name: str
    zone_type: str
    x: float
    y: float
    occupants: list[dict]
    resources: list[dict]


@dataclass
class ZoneEdge:
    source_zone_id: str
    target_zone_id: str
    agent_movements: int


@dataclass
class AgentTransit:
    agent_name: str
    agent_color: str
    from_zone_id: str
    to_zone_id: str


@dataclass
class WorldGraph:
    nodes: list[ZoneNode]
    edges: list[ZoneEdge]
    transits: list[AgentTransit]


def _health_color(percentage: float) -> str:
    if percentage < 0.3:
        return RESOURCE_CRITICAL
    if percentage < 0.5:
        return RESOURCE_WARN
    return RESOURCE_OK


def _layout_positions(zone_ids: list[str]) -> dict[str, tuple[float, float]]:
    count = len(zone_ids)
    if count <= 0:
        return {}
    if count == 1:
        return {zone_ids[0]: (0.5, 0.5)}
    if count <= 6:
        presets = [
            (0.22, 0.28),
            (0.50, 0.22),
            (0.78, 0.28),
            (0.22, 0.72),
            (0.50, 0.78),
            (0.78, 0.72),
        ]
        return {zone_id: presets[index] for index, zone_id in enumerate(zone_ids)}

    radius = 0.34
    center_x = 0.5
    center_y = 0.5
    positions: dict[str, tuple[float, float]] = {}
    for index, zone_id in enumerate(zone_ids):
        angle = (tau * index / count) - (tau / 4)
        positions[zone_id] = (center_x + radius * cos(angle), center_y + radius * sin(angle))
    return positions


def _agent_color_map(zone_rows: list[dict], event_rows: list[dict]) -> dict[str, str]:
    agent_names = {
        occupant.get("agent_name", "").strip()
        for zone in zone_rows
        for occupant in zone.get("occupants", [])
        if occupant.get("agent_name")
    }
    for event in event_rows:
        match = MOVE_PATTERN.match(str(event.get("content", "")).strip())
        if match:
            agent_names.add(match.group("agent").strip())
    ordered = sorted(name for name in agent_names if name)
    return {
        name: AGENT_COLORS[index % len(AGENT_COLORS)]
        for index, name in enumerate(ordered)
    }


def _resource_rows_by_zone(resource_rows: list[dict]) -> dict[str, dict[str, dict]]:
    grouped: dict[str, dict[str, dict]] = {}
    for row in resource_rows:
        zone_id = str(row.get("zone_id", ""))
        resource_type = str(row.get("resource_type", "resource"))
        zone_bucket = grouped.setdefault(zone_id, {})
        if resource_type not in zone_bucket:
            zone_bucket[resource_type] = {
                "resource_type": resource_type,
                "quantity": int(row.get("quantity", 0) or 0),
                "status": row.get("status", "available"),
            }
        else:
            zone_bucket[resource_type]["quantity"] += int(row.get("quantity", 0) or 0)
    return grouped


def _resource_maxima(resource_rows: list[dict]) -> dict[str, int]:
    maxima: dict[str, int] = {}
    for row in resource_rows:
        resource_type = str(row.get("resource_type", "resource"))
        quantity = int(row.get("quantity", 0) or 0)
        maxima[resource_type] = max(maxima.get(resource_type, 0), quantity)
    return {key: max(value, 1) for key, value in maxima.items()}


def _movement_counts(
    event_rows: list[dict],
    zone_name_to_id: dict[str, str],
    agent_colors: dict[str, str],
    current_tick: int,
) -> tuple[dict[tuple[str, str], int], list[AgentTransit]]:
    counts: dict[tuple[str, str], int] = {}
    transits: list[AgentTransit] = []
    last_zone_by_agent: dict[str, str] = {}
    recent_moves_by_agent: dict[str, AgentTransit] = {}

    ordered = sorted(
        event_rows,
        key=lambda row: (int(row.get("tick_number", 0)), row.get("created_at", "")),
    )
    for event in ordered:
        if event.get("event_type") != "move":
            continue
        match = MOVE_PATTERN.match(str(event.get("content", "")).strip())
        if not match:
            continue
        agent_name = match.group("agent").strip()
        zone_name = match.group("zone").strip()
        destination_id = str((event.get("payload") or {}).get("zone_id") or zone_name_to_id.get(zone_name, ""))
        source_id = last_zone_by_agent.get(agent_name)
        if source_id and destination_id and source_id != destination_id:
            edge_key = tuple(sorted((source_id, destination_id)))
            counts[edge_key] = counts.get(edge_key, 0) + 1
            if int(event.get("tick_number", 0)) >= max(current_tick - 1, 0):
                recent_moves_by_agent[agent_name] = AgentTransit(
                    agent_name=agent_name,
                    agent_color=agent_colors.get(agent_name, AGENT_COLORS[0]),
                    from_zone_id=source_id,
                    to_zone_id=destination_id,
                )
        if destination_id:
            last_zone_by_agent[agent_name] = destination_id

    transits = list(recent_moves_by_agent.values())[:6]
    return counts, transits


def build_world_graph(snapshot: dict) -> WorldGraph:
    zone_rows = snapshot.get("zone_occupancy", [])
    resource_rows = snapshot.get("resource_distribution", [])
    event_rows = snapshot.get("global_event_feed", [])
    current_tick = int(snapshot.get("current_tick", 0) or 0)

    zone_ids = [str(zone.get("zone_id")) for zone in zone_rows if zone.get("zone_id")]
    positions = _layout_positions(zone_ids)
    zone_name_to_id = {
        str(zone.get("zone_name", "")): str(zone.get("zone_id"))
        for zone in zone_rows
        if zone.get("zone_id")
    }
    agent_colors = _agent_color_map(zone_rows, event_rows)
    resource_by_zone = _resource_rows_by_zone(resource_rows)
    resource_maxima = _resource_maxima(resource_rows)
    movement_counts, transits = _movement_counts(
        event_rows,
        zone_name_to_id=zone_name_to_id,
        agent_colors=agent_colors,
        current_tick=current_tick,
    )

    nodes: list[ZoneNode] = []
    for zone in zone_rows:
        zone_id = str(zone.get("zone_id"))
        resource_types = set(zone.get("resource_types", []))
        resource_types.update(resource_by_zone.get(zone_id, {}).keys())
        resources = []
        for resource_type in sorted(resource_types):
            resource_row = resource_by_zone.get(zone_id, {}).get(
                resource_type,
                {"resource_type": resource_type, "quantity": 0, "status": "depleted"},
            )
            max_quantity = resource_maxima.get(resource_type, max(int(resource_row["quantity"]), 1))
            quantity = int(resource_row["quantity"])
            percentage = min(max(quantity / max_quantity, 0.0), 1.0)
            resources.append(
                {
                    "resource_type": resource_type,
                    "quantity": quantity,
                    "max_quantity": max_quantity,
                    "percentage": percentage,
                    "health_color": _health_color(percentage),
                    "track_color": RESOURCE_TRACK,
                    "status": resource_row.get("status", "available"),
                }
            )

        occupants = []
        for occupant in zone.get("occupants", []):
            agent_name = occupant.get("agent_name", "Agent")
            occupants.append(
                {
                    "agent_id": occupant.get("agent_id"),
                    "agent_name": agent_name,
                    "color": agent_colors.get(agent_name, AGENT_COLORS[0]),
                }
            )

        x, y = positions.get(zone_id, (0.5, 0.5))
        nodes.append(
            ZoneNode(
                zone_id=zone_id,
                zone_name=str(zone.get("zone_name", "Zone")),
                zone_type=str(zone.get("zone_type", "zone")),
                x=x,
                y=y,
                occupants=occupants,
                resources=resources,
            )
        )

    edges = [
        ZoneEdge(
            source_zone_id=source_id,
            target_zone_id=target_id,
            agent_movements=movement_counts.get(tuple(sorted((source_id, target_id))), 0),
        )
        for source_id, target_id in combinations(zone_ids, 2)
    ]
    return WorldGraph(nodes=nodes, edges=edges, transits=transits)
