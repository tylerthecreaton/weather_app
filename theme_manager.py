# theme_manager.py

from typing import Dict, NamedTuple

class ColorPalette(NamedTuple):
    background: str
    foreground: str  # Text color on background
    primary: str     # Main accent color (e.g., headers, important buttons)
    secondary: str   # Secondary accent color (e.g., less important details, borders)
    accent: str      # Specific accent for call-to-action or highlights
    text: str        # General text color (can be same as foreground or different)
    card_bg: str     # Background for card elements
    card_text: str   # Text color for card elements
    button_text: str # Text color for buttons (often same as foreground or a contrast to button bg)

class ThemeManager:
    """
    Manages color palettes for different UI themes.
    """
    def __init__(self):
        self.themes: Dict[str, ColorPalette] = {
            "light": ColorPalette(
                background="#F0F0F0",    # Light gray
                foreground="#FFFFFF",    # White (for elements on primary/accent)
                primary="#007AFF",       # Bright blue
                secondary="#E5E5EA",    # Light gray (softer than background)
                accent="#FF9500",       # Orange
                text="#1C1C1E",          # Near black
                card_bg="#FFFFFF",       # White
                card_text="#1C1C1E",     # Near black
                button_text="#FFFFFF"    # White
            ),
            "dark": ColorPalette(
                background="#1C1C1E",    # Near black
                foreground="#000000",    # Black (for elements on primary/accent)
                primary="#0A84FF",       # Bright blue (iOS style)
                secondary="#2C2C2E",    # Dark gray
                accent="#FF9F0A",       # Orange (iOS style)
                text="#F2F2F7",          # Near white
                card_bg="#2C2C2E",       # Dark gray
                card_text="#F2F2F7",     # Near white
                button_text="#FFFFFF"    # White (often on primary color buttons)
            ),
            "hot": ColorPalette( # Theme for warm temperatures
                background="#FFF3E0",    # Light orange/peach
                foreground="#FFFFFF",
                primary="#FF7043",       # Deep orange
                secondary="#FFE0B2",    # Lighter orange
                accent="#DD2C00",       # Strong red-orange
                text="#4E342E",          # Dark brown
                card_bg="#FFFFFF",
                card_text="#4E342E",
                button_text="#FFFFFF"
            ),
            "cold": ColorPalette( # Theme for cool temperatures
                background="#E3F2FD",    # Light blue
                foreground="#FFFFFF",
                primary="#2196F3",       # Standard blue
                secondary="#BBDEFB",    # Lighter blue
                accent="#0D47A1",       # Dark blue
                text="#0D47A1",          # Dark blue
                card_bg="#FFFFFF",
                card_text="#0D47A1",
                button_text="#FFFFFF"
            ),
            # Default theme for fallback
            "default": ColorPalette(
                background="#ECECEC",
                foreground="#FFFFFF",
                primary="#5A9BD5",
                secondary="#C5C5C5",
                accent="#ED7D31",
                text="#333333",
                card_bg="#FFFFFF",
                card_text="#333333",
                button_text="#FFFFFF"
            )
        }

    def get_palette(self, theme_name: str) -> ColorPalette:
        """
        Retrieves the color palette for a given theme name.
        Returns the default palette if the theme_name is not found.
        """
        return self.themes.get(theme_name.lower(), self.themes["default"])

    def get_temperature_theme(self, temperature: float) -> ColorPalette:
        """
        Determines the theme based on temperature.
        Adjust thresholds as needed.
        """
        if temperature >= 28: # Hot threshold (Celsius)
            return self.get_palette("hot")
        elif temperature <= 15: # Cold threshold (Celsius)
            return self.get_palette("cold")
        else: # Neutral, could be light or dark based on another setting
            # For now, let's default to light for neutral temps if not specified
            return self.get_palette("light")

if __name__ == '__main__':
    # Example Usage
    manager = ThemeManager()

    print("Light Theme:", manager.get_palette("light"))
    print("Dark Theme:", manager.get_palette("dark"))
    print("Hot Theme (30C):", manager.get_temperature_theme(30))
    print("Warm Theme (25C):", manager.get_temperature_theme(25)) # Will default to light
    print("Cold Theme (10C):", manager.get_temperature_theme(10))
    print("Unknown Theme:", manager.get_palette("ocean")) # Will use default
