from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import Relationship
from app.persistence.repositories.base import RepositoryBase


class RelationshipRepository(RepositoryBase[Relationship]):
    def __init__(self, session: Session):
        super().__init__(session)

    def list_by_scenario(self, scenario_id: UUID) -> list[Relationship]:
        statement = select(Relationship).where(Relationship.scenario_id == scenario_id)
        return list(self.session.exec(statement))
