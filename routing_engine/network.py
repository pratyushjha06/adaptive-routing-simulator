"""Weighted, undirected network topology for the routing simulator."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Mapping


@dataclass
class Network:
    """A graph of routers and links, where link cost is non-negative latency/cost.

    Links are undirected. Failed routers and links are retained in the topology
    but excluded from routing calculations, making recovery straightforward.
    """
    adjacency: Dict[str, Dict[str, float]] = field(default_factory=dict)
    failed_routers: set[str] = field(default_factory=set)
    failed_links: set[tuple[str, str]] = field(default_factory=set)

    def add_router(self, router: str) -> None:
        router = self._validate_router(router)
        self.adjacency.setdefault(router, {})

    def add_link(self, router_a: str, router_b: str, cost: float) -> None:
        a, b = self._validate_router(router_a), self._validate_router(router_b)
        if a == b:
            raise ValueError("A router cannot link to itself")
        if isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost < 0:
            raise ValueError("Link cost must be a non-negative number")
        self.add_router(a)
        self.add_router(b)
        self.adjacency[a][b] = float(cost)
        self.adjacency[b][a] = float(cost)
        self.failed_links.discard(self._link_key(a, b))

    def remove_link(self, router_a: str, router_b: str) -> None:
        a, b = self._require_router(router_a), self._require_router(router_b)
        self.adjacency[a].pop(b, None)
        self.adjacency[b].pop(a, None)
        self.failed_links.discard(self._link_key(a, b))

    def fail_router(self, router: str) -> None:
        self._require_router(router)
        self.failed_routers.add(router)

    def recover_router(self, router: str) -> None:
        self._require_router(router)
        self.failed_routers.discard(router)

    def fail_link(self, router_a: str, router_b: str) -> None:
        a, b = self._require_router(router_a), self._require_router(router_b)
        if b not in self.adjacency[a]:
            raise ValueError(f"No link exists between {a} and {b}")
        self.failed_links.add(self._link_key(a, b))

    def recover_link(self, router_a: str, router_b: str) -> None:
        a, b = self._require_router(router_a), self._require_router(router_b)
        self.failed_links.discard(self._link_key(a, b))

    def neighbors(self, router: str) -> Dict[str, float]:
        """Return currently reachable adjacent routers and their link costs."""
        self._require_router(router)
        if router in self.failed_routers:
            return {}
        return {
            neighbor: cost
            for neighbor, cost in self.adjacency[router].items()
            if neighbor not in self.failed_routers
            and self._link_key(router, neighbor) not in self.failed_links
        }

    def routers(self) -> list[str]:
        return sorted(self.adjacency)

    def to_dict(self) -> dict:
        return {
            "routers": self.routers(),
            "links": [
                {"source": a, "target": b, "cost": cost,
                 "failed": self._link_key(a, b) in self.failed_links}
                for a in sorted(self.adjacency)
                for b, cost in sorted(self.adjacency[a].items()) if a < b
            ],
            "failed_routers": sorted(self.failed_routers),
        }

    @staticmethod
    def _validate_router(router: str) -> str:
        if not isinstance(router, str) or not router.strip():
            raise ValueError("Router ID must be a non-empty string")
        return router.strip()

    def _require_router(self, router: str) -> str:
        router = self._validate_router(router)
        if router not in self.adjacency:
            raise KeyError(f"Unknown router: {router}")
        return router

    @staticmethod
    def _link_key(a: str, b: str) -> tuple[str, str]:
        return tuple(sorted((a, b)))
