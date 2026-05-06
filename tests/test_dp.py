"""Tests for Dynamic Programming algorithms."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.algorithms.dynamic_programming import (
    optimize_public_transit_scheduling, optimize_bus_allocation,
    road_maintenance_allocation, MemoizedRoutePlanner
)
from src.models.graph import TransportationGraph


def test_bus_allocation_improvement():
    """Legacy bus-only alias still works."""
    result = optimize_bus_allocation()
    assert result["total_passengers_optimal"] >= result["total_passengers_current"], \
        "DP allocation should be at least as good as current"
    assert result["improvement_pct"] >= 0
    print(f"✅ Bus allocation (legacy): {result['improvement_pct']}% improvement")


def test_public_transit_scheduling():
    """Unified Bus+Metro scheduling."""
    result = optimize_public_transit_scheduling()
    assert result["total_passengers_optimal"] >= result["total_passengers_current"]
    assert result["num_bus_routes"] > 0
    assert result["num_metro_lines"] > 0
    # Check that both types appear in allocation
    types = {d["type"] for d in result["optimal_allocation"].values()}
    assert "Bus" in types, "Should include bus routes"
    assert "Metro" in types, "Should include metro lines"
    # Metro entries should have trains field
    for lid, data in result["optimal_allocation"].items():
        if data["type"] == "Metro":
            assert "trains" in data
    print(f"✅ Transit scheduling: {result['num_bus_routes']} bus + "
          f"{result['num_metro_lines']} metro, {result['improvement_pct']}% improvement")


def test_maintenance_allocation():
    result = road_maintenance_allocation(budget=500, granularity=50)
    assert result["total_improvement"] > 0
    assert result["budget_used"] <= result["budget_total"]
    print(f"✅ Maintenance: improvement={result['total_improvement']:.1f}, "
          f"budget={result['budget_used']}/{result['budget_total']}M")


def test_memoized_planner():
    graph = TransportationGraph()
    planner = MemoizedRoutePlanner(graph)
    
    # First query - cache miss
    r1 = planner.get_shortest_path("1", "3")
    assert planner.misses == 1
    
    # Same query - cache hit
    r2 = planner.get_shortest_path("1", "3")
    assert planner.hits == 1
    assert r1["path_distance"] == r2["path_distance"]
    
    stats = planner.get_stats()
    assert stats["hit_rate"] == 50.0
    print(f"✅ Memoized routing: hit_rate={stats['hit_rate']}%")


if __name__ == "__main__":
    test_bus_allocation_improvement()
    test_public_transit_scheduling()
    test_maintenance_allocation()
    test_memoized_planner()
    print("\n🎉 All DP tests passed!")
