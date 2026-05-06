"""Page 4: Public Transit Optimization — Dynamic Programming"""
import streamlit as st
import math
from src.algorithms.dynamic_programming import (
    optimize_public_transit_scheduling, road_maintenance_allocation, MemoizedRoutePlanner, analyze_transfer_points
)
from src.models.graph import TransportationGraph
from src.visualization.charts import plot_bus_allocation, plot_maintenance_allocation
from src.data.cairo_data import BUS_ROUTES, METRO_LINES, EXISTING_ROADS, get_all_nodes

st.set_page_config(page_title="Public Transit", page_icon="🚌", layout="wide")
st.markdown("# 🚌 Public Transit Optimization")
st.markdown("Optimize **Bus + Metro** capacity allocation and road maintenance using **Dynamic Programming**.")

graph = TransportationGraph()
nodes = get_all_nodes()

tab1, tab2, tab3 = st.tabs(["🚌🚇 Transit Scheduling", "🔧 Road Maintenance", "💾 Memoized Routing"])


# =============================================================================
# TAB 1: Transit Scheduling
# =============================================================================
with tab1:
    st.markdown("### 🚌🚇 Optimal Public Transit Scheduling")
    st.markdown("Using DP to maximize total passengers served across **Bus routes + Metro lines**.")
    st.caption("1 Metro train = 10 capacity units | 1 Bus = 1 capacity unit")
    
    # ✅ التعديل 2 و 3: توضيح Bus units و Metro multiplier
    st.caption("📌 **Note:** Bus counts represent abstract capacity units for optimization. 1 unit ≈ 2-3 actual buses in peak hour operations.")
    st.caption("🚇 **Metro efficiency assumption:** 1 train = 10 bus units based on capacity ratio (≈2000 passengers/train vs ≈200 passengers/bus)")

    # Current capacity
    bus_units = sum(r["buses"] for r in BUS_ROUTES.values())
    metro_units = len(METRO_LINES) * 5 * 10
    default_total = bus_units + metro_units

    total_cap = st.slider("Total Capacity Units", 50, 600, default_total, 10)
    max_per = st.slider("Max Units Per Line", 10, 80, 40, 5)

    with st.spinner("Optimizing transit scheduling..."):
        result = optimize_public_transit_scheduling(
            BUS_ROUTES, METRO_LINES, total_cap, max_per
        )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Optimal Passengers", f"{result['total_passengers_optimal']:,}")
    col2.metric("Current Passengers", f"{result['total_passengers_current']:,}")
    col3.metric("Improvement", f"{result['improvement_pct']}%",
                delta=f"{result['improvement_pct']:+.2f}%")
    col4.metric("Lines Optimized",
                f"{result['num_bus_routes']} Bus + {result['num_metro_lines']} Metro")

    # Split allocation into Bus and Metro for display
    bus_alloc = {k: v for k, v in result["optimal_allocation"].items() if v["type"] == "Bus"}
    metro_alloc = {k: v for k, v in result["optimal_allocation"].items() if v["type"] == "Metro"}

    st.plotly_chart(plot_bus_allocation(result["optimal_allocation"]), use_container_width=True)

    with st.expander("🚌 Bus Route Allocation Detail"):
        for rid, data in bus_alloc.items():
            orig = BUS_ROUTES.get(rid, {}).get("buses", 0)
            diff = data["buses"] - orig
            arrow = "🔺" if diff > 0 else "🔻" if diff < 0 else "➡️"
            st.write(f"{arrow} **{rid}** ({' → '.join(data['stops'])}): "
                    f"{orig} → {data['buses']} buses | "
                    f"Passengers: {data['passengers_served']:,}")

    with st.expander("🚇 Metro Line Allocation Detail"):
        for mid, data in metro_alloc.items():
            st.write(f"🚇 **{mid}** ({' → '.join(data['stops'][:4])}...): "
                    f"{data['trains']} trains ({data['units']} units) | "
                    f"Passengers: {data['passengers_served']:,} | "
                    f"Demand: {data['potential_demand']:,}")

    st.info(f"**Complexity:** {result['complexity']} | "
            f"**Execution:** {result['execution_time']*1000:.2f} ms")

    # Transfer Points Analysis
    st.divider()
    st.markdown("### 🔄 Multi-Modal Transfer Points Analysis")
    st.markdown("Identifying nodes where **Metro** and **Bus** lines intersect — "
                "critical hubs for seamless passenger transfers.")

    hubs = analyze_transfer_points(BUS_ROUTES, METRO_LINES, nodes)

    col_main, col_side = st.columns([3, 1])

    with col_side:
        st.metric("Multi-Modal Hubs", len(hubs))
        if hubs:
            avg_score = sum(h["hub_complexity_score"] for h in hubs) / len(hubs)
            st.metric("Avg Complexity", f"{avg_score:.1f}")

    with col_main:
        if not hubs:
            st.warning("No multi-modal transfer hubs found in the current data.")
        else:
            for hub in hubs:
                metros_str = ", ".join(hub["connecting_metro"])
                buses_str = ", ".join(hub["connecting_buses"])
                st.info(
                    f"🏙️ **{hub['name']}** (ID: `{hub['node_id']}`) — "
                    f"Complexity Score: **{hub['hub_complexity_score']}**\n\n"
                    f"🚇 Metro: {metros_str}  \n"
                    f"🚌 Bus: {buses_str}"
                )

    st.success(
        "**Optimization Strategy:** While explicit time-synchronization is constrained "
        "by fixed Metro schedules, our Dynamic Programming algorithm naturally optimizes "
        "these transfer points by allocating maximum capacity (Buses) to intersecting "
        "high-demand nodes, reducing passenger wait times at multi-modal hubs."
    )


