# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\colorButton.py
try:
    from PySide2.QtCore import Qt, QMimeData, QByteArray, Signal, QEvent
    from PySide2.QtGui import QPalette, QDrag, QPixmap, QColor, QMouseEvent, QPainter
    from PySide2.QtWidgets import QPushButton, QApplication
except:
    from PySide.QtCore import Qt, QMimeData, QByteArray, Signal, QEvent
    from PySide.QtGui import QPushButton, QPalette, QDrag, QPixmap, QColor, QApplication, QMouseEvent, QPainter

from const import MIME_COLOR_MODIFIER
import sys, ast
try:
    import maya.cmds as mc
    INMAYA = int(mc.about(v=True))
except:
    INMAYA = 0

class ColorButton(QPushButton):
    colorChanged = Signal(QColor)

    def __init__(self, parent = None, color = QColor(Qt.red), enableDragDrop = True):
        QPushButton.__init__(self, parent)
        self.setAcceptDrops(True)
        self.__enableDragDrop = enableDragDrop
        self.__mimeTypeString = MIME_COLOR_MODIFIER
        self.__pressed = False
        self.setFixedSize(20, 20)
        self.setMouseTracking(True)
        self.setColor(color)

    def enableDragDrop(self, enable):
        self.__enableDragDrop = enable

    def setColor(self, color):
        currentColor = self.color()
        if INMAYA:
            palette = self.palette()
            palette.setColor(QPalette.Button, color)
            self.setPalette(palette)
        else:
            self.setStyleSheet('background-color: rgb(%d, %d, %d)' % color.getRgb()[:3])
        if color != currentColor:
            self.colorChanged.emit(color)

    def color(self):
        if INMAYA:
            palette = self.palette()
            return palette.color(QPalette.Button)
        else:
            style = self.styleSheet()
            index = style.index('rgb')
            data = ast.literal_eval(style[index + 3:])
            return QColor(*data)

    def mousePressEvent(self, event):
        if self.__enableDragDrop:
            self.__pressed = True
        QPushButton.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.__pressed:
            drag = QDrag(self)
            data = QMimeData()
            data.setText('ABC')
            data.setColorData(self.color())
            data.setData(self.__mimeTypeString, QByteArray.number(QApplication.keyboardModifiers()))
            drag.setMimeData(data)
            pixmap = QPixmap(20, 20)
            pixmap.fill(self.color())
            drag.setDragCursor(pixmap, Qt.CopyAction)
            drag.start()
            self.__pressed = False
            if self.isDown():
                self.setDown(False)
        QPushButton.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.__pressed = False
        QPushButton.mouseReleaseEvent(self, event)

    def dragEnterEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasFormat(self.__mimeTypeString):
            event.accept()
        QPushButton.dragEnterEvent(self, event)

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasFormat(self.__mimeTypeString):
            modifier = QApplication.keyboardModifiers()
            pos = event.pos()
            mouseEvent = QMouseEvent(QEvent.MouseButtonRelease, pos, Qt.LeftButton, Qt.LeftButton, modifier)
            QPushButton.mouseReleaseEvent(self, mouseEvent)
            if self.isDown():
                self.setDown(False)
        else:
            QPushButton.dropEvent(self, event)

    def childEvent(self, event):
        if event.type() == QEvent.ChildRemoved:
            self.__pressed = False
            if self.isDown():
                self.setDown(False)
        QPushButton.childEvent(self, event)

    def paintEvent(self, event):
        if INMAYA > 2015:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            rect = event.rect()
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.color().darker())
            painter.setOpacity(0.35)
            painter.drawRoundedRect(rect, 2, 2)
            if self.__pressed:
                rect.adjust(1, 1, 0, 0)
            else:
                rect.adjust(0, 0, -1, -1)
            painter.setBrush(self.color())
            painter.setOpacity(1.0)
            painter.drawRoundedRect(rect, 2, 2)
        else:
            QPushButton.paintEvent(self, event)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = ColorButton()
    w.show()
    sys.exit(app.exec_())