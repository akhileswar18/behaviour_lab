from __future__ import annotations

import logging
from datetime import datetime
from dataclasses import dataclass
from uuid import UUID

from sqlmodel import Session, select

from app.api.schemas.world import build_world_snapshot
from app.persistence.models import (
    Agent,
    AgentStateSnapshot,
    DecisionLog,
    Memory,
    MemoryRetrievalTrace,
    Message,
    Relationship,
    ScenarioEventInjection,
    SimulationEvent,
    TickResult,
    RunMetadata,
)
from app.persistence.repositories.run_repository import RunRepository
from app.schemas.decision_engine import LlmConfig, PolicyMode
from app.schemas.social import SimulationEventType
from app.simulation.tick_engine import run_tick
from app.ws.broadcaster import world_broadcaster

logger = logging.getLogger(__name__)


@dataclass
class RunSummary:
    policy_mode: str
    fallback_count: int
    llm_decision_count: int
    deterministic_decision_count: int
    run_metadata_id: UUID | None = None


class SimulationRunner:
    def __init__(self, session: Session):
        self.session = session
        self.last_run_summary = RunSummary(
            policy_mode=PolicyMode.DETERMINISTIC.value,
            fallback_count=0,
            llm_decision_count=0,
            deterministic_decision_count=0,
        )

    def run(
        self,
        scenario_id: UUID,
        ticks: int,
        policy_mode: PolicyMode = PolicyMode.DETERMINISTIC,
        llm_config: LlmConfig | None = None,
        source_scenario_id: UUID | None = None,
        run_kind: str = "baseline",
        variant_name: str = "baseline",
        persona_overrides: dict | None = None,
        planning_overrides: dict | None = None,
        world_overrides: dict | None = None,
    ) -> list[TickResult]:
        run_repo = RunRepository(self.session)
        existing = list(
            self.session.exec(
                select(TickResult)
                .where(TickResult.scenario_id == scenario_id)
                .order_by(TickResult.tick_number.desc())
            )
        )
        start_tick = (existing[0].tick_number + 1) if existing else 1
        effective_llm = llm_config or LlmConfig()

        run_row = run_repo.create(
            RunMetadata(
                scenario_id=scenario_id,
                source_scenario_id=source_scenario_id,
                run_kind=run_kind,
                variant_name=variant_name,
                persona_overrides=persona_overrides or {},
                planning_overrides=planning_overrides or {},
                world_overrides=world_overrides or {},
                ticks_requested=ticks,
                policy_mode=policy_mode.value,
                llm_provider=effective_llm.provider,
                llm_model=effective_llm.model,
                llm_config_summary={
                    "provider": effective_llm.provider,
                    "model": effective_llm.model,
                    "endpoint": effective_llm.endpoint,
                    "timeout_seconds": effective_llm.timeout_seconds,
                    "temperature": effective_llm.temperature,
                    "max_tokens": effective_llm.max_tokens,
                },
                started_at=datetime.utcnow(),
            )
        )

        self.session.add(
            SimulationEvent(
                scenario_id=scenario_id,
                tick_number=start_tick,
                event_type=SimulationEventType.SYSTEM.value,
                content=f"run_started:{ticks}_ticks",
                payload={
                    "label": "simulation_run_started",
                    "phase": "phase4_hybrid_decision",
                    "start_tick": start_tick,
                    "ticks_requested": ticks,
                    "policy_mode": policy_mode.value,
                    "run_metadata_id": str(run_row.id),
                },
                created_at=datetime.utcnow(),
            )
        )
        self.session.commit()
        logger.info(
            "simulation_run_started scenario_id=%s start_tick=%s ticks_requested=%s",
            scenario_id,
            start_tick,
            ticks,
        )

        results: list[TickResult] = []
        for tick in range(start_tick, start_tick + ticks):
            tick_result = run_tick(
                self.session,
                scenario_id,
                tick,
                policy_mode=policy_mode,
                llm_config=effective_llm,
            )
            results.append(tick_result)
            world_broadcaster.publish_snapshot(build_world_snapshot(self.session, scenario_id, tick))

        end_tick = results[-1].tick_number if results else start_tick
        events_created = sum(result.events_created for result in results)
        messages_created = sum(result.messages_created for result in results)

        source_counts, fallback_count = run_repo.summarize_decision_sources(
            scenario_id=scenario_id,
            tick_from=start_tick,
            tick_to=end_tick,
        )
        llm_decisions = int(source_counts.get("llm", 0))
        deterministic_decisions = int(source_counts.get("deterministic", 0))

        run_row.ended_at = datetime.utcnow()
        run_row.decision_source_counts = source_counts
        run_row.fallback_count = fallback_count
        run_row.parse_failure_count = fallback_count
        run_repo.save(run_row)
        self.session.add(
            SimulationEvent(
                scenario_id=scenario_id,
                tick_number=end_tick,
                event_type=SimulationEventType.SYSTEM.value,
                content="run_completed",
                payload={
                    "label": "simulation_run_completed",
                    "phase": "phase4_hybrid_decision",
                    "start_tick": start_tick,
                    "end_tick": end_tick,
                    "ticks_processed": len(results),
                    "events_created": events_created,
                    "messages_created": messages_created,
                    "policy_mode": policy_mode.value,
                    "decision_source_counts": source_counts,
                    "fallback_count": fallback_count,
                    "run_metadata_id": str(run_row.id),
                },
                created_at=datetime.utcnow(),
            )
        )
        self.session.commit()
        logger.info(
            "simulation_run_completed scenario_id=%s start_tick=%s end_tick=%s ticks_processed=%s events_created=%s messages_created=%s",
            scenario_id,
            start_tick,
            end_tick,
            len(results),
            events_created,
            messages_created,
        )
        self.last_run_summary = RunSummary(
            policy_mode=policy_mode.value,
            fallback_count=fallback_count,
            llm_decision_count=llm_decisions,
            deterministic_decision_count=deterministic_decisions,
            run_metadata_id=run_row.id,
        )
        return results

    def reset(self, scenario_id: UUID) -> None:
        self.session.add(
            SimulationEvent(
                scenario_id=scenario_id,
                tick_number=0,
                event_type=SimulationEventType.SYSTEM.value,
                content="reset_requested",
                payload={"label": "scenario_reset_requested", "phase": "phase3_goal_resource"},
                created_at=datetime.utcnow(),
            )
        )
        self.session.commit()
        logger.info("scenario_reset_started scenario_id=%s", scenario_id)
        models = [
            TickResult,
            DecisionLog,
            SimulationEvent,
            Message,
            Relationship,
            ScenarioEventInjection,
        ]
        for model in models:
            rows = list(self.session.exec(select(model).where(model.scenario_id == scenario_id)))
            for row in rows:
                self.session.delete(row)

        agents = list(self.session.exec(select(Agent).where(Agent.scenario_id == scenario_id)))
        agent_ids = [a.id for a in agents]
        for model in [Memory, AgentStateSnapshot, MemoryRetrievalTrace]:
            for agent_id in agent_ids:
                rows = list(self.session.exec(select(model).where(model.agent_id == agent_id)))
                for row in rows:
                    self.session.delete(row)

        self.session.commit()
        self.session.add(
            SimulationEvent(
                scenario_id=scenario_id,
                tick_number=0,
                event_type=SimulationEventType.SYSTEM.value,
                content="reset_completed",
                payload={"label": "scenario_reset_completed", "phase": "phase3_goal_resource"},
                created_at=datetime.utcnow(),
            )
        )
        self.session.commit()
        logger.info("scenario_reset_completed scenario_id=%s", scenario_id)
