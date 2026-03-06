from __future__ import annotations

from uuid import UUID

from sqlmodel import Session, select

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
)
from app.simulation.tick_engine import run_tick


class SimulationRunner:
    def __init__(self, session: Session):
        self.session = session

    def run(self, scenario_id: UUID, ticks: int) -> list[TickResult]:
        existing = list(
            self.session.exec(
                select(TickResult)
                .where(TickResult.scenario_id == scenario_id)
                .order_by(TickResult.tick_number.desc())
            )
        )
        start_tick = (existing[0].tick_number + 1) if existing else 1

        results: list[TickResult] = []
        for tick in range(start_tick, start_tick + ticks):
            results.append(run_tick(self.session, scenario_id, tick))
        return results

    def reset(self, scenario_id: UUID) -> None:
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
