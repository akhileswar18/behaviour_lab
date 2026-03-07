from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import Message, Relationship, ScenarioEventInjection, SimulationEvent


class SocialRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_message(self, message: Message) -> Message:
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def list_messages(
        self,
        scenario_id: UUID,
        agent_id: UUID | None = None,
        tick_from: int | None = None,
        tick_to: int | None = None,
        intent: str | None = None,
    ) -> list[Message]:
        statement = select(Message).where(Message.scenario_id == scenario_id)
        if agent_id is not None:
            statement = statement.where(
                (Message.sender_agent_id == agent_id) | (Message.receiver_agent_id == agent_id)
            )
        if tick_from is not None:
            statement = statement.where(Message.tick_number >= tick_from)
        if tick_to is not None:
            statement = statement.where(Message.tick_number <= tick_to)
        if intent is not None:
            statement = statement.where(Message.intent == intent)
        statement = statement.order_by(Message.tick_number, Message.created_at)
        return list(self.session.exec(statement))

    def add_event(self, event: SimulationEvent) -> SimulationEvent:
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def list_timeline(
        self,
        scenario_id: UUID,
        tick_from: int | None = None,
        tick_to: int | None = None,
        agent_id: UUID | None = None,
        event_type: str | None = None,
        zone_id: UUID | None = None,
    ) -> list[SimulationEvent]:
        statement = select(SimulationEvent).where(SimulationEvent.scenario_id == scenario_id)
        if tick_from is not None:
            statement = statement.where(SimulationEvent.tick_number >= tick_from)
        if tick_to is not None:
            statement = statement.where(SimulationEvent.tick_number <= tick_to)
        if agent_id is not None:
            statement = statement.where(
                (SimulationEvent.actor_agent_id == agent_id)
                | (SimulationEvent.target_agent_id == agent_id)
            )
        if event_type is not None:
            statement = statement.where(SimulationEvent.event_type == event_type)
        statement = statement.order_by(SimulationEvent.tick_number, SimulationEvent.created_at)
        rows = list(self.session.exec(statement))
        if zone_id is not None:
            rows = [row for row in rows if str(row.payload.get("zone_id", "")) == str(zone_id)]
        return rows

    def list_agent_events(
        self,
        scenario_id: UUID,
        agent_id: UUID,
        tick_from: int | None = None,
        tick_to: int | None = None,
        limit: int = 20,
    ) -> list[SimulationEvent]:
        rows = self.list_timeline(
            scenario_id=scenario_id,
            tick_from=tick_from,
            tick_to=tick_to,
            agent_id=agent_id,
        )
        return rows[:limit]

    def get_relationship(
        self, scenario_id: UUID, source_agent_id: UUID, target_agent_id: UUID
    ) -> Relationship | None:
        statement = (
            select(Relationship)
            .where(Relationship.scenario_id == scenario_id)
            .where(Relationship.source_agent_id == source_agent_id)
            .where(Relationship.target_agent_id == target_agent_id)
        )
        return self.session.exec(statement).first()

    def upsert_relationship(
        self,
        scenario_id: UUID,
        source_agent_id: UUID,
        target_agent_id: UUID,
        trust_delta: float,
        affinity_delta: float,
        stance: str,
        tick_number: int,
    ) -> Relationship:
        relationship = self.get_relationship(scenario_id, source_agent_id, target_agent_id)
        if relationship is None:
            relationship = Relationship(
                scenario_id=scenario_id,
                source_agent_id=source_agent_id,
                target_agent_id=target_agent_id,
                trust=max(-1.0, min(1.0, trust_delta)),
                affinity=max(-1.0, min(1.0, affinity_delta)),
                stance=stance,
                influence=0.5,
                last_updated_tick=tick_number,
                last_interaction_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        else:
            relationship.trust = max(-1.0, min(1.0, relationship.trust + trust_delta))
            relationship.affinity = max(-1.0, min(1.0, relationship.affinity + affinity_delta))
            relationship.stance = stance
            relationship.last_updated_tick = tick_number
            relationship.last_interaction_at = datetime.utcnow()
            relationship.updated_at = datetime.utcnow()
        self.session.add(relationship)
        self.session.commit()
        self.session.refresh(relationship)
        return relationship

    def list_relationships(self, scenario_id: UUID, agent_id: UUID | None = None) -> list[Relationship]:
        statement = select(Relationship).where(Relationship.scenario_id == scenario_id)
        if agent_id is not None:
            statement = statement.where(
                (Relationship.source_agent_id == agent_id)
                | (Relationship.target_agent_id == agent_id)
            )
        statement = statement.order_by(Relationship.updated_at.desc())
        return list(self.session.exec(statement))

    def add_world_event(
        self, scenario_id: UUID, tick_number: int, event_key: str, content: str, payload: dict
    ) -> ScenarioEventInjection:
        row = ScenarioEventInjection(
            scenario_id=scenario_id,
            tick_number=tick_number,
            event_key=event_key,
            event_content=content,
            payload=payload,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def scheduled_world_events(
        self, scenario_id: UUID, tick_number: int
    ) -> list[ScenarioEventInjection]:
        statement = (
            select(ScenarioEventInjection)
            .where(ScenarioEventInjection.scenario_id == scenario_id)
            .where(ScenarioEventInjection.tick_number == tick_number)
            .where(ScenarioEventInjection.is_consumed.is_(False))
            .order_by(ScenarioEventInjection.created_at)
        )
        return list(self.session.exec(statement))

    def mark_world_event_consumed(self, event_id: UUID) -> None:
        event = self.session.get(ScenarioEventInjection, event_id)
        if event is None:
            return
        event.is_consumed = True
        self.session.add(event)
        self.session.commit()
