"""
Shortest Path Algorithms
==========================
Dijkstra's (standard + time-dependent) and A* search for route planning.
"""
import heapq
import time


def dijkstra(graph, source, target=None, time_period=None, weight_type="distance"):
    """
    Dijkstra's shortest path algorithm.
    Time Complexity: O((V+E) log V), Space: O(V)
    """
    start_time = time.perf_counter()
    distances = {n: float('inf') for n in graph.nodes}
    predecessors = {n: None for n in graph.nodes}
    distances[source] = 0
    visited = set()
    nodes_explored = 0
    pq = [(0, source)]

    while pq:
        dist, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        nodes_explored += 1
        if u == target:
            break
        for neighbor, edge_data in graph.get_neighbors(u):
            if neighbor in visited:
                continue
            if weight_type == "time" and time_period:
                w = graph._compute_travel_time(u, neighbor, edge_data, time_period)
            elif weight_type == "congestion" and time_period:
                w = graph._compute_congestion_weight(u, neighbor, edge_data, time_period)
            else:
                w = edge_data["distance"]
            new_dist = dist + w
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = u
                heapq.heappush(pq, (new_dist, neighbor))

    result = {
        "distances": distances, "predecessors": predecessors,
        "nodes_explored": nodes_explored,
        "execution_time": time.perf_counter() - start_time,
        "algorithm": "Dijkstra's",
    }
    if target:
        result["path"] = reconstruct_path(predecessors, source, target)
        result["path_distance"] = distances.get(target, float('inf'))
    return result


def dijkstra_time_dependent(graph, source, target, time_period="morning"):
    """
    Modified Dijkstra's with time-varying traffic using BPR function.
    Time Complexity: O((V+E) log V), Space: O(V)
    """
    return dijkstra(graph, source, target, time_period=time_period, weight_type="time")


def astar_search(graph, source, target, time_period=None, emergency=False):
    """
    A* search with Haversine heuristic. Admissible since straight-line <= road distance.
    For emergency vehicles, applies 0.6x preemption factor.
    Time Complexity: O((V+E) log V) worst case, typically better.
    """
    start_time = time.perf_counter()
    g_score = {n: float('inf') for n in graph.nodes}
    g_score[source] = 0
    f_score = {n: float('inf') for n in graph.nodes}
    f_score[source] = graph.haversine_distance(source, target)
    predecessors = {n: None for n in graph.nodes}
    visited = set()
    nodes_explored = 0
    preemption = 0.6 if emergency else 1.0
    pq = [(f_score[source], 0, source)]
    counter = 1

    while pq:
        f, _, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        nodes_explored += 1
        if u == target:
            break
        for neighbor, edge_data in graph.get_neighbors(u):
            if neighbor in visited:
                continue
            if time_period:
                cost = graph._compute_travel_time(u, neighbor, edge_data, time_period)
            else:
                cost = edge_data["distance"]
            cost *= preemption
            tent_g = g_score[u] + cost
            if tent_g < g_score[neighbor]:
                g_score[neighbor] = tent_g
                predecessors[neighbor] = u
                h = graph.haversine_distance(neighbor, target)
                if time_period:
                    h = h / 40 * 60
                    if emergency:
                        h *= preemption
                f_score[neighbor] = tent_g + h
                heapq.heappush(pq, (f_score[neighbor], counter, neighbor))
                counter += 1

    path = reconstruct_path(predecessors, source, target)
    return {
        "path": path,
        "path_distance": g_score.get(target, float('inf')),
        "f_score": f_score.get(target, float('inf')),
        "nodes_explored": nodes_explored,
        "execution_time": time.perf_counter() - start_time,
        "algorithm": "A*",
        "emergency": emergency,
    }


def reconstruct_path(predecessors, source, target):
    """Reconstruct path from predecessors dict."""
    path = []
    current = target
    while current is not None:
        path.append(current)
        if current == source:
            break
        current = predecessors.get(current)
    if not path or path[-1] != source:
        return []
    path.reverse()
    return path


def dijkstra_with_closures(graph, source, target, closed_edges, time_period="morning"):
    """
    Dijkstra's with road closures — routes around accidents or maintenance.

    Ignores any edge (in both directions) present in closed_edges.
    Falls back to time-dependent weights via BPR function.

    Args:
        graph: TransportationGraph instance
        source: Source node ID
        target: Target node ID
        closed_edges: List of (from_id, to_id) tuples representing closed roads
        time_period: Time of day for traffic-aware weights

    Time Complexity: O((V+E) log V), Space: O(V)
    """
    start_time = time.perf_counter()

    # Build a set of closed edges (both directions) for O(1) lookup
    closed = set()
    for u, v in closed_edges:
        closed.add((u, v))
        closed.add((v, u))

    distances = {n: float('inf') for n in graph.nodes}
    predecessors = {n: None for n in graph.nodes}
    distances[source] = 0
    visited = set()
    nodes_explored = 0
    pq = [(0, source)]

    while pq:
        dist, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        nodes_explored += 1
        if u == target:
            break
        for neighbor, edge_data in graph.get_neighbors(u):
            if neighbor in visited:
                continue
            # Skip closed roads
            if (u, neighbor) in closed:
                continue
            w = graph._compute_travel_time(u, neighbor, edge_data, time_period)
            new_dist = dist + w
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = u
                heapq.heappush(pq, (new_dist, neighbor))

    path = reconstruct_path(predecessors, source, target)
    return {
        "path": path,
        "path_distance": distances.get(target, float('inf')),
        "nodes_explored": nodes_explored,
        "execution_time": time.perf_counter() - start_time,
        "algorithm": "Dijkstra's (with closures)",
        "closed_edges": list(closed_edges),
    }


def compare_algorithms(graph, source, target, time_period="morning"):
    """Compare Dijkstra's and A* side-by-side."""
    return {
        "dijkstra": dijkstra_time_dependent(graph, source, target, time_period),
        "astar": astar_search(graph, source, target, time_period, emergency=False),
        "astar_emergency": astar_search(graph, source, target, time_period, emergency=True),
    }

