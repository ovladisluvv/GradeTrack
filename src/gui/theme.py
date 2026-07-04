import sys
import logging
from pathlib import Path
from PyQt6.QtGui import QFontDatabase

logger = logging.getLogger(__name__)

# Color palette constants
COLOR_BG = "#0C0C0C"  # Black for background
COLOR_SCREEN_BG = "#050505"  # Dark black background for the output console
COLOR_PRIMARY = "#33FF33"  # Neon green for text and active elements
COLOR_SECONDARY = "#00AA00"  # Muted green for borders, secondary labels and grids
COLOR_ACCENT = "#FFFF33"  # Yellow for highlights and alerts
COLOR_ERROR = "#FF3333"  # Red for critical errors
COLOR_BTN_BG = "#151515"  # Gray for unhovered button background

# Used fonts. Press Start 2P is a pixel font for terminal look
PRIMARY_FONT_NAME = "Press Start 2P"
FALLBACK_FONT_NAME = "Courier New"
FONT_FILE_NAME = "PressStart2P-Regular.ttf"


def get_source_path(*path_parts: str) -> Path:
    """
    Returns path to bundled resources. Expected source paths based on execution context:
    1. Python run:
       gui/fonts/PressStart2P-Regular.ttf

    2. .exe:
       temporary _MEIPASS/fonts/PressStart2P-Regular.ttf
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).joinpath(*path_parts)

    return Path(__file__).resolve().parent.joinpath(*path_parts)


def init_fonts() -> str:
    """Registers bundled application font and returns resolved font family name string"""
    if PRIMARY_FONT_NAME in QFontDatabase.families():
        return PRIMARY_FONT_NAME

    font_path = get_source_path("fonts", FONT_FILE_NAME)

    if not font_path.exists():
        logger.warning(f"Font file not found: {font_path}")
        return FALLBACK_FONT_NAME

    font_id = QFontDatabase.addApplicationFont(str(font_path))

    if font_id == -1:
        logger.warning(f"Failed to register font: {font_path}")
        return FALLBACK_FONT_NAME

    font_families = QFontDatabase.applicationFontFamilies(font_id)

    if not font_families:
        logger.warning(f"No font families found after registering font: {font_path}")
        return FALLBACK_FONT_NAME

    return font_families[0]


def build_stylesheet(font_family: str) -> str:
    """Returns complete Qt Style Sheets string for application skinning"""
    font_stack = f"'{font_family}', '{FALLBACK_FONT_NAME}', Terminal, monospace"

    stylesheet = f"""
QMainWindow {{
    background-color: {COLOR_BG};
}}

QTextEdit, QTextBrowser {{
    background-color: {COLOR_SCREEN_BG};
    color: {COLOR_PRIMARY};
    border: 2px solid {COLOR_SECONDARY};
    border-radius: 0px;
    font-family: {font_stack};
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
    font-family: {font_stack};
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
    font-family: {font_stack};
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

    return stylesheet
