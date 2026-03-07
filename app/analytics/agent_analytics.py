from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from uuid import UUID

from sqlmodel import Session, select

from app.analytics.social_analytics import interaction_metrics
from app.analytics.world_analytics import goal_completion_rate
from app.api.schemas.analytics import (
    ActionMixItemRead,
    AgentIdentityRead,
    AgentObservatoryRead,
    AgentScenarioOptionRead,
    AgentSummaryRead,
    BehavioralTrendPointRead,
    DecisionTraceRead,
    GoalSummaryRead,
    InteractionMetricsRead,
    IntentionSummaryRead,
    InventoryItemRead,
    MemoryInfluenceRead,
    MemoryInfluenceTrendPointRead,
    MemorySummaryRead,
    NeedGaugeRead,
    NeedHistoryPointRead,
    PlanHistoryPointRead,
    RelationshipSummaryRead,
)
from app.persistence.models import Agent, DecisionLog, Memory, MemoryRetrievalTrace, PersonaProfile, Scenario
from app.persistence.repositories.agent_repository import AgentRepository
from app.persistence.repositories.planning_repository import PlanningRepository
from app.persistence.repositories.social_repository import SocialRepository
from app.persistence.repositories.world_repository import WorldRepository


@dataclass
class AgentIdentityRecord:
    agent: Agent
    persona: PersonaProfile | None
    scenario_name: str
    latest_zone_name: str | None
    latest_mood: str
    latest_tick: int


def _severity(value: float) -> str:
    if value >= 0.8:
        return "critical"
    if value >= 0.5:
        return "elevated"
    return "stable"


