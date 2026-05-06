"""Tests for Greedy algorithms."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.algorithms.greedy import optimize_traffic_signals, emergency_vehicle_preemption


def test_traffic_signals():
    result = optimize_traffic_signals("morning", 120)
    assert result["num_intersections"] > 0
    assert result["total_throughput"] > 0
    for nid, data in result["intersections"].items():
        total_green = sum(s["green_time"] for s in data["signal_plan"])
        assert total_green > 0, f"Intersection {nid} should have positive green time"
    print(f"✅ Traffic signals: {result['num_intersections']} intersections optimized")


def test_signal_all_periods():
    for period in ["morning", "afternoon", "evening", "night"]:
        result = optimize_traffic_signals(period)
        assert result["num_intersections"] > 0
    print("✅ Signals work for all time periods")


def test_emergency_preemption():
    path = ["7", "8", "10", "3"]  # 6th October → Downtown
    result = emergency_vehicle_preemption(path, "morning")
    assert result["total_delay_saved_sec"] > 0
    assert result["num_intersections_preempted"] == len(path) - 1
    print(f"✅ Emergency preemption: {result['total_delay_saved_min']} min saved")


if __name__ == "__main__":
    test_traffic_signals()
    test_signal_all_periods()
    test_emergency_preemption()
    print("\n🎉 All greedy tests passed!")
