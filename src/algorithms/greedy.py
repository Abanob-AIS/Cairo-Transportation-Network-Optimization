"""
Greedy Algorithms
===================
Traffic signal optimization and emergency vehicle preemption.
"""
import time
from src.data.cairo_data import TRAFFIC_FLOW, EXISTING_ROADS, get_all_nodes


def optimize_traffic_signals(time_period="morning", cycle_length=120):
    """
    Greedy traffic signal optimization at Cairo intersections.
    
    Strategy: At each intersection, allocate green time proportional
    to incoming traffic flow (greedy choice: highest flow gets most green time).
    
    Algorithm:
        1. For each intersection node, find all incoming roads
        2. Get traffic flow for current time period
        3. Greedily allocate green time proportional to flow
        4. Ensure minimum 10s green for each approach
    
    Optimality Analysis:
        - OPTIMAL when traffic flows are stable and predictable
        - SUBOPTIMAL when there are cascading effects between intersections
        - Works well for isolated intersections, less so for coordinated signals
    
    Time Complexity: O(V * E) where V = intersections, E = roads per intersection
    Space Complexity: O(V)
    """
    start_time = time.perf_counter()
    nodes = get_all_nodes()
    min_green = 10  # Minimum green time per approach (seconds)
    yellow = 3      # Yellow time per phase

    # Build intersection data: for each node, find incoming roads
    intersections = {}
    for node_id in nodes:
        incoming = []
        for road in EXISTING_ROADS:
            if road["to"] == node_id:
                flow_key = (road["from"], road["to"])
                flow_data = TRAFFIC_FLOW.get(flow_key, {})
                flow = flow_data.get(time_period, road["capacity"] * 0.5)
                incoming.append({
                    "from": road["from"],
                    "flow": flow,
                    "capacity": road["capacity"],
                    "congestion": flow / road["capacity"],
                })
            elif road["from"] == node_id:
                # ASSUMPTION: In the absence of explicit reverse-direction flow data,
                # we estimate reverse flow as 70% of the forward direction's measured flow.
                # This models typical residential-to-business commuting patterns in Cairo
                # where morning flow toward business districts is dominant, and the
                # reverse direction carries roughly 70% of that volume. The 0.3 default
                # capacity multiplier handles the case where no flow data exists at all.
                flow_key = (road["from"], road["to"])
                rev_key = (road["to"], road["from"])
                flow_data = TRAFFIC_FLOW.get(flow_key) or TRAFFIC_FLOW.get(rev_key, {})
                flow = flow_data.get(time_period, road["capacity"] * 0.3)
                incoming.append({
                    "from": road["to"],
                    "flow": flow * 0.7,
                    "capacity": road["capacity"],
                    "congestion": flow * 0.7 / road["capacity"],
                })

        if len(incoming) < 2:
            continue

        # Greedy allocation: proportional to flow
        total_flow = sum(a["flow"] for a in incoming)
        if total_flow == 0:
            continue

        num_phases = len(incoming)
        available_green = cycle_length - num_phases * yellow
        if available_green < num_phases * min_green:
            available_green = num_phases * min_green

        signal_plan = []
        for approach in incoming:
            proportion = approach["flow"] / total_flow
            green = max(min_green, int(available_green * proportion))
            signal_plan.append({
                "from": approach["from"],
                "green_time": green,
                "flow": approach["flow"],
                "capacity": approach["capacity"],
                "congestion_before": round(approach["congestion"], 3),
                "throughput": min(approach["flow"], approach["capacity"] * green / cycle_length),
            })

        # Normalize to fit cycle
        total_assigned = sum(s["green_time"] for s in signal_plan) + num_phases * yellow
        if total_assigned > cycle_length:
            scale = (cycle_length - num_phases * yellow) / sum(s["green_time"] for s in signal_plan)
            for s in signal_plan:
                s["green_time"] = max(min_green, int(s["green_time"] * scale))

        intersections[node_id] = {
            "name": nodes[node_id]["name"],
            "num_approaches": num_phases,
            "signal_plan": signal_plan,
            "cycle_length": cycle_length,
            "total_throughput": sum(s["throughput"] for s in signal_plan),
        }

    # Analyze optimality
    total_throughput = sum(i["total_throughput"] for i in intersections.values())
    congested = [nid for nid, data in intersections.items()
                 if any(s["congestion_before"] > 0.85 for s in data["signal_plan"])]

    return {
        "intersections": intersections,
        "total_throughput": round(total_throughput, 0),
        "num_intersections": len(intersections),
        "congested_intersections": congested,
        "time_period": time_period,
        "cycle_length": cycle_length,
        "execution_time": time.perf_counter() - start_time,
        "algorithm": "Greedy (Traffic Signals)",
        "optimality_note": (
            "Greedy is optimal for isolated intersections but may be suboptimal "
            "when signal coordination between adjacent intersections matters."
        ),
    }


