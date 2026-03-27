from typing import Dict, List, Tuple
from zones import Zone


class Graph:
    """Bidirectional graph of zones with per-connection capacity."""

    def __init__(self) -> None:
        """Initialize empty graph."""
        self.zones: Dict[str, Zone] = {}
        self.adj: Dict[str, List[str]] = {}
        self.link_capacity: Dict[Tuple[str, str], int] = {}

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph."""
        self.zones[zone.name] = zone
        self.adj[zone.name] = []

    def add_connection(
        self, zone_a_name: str, zone_b_name: str, capacity: int = 1
    ) -> None:
        """Add a bidirectional connection between two zones."""
        if zone_a_name not in self.zones or zone_b_name not in self.zones:
            print(
                f"Error: zone '{zone_a_name}' or '{zone_b_name}' not found."
            )
            return

        self.adj[zone_a_name].append(zone_b_name)
        self.adj[zone_b_name].append(zone_a_name)

        self.zones[zone_a_name].neighbors.append(self.zones[zone_b_name])
        self.zones[zone_b_name].neighbors.append(self.zones[zone_a_name])

        key = self._make_key(zone_a_name, zone_b_name)
        self.link_capacity[key] = capacity

    def get_link_capacity(self, zone_a: str, zone_b: str) -> int:
        """Return max capacity of the link between two zones."""
        key = self._make_key(zone_a, zone_b)
        return self.link_capacity.get(key, 1)

    def get_neighbors(self, zone_name: str) -> List[Zone]:
        """Return list of Zone objects adjacent to the given zone."""
        return [
            self.zones[name]
            for name in self.adj.get(zone_name, [])
        ]

    def _make_key(self, a: str, b: str) -> Tuple[str, str]:
        """Return a canonical sorted key for a connection."""
        return (min(a, b), max(a, b))

    def __repr__(self) -> str:
        """Return string representation of graph."""
        return (
            f"Graph({len(self.zones)} zones, "
            f"{len(self.link_capacity)} links)"
        )
