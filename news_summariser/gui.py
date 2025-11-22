import sys
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLabel, QLineEdit, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal

from summary import summarise_news, google_search   # your backend


# -----------------------------
# WORKER (runs in background)
# -----------------------------
class Worker(QObject):
    finished = pyqtSignal(str)     # send result back to UI thread

    def run(self, query):
        news_results = google_search(query)
        if not news_results:
            self.finished.emit("No news articles found.")
            return

        response = summarise_news(query, news_results)
        self.finished.emit(response)


# -----------------------------
# CHAT BUBBLES
# -----------------------------
class ChatBubble(QLabel):
    def __init__(self, text, is_user=False):
        super().__init__(text)
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setStyleSheet(
            f"""
            background-color: {'#DCF8C6' if is_user else '#E6E6E6'};
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            """
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)


# -----------------------------
# MAIN WINDOW
# -----------------------------
class ChatGPTWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Clone - PyQt6")
        self.resize(700, 800)

        main_layout = QVBoxLayout(self)

        # SCROLL AREA
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()

        self.scroll.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll)

        # INPUT BAR
        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask something...")
        self.input.returnPressed.connect(self.send_message)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input)
        input_layout.addWidget(send_btn)

        main_layout.addLayout(input_layout)

    # Add message bubble safely on UI thread
    def add_message(self, text, is_user=False):
        bubble = ChatBubble(text, is_user=is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)

        QApplication.processEvents()
        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        )

    def send_message(self):
        text = self.input.text().strip()
        if not text:
            return

        # show user's message
        self.add_message(text, is_user=True)
        self.input.clear()

        # create worker for background work
        self.worker = Worker()
        self.worker.finished.connect(self.handle_result)

        thread = threading.Thread(target=self.worker.run, args=(text,))
        thread.start()

    # RECEIVE result safely on main UI thread
    def handle_result(self, result_text):
        self.add_message(result_text, is_user=False)


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatGPTWindow()
    window.show()
    sys.exit(app.exec())
