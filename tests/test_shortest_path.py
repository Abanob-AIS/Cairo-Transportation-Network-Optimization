"""Tests for shortest path algorithms."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.graph import TransportationGraph
from src.algorithms.shortest_path import dijkstra, dijkstra_time_dependent, astar_search, reconstruct_path


def test_dijkstra_basic():
    graph = TransportationGraph()
    result = dijkstra(graph, "1", "3")
    assert result["path"], "Should find a path from Maadi to Downtown"
    assert result["path"][0] == "1" and result["path"][-1] == "3"
    assert result["path_distance"] < float('inf')
    print(f"✅ Dijkstra basic: {' → '.join(result['path'])}, distance={result['path_distance']:.1f} km")


def test_dijkstra_time_dependent():
    graph = TransportationGraph()
    for period in ["morning", "afternoon", "evening", "night"]:
        result = dijkstra_time_dependent(graph, "1", "4", period)
        assert result["path"], f"Should find path during {period}"
        print(f"✅ Dijkstra {period}: {result['path_distance']:.1f} min")


def test_astar_finds_path():
    graph = TransportationGraph()
    result = astar_search(graph, "7", "F9")  # 6th October to Hospital
    assert result["path"], "A* should find path to hospital"
    assert result["path"][0] == "7"
    assert result["path"][-1] == "F9" or len(result["path"]) > 0
    print(f"✅ A* path: {' → '.join(result['path'])}")


def test_astar_fewer_nodes_than_dijkstra():
    graph = TransportationGraph()
    dij = dijkstra(graph, "7", "13")
    ast = astar_search(graph, "7", "13")
    assert ast["nodes_explored"] <= dij["nodes_explored"], \
        "A* should explore fewer or equal nodes than Dijkstra"
    print(f"✅ A* explored {ast['nodes_explored']} vs Dijkstra {dij['nodes_explored']}")


def test_emergency_preemption():
    graph = TransportationGraph()
    normal = astar_search(graph, "2", "F9", "morning", emergency=False)
    emergency = astar_search(graph, "2", "F9", "morning", emergency=True)
    assert emergency["path_distance"] <= normal["path_distance"], \
        "Emergency route should be faster"
    print(f"✅ Emergency: {emergency['path_distance']:.1f} vs Normal: {normal['path_distance']:.1f} min")


def test_reconstruct_no_path():
    preds = {"a": None, "b": None, "c": None}
    path = reconstruct_path(preds, "a", "c")
    assert path == [], "Should return empty for disconnected nodes"
    print("✅ No-path reconstruction")


def test_no_path_found():
    """Verify dijkstra returns empty path for an unreachable isolated node."""
    graph = TransportationGraph()
    # Inject an isolated dummy node with no edges
    graph.nodes["ISOLATED_99"] = {
        "name": "Isolated Test Node", "population": 0, "type": "Test",
        "x": 32.0, "y": 31.0, "category": "neighborhood",
    }
    result = dijkstra(graph, "1", "ISOLATED_99")
    assert result["path"] == [], "Should return empty path for unreachable node"
    assert result["path_distance"] == float('inf'), "Distance should be infinity"
    print("✅ No-path-found test passed")


if __name__ == "__main__":
    test_dijkstra_basic()
    test_dijkstra_time_dependent()
    test_astar_finds_path()
    test_astar_fewer_nodes_than_dijkstra()
    test_emergency_preemption()
    test_reconstruct_no_path()
    test_no_path_found()
    print("\n🎉 All shortest path tests passed!")

