"""
Route Recommendation module (Phase 6).

Models the road network as a weighted graph (networkx) where edge weight =
a blend of raw distance and predicted congestion, so the "fastest" route
accounts for real-time conditions rather than pure distance.

Both Dijkstra and A* are provided; A* uses straight-line (haversine) distance
as its admissible heuristic when node coordinates are available.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import networkx as nx


class RoadNetwork:
    """
    Thin wrapper around a networkx graph representing the road network.
    Nodes: intersections/locations, each with (lat, lon).
    Edges: road segments, each with distance_km and a mutable congestion_factor.
    """

    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, node_id: str, lat: float, lon: float):
        self.graph.add_node(node_id, lat=lat, lon=lon)

    def add_edge(self, u: str, v: str, distance_km: float, base_speed_kmh: float = 40.0):
        self.graph.add_edge(u, v, distance_km=distance_km, base_speed_kmh=base_speed_kmh, congestion_factor=1.0)

    def update_congestion(self, u: str, v: str, congestion_factor: float):
        """congestion_factor: 1.0 = free-flow, >1.0 = slower (e.g. 2.0 = half speed)."""
        if self.graph.has_edge(u, v):
            self.graph[u][v]["congestion_factor"] = congestion_factor

    def _edge_time_minutes(self, u: str, v: str, data: dict) -> float:
        effective_speed = data["base_speed_kmh"] / max(data.get("congestion_factor", 1.0), 0.1)
        return (data["distance_km"] / effective_speed) * 60

    def _haversine_km(self, a: str, b: str) -> float:
        lat1, lon1 = self.graph.nodes[a]["lat"], self.graph.nodes[a]["lon"]
        lat2, lon2 = self.graph.nodes[b]["lat"], self.graph.nodes[b]["lon"]
        R = 6371
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        h = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return 2 * R * math.asin(math.sqrt(h))

    def recommend_route(self, origin: str, destination: str, algorithm: str = "dijkstra") -> dict:
        if origin not in self.graph or destination not in self.graph:
            raise ValueError("Origin or destination node not found in road network")

        weight_fn = lambda u, v, d: self._edge_time_minutes(u, v, d)

        if algorithm == "astar":
            # Heuristic: straight-line distance converted to an optimistic time estimate
            def heuristic(u, v):
                return (self._haversine_km(u, v) / 60) * 60  # assume ~60 km/h best case

            path = nx.astar_path(self.graph, origin, destination, heuristic=heuristic, weight=weight_fn)
        else:
            path = nx.dijkstra_path(self.graph, origin, destination, weight=weight_fn)

        total_distance = 0.0
        total_time = 0.0
        for u, v in zip(path[:-1], path[1:]):
            data = self.graph[u][v]
            total_distance += data["distance_km"]
            total_time += self._edge_time_minutes(u, v, data)

        return {
            "path": path,
            "total_distance_km": round(total_distance, 2),
            "estimated_time_minutes": round(total_time, 2),
            "congestion_adjusted": True,
        }


def build_sample_network() -> RoadNetwork:
    """A tiny illustrative network for local testing/demos without a real dataset."""
    net = RoadNetwork()
    nodes = {
        "A": (17.385, 78.486), "B": (17.395, 78.496), "C": (17.405, 78.476),
        "D": (17.415, 78.506), "E": (17.425, 78.486),
    }
    for node_id, (lat, lon) in nodes.items():
        net.add_node(node_id, lat, lon)

    net.add_edge("A", "B", distance_km=3.2, base_speed_kmh=40)
    net.add_edge("B", "D", distance_km=4.1, base_speed_kmh=45)
    net.add_edge("A", "C", distance_km=2.8, base_speed_kmh=35)
    net.add_edge("C", "E", distance_km=5.0, base_speed_kmh=50)
    net.add_edge("D", "E", distance_km=2.5, base_speed_kmh=40)
    net.add_edge("B", "E", distance_km=6.0, base_speed_kmh=55)

    # Simulate heavier congestion on the direct A-B-D-E route
    net.update_congestion("A", "B", 1.8)
    net.update_congestion("B", "D", 1.6)

    return net
