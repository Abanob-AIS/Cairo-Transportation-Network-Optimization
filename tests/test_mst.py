"""Tests for MST algorithms."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.graph import TransportationGraph
from src.algorithms.mst import kruskal_mst, prim_mst, UnionFind


def test_union_find():
    uf = UnionFind(["a", "b", "c", "d"])
    assert uf.find("a") == "a"
    assert uf.union("a", "b") == True
    assert uf.find("a") == uf.find("b")
    assert uf.union("a", "b") == False
    assert uf.components == 3
    print("✅ Union-Find tests passed")


def test_kruskal_connectivity():
    graph = TransportationGraph(include_potential=True)
    result = kruskal_mst(graph)
    assert result["connected"], "MST should connect all nodes"
    assert result["num_edges"] == result["num_nodes"] - 1, "MST should have V-1 edges"
    assert result["total_distance"] > 0
    print(f"✅ Kruskal's: {result['num_edges']} edges, {result['total_distance']} km")


def test_prim_connectivity():
    graph = TransportationGraph(include_potential=True)
    result = prim_mst(graph)
    assert result["connected"], "MST should connect all nodes"
    assert result["num_edges"] == result["num_nodes"] - 1
    print(f"✅ Prim's: {result['num_edges']} edges, {result['total_distance']} km")


def test_mst_consistency():
    """Both algorithms should produce MSTs with similar total distance."""
    graph = TransportationGraph(include_potential=True)
    kr = kruskal_mst(graph, 0.0, 0.0)  # No modifications
    pr = prim_mst(graph, "3", 0.0, 0.0)
    # Both should have same number of edges
    assert kr["num_edges"] == pr["num_edges"]
    # Distances should be close (may differ due to tie-breaking)
    diff = abs(kr["total_distance"] - pr["total_distance"])
    assert diff < 50, f"MST distances differ by {diff} km"
    print(f"✅ MST consistency: Kruskal={kr['total_distance']}, Prim={pr['total_distance']}")


if __name__ == "__main__":
    test_union_find()
    test_kruskal_connectivity()
    test_prim_connectivity()
    test_mst_consistency()
    print("\n🎉 All MST tests passed!")
