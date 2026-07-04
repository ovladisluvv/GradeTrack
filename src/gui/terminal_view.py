from collections import deque
from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor

from gui import COLOR_PRIMARY, COLOR_ACCENT, COLOR_ERROR


class TerminalView(QTextBrowser):
    """A text browser that simulates a terminal display. Features a typewriter effect where characters appear one by one"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setOpenExternalLinks(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameStyle(0)

        # Typewriter effect state
        self._typing_timer = QTimer(self)
        self._typing_timer.timeout.connect(self._type_next_char)
        self._typing_speed_ms = 15  # Speed of typing in milliseconds

        self._queue = deque()
        self._current_text = ""
        self._current_color = None
        self._current_index = 0

    def print_line(self, text: str, msg_type: str = "primary", typewriter: bool = True):
        """Queues a line of text to be printed. If typewriter is True, text will appear one by one"""
        color_map = {
            "primary": COLOR_PRIMARY,
            "info": COLOR_ACCENT,
            "error": COLOR_ERROR
        }
        color = color_map.get(msg_type, COLOR_PRIMARY)

        if not typewriter:
            # Bypass queue and print instantly
            self.force_finish_typing()
            self._insert_text_with_color(text + "\n", color)
            self._scroll_to_bottom()
            return

        self._queue.append((text + "\n", color))

        if not self._typing_timer.isActive():
            self._process_next_message()

    def print_empty_line(self):
        """Prints a blank line"""
        self.print_line("")

    def clear_screen(self):
        """Clears the terminal and aborts any ongoing typing effect"""
        self._typing_timer.stop()
        self._queue.clear()
        self._current_text = ""
        self._current_color = None
        self._current_index = 0
        self.clear()

    def force_finish_typing(self):
        """Instantly prints all remaining queued text and stops the timer"""
        if not self._typing_timer.isActive() and not self._queue:
            return

        self._typing_timer.stop()

        # Flush currently typing text
        if self._current_text and self._current_index < len(self._current_text):
            remaining_text = self._current_text[self._current_index:]
            self._insert_text_with_color(remaining_text, self._current_color)
            self._current_text = ""
            self._current_color = None
            self._current_index = 0

        # Flush the entire queue
        while self._queue:
            text, color = self._queue.popleft()
            self._insert_text_with_color(text, color)

        self._scroll_to_bottom()

    def _process_next_message(self):
        """Loads the next message from the queue and starts the typing timer"""
        if not self._queue:
            self._typing_timer.stop()
            return

        self._current_text, self._current_color = self._queue.popleft()
        self._current_index = 0
        self._typing_timer.start(self._typing_speed_ms)

    def _type_next_char(self):
        """Types a single character and advances the index"""
        if self._current_index >= len(self._current_text):
            self._typing_timer.stop()
            self._process_next_message()
            return

        char = self._current_text[self._current_index]
        self._insert_text_with_color(char, self._current_color)
        self._current_index += 1
        self._scroll_to_bottom()

    def _insert_text_with_color(self, text: str, color_hex: str):
        """Inserts raw text at the end of the document with the specified color format"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color_hex))
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self.setTextCursor(cursor)

    def _scroll_to_bottom(self):
        """Ensures the scrollbar stays at the very bottom so new text is visible"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def mousePressEvent(self, event):
        """If the user clicks inside the terminal view, instantly finish typing"""
        super().mousePressEvent(event)
        self.force_finish_typing()
