*This project has been created as part of the 42 curriculum by savaquer42.*

# Fly-in — Drone Routing Simulator

## Description

Fly-in is a drone fleet routing simulator built in Python. The goal is to move all drones from a central start zone to a target end zone across a network of connected zones, in the fewest possible simulation turns.

The system reads a map file describing zones and connections, computes optimal routes using a pathfinding algorithm, distributes drones across multiple paths to maximize throughput, and runs a turn-by-turn simulation respecting all movement and capacity constraints. Both a terminal output and a Pygame graphical interface are provided.

**Key features:**
- Custom map parser supporting zone types, capacities, colors, and connection metadata
- Dijkstra-based pathfinding with support for priority, restricted, blocked, and normal zones
- Multi-drone distribution across parallel paths
- Turn-based simulation engine with simultaneous movement and conflict resolution
- Colored terminal output and real-time Pygame visualizer

---

## Instructions

### Requirements

- Python 3.10 or later
- pip

### Installation

```bash
make install
```

This creates a virtual environment and installs all dependencies (pygame, mypy, flake8).

### Running the simulator

```bash
make run
```

By default this runs the map defined in `CONFIG_FILE` inside the Makefile. To run a specific map manually:

```bash
python main.py <map_file>
```

Example:

```bash
python main.py 03_priority_puzzle.txt
```

When launched, the program will ask you to choose between two modes:

```
1 — Terminal only (faster)
2 — Terminal + Pygame visualizer
```

### Optional flags

```bash
python main.py --capacity-info <map_file>
```

Displays current drone occupancy per zone after each simulation turn. Example output:

```
D1-fast_junction D2-start-slow_path1
  [capacity] fast_junction:1/2  start:3/4
D1-fast_path D2-slow_path1
  [capacity] fast_path:1/1  slow_path1:1/1
```

### Other Makefile rules

```bash
make lint     # Run flake8 and mypy
make debug    # Run with Python debugger (pdb)
make clean    # Remove __pycache__, .mypy_cache, venv
```

---

## Algorithm

### Pathfinding — Dijkstra + DFS path enumeration

The pathfinding module uses two complementary strategies:

**1. `get_all_paths` — DFS (Depth-First Search)**

Before assigning any drone, the system enumerates all simple paths from start to end using an iterative DFS. Blocked zones are excluded. Paths are sorted by total cost (sum of zone entry costs along the path). A limit of 50 paths prevents combinatorial explosion on complex maps.

Complexity: O(V + E) per path found, where V = number of zones and E = number of connections.

**2. `get_shortest_path` — Dijkstra**

A classic Dijkstra implementation using a min-heap. The priority tuple is `(cost, preference, zone_name)` where preference ranks zone types: priority (0) < normal (1) < restricted (2). This ensures that among paths of equal cost, zones marked as `priority` are always preferred.

Complexity: O((V + E) log V).

**3. `assign_drones_to_paths` — Greedy distribution**

Once all paths are found, drones are assigned one by one to the best available path. The scoring function is:

```
score = path_cost + (drones_already_assigned / min_capacity_on_path) * 10
```

This penalises saturating a bottleneck path and naturally spreads drones across parallel routes.

### Design decisions

- **No graph libraries** — all graph logic (adjacency, pathfinding, traversal) is implemented from scratch as required by the subject.
- **Costs are derived from zone type** — normal and priority cost 1 turn, restricted costs 2 turns. The cost is computed automatically in `Zone._compute_cost()` so the parser never needs to set it manually.
- **Paths are computed once and cached** — routes are assigned before the simulation starts and not recalculated during turns, keeping the simulation loop O(D) per turn where D = number of active drones.
- **Priority zones** — treated as cost 1 but given preference score 0 in Dijkstra, so they are chosen over normal zones when costs are equal.
- **Greedy trade-off** — drone assignment is greedy rather than optimal. This keeps complexity low while performing well in practice. A fully optimal assignment would require exploring exponential combinations.

### Simulation engine — two-phase turns

Each simulation turn runs in two phases to ensure all drones move simultaneously:

**Phase 1 — Decision:** every active drone decides its intended destination based on its current route and state (`idle` or `in_transit`).

**Phase 2 — Execution:** moves are applied in order of drone ID. Zone capacity and link capacity are tracked with incoming/outgoing counters so that drones leaving a zone free up space for drones entering that same turn. Drones that cannot move (zone full or link at capacity) wait and retry next turn.

