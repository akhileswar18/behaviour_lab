from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import Message, SimulationEvent
from app.persistence.repositories.base import RepositoryBase


class EventRepository(RepositoryBase[SimulationEvent]):
    def __init__(self, session: Session):
        super().__init__(session)

    def add_event(self, event: SimulationEvent) -> SimulationEvent:
        return self.add(event)

    def list_timeline(self, scenario_id: UUID, tick_from: int | None = None, tick_to: int | None = None, agent_id: UUID | None = None) -> list[SimulationEvent]:
        statement = select(SimulationEvent).where(SimulationEvent.scenario_id == scenario_id)
        if tick_from is not None:
            statement = statement.where(SimulationEvent.tick_number >= tick_from)
        if tick_to is not None:
            statement = statement.where(SimulationEvent.tick_number <= tick_to)
        if agent_id is not None:
            statement = statement.where((SimulationEvent.actor_agent_id == agent_id) | (SimulationEvent.target_agent_id == agent_id))
        statement = statement.order_by(SimulationEvent.tick_number, SimulationEvent.created_at)
        return list(self.session.exec(statement))

    def add_message(self, message: Message) -> Message:
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def list_messages(self, scenario_id: UUID) -> list[Message]:
        statement = select(Message).where(Message.scenario_id == scenario_id).order_by(Message.tick_number, Message.created_at)
        return list(self.session.exec(statement))

    def list_messages_for_agent(self, scenario_id: UUID, agent_id: UUID) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.scenario_id == scenario_id)
            .where((Message.sender_agent_id == agent_id) | (Message.receiver_agent_id == agent_id))
            .order_by(Message.tick_number, Message.created_at)
        )
        return list(self.session.exec(statement))
