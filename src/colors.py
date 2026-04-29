"""Terminal color utilities for visualization."""


class Colors:
    """ANSI color codes for terminal output."""
    
    # Reset
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Color mapping for zone colors
    COLOR_MAP = {
        'red': RED,
        'green': GREEN,
        'yellow': YELLOW,
        'blue': BLUE,
        'magenta': MAGENTA,
        'cyan': CYAN,
        'white': WHITE,
        'gray': GRAY,
        'grey': GRAY,
        'orange': YELLOW,
        'purple': MAGENTA,
        'pink': BRIGHT_MAGENTA,
    }
    
    # Default colors for zone types
    TYPE_COLORS = {
        'normal': BLUE,
        'restricted': YELLOW,
        'priority': GREEN,
        'blocked': GRAY,
        'start': BRIGHT_GREEN,
        'end': BRIGHT_RED,
    }
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        """
        Colorize text with the given color.
        
        Args:
            text: Text to colorize
            color: Color name or ANSI code
            
        Returns:
            Colorized text
        """
        if color.startswith('\033['):
            # Already an ANSI code
            return f"{color}{text}{Colors.RESET}"
        
        # Look up color name
        color_code = Colors.COLOR_MAP.get(color.lower(), Colors.WHITE)
        return f"{color_code}{text}{Colors.RESET}"
    
    @staticmethod
    def get_zone_color(zone_type: str, zone_color: str | None, is_start: bool, is_end: bool) -> str:
        """
        Get the appropriate color for a zone.
        
        Args:
            zone_type: Type of zone (normal, restricted, etc.)
            zone_color: Optional color specified in map
            is_start: Whether this is the start zone
            is_end: Whether this is the end zone
            
        Returns:
            ANSI color code
        """
        # Priority: start/end > custom color > type color
        if is_start:
            return Colors.TYPE_COLORS['start']
        if is_end:
            return Colors.TYPE_COLORS['end']
        if zone_color:
            return Colors.COLOR_MAP.get(zone_color.lower(), Colors.TYPE_COLORS.get(zone_type, Colors.WHITE))
        return Colors.TYPE_COLORS.get(zone_type, Colors.WHITE)
