"""Page 7: Algorithm Comparison Visualizer (Bonus)"""
import streamlit as st
import time
from src.models.graph import TransportationGraph
from src.algorithms.mst import kruskal_mst, prim_mst
from src.algorithms.shortest_path import dijkstra, dijkstra_time_dependent, astar_search
from src.algorithms.dynamic_programming import optimize_bus_allocation
from src.visualization.charts import plot_complexity_comparison
from src.data.cairo_data import get_all_nodes, TIME_PERIOD_LABELS
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Algorithm Comparison", page_icon="📊", layout="wide")
st.markdown("# 📊 Algorithm Comparison Visualizer")
st.markdown("Side-by-side performance comparison of all implemented algorithms.")

graph = TransportationGraph(include_potential=True)
nodes = get_all_nodes()
node_options = {f"{nid} - {d['name']}": nid for nid, d in sorted(nodes.items())}

# ── MST Comparison ──────────────────────────────────────────────────────────
st.markdown("## 🏗️ MST: Kruskal's vs Prim's")

pop_weights = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
kruskal_times, prim_times = [], []
kruskal_dists, prim_dists = [], []

for pw in pop_weights:
    kr = kruskal_mst(graph, pw, 0.4)
    pr = prim_mst(graph, "3", pw, 0.4)
    kruskal_times.append(kr["execution_time"] * 1000)
    prim_times.append(pr["execution_time"] * 1000)
    kruskal_dists.append(kr["total_distance"])
    prim_dists.append(pr["total_distance"])

fig = make_subplots(rows=1, cols=2,
                    subplot_titles=("Execution Time vs Population Weight",
                                    "MST Distance vs Population Weight"))
fig.add_trace(go.Scatter(x=pop_weights, y=kruskal_times, name="Kruskal's",
                          line=dict(color="#4FC3F7", width=3), mode="lines+markers"), row=1, col=1)
fig.add_trace(go.Scatter(x=pop_weights, y=prim_times, name="Prim's",
                          line=dict(color="#FF6B35", width=3), mode="lines+markers"), row=1, col=1)
fig.add_trace(go.Scatter(x=pop_weights, y=kruskal_dists, name="Kruskal's",
                          line=dict(color="#4FC3F7", width=3), mode="lines+markers",
                          showlegend=False), row=1, col=2)
fig.add_trace(go.Scatter(x=pop_weights, y=prim_dists, name="Prim's",
                          line=dict(color="#FF6B35", width=3), mode="lines+markers",
                          showlegend=False), row=1, col=2)
fig.update_layout(height=400, plot_bgcolor="#1a1a2e", paper_bgcolor="#16213e",
                  font=dict(color="white"))
fig.update_xaxes(title_text="Population Weight", color="white")
fig.update_yaxes(color="white")
st.plotly_chart(fig, use_container_width=True)

# ── Shortest Path Comparison ────────────────────────────────────────────────
st.markdown("## 🚗 Shortest Path: Dijkstra's vs A*")

source_label = st.selectbox("Source", list(node_options.keys()), index=0)
target_label = st.selectbox("Target", list(node_options.keys()), index=12)
source = node_options[source_label]
target = node_options[target_label]

results_by_period = {}
for period in ["morning", "afternoon", "evening", "night"]:
    dij = dijkstra_time_dependent(graph, source, target, period)
    ast = astar_search(graph, source, target, period, emergency=False)
    ast_em = astar_search(graph, source, target, period, emergency=True)
    results_by_period[period] = {"dijkstra": dij, "astar": ast, "astar_emergency": ast_em}

fig = make_subplots(rows=1, cols=3,
                    subplot_titles=("Nodes Explored", "Execution Time (ms)", "Travel Time (min)"))
periods = list(results_by_period.keys())
for algo, color, name in [("dijkstra", "#4FC3F7", "Dijkstra's"),
                            ("astar", "#FF6B35", "A*"),
                            ("astar_emergency", "#EF5350", "A* Emergency")]:
    explored = [results_by_period[p][algo]["nodes_explored"] for p in periods]
    times = [results_by_period[p][algo]["execution_time"]*1000 for p in periods]
    dists = [results_by_period[p][algo].get("path_distance", 0) for p in periods]
    fig.add_trace(go.Bar(x=periods, y=explored, name=name, marker_color=color), row=1, col=1)
    fig.add_trace(go.Bar(x=periods, y=times, name=name, marker_color=color, showlegend=False), row=1, col=2)
    fig.add_trace(go.Bar(x=periods, y=dists, name=name, marker_color=color, showlegend=False), row=1, col=3)

fig.update_layout(height=400, barmode="group",
                  plot_bgcolor="#1a1a2e", paper_bgcolor="#16213e", font=dict(color="white"))
fig.update_xaxes(color="white")
fig.update_yaxes(color="white")
st.plotly_chart(fig, use_container_width=True)

# ── All Algorithms Summary ──────────────────────────────────────────────────
st.markdown("## 📋 Complete Algorithm Summary")
st.markdown("""
| Algorithm | Category | Time Complexity | Space Complexity | Optimality |
|-----------|----------|----------------|-----------------|------------|
| **Kruskal's MST** | Greedy/MST | O(E log E) | O(V + E) | ✅ Optimal (with modifications) |
| **Prim's MST** | Greedy/MST | O(E log V) | O(V + E) | ✅ Optimal (with modifications) |
| **Dijkstra's** | Shortest Path | O((V+E) log V) | O(V) | ✅ Optimal (non-negative weights) |
| **A* Search** | Shortest Path | O((V+E) log V) | O(V) | ✅ Optimal (admissible heuristic) |
| **Bus Allocation DP** | Dynamic Prog. | O(R × B × M) | O(R × B) | ✅ Optimal |
| **Maintenance DP** | Dynamic Prog. | O(R × B²/G²) | O(R × B/G) | ✅ Optimal |
| **Signal Optimization** | Greedy | O(V × E) | O(V) | ⚠️ Locally optimal |
| **Emergency Preemption** | Greedy | O(P × A) | O(P) | ⚠️ Heuristic |
| **ML Prediction** | Machine Learning | O(N × T × D) | O(N × D) | N/A (prediction) |
""")
