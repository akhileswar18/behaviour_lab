from __future__ import annotations

from html import escape
from math import sqrt

import streamlit as st

from app.dashboard.components.zone_graph import NODE_BORDER, NODE_FILL, WorldGraph, build_world_graph


AXIS_MAX = 100.0
CARD_WIDTH = 22.0
CARD_HEIGHT = 18.0


def _plotly_objects():
    try:
        import plotly.graph_objects as go
    except ModuleNotFoundError:
        return None
    return go


def _scaled(value: float) -> float:
    return value * AXIS_MAX


def _node_lookup(graph: WorldGraph) -> dict[str, object]:
    return {node.zone_id: node for node in graph.nodes}


def _edge_style(movement_count: int) -> tuple[str, float, float]:
    if movement_count > 0:
        return "#4E5D6C", 2.0 + min(movement_count, 4) * 0.9, 0.75
    return "#B5BDC7", 1.1, 0.28


def _zone_hover(node) -> str:
    occupants = ", ".join(occupant["agent_name"] for occupant in node.occupants) or "No agents"
    resources = "<br>".join(
        f"{escape(resource['resource_type'])}: {int(resource['quantity'])} ({resource['percentage']:.0%})"
        for resource in node.resources
    ) or "No resources"
    return (
        f"<b>{escape(node.zone_name)}</b><br>"
        f"{escape(node.zone_type.title())}<br>"
        f"Occupants: {escape(occupants)}<br>"
        f"{resources}<extra></extra>"
    )


def _curve_points(start_x: float, start_y: float, end_x: float, end_y: float) -> tuple[list[float], list[float]]:
    mid_x = (start_x + end_x) / 2
    mid_y = (start_y + end_y) / 2
    dx = end_x - start_x
    dy = end_y - start_y
    distance = max(sqrt(dx**2 + dy**2), 1.0)
    offset_scale = min(9.0, 3.5 + distance * 0.06)
    control_x = mid_x - dy / distance * offset_scale
    control_y = mid_y + dx / distance * offset_scale

    xs: list[float] = []
    ys: list[float] = []
    steps = 16
    for step in range(steps + 1):
        t = step / steps
        xs.append(
            ((1 - t) ** 2) * start_x
            + (2 * (1 - t) * t * control_x)
            + (t**2) * end_x
        )
        ys.append(
            ((1 - t) ** 2) * start_y
            + (2 * (1 - t) * t * control_y)
            + (t**2) * end_y
        )
    return xs, ys


