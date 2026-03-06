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

    def latest_state(self, agent_id: UUID) -> AgentStateSnapshot | None:
        statement = (
            select(AgentStateSnapshot)
            .where(AgentStateSnapshot.agent_id == agent_id)
            .order_by(AgentStateSnapshot.tick_number.desc())
        )
        return self.session.exec(statement).first()
