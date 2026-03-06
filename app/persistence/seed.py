from __future__ import annotations

import argparse
from pathlib import Path
from uuid import UUID

import yaml
from sqlmodel import Session, delete

from app.persistence.engine import get_engine
from app.persistence.models import (
    Agent,
    AgentStateSnapshot,
    DecisionLog,
    Memory,
    MemoryRetrievalTrace,
    Message,
    PersonaProfile,
    Relationship,
    Scenario,
    ScenarioEventInjection,
    SimulationEvent,
    TickResult,
)
from app.schemas.social import MessageTargetMode, SimulationEventType


def seed_scenario(scenario_name: str = "sample_social_triad") -> None:
    base = Path(__file__).resolve().parents[1] / "configs"
    agents_cfg = yaml.safe_load((base / "agents" / "sample_agents.yaml").read_text())
    scenario_path = base / "scenarios" / f"{scenario_name}.yaml"
    if not scenario_path.exists():
        raise ValueError(f"Scenario '{scenario_name}' was not found in {scenario_path.parent}")
    scenario_cfg = yaml.safe_load(scenario_path.read_text())

    with Session(get_engine()) as session:
        # Keep seed deterministic and remove stale rows from previous schema versions.
        session.exec(delete(MemoryRetrievalTrace))
        session.exec(delete(Memory))
        session.exec(delete(DecisionLog))
        session.exec(delete(Message))
        session.exec(delete(SimulationEvent))
        session.exec(delete(TickResult))
        session.exec(delete(AgentStateSnapshot))
        session.exec(delete(Relationship))
        session.exec(delete(ScenarioEventInjection))
        session.exec(delete(Agent))
        session.exec(delete(PersonaProfile))
        session.exec(delete(Scenario))
        session.commit()

        scenario = Scenario(name=scenario_cfg["name"], description=scenario_cfg["description"], status="ready")
        session.add(scenario)
        session.commit()
        session.refresh(scenario)

        agent_rows = {}
        for a in agents_cfg["agents"]:
            persona = PersonaProfile(label=a["persona"]["label"], communication_style=a["persona"].get("communication_style", "neutral"))
            persona.risk_tolerance = a["persona"].get("risk_tolerance", 0.5)
            persona.cooperation_tendency = a["persona"].get("cooperation_tendency", 0.5)
            persona.memory_sensitivity = a["persona"].get("memory_sensitivity", 0.5)
            persona.emotional_bias = a["persona"].get("emotional_bias", 0.0)
            persona.priority_weights = a["persona"].get("priority_weights", {})
            persona.reaction_biases = a["persona"].get("reaction_biases", {})
            session.add(persona)
            session.commit()
            session.refresh(persona)

            agent = Agent(name=a["name"], scenario_id=scenario.id, persona_profile_id=persona.id)
            session.add(agent)
            session.commit()
            session.refresh(agent)

            state = AgentStateSnapshot(
                agent_id=agent.id,
                mood=a.get("initial_state", {}).get("mood", "neutral"),
                active_goals=a.get("initial_state", {}).get("goals", []),
                beliefs=a.get("initial_state", {}).get("beliefs", {}),
            )
            session.add(state)
            session.commit()

            agent_rows[a["name"]] = agent

        for rel in scenario_cfg.get("relationships", []):
            session.add(
                Relationship(
                    scenario_id=scenario.id,
                    source_agent_id=agent_rows[rel["source"]].id,
                    target_agent_id=agent_rows[rel["target"]].id,
                    trust=rel.get("trust", 0.0),
                    affinity=rel.get("affinity", 0.0),
                    stance="neutral",
                )
            )

        for world_event in scenario_cfg.get("world_events", []):
            session.add(
                ScenarioEventInjection(
                    scenario_id=scenario.id,
                    tick_number=world_event["tick"],
                    event_key=world_event["key"],
                    event_content=world_event["content"],
                    payload=world_event.get("payload", {}),
                    is_consumed=False,
                )
            )

        for seed_message in scenario_cfg.get("seed_messages", []):
            sender_id = agent_rows[seed_message["sender"]].id
            receiver_name = seed_message.get("receiver")
            receiver_id: UUID | None = agent_rows[receiver_name].id if receiver_name else None
            msg = Message(
                scenario_id=scenario.id,
                tick_number=seed_message.get("tick", 0),
                sender_agent_id=sender_id,
                receiver_agent_id=receiver_id,
                target_mode=(
                    MessageTargetMode.BROADCAST.value
                    if receiver_id is None
                    else MessageTargetMode.DIRECT.value
                ),
                message_type=(
                    MessageTargetMode.BROADCAST.value
                    if receiver_id is None
                    else MessageTargetMode.DIRECT.value
                ),
                content=seed_message["content"],
                intent=seed_message.get("intent", "observe"),
                emotional_tone=seed_message.get("emotional_tone", "neutral"),
                intent_tags=["seed", seed_message.get("intent", "observe")],
            )
            session.add(msg)
            session.flush()
            session.add(
                SimulationEvent(
                    scenario_id=scenario.id,
                    tick_number=seed_message.get("tick", 0),
                    event_type=SimulationEventType.MESSAGE.value,
                    actor_agent_id=sender_id,
                    target_agent_id=receiver_id,
                    content=seed_message["content"],
                    payload={"message_id": str(msg.id), "source": "seed"},
                )
            )
        session.commit()


def seed_sample_social_triad() -> None:
    seed_scenario("sample_social_triad")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", default="sample_social_triad")
    args = parser.parse_args()
    seed_scenario(args.scenario)
    print("Seed complete")


if __name__ == "__main__":
    main()
