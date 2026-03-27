import heapq
from typing import Optional
from zones import TypeZone
from graph import Graph


def get_all_paths(
    graph: Graph,
    start_name: str,
    end_name: str,
    max_paths: int = 50
) -> list[list[str]]:
    """Find all simple paths from start to end, sorted by cost."""
    all_paths: list[list[str]] = []

    stack: list[tuple[list[str], set[str]]] = (
        [([start_name], {start_name})]
    )

    while stack:
        if len(all_paths) >= max_paths:
            break
        current_path, visited = stack.pop()
        current_name = current_path[-1]

        if current_name == end_name:
            all_paths.append(current_path)
            continue

        zone = graph.zones[current_name]
        for neighbor in zone.neighbors:
            if neighbor.name not in visited:
                if neighbor.type == TypeZone.blocked:
                    continue
                new_visited = visited | {neighbor.name}
                stack.append(
                    (current_path + [neighbor.name], new_visited)
                )

    def path_cost(path: list[str]) -> int:
        """Return total movement cost of a path."""
        return sum(graph.zones[name].cost for name in path[1:])

    all_paths.sort(key=path_cost)
    return all_paths


def get_shortest_path(
    graph: Graph,
    start_name: str,
    end_name: str
) -> list[str]:
    """Return shortest path using Dijkstra, preferring priority zones."""
    heap: list[tuple[int, int, str]] = [(0, 0, start_name)]
    distancias: dict[str, int] = {start_name: 0}
    padres: dict[str, Optional[str]] = {start_name: None}

    while heap:
        coste_actual, pref_actual, actual_name = heapq.heappop(heap)
        zone = graph.zones[actual_name]

        if actual_name == end_name:
            ruta: list[str] = []
            paso: Optional[str] = end_name
            while paso is not None:
                ruta.append(paso)
                paso = padres[paso]
            ruta.reverse()
            return ruta

        for vecino in zone.neighbors:
            if vecino.type == TypeZone.blocked:
                continue

            nuevo_coste = coste_actual + vecino.cost
            pref = {
                TypeZone.priority: 0,
                TypeZone.normal: 1,
                TypeZone.restricted: 2,
                TypeZone.blocked: 99,
            }[vecino.type]

            if (vecino.name not in distancias or
                    nuevo_coste < distancias[vecino.name] or
                    (nuevo_coste == distancias[vecino.name]
                     and pref < pref_actual)):
                distancias[vecino.name] = nuevo_coste
                padres[vecino.name] = actual_name
                heapq.heappush(
                    heap, (nuevo_coste, pref, vecino.name)
                )

    return []


def assign_drones_to_paths(
    nb_drones: int,
    all_paths: list[list[str]],
    graph: Graph
) -> list[list[str]]:
    """Assign each drone to the best available route."""
    if not all_paths:
        return []

    def path_min_capacity(path: list[str]) -> int:
        """Return the minimum zone capacity along the path."""
        return min(graph.zones[name].max_drones for name in path[1:])

    def path_cost(path: list[str]) -> int:
        """Return total movement cost of a path."""
        return sum(graph.zones[name].cost for name in path[1:])

    assignments: list[list[str]] = []
    path_usage: list[int] = [0] * len(all_paths)

    for _ in range(nb_drones):
        best_idx = 0
        best_score = float('inf')

        for i, path in enumerate(all_paths):
            cap = path_min_capacity(path)
            cost = path_cost(path)
            saturation = path_usage[i] / cap
            score = cost + saturation * 10

            if score < best_score:
                best_score = score
                best_idx = i

        path_usage[best_idx] += 1
        assignments.append(all_paths[best_idx][1:])

    return assignments
