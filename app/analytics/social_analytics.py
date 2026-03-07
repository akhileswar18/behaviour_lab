from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from sqlmodel import Session, select

from app.api.schemas.analytics import (
    AgentInteractionMetricRead,
    CausalChainRead,
    RelationshipHistoryRead,
    SocialAnalyticsRead,
    SocialEdgeRead,
)
from app.persistence.models import Agent, Memory, Message, SimulationEvent
from app.persistence.repositories.social_repository import SocialRepository

COOPERATIVE_INTENTS = {"cooperate", "propose"}
CONFLICT_INTENTS = {"warn", "avoid"}


def interaction_metrics(messages: list[Message], events: list[SimulationEvent], agent_id: str) -> dict[str, int]:
    messages_sent = sum(1 for message in messages if str(message.sender_agent_id) == agent_id)
    messages_received = sum(1 for message in messages if str(message.receiver_agent_id) == agent_id)
    cooperation_events = sum(
        1
        for message in messages
        if (str(message.sender_agent_id) == agent_id or str(message.receiver_agent_id) == agent_id)
        and message.intent in COOPERATIVE_INTENTS
    )
    conflict_events = sum(
        1
        for message in messages
        if (str(message.sender_agent_id) == agent_id or str(message.receiver_agent_id) == agent_id)
        and message.intent in CONFLICT_INTENTS
    )
    interruption_count = sum(
        1
        for event in events
        if event.event_type == "interruption" and str(event.actor_agent_id) == agent_id
    )
    return {
        "messages_sent": messages_sent,
        "messages_received": messages_received,
        "cooperation_events": cooperation_events,
        "conflict_events": conflict_events,
        "interruption_count": interruption_count,
    }


