"""
Minimum Spanning Tree Algorithms
==================================
Implements Kruskal's and Prim's algorithms with modifications for
infrastructure network design, prioritizing high-population areas
and critical facility connectivity.

Complexity Analysis:
    Kruskal's: O(E log E) time, O(V + E) space
    Prim's:    O(E log V) time, O(V + E) space
"""

import heapq
import time
from src.data.cairo_data import CRITICAL_FACILITY_TYPES


# =============================================================================
# Union-Find (Disjoint Set Union) Data Structure
# =============================================================================
class UnionFind:
    """
    Union-Find with path compression and union by rank.
    
    Time Complexity:
        - find: O(α(n)) amortized (nearly O(1))
        - union: O(α(n)) amortized
    Space Complexity: O(n)
    """

    def __init__(self, elements):
        self.parent = {e: e for e in elements}
        self.rank = {e: 0 for e in elements}
        self.components = len(elements)

    def find(self, x):
        """Find root with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        """Union by rank. Returns True if merged, False if already in same set."""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        self.components -= 1
        return True


# =============================================================================
# Modified Edge Weight Computation
# =============================================================================
def compute_mst_weight(edge, nodes, population_weight=0.3, facility_bonus=0.4, alpha=0.3):
    """
    Compute modified edge weight for MST that prioritizes:
    1. Connections between high-population areas (lower weight)
    2. Connections to critical facilities like hospitals and government centers
    3. Road condition quality (better condition = lower weight)
    4. Construction cost (cheaper roads are preferred)

    Modified Weight = effective_distance * condition_penalty / (population_factor * facility_factor)
    
    Where effective_distance = distance * (1-α) + (cost / 20) * α
    - α controls the trade-off between distance and financial cost
    - construction_cost_per_km = 20 million EGP (average road construction cost in Egypt)

    Args:
        edge: Edge dictionary with from, to, distance, condition
        nodes: All nodes dictionary
        population_weight: Weight factor for population priority (0-1)
        facility_bonus: Weight reduction factor for critical facilities (0-1)
        alpha: Trade-off parameter (0 = only distance, 1 = only cost)

    Returns:
        Modified edge weight (float)
    """
    distance = edge["distance"]
    condition = edge.get("condition", 7)

    # Condition penalty: worse condition = higher cost (repairs needed)
    condition_penalty = 1 + (10 - condition) * 0.1

    # Population factor: higher population = lower weight (more priority)
    from_node = nodes.get(edge["from"], {})
    to_node = nodes.get(edge["to"], {})
    from_pop = from_node.get("population", 0)
    to_pop = to_node.get("population", 0)
    max_pop = 550000  # Giza has highest at 550k
    avg_pop = (from_pop + to_pop) / 2
    population_factor = 1 + population_weight * (avg_pop / max_pop)

    # Critical facility factor: connections to hospitals, government get bonus
    facility_factor = 1.0
    from_type = from_node.get("type", "")
    to_type = to_node.get("type", "")
    if from_type in CRITICAL_FACILITY_TYPES or to_type in CRITICAL_FACILITY_TYPES:
        facility_factor = 1 + facility_bonus

    # =========================================================================
    # التعديل الجديد: Hybrid Distance-Cost Objective Function
    # =========================================================================
    if edge.get("is_potential", False):
        # Convert cost to equivalent distance (20M EGP per km construction cost)
        # So a 500M road is equivalent to 25 additional km
        construction_cost_per_km = 20  # Million EGP
        cost_equivalent_distance = edge.get("cost", 0) / construction_cost_per_km
        
        # Blend with original distance (α controls the trade-off)
        # α = 0: only distance matters
        # α = 1: only financial cost matters
        # α = 0.3: 70% distance, 30% cost (balanced approach)
        effective_distance = distance * (1 - alpha) + cost_equivalent_distance * alpha
        
        # Calculate modified weight with effective distance
        modified_weight = (effective_distance * condition_penalty) / (population_factor * facility_factor)
    else:
        # Existing roads have no construction cost
        modified_weight = (distance * condition_penalty) / (population_factor * facility_factor)
    
    return modified_weight


# =============================================================================
# Kruskal's Algorithm
# =============================================================================
def kruskal_mst(graph, population_weight=0.3, facility_bonus=0.4, alpha=0.3):
    """
    Modified Kruskal's algorithm for infrastructure network design.

    Builds a minimum spanning tree that connects all neighborhoods while:
    - Minimizing total road distance/cost
    - Prioritizing high-population area connections
    - Ensuring critical facilities have adequate connectivity
    - Balancing distance vs construction cost (hybrid objective)

    Algorithm:
        1. Compute modified weights for all edges
        2. Sort edges by modified weight (ascending)
        3. Greedily add edges that don't create cycles (Union-Find)
        4. Stop when all nodes are connected (V-1 edges)

    Time Complexity: O(E log E) for sorting + O(E α(V)) for union-find ≈ O(E log E)
    Space Complexity: O(V + E)

    Args:
        graph: TransportationGraph instance
        population_weight: Weight for population priority (0-1)
        facility_bonus: Bonus for critical facility connections (0-1)
        alpha: Trade-off between distance and cost (0 = only distance, 1 = only cost)

    Returns:
        dict with keys:
            - mst_edges: List of edges in the MST
            - total_distance: Sum of distances in MST
            - total_cost: Sum of construction costs (for potential roads)
            - execution_time: Time in seconds
            - steps: Number of edges considered
    """
    start_time = time.perf_counter()

    nodes = graph.nodes
    all_edges = graph.edges

    # Step 1: Compute modified weights
    weighted_edges = []
    for edge in all_edges:
        w = compute_mst_weight(edge, nodes, population_weight, facility_bonus, alpha)
        weighted_edges.append((w, edge))

    # Step 2: Sort by modified weight
    weighted_edges.sort(key=lambda x: x[0])

    # Step 3: Initialize Union-Find
    node_ids = list(nodes.keys())
    uf = UnionFind(node_ids)

    # Step 4: Build MST
    mst_edges = []
    total_distance = 0
    total_cost = 0
    steps = 0

    for weight, edge in weighted_edges:
        steps += 1
        if uf.union(edge["from"], edge["to"]):
            mst_edges.append({**edge, "mst_weight": weight})
            total_distance += edge["distance"]
            if edge.get("is_potential", False):
                total_cost += edge.get("cost", 0)
            if len(mst_edges) == len(node_ids) - 1:
                break

    execution_time = time.perf_counter() - start_time

    return {
        "mst_edges": mst_edges,
        "total_distance": round(total_distance, 2),
        "total_cost": round(total_cost, 2),
        "num_edges": len(mst_edges),
        "num_nodes": len(node_ids),
        "connected": uf.components == 1,
        "execution_time": execution_time,
        "steps": steps,
        "algorithm": "Kruskal's",
        "alpha": alpha,  # Include alpha in results for transparency
    }


# =============================================================================
# Prim's Algorithm
# =============================================================================
def prim_mst(graph, start_node="3", population_weight=0.3, facility_bonus=0.4, alpha=0.3):
    """
    Modified Prim's algorithm for infrastructure network design.

    Grows the MST from a starting node by always adding the cheapest
    edge connecting a visited node to an unvisited node.

    Algorithm:
        1. Start from the given node (default: Downtown Cairo)
        2. Add all edges from current node to priority queue
        3. Extract minimum weight edge to unvisited node
        4. Add that node and its edges to the queue
        5. Repeat until all nodes are visited

    Time Complexity: O(E log V) with binary heap
    Space Complexity: O(V + E)

    Returns:
        dict with same structure as kruskal_mst output
    """
    start_time = time.perf_counter()

    nodes = graph.nodes
    visited = set()
    mst_edges = []
    total_distance = 0
    total_cost = 0
    steps = 0

    # Priority queue: (modified_weight, edge_dict)
    pq = []
    visited.add(start_node)

    # Add edges from start node
    for neighbor, edge_data in graph.get_neighbors(start_node):
        edge = {"from": start_node, "to": neighbor, **edge_data}
        w = compute_mst_weight(edge, nodes, population_weight, facility_bonus, alpha)
        heapq.heappush(pq, (w, id(edge), edge))

    while pq and len(visited) < len(nodes):
        weight, _, edge = heapq.heappop(pq)
        steps += 1
        to_node = edge["to"]

        if to_node in visited:
            continue

        visited.add(to_node)
        mst_edges.append({**edge, "mst_weight": weight})
        total_distance += edge["distance"]
        if edge.get("is_potential", False):
            total_cost += edge.get("cost", 0)

        # Add edges from newly added node
        for neighbor, edge_data in graph.get_neighbors(to_node):
            if neighbor not in visited:
                new_edge = {"from": to_node, "to": neighbor, **edge_data}
                w = compute_mst_weight(new_edge, nodes, population_weight, facility_bonus, alpha)
                heapq.heappush(pq, (w, id(new_edge), new_edge))

    execution_time = time.perf_counter() - start_time

    return {
        "mst_edges": mst_edges,
        "total_distance": round(total_distance, 2),
        "total_cost": round(total_cost, 2),
        "num_edges": len(mst_edges),
        "num_nodes": len(nodes),
        "connected": len(visited) == len(nodes),
        "execution_time": execution_time,
        "steps": steps,
        "algorithm": "Prim's",
        "alpha": alpha,
    }