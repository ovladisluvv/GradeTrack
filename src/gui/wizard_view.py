import logging
from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtCore import pyqtSignal

logger = logging.getLogger(__name__)


class WizardView(QWidget):
    """A dynamic control panel (Wizard) that creates selection buttons based on the current stage (faculty selection, program, semesters, etc.)"""

    # Signal emitted when an option button is clicked. It sends a tuple: (selected_option_id, button_text). Id is needed for logic (state_manager), and text is for display in terminal_view
    option_selected = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("wizard_panel")

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(15, 15, 15, 15)
        self._main_layout.setSpacing(10)

        # Grid layout for buttons. It will dynamically adjust based on the number of options and specified columns
        self._grid_layout = QGridLayout()
        self._grid_layout.setSpacing(10)
        self._main_layout.addLayout(self._grid_layout)

        # Spacer item to prevent buttons from stretching to fill the entire panel height if there are few buttons
        self._spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self._main_layout.addItem(self._spacer)

        self._buttons: list[QPushButton] = []

    def set_options(self, options: dict[str, str], columns: int = 2):
        """Draws new buttons on the panel based on the provided options dictionary"""
        if columns < 1:
            logger.error(f"Invalid columns value for WizardView: {columns}")
            raise ValueError("Error: Columns has to be >= 1")

        self.clear_options()

        if not options:
            logger.warning("WizardView received empty options")
            return

        row, col = 0, 0
        for opt_id, text in options.items():
            btn = QPushButton(text)
            btn.setToolTip(text)
            # Allow the button to expand horizontally but keep a fixed vertical size
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            # Connect the button click handler. Use a lambda with captured variables (opt_id, text) to pass them to the signal
            btn.clicked.connect(lambda checked, oid=opt_id, txt=text: self._on_button_clicked(oid, txt))

            self._grid_layout.addWidget(btn, row, col)
            self._buttons.append(btn)

            col += 1
            if col >= columns:
                col = 0
                row += 1

    def clear_options(self):
        """Clears all buttons from the panel"""
        for btn in self._buttons:
            self._grid_layout.removeWidget(btn)
            btn.deleteLater()

        self._buttons.clear()

    def set_loading_state(self, is_loading: bool):
        """Blocks or unblocks the buttons"""
        for btn in self._buttons:
            btn.setEnabled(not is_loading)

    def _on_button_clicked(self, option_id: str, text: str):
        """Emits selected option and blocks buttons until external code updates or unlocks the view"""
        self.set_loading_state(True)
        self.option_selected.emit(option_id, text)
