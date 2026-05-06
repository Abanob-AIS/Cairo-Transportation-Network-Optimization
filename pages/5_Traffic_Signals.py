"""Page 5: Traffic Signal Optimization — Greedy Algorithms"""
import streamlit as st
from src.algorithms.greedy import optimize_traffic_signals
from src.visualization.charts import plot_signal_timing
from src.data.cairo_data import TIME_PERIOD_LABELS, get_all_nodes

st.set_page_config(page_title="Traffic Signals", page_icon="🚦", layout="wide")
st.markdown("# 🚦 Traffic Signal Optimization")
st.markdown("Optimize signal timing using a **Greedy** approach — proportional to traffic flow.")

nodes = get_all_nodes()

st.sidebar.header("⚙️ Signal Parameters")
time_period = st.sidebar.selectbox("Time of Day", list(TIME_PERIOD_LABELS.keys()),
                                    format_func=lambda x: TIME_PERIOD_LABELS[x])
cycle_length = st.sidebar.slider("Cycle Length (seconds)", 60, 180, 120, 10)

# ── Run Optimization ────────────────────────────────────────────────────────
result = optimize_traffic_signals(time_period, cycle_length)

col1, col2, col3 = st.columns(3)
col1.metric("Intersections Optimized", result["num_intersections"])
col2.metric("Total Throughput", f"{result['total_throughput']:,.0f} veh/h")
col3.metric("Congested Intersections", len(result["congested_intersections"]))

st.divider()

# ── Intersection Details ────────────────────────────────────────────────────
st.markdown("### 🚦 Signal Plans by Intersection")

for nid, data in sorted(result["intersections"].items(),
                         key=lambda x: x[1]["total_throughput"], reverse=True):
    with st.expander(f"🚦 {data['name']} ({data['num_approaches']} approaches) — "
                     f"Throughput: {data['total_throughput']:.0f} veh/h"):
        col1, col2 = st.columns([1, 1])
        with col1:
            for s in data["signal_plan"]:
                from_name = nodes.get(s["from"], {}).get("name", s["from"])
                cong = s["congestion_before"]
                cong_icon = "🟢" if cong < 0.5 else "🟡" if cong < 0.75 else "🟠" if cong < 0.9 else "🔴"
                st.write(f"{cong_icon} From **{from_name}**: 🟢 {s['green_time']}s | "
                        f"Flow: {s['flow']:.0f} | Congestion: {cong:.0%}")
        with col2:
            fig = plot_signal_timing(data["signal_plan"], data["name"])
            st.plotly_chart(fig, use_container_width=True)

# ── Optimality Analysis ─────────────────────────────────────────────────────
st.divider()
st.markdown("### 📐 Optimality Analysis")
st.markdown(f"*{result['optimality_note']}*")

st.markdown("""
#### When Greedy is Optimal ✅
- **Isolated intersections** with independent traffic streams
- **Proportional allocation** when all approaches have similar importance
- **Real-time response** where computation speed matters more than global optimality

#### When Greedy is Suboptimal ❌
- **Coordinated signal corridors** (e.g., ring road signals should be synchronized)
- **Network effects** where one intersection's timing affects neighbors
- **Asymmetric priorities** (e.g., bus rapid transit lanes need fixed minimum green)

#### Complexity
| Aspect | Value |
|--------|-------|
| **Time Complexity** | O(V × E) per intersection |
| **Space Complexity** | O(V) |
| **Greedy Choice** | Allocate green time ∝ traffic flow |
| **Execution Time** | {exec_time:.3f} ms |
""".format(exec_time=result["execution_time"]*1000))
