# Embedded file name: C:\Users\hgkim\Documents\maya\2016\pythons\LocusPicker\dragComboBox.py
from PySide.QtCore import Qt, QMimeData, QByteArray, QPoint
from PySide.QtGui import QComboBox, QDrag, QPixmap, QPainter
from const import MIME_DRAGCOMBO_TEXT

class DragComboBox(QComboBox):

    def __init__(self, items = [], parent = None):
        QComboBox.__init__(self, parent)
        if items and isinstance(items, list):
            self.addItems(items)
        from const import COMMAND_COMBOBOX_TIP
        self.setToolTip(COMMAND_COMBOBOX_TIP)
        self.timer_id = None
        self.drag = False
        self.__popupShown = False
        return

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.modifiers() == Qt.NoModifier:
            self.drag = True
            self.catchTimer()

    def mouseReleaseEvent(self, event):
        self.removeTimer()
        QComboBox.mouseReleaseEvent(self, event)

    def catchTimer(self):
        self.timer_id = self.startTimer(100)

    def removeTimer(self):
        if self.drag:
            if self.__popupShown:
                self.hidePopup()
            else:
                self.showPopup()
            self.drag = False
        if self.timer_id:
            self.killTimer(self.timer_id)
            self.timer_id = None
        return

    def timerEvent(self, event):
        if event.timerId() == self.timer_id:
            self.drag = False
            drag = QDrag(self)
            data = QMimeData()
            data.setData(MIME_DRAGCOMBO_TEXT, QByteArray(self.currentText()))
            drag.setMimeData(data)
            drag.start()
            self.removeTimer()

    def showPopup(self):
        QComboBox.showPopup(self)
        self.__popupShown = True

    def hidePopup(self):
        QComboBox.hidePopup(self)
        self.__popupShown = False


if __name__ == '__main__':
    from PySide.QtGui import QApplication
    import sys
    app = QApplication(sys.argv)
    w = DragComboBox()
    w.addItems(['Select',
     'Reset',
     'Key',
     'Toggle',
     'Pose',
     'Range'])
    w.show()
    sys.exit(app.exec_())