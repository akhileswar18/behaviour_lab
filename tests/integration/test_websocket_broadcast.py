from fastapi.testclient import TestClient


def test_websocket_broadcast_fans_out_to_multiple_clients(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]

    with phase3_seeded_client.websocket_connect(f"/ws/simulation?scenario_id={scenario_id}") as first:
        with phase3_seeded_client.websocket_connect(f"/ws/simulation?scenario_id={scenario_id}") as second:
            ack_one = first.receive_json()
            ack_two = second.receive_json()
            run_response = phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 1})

            assert ack_one["type"] == "connection_ack"
            assert ack_two["type"] == "connection_ack"
            assert run_response.status_code == 200
            assert first.receive_json()["type"] == "tick_update"
            assert second.receive_json()["type"] == "tick_update"
