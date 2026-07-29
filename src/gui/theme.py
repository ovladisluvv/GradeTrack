import sys
import logging
from pathlib import Path
from PyQt6.QtGui import QFontDatabase

logger = logging.getLogger(__name__)

# Color palette constants
COLOR_BG = "#0B0E0C"  # Near-black, faint green tint, for the window background
COLOR_SCREEN_BG = "#0A0F0C"  # Slightly deeper background for the output console
COLOR_PRIMARY = "#3BE86B"  # Bright phosphor green for headings / active accents
COLOR_TEXT = "#9AD0AB"  # Muted green for regular body text
COLOR_SECONDARY = "#1F9E4B"  # Dim green for echoes and secondary marks
COLOR_ACCENT = "#F2D65C"  # Warm amber for prompts, stage headers and highlights
COLOR_ERROR = "#FF5C5C"  # Soft red for errors
COLOR_NUMBER = "#4FE8DC"  # Turquoise for numeric values
COLOR_BORDER = "#1E3A28"  # Dim green, low-contrast borders and the separator line

# Button state colors
COLOR_BTN_BG = "#141B10" # rest background
COLOR_BTN_BORDER = "#2E5A3B" # rest border
COLOR_BTN_TEXT = "#63E890" # rest text
COLOR_BTN_HOVER_BG = "#224730" # hover background
COLOR_BTN_HOVER_TEXT = "#B6FFCB" # hover text

# Two fonts:
#  - Press Start 2P (pixel display font) for the app name, headings, stage numbers, buttons
#  - JetBrains Mono for the readable terminal body text
HEADING_FONT_NAME = "Press Start 2P"
HEADING_FONT_FILE = "PressStart2P-Regular.ttf"
BODY_FONT_NAME = "JetBrains Mono"
BODY_FONT_FILES = ["JetBrainsMono-Regular.ttf", "JetBrainsMono-Bold.ttf"]
FALLBACK_FONT_NAME = "Courier New"

# Base point sizes for terminal text
BODY_POINT_SIZE = 11
HEADING_POINT_SIZE = 9


def get_source_path(*path_parts: str) -> Path:
    """
    Returns path to bundled resources. Expected source paths based on execution context:
    1. Python run:
       gui/fonts/<file>

    2. .exe:
       temporary _MEIPASS/fonts/<file>
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).joinpath(*path_parts)

    return Path(__file__).resolve().parent.joinpath(*path_parts)


def _register_font_files(filenames: list[str]) -> str | None:
    """Registers the given bundled font files; returns the first resolved family name"""
    loaded_family: str | None = None

    for file_name in filenames:
        font_path = get_source_path("fonts", file_name)

        if not font_path.exists():
            logger.warning(f"Font file not found: {font_path}")
            continue

        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id == -1:
            logger.warning(f"Failed to register font: {font_path}")
            continue

        families = QFontDatabase.applicationFontFamilies(font_id)
        if families and loaded_family is None:
            loaded_family = families[0]

    return loaded_family


def init_fonts() -> tuple[str, str]:
    """Registers the bundled fonts and returns (heading_family, body_family)."""
    heading = _register_font_files([HEADING_FONT_FILE]) or FALLBACK_FONT_NAME
    body = _register_font_files(BODY_FONT_FILES) or FALLBACK_FONT_NAME
    return heading, body


def build_stylesheet(heading_family: str, body_family: str) -> str:
    """Returns complete Qt Style Sheets string"""
    body_stack = f"'{body_family}', '{FALLBACK_FONT_NAME}', Consolas, monospace"
    heading_stack = f"'{heading_family}', '{body_family}', monospace"

    stylesheet = f"""
QMainWindow, QWidget#central_widget {{
    background-color: {COLOR_BG};
}}

QWidget#terminal_screen {{
    background-color: {COLOR_SCREEN_BG};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
}}

QTextEdit, QTextBrowser {{
    background-color: transparent;
    color: {COLOR_TEXT};
    border: none;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    font-family: {body_stack};
    font-size: 11pt;
    line-height: 1.5;
    padding: 16px;
    selection-background-color: {COLOR_SECONDARY};
    selection-color: {COLOR_BG};
}}

QLineEdit#console_input {{
    background-color: transparent;
    color: {COLOR_PRIMARY};
    border: none;
    border-top: 1px solid {COLOR_BORDER};
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
    font-family: {body_stack};
    font-size: 11pt;
    padding: 12px 16px;
    selection-background-color: {COLOR_SECONDARY};
    selection-color: {COLOR_BG};
}}

QLineEdit#console_input:disabled {{
    color: #2C3A30;
}}

QFrame#screen_separator {{
    background-color: {COLOR_BORDER};
    border: none;
    min-height: 1px;
    max-height: 1px;
}}

QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 10px;
    margin: 6px 4px 6px 0px;
}}

QScrollBar::handle:vertical {{
    background: {COLOR_BORDER};
    min-height: 24px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLOR_SECONDARY};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    background: none;
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

/* Container for control panel buttons (Wizard Panel) */
QWidget#wizard_panel {{
    background-color: {COLOR_BG};
}}

QPushButton {{
    background-color: {COLOR_BTN_BG};
    color: {COLOR_BTN_TEXT};
    border: 2px solid {COLOR_BTN_BORDER};
    border-radius: 8px;
    padding: 16px 22px;
    font-family: {heading_stack};
    font-size: 8pt;
}}

QPushButton:hover {{
    background-color: {COLOR_BTN_HOVER_BG};
    color: {COLOR_BTN_HOVER_TEXT};
    border-color: {COLOR_PRIMARY};
}}

QPushButton:pressed {{
    background-color: {COLOR_PRIMARY};
    color: {COLOR_BG};
    border-color: {COLOR_PRIMARY};
}}

QPushButton:disabled {{
    background-color: #0E120C;
    color: #2C3A30;
    border-color: #16241B;
}}

/* Small +/- controls that scale the terminal text. Body font, compact, fixed width */
QPushButton#zoom_button {{
    background-color: {COLOR_BTN_BG};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 2px 0px;
    min-width: 34px;
    max-width: 34px;
    min-height: 26px;
    font-family: {body_stack};
    font-size: 14pt;
}}

QPushButton#zoom_button:hover {{
    background-color: {COLOR_BTN_HOVER_BG};
    border-color: {COLOR_PRIMARY};
    color: {COLOR_BTN_HOVER_TEXT};
}}

QPushButton#zoom_button:pressed {{
    background-color: {COLOR_PRIMARY};
    color: {COLOR_BG};
    border-color: {COLOR_PRIMARY};
}}

/* Labels inside the UI */
QLabel {{
    color: {COLOR_TEXT};
    font-family: {body_stack};
    font-size: 10pt;
}}
"""

    return stylesheet
