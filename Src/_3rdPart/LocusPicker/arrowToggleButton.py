# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\arrowToggleButton.py
try:
    from PySide2.QtCore import Qt, QSize
    from PySide2.QtGui import QIcon, QPixmap
    from PySide2.QtWidgets import QToolButton, QSizePolicy
except:
    from PySide.QtCore import Qt, QSize
    from PySide.QtGui import QToolButton, QIcon, QSizePolicy, QPixmap

from locusPickerResources import *
import sys
try:
    import maya.cmds as mc
    INMAYA = int(mc.about(v=True))
except:
    INMAYA = 0

class ArrowToggleButton(QToolButton):

    def __init__(self, parent = None):
        QToolButton.__init__(self, parent)
        self.setMouseTracking(True)
        self.setFixedHeight(12)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.NoFocus)
        self.setIconSize(QSize(8, 8))
        self.__upsideDown = True
        self.__hover = False
        self.setIcon(QIcon(':/downarrow'))
        self.setAutoFillBackground(INMAYA > 2015)

    @property
    def upsideDown(self):
        return self.__upsideDown

    @upsideDown.setter
    def upsideDown(self, ud):
        self.__upsideDown = ud
        self.updateIcon()

    def updateIcon(self):
        if self.__upsideDown:
            self.setIcon(self.__hover and QIcon(':/downarrow_hover') or QIcon(':/downarrow'))
        else:
            self.setIcon(self.__hover and QIcon(':/uparrow_hover') or QIcon(':/uparrow'))

    def enterEvent(self, event):
        self.__hover = True
        self.updateIcon()
        QToolButton.enterEvent(self, event)

    def leaveEvent(self, event):
        self.__hover = False
        self.updateIcon()
        QToolButton.leaveEvent(self, event)


class HoverIconButton(QToolButton):

    def __init__(self, icon = QIcon(), hoverIcon = QIcon(), parent = None):
        QToolButton.__init__(self, parent)
        self.__icon = QIcon()
        self.__hoverIcon = QIcon()
        self.__disabled = QPixmap()
        self.setCustomIcon(icon, hoverIcon)

    def setDisabledPixmap(self, pixmap):
        if isinstance(pixmap, str):
            pixmap = QPixmap(pixmap)
        self.__disabled = pixmap

    def setCustomIcon(self, pixmap, hover_pixmap):
        if isinstance(pixmap, str):
            pixmap = QPixmap(pixmap)
        self.__icon = QIcon(pixmap)
        if isinstance(hover_pixmap, str):
            hover_pixmap = QPixmap(hover_pixmap)
        self.__hoverIcon = QIcon(hover_pixmap)
        if not self.__disabled.isNull():
            self.__icon.addPixmap(self.__disabled, QIcon.Disabled)
            self.__hoverIcon.addPixmap(self.__disabled, QIcon.Disabled)
        self.setIcon(self.__icon)

    def enterEvent(self, event):
        if not self.__hoverIcon.isNull():
            self.setIcon(self.__hoverIcon)
            self.update()
        QToolButton.enterEvent(self, event)

    def leaveEvent(self, event):
        if not self.__icon.isNull():
            self.setIcon(self.__icon)
            self.update()
        QToolButton.leaveEvent(self, event)


if __name__ == '__main__':

    def toggleUpsideDown(widget):
        widget.upsideDown ^= True


    from PySide.QtGui import QApplication
    import sys
    app = QApplication(sys.argv)
    w = HoverIconButton()
    w.setDisabledPixmap(':play_disabled')
    w.setCustomIcon(':/play', ':/play_hover')
    w.show()
    sys.exit(app.exec_())