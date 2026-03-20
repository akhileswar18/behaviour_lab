export type MessageType =
  | "connection_ack"
  | "tick_update"
  | "agent_selected"
  | "sim_control"
  | "replay_request";

export type PlaybackSpeed = 1 | 2 | 5;

export interface TilePosition {
  tile_x: number;
  tile_y: number;
  subtile_progress?: number | null;
}

export interface PathSegment {
  waypoints: TilePosition[];
  path_cost: number;
  target_zone_id?: string | null;
  target_object_id?: string | null;
}

export interface NearbyAgent {
  agent_id: string;
  agent_name: string;
  tile_distance: number;
  zone_name?: string | null;
}

export interface NearbyObject {
  object_id: string;
  name: string;
  zone_name?: string | null;
  affordance_type?: string | null;
  resource_type?: string | null;
  tile_position: TilePosition;
  properties: Record<string, unknown>;
}

export interface SpatialPerception {
  current_tile?: TilePosition | null;
  current_room?: string | null;
  zone_id?: string | null;
  nearby_agents: NearbyAgent[];
  nearby_objects: NearbyObject[];
  visible_resources: Record<string, unknown>[];
  pathfinding_costs: Record<string, number>;
  door_connections: string[];
}

export interface NeedLevels {
  hunger: number;
  safety_need: number;
  social_need: number;
  energy?: number;
  stress?: number;
}

export interface GoalSummary {
  goal_type: string;
  priority: number;
}

export interface DecisionSummary {
  tick_number: number;
  action: string;
  rationale: string;
}

export interface BubblePayload {
  content: string;
  tone?: string | null;
}

export interface ConversationSummary {
  source_agent_id: string;
  target_agent_id?: string | null;
  intent: string;
  tone: string;
  content: string;
}

export interface WorldEventSummary {
  event_id?: string | null;
  event_type: string;
  content: string;
  created_at?: string | null;
}

export interface AgentSnapshot {
  agent_id: string;
  name: string;
  zone_id?: string | null;
  zone_name?: string | null;
  position: TilePosition | null;
  target?: TilePosition | null;
  path?: PathSegment | null;
  mood: string;
  emoji?: string | null;
  action: string;
  speech?: BubblePayload | null;
  thought?: BubblePayload | null;
  needs: NeedLevels;
  goal?: GoalSummary | null;
  recent_decisions: DecisionSummary[];
  spatial_context?: SpatialPerception | null;
}

export interface WorldSnapshot {
  schema_version: "1.0";
  type: "tick_update";
  scenario_id: string;
  tick_number: number;
  sim_time: string;
  time_of_day: string;
  agents: AgentSnapshot[];
  conversations: ConversationSummary[];
  world_events: WorldEventSummary[];
}

export interface ConnectionAck {
  schema_version: "1.0";
  type: "connection_ack";
  scenario_id: string;
  current_tick: number;
  server_time: string;
}

export interface ReplayResponse {
  scenario_id: string;
  tick_start: number;
  tick_end: number;
  snapshots: WorldSnapshot[];
}

export interface WorldMapResponse {
  scenario_id?: string | null;
  map_file_path: string;
  map: Record<string, unknown>;
}

export type SocketMessage = ConnectionAck | WorldSnapshot;
