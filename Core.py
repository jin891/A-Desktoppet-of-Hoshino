import sys

from PyQt6.QtCore import Qt, QElapsedTimer, QTimer, pyqtSignal, QPoint, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QGuiApplication, QMovie
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QScrollArea

import jsontool as jt
from AnswerBubble import AutoWrapLabel
from InputEditLine import EditLine
from MainBody import MainWindow, Controller
from MainMenu import MainMenu


class ParentWindow(QMainWindow):
    TimerisStarted = False
    is_clicking = False
    isBeUrge = pyqtSignal()
    rightlongclickpattern = True
    isFolding = False
    Input_is_show = True
    GoWhichEdge = ""
    def __init__(self):
        super().__init__()
        self.answerscroll = QScrollArea()
        self.answerscroll.setFixedWidth(215)
        self.answerscroll.setFixedHeight(jt.get_value('settings.json', 'MainBodySize'))
        self.answerscroll.setWidgetResizable(False)
        self.answerscroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.answerscroll.setStyleSheet("QScrollArea { background: transparent; border: none;}")
        self.answerscroll.viewport().setStyleSheet("background: transparent;")
        self.answerscroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.answerscroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.answerscroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.answerscroll.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)

        self.GoBack = QTimer()
        self.GoBack.setSingleShot(True)
        self.isFristClick = True
        self.attClickTimer = QElapsedTimer()
        self.attisFristClick = True
        self.ClickTimer = QElapsedTimer()
        central_widget = QWidget()
        self.top_layout = QHBoxLayout()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        MainWindow.Image_size = jt.get_value('settings.json', 'MainBodySize')
        self.MainBody = MainWindow()
        self.controller = Controller(self.MainBody.sleep_timer, self.MainBody.deep_sleep_timer)
        self.InputEditLine = EditLine()
        self.MainBody.start_clicked_left.connect(self.controller.StopTimer)
        self.MainBody.start_clicked_left.connect(self._is_clicking)
        self.MainBody.is_moving.connect(self._is_moving)
        self.MainBody.leftreleased.connect(self.StartTimer)
        self.MainBody.start_clicked_right.connect(self.controller.StopTimer)
        self.MainBody.start_clicked_right.connect(self._is_clicking)
        self.MainBody.start_clicked_right.connect(self._isBeEncouraged)
        self.MainBody.rightreleased.connect(self.StartTimer)
        self.AnswerBubble = AutoWrapLabel()
        self.answerscroll.setWidget(self.AnswerBubble)
        self.MainMenu = MainMenu()
        self.MainMenu.Settings.sizeischanged.connect(self.changeSize)
        self.InputEditLine.GetAnswer.response_ready.connect(self.GetAnswer)
        self.InputEditLine.response_start.connect(self._WaitForRespon)
        self.InputEditLine.setFixedHeight(50)
        self.InputEditLine.setFixedWidth(481)
        self.InputEditLine.GetAnswer.api_error.connect(self.GetAnswer)
        self.InputEditLine.GetAnswer.api_error.connect(self._isAnsweringTag)
        self.MainBody.leftclicked.connect(self.left_clicked)
        self.MainBody.rightclicked.connect(self.right_clicked)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.MainMenu, alignment=Qt.AlignmentFlag.AlignCenter)
        self.top_layout.addWidget(self.answerscroll, alignment=Qt.AlignmentFlag.AlignCenter)
        self.top_layout.addWidget(self.MainBody, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.answerscroll.hide()
        self.MainMenu.hide()
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addWidget(self.InputEditLine, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addStretch()
        self.InputEditLine.show()
        self.GoBack.timeout.connect(self.MainBody.ChangeToMain)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.adjustSize()
        self.MainMenu.is_killed.connect(lambda: sys.exit(app.exec()))
        self.isBeUrge.connect(self.InputEditLine.isBeUrge)
        self.InputEditLine.GetAnswer.response_end.connect(self._isAnsweringTag)
        self.MainMenu.Tosmall.connect(self._Tosmall)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setContentsMargins(0, 0, 0, 0)

        self.WaitForResponMoive = QMovie(r"gifs/WaitforRespon.gif")

        self.GoEdgeAni = QPropertyAnimation(self.window(), b"geometry")
        self.GoEdgeAni.setEasingCurve(QEasingCurve.Type.OutQuad)
    def _Tosmall(self, is_Tosmall):
        self.GoBack.stop()
        if is_Tosmall:
            self.Nowposition = self.window().pos()
            self.Input_is_show = self.InputEditLine.isVisible()
            self.isFolding = True
            self.InputEditLine.hide()
            self.controller.StopTimer()
            self.GoEdge()
        else:
            self.MainBody.ToSmall(False)
            if self.Input_is_show:
                self.InputEditLine.show()
            self.window().move(self.Nowposition)
            self.isFolding = False
            if (not self.InputEditLine.isVisible()) and (not self.MainMenu.isVisible()):
                self.controller.StartTimer()
    def _isAnsweringTag(self):
        self.InputEditLine.AnswerTag = True
    def _isBeEncouraged(self):
        if not self.isFolding:
            rightlongclickpattern = jt.get_value('settings.json', 'RightLongClickPattern')
            self.MainBody.ToEnjoyClick()
            if rightlongclickpattern:
                if self.InputEditLine.AnswerTag:
                    self.InputEditLine.isBeEncouraged()
                    self.InputEditLine.AnswerTag = False
            else:
                pass
                #self.MainBody.gifanimation()
    def left_clicked(self):
        if not self.isFolding:
            Clickinterval = jt.get_value('settings.json', 'Clickinterval')
            elapsed_ms = 114514
            if self.isFristClick:
                self.ClickTimer.start()
                self.isFristClick = False
            else:
                elapsed_ms = self.ClickTimer.elapsed()
                self.ClickTimer.restart()
            if elapsed_ms < Clickinterval:
                self.MainBody.ToEnjoyClick()
                self.InputEditLine.hide()
                self.AnswerBubble.hide()
                self.MainMenu.hide()
                self.GoBack.start(jt.get_value('settings.json', 'GoBack') * 1000)
                self.controller.StartTimer()
                self.StartTimer()
            else:
                self.MainBody.ChangeToMain()
                if not self.InputEditLine.isVisible():
                    self.controller.StopTimer()
                    self.InputEditLine.show()
                else:
                    if not self.MainMenu.isVisible():
                        self.controller.StartTimer()
                    self.InputEditLine.hide()
                    self.AnswerBubble.hide()
    def right_clicked(self):
        Clickinterval = jt.get_value('settings.json', 'Clickinterval')
        elapsed_ms = 114514
        if self.attisFristClick:
            self.attClickTimer.start()
            self.attisFristClick = False
        else:
            elapsed_ms = self.attClickTimer.elapsed()
            self.attClickTimer.restart()
        if elapsed_ms < Clickinterval and not self.isFolding:
            if self.InputEditLine.AnswerTag:
                self.isBeUrge.emit()
                self.MainBody.isBeUrged()
                self.MainMenu.hide()
                self.GoBack.start(jt.get_value('settings.json', 'GoBack') * 1000)
                self.InputEditLine.AnswerTag = False
        else:
            if not self.MainMenu.isVisible():
                self.answerscroll.hide()
                self.MainMenu.show()
                if not self.InputEditLine.isVisible() and not self.isFolding:
                    self.controller.StopTimer()
                if self.isFolding:
                    self._GoEdge(self.GoWhichEdge)
            else:
                self.MainMenu.hide()
                if not self.InputEditLine.isVisible() and not self.isFolding:
                    self.controller.StartTimer()
                if self.isFolding:
                    self.GoEdge(self.GoWhichEdge)

    def _is_clicking(self):
        self.is_clicking = True
        self.GoBack.stop()
    def _is_moving(self, global_pos):
        self.window().move(global_pos - self.MainBody._offset)
    def StartTimer(self):
        if self.is_clicking and not self.isFolding:
            if (not self.InputEditLine.isVisible()) and (not self.MainMenu.isVisible()):
                self.controller.StartTimer()
            self.GoBack.start(jt.get_value('settings.json', 'GoBack') * 1000)
        self.checkEdge()
        self.is_clicking = False
    def GetAnswer(self, text):
        self.AnswerBubble.setText(text)
        QTimer.singleShot(0, self._scroll_to_bottom)
    def _scroll_to_bottom(self):
        sb = self.answerscroll.verticalScrollBar()
        sb.setValue(sb.maximum())
    def changeSize(self, width: int):
        if not self.isFolding:
            self.MainBody.changeSize(width)
            self.InputEditLine.show()
            self.adjustSize()
        else:
            self.MainBody.Image_size = width
            self.Input_is_show = True
        self.answerscroll.setFixedHeight(jt.get_value('settings.json', 'MainBodySize'))
    def _WaitForRespon(self):
        self.MainMenu.hide()
        self.answerscroll.show()
        self.AnswerBubble.show()
        self.AnswerBubble.setMovie(self.WaitForResponMoive)
        size = jt.get_value('settings.json', "GifAnimationSize")
        self.AnswerBubble.resize(size[0], size[1])
        self.WaitForResponMoive.start()
    def GoEdge(self, GoWhichEdge = None):
        NowWindowPos = self.window().pos()
        NowMainBodyPos = self.MainBody.pos()
        screen_size = QGuiApplication.primaryScreen().geometry()
        NowMainBodySize = self.MainBody.size()
        NowPos = NowWindowPos + NowMainBodyPos + QPoint(int(0.5 * NowMainBodySize.width()), int(0.5 * NowMainBodySize.height()))
        ToTop = NowPos.y() - screen_size.y()
        ToButtom = screen_size.height() - NowPos.y()
        ToLeft = NowPos.x() - screen_size.x()
        ToRight = screen_size.width() - NowPos.x()

        NowWindowGeo = self.window().geometry()
        self.GoEdgeAni.setDuration(200)

        if (min(ToTop, ToButtom, ToLeft, ToRight) == ToTop and GoWhichEdge is None) or GoWhichEdge == "top":
            self.MainBody.ToSmall(True, "top")
            target_geo = QRect(NowWindowPos.x(), 0 , NowWindowGeo.width(), NowWindowGeo.height())
            self.GoEdgeAni.setStartValue(NowWindowGeo)
            self.GoEdgeAni.setEndValue(target_geo)
            self.GoWhichEdge = "top"
            self.GoEdgeAni.start()
        elif (min(ToTop, ToButtom, ToRight) == ToButtom and GoWhichEdge is None) or GoWhichEdge == "bottom":
            self.MainBody.ToSmall(True, "bottom")
            target_geo = QRect(NowWindowPos.x(), screen_size.height() - self.MainBody.pos().y() - self.MainBody.size().height(), NowWindowGeo.width(), NowWindowGeo.height())
            self.GoEdgeAni.setStartValue(NowWindowGeo)
            self.GoEdgeAni.setEndValue(target_geo)
            self.GoWhichEdge = "bottom"
            self.GoEdgeAni.start()
        elif (min(ToTop, ToButtom, ToLeft, ToRight) == ToLeft and GoWhichEdge is None) or GoWhichEdge == "left":
            self.MainBody.ToSmall(True, "left")
            target_geo = QRect(screen_size.x() - self.MainBody.pos().x(), NowWindowPos.y(), NowWindowGeo.width(), NowWindowGeo.height())
            self.GoEdgeAni.setStartValue(NowWindowGeo)
            self.GoEdgeAni.setEndValue(target_geo)
            self.GoWhichEdge = "left"
            self.GoEdgeAni.start()
        elif (min(ToTop, ToButtom, ToLeft, ToRight) == ToRight and GoWhichEdge is None) or GoWhichEdge == "right":
            self.MainBody.ToSmall(True, "right")
            target_geo = QRect(screen_size.width() - self.MainBody.pos().x() - self.MainBody.width(), NowWindowPos.y(), NowWindowGeo.width(), NowWindowGeo.height())
            self.GoEdgeAni.setStartValue(NowWindowGeo)
            self.GoEdgeAni.setEndValue(target_geo)
            self.GoWhichEdge = "right"
            self.GoEdgeAni.start()
    def _GoEdge(self, WhichEdge = "left"):
        screen_size = QGuiApplication.primaryScreen().geometry()
        NowWindowPos = self.window().pos()
        if WhichEdge == "left":
            QTimer.singleShot(0, lambda: self.window().move(screen_size.x() - self.MainMenu.pos().x() ,NowWindowPos.y()))
        elif WhichEdge == "right":
            QTimer.singleShot(0, lambda: self.window().move(screen_size.width() - self.MainBody.pos().x() - self.MainBody.width(), NowWindowPos.y()))
        elif WhichEdge == "top":
            QTimer.singleShot(0, lambda: self.window().move(NowWindowPos.x(), 0))
        elif WhichEdge == "bottom":
            MainMenuY = screen_size.height() - self.MainMenu.pos().y() - self.MainMenu.size().height()
            MainBodyY = screen_size.height() - self.MainBody.pos().y() - self.MainBody.size().height()
            if MainBodyY > MainMenuY:
                QTimer.singleShot(0, lambda: self.window().move(NowWindowPos.x(), MainMenuY))
            else:
                QTimer.singleShot(0, lambda: self.window().move(NowWindowPos.x(), MainBodyY))
    def checkEdge(self):
        if self.isFolding and self.is_clicking:
            self.GoEdge()
            self.is_clicking = False
if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = QGuiApplication.primaryScreen()
    window = ParentWindow()
    window.show()
    sys.exit(app.exec())