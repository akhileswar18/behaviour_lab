from sqlmodel import Session, select

from app.persistence.models import Memory


def retrieve_relevant(session: Session, agent_id, limit: int = 5) -> list[Memory]:
    statement = (
        select(Memory)
        .where(Memory.agent_id == agent_id)
        .order_by(Memory.salience.desc(), Memory.created_at.desc())
        .limit(limit)
    )
    return list(session.exec(statement))
