from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import Memory
from app.persistence.repositories.base import RepositoryBase


class MemoryRepository(RepositoryBase[Memory]):
    def __init__(self, session: Session):
        super().__init__(session)

    def add_memory(self, memory: Memory) -> Memory:
        return self.add(memory)

    def list_for_agent(self, agent_id: UUID) -> list[Memory]:
        statement = select(Memory).where(Memory.agent_id == agent_id).order_by(Memory.created_at.desc())
        return list(self.session.exec(statement))
