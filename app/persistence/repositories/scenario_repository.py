from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import Scenario
from app.persistence.repositories.base import RepositoryBase


class ScenarioRepository(RepositoryBase[Scenario]):
    def __init__(self, session: Session):
        super().__init__(session)

    def list_scenarios(self) -> list[Scenario]:
        statement = select(Scenario).order_by(Scenario.created_at.desc())
        return list(self.session.exec(statement))

    def create_scenario(self, scenario: Scenario) -> Scenario:
        return self.add(scenario)

    def get(self, scenario_id: UUID) -> Scenario | None:
        return self.get_optional(Scenario, scenario_id)

    def update_status(self, scenario_id: UUID, status: str) -> Scenario | None:
        scenario = self.get(scenario_id)
        if not scenario:
            return None
        scenario.status = status
        self.session.add(scenario)
        self.session.commit()
        self.session.refresh(scenario)
        return scenario
