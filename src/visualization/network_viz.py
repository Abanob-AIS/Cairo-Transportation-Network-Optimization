"""
Network Visualization (Geographic Mapbox)
============================================
Plotly Scattermapbox-based interactive visualizations on real geographic maps.
Uses 'carto-darkmatter' style (no API key required) for dark theme consistency.
"""
import plotly.graph_objects as go
from src.data.cairo_data import get_all_nodes, EXISTING_ROADS, NEIGHBORHOODS, FACILITIES


# ── Color palette ───────────────────────────────────────────────────────────
COLORS = {
    "Residential": "#4FC3F7", "Mixed": "#81C784", "Business": "#FFB74D",
    "Industrial": "#E57373", "Government": "#CE93D8", "Airport": "#F06292",
    "Transit Hub": "#4DD0E1", "Education": "#AED581", "Tourism": "#FFD54F",
    "Sports": "#FF8A65", "Commercial": "#9575CD", "Medical": "#EF5350",
}

MARKER_SYMBOLS = {
    "Medical": "hospital", "Airport": "airport", "Transit Hub": "rail",
    "Education": "college", "Tourism": "museum", "Sports": "stadium",
    "Commercial": "shop", "Business": "commercial",
}

# Cairo center for default map view
CAIRO_CENTER = {"lat": 30.02, "lon": 31.23}
DEFAULT_ZOOM = 9.5
MAP_STYLE = "carto-darkmatter"


def _base_layout(title="", zoom=DEFAULT_ZOOM, center=None):
    """Shared Mapbox layout for every map in the project."""
    if center is None:
        center = CAIRO_CENTER
    return dict(
        title=dict(text=title, font=dict(size=18, color="white")),
        paper_bgcolor="#16213e",
        margin=dict(l=0, r=0, t=50, b=0),
        height=650,
        font=dict(color="white"),
        legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0.5)"),
        mapbox=dict(
            style=MAP_STYLE,
            center=center,
            zoom=zoom,
        ),
    )


def _get_node_color(node_data):
    return COLORS.get(node_data.get("type", ""), "#90A4AE")


def _node_size(data):
    """Node marker size based on population / category."""
    if data.get("category") == "facility":
        return 10
    pop = data.get("population", 0)
    return max(8, min(22, pop / 25000))


# ── Edge helpers ────────────────────────────────────────────────────────────

def _edge_trace(lats, lons, color="#555555", width=1.5, name="", text="",
                dash=None, showlegend=False):
    """Create a single Mapbox line trace for one or more edges."""
    return go.Scattermapbox(
        lat=lats, lon=lons, mode="lines",
        line=dict(width=width, color=color),
        hovertext=text, hoverinfo="text",
        name=name, showlegend=showlegend,
    )


def _draw_road_edges(fig, nodes, roads, color="#555555", width=1.5):
    """Batch all road edges into a single trace for performance."""
    lats, lons, texts = [], [], []
    for road in roads:
        fn, tn = nodes.get(road["from"]), nodes.get(road["to"])
        if not fn or not tn:
            continue
        lats += [fn["y"], tn["y"], None]
        lons += [fn["x"], tn["x"], None]
        texts.append(f"{road['from']}→{road['to']}: {road['distance']}km")
    fig.add_trace(go.Scattermapbox(
        lat=lats, lon=lons, mode="lines",
        line=dict(width=width, color=color),
        hovertext=texts, hoverinfo="text",
        name="Roads", showlegend=False,
    ))


# ── Public API ──────────────────────────────────────────────────────────────

def plot_network(title="Cairo Transportation Network", show_labels=True,
                 highlight_edges=None, highlight_nodes=None, edge_color_map=None):
    """Plot the full transportation network on a real geographic map."""
    nodes = get_all_nodes()
    fig = go.Figure()

    # --- Edges ---
    _draw_road_edges(fig, nodes, EXISTING_ROADS)

    # --- Nodes grouped by type (for legend) ---
    type_groups = {}
    for nid, data in nodes.items():
        t = data.get("type", "Other")
        if t not in type_groups:
            type_groups[t] = {"lat": [], "lon": [], "text": [], "size": [], "ids": []}
        grp = type_groups[t]
        grp["lat"].append(data["y"])
        grp["lon"].append(data["x"])
        grp["size"].append(_node_size(data))
        grp["ids"].append(nid)
        label = f"<b>{data['name']}</b><br>ID: {nid}<br>Type: {t}"
        pop = data.get("population", 0)
        if pop:
            label += f"<br>Pop: {pop:,}"
        grp["text"].append(label)

    for t, grp in type_groups.items():
        fig.add_trace(go.Scattermapbox(
            lat=grp["lat"], lon=grp["lon"],
            mode="markers+text" if show_labels else "markers",
            marker=dict(size=grp["size"], color=_get_node_color({"type": t})),
            text=[nodes[nid]["name"][:12] for nid in grp["ids"]] if show_labels else None,
            textposition="top center", textfont=dict(size=8, color="white"),
            hovertext=grp["text"], hoverinfo="text",
            name=t,
        ))

    fig.update_layout(**_base_layout(title))
    return fig


