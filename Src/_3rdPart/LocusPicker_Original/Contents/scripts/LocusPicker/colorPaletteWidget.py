# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\colorPaletteWidget.py
try:
    from PySide2.QtCore import Signal, QEvent, QMimeData, Qt
    from PySide2.QtGui import QColor, QPalette, QDrag, QPixmap
    from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QDialog, QFrame
except:
    from PySide.QtCore import Signal, QEvent, QMimeData, Qt
    from PySide.QtGui import QWidget, QColor, QHBoxLayout, QVBoxLayout, QPushButton, QPalette, QDrag, QPixmap, QDialog, QFrame

from const import MIME_COLOR

class ColorPaletteWidget(QWidget):
    setButtonColor = Signal(QColor)

    def __init__(self, parent = None, draggable = True):
        QWidget.__init__(self, parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        self.setLayout(layout)
        self.__pressed = None
        self.__dragColor = QColor()
        self.__draggable = draggable
        self.__previousButton = None
        self.defaultColorList()
        self.greyColorList(0.06)
        self.hsvColorList(0.06, 0.2, 1.0)
        self.hsvColorList(0.06, 0.4, 1.0)
        self.hsvColorList(0.06, 0.6, 1.0)
        self.hsvColorList(0.06, 0.8, 1.0)
        self.hsvColorList(0.06, 1.0, 1.0)
        self.hsvColorList(0.06, 1.0, 0.8)
        self.hsvColorList(0.06, 1.0, 0.6)
        self.hsvColorList(0.06, 1.0, 0.4)
        self.hsvColorList(0.06, 1.0, 0.2)
        return

    def eventFilter(self, widget, event):
        if self.__draggable and isinstance(widget, QPushButton):
            if event.type() == QEvent.MouseButtonPress:
                self.__pressed = widget
                palette = widget.palette()
                self.__dragColor = palette.color(QPalette.Button)
            elif event.type() == QEvent.MouseMove:
                if self.__pressed == widget:
                    if widget.isDown():
                        widget.setDown(False)
                    drag = QDrag(widget)
                    data = QMimeData()
                    data.setData(MIME_COLOR, 'color')
                    data.setColorData(self.__dragColor)
                    drag.setMimeData(data)
                    pixmap = QPixmap(18, 18)
                    pixmap.fill(self.__dragColor)
                    drag.setDragCursor(pixmap, Qt.CopyAction)
                    drag.start()
                    self.__pressed = None
            elif event.type() == QEvent.MouseButtonRelease:
                self.__pressed = None
            elif event.type() == QEvent.ChildRemoved:
                widget.setDown(False)
        return QWidget.eventFilter(self, widget, event)

    def defaultColorList(self):
        from const import getDefaultColor as gdc
        self.buildColorColumn([gdc('RtIK'),
         gdc('RtFK'),
         gdc('CnIK'),
         gdc('CnFK'),
         gdc('LfIK'),
         gdc('LfFK')])

    def greyColorList(self, step):
        colorSet = []
        value = 0.0
        while value < 1.0:
            colorSet.append(QColor.fromRgbF(value, value, value))
            value += step

        self.buildColorColumn(colorSet)

    def hsvColorList(self, step, sat, val):
        colorSet = []
        hue = 0.0
        while hue < 1.0:
            colorSet.append(QColor.fromHsvF(hue, sat, val))
            hue += step

        self.buildColorColumn(colorSet)

    def buildColorColumn(self, colorSet):
        from const import COLOR_PALETTE_TIP
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        for color in colorSet:
            frame = QFrame(self)
            frame.setFixedSize(20, 20)
            frame.setFrameShape(QFrame.Box)
            frame.setFrameShadow(QFrame.Plain)
            frame.setLineWidth(0)
            l = QHBoxLayout()
            l.setContentsMargins(0, 0, 0, 0)
            button = QPushButton(frame)
            button.setFixedSize(18, 18)
            button.setFocusPolicy(Qt.NoFocus)
            palette = button.palette()
            palette.setColor(QPalette.Button, color)
            button.setPalette(palette)
            l.addWidget(button)
            frame.setLayout(l)
            layout.addWidget(frame)
            if hasattr(color, 'ann'):
                button.setToolTip((self.__draggable and COLOR_PALETTE_TIP or '') + color.ann)
            else:
                button.setToolTip((self.__draggable and COLOR_PALETTE_TIP or '') + 'R%d G%d B%d' % color.getRgb()[:3])
            button.installEventFilter(self)
            button.clicked.connect(self.emitButtonColor)
            button.pressed.connect(self.setFrameBorder)

        layout.addStretch()
        self.layout().insertLayout(self.layout().count(), layout)

    def setFrameBorder(self):
        if self.__previousButton:
            self.__previousButton.parent().setLineWidth(0)
        button = self.sender()
        frame = button.parent()
        frame.setLineWidth(1)
        self.__previousButton = button

    def emitButtonColor(self):
        button = self.sender()
        palette = button.palette()
        self.setButtonColor.emit(palette.color(QPalette.Button))

    def clearSelection(self):
        if self.__previousButton:
            self.__previousButton.parent().setLineWidth(0)
        self.__previousButton = None
        return


class ColorPaletteDialog(QDialog):
    saveINI = Signal()

    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.Popup)
        self.setWindowTitle('Color Swatch Palette')
        self.paletteWidget = ColorPaletteWidget(self, False)
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(self.paletteWidget)
        buttonLayout = QHBoxLayout()
        self.done_button = QPushButton('Done', self)
        self.revert_button = QPushButton('Revert', self)
        buttonLayout.addWidget(self.done_button)
        buttonLayout.addWidget(self.revert_button)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        self.__designatedButton = None
        self.__revertColor = QColor()
        self.__close = False
        self.paletteWidget.setButtonColor.connect(self.setDesignatedButtonColor)
        self.done_button.clicked.connect(self.close)
        self.revert_button.clicked.connect(self.revert)
        return

    def closeEvent(self, event):
        if self.sender() == None and not self.__close:
            self.revert()
        self.__close = False
        self.saveINI.emit()
        QDialog.closeEvent(self, event)
        return

    def close(self):
        self.__close = True
        QDialog.close(self)

    def showEvent(self, event):
        self.adjustSize()
        self.setFixedSize(self.size())
        QDialog.showEvent(self, event)

    @property
    def designatedButton(self):
        return self.__designatedButton

    @designatedButton.setter
    def designatedButton(self, but):
        self.__designatedButton = but
        self.__revertColor = but.color()

    def setDesignatedButtonColor(self, color):
        if self.designatedButton:
            self.designatedButton.setColor(color)

    def clearSelection(self):
        self.paletteWidget.clearSelection()

    def revert(self):
        self.setDesignatedButtonColor(self.__revertColor)
        self.close()


if __name__ == '__main__':
    from PySide.QtGui import QApplication
    import sys
    app = QApplication(sys.argv)
    w = ColorPaletteDialog()
    w.show()
    sys.exit(app.exec_())