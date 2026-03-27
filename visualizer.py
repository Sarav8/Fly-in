import pygame
from typing import Tuple
from zones import Zone, TypeZone
from graph import Graph
from drone import Drone


ZONE_COLORS: dict[TypeZone, Tuple[int, int, int]] = {
    TypeZone.normal: (100, 140, 200),
    TypeZone.priority: (0, 220, 180),
    TypeZone.restricted: (220, 120, 30),
    TypeZone.blocked: (80, 80, 80),
}

COLOR_START = (80, 200, 80)
COLOR_END = (220, 220, 50)
COLOR_CONN = (60, 60, 60)
COLOR_DRONE = (255, 255, 255)
COLOR_LABEL = (200, 200, 200)
COLOR_BG = (20, 20, 20)


class DroneVisualizer:
    """
    Pygame visualizer for drone simulation.
    """

    def __init__(
        self,
        graph: Graph,
        drones: list[Drone],
        scale: int = 100,
    ) -> None:
        """Initialize visualizer with graph and drones."""
        pygame.init()
        self.graph = graph
        self.drones = drones
        self.scale = scale
        self.offset_x = 80
        self.offset_y = 80

        max_x = (
            max(z.x for z in graph.zones.values())
            * scale
            + self.offset_x
            + 100
        )
        max_y = (
            max(z.y for z in graph.zones.values())
            * scale
            + self.offset_y
            + 100
        )

        win_w = max(600, max_x)
        win_h = max(400, max_y)

        self.screen = pygame.display.set_mode((win_w, win_h))
        pygame.display.set_caption("Drone Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 13)
        self.font_small = pygame.font.SysFont("Arial", 11)

        self.zone_positions = self._map_positions()

    def _map_positions(self) -> dict[str, tuple[int, int]]:
        """Convert map coordinates to screen positions."""
        min_x = min(z.x for z in self.graph.zones.values())
        min_y = min(z.y for z in self.graph.zones.values())

        positions: dict[str, tuple[int, int]] = {}
        for zone in self.graph.zones.values():
            x = (zone.x - min_x) * self.scale + self.offset_x
            y = (zone.y - min_y) * self.scale + self.offset_y
            positions[zone.name] = (x, y)

        return positions

    def _get_zone_color(self, zone: Zone) -> tuple[int, int, int]:
        """Return display color for a zone."""
        type_colors: dict[TypeZone, tuple[int, int, int]] = {
            TypeZone.normal: (100, 140, 200),
            TypeZone.priority: (0, 220, 180),
            TypeZone.restricted: (220, 120, 30),
            TypeZone.blocked: (80, 80, 80),
        }

        if zone.name == self._start_name():
            return (80, 200, 80)

        if zone.is_end:
            return (220, 220, 50)

        if zone.color and zone.color != "white":
            from utils import Colors

            c = Colors()
            return c.get_rgb(zone.color)

        return type_colors.get(zone.type, (100, 100, 100))

    def _start_name(self) -> str:
        """Return start zone name."""
        return list(self.graph.zones.keys())[0]

    def draw_connections(self) -> None:
        """Draw graph edges."""
        drawn: set[Tuple[str, str]] = set()

        for zone in self.graph.zones.values():
            for neighbor in zone.neighbors:
                key: Tuple[str, str] = (
                    min(zone.name, neighbor.name),
                    max(zone.name, neighbor.name),
                )

                if key in drawn:
                    continue

                drawn.add(key)

                if neighbor.name not in self.zone_positions:
                    continue

                x1, y1 = self.zone_positions[zone.name]
                x2, y2 = self.zone_positions[neighbor.name]

                pygame.draw.line(
                    self.screen,
                    COLOR_CONN,
                    (x1, y1),
                    (x2, y2),
                    2,
                )

                cap = self.graph.get_link_capacity(
                    zone.name,
                    neighbor.name,
                )

                if cap > 1:
                    mx, my = (x1 + x2) // 2, (y1 + y2) // 2
                    cap_label = self.font_small.render(
                        f"cap:{cap}",
                        True,
                        (150, 150, 100),
                    )
                    self.screen.blit(cap_label, (mx, my))

    def draw_zones(self) -> None:
        """Draw all zones."""
        for zone in self.graph.zones.values():
            x, y = self.zone_positions[zone.name]
            color = self._get_zone_color(zone)

            pygame.draw.circle(self.screen, color, (x, y), 18)
            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                (x, y),
                18,
                2,
            )

            label = self.font.render(zone.name, True, COLOR_LABEL)
            self.screen.blit(
                label,
                (x - label.get_width() // 2, y + 22),
            )

            occ = self.font_small.render(
                f"{zone.current_drones}/{zone.max_drones}",
                True,
                (180, 180, 180),
            )

            self.screen.blit(
                occ,
                (x - occ.get_width() // 2, y - 30),
            )

    def draw_drones(self) -> None:
        """Draw drones in their current zones."""
        zone_drones: dict[str, list[Drone]] = {}

        for drone in self.drones:
            if drone.current_zone:
                zone_drones.setdefault(
                    drone.current_zone,
                    [],
                ).append(drone)

        for zone_name, drones_here in zone_drones.items():
            if zone_name not in self.zone_positions:
                continue

            bx, by = self.zone_positions[zone_name]

            for i, drone in enumerate(drones_here):
                offset = (i - len(drones_here) / 2) * 12
                dx, dy = int(bx + offset), by - 8

                pygame.draw.circle(
                    self.screen,
                    COLOR_DRONE,
                    (dx, dy),
                    6,
                )

                tag = self.font_small.render(
                    f"D{drone.id}",
                    True,
                    (0, 0, 0),
                )

                self.screen.blit(
                    tag,
                    (dx - tag.get_width() // 2, dy - 5),
                )

    def draw_turn_info(self, turn: int) -> None:
        """Display current turn."""
        info = self.font.render(
            f"Turn: {turn}",
            True,
            (220, 220, 220),
        )
        self.screen.blit(info, (10, 10))

    def run_step(self, turn: int = 0) -> bool:
        """
        Render one frame.

        Return False if window is closed.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
                return False

        self.screen.fill(COLOR_BG)
        self.draw_connections()
        self.draw_zones()
        self.draw_drones()
        self.draw_turn_info(turn)

        pygame.display.flip()
        self.clock.tick(2)

        return True

    def start(self) -> None:
        """Keep window open after simulation ends."""
        running = True

        while running:
            running = self.run_step()

        pygame.quit()
