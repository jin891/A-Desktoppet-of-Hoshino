import sys

from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QPixmap, QMouseEvent, QTransform
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import jsontool as jt


class MainWindow(QWidget):
    leftclicked = pyqtSignal()
    rightclicked = pyqtSignal()
    leftreleased = pyqtSignal()
    rightreleased = pyqtSignal()
    start_clicked_left = pyqtSignal()
    start_clicked_right = pyqtSignal()
    is_moving = pyqtSignal(QPoint)
    is_Draging = False
    shouldSetFixedSize = False
    is_folding = False
    Image_size = jt.get_value("settings.json", "MainBodySize")
    NowPixmapis = r"pngs/Main.png"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._offset = None
        self.LongClickActivateTime = jt.get_value('settings.json', 'LongClickActivate')
        self.initial_geometry = QRect(0, 0, 0, 0)
        self.label = QLabel()
        self.label.setScaledContents(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.start_clicked_left.connect(self.IsDraging)
        #self.setStyleSheet("background-color: #3498db;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ChangeToMain()
        self.sleep_timer = QTimer()
        self.deep_sleep_timer = QTimer()
        self.sleep_timer.setSingleShot(True)
        self.deep_sleep_timer.setSingleShot(True)
        self.sleep_timer.timeout.connect(self.Tosleep)
        self.deep_sleep_timer.timeout.connect(self.ToDeepsleep)
        self.leftlongclick_timer = QTimer()
        self.leftlongclick_timer.setSingleShot(True)
        self.leftlongclick_timer.timeout.connect(self.start_clicked_left.emit)
        self.rightlongclick_timer = QTimer()
        self.rightlongclick_timer.setSingleShot(True)
        self.rightlongclick_timer.timeout.connect(self.start_clicked_right.emit)
        self.animation = QPropertyAnimation(self.label, b"geometry")
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)


    def isBeUrged(self):
        self.Change_Image(QPixmap(r"pngs/Draging.png"))
        self.NowPixmapis = r"pngs/Draging.png"
    def ChangeToMain(self):
        self.Change_Image(QPixmap(r"pngs/Main.png"))
        self.NowPixmapis = r"pngs/Main.png"
    def Tosleep(self):
        self.Change_Image(QPixmap(r"pngs/Sleep.png"))
        self.NowPixmapis = r"pngs/Sleep.png"
    def ToDeepsleep(self):
        self.Change_Image(QPixmap(r"pngs/DeepSleep.png"))
        self.NowPixmapis = r"pngs/DeepSleep.png"
    def ToEnjoyClick(self):
        self.shouldSetFixedSize = True
        print("T1")
        self.Change_Image(QPixmap(r"pngs/EnjoyClick.png"))
        self.NowPixmapis = r"pngs/EnjoyClick.png"
    def IsDraging(self):
        self.is_Draging = True
        if not self.is_folding:
            self.shouldSetFixedSize = True
            print("T2")
            self.Change_Image(QPixmap(r"pngs/Draging.png"))
            self.NowPixmapis = r"pngs/Draging.png"
    def changeSize(self, width: int):
        self.Image_size = width
        self.Change_Image(QPixmap(self.NowPixmapis))
    def ToSmall(self, is_Tosmall: bool, WhichEdge = "bottom"):
        if is_Tosmall:
            self.is_folding = True
            self.NowPixmapis = r"pngs/Small.png"
            self.changeSize(100)
            if WhichEdge == "bottom":
                self.Change_Image(QPixmap(self.NowPixmapis), 0)
            elif WhichEdge == "top":
                self.Change_Image(QPixmap(self.NowPixmapis), 180)
            elif WhichEdge == "left":
                self.Change_Image(QPixmap(self.NowPixmapis), 90)
            elif WhichEdge == "right":
                self.Change_Image(QPixmap(self.NowPixmapis), 270)
        else:
            self.is_folding = False
            self.NowPixmapis = r"pngs/Main.png"
            self.changeSize(jt.get_value('settings.json', 'MainBodySize'))


    def Change_Image(self, pixmap, Angel = 0):
        if pixmap.isNull():
            print("load image error")
            return
        target_width = self.Image_size
        rotated_pixmap = pixmap.transformed(QTransform().rotate(Angel))
        if rotated_pixmap.isNull():
            print("cannot transform image")
            return
        self.label.setPixmap(rotated_pixmap)
        self.setFixedSize(target_width, int(target_width * pixmap.height() / pixmap.width()))
        self.adjustSize()
        self.initial_geometry = self.label.geometry()
        if self.shouldSetFixedSize:
            self.label.setGeometry(self.get_ani_target_size())



    def click_animation(self, is_Tosmall: bool):
        self.animation.stop()
        if not is_Tosmall:
            self.animation.setStartValue(self.get_ani_target_size())
            self.animation.setEndValue(self.initial_geometry)
        else:
            self.animation.setStartValue(self.initial_geometry)
            self.animation.setEndValue(self.get_ani_target_size())
        self.animation.setDuration(int(jt.get_value('settings.json', 'AnimationTime') / 2))
        self.animation.start()

    def get_ani_target_size(self):
        target_w = int(self.initial_geometry.width() * (1 + (jt.get_value('settings.json', 'AnimationStrength') / 10)))
        target_h = int(self.initial_geometry.height() * (1 - (jt.get_value('settings.json', 'AnimationStrength') / 10)))
        center_x = self.initial_geometry.x() + self.initial_geometry.width() / 2
        center_y = self.initial_geometry.y() + self.initial_geometry.height() / 2
        target_geometry = QRect(
            int(center_x - target_w / 2),
            int(center_y - target_h / 2),
            target_w,
            target_h
        )
        return target_geometry

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.LongClickActivateTime = jt.get_value('settings.json', 'LongClickActivate')
        self.click_animation(True)
        if event.button() == Qt.MouseButton.LeftButton:
            self._offset = event.globalPosition().toPoint() - self.window().pos()
            self.leftlongclick_timer.start(self.LongClickActivateTime)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightlongclick_timer.start(self.LongClickActivateTime)
        event.accept()
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.click_animation(False)
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftreleased.emit()
            self.is_Draging = False
            QTimer.singleShot(50, lambda: self._shouldSetFixedSize(False))
            if self.leftlongclick_timer.isActive():
                self.leftclicked.emit()
                self.leftlongclick_timer.stop()
            self.leftreleased.emit()
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightreleased.emit()
            QTimer.singleShot(50, lambda: self._shouldSetFixedSize(False))
            if self.rightlongclick_timer.isActive():
                self.rightclicked.emit()
                self.rightlongclick_timer.stop()
            self.rightreleased.emit()
        event.accept()
    def _shouldSetFixedSize(self, should: bool):
        self.shouldSetFixedSize = should
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.is_Draging:
            self.is_moving.emit(event.globalPosition().toPoint())

class Controller:
    def __init__(self, sleep_timer_widget, deep_sleep_timer_widget):
        self.sleep_timer = sleep_timer_widget
        self.deep_sleep_timer = deep_sleep_timer_widget
    def StopTimer(self):
        if self.sleep_timer.isActive():
            self.sleep_timer.stop()
            self.deep_sleep_timer.stop()
    def StartTimer(self):
        sleeptime = jt.get_value("settings.json", "SLEEP_TIME") * 1000
        deepsleeptime = jt.get_value("settings.json", "DEEP_SLEEP_TIME") * 1000
        self.sleep_timer.start(sleeptime)
        self.deep_sleep_timer.start(deepsleeptime)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())