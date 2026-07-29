from collections import deque
from PyQt6.QtWidgets import QWidget, QTextBrowser, QLineEdit, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QIntValidator

from gui import (
    COLOR_PRIMARY,
    COLOR_TEXT,
    COLOR_ACCENT,
    COLOR_ERROR,
    COLOR_NUMBER,
    HEADING_POINT_SIZE,
    BODY_POINT_SIZE,
)

# Segment is (text, color_hex, font_family_or_None, point_size). A queued message is a list of segments, so one line can mix colors AND fonts
Segment = tuple[str, str, "str | None", "int | float | None"]


class OutputScreen(QTextBrowser):
    """
    Read-only text screen with a queued typewriter effect where characters appear one by one
    Each queued message is a list of styled segments
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setOpenExternalLinks(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameStyle(0)

        self._typing_timer = QTimer(self)
        self._typing_timer.timeout.connect(self._type_next_char)
        self._typing_speed_ms = 15

        self._queue: deque[list[Segment]] = deque()
        self._segments: list[Segment] | None = None
        self._seg_index = 0
        self._char_index = 0

    def print_segments(self, segments: list[Segment], typewriter: bool = True) -> None:
        """Queues a styled line (list of segments) for display"""
        if not typewriter:
            self.force_finish_typing()

            for seg in segments:
                self._insert_segment(seg)

            self._scroll_to_bottom()
            return

        self._queue.append(segments)

        if not self._typing_timer.isActive():
            self._process_next_message()

    def is_busy(self) -> bool:
        """True while text is still being typed out or waits in the queue"""
        return self._typing_timer.isActive() or bool(self._queue)

    def clear_screen(self) -> None:
        """Clears the screen and aborts any ongoing typing effect"""
        self._typing_timer.stop()
        self._queue.clear()
        self._segments = None
        self._seg_index = 0
        self._char_index = 0
        self.clear()

    def force_finish_typing(self) -> None:
        """Instantly prints all remaining queued text and stops the timer"""
        if not self._typing_timer.isActive() and not self._queue:
            return

        self._typing_timer.stop()

        if self._segments is not None:
            for i in range(self._seg_index, len(self._segments)):
                text, color, family, size = self._segments[i]
                start = self._char_index if i == self._seg_index else 0

                if start < len(text):
                    self._insert_segment((text[start:], color, family, size))

            self._segments = None
            self._seg_index = 0
            self._char_index = 0

        while self._queue:
            for seg in self._queue.popleft():
                self._insert_segment(seg)

        self._scroll_to_bottom()

    def rescale(self, ratio: float) -> None:
        """Multiplies the point size of every fragment currently on screen by ratio"""
        if ratio == 1.0:
            return

        self.force_finish_typing()
        doc = self.document()

        ranges: list[tuple[int, int, float]] = []
        block = doc.begin()

        while block.isValid():
            it = block.begin()

            while not it.atEnd():
                frag = it.fragment()

                if frag.isValid():
                    size = frag.charFormat().fontPointSize() or BODY_POINT_SIZE
                    ranges.append((frag.position(), frag.length(), size * ratio))

                it += 1

            block = block.next()

        for pos, length, new_size in ranges:
            cursor = QTextCursor(doc)
            cursor.setPosition(pos)
            cursor.setPosition(pos + length, QTextCursor.MoveMode.KeepAnchor)
            fmt = QTextCharFormat()
            fmt.setFontPointSize(new_size)
            cursor.mergeCharFormat(fmt)

    def _process_next_message(self) -> None:
        """Starts typing the next queued message, if any"""
        if not self._queue:
            self._typing_timer.stop()
            return

        self._segments = self._queue.popleft()
        self._seg_index = 0
        self._char_index = 0
        self._typing_timer.start(self._typing_speed_ms)

    def _type_next_char(self) -> None:
        """Skip over any segments already fully typed or empty and type the next character from the current segment"""
        while (
            self._segments is not None
            and self._seg_index < len(self._segments)
            and self._char_index >= len(self._segments[self._seg_index][0])
        ):
            self._seg_index += 1
            self._char_index = 0

        if self._segments is None or self._seg_index >= len(self._segments):
            self._typing_timer.stop()
            self._process_next_message()
            return

        text, color, family, size = self._segments[self._seg_index]
        self._insert_segment((text[self._char_index], color, family, size))
        self._char_index += 1
        self._scroll_to_bottom()

    def _insert_segment(self, seg: Segment) -> None:
        """Inserts a single styled segment at the end of the screen"""
        text, color_hex, family, size = seg
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color_hex))

        if family:
            fmt.setFontFamily(family)

        if size:
            fmt.setFontPointSize(size)

        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self.setTextCursor(cursor)

    def _scroll_to_bottom(self) -> None:
        """Scrolls the screen to the bottom so the latest text is visible"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def mousePressEvent(self, event) -> None:
        """Clicking inside the screen instantly finishes the typewriter animation"""
        super().mousePressEvent(event)
        self.force_finish_typing()


