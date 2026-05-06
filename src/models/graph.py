"""
Transportation Graph Model
============================
Weighted graph representation of Cairo's transportation network.
Supports both adjacency list and matrix representations.
"""

import math
from collections import defaultdict
from src.data.cairo_data import (
    NEIGHBORHOODS, FACILITIES, EXISTING_ROADS, POTENTIAL_ROADS,
    TRAFFIC_FLOW, get_all_nodes
)


class TransportationGraph:
    """
    Weighted graph representation of Cairo's transportation network.

    Supports:
    - Adjacency list representation for efficient traversal
    - Time-dependent edge weights based on traffic flow data
    - Node metadata (population, type, coordinates)
    - Both directed and undirected edge queries

    Space Complexity: O(V + E) for adjacency list
    """

    def __init__(self, include_potential=False):
        """
        Initialize the graph from Cairo data.

        Args:
            include_potential: If True, include potential new roads in the graph.
        """
        self.nodes = {}           # node_id -> {name, population, type, x, y, category}
        self.adj = defaultdict(list)  # node_id -> [(neighbor_id, edge_data)]
        self.edges = []           # list of all edges for MST algorithms

        self._load_nodes()
        self._load_edges(include_potential)
        self._connect_isolated_facilities()

    def _load_nodes(self):
        """Load all neighborhoods and facilities as graph nodes."""
        self.nodes = get_all_nodes()

    def _load_edges(self, include_potential):
        """Load existing roads (and optionally potential roads) as edges."""
        for road in EXISTING_ROADS:
            edge_data = {
                "distance": road["distance"],
                "capacity": road["capacity"],
                "condition": road["condition"],
                "is_potential": False,
                "cost": 0,
            }
            self.adj[road["from"]].append((road["to"], edge_data))
            self.adj[road["to"]].append((road["from"], edge_data))
            self.edges.append({
                "from": road["from"],
                "to": road["to"],
                **edge_data
            })

        if include_potential:
            for road in POTENTIAL_ROADS:
                edge_data = {
                    "distance": road["distance"],
                    "capacity": road["capacity"],
                    "condition": 10,  # New roads are in perfect condition
                    "is_potential": True,
                    "cost": road["cost"],
                }
                self.adj[road["from"]].append((road["to"], edge_data))
                self.adj[road["to"]].append((road["from"], edge_data))
                self.edges.append({
                    "from": road["from"],
                    "to": road["to"],
                    **edge_data
                })

    def _connect_isolated_facilities(self):
        """
        Connect facility nodes that have no roads to their nearest neighborhood.
        Facilities like hospitals, universities, and museums sit within neighborhoods
        and are reachable via local roads not in the main network data.
        """
        connected_nodes = set()
        for edge in self.edges:
            connected_nodes.add(edge["from"])
            connected_nodes.add(edge["to"])

        for fid, fdata in FACILITIES.items():
            if fid in connected_nodes:
                continue  # Already has roads

            # Find nearest neighborhood by Euclidean distance
            best_nid, best_dist = None, float('inf')
            for nid, ndata in NEIGHBORHOODS.items():
                dx = (fdata["x"] - ndata["x"]) * 111  # degrees to ~km
                dy = (fdata["y"] - ndata["y"]) * 111
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < best_dist:
                    best_dist = dist
                    best_nid = nid

            if best_nid:
                edge_data = {
                    "distance": round(best_dist, 1),
                    "capacity": 2000,
                    "condition": 8,
                    "is_potential": False,
                    "cost": 0,
                }
                self.adj[fid].append((best_nid, edge_data))
                self.adj[best_nid].append((fid, edge_data))
                self.edges.append({"from": fid, "to": best_nid, **edge_data})

    def get_neighbors(self, node_id):
        """
        Get all neighbors of a node with edge data.

        Returns:
            List of (neighbor_id, edge_data) tuples.
        """
        return self.adj.get(node_id, [])

    def get_edge_weight(self, from_id, to_id, time_period=None, weight_type="distance"):
        """
        Get edge weight between two nodes.

        Args:
            from_id: Source node ID
            to_id: Target node ID
            time_period: Optional time period for time-dependent weight
            weight_type: "distance", "time", or "congestion"

        Returns:
            Edge weight (float) or infinity if no edge exists.
        """
        for neighbor, data in self.adj.get(from_id, []):
            if neighbor == to_id:
                if weight_type == "distance":
                    return data["distance"]
                elif weight_type == "time":
                    return self._compute_travel_time(from_id, to_id, data, time_period)
                elif weight_type == "congestion":
                    return self._compute_congestion_weight(from_id, to_id, data, time_period)
        return float('inf')

    def _compute_travel_time(self, from_id, to_id, edge_data, time_period=None):
        """
        Compute travel time based on distance and traffic conditions.

        Base speed is 60 km/h, reduced by congestion ratio.
        During peak hours, speed can drop to 15-20 km/h in heavy congestion.
        """
        base_speed = 60.0  # km/h
        distance = edge_data["distance"]

        if time_period:
            flow_key = (from_id, to_id)
            rev_key = (to_id, from_id)
            flow_data = TRAFFIC_FLOW.get(flow_key) or TRAFFIC_FLOW.get(rev_key)

            if flow_data:
                flow = flow_data[time_period]
                capacity = edge_data["capacity"]
                # BPR (Bureau of Public Roads) function: t = t0 * (1 + alpha * (v/c)^beta)
                congestion_ratio = flow / capacity
                alpha, beta = 0.15, 4.0
                speed = base_speed / (1 + alpha * (congestion_ratio ** beta))
                speed = max(speed, 5.0)  # Minimum 5 km/h
                return distance / speed * 60  # Return in minutes
        
        # Default: moderate traffic
        condition_factor = edge_data.get("condition", 7) / 10.0
        speed = base_speed * condition_factor
        return distance / speed * 60  # Return in minutes

    def _compute_congestion_weight(self, from_id, to_id, edge_data, time_period=None):
        """Compute congestion-aware weight combining distance and traffic."""
        travel_time = self._compute_travel_time(from_id, to_id, edge_data, time_period)
        return travel_time

    def get_node_coords(self, node_id):
        """Get (x, y) coordinates of a node."""
        node = self.nodes.get(node_id)
        if node:
            return (node["x"], node["y"])
        return None

    def haversine_distance(self, node1_id, node2_id):
        """
        Calculate the great-circle distance between two nodes using Haversine formula.
        Returns distance in kilometers.

        Used as an admissible heuristic for A* search.
        """
        c1 = self.get_node_coords(node1_id)
        c2 = self.get_node_coords(node2_id)
        if not c1 or not c2:
            return 0.0

        lon1, lat1 = math.radians(c1[0]), math.radians(c1[1])
        lon2, lat2 = math.radians(c2[0]), math.radians(c2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Earth radius in km
        return r * c

    def euclidean_distance(self, node1_id, node2_id):
        """
        Calculate Euclidean distance between two nodes based on coordinates.
        Approximation using degree-to-km conversion (~111 km per degree).
        """
        c1 = self.get_node_coords(node1_id)
        c2 = self.get_node_coords(node2_id)
        if not c1 or not c2:
            return 0.0
        dx = (c1[0] - c2[0]) * 111  # Approximate km per degree longitude at ~30°N
        dy = (c1[1] - c2[1]) * 111  # Approximate km per degree latitude
        return math.sqrt(dx ** 2 + dy ** 2)

    def get_all_node_ids(self):
        """Get all node IDs in the graph."""
        return list(self.nodes.keys())

    def get_node_name(self, node_id):
        """Get human-readable name for a node."""
        node = self.nodes.get(node_id)
        return node["name"] if node else node_id

    def get_adjacency_matrix(self):
        """
        Build adjacency matrix for the graph.
        Returns (matrix, node_id_list) where matrix[i][j] = distance between nodes i and j.
        """
        node_ids = sorted(self.nodes.keys())
        n = len(node_ids)
        idx = {nid: i for i, nid in enumerate(node_ids)}
        matrix = [[float('inf')] * n for _ in range(n)]
        
        for i in range(n):
            matrix[i][i] = 0
        
        for edge in self.edges:
            i, j = idx[edge["from"]], idx[edge["to"]]
            matrix[i][j] = edge["distance"]
            matrix[j][i] = edge["distance"]
        
        return matrix, node_ids

    def __repr__(self):
        return f"TransportationGraph(nodes={len(self.nodes)}, edges={len(self.edges)})"
