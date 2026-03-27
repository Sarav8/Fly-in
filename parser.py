import sys
from zones import TypeZone, Zone
from graph import Graph


class Parser:
    """Reads and validates a map file and builds the graph."""

    def __init__(self, file_name: str) -> None:
        """Initialize parser with the map file path."""
        self.file_name = file_name
        self.nb_drones: int = 0
        self.zones_dict: dict[str, Zone] = {}
        self.graph: Graph = Graph()
        self.start_node: str = ""
        self.end_node: str = ""
        self.seen_connections: set[tuple[str, str]] = set()

    def read_file(self) -> None:
        """Parse the map file line by line."""
        try:
            with open(self.file_name, 'r') as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("nb_drones"):
                        self._handle_nb_drones(line, line_num)
                    elif line.startswith(("hub:", "start_hub:", "end_hub:")):
                        self._handle_zone(line, line_num)
                    elif line.startswith("connection:"):
                        self._handle_connection(line, line_num)
        except FileNotFoundError:
            print(f"Error: file '{self.file_name}' not found.")
            sys.exit(1)

        if self.nb_drones == 0:
            print("Error: nb_drones is missing or zero.")
            sys.exit(1)

        if not self.start_node or not self.end_node:
            print(
                "Error: map must have exactly "
                "one start_hub and one end_hub."
                )
            sys.exit(1)

    def _handle_nb_drones(self, line: str, line_num: int) -> None:
        """Parse the nb_drones line."""
        try:
            valor = int(line.split(":")[1].strip())
            if valor <= 0:
                raise ValueError
            self.nb_drones = valor
        except (IndexError, ValueError):
            print(
                f"Error line {line_num}: "
                "nb_drones must be a positive integer."
                )
            sys.exit(1)

    def _handle_zone(self, line: str, line_num: int) -> None:
        """Parse a hub, start_hub or end_hub line."""
        if "[" in line:
            idx = line.find("[")
            parte_principal = line[:idx].strip()
            texto_meta = line[idx + 1: line.find("]")].strip()
        else:
            parte_principal = line.strip()
            texto_meta = ""

        partes = parte_principal.replace(":", " ").split()
        if len(partes) != 4:
            print(f"Error line {line_num}: invalid zone format -> {line}")
            sys.exit(1)

        tipo_hub, name_hub, raw_x, raw_y = partes

        if "-" in name_hub:
            print(
                f"Error line {line_num}: "
                f"name '{name_hub}' cannot contain '-'."
            )
            sys.exit(1)
        if name_hub in self.zones_dict:
            print(f"Error line {line_num}: zone '{name_hub}' already defined.")
            sys.exit(1)

        try:
            hub_x, hub_y = int(raw_x), int(raw_y)
        except ValueError:
            print(
                f"Error line {line_num}: "
                f"invalid coordinates for '{name_hub}'."
            )
            sys.exit(1)

        type_zone_str = "normal"
        max_drones = 1
        color = "white"

        for pieza in texto_meta.split():
            if "=" in pieza:
                clave, valor = pieza.split("=", 1)
                if clave == "zone":
                    type_zone_str = valor
                elif clave == "max_drones":
                    try:
                        max_drones = int(valor)
                        if max_drones <= 0:
                            raise ValueError
                    except ValueError:
                        print(
                            f"Error line {line_num}: "
                            f"max_drones must be a positive integer."
                        )
                        sys.exit(1)
                elif clave == "color":
                    color = valor

        valid_types = [t.name for t in TypeZone]
        if type_zone_str not in valid_types:
            print(
                f"Error line {line_num}: "
                f"invalid type '{type_zone_str}'. Valid: {valid_types}"
            )
            sys.exit(1)

        type_zone_enum = TypeZone[type_zone_str]
        is_end = tipo_hub == "end_hub"

        new_zone = Zone(
            name=name_hub,
            x=hub_x,
            y=hub_y,
            type_zone=type_zone_enum,
            color=color,
            max_drones=max_drones,
            is_end=is_end,
        )
        self.zones_dict[name_hub] = new_zone
        self.graph.add_zone(new_zone)

        if tipo_hub == "start_hub":
            if self.start_node:
                print(
                    f"Error line {line_num}: "
                    f"only one start_hub allowed."
                )
                sys.exit(1)
            self.start_node = name_hub
        elif tipo_hub == "end_hub":
            if self.end_node:
                print(
                    f"Error line {line_num}: "
                    f"only one end_hub allowed."
                )
                sys.exit(1)
            self.end_node = name_hub

    def _handle_connection(self, line: str, line_num: int) -> None:
        """Parse a connection line."""
        contenido = line.replace("connection:", "").strip()
        texto_meta = ""

        if "[" in contenido:
            idx = contenido.find("[")
            nombres = contenido[:idx].strip()
            texto_meta = contenido[idx + 1: contenido.find("]")].strip()
        else:
            nombres = contenido

        if "-" not in nombres:
            print(f"Error line {line_num}: connection missing '-' -> {line}")
            sys.exit(1)

        zona_a, zona_b = map(str.strip, nombres.split("-", 1))

        if zona_a not in self.zones_dict or zona_b not in self.zones_dict:
            print(
                f"Error line {line_num}: "
                f"zones '{zona_a}' or '{zona_b}' not defined."
            )
            sys.exit(1)

        key: tuple[str, str] = (min(zona_a, zona_b), max(zona_a, zona_b))
        if key in self.seen_connections:
            print(
                f"Error line {line_num}: "
                f"duplicate connection '{zona_a}-{zona_b}'."
            )
            sys.exit(1)
        self.seen_connections.add(key)

        link_capacity = 1
        for pieza in texto_meta.split():
            if "=" in pieza:
                clave, valor = pieza.split("=", 1)
                if clave == "max_link_capacity":
                    try:
                        link_capacity = int(valor)
                        if link_capacity <= 0:
                            raise ValueError
                    except ValueError:
                        print(
                            f"Error line {line_num}: "
                            f"max_link_capacity must be a positive integer."
                        )
                        sys.exit(1)

        self.graph.add_connection(zona_a, zona_b, link_capacity)