class SocialAnalyticsService:
    def __init__(self, session: Session):
        self.session = session
        self.social_repo = SocialRepository(session)

    def build_snapshot(
        self,
        scenario_id: UUID,
        tick_from: int | None = None,
        tick_to: int | None = None,
        agent_id: UUID | None = None,
        zone_id: UUID | None = None,
        event_type: str | None = None,
    ) -> SocialAnalyticsRead:
        agents = list(self.session.exec(select(Agent).where(Agent.scenario_id == scenario_id)))
        id_to_name = {str(agent.id): agent.name for agent in agents}

        messages = self.social_repo.list_messages(
            scenario_id=scenario_id,
            agent_id=agent_id,
            tick_from=tick_from,
            tick_to=tick_to,
        )
        relationships = self.social_repo.list_relationships(scenario_id, agent_id=agent_id)
        timeline = self.social_repo.list_timeline(
            scenario_id=scenario_id,
            tick_from=tick_from,
            tick_to=tick_to,
            agent_id=agent_id,
            event_type=event_type,
            zone_id=zone_id,
        )

        relationship_updates = [event for event in timeline if event.event_type == "relationship_update"]
        message_events = [event for event in timeline if event.event_type == "message"]
        memory_rows = list(
            self.session.exec(
                select(Memory).where(Memory.source_event_id.in_([event.id for event in message_events] if message_events else [UUID(int=0)]))
            )
        ) if message_events else []
        memories_by_source: dict[str, list[Memory]] = defaultdict(list)
        for memory in memory_rows:
            if memory.source_event_id is not None:
                memories_by_source[str(memory.source_event_id)].append(memory)

        relationship_by_message: dict[str, SimulationEvent] = {}
        for event in relationship_updates:
            message_id = str((event.payload or {}).get("message_id", ""))
            if message_id:
                relationship_by_message[message_id] = event

        communication_feed = [
            {
                "id": str(message.id),
                "tick_number": message.tick_number,
                "sender_agent_id": str(message.sender_agent_id),
                "receiver_agent_id": str(message.receiver_agent_id) if message.receiver_agent_id else None,
                "sender_agent_name": id_to_name.get(str(message.sender_agent_id), "unknown"),
                "receiver_agent_name": id_to_name.get(str(message.receiver_agent_id), "broadcast") if message.receiver_agent_id else "broadcast",
                "intent": message.intent,
                "emotional_tone": message.emotional_tone,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            }
            for message in messages
        ]

        interaction_rows: list[AgentInteractionMetricRead] = []
        for agent in agents:
            if agent_id is not None and agent.id != agent_id:
                continue
            metrics = interaction_metrics(messages, timeline, str(agent.id))
            interaction_rows.append(
                AgentInteractionMetricRead(
                    agent_id=agent.id,
                    agent_name=agent.name,
                    messages_sent=metrics["messages_sent"],
                    messages_received=metrics["messages_received"],
                    cooperation_events=metrics["cooperation_events"],
                    conflict_events=metrics["conflict_events"],
                    relationship_updates=sum(
                        1
                        for event in relationship_updates
                        if event.actor_agent_id == agent.id or event.target_agent_id == agent.id
                    ),
                )
            )

        relationship_graph = [
            SocialEdgeRead(
                source_agent_id=relationship.source_agent_id,
                target_agent_id=relationship.target_agent_id,
                source_agent_name=id_to_name.get(str(relationship.source_agent_id), "unknown"),
                target_agent_name=id_to_name.get(str(relationship.target_agent_id), "unknown"),
                trust=relationship.trust,
                affinity=relationship.affinity,
                stance=relationship.stance,
                influence=relationship.influence,
                last_updated_tick=relationship.last_updated_tick,
            )
            for relationship in relationships
        ]

        relationship_history = [
            RelationshipHistoryRead(
                event_id=event.id,
                tick_number=event.tick_number,
                source_agent_id=event.actor_agent_id,
                target_agent_id=event.target_agent_id,
                source_agent_name=id_to_name.get(str(event.actor_agent_id), None) if event.actor_agent_id else None,
                target_agent_name=id_to_name.get(str(event.target_agent_id), None) if event.target_agent_id else None,
                trust_before=(event.payload or {}).get("trust_before"),
                trust_after=(event.payload or {}).get("trust_after"),
                affinity_before=(event.payload or {}).get("affinity_before"),
                affinity_after=(event.payload or {}).get("affinity_after"),
                stance=(event.payload or {}).get("stance"),
                content=event.content,
            )
            for event in relationship_updates[:20]
        ]

        causal_chains: list[CausalChainRead] = []
        for message_event in message_events[:20]:
            message_id = (message_event.payload or {}).get("message_id")
            relationship_event = relationship_by_message.get(str(message_id)) if message_id else None
            source_memories = memories_by_source.get(str(message_event.id), [])
            causal_chains.append(
                CausalChainRead(
                    message_event_id=message_event.id,
                    relationship_event_id=relationship_event.id if relationship_event else None,
                    message_id=UUID(str(message_id)) if message_id else None,
                    tick_number=message_event.tick_number,
                    sender_agent_id=message_event.actor_agent_id,
                    receiver_agent_id=message_event.target_agent_id,
                    sender_agent_name=id_to_name.get(str(message_event.actor_agent_id), None) if message_event.actor_agent_id else None,
                    receiver_agent_name=id_to_name.get(str(message_event.target_agent_id), None) if message_event.target_agent_id else None,
                    intent=(message_event.payload or {}).get("intent"),
                    emotional_tone=(message_event.payload or {}).get("emotional_tone"),
                    relationship_delta={
                        "trust_before": (relationship_event.payload or {}).get("trust_before") if relationship_event else None,
                        "trust_after": (relationship_event.payload or {}).get("trust_after") if relationship_event else None,
                        "affinity_before": (relationship_event.payload or {}).get("affinity_before") if relationship_event else None,
                        "affinity_after": (relationship_event.payload or {}).get("affinity_after") if relationship_event else None,
                    },
                    memory_ids=[memory.id for memory in source_memories],
                )
            )

        return SocialAnalyticsRead(
            scenario_id=scenario_id,
            communication_feed=communication_feed,
            relationship_graph=relationship_graph,
            interaction_metrics=interaction_rows,
            relationship_history=relationship_history,
            causal_chains=causal_chains,
            cooperation_conflict_summary={
                "total_messages": len(messages),
                "cooperation_events": sum(1 for message in messages if message.intent in COOPERATIVE_INTENTS),
                "conflict_events": sum(1 for message in messages if message.intent in CONFLICT_INTENTS),
                "relationship_updates": len(relationship_updates),
            },
        )
