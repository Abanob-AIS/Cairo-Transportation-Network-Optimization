"""Page 2: Traffic Flow Optimization — Dijkstra's Algorithm"""
import streamlit as st
from src.models.graph import TransportationGraph
from src.algorithms.shortest_path import dijkstra, dijkstra_time_dependent
from src.visualization.network_viz import plot_path, plot_congestion_map
from src.visualization.charts import plot_traffic_flow
from src.data.cairo_data import TRAFFIC_FLOW, EXISTING_ROADS, TIME_PERIOD_LABELS, get_all_nodes

st.set_page_config(page_title="Traffic Optimization", page_icon="🚗", layout="wide")
st.markdown("# 🚗 Traffic Flow Optimization")
st.markdown("Find optimal routes using **Dijkstra's algorithm** with time-dependent traffic modeling.")

graph = TransportationGraph()
nodes = get_all_nodes()
node_options = {f"{nid} - {d['name']}": nid for nid, d in sorted(nodes.items())}

# ── Controls ────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Route Planning")
source_label = st.sidebar.selectbox("From", list(node_options.keys()), index=2)  # Downtown
target_label = st.sidebar.selectbox("To", list(node_options.keys()), index=3)   # New Cairo
source = node_options[source_label]
target = node_options[target_label]
time_period = st.sidebar.selectbox("Time of Day", list(TIME_PERIOD_LABELS.keys()),
                                    format_func=lambda x: TIME_PERIOD_LABELS[x])

# ── Run Dijkstra ────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🗺️ Route Planning", "🌡️ Congestion Map", "📊 Traffic Analysis"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Standard Dijkstra (Distance)")
        result_dist = dijkstra(graph, source, target, weight_type="distance")
        if result_dist["path"]:
            st.metric("Path Distance", f"{result_dist['path_distance']:.1f} km")
            st.metric("Nodes Explored", result_dist["nodes_explored"])
            st.metric("Time", f"{result_dist['execution_time']*1000:.3f} ms")
            path_names = " → ".join(graph.get_node_name(n) for n in result_dist["path"])
            st.info(f"**Route:** {path_names}")
            st.plotly_chart(plot_path(result_dist["path"], graph, "Shortest Distance Route", "#00E5FF"),
                          use_container_width=True)
        else:
            st.error("No path found!")

    with col2:
        st.markdown(f"### Time-Dependent ({time_period.title()})")
        with st.spinner("Computing time-dependent route..."):
            result_time = dijkstra_time_dependent(graph, source, target, time_period)
        if result_time["path"]:
            st.metric("Travel Time", f"{result_time['path_distance']:.1f} min")
            st.metric("Nodes Explored", result_time["nodes_explored"])
            st.metric("Time", f"{result_time['execution_time']*1000:.3f} ms")
            path_names = " → ".join(graph.get_node_name(n) for n in result_time["path"])
            st.info(f"**Route:** {path_names}")
            st.plotly_chart(plot_path(result_time["path"], graph,
                                     f"Fastest Route ({time_period.title()})", "#FF6B35"),
                          use_container_width=True)
        else:
            st.warning("⚠️ No valid path found between these locations due to network constraints.")

    # ── Road Closure Rerouting ──────────────────────────────────────────────
    st.divider()
    st.markdown("### 🚧 Alternate Route (Road Closures)")
    st.markdown("Simulate road closures and find alternate routes.")
    
    from src.algorithms.shortest_path import dijkstra_with_closures
    
    # Let user select roads to close
    road_labels = [f"{r['from']} → {r['to']} ({graph.get_node_name(r['from'])} → {graph.get_node_name(r['to'])})"
                   for r in EXISTING_ROADS]
    closed_selection = st.multiselect("Select roads to close:", road_labels)
    
    closed_edges = []
    for sel in closed_selection:
        parts = sel.split(" → ")
        from_id = parts[0].strip()
        to_id = parts[1].split(" (")[0].strip()
        closed_edges.append((from_id, to_id))
    
    if closed_edges:
        with st.spinner("Rerouting around closures..."):
            closure_result = dijkstra_with_closures(graph, source, target, closed_edges, time_period)
        
        if closure_result["path"]:
            path_names = " → ".join(graph.get_node_name(n) for n in closure_result["path"])
            st.success(f"**Alternate Route:** {path_names}")
            st.metric("Travel Time", f"{closure_result['path_distance']:.1f} min")
            st.plotly_chart(plot_path(closure_result["path"], graph,
                                     "🚧 Alternate Route", "#FFC107"),
                          use_container_width=True)
        else:
            st.warning("⚠️ No valid path found between these locations due to network constraints or closures.")

    # Compare across all time periods
    st.divider()
    st.markdown("### ⏰ Route Comparison Across Time Periods")
    periods = ["morning", "afternoon", "evening", "night"]
    period_results = []
    for p in periods:
        r = dijkstra_time_dependent(graph, source, target, p)
        period_results.append(r)
    
    cols = st.columns(4)
    for i, (p, r) in enumerate(zip(periods, period_results)):
        with cols[i]:
            st.metric(TIME_PERIOD_LABELS[p].split("(")[0].strip(),
                     f"{r['path_distance']:.1f} min" if r["path"] else "N/A")

with tab2:
    st.markdown(f"### 🌡️ Network Congestion — {TIME_PERIOD_LABELS[time_period]}")
    st.markdown("🟢 Low (<50%) &nbsp; 🟡 Moderate (50-75%) &nbsp; 🟠 High (75-90%) &nbsp; 🔴 Severe (>90%)")
    fig = plot_congestion_map(graph, time_period)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### 📊 Traffic Flow Patterns")
    # Show traffic for selected roads
    for (from_id, to_id), flow_data in list(TRAFFIC_FLOW.items())[:10]:
        from_name = nodes.get(from_id, {}).get("name", from_id)
        to_name = nodes.get(to_id, {}).get("name", to_id)
        flows = [flow_data["morning"], flow_data["afternoon"], flow_data["evening"], flow_data["night"]]
        st.plotly_chart(plot_traffic_flow(flows, f"{from_name} → {to_name}"), use_container_width=True)

# ── Complexity ──────────────────────────────────────────────────────────────
st.divider()
st.markdown("""### 📐 Complexity Analysis
| Variant | Time | Space | Notes |
|---------|------|-------|-------|
| **Standard Dijkstra** | O((V+E) log V) | O(V) | Binary heap, distance weights |
| **Time-Dependent** | O((V+E) log V) | O(V) | BPR congestion function per edge |

**BPR Function:** `travel_time = free_flow_time × (1 + 0.15 × (volume/capacity)⁴)`
""")
