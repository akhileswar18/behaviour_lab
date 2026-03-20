from collections.abc import Iterable

from sqlmodel import SQLModel

from app.persistence.engine import get_engine
from app.persistence import models  # noqa: F401


def _ensure_columns(table_name: str, column_definitions: Iterable[str]) -> None:
    engine = get_engine()
    with engine.begin() as connection:
        rows = connection.exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
        existing = {row[1] for row in rows}
        for column in column_definitions:
            column_name = column.split(" ", 1)[0]
            if column_name not in existing:
                connection.exec_driver_sql(f"ALTER TABLE {table_name} ADD COLUMN {column}")


def _ensure_indexes() -> None:
    engine = get_engine()
    statements = [
        "CREATE INDEX IF NOT EXISTS ix_message_scenario_tick ON message (scenario_id, tick_number)",
        "CREATE INDEX IF NOT EXISTS ix_message_sender_receiver ON message (sender_agent_id, receiver_agent_id)",
        "CREATE INDEX IF NOT EXISTS ix_event_scenario_tick_type ON simulationevent (scenario_id, tick_number, event_type)",
        "CREATE INDEX IF NOT EXISTS ix_relationship_scenario_agents ON relationship (scenario_id, source_agent_id, target_agent_id)",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_relationship_scenario_pair ON relationship (scenario_id, source_agent_id, target_agent_id)",
        "CREATE INDEX IF NOT EXISTS ix_decision_scenario_tick_agent ON decisionlog (scenario_id, tick_number, agent_id)",
        "CREATE INDEX IF NOT EXISTS ix_event_injection_scenario_tick ON scenarioeventinjection (scenario_id, tick_number, is_consumed)",
        "CREATE INDEX IF NOT EXISTS ix_goal_scenario_agent_status ON goal (scenario_id, agent_id, status)",
        "CREATE INDEX IF NOT EXISTS ix_intention_scenario_agent_status ON intention (scenario_id, agent_id, status)",
        "CREATE INDEX IF NOT EXISTS ix_resource_scenario_zone_type ON resource (scenario_id, zone_id, resource_type)",
        "CREATE INDEX IF NOT EXISTS ix_agent_state_agent_tick ON agentstatesnapshot (agent_id, tick_number)",
        "CREATE INDEX IF NOT EXISTS ix_agentstatesnapshot_tile_x ON agentstatesnapshot (tile_x)",
        "CREATE INDEX IF NOT EXISTS ix_agentstatesnapshot_tile_y ON agentstatesnapshot (tile_y)",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_zone_scenario_name ON zone (scenario_id, name)",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_tilemapconfig_scenario ON tilemapconfig (scenario_id)",
    ]
    with engine.begin() as connection:
        for statement in statements:
            connection.exec_driver_sql(statement)


def init_db() -> None:
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    _ensure_columns(
        "personaprofile",
        [
            "memory_sensitivity FLOAT DEFAULT 0.5",
            "emotional_bias FLOAT DEFAULT 0.0",
        ],
    )
    _ensure_columns(
        "agentstatesnapshot",
        [
            "hunger FLOAT DEFAULT 0.0",
            "safety_need FLOAT DEFAULT 0.0",
            "social_need FLOAT DEFAULT 0.0",
            "zone_id CHAR(32)",
            "tile_x INTEGER",
            "tile_y INTEGER",
            "inventory JSON DEFAULT '{}'",
        ],
    )
    _ensure_columns(
        "message",
        [
            "target_mode VARCHAR DEFAULT 'direct'",
            "intent VARCHAR DEFAULT 'observe'",
            "emotional_tone VARCHAR DEFAULT 'neutral'",
        ],
    )
    _ensure_columns(
        "relationship",
        [
            "stance VARCHAR DEFAULT 'neutral'",
            "last_interaction_at DATETIME",
        ],
    )
    _ensure_columns(
        "simulationevent",
        [
            "content VARCHAR DEFAULT ''",
        ],
    )
    _ensure_columns(
        "decisionlog",
        [
            "persona_factors JSON DEFAULT '{}'",
            "relationship_factors JSON DEFAULT '{}'",
            "world_event_factors JSON DEFAULT '{}'",
            "decision_source VARCHAR DEFAULT 'deterministic'",
            "parser_status VARCHAR DEFAULT 'not_attempted'",
            "fallback_reason VARCHAR",
            "prompt_summary JSON DEFAULT '{}'",
            "llm_metadata JSON DEFAULT '{}'",
            "message_id CHAR(32)",
        ],
    )
    _ensure_columns(
        "runmetadata",
        [
            "planning_overrides JSON DEFAULT '{}'",
            "world_overrides JSON DEFAULT '{}'",
            "policy_mode VARCHAR DEFAULT 'deterministic'",
            "llm_provider VARCHAR",
            "llm_model VARCHAR",
            "llm_config_summary JSON DEFAULT '{}'",
            "decision_source_counts JSON DEFAULT '{}'",
            "fallback_count INTEGER DEFAULT 0",
            "parse_failure_count INTEGER DEFAULT 0",
        ],
    )
    _ensure_columns(
        "runcomparisonsummary",
        [
            "completed_goal_delta INTEGER DEFAULT 0",
            "move_event_delta INTEGER DEFAULT 0",
            "resource_event_delta INTEGER DEFAULT 0",
            "fallback_count_delta INTEGER DEFAULT 0",
            "llm_decision_delta INTEGER DEFAULT 0",
        ],
    )
    _ensure_indexes()


if __name__ == "__main__":
    init_db()
    print("Database initialized")
