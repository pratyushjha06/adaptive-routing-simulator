"""Run a small command-line demonstration of the routing engine."""
from pathlib import Path

from routing_engine import find_route, load_network, build_routing_table

ROOT = Path(__file__).resolve().parent


def main() -> None:
    network = load_network(ROOT / "data" / "sample_network.json")
    show_route(network, "R1", "R8")

    print("\nSimulating failure of link R5-R6 ...")
    network.fail_link("R5", "R6")
    show_route(network, "R1", "R8")

    print("\nRouting table at R1:")
    for destination, entry in build_routing_table(network, "R1").items():
        path = " -> ".join(entry["path"]) if entry["reachable"] else "unreachable"
        print(f"  {destination:>2}: next_hop={str(entry['next_hop']):>3}  cost={str(entry['total_cost']):>5}  {path}")


def show_route(network, source: str, destination: str) -> None:
    result = find_route(network, source, destination)
    if result.reachable:
        print(f"Route {source} -> {destination}: {' -> '.join(result.path)} (cost={result.total_cost:g})")
    else:
        print(f"Route {source} -> {destination}: {result.status.value}")


if __name__ == "__main__":
    main()
