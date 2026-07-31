import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton
)

from gui import (
    init_fonts,
    build_stylesheet,
    HEADING_POINT_SIZE,
    TerminalView,
    WizardView,
    StateManager
)


class MainWindow(QMainWindow):
    """Main application window. Contains the terminal and wizard view, and manages the state transitions"""
    def __init__(self, heading_family: str | None = None):
        super().__init__()
        self.setWindowTitle("GradeTrack")
        self.resize(900, 720)

        central = QWidget(self)
        central.setObjectName("central_widget")
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        self.terminal = TerminalView(central)
        if heading_family:
            self.terminal.set_heading_font(heading_family, HEADING_POINT_SIZE)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.addStretch(1)
        self.zoom_out_btn = self._make_zoom_button("−", self.terminal.decrease_font)
        self.zoom_in_btn = self._make_zoom_button("+", self.terminal.increase_font)
        top_bar.addWidget(self.zoom_out_btn)
        top_bar.addWidget(self.zoom_in_btn)

        self.separator = QFrame(central)
        self.separator.setObjectName("screen_separator")
        self.separator.setFrameShape(QFrame.Shape.NoFrame)

        self.wizard = WizardView(central)

        self.footer = QLabel("GradeTrack v1.0 · made by ovladisluvv · 2026", central)
        self.footer.setObjectName("footer_label")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addLayout(top_bar)
        layout.addSpacing(8)
        layout.addWidget(self.terminal, stretch=3)
        layout.addSpacing(12)
        layout.addWidget(self.separator)
        layout.addWidget(self.wizard, stretch=1)
        layout.addWidget(self.footer)

        self.setCentralWidget(central)

        self.state_manager = StateManager(self.terminal, self.wizard)
        QTimer.singleShot(0, self.state_manager.start)

    def keyPressEvent(self, event):
        """Real keyboard +/- scale the terminal text"""
        key = event.key()

        if key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            self.terminal.increase_font()
        elif key in (Qt.Key.Key_Minus, Qt.Key.Key_Underscore):
            self.terminal.decrease_font()
        else:
            super().keyPressEvent(event)

    def _make_zoom_button(self, text: str, handler) -> QPushButton:
        """Creates a small button for zooming the terminal text"""
        btn = QPushButton(text, self)
        btn.setObjectName("zoom_button")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.clicked.connect(handler)

        return btn


def main():
    app = QApplication(sys.argv)

    heading_family, body_family = init_fonts()
    app.setStyleSheet(build_stylesheet(heading_family, body_family))

    window = MainWindow(heading_family=heading_family)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
