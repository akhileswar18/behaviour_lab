from __future__ import annotations

from typing import Any
from uuid import UUID

from app.persistence.models import AgentStateSnapshot, Goal, Intention, Resource, Zone
from app.schemas.spatial import SpatialPerception
from app.schemas.settings import get_settings
from app.schemas.social import GoalStatus, IntentionStatus, SocialAction


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _resource_zone(resources: list[Resource], resource_type: str) -> UUID | None:
    for resource in resources:
        if resource.resource_type == resource_type and resource.quantity > 0:
            return resource.zone_id
    return None


def _zone_id_by_name(zones_by_id: dict[UUID, Zone] | None, zone_name: str) -> UUID | None:
    if not zones_by_id:
        return None
    for zone in zones_by_id.values():
        if zone.name == zone_name:
            return zone.id
    return None


def _nearest_resource(
    resources: list[Resource],
    resource_type: str,
    zones_by_id: dict[UUID, Zone] | None,
    spatial_context: SpatialPerception | None,
) -> tuple[Resource | None, str | None, int | None]:
    fallback = next(
        (resource for resource in resources if resource.resource_type == resource_type and resource.quantity > 0),
        None,
    )
    if fallback is None:
        return None, None, None
    if spatial_context is None or not zones_by_id:
        zone = zones_by_id.get(fallback.zone_id) if zones_by_id else None
        return fallback, zone.name if zone else None, None

    best_resource = fallback
    best_zone = zones_by_id.get(fallback.zone_id)
    best_cost = None
    for resource in resources:
        if resource.resource_type != resource_type or resource.quantity <= 0:
            continue
        zone = zones_by_id.get(resource.zone_id)
        if zone is None:
            continue
        key = f"{zone.name}:{resource.resource_type}"
        cost = spatial_context.pathfinding_costs.get(key)
        if cost is None:
            continue
        if best_cost is None or cost < best_cost:
            best_resource = resource
            best_zone = zone
            best_cost = cost
    return best_resource, best_zone.name if best_zone else None, best_cost


