"""Unit tests for the route recommendation module (Module 13: Testing)."""
from app.ml.route_recommendation import build_sample_network


def test_dijkstra_finds_valid_path():
    net = build_sample_network()
    result = net.recommend_route("A", "E", algorithm="dijkstra")
    assert result["path"][0] == "A"
    assert result["path"][-1] == "E"
    assert result["total_distance_km"] > 0
    assert result["estimated_time_minutes"] > 0


def test_astar_finds_valid_path():
    net = build_sample_network()
    result = net.recommend_route("A", "E", algorithm="astar")
    assert result["path"][0] == "A"
    assert result["path"][-1] == "E"


def test_congestion_increases_travel_time():
    net = build_sample_network()
    before = net.recommend_route("A", "D", algorithm="dijkstra")
    net.update_congestion("A", "B", 5.0)
    net.update_congestion("A", "C", 5.0)
    after = net.recommend_route("A", "D", algorithm="dijkstra")
    assert after["estimated_time_minutes"] >= before["estimated_time_minutes"]


def test_invalid_node_raises():
    net = build_sample_network()
    try:
        net.recommend_route("A", "ZZZ")
        assert False, "Expected ValueError"
    except ValueError:
        pass
