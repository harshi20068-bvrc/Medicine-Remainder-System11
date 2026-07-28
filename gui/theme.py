"""
Theme configuration and styling constants for the GUI application.
"""

class Theme:
    """Modern Theme Color Tokens and Font Configs."""

    # Brand Colors
    PRIMARY = "#0F766E"         # Teal 700
    PRIMARY_HOVER = "#115E59"   # Teal 800
    PRIMARY_LIGHT = "#0D9488"   # Teal 600
    ACCENT = "#14B8A6"          # Teal 500

    # Backgrounds & Cards
    BG_DARK = "#0F172A"         # Slate 900
    SIDEBAR_BG = "#1E293B"      # Slate 800
    CARD_BG = "#1E293B"         # Slate 800
    CARD_HOVER = "#334155"      # Slate 700
    INPUT_BG = "#334155"       # Slate 700

    # Status Colors
    COLOR_TAKEN = "#10B981"     # Emerald 500
    COLOR_MISSED = "#EF4444"    # Red 500
    COLOR_PENDING = "#F59E0B"   # Amber 500

    # Text Colors
    TEXT_MAIN = "#F8FAFC"       # Slate 50
    TEXT_MUTED = "#94A3B8"      # Slate 400
    TEXT_DARK = "#0F172A"       # Slate 900

    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_TITLE = ("Segoe UI", 24, "bold")
    FONT_SUBTITLE = ("Segoe UI", 16, "bold")
    FONT_HEADER = ("Segoe UI", 14, "bold")
    FONT_BODY = ("Segoe UI", 12)
    FONT_BODY_BOLD = ("Segoe UI", 12, "bold")
    FONT_SMALL = ("Segoe UI", 10)

    @classmethod
    def get_status_color(cls, status: str) -> str:
        """Returns the theme color associated with a reminder status."""
        st = status.lower()
        if st == 'taken':
            return cls.COLOR_TAKEN
        elif st == 'missed':
            return cls.COLOR_MISSED
        elif st == 'pending':
            return cls.COLOR_PENDING
        return cls.TEXT_MUTED