def select_plan(
    latest_state: AgentStateSnapshot | None,
    active_goal: Goal | None,
    active_intention: Intention | None,
    zone: Zone | None,
    local_resources: list[Resource],
    all_resources: list[Resource],
    urgent_events: list[dict[str, Any]],
    zones_by_id: dict[UUID, Zone] | None = None,
    spatial_context: SpatialPerception | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    hunger = _clamp(latest_state.hunger if latest_state else 0.0)
    safety_need = _clamp(latest_state.safety_need if latest_state else 0.0)
    social_need = _clamp(latest_state.social_need if latest_state else 0.0)
    inventory = dict(latest_state.inventory if latest_state else {})
    zone_name = zone.name if zone else "unknown"

    if urgent_events and (active_intention is None or active_intention.is_interruptible):
        target_zone_id = _zone_id_by_name(zones_by_id, "Shelter")
        return {
            "goal_type": "seek_safety",
            "goal_priority": 1.0,
            "goal_source": "world_event",
            "goal_target": {"zone": "Shelter"},
            "action": SocialAction.MOVE.value if zone_name != "Shelter" else SocialAction.OBSERVE.value,
            "rationale": "Urgent event overrides the current plan and shifts the agent toward safety.",
            "interrupt": True,
            "target_zone_id": target_zone_id,
            "target_resource_id": None,
        }

    if hunger >= settings.severe_need_threshold:
        if inventory.get("food", 0) > 0:
            return {
                "goal_type": "satisfy_hunger",
                "goal_priority": hunger,
                "goal_source": "need",
                "goal_target": {"resource_type": "food", "zone": zone_name},
                "action": SocialAction.CONSUME_RESOURCE.value,
                "rationale": "Severe hunger makes immediate consumption the highest-priority action.",
                "interrupt": active_goal is not None and active_goal.goal_type != "satisfy_hunger",
                "target_zone_id": zone.id if zone else None,
                "target_resource_id": None,
            }
        local_food = next((item for item in local_resources if item.resource_type == "food" and item.quantity > 0), None)
        if local_food is not None:
            return {
                "goal_type": "satisfy_hunger",
                "goal_priority": hunger,
                "goal_source": "need",
                "goal_target": {"resource_type": "food", "zone": zone_name},
                "action": SocialAction.ACQUIRE_RESOURCE.value,
                "rationale": "Severe hunger makes nearby food acquisition the highest-priority action.",
                "interrupt": active_goal is not None and active_goal.goal_type != "satisfy_hunger",
                "target_zone_id": zone.id if zone else None,
                "target_resource_id": local_food.id,
            }
        nearest_food, food_zone_name, path_cost = _nearest_resource(
            all_resources,
            "food",
            zones_by_id,
            spatial_context,
        )
        food_zone_id = nearest_food.zone_id if nearest_food is not None else _resource_zone(all_resources, "food")
        target_zone_name = food_zone_name or "known food"
        rationale = "Hunger is high enough to redirect movement toward known food."
        if path_cost is not None:
            rationale = (
                f"Hunger is high enough to redirect movement toward food in {target_zone_name} "
                f"with path cost {path_cost}."
            )
        return {
            "goal_type": "satisfy_hunger",
            "goal_priority": hunger,
            "goal_source": "need",
            "goal_target": {"resource_type": "food", "zone": food_zone_name} if food_zone_name else {"resource_type": "food"},
            "action": SocialAction.MOVE.value,
            "rationale": rationale,
            "interrupt": active_goal is not None and active_goal.goal_type != "satisfy_hunger",
            "target_zone_id": food_zone_id,
            "target_resource_id": None,
        }

    if safety_need >= settings.severe_need_threshold and zone_name != "Shelter":
        return {
            "goal_type": "seek_safety",
            "goal_priority": safety_need,
            "goal_source": "need",
            "goal_target": {"zone": "Shelter"},
            "action": SocialAction.MOVE.value,
            "rationale": "Safety need is severe, so the agent moves to shelter.",
            "interrupt": active_goal is not None and active_goal.goal_type != "seek_safety",
            "target_zone_id": _zone_id_by_name(zones_by_id, "Shelter"),
            "target_resource_id": None,
        }

    if active_goal is not None and active_goal.status == GoalStatus.ACTIVE.value:
        target_zone_name = str(active_goal.target.get("zone", "")).strip()
        if target_zone_name and zone_name != target_zone_name:
            return {
                "goal_type": active_goal.goal_type,
                "goal_priority": active_goal.priority,
                "goal_source": active_goal.source,
                "goal_target": active_goal.target,
                "action": SocialAction.MOVE.value,
                "rationale": f"Continue active goal '{active_goal.goal_type}' by moving toward its target zone.",
                "interrupt": False,
                "target_zone_id": _zone_id_by_name(zones_by_id, target_zone_name),
                "target_resource_id": None,
            }
        if social_need >= 0.55:
            return {
                "goal_type": active_goal.goal_type,
                "goal_priority": active_goal.priority,
                "goal_source": active_goal.source,
                "goal_target": active_goal.target,
                "action": SocialAction.COOPERATE.value,
                "rationale": f"Social need supports cooperative progress on goal '{active_goal.goal_type}'.",
                "interrupt": False,
                "target_zone_id": zone.id if zone else None,
                "target_resource_id": None,
            }
        return {
            "goal_type": active_goal.goal_type,
            "goal_priority": active_goal.priority,
            "goal_source": active_goal.source,
            "goal_target": active_goal.target,
            "action": SocialAction.OBSERVE.value,
            "rationale": f"Continue observing while maintaining goal '{active_goal.goal_type}'.",
            "interrupt": False,
            "target_zone_id": zone.id if zone else None,
            "target_resource_id": None,
        }

    return {
        "goal_type": "maintain_context",
        "goal_priority": 0.4,
        "goal_source": "fallback",
        "goal_target": {"zone": zone_name},
        "action": SocialAction.OBSERVE.value,
        "rationale": "No urgent need dominates, so the agent continues observing local context.",
        "interrupt": False,
        "target_zone_id": zone.id if zone else None,
        "target_resource_id": None,
    }


def resolve_goal_status(action: str, succeeded: bool) -> str:
    if not succeeded:
        return GoalStatus.DEFERRED.value
    if action in {SocialAction.CONSUME_RESOURCE.value, SocialAction.ACQUIRE_RESOURCE.value}:
        return GoalStatus.COMPLETED.value
    return GoalStatus.ACTIVE.value


def resolve_intention_status(action: str, succeeded: bool, interrupted: bool) -> str:
    if interrupted:
        return IntentionStatus.INTERRUPTED.value
    if not succeeded:
        return IntentionStatus.DEFERRED.value
    if action in {SocialAction.CONSUME_RESOURCE.value, SocialAction.ACQUIRE_RESOURCE.value}:
        return IntentionStatus.COMPLETED.value
    return IntentionStatus.ACTIVE.value
