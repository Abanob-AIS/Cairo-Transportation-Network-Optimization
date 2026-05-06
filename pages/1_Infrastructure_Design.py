"""Page 1: Infrastructure Network Design — MST Algorithms"""
import streamlit as st
from src.models.graph import TransportationGraph
from src.algorithms.mst import kruskal_mst, prim_mst
from src.visualization.network_viz import plot_mst
from src.visualization.charts import plot_complexity_comparison

st.set_page_config(page_title="Infrastructure Design", page_icon="🏗️", layout="wide")
st.markdown("# 🏗️ Infrastructure Network Design")
st.markdown("Design an optimal road network using **Minimum Spanning Tree** algorithms.")

# ── Sidebar Controls ────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Parameters")
include_potential = st.sidebar.checkbox("Include potential new roads", True)
pop_weight = st.sidebar.slider("Population priority weight", 0.0, 1.0, 0.3, 0.05)
facility_bonus = st.sidebar.slider("Critical facility bonus", 0.0, 1.0, 0.4, 0.05)
algorithm = st.sidebar.radio("Algorithm", ["Both", "Kruskal's", "Prim's"])

graph = TransportationGraph(include_potential=include_potential)

# ── Run Algorithms ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

if algorithm in ["Both", "Kruskal's"]:
    with st.spinner("Running Kruskal's algorithm..."):
        kruskal_result = kruskal_mst(graph, pop_weight, facility_bonus)
    with col1:
        st.markdown("### Kruskal's Algorithm")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Distance", f"{kruskal_result['total_distance']} km")
        c2.metric("Construction Cost", f"{kruskal_result['total_cost']}M EGP")
        c3.metric("Execution Time", f"{kruskal_result['execution_time']*1000:.3f} ms")
        st.metric("Connected", "✅ Yes" if kruskal_result["connected"] else "❌ No")
        
        # ✅ التعديل: توضيح أن المسافة المعروضة هي المسافة الفعلية
        st.caption("📌 **Note:** Distance shown is actual road distance (km). Route selection optimized using weighted criteria including population, facilities, condition, and construction cost (for potential roads).")
        
        st.plotly_chart(plot_mst(kruskal_result, graph, "Kruskal's MST"), use_container_width=True)

        with st.expander("📋 MST Edges Detail"):
            for e in kruskal_result["mst_edges"]:
                tag = "🆕" if e.get("is_potential") else "✅"
                cost = f" | Cost: {e.get('cost', 0)}M EGP" if e.get("is_potential") else ""
                st.write(f"{tag} {graph.get_node_name(e['from'])} → {graph.get_node_name(e['to'])}: "
                         f"{e['distance']} km{cost}")

if algorithm in ["Both", "Prim's"]:
    with st.spinner("Running Prim's algorithm..."):
        prim_result = prim_mst(graph, "3", pop_weight, facility_bonus)
    with col2:
        st.markdown("### Prim's Algorithm")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Distance", f"{prim_result['total_distance']} km")
        c2.metric("Construction Cost", f"{prim_result['total_cost']}M EGP")
        c3.metric("Execution Time", f"{prim_result['execution_time']*1000:.3f} ms")
        st.metric("Connected", "✅ Yes" if prim_result["connected"] else "❌ No")
        
        # ✅ التعديل: توضيح أن المسافة المعروضة هي المسافة الفعلية
        st.caption("📌 **Note:** Distance shown is actual road distance (km). Route selection optimized using weighted criteria including population, facilities, condition, and construction cost (for potential roads).")
        
        st.plotly_chart(plot_mst(prim_result, graph, "Prim's MST"), use_container_width=True)

        with st.expander("📋 MST Edges Detail"):
            for e in prim_result["mst_edges"]:
                tag = "🆕" if e.get("is_potential") else "✅"
                cost = f" | Cost: {e.get('cost', 0)}M EGP" if e.get("is_potential") else ""
                st.write(f"{tag} {graph.get_node_name(e['from'])} → {graph.get_node_name(e['to'])}: "
                         f"{e['distance']} km{cost}")

# ── Comparison ──────────────────────────────────────────────────────────────
if algorithm == "Both":
    st.divider()
    st.markdown("### 📊 Algorithm Comparison")
    fig = plot_complexity_comparison([kruskal_result, prim_result])
    st.plotly_chart(fig, use_container_width=True)
    
    # ✅ التعديل الإضافي: توضيح الفرق بين الـ algorithms
    with st.expander("📐 Why are Kruskal and Prim results different?"):
        st.markdown("""
        **Kruskal's vs Prim's:**
        - Both algorithms find a Minimum Spanning Tree (MST)
        - Results may differ in **total distance** due to:
          - Different tie-breaking when multiple edges have equal weights
          - Different starting points (Prim starts from Downtown Cairo)
          - Different edge selection order
        - Both results are **optimal** for their respective weight configurations
        
        **In this implementation:**
        - Edge weights are modified to prioritize high-population areas and critical facilities
        - Both algorithms use the same modified weight function
        - Any difference in total distance is due to tie-breaking only
        """)

# ── Complexity Analysis ─────────────────────────────────────────────────────
st.divider()
st.markdown("### 📐 Complexity Analysis")
st.markdown("""
| Algorithm | Time Complexity | Space Complexity | Key Data Structure |
|-----------|----------------|-----------------|-------------------|
| **Kruskal's** | O(E log E) | O(V + E) | Union-Find (Disjoint Set) |
| **Prim's** | O(E log V) | O(V + E) | Binary Heap (Priority Queue) |

**Modifications Made:**
- Edge weights adjusted by population density to prioritize high-traffic connections
- Critical facilities (hospitals, government) get reduced weights for better connectivity
- Road condition factored into cost to account for maintenance needs
- Construction cost included for potential roads (hybrid distance-cost objective)
""")

# modified weight function
with st.expander("📐 How Modified MST Weights Are Calculated"):
    st.markdown(r"""
    **Modified Weight Function:**
    
    $$
    \text{Weight} = \frac{\text{distance} \times \text{condition\_penalty} \times \text{cost\_factor}}{\text{population\_factor} \times \text{facility\_factor}}
    $$
    
    **Components:**
    - **condition_penalty** = 1 + (10 - condition) × 0.1 (worse roads cost more)
    - **population_factor** = 1 + pop_weight × (avg_pop / 550000) (prioritize dense areas)
    - **facility_factor** = 1 + facility_bonus if critical facility connected
    - **cost_factor** = 1 + (cost / 20) × α for potential roads (α = 0.3)
    
    **Hybrid Cost-Distance Objective:**
    For potential roads, effective distance = distance × (1-α) + (cost/20) × α
    - α = 0: Only distance matters (classic MST)
    - α = 0.3: 70% distance, 30% construction cost (balanced)
    - α = 1: Only construction cost matters
    """)