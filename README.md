# Adaptive Network Routing Simulator

Computer Networks semester project: a tested routing engine using weighted graphs and Dijkstra shortest paths.

## Pratyush's routing-engine module

### Features
- Weighted, undirected router topology with non-negative link costs.
- Dijkstra's shortest path algorithm.
- Per-router routing/forwarding tables (`next_hop`, path, total cost and status).
- Simulated router/link failures and recovery. The topology remains available so failed components can be restored.
- JSON loading and JSON-compatible route results for downstream modules.
- Automated tests for shortest paths, failures, unreachable nodes, validation and sample data.

### Setup
Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python demo.py
```

### Public interface

```python
from routing_engine import Network, find_route, load_network, build_routing_table

network = load_network("data/sample_network.json")
result = find_route(network, "R1", "R8")
print(result.to_dict())
print(build_routing_table(network, "R1"))

network.fail_link("R5", "R6")
result_after_failure = find_route(network, "R1", "R8")
network.recover_link("R5", "R6")
```

`find_route(network, source, destination)` returns a `RouteResult`. Its `to_dict()` output is stable and suitable for JSON serialization:

```json
{
  "source": "R1",
  "destination": "R8",
  "status": "ok",
  "reachable": true,
  "path": ["R1", "R3", "R5", "R6", "R7", "R8"],
  "total_cost": 13.0
}
```

Possible statuses: `ok`, `unknown_router`, `unreachable`. Costs represent simulated link cost/latency units, not real measured network latency. Router/link failure is simulated in-memory; this module does not configure physical routers or capture real packets.

### Contract for Sunidhi
- Import the engine using `from routing_engine import Network, find_route, load_network`.
- For display or JSON handoff, call `result.to_dict()` rather than parsing the dataclass.
- Network JSON shape: `routers` is a list of router IDs; `links` is a list of `{source, target, cost}` objects; optional `failed_routers` and per-link `failed` flags can restore failure state.
- Call `network.fail_link(a, b)`, `network.recover_link(a, b)`, `network.fail_router(r)`, and `network.recover_router(r)` for failure scenarios.
- `build_routing_table(network, source)` returns a dictionary keyed by destination. Unreachable destinations have `reachable: false`, `next_hop: null`, and `total_cost: null`.

### Commit history
Each subtask was committed separately. Run `git log --oneline` to see the checkpoints.
