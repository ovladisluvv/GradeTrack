import logging
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy
)

logger = logging.getLogger(__name__)


class WizardView(QWidget):
    """
    A dynamic control panel that renders selection buttons for the current wizard stage
    (faculty, program, department, action, semesters)
    """

    # Detects when an option button is clicked: (option_id, button_text)
    option_selected = pyqtSignal(str, str) 

    MIN_BUTTON_WIDTH = 110
    BACK_ID = "__back__"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("wizard_panel")

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(18, 16, 18, 18)
        self._main_layout.setSpacing(10)

        # Center the grid horizontally
        self._center_row = QHBoxLayout()
        self._center_row.addStretch(1)
        self._grid_layout = QGridLayout()
        self._grid_layout.setSpacing(12)
        self._center_row.addLayout(self._grid_layout)
        self._center_row.addStretch(1)
        self._main_layout.addLayout(self._center_row)

        # Keeps buttons from stretching vertically
        self._spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self._main_layout.addItem(self._spacer)

        self._buttons: list[QPushButton] = []

    def set_options(self, options: dict[str, str], columns: int = 2) -> None:
        """Renders choices in a grid with a separate, centered back button below"""
        if columns < 1:
            logger.error(f"Invalid columns value for WizardView: {columns}")
            raise ValueError("Error: Columns has to be >= 1")

        self.clear_options()

        if not options:
            logger.warning("WizardView received empty options")
            return

        choice_count = len(options) - (self.BACK_ID in options)
        columns = max(1, min(columns, choice_count))
        row, col = 0, 0
        for opt_id, text in options.items():
            if opt_id == self.BACK_ID:
                continue

            self._grid_layout.addWidget(self._make_button(opt_id, text), row, col)
            col += 1

            if col >= columns:
                col = 0
                row += 1

        if self.BACK_ID in options:
            back_button = self._make_button(self.BACK_ID, options[self.BACK_ID])
            self._grid_layout.addWidget(
                back_button, row + (col > 0), 0, 1, columns, Qt.AlignmentFlag.AlignHCenter
            )

        self._equalize_button_widths()

    def clear_options(self) -> None:
        """Removes all buttons from the panel"""
        for button in self._buttons:
            self._grid_layout.removeWidget(button)
            button.hide()
            button.deleteLater()

        self._buttons.clear()

    def set_loading_state(self, is_loading: bool) -> None:
        """Enables or disables all current buttons (used while work is in progress)"""
        for button in self._buttons:
            button.setEnabled(not is_loading)

    def _equalize_button_widths(self) -> None:
        """Gives every button the width of the widest one so grid columns stay uniform"""
        widest = self.MIN_BUTTON_WIDTH

        for button in self._buttons:
            button.ensurePolished() # applies the stylesheet font before measuring
            widest = max(widest, button.sizeHint().width())

        for button in self._buttons:
            button.setFixedWidth(widest)

    def _make_button(self, opt_id: str, text: str) -> QPushButton:
        """Makes a button for the given option and connects its click signal to the selection handler"""
        button = QPushButton(text)
        button.setToolTip(text)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        button.setMinimumWidth(self.MIN_BUTTON_WIDTH)
        button.clicked.connect(lambda checked, oid=opt_id, txt=text: self._on_button_clicked(oid, txt))

        self._buttons.append(button)
        return button
    
    def _on_button_clicked(self, option_id: str, text: str) -> None:
        """Locks buttons and emits the selection until the controller renders the next stage"""
        self.set_loading_state(True)
        self.option_selected.emit(option_id, text)
