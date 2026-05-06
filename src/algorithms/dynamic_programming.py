"""
Dynamic Programming Solutions
===============================
DP for public transit scheduling, road maintenance allocation, and memoized routing.
"""
import math
import time
from src.data.cairo_data import BUS_ROUTES, METRO_LINES, EXISTING_ROADS, TRANSIT_DEMAND
from src.algorithms.shortest_path import dijkstra


# Metro train capacity is equivalent to 10 bus units
METRO_CAPACITY_MULTIPLIER = 10


def _compute_route_demand(route_stops):
    """
    Compute potential passenger demand for a route from the OD-matrix.

    Sums passengers from TRANSIT_DEMAND where both the origin and destination
    appear in the route's stop list AND the origin comes before the destination
    in the stop sequence (enforcing route directionality).

    NOTE: Routes are treated as strictly directional (one-way sequences).
    If routes are bidirectional (round-trip), the caller should invoke this
    function twice with the reversed stop list, or the route data should
    include both directions explicitly.

    Args:
        route_stops: Ordered list of stop IDs on the route.

    Returns:
        Total potential daily passengers for this route.
    """
    demand = 0
    for entry in TRANSIT_DEMAND:
        try:
            from_idx = route_stops.index(entry["from"])
            to_idx = route_stops.index(entry["to"])
        except ValueError:
            # Origin or destination not on this route — skip
            continue
        # Only count demand where travel follows the route direction
        if from_idx < to_idx:
            demand += entry["passengers"]
    return demand