# =============================================================================
# TAB 2: Road Maintenance (WITH ALL IMPROVEMENTS)
# =============================================================================
with tab2:
    st.markdown("### 🔧 Road Maintenance Budget Allocation")
    st.markdown("Using DP to optimally distribute maintenance budget across roads.")
    
    # Helper function for impact calculation
    def calculate_impact(road):
        """Calculate impact score for a road (higher = more critical)"""
        condition_gap = 10 - road["condition"]
        return condition_gap * road["distance"] * (road["capacity"] / 1000)
    
    # Sliders
    col_budget, col_gran = st.columns(2)
    with col_budget:
        budget = st.slider("Total Budget (Million EGP)", 100, 2000, 600, 50)
    with col_gran:
        granularity = st.selectbox("Investment Granularity (M EGP)", [25, 50, 100], index=1)

    with st.spinner("Optimizing maintenance budget..."):
        maint_result = road_maintenance_allocation(budget, granularity)

    # Metrics with Unit Explanation
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Improvement Score", f"{maint_result['total_improvement']:.1f}")
        st.caption("📊 **Weighted Index** (0-1000+) = Σ [condition_gap × distance × (capacity/1000)]")
        st.caption("Higher score = more critical roads prioritized")
    
    with col2:
        st.metric("Budget Used", f"{maint_result['budget_used']}M / {budget}M EGP")
        percent_used = (maint_result['budget_used'] / budget) * 100 if budget > 0 else 0
        st.progress(min(percent_used / 100, 1.0))
        st.caption(f"{percent_used:.0f}% of budget allocated")

    # Allocation Chart
    st.plotly_chart(plot_maintenance_allocation(maint_result["allocations"]), use_container_width=True)

    # Before/After Condition Comparison
    if maint_result["allocations"]:
        with st.expander("📈 Before / After Road Condition Comparison"):
            st.markdown("**Investment impact on road condition:**")
            for road_key, data in maint_result["allocations"].items():
                old_cond = data["current_condition"]
                # Estimate new condition based on improvement (diminishing returns)
                investment_units = data["investment_million_egp"] / granularity
                # Max 2 condition points improvement per 50M
                improvement_per_unit = 2 * (1 - math.exp(-0.5 * investment_units))
                new_cond = min(10, old_cond + improvement_per_unit)
                improvement_gain = new_cond - old_cond
                
                # Visual bars
                old_bar = "🟥" * (10 - old_cond) + "🟩" * old_cond
                new_bar = "🟥" * (10 - int(new_cond)) + "🟩" * int(new_cond)
                
                st.write(f"**{data['road']}**")
                st.write(f"Before: {old_cond}/10 {old_bar}")
                st.write(f"After:  {new_cond:.0f}/10 {new_bar} (+{improvement_gain:.1f})")
                st.write(f"💰 Investment: {data['investment_million_egp']}M EGP")
                st.divider()

    # Priority Roads by Impact
    st.markdown("#### 🚨 Priority Roads (Highest Impact First)")
    
    sorted_by_impact = sorted(EXISTING_ROADS, key=calculate_impact, reverse=True)[:5]
    
    for r in sorted_by_impact:
        from_name = nodes.get(r["from"], {}).get("name", r["from"])
        to_name = nodes.get(r["to"], {}).get("name", r["to"])
        impact = calculate_impact(r)
        condition_gap = 10 - r["condition"]
        bar = "🟥" * condition_gap + "🟩" * r["condition"]
        
        road_key = f"{r['from']}-{r['to']}"
        funded = road_key in maint_result["allocations"]
        funded_icon = "✅" if funded else "⏳"
        
        st.write(f"{funded_icon} **{from_name} → {to_name}**: Condition {r['condition']}/10 {bar}")
        st.caption(f"Impact Score: {impact:.1f} | Gap: {condition_gap} | Distance: {r['distance']}km | Capacity: {r['capacity']}")

    # Diminishing Returns Warning
    if maint_result["budget_used"] == budget and budget > 100:
        if maint_result["allocations"]:
            last_allocation = list(maint_result["allocations"].values())[-1]
            last_investment = last_allocation["investment_million_egp"]
            last_improvement = last_allocation["improvement_score"]
            if last_investment > 0 and last_improvement / last_investment < 0.05:
                st.warning(f"⚠️ **Diminishing Returns**: Last {granularity}M gave only {last_improvement:.1f} improvement. Consider reducing budget.")

    st.info(f"⚡ **Execution:** {maint_result['execution_time']*1000:.2f} ms")

    # Formula Explanation
    with st.expander("📐 How Improvement Score is Calculated"):
        st.markdown(r"""
        **Formula:**
        
        $$
        \text{Improvement} = \text{condition\_gap} \times \text{distance} \times \frac{\text{capacity}}{1000} \times \left(1 - e^{-0.5 \times \frac{\text{investment}}{\text{granularity}}}\right)
        $$
        
        **Variables:**
        - **condition_gap** = 10 − current_condition (higher = worse road)
        - **distance** = Road length in km (longer roads need more investment)
        - **capacity** = Vehicles per hour (busier roads get priority)
        - **investment** = Amount spent in million EGP
        - **granularity** = Investment step size (25, 50, or 100 M EGP)
        
        **Diminishing Returns:**
        - First investment unit gives ~39% of max possible improvement
        - Second gives ~24%
        - Third gives ~14%
        - Returns decrease exponentially
        
        **Example:** A road with condition 5, distance 15km, capacity 3000
        - Max improvement = 5 × 15 × 3 = 225
        - First 50M gives: 225 × (1 − e⁻⁰·⁵) = 225 × 0.393 = 88.5
        """)

    # Complexity Explanation
    with st.expander("📐 Why O(R × (B/G)²)?"):
        st.markdown(f"""
        **Time Complexity Explanation:**
        
        - **R** = Number of roads ({len(EXISTING_ROADS)})
        - **B** = Total budget in million EGP ({budget})
        - **G** = Granularity ({granularity} M EGP)
        - **B/G** = Number of budget units ({budget // granularity} units)
        
        **Why squared?** For each road (R) and each budget unit (B/G), 
        the algorithm tries all possible investment levels `k` from 1 to the current budget unit `b`.
        
        This creates a nested loop: `O(R × (B/G) × (B/G))` = `O(R × (B/G)²)`
        
        **Example with current values:**
        - R = {len(EXISTING_ROADS)}
        - B/G = {budget // granularity}
        - Operations ≈ {len(EXISTING_ROADS)} × {budget // granularity} × {budget // granularity} = {len(EXISTING_ROADS) * (budget // granularity) ** 2:,} operations
        - Result: Very fast (< 1ms)
        
        **Space Complexity:** O(R × B/G) for storing DP table
        """)


