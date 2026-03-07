from __future__ import annotations

from collections import Counter
from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import Goal, Intention
from app.persistence.repositories.base import RepositoryBase


class PlanningRepository(RepositoryBase[Goal]):
    def __init__(self, session: Session):
        super().__init__(session)

    def add_goal(self, goal: Goal) -> Goal:
        return self.add(goal)

    def save_goal(self, goal: Goal) -> Goal:
        self.session.add(goal)
        self.session.commit()
        self.session.refresh(goal)
        return goal

    def list_goals(self, scenario_id: UUID, agent_id: UUID | None = None) -> list[Goal]:
        statement = select(Goal).where(Goal.scenario_id == scenario_id).order_by(Goal.priority.desc(), Goal.updated_at.desc())
        if agent_id is not None:
            statement = statement.where(Goal.agent_id == agent_id)
        return list(self.session.exec(statement))

    def active_goal(self, scenario_id: UUID, agent_id: UUID) -> Goal | None:
        statement = (
            select(Goal)
            .where(Goal.scenario_id == scenario_id)
            .where(Goal.agent_id == agent_id)
            .where(Goal.status == "active")
            .order_by(Goal.priority.desc(), Goal.updated_at.desc())
        )
        return self.session.exec(statement).first()

    def add_intention(self, intention: Intention) -> Intention:
        self.session.add(intention)
        self.session.commit()
        self.session.refresh(intention)
        return intention

    def save_intention(self, intention: Intention) -> Intention:
        self.session.add(intention)
        self.session.commit()
        self.session.refresh(intention)
        return intention

    def list_intentions(self, scenario_id: UUID, agent_id: UUID | None = None) -> list[Intention]:
        statement = (
            select(Intention)
            .where(Intention.scenario_id == scenario_id)
            .order_by(Intention.updated_at.desc())
        )
        if agent_id is not None:
            statement = statement.where(Intention.agent_id == agent_id)
        return list(self.session.exec(statement))

    def active_intention(self, scenario_id: UUID, agent_id: UUID) -> Intention | None:
        statement = (
            select(Intention)
            .where(Intention.scenario_id == scenario_id)
            .where(Intention.agent_id == agent_id)
            .where(Intention.status == "active")
            .order_by(Intention.updated_at.desc())
        )
        return self.session.exec(statement).first()

    def goal_status_counts(self, scenario_id: UUID, agent_id: UUID | None = None) -> dict[str, int]:
        statuses = [goal.status for goal in self.list_goals(scenario_id, agent_id=agent_id)]
        return dict(Counter(statuses))

    def recent_goal_history(self, scenario_id: UUID, agent_id: UUID, limit: int = 6) -> list[Goal]:
        statement = (
            select(Goal)
            .where(Goal.scenario_id == scenario_id)
            .where(Goal.agent_id == agent_id)
            .order_by(Goal.updated_at.desc())
        )
        return list(self.session.exec(statement))[:limit]

    def recent_intention_history(self, scenario_id: UUID, agent_id: UUID, limit: int = 6) -> list[Intention]:
        statement = (
            select(Intention)
            .where(Intention.scenario_id == scenario_id)
            .where(Intention.agent_id == agent_id)
            .order_by(Intention.updated_at.desc())
        )
        return list(self.session.exec(statement))[:limit]
