import json

import pandas as pd
import streamlit as st

from app.dashboard.components.api_client import post_json

st.title("Comparison")
scenario_id = st.text_input("Base Scenario ID")
ticks = st.number_input("Ticks", min_value=1, max_value=50, value=3, step=1)
variant_name = st.text_input("Variant Name", value="persona-variant")
overrides_text = st.text_area(
    "Persona Overrides (JSON by agent name)",
    value='{"Ava": {"risk_tolerance": 0.95, "cooperation_tendency": 0.2}}',
    height=120,
)

if st.button("Run Variant Comparison", type="primary"):
    if not scenario_id:
        st.error("Scenario ID is required.")
    else:
        try:
            overrides = json.loads(overrides_text) if overrides_text.strip() else {}
            result = post_json(
                f"/scenarios/{scenario_id}/compare-rerun",
                {
                    "ticks": int(ticks),
                    "variant_name": variant_name,
                    "persona_overrides": overrides,
                },
            )
            st.success("Comparison completed")
            st.json(result)
            differences = result.get("comparison", {}).get("differences", {})
            if differences:
                st.subheader("Difference Summary")
                st.dataframe(pd.DataFrame([differences]), width="stretch")
        except json.JSONDecodeError:
            st.error("Invalid JSON in persona overrides.")
        except Exception as exc:  # pragma: no cover - streamlit runtime path
            st.error(f"Comparison failed: {exc}")
