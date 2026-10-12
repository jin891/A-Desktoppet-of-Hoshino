import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtCore import QObject, QThread
from openai import AuthenticationError

from llm import *
import jsontool as jt

from PyQt6 import QtWidgets


class lineEdit(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(471, 41)
        self.horizontalLayout = QHBoxLayout()
        self.setLayout(self.horizontalLayout)
        self.horizontalLayout.setContentsMargins(5, 0, 5, 0)
        self.horizontalLayout.setSpacing(5)
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setStyleSheet("QLineEdit {\n"
"    border: 2px solid #DDDDDD;\n"
"    border-radius: 15px;\n"
"    padding: 7px 10px;\n"
"    background-color: #ffffff;\n"
"    font-size: 15px;\n"
"}\n"
"QLineEdit:focus {\n"
"    border-color: #6C82FF;\n"
"    background-color: #FFFFFF;\n"
"}")
        self.horizontalLayout.addWidget(self.lineEdit)

        self.Send_botton = QtWidgets.QPushButton("↑")
        self.Send_botton.setStyleSheet("QPushButton {\n"
"    border: 5px solid #6B81FE;\n"
"    border-radius: 15px;\n"
"    background-color: #6C82FF;\n"
"    color: white;\n"
"    padding: 6px 12px;\n"
"}")
        self.horizontalLayout.addWidget(self.Send_botton)
        self.recognize_screen_button = QtWidgets.QPushButton("识别屏幕")
        self.recognize_screen_button.setStyleSheet("QPushButton {\n"
"    border: 5px solid #6B81FE;\n"
"    border-radius: 15px;\n"
"    background-color: #6C82FF;\n"
"    color: white;\n"
"    padding: 6px 12px;\n"
"}")
        self.horizontalLayout.addWidget(self.recognize_screen_button)


class EditLine(QWidget):
    isAnswering = pyqtSignal(str)
    _isAnswering = pyqtSignal(str)
    response_start = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.main_layout = QVBoxLayout()
        self.Inputline = lineEdit()
        self.main_layout.addWidget(self.Inputline)
        self.setLayout(self.main_layout)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.GetAnswer = GetAnswer()
        self.AnswerThread = QThread()
        self.GetAnswer.moveToThread(self.AnswerThread)
        self.AnswerThread.start()
        self.AnswerTag = True
        self.Inputline.Send_botton.clicked.connect(lambda: self.ControlClass("Talk"))
        self.Inputline.recognize_screen_button.clicked.connect(lambda: self.ControlClass("RecScreen"))
        self._isAnswering.connect(self.GetAnswer.SendToLLM)
    def ControlClass(self, pattern_is: str):
        if self.AnswerTag:
            self.AnswerTag = False
            if pattern_is == "Talk":
                try:
                    self.isAnswering.disconnect()
                except TypeError:
                    pass
                self.response_start.emit()
                self.isAnswering.connect(self.GetAnswer.SendToLLM)
                self.isAnswering.emit(self.Inputline.lineEdit.text())
                self.Inputline.lineEdit.clear()
            elif pattern_is == "RecScreen":
                try:
                    self.isAnswering.disconnect()
                except TypeError:
                    pass
                self.response_start.emit()
                self.isAnswering.connect(self.GetAnswer.recognize_screen_inside)
                self.isAnswering.emit(self.Inputline.lineEdit.text())
                self.Inputline.lineEdit.clear()

    def isBeUrge(self):
        self._isAnswering.emit("(你正在被sensei批评)" + self.Inputline.lineEdit.text())
        self.Inputline.lineEdit.clear()
        self.response_start.emit()
    def isBeEncouraged(self):
        self._isAnswering.emit("(你正在被sensei鼓励/关爱)" + self.Inputline.lineEdit.text())
        self.Inputline.lineEdit.clear()
        self.response_start.emit()
class GetAnswer(QObject):
    response_ready = pyqtSignal(str)
    response_end = pyqtSignal()
    api_error = pyqtSignal(str)
    def SendToLLM(self, question_is):
        isStream = jt.get_value('settings.json', 'isStream')
        WordToLLM = question_is
        self.write_question(WordToLLM)
        if not isStream:
            try:
                respon = get_llm_respon(WordToLLM)
                self.write_respon(respon)
                self.response_ready.emit(respon)
            except AuthenticationError:
                self.api_error.emit("API_KEY错误")
        else:
            try:
                content = get_llm_stream(WordToLLM)
                respon = ""
                for chunk in content:
                    respon += chunk
                    self.response_ready.emit(respon)
                self.write_respon(respon)
            except AuthenticationError:
                self.api_error.emit("API_KEY错误")
    def recognize_screen_inside(self, question_is):
        WordToLLM = question_is
        now = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
        screenshot = pyautogui.screenshot(region=None)
        screenshot.save("saves/" + now)
        buffered = io.BytesIO()
        screenshot.save(buffered, format='PNG')
        picturebase64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        isStream = jt.get_value('settings.json', 'isStream')
        self.write_question(WordToLLM, now)
        if not isStream:
            try:
                respon = recognize_screen_respon(WordToLLM, picturebase64)
                self.write_respon(respon)
                self.response_ready.emit(respon)
            except AuthenticationError:
                self.api_error.emit("API_KEY错误")
        else:
            try:
                content = recognize_screen_stream(WordToLLM, picturebase64)
                respon = ""
                for chunk in content:
                    respon += chunk
                    self.response_ready.emit(respon)
                self.write_respon(respon)
            except AuthenticationError:
                self.api_error.emit("API_KEY错误")
    def write_question(self, content, image = None):
        with open('lines.jsonl', 'a', encoding='utf-8') as f:
            if not content == "":
                jsonstr = {"InputFromSelf": content}
                f.write(json.dumps(jsonstr, ensure_ascii=False) + '\n')
            else:
                jsonstr = {"InputFromSelf": "(什么也没说)"}
                f.write(json.dumps(jsonstr, ensure_ascii=False) + '\n')
        if image is not None:
            with open('lines.jsonl', 'a', encoding='utf-8') as f:
                jsonstr = {"Image": image}
                f.write(json.dumps(jsonstr, ensure_ascii=False) + '\n')
    def write_respon(self, content):
        self.response_end.emit()
        with open('lines.jsonl', 'a', encoding='utf-8') as f:
                jsonstr = {"InputFromLLM": content}
                f.write(json.dumps(jsonstr, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditLine()
    window.show()
    sys.exit(app.exec())
