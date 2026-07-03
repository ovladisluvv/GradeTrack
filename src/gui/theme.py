import urllib.request
from pathlib import Path
from PyQt6.QtGui import QFontDatabase

# Color palette constants
COLOR_BG = "#0C0C0C"  # Black for background
COLOR_SCREEN_BG = "#050505"  # Dark black background for the output console
COLOR_PRIMARY = "#33FF33"  # Neon green for text and active elements
COLOR_SECONDARY = "#00AA00"  # Muted green for borders, secondary labels and grids
COLOR_ACCENT = "#FFFF33"  # Yellow for highlights and alerts
COLOR_ERROR = "#FF3333"  # Red for critical errors
COLOR_BTN_BG = "#151515"  # Gray for unhovered button background

# Used fonts. Press Start 2P is a pixel font for terminal look
FONT_FAMILY = "'Press Start 2P', 'Courier New', Terminal, monospace"

# Complete Qt Style Sheets string for application skinning
TERMINAL_STYLESHEET = f"""
QMainWindow {{
    background-color: {COLOR_BG};
}}

QTextEdit, QTextBrowser {{
    background-color: {COLOR_SCREEN_BG};
    color: {COLOR_PRIMARY};
    border: 2px solid {COLOR_SECONDARY};
    border-radius: 0px;
    font-family: {FONT_FAMILY};
    font-size: 9pt;
    line-height: 1.6;
    padding: 12px;
}}

QScrollBar:vertical {{
    border: 1px solid {COLOR_SECONDARY};
    background: {COLOR_SCREEN_BG};
    width: 14px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {COLOR_SECONDARY};
    min-height: 20px;
    border: 1px solid {COLOR_BG};
}}

QScrollBar::handle:vertical:hover {{
    background: {COLOR_PRIMARY};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    background: none;
    height: 0px;
}}

/* Container for control panel buttons (Wizard Panel) */
QWidget#wizard_panel {{
    background-color: {COLOR_BG};
    border-top: 2px solid {COLOR_SECONDARY};
}}

/* Styled Retro Buttons resembling physical terminal keys or old CLI toggles */
QPushButton {{
    background-color: {COLOR_BTN_BG};
    color: {COLOR_PRIMARY};
    border: 2px solid {COLOR_SECONDARY};
    border-radius: 0px;
    padding: 10px 14px;
    font-family: {FONT_FAMILY};
    font-size: 8pt;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {COLOR_PRIMARY};
    color: {COLOR_BG};
    border-color: {COLOR_PRIMARY};
    cursor: pointer;
}}

QPushButton:pressed {{
    background-color: {COLOR_SECONDARY};
    color: {COLOR_BG};
    border-color: {COLOR_SECONDARY};
}}

QPushButton:disabled {{
    background-color: #080808;
    color: #333333;
    border-color: #1A1A1A;
}}

/* Labels inside the UI */
QLabel {{
    color: {COLOR_PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: 8pt;
}}

/* Text styling helpers for console simulation */
.prompt-line {{
    color: {COLOR_PRIMARY};
}}

.info-line {{
    color: {COLOR_ACCENT};
}}

.error-line {{
    color: {COLOR_ERROR};
}}
"""


def init_fonts() -> str:
    """
    Attempts to download and register the 'Press Start 2P' font dynamically if it is missing from the local operating system
    Returns the resolved primary font family name string
    """
    font_name = "Press Start 2P"

    if font_name in QFontDatabase().families():
        return font_name

    try:
        font_dir = Path(__file__).parent / "fonts"
        font_dir.mkdir(exist_ok=True)
        font_path = font_dir / "PressStart2P-Regular.ttf"

        if not font_path.exists():
            url = "https://github.com/google/fonts/raw/main/ofl/pressstart2p/PressStart2P-Regular.ttf"
            with urllib.request.urlopen(url, timeout=5) as response:
                font_path.write_bytes(response.read())

        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                return families[0]
    except Exception:
        # Fail safe: if no network or writing fails, fallback to OS monospace stack
        pass

    return "Courier New"
