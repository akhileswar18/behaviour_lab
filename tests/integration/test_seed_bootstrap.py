from app.persistence.init_db import init_db
from app.persistence.seed import seed_sample_social_triad
from app.persistence.repositories.scenario_repository import ScenarioRepository
from app.persistence.engine import get_engine
from sqlmodel import Session


def test_seed_bootstrap_creates_scenario() -> None:
    init_db()
    seed_sample_social_triad()
    with Session(get_engine()) as session:
        repo = ScenarioRepository(session)
        scenarios = repo.list_scenarios()
        assert len(scenarios) >= 1
