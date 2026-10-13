"""JSON-compatible loading helpers for sample networks and handoffs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .network import Network


def network_from_dict(data: dict[str, Any]) -> Network:
    """Create a Network from {routers: [], links: [{source,target,cost,failed?}]}.

    Optional failed_routers and failed links are restored after topology creation.
    """
    if not isinstance(data, dict):
        raise ValueError("Network data must be a JSON object")
    network = Network()
    routers = data.get("routers", [])
    links = data.get("links", [])
    if not isinstance(routers, list) or not isinstance(links, list):
        raise ValueError("'routers' and 'links' must be lists")
    for router in routers:
        network.add_router(router)
    for link in links:
        try:
            network.add_link(link["source"], link["target"], link["cost"])
        except (KeyError, TypeError) as exc:
            raise ValueError(f"Invalid link entry: {link!r}") from exc
    for router in data.get("failed_routers", []):
        network.fail_router(router)
    for link in links:
        if link.get("failed", False):
            network.fail_link(link["source"], link["target"])
    return network


def load_network(path: str | Path) -> Network:
    """Load network topology from a JSON file."""
    with Path(path).open("r", encoding="utf-8") as file:
        return network_from_dict(json.load(file))
