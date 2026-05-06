"""Page 3: Emergency Response Planning — A* Search"""
import streamlit as st
from src.models.graph import TransportationGraph
from src.algorithms.shortest_path import astar_search, dijkstra_time_dependent, compare_algorithms
from src.algorithms.greedy import emergency_vehicle_preemption
from src.visualization.network_viz import plot_emergency_route, plot_path
from src.visualization.charts import plot_complexity_comparison, plot_algorithm_race
from src.data.cairo_data import get_all_nodes, FACILITIES, TIME_PERIOD_LABELS

st.set_page_config(page_title="Emergency Response", page_icon="🚑", layout="wide")
st.markdown("# 🚑 Emergency Response Planning")
st.markdown("Route emergency vehicles using **A* search** with signal preemption.")

graph = TransportationGraph()
nodes = get_all_nodes()
node_options = {f"{nid} - {d['name']}": nid for nid, d in sorted(nodes.items())}

# Medical facilities for quick selection
medical = {fid: d for fid, d in FACILITIES.items() if d["type"] == "Medical"}

st.sidebar.header("🚨 Emergency Setup")
source_label = st.sidebar.selectbox("Emergency Origin", list(node_options.keys()), index=6)
# Default target to nearest hospital
hospital_options = {f"{fid} - {d['name']}": fid for fid, d in medical.items()}
target_label = st.sidebar.selectbox("Destination (Hospital)", list(hospital_options.keys()))
source = node_options[source_label]
target = hospital_options[target_label]
time_period = st.sidebar.selectbox("Time of Day", list(TIME_PERIOD_LABELS.keys()),
                                    format_func=lambda x: TIME_PERIOD_LABELS[x])

# ── Run Algorithms ──────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🚨 Emergency Route", "⚡ A* vs Dijkstra", "🚦 Signal Preemption"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🚑 A* Emergency Route")
        astar_em = astar_search(graph, source, target, time_period, emergency=True)
        if astar_em["path"]:
            st.metric("Travel Time", f"{astar_em['path_distance']:.1f} min")
            st.metric("Nodes Explored", astar_em["nodes_explored"])
            st.metric("Execution Time", f"{astar_em['execution_time']*1000:.3f} ms")
            path_names = " → ".join(graph.get_node_name(n) for n in astar_em["path"])
            st.success(f"**Emergency Route:** {path_names}")
            st.plotly_chart(plot_emergency_route(astar_em["path"], graph, "🚑 Emergency Route"),
                          use_container_width=True)
        else:
            st.error("No route found!")

    with col2:
        st.markdown("### 🚗 Normal A* Route")
        astar_normal = astar_search(graph, source, target, time_period, emergency=False)
        if astar_normal["path"]:
            st.metric("Travel Time", f"{astar_normal['path_distance']:.1f} min")
            st.metric("Nodes Explored", astar_normal["nodes_explored"])
            st.metric("Execution Time", f"{astar_normal['execution_time']*1000:.3f} ms")
            path_names = " → ".join(graph.get_node_name(n) for n in astar_normal["path"])
            st.info(f"**Normal Route:** {path_names}")
            st.plotly_chart(plot_path(astar_normal["path"], graph, "Normal Route", "#FFB74D"),
                          use_container_width=True)
        else:
            st.error("No route found!")

    if astar_em["path"] and astar_normal["path"]:
        improvement = ((astar_normal["path_distance"] - astar_em["path_distance"])
                      / astar_normal["path_distance"] * 100)
        st.metric("⏱️ Time Saved with Emergency Preemption", f"{improvement:.1f}%")

with tab2:
    st.markdown("### ⚡ A* vs Dijkstra's Comparison")
    comparison = compare_algorithms(graph, source, target, time_period)

    col1, col2, col3 = st.columns(3)
    dij = comparison["dijkstra"]
    ast = comparison["astar"]
    col1.metric("Dijkstra Nodes Explored", dij["nodes_explored"])
    col2.metric("A* Nodes Explored", ast["nodes_explored"])
    saved = dij["nodes_explored"] - ast["nodes_explored"]
    col3.metric("Nodes Saved by A*", saved, delta=f"{saved} fewer")

    fig = plot_algorithm_race(dij, ast, graph)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **Why A* is faster:** The Haversine heuristic guides search toward the target,
    avoiding exploration of nodes in the opposite direction. This is especially
    effective in Cairo's geographic layout where the heuristic closely approximates
    actual road distances.
    """)

with tab3:
    st.markdown("### 🚦 Emergency Signal Preemption")
    if astar_em["path"]:
        preemption = emergency_vehicle_preemption(astar_em["path"], time_period)
        st.metric("Total Delay Saved", f"{preemption['total_delay_saved_min']} minutes")
        st.metric("Intersections Preempted", preemption["num_intersections_preempted"])
        
        for p in preemption["preemptions"]:
            st.write(f"🚦 **{p['name']}**: Normal wait {p['normal_wait_sec']:.0f}s → "
                    f"Preempted {p['preempted_wait_sec']:.0f}s "
                    f"(saved {p['delay_saved_sec']:.0f}s)")

# ── Complexity ──────────────────────────────────────────────────────────────
st.divider()
st.markdown("""### 📐 Complexity Analysis
| Algorithm | Time | Space | Heuristic |
|-----------|------|-------|-----------|
| **Dijkstra's** | O((V+E) log V) | O(V) | None (exhaustive) |
| **A*** | O((V+E) log V) worst | O(V) | Haversine (admissible) |

**A* Admissibility:** Haversine distance ≤ actual road distance, guaranteeing optimal paths.  
**Emergency Preemption:** 0.6× travel time factor models priority signal changes.
""")