class AgentAnalyticsService:
    def __init__(self, session: Session):
        self.session = session
        self.agent_repo = AgentRepository(session)
        self.planning_repo = PlanningRepository(session)
        self.social_repo = SocialRepository(session)
        self.world_repo = WorldRepository(session)

    @staticmethod
    def identity_key(name: str, persona_label: str) -> str:
        return f"{name.strip().lower()}::{persona_label.strip().lower()}"

    def list_agent_identities(self) -> list[AgentIdentityRead]:
        groups = self._identity_groups()
        identities: list[AgentIdentityRead] = []
        for key, records in groups.items():
            latest = max(records, key=lambda row: (row.latest_tick, row.agent.created_at))
            scenario_map: dict[UUID, str] = {}
            for row in records:
                scenario_map[row.agent.scenario_id] = row.scenario_name
            scenario_options = [
                AgentScenarioOptionRead(scenario_id=scenario_id, scenario_name=scenario_name)
                for scenario_id, scenario_name in sorted(
                    scenario_map.items(), key=lambda item: item[1].lower()
                )
            ]
            persona_label = latest.persona.label if latest.persona else "persona"
            identities.append(
                AgentIdentityRead(
                    identity_key=key,
                    name=latest.agent.name,
                    persona_label=persona_label,
                    scenario_count=len(scenario_options),
                    latest_agent_id=latest.agent.id,
                    latest_scenario_id=latest.agent.scenario_id,
                    latest_scenario_name=latest.scenario_name,
                    latest_zone_name=latest.latest_zone_name,
                    latest_mood=latest.latest_mood,
                    available_scenarios=scenario_options,
                )
            )
        return sorted(identities, key=lambda row: (row.name.lower(), row.persona_label.lower()))

    def build_agent_observatory(
        self,
        identity_key: str,
        scenario_id: UUID | None = None,
        tick_from: int | None = None,
        tick_to: int | None = None,
        zone_id: UUID | None = None,
        event_type: str | None = None,
        decision_source: str | None = None,
    ) -> AgentObservatoryRead:
        identities = {row.identity_key: row for row in self.list_agent_identities()}
        selected_identity = identities.get(identity_key)
        if selected_identity is None:
            raise ValueError("Agent identity not found")

        groups = self._identity_groups()
        records = groups.get(identity_key, [])
        if not records:
            raise ValueError("Agent identity not found")

        if scenario_id is not None:
            anchor = next((row for row in records if row.agent.scenario_id == scenario_id), None)
            if anchor is None:
                raise ValueError("Selected scenario is not available for this agent identity")
            mode = "scenario"
            scope_label = f"Scenario: {anchor.scenario_name}"
            scope_notes = None
            metric_records = [anchor]
        else:
            anchor = max(records, key=lambda row: (row.latest_tick, row.agent.created_at))
            mode = "overview"
            scope_label = "All scenarios"
            scope_notes = (
                "Overview mode anchors timelines to the latest scenario instance "
                "while KPI cards aggregate across matching persisted identity records."
            )
            metric_records = records

        return self._build_observatory_payload(
            identity=selected_identity,
            anchor=anchor,
            metric_records=metric_records,
            mode=mode,
            scope_label=scope_label,
            scope_notes=scope_notes,
            scenario_id=scenario_id,
            tick_from=tick_from,
            tick_to=tick_to,
            zone_id=zone_id,
            event_type=event_type,
            decision_source=decision_source,
        )

    def build_agent_snapshot(
        self,
        scenario_id: UUID,
        agent_id: UUID,
        tick_from: int | None = None,
        tick_to: int | None = None,
        zone_id: UUID | None = None,
        event_type: str | None = None,
        decision_source: str | None = None,
    ) -> AgentObservatoryRead:
        agent = self.session.get(Agent, agent_id)
        if agent is None or agent.scenario_id != scenario_id:
            raise ValueError("Agent not found")
        persona = self.session.get(PersonaProfile, agent.persona_profile_id)
        identity_key = self.identity_key(agent.name, persona.label if persona else "persona")
        return self.build_agent_observatory(
            identity_key=identity_key,
            scenario_id=scenario_id,
            tick_from=tick_from,
            tick_to=tick_to,
            zone_id=zone_id,
            event_type=event_type,
            decision_source=decision_source,
        )

    def _identity_groups(self) -> dict[str, list[AgentIdentityRecord]]:
        agents = self.agent_repo.list_all()
        if not agents:
            return {}

        scenario_ids = {agent.scenario_id for agent in agents}
        scenarios = {
            row.id: row
            for row in self.session.exec(select(Scenario).where(Scenario.id.in_(scenario_ids)))
        }
        persona_ids = {agent.persona_profile_id for agent in agents}
        personas = {
            row.id: row
            for row in self.session.exec(select(PersonaProfile).where(PersonaProfile.id.in_(persona_ids)))
        }

        zones_by_scenario: dict[UUID, dict[UUID, str]] = {}
        for scenario_id in scenario_ids:
            zones_by_scenario[scenario_id] = {
                zone.id: zone.name for zone in self.world_repo.list_zones(scenario_id)
            }

        groups: dict[str, list[AgentIdentityRecord]] = defaultdict(list)
        for agent in agents:
            persona = personas.get(agent.persona_profile_id)
            persona_label = persona.label if persona else "persona"
            key = self.identity_key(agent.name, persona_label)
            latest_state = self.agent_repo.latest_state(agent.id)
            zones = zones_by_scenario.get(agent.scenario_id, {})
            groups[key].append(
                AgentIdentityRecord(
                    agent=agent,
                    persona=persona,
                    scenario_name=scenarios.get(agent.scenario_id).name
                    if scenarios.get(agent.scenario_id)
                    else str(agent.scenario_id),
                    latest_zone_name=zones.get(latest_state.zone_id) if latest_state and latest_state.zone_id else None,
                    latest_mood=latest_state.mood if latest_state else "neutral",
                    latest_tick=int(latest_state.tick_number if latest_state else -1),
                )
            )
        return groups

    def _build_observatory_payload(
        self,
        identity: AgentIdentityRead,
        anchor: AgentIdentityRecord,
        metric_records: list[AgentIdentityRecord],
        mode: str,
        scope_label: str,
        scope_notes: str | None,
        scenario_id: UUID | None,
        tick_from: int | None,
        tick_to: int | None,
        zone_id: UUID | None,
        event_type: str | None,
        decision_source: str | None,
    ) -> AgentObservatoryRead:
        anchor_agent = anchor.agent
        scenario_uuid = anchor_agent.scenario_id
        latest_state = self.agent_repo.latest_state(anchor_agent.id)
        zones = {zone.id: zone for zone in self.world_repo.list_zones(scenario_uuid)}
        current_zone = zones.get(latest_state.zone_id) if latest_state and latest_state.zone_id else None
        persona = anchor.persona

        goals = self.planning_repo.list_goals(scenario_uuid, anchor_agent.id)
        intentions = self.planning_repo.list_intentions(scenario_uuid, anchor_agent.id)
        active_goal = self.planning_repo.active_goal(scenario_uuid, anchor_agent.id)
        active_intention = self.planning_repo.active_intention(scenario_uuid, anchor_agent.id)

        messages = self.social_repo.list_messages(
            scenario_id=scenario_uuid,
            agent_id=anchor_agent.id,
            tick_from=tick_from,
            tick_to=tick_to,
        )
        timeline = self.social_repo.list_timeline(
            scenario_id=scenario_uuid,
            tick_from=tick_from,
            tick_to=tick_to,
            agent_id=anchor_agent.id,
            event_type=event_type,
            zone_id=zone_id,
        )
        relationships = self.social_repo.list_relationships(scenario_uuid, agent_id=anchor_agent.id)

        decision_statement = (
            select(DecisionLog)
            .where(DecisionLog.scenario_id == scenario_uuid)
            .where(DecisionLog.agent_id == anchor_agent.id)
            .order_by(DecisionLog.tick_number.desc(), DecisionLog.created_at.desc())
        )
        if tick_from is not None:
            decision_statement = decision_statement.where(DecisionLog.tick_number >= tick_from)
        if tick_to is not None:
            decision_statement = decision_statement.where(DecisionLog.tick_number <= tick_to)
        if decision_source is not None:
            decision_statement = decision_statement.where(DecisionLog.decision_source == decision_source)
        decisions = list(self.session.exec(decision_statement))[:50]

        memory_statement = (
            select(MemoryRetrievalTrace, Memory)
            .join(Memory, Memory.id == MemoryRetrievalTrace.memory_id)
            .where(MemoryRetrievalTrace.agent_id == anchor_agent.id)
            .order_by(MemoryRetrievalTrace.tick_number.desc(), MemoryRetrievalTrace.created_at.desc())
        )
        if tick_from is not None:
            memory_statement = memory_statement.where(MemoryRetrievalTrace.tick_number >= tick_from)
        if tick_to is not None:
            memory_statement = memory_statement.where(MemoryRetrievalTrace.tick_number <= tick_to)
        memory_rows = list(self.session.exec(memory_statement))[:80]

        state_history = self.agent_repo.state_history(
            anchor_agent.id, tick_from=tick_from, tick_to=tick_to, limit=300
        )

        inventory: list[InventoryItemRead] = []
        if latest_state is not None:
            inventory = [
                InventoryItemRead(resource_type=resource_type, quantity=quantity)
                for resource_type, quantity in sorted((latest_state.inventory or {}).items())
            ]

        needs = [
            NeedGaugeRead(
                label="Hunger",
                value=float(latest_state.hunger if latest_state else 0.0),
                severity=_severity(float(latest_state.hunger if latest_state else 0.0)),
            ),
            NeedGaugeRead(
                label="Safety",
                value=float(latest_state.safety_need if latest_state else 0.0),
                severity=_severity(float(latest_state.safety_need if latest_state else 0.0)),
            ),
            NeedGaugeRead(
                label="Social",
                value=float(latest_state.social_need if latest_state else 0.0),
                severity=_severity(float(latest_state.social_need if latest_state else 0.0)),
            ),
        ]
        needs_history = [
            NeedHistoryPointRead(
                tick_number=state.tick_number,
                hunger=float(state.hunger),
                safety_need=float(state.safety_need),
                social_need=float(state.social_need),
            )
            for state in state_history
        ]

        id_to_name = {str(row.id): row.name for row in self.agent_repo.list_by_scenario(scenario_uuid)}
        relationship_items = [
            RelationshipSummaryRead(
                target_agent_id=relationship.target_agent_id,
                target_agent_name=id_to_name.get(str(relationship.target_agent_id), "unknown"),
                trust=relationship.trust,
                affinity=relationship.affinity,
                stance=relationship.stance,
                influence=relationship.influence,
                last_updated_tick=relationship.last_updated_tick,
            )
            for relationship in relationships[:12]
        ]

        metrics = self._build_interaction_metrics(
            anchor_agent_id=anchor_agent.id,
            anchor_goals=goals,
            anchor_messages=messages,
            anchor_timeline=timeline,
            metric_records=metric_records,
            tick_from=tick_from,
            tick_to=tick_to,
            zone_id=zone_id,
            event_type=event_type,
            decision_source=decision_source,
            mode=mode,
        )

        plan_history = self._build_plan_history(timeline)
        action_mix = self._build_action_mix(decisions)
        memory_summary, memory_influence_trend = self._build_memory_summaries(memory_rows)
        behavioral_trends = self._build_behavioral_trends(
            decisions=decisions,
            timeline=timeline,
            state_history=state_history,
        )

        recent_decisions = decisions[:20]
        recent_memory_rows = memory_rows[:20]

        return AgentObservatoryRead(
            scenario_id=scenario_uuid,
            mode=mode,
            scope_label=scope_label,
            scope_notes=scope_notes,
            selected_scenario_id=scenario_id,
            available_scenarios=identity.available_scenarios,
            agent=AgentSummaryRead(
                id=anchor_agent.id,
                name=anchor_agent.name,
                persona_label=persona.label if persona else "persona",
                communication_style=persona.communication_style if persona else "neutral",
                cooperation_tendency=float(persona.cooperation_tendency if persona else 0.0),
                risk_tolerance=float(persona.risk_tolerance if persona else 0.0),
                memory_sensitivity=float(persona.memory_sensitivity if persona else 0.0),
                emotional_bias=float(persona.emotional_bias if persona else 0.0),
                zone_id=latest_state.zone_id if latest_state else None,
                zone_name=current_zone.name if current_zone else None,
                mood=latest_state.mood if latest_state else "neutral",
                inventory=inventory,
            ),
            needs=needs,
            needs_history=needs_history,
            active_goal=(
                GoalSummaryRead(
                    id=active_goal.id,
                    goal_type=active_goal.goal_type,
                    priority=active_goal.priority,
                    status=active_goal.status,
                    source=active_goal.source,
                    target=active_goal.target,
                    updated_at=active_goal.updated_at,
                )
                if active_goal
                else None
            ),
            active_intention=(
                IntentionSummaryRead(
                    id=active_intention.id,
                    current_action_type=active_intention.current_action_type,
                    status=active_intention.status,
                    rationale=active_intention.rationale,
                    target_zone_id=active_intention.target_zone_id,
                    target_resource_id=active_intention.target_resource_id,
                    is_interruptible=active_intention.is_interruptible,
                    updated_at=active_intention.updated_at,
                )
                if active_intention
                else None
            ),
            recent_goals=[
                GoalSummaryRead(
                    id=goal.id,
                    goal_type=goal.goal_type,
                    priority=goal.priority,
                    status=goal.status,
                    source=goal.source,
                    target=goal.target,
                    updated_at=goal.updated_at,
                )
                for goal in goals[:8]
            ],
            recent_intentions=[
                IntentionSummaryRead(
                    id=intention.id,
                    current_action_type=intention.current_action_type,
                    status=intention.status,
                    rationale=intention.rationale,
                    target_zone_id=intention.target_zone_id,
                    target_resource_id=intention.target_resource_id,
                    is_interruptible=intention.is_interruptible,
                    updated_at=intention.updated_at,
                )
                for intention in intentions[:8]
            ],
            plan_history=plan_history,
            decisions=[
                DecisionTraceRead(
                    id=decision.id,
                    tick_number=decision.tick_number,
                    selected_action=decision.selected_action,
                    rationale=decision.rationale,
                    confidence=decision.confidence,
                    persona_factors=decision.persona_factors,
                    relationship_factors=decision.relationship_factors,
                    world_event_factors=decision.world_event_factors,
                    decision_source=decision.decision_source,
                    parser_status=decision.parser_status,
                    fallback_reason=decision.fallback_reason,
                    llm_metadata=decision.llm_metadata,
                    message_id=decision.message_id,
                    created_at=decision.created_at,
                )
                for decision in recent_decisions
            ],
            action_mix=action_mix,
            memory_influences=[
                MemoryInfluenceRead(
                    trace_id=trace.id,
                    decision_log_id=trace.decision_log_id,
                    memory_id=memory.id,
                    tick_number=trace.tick_number,
                    relevance_score=trace.relevance_score,
                    memory_type=memory.memory_type,
                    content=memory.content,
                    salience=memory.salience,
                    valence=memory.valence,
                    created_at=trace.created_at,
                )
                for trace, memory in recent_memory_rows
            ],
            memory_summary=memory_summary,
            memory_influence_trend=memory_influence_trend,
            relationships=relationship_items,
            interaction_metrics=metrics,
            behavioral_trends=behavioral_trends,
            recent_events=[
                {
                    "id": str(event.id),
                    "tick_number": event.tick_number,
                    "event_type": event.event_type,
                    "content": event.content,
                    "payload": event.payload,
                    "created_at": event.created_at.isoformat(),
                }
                for event in timeline[:25]
            ],
        )

    def _build_interaction_metrics(
        self,
        anchor_agent_id: UUID,
        anchor_goals: list,
        anchor_messages: list,
        anchor_timeline: list,
        metric_records: list[AgentIdentityRecord],
        tick_from: int | None,
        tick_to: int | None,
        zone_id: UUID | None,
        event_type: str | None,
        decision_source: str | None,
        mode: str,
    ) -> InteractionMetricsRead:
        if mode == "scenario":
            metrics_base = interaction_metrics(anchor_messages, anchor_timeline, str(anchor_agent_id))
            all_statuses = [goal.status for goal in anchor_goals]
            completed_goals = sum(1 for goal in anchor_goals if goal.status == "completed")
            decision_rows = list(
                self.session.exec(
                    select(DecisionLog)
                    .where(DecisionLog.scenario_id == metric_records[0].agent.scenario_id)
                    .where(DecisionLog.agent_id == anchor_agent_id)
                )
            )
        else:
            metrics_base = {
                "messages_sent": 0,
                "messages_received": 0,
                "cooperation_events": 0,
                "conflict_events": 0,
                "interruption_count": 0,
            }
            all_statuses: list[str] = []
            completed_goals = 0
            decision_rows = []
            for record in metric_records:
                scenario_messages = self.social_repo.list_messages(
                    scenario_id=record.agent.scenario_id,
                    agent_id=record.agent.id,
                    tick_from=tick_from,
                    tick_to=tick_to,
                )
                scenario_timeline = self.social_repo.list_timeline(
                    scenario_id=record.agent.scenario_id,
                    tick_from=tick_from,
                    tick_to=tick_to,
                    agent_id=record.agent.id,
                    event_type=event_type,
                    zone_id=zone_id,
                )
                values = interaction_metrics(scenario_messages, scenario_timeline, str(record.agent.id))
                for key in metrics_base:
                    metrics_base[key] += int(values[key])
                scenario_goals = self.planning_repo.list_goals(record.agent.scenario_id, record.agent.id)
                all_statuses.extend(goal.status for goal in scenario_goals)
                completed_goals += sum(1 for goal in scenario_goals if goal.status == "completed")
                scenario_decisions = list(
                    self.session.exec(
                        select(DecisionLog)
                        .where(DecisionLog.scenario_id == record.agent.scenario_id)
                        .where(DecisionLog.agent_id == record.agent.id)
                    )
                )
                decision_rows.extend(scenario_decisions)

        if tick_from is not None:
            decision_rows = [row for row in decision_rows if row.tick_number >= tick_from]
        if tick_to is not None:
            decision_rows = [row for row in decision_rows if row.tick_number <= tick_to]

        if decision_source is not None:
            decision_rows = [row for row in decision_rows if row.decision_source == decision_source]
        llm_decision_count = sum(1 for row in decision_rows if row.decision_source == "llm")
        deterministic_decision_count = sum(
            1 for row in decision_rows if row.decision_source == "deterministic"
        )
        fallback_count = sum(
            1
            for row in decision_rows
            if row.decision_source == "fallback_deterministic" or bool(row.fallback_reason)
        )

        return InteractionMetricsRead(
            messages_sent=metrics_base["messages_sent"],
            messages_received=metrics_base["messages_received"],
            cooperation_events=metrics_base["cooperation_events"],
            conflict_events=metrics_base["conflict_events"],
            interruption_count=metrics_base["interruption_count"],
            completed_goals=completed_goals,
            goal_completion_rate=goal_completion_rate(all_statuses),
            fallback_count=fallback_count,
            llm_decision_count=llm_decision_count,
            deterministic_decision_count=deterministic_decision_count,
        )

    @staticmethod
    def _build_plan_history(timeline: list) -> list[PlanHistoryPointRead]:
        rows: list[PlanHistoryPointRead] = []
        for event in timeline:
            if event.event_type not in {"plan_change", "interruption", "decision"}:
                continue
            payload = event.payload or {}
            rows.append(
                PlanHistoryPointRead(
                    tick_number=event.tick_number,
                    event_type=event.event_type,
                    summary=event.content or str(payload.get("reason", "")),
                    status=payload.get("status") or payload.get("to_status"),
                    action_type=payload.get("action") or payload.get("current_action_type"),
                )
            )
        return rows[:30]

    @staticmethod
    def _build_action_mix(decisions: list[DecisionLog]) -> list[ActionMixItemRead]:
        counter = Counter(decision.selected_action for decision in decisions)
        return [
            ActionMixItemRead(action=action, count=count)
            for action, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
        ]

    @staticmethod
    def _build_memory_summaries(
        memory_rows: list[tuple[MemoryRetrievalTrace, Memory]],
    ) -> tuple[list[MemorySummaryRead], list[MemoryInfluenceTrendPointRead]]:
        top_rows = sorted(
            memory_rows,
            key=lambda pair: (pair[0].relevance_score, pair[0].tick_number),
            reverse=True,
        )[:12]
        summaries = [
            MemorySummaryRead(
                memory_id=memory.id,
                tick_number=trace.tick_number,
                memory_type=memory.memory_type,
                content=memory.content,
                relevance_score=trace.relevance_score,
                salience=memory.salience,
            )
            for trace, memory in top_rows
        ]

        relevance_by_tick: dict[int, list[float]] = defaultdict(list)
        for trace, _memory in memory_rows:
            relevance_by_tick[trace.tick_number].append(float(trace.relevance_score))
        trend = [
            MemoryInfluenceTrendPointRead(
                tick_number=tick,
                count=len(values),
                avg_relevance=(sum(values) / len(values)) if values else 0.0,
            )
            for tick, values in sorted(relevance_by_tick.items())
        ]
        return summaries, trend

    @staticmethod
    def _build_behavioral_trends(
        decisions: list[DecisionLog],
        timeline: list,
        state_history: list,
    ) -> list[BehavioralTrendPointRead]:
        rows: dict[int, BehavioralTrendPointRead] = {}
        action_sets: dict[int, set[str]] = defaultdict(set)

        def point_for_tick(tick: int) -> BehavioralTrendPointRead:
            if tick not in rows:
                rows[tick] = BehavioralTrendPointRead(tick_number=tick)
            return rows[tick]

        for decision in decisions:
            point = point_for_tick(decision.tick_number)
            point.action_count += 1
            action_sets[decision.tick_number].add(decision.selected_action)

        for event in timeline:
            point = point_for_tick(event.tick_number)
            if event.event_type == "interruption":
                point.interruption_count += 1
            if event.event_type == "move":
                point.move_count += 1
            if event.event_type in {"plan_change", "goal_completed"}:
                payload = event.payload or {}
                if payload.get("to_status") == "completed" or payload.get("status") == "completed":
                    point.goal_completion_count += 1

        previous_zone = None
        for state in state_history:
            point = point_for_tick(state.tick_number)
            if previous_zone is not None and state.zone_id != previous_zone:
                point.zone_transition_count += 1
            previous_zone = state.zone_id

        for tick, actions in action_sets.items():
            point_for_tick(tick).distinct_action_count = len(actions)

        return [rows[tick] for tick in sorted(rows.keys())]
