from pathlib import Path

import pytest

from routing_engine import (
    Network, RouteStatus, build_all_routing_tables, build_routing_table,
    find_route, load_network,
)


@pytest.fixture
def network():
    graph = Network()
    for router in "ABCDE":
        graph.add_router(router)
    graph.add_link("A", "B", 4)
    graph.add_link("A", "C", 1)
    graph.add_link("C", "B", 1)
    graph.add_link("B", "D", 2)
    graph.add_link("C", "D", 8)
    # E is intentionally disconnected.
    return graph


def test_dijkstra_finds_minimum_cost_route(network):
    result = find_route(network, "A", "D")
    assert result.status is RouteStatus.OK
    assert result.path == ("A", "C", "B", "D")
    assert result.total_cost == 4
    assert result.to_dict() == {
        "source": "A", "destination": "D", "status": "ok",
        "reachable": True, "path": ["A", "C", "B", "D"], "total_cost": 4.0,
    }


def test_route_to_self_has_zero_cost(network):
    result = find_route(network, "A", "A")
    assert result.path == ("A",)
    assert result.total_cost == 0


def test_disconnected_router_is_unreachable(network):
    result = find_route(network, "A", "E")
    assert result.status is RouteStatus.UNREACHABLE
    assert result.path == ()
    assert result.total_cost is None


def test_unknown_router_is_reported(network):
    assert find_route(network, "A", "Z").status is RouteStatus.UNKNOWN_ROUTER


def test_link_failure_causes_route_recalculation(network):
    network.fail_link("C", "B")
    result = find_route(network, "A", "D")
    assert result.path == ("A", "B", "D")
    assert result.total_cost == 6


def test_link_recovery_restores_better_route(network):
    network.fail_link("C", "B")
    network.recover_link("C", "B")
    assert find_route(network, "A", "D").path == ("A", "C", "B", "D")


def test_router_failure_avoids_router_and_recovers(network):
    network.fail_router("C")
    assert find_route(network, "A", "D").path == ("A", "B", "D")
    network.recover_router("C")
    assert find_route(network, "A", "D").path == ("A", "C", "B", "D")


def test_failed_source_or_destination_is_unreachable(network):
    network.fail_router("A")
    assert find_route(network, "A", "D").status is RouteStatus.UNREACHABLE
    network.recover_router("A")
    network.fail_router("D")
    assert find_route(network, "A", "D").status is RouteStatus.UNREACHABLE


def test_routing_table_next_hop_and_unreachable(network):
    table = build_routing_table(network, "A")
    assert table["D"]["next_hop"] == "C"
    assert table["D"]["total_cost"] == 4
    assert table["E"]["reachable"] is False
    assert table["E"]["next_hop"] is None
    assert set(build_all_routing_tables(network)) == set("ABCDE")


def test_negative_cost_rejected():
    graph = Network()
    with pytest.raises(ValueError, match="non-negative"):
        graph.add_link("A", "B", -1)


def test_self_link_rejected():
    graph = Network()
    with pytest.raises(ValueError, match="itself"):
        graph.add_link("A", "A", 1)


def test_invalid_link_failure_rejected(network):
    with pytest.raises(ValueError, match="No link"):
        network.fail_link("A", "E")


def test_sample_network_loads():
    path = Path(__file__).parents[1] / "data" / "sample_network.json"
    graph = load_network(path)
    result = find_route(graph, "R1", "R8")
    assert result.reachable
    assert result.path[0] == "R1"
    assert result.path[-1] == "R8"
    assert result.total_cost == 13