def plot_mst(mst_result, graph, title="Optimized Infrastructure Network (MST)"):
    """Plot MST edges highlighted on the geographic map."""
    fig = plot_network(title=title, show_labels=True)
    nodes = graph.nodes

    # Separate existing vs potential new roads
    for is_pot, color, name in [(False, "#00E676", "Existing (MST)"),
                                 (True, "#FF6B35", "New Road (MST)")]:
        lats, lons, texts = [], [], []
        for edge in mst_result["mst_edges"]:
            if edge.get("is_potential", False) != is_pot:
                continue
            fn, tn = nodes.get(edge["from"]), nodes.get(edge["to"])
            if not fn or not tn:
                continue
            lats += [fn["y"], tn["y"], None]
            lons += [fn["x"], tn["x"], None]
            texts.append(f"MST: {edge['from']}→{edge['to']} ({edge['distance']}km)")
        if lats:
            fig.add_trace(go.Scattermapbox(
                lat=lats, lon=lons, mode="lines",
                line=dict(width=4, color=color),
                hovertext=texts, hoverinfo="text",
                name=name,
            ))
    return fig


def plot_path(path, graph, title="Route", color="#00E5FF", show_all=True):
    """Plot a path on the geographic map."""
    fig = plot_network(title=title, show_labels=True) if show_all else go.Figure()
    nodes = graph.nodes
    if not path:
        if not show_all:
            fig.update_layout(**_base_layout(title))
        return fig

    # Path edges
    lats, lons = [], []
    for i in range(len(path) - 1):
        fn, tn = nodes.get(path[i]), nodes.get(path[i + 1])
        if fn and tn:
            lats += [fn["y"], tn["y"], None]
            lons += [fn["x"], tn["x"], None]
    fig.add_trace(go.Scattermapbox(
        lat=lats, lon=lons, mode="lines",
        line=dict(width=5, color=color),
        name="Route", showlegend=True,
    ))

    # Start marker
    start = nodes.get(path[0])
    if start:
        fig.add_trace(go.Scattermapbox(
            lat=[start["y"]], lon=[start["x"]], mode="markers",
            marker=dict(size=18, color="#00E676", symbol="star"),
            name="Start",
            hovertext=f"Start: {graph.get_node_name(path[0])}", hoverinfo="text",
        ))
    # End marker
    end = nodes.get(path[-1])
    if end:
        fig.add_trace(go.Scattermapbox(
            lat=[end["y"]], lon=[end["x"]], mode="markers",
            marker=dict(size=18, color="#FF1744", symbol="star"),
            name="End",
            hovertext=f"End: {graph.get_node_name(path[-1])}", hoverinfo="text",
        ))

    if not show_all:
        fig.update_layout(**_base_layout(title))
    return fig


def plot_emergency_route(path, graph, title="Emergency Route"):
    """Plot emergency vehicle route with red styling on the real map."""
    return plot_path(path, graph, title=title, color="#FF1744")


def plot_congestion_map(graph, time_period="morning"):
    """Plot network colored by congestion level on the real map."""
    from src.data.cairo_data import TRAFFIC_FLOW
    nodes = graph.nodes
    fig = go.Figure()

    # Color-coded edges by congestion
    buckets = {
        "Low (<50%)":     {"color": "#4CAF50", "lats": [], "lons": [], "texts": []},
        "Moderate (50-75%)": {"color": "#FFC107", "lats": [], "lons": [], "texts": []},
        "High (75-90%)":  {"color": "#FF9800", "lats": [], "lons": [], "texts": []},
        "Severe (>90%)":  {"color": "#F44336", "lats": [], "lons": [], "texts": []},
    }

    for road in EXISTING_ROADS:
        fn, tn = nodes.get(road["from"]), nodes.get(road["to"])
        if not fn or not tn:
            continue
        flow_key = (road["from"], road["to"])
        flow_data = TRAFFIC_FLOW.get(flow_key, {})
        flow = flow_data.get(time_period, road["capacity"] * 0.5)
        ratio = flow / road["capacity"]

        if ratio < 0.5:
            key = "Low (<50%)"
        elif ratio < 0.75:
            key = "Moderate (50-75%)"
        elif ratio < 0.9:
            key = "High (75-90%)"
        else:
            key = "Severe (>90%)"

        buckets[key]["lats"] += [fn["y"], tn["y"], None]
        buckets[key]["lons"] += [fn["x"], tn["x"], None]
        buckets[key]["texts"].append(
            f"{road['from']}→{road['to']}<br>Flow: {flow:.0f}<br>"
            f"Cap: {road['capacity']}<br>Congestion: {ratio:.0%}"
        )

    for label, b in buckets.items():
        if b["lats"]:
            fig.add_trace(go.Scattermapbox(
                lat=b["lats"], lon=b["lons"], mode="lines",
                line=dict(width=4, color=b["color"]),
                hovertext=b["texts"], hoverinfo="text",
                name=label,
            ))

    # Node markers
    for nid, data in nodes.items():
        fig.add_trace(go.Scattermapbox(
            lat=[data["y"]], lon=[data["x"]],
            mode="markers+text",
            marker=dict(size=8, color=_get_node_color(data)),
            text=[data["name"][:10]], textposition="top center",
            textfont=dict(size=7, color="white"),
            hovertext=f"<b>{data['name']}</b>", hoverinfo="text",
            showlegend=False,
        ))

    fig.update_layout(**_base_layout(
        f"Congestion Map ({time_period.title()})", zoom=10
    ))
    return fig