def emergency_vehicle_preemption(emergency_path, time_period="morning", cycle_length=120):
    """
    Priority-based emergency vehicle preemption at intersections.
    
    Greedy strategy: For each intersection on the emergency route,
    preempt the current signal phase and give full green to the
    emergency vehicle's approach.
    
    The normal wait time is estimated dynamically based on:
    - Intersection degree (more approaches → longer average wait)
    - Congestion level from traffic flow data (heavier traffic → longer queues)
    
    Algorithm:
        1. For each intersection along the emergency path
        2. Estimate normal wait from degree and congestion
        3. Preempt signal: emergency vehicle waits only ~5s for phase change
        4. Greedy choice: always preempt (locally optimal per intersection)
    
    Time Complexity: O(P * E) where P = path length, E = edges per node
    Space Complexity: O(P)
    """
    start_time = time.perf_counter()
    nodes = get_all_nodes()

    preemption_results = []
    total_delay_saved = 0

    for i in range(len(emergency_path) - 1):
        current = emergency_path[i]
        next_node = emergency_path[i + 1]
        node_data = nodes.get(next_node, {})

        # --- Dynamic normal_wait estimation ---
        # 1) Intersection degree: more connected roads → more signal phases → longer wait
        degree = 0
        total_congestion = 0.0
        for road in EXISTING_ROADS:
            if road["to"] == next_node or road["from"] == next_node:
                degree += 1
                # Check congestion on this approach
                flow_key = (road["from"], road["to"])
                rev_key = (road["to"], road["from"])
                flow_data = TRAFFIC_FLOW.get(flow_key) or TRAFFIC_FLOW.get(rev_key)
                if flow_data:
                    flow = flow_data.get(time_period, road["capacity"] * 0.5)
                    total_congestion += flow / road["capacity"]

        # Average congestion across approaches (0.0 = empty, 1.0+ = over capacity)
        avg_congestion = total_congestion / max(degree, 1)

        # Base wait = fraction of cycle proportional to number of phases
        # With 2 approaches you wait ~1/2 cycle; with 4 approaches ~3/4 cycle
        phase_fraction = max(0.3, (degree - 1) / max(degree, 1))
        base_wait = cycle_length * phase_fraction

        # Congestion multiplier: heavy traffic extends queue clearance time
        # At 100% capacity → 1.5x wait; at 50% → 1.0x (no extra)
        congestion_multiplier = 1.0 + max(0, avg_congestion - 0.5)
        normal_wait = base_wait * congestion_multiplier

        # With preemption: minimal wait (just signal change time)
        preempted_wait = 5  # seconds for signal to change

        delay_saved = max(0, normal_wait - preempted_wait)
        total_delay_saved += delay_saved

        preemption_results.append({
            "intersection": next_node,
            "name": node_data.get("name", next_node),
            "from_direction": current,
            "degree": degree,
            "avg_congestion": round(avg_congestion, 3),
            "normal_wait_sec": round(normal_wait, 1),
            "preempted_wait_sec": preempted_wait,
            "delay_saved_sec": round(delay_saved, 1),
            "priority": "EMERGENCY",
        })

    return {
        "preemptions": preemption_results,
        "total_delay_saved_sec": round(total_delay_saved, 1),
        "total_delay_saved_min": round(total_delay_saved / 60, 2),
        "num_intersections_preempted": len(preemption_results),
        "execution_time": time.perf_counter() - start_time,
        "algorithm": "Greedy (Emergency Preemption)",
    }

