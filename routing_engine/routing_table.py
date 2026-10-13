"""Per-router forwarding/routing table generation."""
from __future__ import annotations

from .algorithms import find_route
from .network import Network


def build_routing_table(network: Network, source: str) -> dict[str, dict]:
    """Return a destination-keyed routing table for one source router.

    Each entry contains destination, next_hop, path, total_cost, reachable,
    and status. The source itself has next_hop equal to itself and cost zero.
    """
    if source not in network.adjacency:
        raise KeyError(f"Unknown router: {source}")
    table: dict[str, dict] = {}
    for destination in network.routers():
        result = find_route(network, source, destination)
        path = list(result.path)
        table[destination] = {
            "destination": destination,
            "next_hop": path[1] if len(path) > 1 else (source if result.reachable else None),
            "path": path,
            "total_cost": result.total_cost,
            "reachable": result.reachable,
            "status": result.status.value,
        }
    return table


def build_all_routing_tables(network: Network) -> dict[str, dict[str, dict]]:
    """Build a routing table for every router, including failed routers."""
    return {router: build_routing_table(network, router) for router in network.routers()}
