from typing import Optional
from drone import Drone
from graph import Graph
from zones import TypeZone
from utils import Colors


class Simulation:
    """
    Turn-based simulation engine.

    Processes all drones in two phases:
    1. Decision
    2. Execution
    """

    def __init__(self, graph: Graph, drones: list[Drone]) -> None:
        """Initialize simulation with graph and drones."""
        self.graph = graph
        self.drones = drones
        self.turn: int = 0
        self.log: list[str] = []

    def run(self) -> list[str]:
        """
        Run simulation until all drones arrive.

        Returns the movement log.
        """
        while not self._all_arrived():
            self.step()

        return self.log

    def step(self) -> str:
        """
        Execute one simulation turn.

        Returns the output line for the turn.
        """
        self.turn += 1

        decisions: dict[int, Optional[str]] = {}
        for drone in self.active_drones():
            decisions[drone.id] = self._decide(drone)

        final_moves: dict[int, Optional[str]] = {}
        zone_incoming: dict[str, int] = {}
        zone_outgoing: dict[str, int] = {}
        link_usage: dict[tuple[str, str], int] = {}

        for drone in self.active_drones():
            dest = decisions[drone.id]
            if dest is not None and dest != drone.current_zone:
                if drone.current_zone is not None:
                    zone_outgoing[drone.current_zone] = (
                        zone_outgoing.get(drone.current_zone, 0) + 1
                    )

        for drone in sorted(self.active_drones(), key=lambda d: d.id):
            dest = decisions[drone.id]

            if dest is None:
                final_moves[drone.id] = None
                continue

            dest_zone = self.graph.zones[dest]
            incoming_so_far = zone_incoming.get(dest, 0)
            outgoing_from_dest = zone_outgoing.get(dest, 0)

            available = (
                dest_zone.max_drones
                - dest_zone.current_drones
                + outgoing_from_dest
                - incoming_so_far
            )

            link_ok = True
            if drone.current_zone is not None:
                link_key = (
                    min(drone.current_zone, dest),
                    max(drone.current_zone, dest),
                )
                link_cap = self.graph.get_link_capacity(
                    drone.current_zone, dest
                )
                link_ok = link_usage.get(link_key, 0) < link_cap

            if (dest_zone.is_end or available > 0) and link_ok:
                final_moves[drone.id] = dest
                zone_incoming[dest] = incoming_so_far + 1

                if drone.current_zone is not None:
                    link_key = (
                        min(drone.current_zone, dest),
                        max(drone.current_zone, dest),
                    )
                    link_usage[link_key] = (
                        link_usage.get(link_key, 0) + 1
                    )
            else:
                final_moves[drone.id] = None

        turn_output: list[str] = []
        for drone in self.active_drones():
            dest = final_moves[drone.id]
            output_token = self._apply_move(drone, dest)
            if output_token:
                turn_output.append(output_token)

        line = " ".join(turn_output)
        if line:
            self.log.append(line)
        return line

    def _decide(self, drone: Drone) -> Optional[str]:
        """
        Decide next move for a drone.

        Returns destination zone or None.
        """
        if drone.state == "in_transit":
            return drone.target_restricted

        if not drone.route:
            return None

        next_zone_name = drone.route[0]
        next_zone = self.graph.zones[next_zone_name]

        if next_zone.type == TypeZone.blocked:
            drone.route.pop(0)
            return None

        return next_zone_name

    def _apply_move(
        self,
        drone: Drone,
        dest: Optional[str],
    ) -> Optional[str]:
        """
        Apply movement and update drone state.

        Returns output token or None.
        """
        if dest is None:
            return None

        dest_zone = self.graph.zones[dest]
        current_zone = (
            self.graph.zones.get(drone.current_zone)
            if drone.current_zone
            else None
        )

        if drone.state == "in_transit":
            if current_zone:
                current_zone.exit_drone()
            dest_zone.enter_drone(drone)
            drone.state = "idle"
            drone.target_restricted = None
            if drone.route and drone.route[0] == dest:
                drone.route.pop(0)
            return f"D{drone.id}-{dest}"

        if current_zone:
            current_zone.exit_drone()

        if dest_zone.type == TypeZone.restricted:
            drone.state = "in_transit"
            drone.target_restricted = dest
            origin = drone.current_zone or "start"
            drone.current_zone = dest
            return f"D{drone.id}-{origin}-{dest}"

        dest_zone.enter_drone(drone)
        if drone.route and drone.route[0] == dest:
            drone.route.pop(0)
        return f"D{drone.id}-{dest}"

    def active_drones(self) -> list[Drone]:
        """Return drones that have not reached the end."""
        end_name = next(
            name for name, z in self.graph.zones.items() if z.is_end
        )
        return [
            d for d in self.drones
            if d.current_zone != end_name or d.state == "in_transit"
        ]

    def _all_arrived(self) -> bool:
        """Return True if all drones reached the end."""
        return len(self.active_drones()) == 0

    def print_summary(self) -> None:
        """Print final summary stats."""
        c = Colors()
        print(c.color_text(f"\nTotal turns: {self.turn}", "cyan"))
        print(c.color_text(f"Drones: {len(self.drones)}", "cyan"))
