import time
import math
from typing import Dict, Tuple


class Colors:
    """
    Handle terminal and RGB colors.
    """

    def __init__(self) -> None:
        """Initialize color mappings."""
        # Terminal colors
        self.colors_ascii: Dict[str, str] = {
            "red": "\033[91m",
            "green": "\033[92m",
            "blue": "\033[94m",
            "yellow": "\033[93m",
            "white": "\033[97m",
            "reset": "\033[0m",
            "orange": "\033[38;2;255;165;0m",
            "purple": "\033[35m",
            "cyan": "\033[96m",
            "rainbow": "\033[38;5;201m",
        }

        # RGB colors (for graphics)
        self.rgb: Dict[str, Tuple[int, int, int]] = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "white": (255, 255, 255),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "cyan": (0, 255, 255),
            "rainbow": (148, 0, 211),
        }

    def get_rgb(self, color_name: str) -> Tuple[int, int, int]:
        """Return RGB tuple for a given color."""
        if color_name.lower() == "rainbow":
            t = time.time() * 3
            r = int(math.sin(t) * 127 + 128)
            g = int(math.sin(t + 2) * 127 + 128)
            b = int(math.sin(t + 4) * 127 + 128)
            return (r, g, b)

        return self.rgb.get(color_name.lower(), (255, 255, 255))

    def color_text(self, text: str, color_name: str) -> str:
        """Return colored text for terminal output."""
        if color_name.lower() == "rainbow":
            rainbow_colors = [
                "\033[91m",
                "\033[93m",
                "\033[92m",
                "\033[96m",
                "\033[94m",
                "\033[95m",
            ]

            colored_text = ""
            for i, char in enumerate(text):
                color = rainbow_colors[i % len(rainbow_colors)]
                colored_text += f"{color}{char}"

            return f"{colored_text}{self.colors_ascii['reset']}"

        color_code = self.colors_ascii.get(
            color_name.lower(),
            self.colors_ascii["reset"],
        )
        return f"{color_code}{text}{self.colors_ascii['reset']}"
