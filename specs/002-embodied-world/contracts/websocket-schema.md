# WebSocket Contract: Phase 5 2D Embodied Simulation World

## Endpoint

- **Path**: `/ws/simulation`
- **Transport**: FastAPI WebSocket
- **Schema Version**: `1.0`

## Message Types

### 1. `connection_ack`

Sent by the server after a successful WebSocket connection.

```json
{
  "schema_version": "1.0",
  "type": "connection_ack",
  "scenario_id": "uuid",
  "current_tick": 142,
  "server_time": "2026-03-19T20:15:00Z"
}
```

### 2. `tick_update`

Sent by the server after each completed authoritative tick.

```json
{
  "schema_version": "1.0",
  "type": "tick_update",
  "scenario_id": "uuid",
  "tick_number": 142,
  "sim_time": "2026-03-19T20:15:00Z",
  "time_of_day": "evening",
  "agents": [
    {
      "agent_id": "uuid",
      "name": "Alice",
      "zone_id": "uuid",
      "zone_name": "kitchen",
      "position": {
        "tile_x": 14,
        "tile_y": 8
      },
      "target": {
        "tile_x": 18,
        "tile_y": 8
      },
      "path": {
        "waypoints": [
          {"tile_x": 15, "tile_y": 8},
          {"tile_x": 16, "tile_y": 8},
          {"tile_x": 17, "tile_y": 8},
          {"tile_x": 18, "tile_y": 8}
        ],
        "path_cost": 4,
        "target_zone_id": "uuid"
      },
      "mood": "content",
      "emoji": "🍳",
      "action": "consume_resource",
      "speech": {
        "content": "I found food.",
        "tone": "supportive"
      },
      "thought": {
        "content": "Need to eat now."
      },
      "needs": {
        "hunger": 0.75,
        "safety_need": 0.22,
        "social_need": 0.48
      },
      "goal": {
        "goal_type": "satisfy_hunger",
        "priority": 0.8
      },
      "recent_decisions": [
        {"tick_number": 140, "action": "move", "rationale": "Food is in the kitchen."},
        {"tick_number": 141, "action": "acquire_resource", "rationale": "Food is nearby."},
        {"tick_number": 142, "action": "consume_resource", "rationale": "Hunger is severe."}
      ]
    }
  ],
  "conversations": [
    {
      "source_agent_id": "uuid",
      "target_agent_id": "uuid",
      "intent": "cooperate",
      "tone": "supportive",
      "content": "Let's eat together."
    }
  ],
  "world_events": [
    {
      "event_id": "uuid",
      "event_type": "move",
      "content": "Alice moved to kitchen",
      "created_at": "2026-03-19T20:15:00Z"
    }
  ]
}
```

### 3. `agent_selected`

Sent by the client when a user selects one agent in the viewer.

```json
{
  "schema_version": "1.0",
  "type": "agent_selected",
  "agent_id": "uuid"
}
```

### 4. `sim_control`

Sent by the client when a user requests play/pause/speed changes.

```json
{
  "schema_version": "1.0",
  "type": "sim_control",
  "command": "pause",
  "speed": 1
}
```

Allowed commands:

- `play`
- `pause`
- `set_speed`

### 5. `replay_request`

Sent by the client to request a replay range or mode switch.

```json
{
  "schema_version": "1.0",
  "type": "replay_request",
  "tick_start": 100,
  "tick_end": 150,
  "speed": 2
}
```

## Contract Rules

- All messages MUST include `schema_version`.
- The backend is authoritative for all `tick_update` payloads.
- Clients MAY send selection and control commands, but those commands MUST NOT mutate state
  directly in the client.
- Live snapshots and replay snapshots MUST use the same agent payload shape where possible.
- Heavy payloads such as tilemap definitions and replay arrays SHOULD use REST.
- Unknown message types MUST be ignored safely and logged.
