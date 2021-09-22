# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\popupLineEdit.py
try:
    from PySide2.QtCore import Qt, QEvent, Signal, QPoint
    from PySide2.QtGui import QRegExpValidator
    from PySide2.QtWidgets import QLineEdit, QMenu
except:
    from PySide.QtCore import Qt, QEvent, Signal, QPoint
    from PySide.QtGui import QLineEdit, QMenu, QRegExpValidator

from decorator import accepts, returns
from const import WaitState, nameRegExp

class PressSendLineEdit(QLineEdit):
    pressed = Signal()

    def __init__(self, parent = None):
        QLineEdit.__init__(self, parent)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.NoFocus)

    def mousePressEvent(self, event):
        button = event.button()
        modifier = event.modifiers()
        if button == Qt.LeftButton and modifier == Qt.NoModifier:
            self.pressed.emit()
        else:
            QLineEdit.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        pass


class PopupLineEdit(QLineEdit):
    labelRenamed = Signal(unicode, unicode)
    waitStart = Signal()
    labelSelected = Signal(unicode)
    requestRenamable = Signal(unicode)

    def __init__(self, parent = None):
        QLineEdit.__init__(self, parent)
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setValidator(QRegExpValidator(nameRegExp))
        from const import SELECT_CHAR_TIP
        self.setToolTip(SELECT_CHAR_TIP)
        self.timer_id = None
        self.__pos = QPoint()
        self.__labels = []
        self.__editable = True
        self.__wait = WaitState.Proceed
        self.previousText = ''
        return

    @property
    @returns(list)
    def labels(self):
        return self.__labels

    @labels.setter
    @accepts(list)
    def labels(self, labels):
        self.__labels = labels
        if labels:
            self.setText(labels[0])

    @property
    @returns(bool)
    def editable(self):
        return self.__editable

    @editable.setter
    @accepts(bool)
    def editable(self, editable):
        self.__editable = editable

    def appendLabel(self, label):
        self.labels.append(label)
        self.setText(label)

    @property
    @returns(int)
    def wait(self):
        return self.__wait

    @wait.setter
    @accepts(int)
    def wait(self, wait):
        self.__wait = wait

    def mousePressEvent(self, event):
        button = event.button()
        modifier = event.modifiers()
        if self.isReadOnly() and self.editable:
            if button == Qt.LeftButton and modifier == Qt.NoModifier:
                if self.labels:
                    menu = QMenu()
                    for label in self.labels:
                        action = menu.addAction(label)
                        action.triggered.connect(self.changeText)

                    menu.exec_(event.globalPos())
                else:
                    QLineEdit.mousePressEvent(self, event)
        else:
            QLineEdit.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.removeTimer()
        QLineEdit.mouseReleaseEvent(self, event)

    def catchTimer(self, pos):
        self.timer_id = self.startTimer(125)
        self.__pos = pos

    def removeTimer(self):
        if self.timer_id:
            self.killTimer(self.timer_id)
            self.timer_id = None
        return

    def timerEvent(self, event):
        if event.timerId() == self.timer_id:
            self.removeTimer()
            menu = QMenu()
            for label in self.labels:
                action = menu.addAction(label)
                action.triggered.connect(self.changeText)

            menu.exec_(self.__pos)

    def mouseDoubleClickEvent(self, event):
        pass

    def contextMenuEvent(self, event):
        if self.labels and self.isReadOnly():
            self.wait = WaitState.Wait
            self.requestRenamable.emit(self.text())
            while not self.wait:
                pass

            if self.wait == WaitState.Proceed:
                menu = QMenu()
                action = menu.addAction('Rename')
                action.triggered.connect(self.setEditingMode)
                menu.exec_(event.globalPos())

    def event(self, event):
        if not self.isReadOnly():
            if event.type() == QEvent.Type.NonClientAreaMouseButtonPress or event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
                self.setText(self.previousText)
                self.previousText = ''
                self.setReadOnly(True)
        return QLineEdit.event(self, event)

    def changeText(self):
        prevText = self.text()
        changeText = self.sender().text()
        self.wait = WaitState.Wait
        self.waitStart.emit()
        while not self.wait:
            pass

        if self.wait == WaitState.Proceed:
            self.doSelectText(changeText)
        elif self.wait == WaitState.GoBack:
            self.setText(prevText)

    def doSelectText(self, changeText):
        if self.text() != changeText:
            self.setText(changeText)
            self.labelSelected.emit(changeText)

    def clear(self):
        QLineEdit.clear(self)
        self.labels = []

    def setEditingMode(self):
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.setReadOnly(False)
        self.previousText = self.text()
        self.returnPressed.connect(self.renameLabel)

    def renameLabel(self):
        newText = self.text()
        if self.previousText != newText:
            self.labelRenamed.emit(self.previousText, newText)
            index = self.labels.index(self.previousText)
            self.previousText = ''
            self.labels[index] = newText
        self.returnPressed.disconnect()
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.clearFocus()


if __name__ == '__main__':
    from PySide.QtGui import QApplication
    import sys
    app = QApplication(sys.argv)
    w = PopupLineEdit()
    w.labels = ['ABC', 'DEF']
    w.show()
    sys.exit(app.exec_())