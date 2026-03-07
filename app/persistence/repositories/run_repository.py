from __future__ import annotations

from collections import Counter
from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import DecisionLog, RunMetadata


class RunRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, row: RunMetadata) -> RunMetadata:
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def save(self, row: RunMetadata) -> RunMetadata:
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def get(self, run_id: UUID) -> RunMetadata | None:
        return self.session.get(RunMetadata, run_id)

    def latest_for_scenario(self, scenario_id: UUID) -> RunMetadata | None:
        statement = (
            select(RunMetadata)
            .where(RunMetadata.scenario_id == scenario_id)
            .order_by(RunMetadata.created_at.desc())
        )
        return self.session.exec(statement).first()

    def summarize_decision_sources(
        self,
        scenario_id: UUID,
        tick_from: int,
        tick_to: int,
    ) -> tuple[dict[str, int], int]:
        statement = (
            select(DecisionLog)
            .where(DecisionLog.scenario_id == scenario_id)
            .where(DecisionLog.tick_number >= tick_from)
            .where(DecisionLog.tick_number <= tick_to)
        )
        rows = list(self.session.exec(statement))
        counts = Counter(row.decision_source for row in rows)
        fallback_count = sum(
            1
            for row in rows
            if row.decision_source == "fallback_deterministic" or bool(row.fallback_reason)
        )
        return dict(counts), fallback_count
