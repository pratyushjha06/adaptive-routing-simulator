"""Shortest-path routing algorithms and stable result format."""
from __future__ import annotations

import heapq
from dataclasses import dataclass
from enum import Enum
from math import inf
from typing import Optional

from .network import Network


class RouteStatus(str, Enum):
    OK = "ok"
    UNKNOWN_ROUTER = "unknown_router"
    UNREACHABLE = "unreachable"


@dataclass(frozen=True)
class RouteResult:
    """Stable output object shared with simulation and dashboard modules."""
    source: str
    destination: str
    status: RouteStatus
    path: tuple[str, ...] = ()
    total_cost: Optional[float] = None

    @property
    def reachable(self) -> bool:
        return self.status is RouteStatus.OK

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "destination": self.destination,
            "status": self.status.value,
            "reachable": self.reachable,
            "path": list(self.path),
            "total_cost": self.total_cost,
        }


def find_route(network: Network, source: str, destination: str) -> RouteResult:
    """Find the minimum-cost route using Dijkstra's algorithm.

    Link costs must be non-negative. Failed routers and links are excluded.
    If source equals destination and the router is active, the route cost is 0.
    """
    if source not in network.adjacency or destination not in network.adjacency:
        return RouteResult(source, destination, RouteStatus.UNKNOWN_ROUTER)
    if source in network.failed_routers or destination in network.failed_routers:
        return RouteResult(source, destination, RouteStatus.UNREACHABLE)
    if source == destination:
        return RouteResult(source, destination, RouteStatus.OK, (source,), 0.0)

    distances = {router: inf for router in network.adjacency}
    previous: dict[str, str] = {}
    distances[source] = 0.0
    queue: list[tuple[float, str]] = [(0.0, source)]

    while queue:
        current_cost, current = heapq.heappop(queue)
        if current_cost != distances[current]:
            continue
        if current == destination:
            break
        for neighbor, edge_cost in network.neighbors(current).items():
            candidate = current_cost + edge_cost
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = current
                heapq.heappush(queue, (candidate, neighbor))

    if distances[destination] == inf:
        return RouteResult(source, destination, RouteStatus.UNREACHABLE)

    path = [destination]
    while path[-1] != source:
        path.append(previous[path[-1]])
    path.reverse()
    return RouteResult(source, destination, RouteStatus.OK, tuple(path), distances[destination])
