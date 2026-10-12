import os
import sys, json
from PyQt6.QtGui import QPixmap, QMouseEvent
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QScrollArea, QPushButton,
    QSizePolicy, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtCore import QTimer
class SureTodo(QMainWindow):
    IsMakeSure = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 10, 0, 0)
        self.resize(200, 100)
        self.setWindowTitle("")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.Yes = QPushButton("是")
        self.No = QPushButton("否")
        self.setStyleSheet("background-color: #141416;")
        self.Yes.setStyleSheet("color: #FFFFFF;background-color: #44454A;border-radius: 5px;border: 1px solid #000000")
        self.No.setStyleSheet("color: #FFFFFF;background-color: #44454A;border-radius: 5px;border: 1px solid #000000")
        self.TextLabel = QLabel("确定删除回忆？")
        self.TextLabel.setStyleSheet("color: #FFFFFF;")
        self.main_layout.addWidget(self.TextLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.No)
        self.button_layout.addWidget(self.Yes)
        self.Yes.clicked.connect(self.ChooseYes)
        self.No.clicked.connect(self.ChooseNo)
        self.button_layout.setContentsMargins(10, 10, 5, 5)
        self.button_layout.setSpacing(20)
        self.main_layout.addLayout(self.button_layout)
        self.setWindowTitle("确认")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
        )
    def ChooseYes(self):
        self.IsMakeSure.emit(True)
        self.hide()
    def ChooseNo(self):
        self.IsMakeSure.emit(False)
        self.hide()
class MessageBubble(QWidget):
    left_clicked = pyqtSignal(str)
    right_clicked = pyqtSignal()
    is_deletelater = False
    def __init__(self, text = None, is_image = False, is_self=False, parent=None):
        super().__init__(parent)
        self.text = text
        self.is_image = is_image
        self.deleteCheckBox = QCheckBox()
        self.deleteCheckBox.setText("")
        self.deleteCheckBox.setStyleSheet("""
            QCheckBox {
                padding: 0px;
                margin: 0px;
                spacing: 0px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """)
        self.deleteCheckBox.setChecked(self.is_deletelater)
        self.deleteCheckBox.toggled.connect(self._is_deletelater)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        if not is_image:
            self.label = QLabel(text)
        else:
            self.label = QLabel(text)
            pixmap = QPixmap(r"saves/" + text)
            self.label.setPixmap(pixmap)
            self.label.setFixedSize(200, int(200 / pixmap.width() *pixmap.height()))
            self.label.setScaledContents(True)
        self.label.setStyleSheet("padding: 2px; color: white;")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop |
        Qt.AlignmentFlag.AlignLeft)

        self.label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.label.setMaximumWidth(200)
        self.label.adjustSize()
        if is_self:
            layout.addStretch()
            layout.addWidget(self.label)
            layout.addWidget(self.deleteCheckBox)
        else:
            layout.addWidget(self.deleteCheckBox)
            layout.addWidget(self.label)
            layout.addStretch()
        self.deleteCheckBox.hide()
        self.setStyleSheet("""
            QWidget {
                background-color: #7A9BFF;
                border-radius: 10px;
                border: 1px solid;
            }
        """)
        if not is_self:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2C2C2E;
                    border-radius: 10px;
                    border: 1px solid;
                }
            """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_image:
                self.left_clicked.emit(self.text)
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_clicked.emit()
    def _is_deletelater(self, is_deletelater: bool):
        self.is_deletelater = is_deletelater
        self.deleteCheckBox.setChecked(is_deletelater)
    def is_show_or_hide(self ,is_show_or_hide = None):
        if is_show_or_hide is None:
            if self.deleteCheckBox.isVisible():
                self.deleteCheckBox.hide()
            else:
                self.deleteCheckBox.show()
        else:
            self.deleteCheckBox.setVisible(is_show_or_hide)
    def setText(self, text):
        self.label.setText(text)
        self.label.adjustSize()

class ImageView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scrollarea = QScrollArea()
        self.scrollarea.setWidgetResizable(False)
        self.label = QLabel()
        self.resize(800, 600)
        self.label.setScaledContents(True)
        self.scrollarea.setWidget(self.label)
        self.setCentralWidget(self.scrollarea)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
        )
    def changewindow(self, title, image):
        self.setWindowTitle(title)
        self.label.setPixmap(QPixmap("saves/" + image))
        self.label.resize(int(QPixmap("saves/" + image).size().width() * 0.5), int(QPixmap("saves/" + image).size().height() * 0.5))

class HistoryWindow(QMainWindow):
    ShowAll = pyqtSignal()
    HideAll = pyqtSignal(bool)
    is_changed = pyqtSignal()
    ChooseAll = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.deleteLater = []
        self.resize(400, 600)
        self.setStyleSheet("background-color: #141416;")
        self.setWindowTitle("回忆")
        self.cleanbutton = QPushButton("删除")
        self.ChooseAllbutton = QPushButton("全选")
        self.is_ChoseAll = True
        self.refreshbutton = QPushButton("刷新")
        self.button_layout = QHBoxLayout()
        self.SureTodo = SureTodo()
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.ImageView = ImageView()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.main_layout.addWidget(self.scroll_area)

        self.messages_widget = QWidget()
        self.messages_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.scroll_area.setWidget(self.messages_widget)

        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.setSpacing(0)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        self.ReFresh()
        self.is_changed.connect(self._check_all)
        self.SureTodo.IsMakeSure.connect(self.clean)
        self.button_layout.addWidget(self.cleanbutton)
        self.button_layout.addWidget(self.ChooseAllbutton)
        self.button_layout.addWidget(self.refreshbutton)
        self.main_layout.addLayout(self.button_layout)
        self.button_layout.setContentsMargins(10, 2, 10, 10)
        self.cleanbutton.setStyleSheet("background-color: #44454A;border-radius: 5px;")
        self.ChooseAllbutton.setStyleSheet("background-color: #44454A;border-radius: 5px;")
        self.refreshbutton.setStyleSheet("background-color: #44454A;border-radius: 5px;")
        self.refreshbutton.clicked.connect(self.ReFresh)
        self.cleanbutton.clicked.connect(lambda: self.SureTodo.show())
        self.scroll_to_bottom()
        self.ChooseAllbutton.hide()
        self.cleanbutton.hide()
        self.ChooseAllbutton.clicked.connect(self._choose_all)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
        )
    def add_message(self, text = None, image = None, is_self=False): #会重复执行
        if text is not None:
            bubble = MessageBubble(text, False, is_self)
            self.ShowAll.connect(bubble.is_show_or_hide)
            bubble.deleteCheckBox.clicked.connect(lambda _text: self.is_changed.emit())
            bubble.right_clicked.connect(self.ShowAll.emit)
            self.HideAll.connect(bubble.is_show_or_hide)
            self.ChooseAll.connect(bubble._is_deletelater)
            self.messages_layout.addWidget(bubble)
            bubble.right_clicked.connect(self._is_show_or_hide)
        elif image is not None:
            bubble = MessageBubble(image, True, is_self)
            self.HideAll.connect(bubble.is_show_or_hide)
            bubble.deleteCheckBox.clicked.connect(lambda _text: self.is_changed.emit())
            self.ChooseAll.connect(bubble._is_deletelater)
            bubble.left_clicked.connect(lambda _text: self.ImageView.changewindow(_text, _text))
            bubble.left_clicked.connect(lambda: self.ImageView.show())
            self.ShowAll.connect(bubble.is_show_or_hide)
            bubble.right_clicked.connect(self.ShowAll.emit)
            bubble.right_clicked.connect(self._is_show_or_hide)
            self.messages_layout.addWidget(bubble)
        self.scroll_to_bottom()

    def _is_show_or_hide(self):
        if self.ChooseAllbutton.isVisible():
            self.ChooseAllbutton.hide()
            self.cleanbutton.hide()
        else:
            self.ChooseAllbutton.show()
            self.cleanbutton.show()
    def _init(self):
        self.HideAll.emit(self.ChooseAllbutton.isVisible())
        self.ChooseAllbutton.hide()
        self.cleanbutton.hide()
        self.ChooseAllbutton.setText("全选")
        self.is_ChoseAll = True
    def _choose_all(self):
        if not self.is_ChoseAll:
            self.ChooseAll.emit(False)
        else:
            self.ChooseAll.emit(True)
        self._check_all()
    def _check_all(self):
        if self.check_all():
            self.ChooseAllbutton.setText("取消全选")
            self.is_ChoseAll = False
        else:
            self.ChooseAllbutton.setText("全选")
            self.is_ChoseAll = True
    def check_all(self):
        self.deleteLater = []
        label = True
        if self.messages_layout is not None:
            count = self.messages_layout.count()
            for i in range(count):
                item = self.messages_layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if not widget.is_deletelater:
                        label = False
                    else:
                        if widget.is_image:
                            self.deleteLater.append("is_image:")
                        self.deleteLater.append(widget.text)
        return label



    def scroll_to_bottom(self):
        QTimer.singleShot(100,self._scroll_to_bottom)
    def _scroll_to_bottom(self):
        sb = self.scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    def clean_layout(self):
        if self.messages_layout is not None:
            count = self.messages_layout.count()
            for i in range(count - 1, -1, -1):
                item = self.messages_layout.itemAt(i)
                widget = item.widget()
                if widget is not None:
                    self.messages_layout.takeAt(i)
                    widget.setParent(None)
                    widget.deleteLater()

    def clean(self, is_Sure: bool):
        if is_Sure:
            is_deletelater = False
            templine = []
            self._init()
            with open('lines.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line is not None:
                        data = json.loads(line)
                        for i in range(len(self.deleteLater)):
                            if self.deleteLater[i] == "is_image:":
                                if self.deleteLater[i + 1] == next(iter(data.values())):
                                    print("saves/" + self.deleteLater[i + 1])
                                    os.remove("saves/" + self.deleteLater[i + 1])
                                    is_deletelater = True
                                    break
                            else:
                                if self.deleteLater[i] == next(iter(data.values())):
                                    is_deletelater = True
                                    break
                    if is_deletelater:
                        is_deletelater = False
                        continue
                    templine.append(line)
            with open('lines.jsonl', 'w', encoding='utf-8') as f:
                for line in templine:
                    f.write(line + "\n")
            self.ReFresh()
    def ReFresh(self):
        self.clean_layout()
        try:
            self.ShowAll.disconnect()
            self.ChooseAll.disconnect()
            self.is_changed.disconnect()
            self.HideAll.disconnect()
        except:
            pass
        self._init()
        with open('lines.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    if "InputFromLLM" in data:
                        self.add_message(data["InputFromLLM"], is_self=False)
                    elif "InputFromSelf" in data:
                        self.add_message(data["InputFromSelf"], is_self=True)
                    elif "Image" in data:
                        self.add_message(None, data["Image"], is_self=True)
                    else:
                        continue

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HistoryWindow()
    window.show()
    sys.exit(app.exec())