def _render_fallback(graph: WorldGraph) -> None:
    st.info("Plotly is not installed, so the world graph is using the built-in fallback view.")
    columns = st.columns(min(max(len(graph.nodes), 1), 3))
    for index, node in enumerate(graph.nodes):
        column = columns[index % len(columns)]
        with column:
            with st.container(border=True):
                st.markdown(f"**{node.zone_name}**")
                st.caption(node.zone_type.replace("_", " ").title())
                if node.resources:
                    for resource in node.resources[:4]:
                        st.caption(
                            f"{resource['resource_type'].replace('_', ' ').title()} "
                            f"{resource['percentage']:.0%}"
                        )
                        st.progress(float(resource["percentage"]))
                else:
                    st.caption("No resources in this zone.")

                if node.occupants:
                    for occupant in node.occupants[:6]:
                        st.markdown(
                            f"<span style='color:{occupant['color']};font-weight:600;'>●</span> "
                            f"{escape(occupant['agent_name'])}",
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("No agents present.")


def render_world_graph(snapshot: dict) -> None:
    graph = build_world_graph(snapshot)
    if not graph.nodes:
        st.info("No world graph data available for the current filters.")
        return

    go = _plotly_objects()
    if go is None:
        _render_fallback(graph)
        st.caption(
            "Install `plotly` for the full transit-map visualization: "
            "`pip install plotly` or `pip install -e .[dev]` after refreshing dependencies."
        )
        return

    fig = go.Figure()
    nodes_by_id = _node_lookup(graph)

    for edge in graph.edges:
        source = nodes_by_id.get(edge.source_zone_id)
        target = nodes_by_id.get(edge.target_zone_id)
        if source is None or target is None:
            continue
        source_x = _scaled(source.x)
        source_y = _scaled(source.y)
        target_x = _scaled(target.x)
        target_y = _scaled(target.y)
        color, width, opacity = _edge_style(edge.agent_movements)
        fig.add_trace(
            go.Scatter(
                x=[source_x, target_x],
                y=[source_y, target_y],
                mode="lines",
                line={
                    "color": color,
                    "width": width,
                    "dash": "solid" if edge.agent_movements > 0 else "dot",
                },
                opacity=opacity,
                hoverinfo="skip",
                showlegend=False,
            )
        )

    for transit in graph.transits:
        source = nodes_by_id.get(transit.from_zone_id)
        target = nodes_by_id.get(transit.to_zone_id)
        if source is None or target is None:
            continue
        xs, ys = _curve_points(
            _scaled(source.x),
            _scaled(source.y),
            _scaled(target.x),
            _scaled(target.y),
        )
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines",
                line={"color": transit.agent_color, "width": 3, "dash": "dash"},
                opacity=0.95,
                hovertemplate=(
                    f"<b>{escape(transit.agent_name)}</b><br>"
                    f"Recent movement: {escape(source.zone_name)} -> {escape(target.zone_name)}"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )
        fig.add_annotation(
            x=xs[len(xs) // 2],
            y=ys[len(ys) // 2] + 2.2,
            text=escape(transit.agent_name),
            showarrow=False,
            font={"size": 11, "color": transit.agent_color},
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor=transit.agent_color,
            borderwidth=1,
        )

    zone_xs: list[float] = []
    zone_ys: list[float] = []
    zone_hover: list[str] = []

    for node in graph.nodes:
        center_x = _scaled(node.x)
        center_y = _scaled(node.y)
        left = center_x - CARD_WIDTH / 2
        right = center_x + CARD_WIDTH / 2
        bottom = center_y - CARD_HEIGHT / 2
        top = center_y + CARD_HEIGHT / 2

        fig.add_shape(
            type="rect",
            x0=left,
            x1=right,
            y0=bottom,
            y1=top,
            line={"color": NODE_BORDER, "width": 2},
            fillcolor=NODE_FILL,
            layer="above",
        )
        fig.add_annotation(
            x=left + 1.8,
            y=top - 2.6,
            text=f"<b>{escape(node.zone_name)}</b>",
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            align="left",
            font={"size": 14, "color": "#1F2933"},
        )
        fig.add_annotation(
            x=left + 1.8,
            y=top - 5.3,
            text=escape(node.zone_type.replace("_", " ").title()),
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            align="left",
            font={"size": 10, "color": "#66737F"},
        )

        resource_start_y = top - 8.1
        for index, resource in enumerate(node.resources[:4]):
            bar_y = resource_start_y - index * 3.1
            label = (
                f"{resource['resource_type'].replace('_', ' ').title()} "
                f"{resource['percentage']:.0%}"
            )
            fig.add_annotation(
                x=left + 1.8,
                y=bar_y + 0.8,
                text=escape(label),
                showarrow=False,
                xanchor="left",
                yanchor="middle",
                align="left",
                font={"size": 9, "color": "#364152"},
            )
            fig.add_shape(
                type="rect",
                x0=left + 1.8,
                x1=right - 1.8,
                y0=bar_y - 0.6,
                y1=bar_y + 0.2,
                line={"color": resource["track_color"], "width": 0},
                fillcolor=resource["track_color"],
                layer="above",
            )
            fig.add_shape(
                type="rect",
                x0=left + 1.8,
                x1=(left + 1.8) + ((right - left - 3.6) * resource["percentage"]),
                y0=bar_y - 0.6,
                y1=bar_y + 0.2,
                line={"color": resource["health_color"], "width": 0},
                fillcolor=resource["health_color"],
                layer="above",
            )

        for index, occupant in enumerate(node.occupants[:6]):
            row = index // 3
            column = index % 3
            dot_x = left + 2.2 + (column * 6.4)
            dot_y = bottom + 2.6 - (row * 2.3)
            fig.add_trace(
                go.Scatter(
                    x=[dot_x],
                    y=[dot_y],
                    mode="markers+text",
                    marker={
                        "size": 10,
                        "color": occupant["color"],
                        "line": {"color": "#FFFFFF", "width": 1.2},
                    },
                    text=[occupant["agent_name"]],
                    textposition="middle right",
                    textfont={"size": 10, "color": "#1F2933"},
                    hovertemplate=(
                        f"<b>{escape(occupant['agent_name'])}</b><br>"
                        f"Zone: {escape(node.zone_name)}<extra></extra>"
                    ),
                    showlegend=False,
                )
            )

        zone_xs.append(center_x)
        zone_ys.append(center_y)
        zone_hover.append(_zone_hover(node))

    fig.add_trace(
        go.Scatter(
            x=zone_xs,
            y=zone_ys,
            mode="markers",
            marker={"size": 48, "color": "rgba(0,0,0,0)"},
            hovertemplate=zone_hover,
            showlegend=False,
        )
    )

    fig.update_layout(
        height=720,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        paper_bgcolor="#FBFBF8",
        plot_bgcolor="#FBFBF8",
        xaxis={
            "range": [0, AXIS_MAX],
            "visible": False,
            "fixedrange": True,
        },
        yaxis={
            "range": [0, AXIS_MAX],
            "visible": False,
            "fixedrange": True,
            "scaleanchor": "x",
            "scaleratio": 1,
        },
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Resource gauges are normalized against the highest visible quantity for each resource "
        "type in the current filtered snapshot because the world analytics endpoint does not "
        "currently expose initial resource baselines."
    )
