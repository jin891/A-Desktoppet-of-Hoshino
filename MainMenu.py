import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMenu

from HistoryBubble import HistoryWindow
from Settings import Settings


class MainMenu(QMenu):
    is_killed = pyqtSignal()
    Tosmall = pyqtSignal(bool)
    Nowparttern = True
    def __init__(self, parent=None):
        super().__init__("MainMenu", parent)
        self.setStyleSheet("""
                    QMenu {
                        border-radius: 10px;  /* 设置圆角大小，值越大越圆 */
                        background-color: white;
                        border: 1px solid #ccc;
                    }
                """)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.HistoryWindow = HistoryWindow()
        self.Settings = Settings()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        history = QAction("回忆", self)
        history.triggered.connect(self.HistoryWindow.show)
        history.triggered.connect(self.HistoryWindow.ReFresh)
        self.addAction(history)

        self.addSeparator()

        settings = QAction("设置", self)
        settings.triggered.connect(self.Settings.show)
        self.addAction(settings)

        self.addSeparator()

        self.foldup = QAction("收起", self)
        self.foldup.triggered.connect(lambda: self.Tosmall.emit(True))
        self.addAction(self.foldup)

        self.addSeparator()

        kill = QAction("退出", self)
        kill.triggered.connect(self.is_killed.emit)
        self.addAction(kill)

        self.Tosmall.connect(self.altparttern)
    def altparttern(self, Tosmall):
        if Tosmall:
            self.foldup.setText("展开")
            self.foldup.triggered.disconnect()
            self.foldup.triggered.connect(lambda: self.Tosmall.emit(False))
        else:
            self.foldup.setText("收起")
            self.foldup.triggered.disconnect()
            self.foldup.triggered.connect(lambda: self.Tosmall.emit(True))
        self.hide()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec())