import sys
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLabel, QLineEdit, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from stylesheet import WINDOW_STYLESHEET  
from summary import summarise_news, google_search   # your backend


# -----------------------------
# WORKER (runs in background)
# -----------------------------
class Worker(QObject):
    finished = pyqtSignal(str, list)     # send result back to UI thread

    def run(self, query):
        news_results = google_search(query)
        if not news_results:
            self.finished.emit("No news articles found.")
            return

        response, urls = summarise_news(query, news_results)
        self.finished.emit(response, urls)


# -----------------------------
# CHAT BUBBLES
# -----------------------------
class ChatBubble(QLabel):
    def __init__(self, text, is_user=False):
        super().__init__(text)
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        # Use object names instead of inline styles
        if is_user:
            self.setObjectName("UserBubble")
        else:
            self.setObjectName("AssistantBubble")

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)


class AssistantBubble(QWidget):
    def __init__(self, text, urls, toggle_callback):
        super().__init__()

        self.urls = urls
        layout = QVBoxLayout(self)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setObjectName("AssistantBubble")
        layout.addWidget(label)

        if urls:  # only show button when URLs exist
            btn = QPushButton("Sources")
            btn.clicked.connect(lambda: toggle_callback(urls))
            layout.addWidget(btn)


# -----------------------------
# MAIN WINDOW
# -----------------------------
class ChatGPTWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Clone - PyQt6")
        self.resize(900, 800)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- MAIN HORIZONTAL ROW (chat + side panel) ---
        self.main_row = QHBoxLayout()
        self.main_row.setContentsMargins(0, 0, 0, 0)
        self.main_row.setSpacing(0)

        # --- CHAT SCROLL AREA ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()

        self.scroll.setWidget(self.chat_container)
        self.main_row.addWidget(self.scroll, stretch=1)

        # --- SIDE PANEL (starts hidden) ---
        self.side_panel = QWidget()
        self.side_panel.setFixedWidth(0)
        self.side_panel.setStyleSheet("SidePanel")

        self.side_layout = QVBoxLayout(self.side_panel)
        self.side_layout.setContentsMargins(10, 10, 10, 10)
        self.side_layout.setSpacing(5)
        self.main_row.addWidget(self.side_panel)

        root.addLayout(self.main_row)

        # --- INPUT BAR ---
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask something...")
        self.input.returnPressed.connect(self.send_message)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input)
        input_layout.addWidget(send_btn)

        root.addLayout(input_layout)

        self.setStyleSheet(WINDOW_STYLESHEET)


    def toggle_sources(self, urls):
        if self.side_panel.width() == 0:
            self.side_panel.setFixedWidth(350)

            # Clear old
            for i in reversed(range(self.side_layout.count())):
                widget = self.side_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            title = QLabel("<b>Sources visited</b>")
            title.setStyleSheet("color: white;")
            self.side_layout.addWidget(title)

            for url in urls:
                link = QLabel(f"<a style='color:#33ddff;' href='{url}'>{url}</a>")
                link.setOpenExternalLinks(True)
                self.side_layout.addWidget(link)

            self.side_layout.addStretch()
        else:
            self.side_panel.setFixedWidth(0)




    # Add message bubble safely on UI thread
    def add_message(self, text, is_user=False, urls=None):
        if is_user:
            bubble = ChatBubble(text, is_user=True)
        else:
            bubble = AssistantBubble(text, urls, self.toggle_sources)

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
    def handle_result(self, result_text, urls):
        self.add_message(result_text, is_user=False, urls=urls)



# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatGPTWindow()
    window.show()
    sys.exit(app.exec())
