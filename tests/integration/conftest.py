from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.persistence.init_db import init_db
from app.persistence.seed import seed_sample_goal_resource_lab, seed_sample_social_triad


@pytest.fixture()
def seeded_client() -> TestClient:
    init_db()
    seed_sample_social_triad()
    return TestClient(app)


@pytest.fixture()
def phase3_seeded_client() -> TestClient:
    init_db()
    seed_sample_goal_resource_lab()
    return TestClient(app)
