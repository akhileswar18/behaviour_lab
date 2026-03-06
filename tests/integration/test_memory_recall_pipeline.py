from sqlmodel import Session, select

from app.persistence.engine import get_engine
from app.persistence.init_db import init_db
from app.persistence.models import DecisionLog, Memory, MemoryRetrievalTrace, Scenario
from app.persistence.seed import seed_sample_social_triad
from app.simulation.runner import SimulationRunner


def test_memory_recall_pipeline_creates_traces() -> None:
    init_db()
    seed_sample_social_triad()

    with Session(get_engine()) as session:
        scenario = session.exec(select(Scenario)).first()
        assert scenario is not None

        runner = SimulationRunner(session)
        runner.run(scenario.id, 2)
        runner.run(scenario.id, 1)

        memories = list(session.exec(select(Memory)))
        decisions = list(session.exec(select(DecisionLog)))
        traces = list(session.exec(select(MemoryRetrievalTrace)))

        assert len(memories) > 0
        assert len(decisions) > 0
        assert len(traces) > 0
