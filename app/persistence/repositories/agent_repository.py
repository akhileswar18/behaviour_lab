from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import Agent, AgentStateSnapshot
from app.persistence.repositories.base import RepositoryBase


class AgentRepository(RepositoryBase[Agent]):
    def __init__(self, session: Session):
        super().__init__(session)

    def list_by_scenario(self, scenario_id: UUID) -> list[Agent]:
        statement = select(Agent).where(Agent.scenario_id == scenario_id)
        return list(self.session.exec(statement))

    def list_all(self) -> list[Agent]:
        statement = select(Agent).order_by(Agent.name, Agent.created_at)
        return list(self.session.exec(statement))

    def latest_state(self, agent_id: UUID) -> AgentStateSnapshot | None:
        statement = (
            select(AgentStateSnapshot)
            .where(AgentStateSnapshot.agent_id == agent_id)
            .order_by(AgentStateSnapshot.tick_number.desc())
        )
        return self.session.exec(statement).first()

    def state_history(
        self,
        agent_id: UUID,
        tick_from: int | None = None,
        tick_to: int | None = None,
        limit: int = 250,
    ) -> list[AgentStateSnapshot]:
        statement = (
            select(AgentStateSnapshot)
            .where(AgentStateSnapshot.agent_id == agent_id)
            .order_by(AgentStateSnapshot.tick_number.asc(), AgentStateSnapshot.created_at.asc())
        )
        if tick_from is not None:
            statement = statement.where(AgentStateSnapshot.tick_number >= tick_from)
        if tick_to is not None:
            statement = statement.where(AgentStateSnapshot.tick_number <= tick_to)
        rows = list(self.session.exec(statement))
        if len(rows) <= limit:
            return rows
        return rows[-limit:]