# =============================================================================
# TAB 3: Memoized Routing
# =============================================================================
with tab3:
    st.markdown("### 💾 Memoized Route Planning")
    st.markdown("Cache shortest paths to avoid redundant computations.")

    planner = MemoizedRoutePlanner(graph)

    queries = [
        ("1", "3"), ("3", "4"), ("1", "3"), ("5", "13"),
        ("1", "3"), ("3", "4"), ("7", "13"), ("5", "13"),
    ]

    st.markdown("**Running 8 queries (with repeated pairs to show cache hits):**")
    for i, (s, t) in enumerate(queries):
        r = planner.get_shortest_path(s, t)
        source_name = graph.get_node_name(s)
        target_name = graph.get_node_name(t)
        dist = r.get("path_distance", "N/A")
        if isinstance(dist, float):
            dist = f"{dist:.1f} km"
        st.write(f"Query {i+1}: {source_name} → {target_name} = {dist}")

    stats = planner.get_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("Cache Size", stats["cache_size"])
    col2.metric("Cache Hits", stats["hits"])
    col3.metric("Hit Rate", f"{stats['hit_rate']}%")
    
    with st.expander("💡 How Memoization Works"):
        st.markdown("""
        - First request for a (source, target, time) pair: Compute and cache
        - Subsequent requests: Return cached result instantly
        - Cache size limited to 1000 entries to prevent memory issues
        - Hit rate shows percentage of requests served from cache
        """)


# =============================================================================
# COMPLEXITY ANALYSIS (Footer)
# =============================================================================
st.divider()
st.markdown("""### 📐 Complexity Analysis

| Problem | State Space | Time Complexity | Space Complexity |
|---------|------------|-----------------|------------------|
| **Transit Scheduling** | dp[lines][capacity] | O(L × C × M) | O(L × C) |
| **Road Maintenance** | dp[roads][budget] | O(R × (B/G)²) | O(R × B/G) |
| **Memoized Routing** | cache[(s,t,time)] | O(1) cached / O((V+E)logV) new | O(V²) |

**Optimal Substructure:** Both transit scheduling and maintenance are variants of the
bounded knapsack problem — optimal solution for N items includes optimal solution for N-1.

**Metro Integration:** Metro trains are modeled as 10× capacity units with 1.2× efficiency
multiplier, reflecting their higher throughput compared to individual bus routes.
""")