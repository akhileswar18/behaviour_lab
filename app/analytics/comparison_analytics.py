from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import DecisionLog, Goal, Message, Relationship, RunMetadata, SimulationEvent, TickResult


@dataclass
class ScenarioCounts:
    ticks: int
    decisions: int
    messages: int
    avg_trust: float
    completed_goals: int
    cooperation_events: int
    conflict_events: int
    fallback_count: int
    llm_decisions: int


def _scenario_counts(session: Session, scenario_id: UUID) -> ScenarioCounts:
    ticks = list(session.exec(select(TickResult).where(TickResult.scenario_id == scenario_id)))
    decisions = list(session.exec(select(DecisionLog).where(DecisionLog.scenario_id == scenario_id)))
    messages = list(session.exec(select(Message).where(Message.scenario_id == scenario_id)))
    relationships = list(session.exec(select(Relationship).where(Relationship.scenario_id == scenario_id)))
    goals = list(session.exec(select(Goal).where(Goal.scenario_id == scenario_id)))
    events = list(session.exec(select(SimulationEvent).where(SimulationEvent.scenario_id == scenario_id)))
    avg_trust = sum(item.trust for item in relationships) / len(relationships) if relationships else 0.0
    completed_goals = sum(1 for item in goals if item.status == "completed")
    cooperation_events = sum(
        1
        for item in events
        if item.event_type == "message" and str((item.payload or {}).get("intent")) in {"cooperate", "propose"}
    )
    conflict_events = sum(
        1
        for item in events
        if item.event_type == "message" and str((item.payload or {}).get("intent")) in {"warn", "avoid"}
    )
    fallback_count = sum(
        1
        for item in decisions
        if item.decision_source == "fallback_deterministic" or bool(item.fallback_reason)
    )
    llm_decisions = sum(1 for item in decisions if item.decision_source == "llm")
    return ScenarioCounts(
        ticks=len(ticks),
        decisions=len(decisions),
        messages=len(messages),
        avg_trust=avg_trust,
        completed_goals=completed_goals,
        cooperation_events=cooperation_events,
        conflict_events=conflict_events,
        fallback_count=fallback_count,
        llm_decisions=llm_decisions,
    )


def compare_policy_modes(
    session: Session,
    base_scenario_id: UUID,
    variant_scenario_id: UUID,
) -> dict:
    base = _scenario_counts(session, base_scenario_id)
    variant = _scenario_counts(session, variant_scenario_id)
    base_run = session.exec(
        select(RunMetadata).where(RunMetadata.scenario_id == base_scenario_id).order_by(RunMetadata.created_at.desc())
    ).first()
    variant_run = session.exec(
        select(RunMetadata).where(RunMetadata.scenario_id == variant_scenario_id).order_by(RunMetadata.created_at.desc())
    ).first()
    return {
        "base_policy_mode": base_run.policy_mode if base_run else "deterministic",
        "variant_policy_mode": variant_run.policy_mode if variant_run else "deterministic",
        "deltas": {
            "tick_count_delta": variant.ticks - base.ticks,
            "decision_count_delta": variant.decisions - base.decisions,
            "message_count_delta": variant.messages - base.messages,
            "relationship_avg_trust_delta": round(variant.avg_trust - base.avg_trust, 6),
            "completed_goal_delta": variant.completed_goals - base.completed_goals,
            "cooperation_event_delta": variant.cooperation_events - base.cooperation_events,
            "conflict_event_delta": variant.conflict_events - base.conflict_events,
            "fallback_count_delta": variant.fallback_count - base.fallback_count,
            "llm_decision_delta": variant.llm_decisions - base.llm_decisions,
        },
    }
