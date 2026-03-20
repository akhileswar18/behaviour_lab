# Quickstart: Embodied World Visual Quality Fix

## Prerequisites

- Python backend dependencies installed for the existing Behavior Lab application
- Node.js dependencies installed in `client/`
- Tiled editor installed locally from `https://www.mapeditor.org/` for design-time map editing

## Asset Setup

Place the visual assets in the public client asset tree:

```text
client/public/assets/
├── tilesets/
│   ├── interiors.png
│   └── agents/
│       ├── agent_1.png
│       ├── agent_2.png
│       └── agent_3.png
├── maps/
│   └── house.json
└── ATTRIBUTION.md
```

Asset rules:

- `interiors.png` is the indoor 16x16 pixel-art tileset used by the house map.
- `agent_1.png`, `agent_2.png`, and `agent_3.png` are 16x16 directional spritesheets.
- `house.json` is the Tiled export for the furnished 40x30 house map.
- `ATTRIBUTION.md` documents the source and license for every third-party asset.

## Edit the House Map in Tiled

1. Open Tiled.
2. Open `C:\Users\akhil\behaviour_lab\client\public\assets\maps\house.json`.
3. Confirm the map uses:
   - tile size `16x16`
   - map size `40x30`
   - layers `floor`, `walls`, `furniture`, `furniture_upper`, `collision`, `objects`
4. Edit room layout, furniture placement, and zone rectangles as needed.
5. Save the JSON export back to the same path.
6. If the backend also consumes `maps/house.json`, copy the finalized map there as part of the implementation slice.

## Start the Backend

From the repository root:

```powershell
uvicorn app.api.main:app --reload --port 8000
```

## Start the Frontend

In a second terminal:

```powershell
Set-Location C:\Users\akhil\behaviour_lab\client
npm run dev
```

Open the browser URL reported by Vite.

## Run the Embodied Scenario

Use the existing embodied-world seed and tick workflow from Phase 5:

1. Seed the household scenario with the current embodied-world setup.
2. Run at least 10 ticks so movement, conversations, and decisions are present.
3. Open the client and connect it to the running backend.

## What to Verify

Check for the following visual outcomes:

- the world shows a furnished pixel-art house instead of outlined rectangles
- the browser can show the full static house before any new ticks arrive
- room shapes and door openings are understandable without reading debug labels
- agents appear as distinct animated characters instead of circles
- movement is smooth between ticks rather than snapping instantly
- speech and thought overlays are styled and readable
- the selected-agent panel shows needs bars, goal card, decision log, and conversation feed
- day/night tinting and the minimap remain readable
- if an asset is missing, the world falls back gracefully instead of failing to render

## Phase 3 Static-World And Fallback Checks

Use these checks when validating the real-house render path and the fallback path:

1. Start the frontend with the normal assets in place and confirm the browser shows the furnished five-room house immediately after load.
2. Confirm the kitchen, living room, bedroom, bathroom, and commons corridor are all visually distinct without relying on the old rectangle labels.
3. Temporarily rename `client/public/assets/maps/house.json` or `client/public/assets/tilesets/interiors.png` and refresh the page.
4. Confirm the scene does not crash, shows the fallback layout, and surfaces a visible fallback message instead of a blank canvas.
5. Restore the asset file and confirm the real tilemap render path returns.

## Suggested Validation Pass

1. Load the world with no new ticks and confirm the static house layout is visible.
2. Run 10 live ticks and watch at least one agent cross multiple tiles smoothly.
3. Click an agent and inspect needs, goal, recent decisions, and recent messages.
4. Observe a conversation and confirm the overlay text is readable and trimmed.
5. Temporarily remove one sprite asset and confirm the agent falls back to a readable marker.