def optimize_public_transit_scheduling(
    bus_routes=None, metro_lines=None,
    total_capacity=None, max_units_per_line=40
):
    """
    DP solution for optimal capacity allocation across Bus AND Metro lines.

    Merges bus routes and metro lines into a single optimization pool.
    A metro train = 10 capacity units; a bus = 1 capacity unit.

    Demand sources:
        - Bus routes: TRANSIT_DEMAND OD-matrix (fallback: daily_passengers)
        - Metro lines: daily_passengers from METRO_LINES data

    State: dp[i][j] = max passengers served using first i lines with j capacity units
    Transition: dp[i][j] = max over k in [0..min(j, max_units)] of
                           (dp[i-1][j-k] + passenger_function(line_i, k))

    Time Complexity: O(L * C * M) where L=total lines, C=total capacity, M=max per line
    Space Complexity: O(L * C)
    """
    start_time = time.perf_counter()

    if bus_routes is None:
        bus_routes = BUS_ROUTES
    if metro_lines is None:
        metro_lines = METRO_LINES

    # --- Build unified line pool ---
    lines = {}  # line_id -> {type, stops/stations, demand, current_units}

    for rid, route in bus_routes.items():
        od_demand = _compute_route_demand(route["stops"])
        demand = od_demand * 1.5 if od_demand > 0 else route["daily_passengers"] * 1.5
        lines[rid] = {
            "type": "Bus",
            "stops": route["stops"],
            "demand": demand,
            "current_units": route["buses"],  # 1 bus = 1 unit
            "daily_passengers": route["daily_passengers"],
        }

    for mid, metro in metro_lines.items():
        # Metro demand is based on daily_passengers (very high volume)
        demand = metro["daily_passengers"] * 1.2  # 20% headroom for growth
        # Current metro capacity in bus-equivalent units:
        # Get actual current trains from data if available, otherwise default to 5
        current_trains = metro.get("current_trains", 5)
        lines[mid] = {
            "type": "Metro",
            "stops": metro["stations"],
            "demand": demand,
            "current_units": current_trains * METRO_CAPACITY_MULTIPLIER,
            "daily_passengers": metro["daily_passengers"],
        }

    line_ids = list(lines.keys())
    n = len(line_ids)

    if total_capacity is None:
        total_capacity = sum(l["current_units"] for l in lines.values())

    # Precompute demand lookup
    line_demand = {lid: lines[lid]["demand"] for lid in line_ids}

    def passengers_served(line_id, num_units):
        """
        Model: diminishing returns with more capacity units.
        
        Returns passengers served using the formula: 
        max_pass * (1 - e^(-0.15 * effective))
        
        Where 0.15 controls the rate of diminishing returns.
        Metro units have 1.2x efficiency multiplier due to higher throughput.
        """
        if num_units == 0:
            return 0
        max_pass = line_demand[line_id]
        # Metro has higher throughput: 1.2x more passengers per unit
        effective = num_units
        if lines[line_id]["type"] == "Metro":
            effective = num_units * 1.2  # Metro carries 20% more per capacity unit
        return int(max_pass * (1 - math.exp(-0.15 * effective)))

    # --- DP table ---
    dp = [[0] * (total_capacity + 1) for _ in range(n + 1)]
    allocation = [[0] * (total_capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        lid = line_ids[i - 1]
        for j in range(total_capacity + 1):
            dp[i][j] = dp[i - 1][j]
            allocation[i][j] = 0
            max_k = min(j, max_units_per_line)
            for k in range(1, max_k + 1):
                val = dp[i - 1][j - k] + passengers_served(lid, k)
                if val > dp[i][j]:
                    dp[i][j] = val
                    allocation[i][j] = k

    # --- Backtrack ---
    result_allocation = {}
    remaining = total_capacity
    for i in range(n, 0, -1):
        lid = line_ids[i - 1]
        units = allocation[i][remaining]
        line_info = lines[lid]
        result_allocation[lid] = {
            "type": line_info["type"],
            "units": units,
            "buses": units if line_info["type"] == "Bus" else 0,
            "trains": units // METRO_CAPACITY_MULTIPLIER if line_info["type"] == "Metro" else 0,
            "passengers_served": passengers_served(lid, units),
            "potential_demand": int(line_info["demand"]),
            "stops": line_info["stops"],
        }
        remaining -= units

    # Compare with current allocation
    current_passengers = sum(
        passengers_served(lid, lines[lid]["current_units"]) for lid in line_ids
    )
    optimal_passengers = dp[n][total_capacity]

    return {
        "optimal_allocation": result_allocation,
        "total_passengers_optimal": optimal_passengers,
        "total_passengers_current": current_passengers,
        "improvement_pct": round(
            (optimal_passengers - current_passengers) / max(current_passengers, 1) * 100, 2
        ),
        "total_capacity_units": total_capacity,
        "num_bus_routes": len(bus_routes),
        "num_metro_lines": len(metro_lines),
        "execution_time": time.perf_counter() - start_time,
        "algorithm": "Dynamic Programming (Public Transit Scheduling)",
        "complexity": f"O({n} × {total_capacity} × {max_units_per_line})",
    }


# Backward-compatible alias
def optimize_bus_allocation(routes=None, total_buses=None, max_buses_per_route=40):
    """Legacy wrapper — calls optimize_public_transit_scheduling for bus routes only."""
    return optimize_public_transit_scheduling(
        bus_routes=routes, metro_lines={},
        total_capacity=total_buses, max_units_per_line=max_buses_per_route,
    )


def analyze_transfer_points(bus_routes=None, metro_lines=None, nodes=None):
    """
    Identify multi-modal transfer hubs where Metro and Bus lines intersect.

    A transfer hub is any node that appears in at least one Metro line's stations
    AND at least one Bus route's stops. These hubs are critical for seamless
    passenger transfers and should receive priority capacity allocation.

    Args:
        bus_routes: Dict of bus routes (default: BUS_ROUTES)
        metro_lines: Dict of metro lines (default: METRO_LINES)
        nodes: Dict of all nodes with names (default: get_all_nodes())

    Returns:
        List of hub dicts sorted by hub_complexity_score (descending).

    Time Complexity: O(B*S + M*S + N) where B=bus routes, M=metro lines, S=avg stops
    Space Complexity: O(N)
    """
    from src.data.cairo_data import get_all_nodes

    if bus_routes is None:
        bus_routes = BUS_ROUTES
    if metro_lines is None:
        metro_lines = METRO_LINES
    if nodes is None:
        nodes = get_all_nodes()

    # Map each node to which bus routes and metro lines it belongs to
    node_buses = {}   # node_id -> set of bus route IDs
    node_metros = {}  # node_id -> set of metro line IDs

    for rid, route in bus_routes.items():
        for stop in route["stops"]:
            node_buses.setdefault(stop, set()).add(rid)

    for mid, metro in metro_lines.items():
        for station in metro["stations"]:
            node_metros.setdefault(station, set()).add(mid)

    # Find multi-modal hubs (present in both sets)
    hubs = []
    all_hub_nodes = set(node_buses.keys()) & set(node_metros.keys())

    for nid in all_hub_nodes:
        metros = sorted(node_metros[nid])
        buses = sorted(node_buses[nid])
        hub_score = len(metros) + len(buses)
        node_data = nodes.get(nid, {})
        hubs.append({
            "node_id": nid,
            "name": node_data.get("name", nid),
            "connecting_metro": metros,
            "connecting_buses": buses,
            "num_metro": len(metros),
            "num_buses": len(buses),
            "hub_complexity_score": hub_score,
        })

    # Sort by complexity score (highest first)
    hubs.sort(key=lambda h: h["hub_complexity_score"], reverse=True)
    return hubs


def get_current_system_capacity(bus_routes=None, metro_lines=None):
    """
    Calculate the current total capacity units in the system.
    
    Useful for setting default values in the UI slider.
    
    Args:
        bus_routes: Dict of bus routes (default: BUS_ROUTES)
        metro_lines: Dict of metro lines (default: METRO_LINES)
        
    Returns:
        Tuple (bus_units, metro_units, total_units)
    """
    if bus_routes is None:
        bus_routes = BUS_ROUTES
    if metro_lines is None:
        metro_lines = METRO_LINES
    
    bus_units = sum(route["buses"] for route in bus_routes.values())
    
    metro_units = 0
    for metro in metro_lines.values():
        current_trains = metro.get("current_trains", 5)
        metro_units += current_trains * METRO_CAPACITY_MULTIPLIER
    
    return bus_units, metro_units, bus_units + metro_units


def road_maintenance_allocation(budget=500, granularity=50):
    """
    DP for optimal road maintenance budget allocation.
    
    State: dp[i][b] = max total improvement using first i roads with budget b
    Each road can receive 0, granularity, 2*granularity, ... million EGP.
    Improvement = condition_gain * distance * capacity (impact score).
    
    Time Complexity: O(R * (B/G)²) where R=roads, B=budget, G=granularity
    Space Complexity: O(R * B/G)
    """
    start_time = time.perf_counter()

    roads = EXISTING_ROADS
    n = len(roads)
    budget_units = budget // granularity

    def improvement(road, investment_units):
        """Improvement from investing in a road."""
        if investment_units == 0:
            return 0
        investment = investment_units * granularity
        condition = road["condition"]
        condition_gap = 10 - condition
        if condition_gap == 0:
            return 0
        # Improvement proportional to investment, gap, and road importance
        max_improvement = condition_gap * road["distance"] * (road["capacity"] / 1000)
        # Diminishing returns: each additional EGP gives less improvement
        return max_improvement * (1 - math.exp(-0.5 * investment / granularity))

    # DP table
    dp = [[0.0] * (budget_units + 1) for _ in range(n + 1)]
    alloc = [[0] * (budget_units + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        road = roads[i - 1]
        for b in range(budget_units + 1):
            dp[i][b] = dp[i - 1][b]
            alloc[i][b] = 0
            for k in range(1, b + 1):
                val = dp[i - 1][b - k] + improvement(road, k)
                if val > dp[i][b]:
                    dp[i][b] = val
                    alloc[i][b] = k

    # Backtrack
    result = {}
    remaining = budget_units
    for i in range(n, 0, -1):
        road = roads[i - 1]
        units = alloc[i][remaining]
        if units > 0:
            inv = units * granularity
            result[f"{road['from']}-{road['to']}"] = {
                "investment_million_egp": inv,
                "improvement_score": round(improvement(road, units), 2),
                "current_condition": road["condition"],
                "road": f"{road['from']} → {road['to']}",
                "distance": road["distance"],
            }
        remaining -= units

    return {
        "allocations": result,
        "total_improvement": round(dp[n][budget_units], 2),
        "budget_used": (budget_units - remaining) * granularity,
        "budget_total": budget,
        "execution_time": time.perf_counter() - start_time,
        "algorithm": "Dynamic Programming (Road Maintenance)",
    }


class MemoizedRoutePlanner:
    """
    Memoized shortest path computation using dynamic programming.
    Caches computed shortest paths to avoid redundant calculations.
    Includes a size limit to prevent unbounded memory growth.
    
    Time: O(1) for cached queries, O((V+E)logV) for new queries
    Space: O(min(V², MAX_CACHE_SIZE)) bounded by cache limit
    """

    MAX_CACHE_SIZE = 1000

    def __init__(self, graph):
        self.graph = graph
        self.cache = {}
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get_shortest_path(self, source, target, time_period=None):
        """Get shortest path with memoization and bounded cache."""
        key = (source, target, time_period)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1

        # Evict cache if size limit exceeded to prevent memory leaks
        if len(self.cache) > self.MAX_CACHE_SIZE:
            self.cache.clear()
            self.evictions += 1

        wt = "time" if time_period else "distance"
        result = dijkstra(self.graph, source, target, time_period, wt)
        self.cache[key] = result
        return result

    def get_stats(self):
        total = self.hits + self.misses
        return {
            "cache_size": len(self.cache),
            "max_cache_size": self.MAX_CACHE_SIZE,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": round(self.hits / max(total, 1) * 100, 2),
        }

    def clear_cache(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.evictions = 0