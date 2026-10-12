from PyQt6 import QtGui
from PyQt6.QtWidgets import QLabel, QSizePolicy, QWidget, QVBoxLayout

class AnswerBubble(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
class AutoWrapLabel(QLabel):
    def __init__(self, max_width=200, parent=None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setScaledContents(True)
        self.setMaximumWidth(max_width)
        self.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                border-radius: 10px;
                background-color: #6C82FF;
                padding: 8px;
            }
        """)
        self.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Minimum
        )

    def setText(self, a0: str):
        super().setText(a0)
        self.adjustSize()
    def setMovie(self, movie: QtGui.QMovie) -> None:
        super().setMovie(movie)
        self.adjustSize()