WINDOW_STYLESHEET = """
        QWidget {
            background-color: #131416;
            color: #ECECEC;
            font-family: "Segoe UI", "SF Pro Text", Arial, sans-serif;
            font-size: 14px;
        }

        QScrollArea {
            border: none;
            background-color: #131416;
        }

        #ChatContainer {
            background-color: #131416;
        }

        /* Chat bubbles */
        QLabel#UserBubble {
            background-color: #10A37F;
            color: #FFFFFF;
            border-radius: 14px;
            padding: 10px 12px;
            margin: 4px 40px 4px 80px;  /* push to right */
        }

        QLabel#AssistantBubble {
            background-color: #1F2125;
            color: #ECECEC;
            border-radius: 14px;
            padding: 10px 12px;
            margin: 4px 80px 4px 40px;  /* push to left */
            border: 1px solid #2A2D33;
        }

        /* Input bar */
        QLineEdit {
            background-color: #1F2125;
            border-radius: 10px;
            padding: 10px 12px;
            border: 1px solid #2F3338;
            color: #ECECEC;
            selection-background-color: #10A37F;
        }

        QLineEdit:focus {
            border: 1px solid #10A37F;
        }

        /* Send button */
        QPushButton {
            background-color: #10A37F;
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 10px 18px;
            font-weight: 600;
            min-width: 80px;
        }

        QPushButton:hover {
            background-color: #15B892;
        }

        QPushButton:pressed {
            background-color: #0E8C6D;
        }

        QPushButton:disabled {
            background-color: #2F3338;
            color: #7A7A7A;
        }

        QScrollBar:vertical {
            background: #131416;
            width: 10px;
            margin: 0px;
        }

        QScrollBar::handle:vertical {
            background: #3A3D42;
            min-height: 20px;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical:hover {
            background: #4A4E54;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }

        #SidePanel {
            background-color: #121212;
            border-left: 1px solid #333;
        }

        #SidePanel QLabel {
            color: white;
        }

        """