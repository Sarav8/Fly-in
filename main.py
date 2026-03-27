import sys
import pygame
from parser import Parser
from pathfinder import get_all_paths, assign_drones_to_paths
from drone import Drone
from simulation import Simulation
from visualizer import DroneVisualizer
from utils import Colors
from zones import TypeZone
from graph import Graph


def main() -> None:
    """Run the drone simulation."""
    # En la defensa, cambia 'False' por: "--capacity-info" in sys.argv
    capacity_info: bool = False

    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if len(args) != 1:
        print("Usage: python main.py [--capacity-info] <map_file>")
        print("Example: python main.py 03_priority_puzzle.txt")
        sys.exit

    file_path = args[0]

    print("\n=== PARSING MAP ===")
    p = Parser(file_path)
    p.read_file()

    print(f"Drones:      {p.nb_drones}")
    print(f"Start:       {p.start_node}")
    print(f"End:         {p.end_node}")
    print(f"Zones:       {len(p.graph.zones)}")
    print(f"Connections: {len(p.graph.link_capacity)}")

    all_paths = get_all_paths(p.graph, p.start_node, p.end_node)

    if not all_paths:
        print("Error: no route found from start to end.")
        sys.exit(1)

    drone_routes = assign_drones_to_paths(p.nb_drones, all_paths, p.graph)

    drones: list[Drone] = []
    start_zone = p.graph.zones[p.start_node]

    for i in range(p.nb_drones):
        drone = Drone(id=i + 1, graph=p.graph)
        drone.route = drone_routes[i]
        drone.current_zone = p.start_node
        start_zone.current_drones += 1
        drones.append(drone)

    print("\nHow do you want to run the simulation?")
    print("  1 - Terminal only")
    print("  2 - Terminal + visualizer")
    choice = input("Choose (1/2): ").strip()

    sim = Simulation(p.graph, drones)

    if choice == "2":
        _run_with_visualizer(sim, p.graph, drones, capacity_info)
    else:
        _run_terminal(sim, capacity_info)


def _print_colored_line(line: str, sim: Simulation) -> None:
    """Helper function to print a line with proper zone colors."""
    c = Colors()
    tokens = line.split()
    colored = []

    for token in tokens:
        parts = token.split("-")
        dest = parts[-1]

        if len(parts) >= 3:
            colored.append(c.color_text(token, "orange"))
            continue

        zone = sim.graph.zones.get(dest)
        if zone is None:
            colored.append(token)
            continue

        if zone.color:
            color_name = zone.color
        else:
            if zone.type == TypeZone.priority:
                color_name = "cyan"
            elif zone.type == TypeZone.restricted:
                color_name = "purple"
            elif zone.type == TypeZone.blocked:
                color_name = "red"
            else:
                color_name = "blue"

        colored.append(c.color_text(token, color_name))

    print(" ".join(colored))


def _run_terminal(sim: Simulation, capacity_info: bool = False) -> None:
    """Run simulation and print colored terminal output."""
    c = Colors()
    print(c.color_text("\n=== SIMULATION ===", "cyan"))

    while not sim._all_arrived():
        line = sim.step()
        if line:
            _print_colored_line(line, sim)

        if capacity_info:
            _print_capacity(sim)

    sim.print_summary()


def _run_with_visualizer(
    sim: Simulation,
    graph: Graph,
    drones: list[Drone],
    capacity_info: bool = False
) -> None:
    """Run simulation step by step with Pygame visualizer."""
    print("\n=== SIMULATION WITH VISUALIZER ===")
    print("Press ESC or close window to exit.")

    visualizer = DroneVisualizer(graph, drones)

    running = True
    while running and not sim._all_arrived():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break

        if not running:
            break

        line = sim.step()
        if line:
            _print_colored_line(line, sim)

        if capacity_info:
            _print_capacity(sim)

        running = visualizer.run_step(sim.turn)

    sim.print_summary()

    if running:
        visualizer.start()


def _print_capacity(sim: Simulation) -> None:
    """Print current drone count per zone and connection after each turn."""
    c = Colors()
    info_parts = []

    for name, zone in sim.graph.zones.items():
        if zone.current_drones > 0:
            info_parts.append(
                f"Zone {name}:{zone.current_drones}/{zone.max_drones}"
            )

    for drone in sim.drones:
        if (
            drone.state == "in_transit"
            and drone.current_zone
            and drone.target_restricted
        ):
            cap = sim.graph.get_link_capacity(
                drone.current_zone, drone.target_restricted
            )
            info_parts.append(
                f"Connection {drone.current_zone}-"
                f"{drone.target_restricted}:1/{cap}"
            )

    if info_parts:
        line = "  " + c.color_text("[capacity]", "yellow")
        line += " " + "  ".join(info_parts)
        print(line)


if __name__ == "__main__":
    main()
