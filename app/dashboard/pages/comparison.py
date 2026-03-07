import json

import pandas as pd
import streamlit as st

from app.dashboard.components.api_client import post_json

st.title("Comparison")
scenario_id = st.text_input("Base Scenario ID")
ticks = st.number_input("Ticks", min_value=1, max_value=50, value=3, step=1)
variant_name = st.text_input("Variant Name", value="phase3-variant")
base_policy_mode = st.selectbox(
    "Base Policy Mode",
    options=["deterministic", "llm", "hybrid"],
    index=0,
)
variant_policy_mode = st.selectbox(
    "Variant Policy Mode",
    options=["deterministic", "llm", "hybrid"],
    index=0,
)
persona_text = st.text_area(
    "Persona Overrides (JSON by agent name)",
    value='{"Ava": {"risk_tolerance": 0.95, "cooperation_tendency": 0.2}}',
    height=100,
)
planning_text = st.text_area(
    "Planning Overrides (JSON by agent name)",
    value='{"Ben": {"hunger": 0.9, "zone_id": "Storage"}}',
    height=100,
)
world_text = st.text_area(
    "World Overrides (JSON by zone name)",
    value='{"Storage": {"food": 0}, "Commons": {"token": 5}}',
    height=100,
)

if st.button("Run Variant Comparison", type="primary"):
    if not scenario_id:
        st.error("Scenario ID is required.")
    else:
        try:
            persona_overrides = json.loads(persona_text) if persona_text.strip() else {}
            planning_overrides = json.loads(planning_text) if planning_text.strip() else {}
            world_overrides = json.loads(world_text) if world_text.strip() else {}
            result = post_json(
                f"/scenarios/{scenario_id}/compare-rerun",
                {
                    "ticks": int(ticks),
                    "variant_name": variant_name,
                    "persona_overrides": persona_overrides,
                    "planning_overrides": planning_overrides,
                    "world_overrides": world_overrides,
                    "base_policy_mode": base_policy_mode,
                    "variant_policy_mode": variant_policy_mode,
                },
            )
            st.success("Comparison completed")
            st.json(result)
            differences = result.get("comparison", {}).get("differences", {})
            if differences:
                st.subheader("Difference Summary")
                st.dataframe(pd.DataFrame([differences]), width="stretch")
            st.caption(
                "Modes: "
                f"base={result.get('base_policy_mode', base_policy_mode)} | "
                f"variant={result.get('variant_policy_mode', variant_policy_mode)}"
            )
        except json.JSONDecodeError:
            st.error("Invalid JSON in overrides.")
        except Exception as exc:  # pragma: no cover - streamlit runtime path
            st.error(f"Comparison failed: {exc}")