class TerminalView(QWidget):
    """The terminal screen: an output area with a typewriter effect and an integrated console input line at the bottom used for login, password and the retakes count"""
    line_entered = pyqtSignal(str)

    COLOR_MAP = {
        "primary": COLOR_TEXT,
        "bright": COLOR_PRIMARY,
        "info": COLOR_ACCENT,
        "error": COLOR_ERROR,
        "number": COLOR_NUMBER,
    }

    SCALE_MIN = 0.6
    SCALE_MAX = 2.2
    SCALE_STEP = 0.1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("terminal_screen")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._output = OutputScreen(self)
        self._input = QLineEdit(self)
        self._input.setObjectName("console_input")
        self._input.setPlaceholderText("")
        self._input.returnPressed.connect(self._on_return_pressed)

        layout.addWidget(self._output, stretch=1)
        layout.addWidget(self._input)

        self._heading_family: str | None = None
        self._heading_base = HEADING_POINT_SIZE
        self._body_base = BODY_POINT_SIZE
        self._scale = 1.0

        self._int_validator = QIntValidator(0, 999, self)
        self._is_password = False
        self.set_input_enabled(False)

    def set_heading_font(self, family: str, point_size: int | None = None) -> None:
        """Sets the pixel display font used for heading lines"""
        self._heading_family = family
        if point_size is not None:
            self._heading_base = point_size

    def increase_font(self) -> None:
        """Increases the font size of all text on screen by SCALE_STEP"""
        self._set_scale(self._scale + self.SCALE_STEP)

    def decrease_font(self) -> None:
        """Decreases the font size of all text on screen by SCALE_STEP"""
        self._set_scale(self._scale - self.SCALE_STEP)

    def print_line(
        self,
        text: str,
        msg_type: str = "primary",
        *,
        heading: bool = False,
        typewriter: bool = True
    ) -> None:
        """Prints a single line in the specified color"""
        color = self.COLOR_MAP.get(msg_type, COLOR_TEXT)

        if heading:
            family, size = self._heading_family, self._heading_size()
        else:
            family, size = None, self._body_size()

        self._output.print_segments([(text + "\n", color, family, size)], typewriter=typewriter)

    def print_kv(
        self,
        label: str,
        value,
        *,
        value_suffix: str = "",
        msg_type: str = "primary",
        typewriter: bool = True
    ) -> None:
        """Prints a label followed by value in turquoise, then an optional value_suffix back in msg_type color"""
        base = self.COLOR_MAP.get(msg_type, COLOR_TEXT)
        number = self.COLOR_MAP["number"]
        size = self._body_size()
        segments: list[Segment] = [(label, base, None, size), (str(value), number, None, size)]

        if value_suffix:
            segments.append((value_suffix, base, None, size))

        segments.append(("\n", base, None, size))
        self._output.print_segments(segments, typewriter=typewriter)

    def print_empty_line(self) -> None:
        """Prints an empty line to the screen"""
        self.print_line("", typewriter=False)

    def clear_screen(self) -> None:
        """Clears the screen and aborts any ongoing typing effect"""
        self._output.clear_screen()

    @property
    def output(self) -> OutputScreen:
        """Returns the OutputScreen widget for direct access"""
        return self._output

    def request_input(self, prompt: str, *, password: bool = False, numeric: bool = False) -> None:
        """Prints a prompt and enables the console input line for one submission"""
        if prompt:
            self.print_line(prompt, "info")

        self._is_password = password
        self._input.setEchoMode(QLineEdit.EchoMode.Password if password else QLineEdit.EchoMode.Normal)
        self._input.setValidator(self._int_validator if numeric else None)
        self._input.clear()
        self.set_input_enabled(True)

    def set_input_enabled(self, enabled: bool) -> None:
        """Shows/enables or hides/disables the console input line"""
        self._input.setEnabled(enabled)
        self._input.setVisible(enabled)

        if enabled:
            self._input.setFocus()

    def _body_size(self) -> float:
        """Returns the current point size of body text, scaled by the current scale factor"""
        return self._body_base * self._scale

    def _heading_size(self) -> float:
        """Returns the current point size of heading text, scaled by the current scale factor"""
        return self._heading_base * self._scale

    def _set_scale(self, new_scale: float) -> None:
        """Sets the scale factor for all text on screen and rescales the output area"""
        new_scale = max(self.SCALE_MIN, min(self.SCALE_MAX, round(new_scale, 2)))

        if new_scale == self._scale:
            return

        ratio = new_scale / self._scale
        self._scale = new_scale
        self._output.rescale(ratio)

    def _on_return_pressed(self) -> None:
        """Handles the user pressing Enter in the console input line""" 
        text = self._input.text()

        if text == "":
            return

        echo = "*" * len(text) if self._is_password else text
        self.print_line(f"> {echo}", "primary", typewriter=False)

        self._input.clear()
        self.set_input_enabled(False) # Lock input until the controller requests the next line
        self.line_entered.emit(text)
