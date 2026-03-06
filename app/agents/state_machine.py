from app.persistence.models import AgentStateSnapshot


def transition_state(previous: AgentStateSnapshot | None, tick_number: int) -> AgentStateSnapshot:
    if previous is None:
        return AgentStateSnapshot(agent_id="00000000-0000-0000-0000-000000000000", tick_number=tick_number)

    mood = previous.mood
    if tick_number % 3 == 0:
        mood = "engaged"

    return AgentStateSnapshot(
        agent_id=previous.agent_id,
        tick_number=tick_number,
        mood=mood,
        active_goals=previous.active_goals,
        beliefs=previous.beliefs,
        energy=max(previous.energy - 1, 0),
        stress=min(previous.stress + 0.5, 100),
    )