Restricted zones use a two-turn transit mechanic: on turn N the drone enters the connection (state `in_transit`), and on turn N+1 it must arrive at the destination. It cannot wait on the connection.

---

## Visual Representation

### Terminal output

Every simulation turn prints one line listing all drone movements in the format required by the subject:

```
D1-fast_junction D2-start-slow_path1
D1-fast_path D2-slow_path1
D1-merge_point D3-fast_path
D1-goal D3-merge_point
```

- `D<ID>-<zone>` — drone arrived at zone this turn (green)
- `D<ID>-<connection>` — drone is in transit toward a restricted zone (orange)
- Drones that do not move are omitted
- Drones that reach the end zone are no longer printed
- Summary line shows total turns and drone count in cyan

### Pygame visualizer

Launched with mode 2, the graphical window shows:

- **Zones** as colored circles. Color is taken from zone metadata in the map file (`color=red` renders red). If no color is specified, the default is based on zone type: teal = normal, cyan = priority, orange = restricted, dark gray = blocked, green = start, yellow = end.
- **Connections** as gray lines between zones. Links with `max_link_capacity > 1` display their capacity label on the line.
- **Drones** as small white circles inside their current zone, labeled with their ID. Multiple drones in the same zone are offset horizontally so they are all visible.
- **Occupancy counter** above each zone showing `current/max` drones.
- **Turn counter** in the top-left corner.

The simulation runs at 2 FPS so each turn is easy to follow visually. Press ESC or close the window to exit.

---

## Example input and expected output

### Input (`03_priority_puzzle.txt`)

```
nb_drones: 4

start_hub: start 0 0 [color=green max_drones=4]
hub: slow_path1 1 -1 [zone=restricted color=red]
hub: slow_path2 2 -1 [zone=restricted color=red]
hub: slow_path3 3 -1 [zone=restricted color=red]
hub: fast_junction 1 0 [zone=priority color=blue max_drones=2]
hub: fast_path 2 0 [zone=priority color=blue]
hub: merge_point 3 0 [color=yellow max_drones=3]
end_hub: goal 4 0 [color=green max_drones=4]

connection: start-slow_path1
connection: start-fast_junction
connection: slow_path1-slow_path2
connection: slow_path2-slow_path3
connection: slow_path3-merge_point
connection: fast_junction-fast_path
connection: fast_path-merge_point
connection: merge_point-goal
```

### Expected output

```
D1-fast_junction D2-start-slow_path1 D3-fast_junction
D1-fast_path D2-slow_path1
D1-merge_point D2-slow_path1-slow_path2 D3-fast_path D4-start-slow_path1
D1-goal D2-slow_path2 D3-merge_point D4-slow_path1
D2-slow_path2-slow_path3 D3-goal D4-slow_path1-slow_path2
D2-slow_path3 D4-slow_path2
D2-merge_point D4-slow_path2-slow_path3
D2-goal D4-slow_path3
D4-merge_point
D4-goal

Total turns: 10
```

Result: **10 turns** — within the subject target of ≤ 12 for this map.

---

## Performance benchmarks

| Map                  | Drones | Target | Result |
|----------------------|--------|--------|--------|
| Priority puzzle      | 4      | ≤ 12   | 10 ✅  |
| The Impossible Dream | 25     | ≤ 41   | 23 ✅  |

---

## Resources

- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Depth-First Search — Wikipedia](https://en.wikipedia.org/wiki/Depth-first_search)
- [Python heapq documentation](https://docs.python.org/3/library/heapq.html)
- [Pygame documentation](https://www.pygame.org/docs/)
- [PEP 257 — Docstring conventions](https://peps.python.org/pep-0257/)
- [mypy documentation](https://mypy.readthedocs.io/)

### AI usage

Claude (Anthropic) was used during this project for the following tasks:

- Identifying bugs in the initial implementation (incorrect `is_accesible()` logic, enum vs string comparisons in the visualizer, duplicate neighbor registration)
- Explaining the two-phase simultaneous movement pattern for the simulation engine
- Reviewing the parser against the subject requirements and suggesting missing validations (duplicate connections, line numbers in error messages)
- Generating boilerplate code for the Pygame visualizer layout
- Drafting and structuring this README

All generated code was reviewed, understood, tested, and adapted before inclusion in the project.