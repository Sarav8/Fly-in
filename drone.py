from typing import Optional
from graph import Graph


class Drone:
    """Holds the state of a single drone."""

    def __init__(self, id: int, graph: Optional[Graph] = None) -> None:
        """Initialize drone with id and optional graph reference."""
        self.id = id
        self.graph = graph
        self.state: str = "idle"
        self.current_zone: Optional[str] = None
        self.route: list[str] = []
        self.target_restricted: Optional[str] = None

    def has_arrived(self, end_name: str) -> bool:
        """Return True if drone is at end zone and not in transit."""
        return self.current_zone == end_name and self.state != "in_transit"

    def __repr__(self) -> str:
        """Return string representation of drone."""
        return (
            f"Drone(id={self.id}, "
            f"zone={self.current_zone}, "
            f"state={self.state})"
        )
