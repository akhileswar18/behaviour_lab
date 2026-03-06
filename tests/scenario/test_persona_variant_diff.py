from fastapi.testclient import TestClient

from app.api.main import app
from app.persistence.init_db import init_db
from app.persistence.seed import seed_sample_social_triad


client = TestClient(app)


def test_persona_variant_diff_endpoint() -> None:
    init_db()
    seed_sample_social_triad()

    # Create a second scenario to serve as comparison baseline.
    second = client.post("/scenarios", json={"name": "variant-scenario", "description": "variant"}).json()

    scenarios = client.get("/scenarios").json()
    first_id = scenarios[0]["id"]
    second_id = second["id"]

    client.post(f"/scenarios/{first_id}/run", json={"ticks": 2})

    compare = client.get(f"/scenarios/{first_id}/compare/{second_id}")
    assert compare.status_code == 200
    metrics = compare.json()["metrics"]
    assert "decision_count_delta" in metrics
