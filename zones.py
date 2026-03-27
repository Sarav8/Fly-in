from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from drone import Drone


class TypeZone(Enum):
    """Zone types."""
    priority = 1
    normal = 2
    restricted = 3
    blocked = 4


class Zone:
    """Graph node representing a zone."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        type_zone: TypeZone,
        color: str,
        max_drones: int = 1,
        is_end: bool = False,
    ) -> None:
        """Initialize zone properties."""
        self.name = name
        self.x = x
        self.y = y
        self.type = type_zone
        self.color = color
        self.max_drones = max_drones
        self.is_end = is_end
        self.neighbors: list["Zone"] = []
        self.current_drones: int = 0
        self.cost: int = self._compute_cost()

    def _compute_cost(self) -> int:
        """Return cost to enter this zone."""
        costs = {
            TypeZone.normal: 1,
            TypeZone.priority: 1,
            TypeZone.restricted: 2,
            TypeZone.blocked: 999,
        }
        return costs[self.type]

    def has_space(self) -> bool:
        """Return True if zone has available capacity."""
        if self.is_end:
            return True
        return self.current_drones < self.max_drones

    def is_accesible(self) -> bool:
        """Return True if zone is accessible."""
        return self.type != TypeZone.blocked

    def enter_drone(self, drone: "Drone") -> bool:
        """Try to add a drone to this zone."""
        if self.has_space() and self.is_accesible():
            self.current_drones += 1
            drone.current_zone = self.name
            return True
        return False

    def exit_drone(self) -> None:
        """Remove a drone from this zone."""
        if self.current_drones > 0:
            self.current_drones -= 1

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Zone({self.name}, {self.type.name}, "
            f"cap={self.max_drones})"
        )
