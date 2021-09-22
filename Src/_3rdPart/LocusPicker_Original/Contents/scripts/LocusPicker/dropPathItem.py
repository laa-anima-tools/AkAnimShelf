# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\dropPathItem.py
try:
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QColor, QTransform, QPainterPath
except:
    from PySide.QtCore import Qt
    from PySide.QtGui import QColor, QTransform, QPainterPath

from dropItem import AbstractDropItem, AbstractEditableDropItem
from decorator import accepts, returns
from const import warn

class PathDropItem(AbstractDropItem):

    def __init__(self, path, color = QColor(Qt.red), parent = None):
        AbstractDropItem.__init__(self, color=color, parent=parent)
        self.__path = QPainterPath()
        self.__originPath = QPainterPath()
        self.__svgData = ''
        self.__originWidth = self.__originHeight = 20
        self.width, self.height = self.__originWidth, self.__originHeight
        self.path = path
        self.comm.sizeChanged.connect(self.scalePath)

    @property
    @returns(QPainterPath)
    def path(self):
        path = self.__path.translated(0, 0)
        return path

    @path.setter
    @accepts(QPainterPath)
    def path(self, path):
        self.__path = path.translated(0, 0)
        self.__originPath = path.translated(0, 0)
        rect = path.boundingRect()
        self.__originWidth, self.__originHeight = rect.width(), rect.height()
        self.width, self.height = self.__originWidth, self.__originHeight

    def setPath(self, path):
        self.__path = path

    @property
    @returns(str)
    def svgData(self):
        return self.__svgData

    @property
    def originPath(self):
        return self.__originPath

    @property
    def originWidth(self):
        return self.__originWidth

    @property
    def originHeight(self):
        return self.__originHeight

    def type(self):
        from const import DropItemType
        return DropItemType.Path

    def paint(self, painter, option, widget = None):
        AbstractDropItem.paint(self, painter, option, widget)
        boundingRect = self.boundingRect().normalized()
        drawPath = self.path.translated(boundingRect.x(), boundingRect.y())
        painter.drawPath(drawPath)

    def shape(self):
        return self.path

    def scalePath(self):
        transform = QTransform()
        if self.originWidth == 0 or self.originHeight == 0:
            return
        transform.scale(abs(self.width) / self.originWidth, abs(self.height) / self.originHeight)
        self.setPath(transform.map(self.originPath))

    def setIconImage(self, path):
        warn('Can not assign icon to Vector Button yet.', 'Sorry', self.scene().primaryView())

    def setLabelText(self, text):
        warn('Can not assign label to Vector Button yet.', 'Sorry', self.scene().primaryView())

    def setLabelFont(self, font):
        warn('Can not assign label to Vector Button yet.', 'Sorry', self.scene().primaryView())


class PathEditableDropItem(AbstractEditableDropItem, PathDropItem):

    def __init__(self, path, color = QColor(Qt.red), parent = None):
        AbstractEditableDropItem.__init__(self, color=color, parent=parent)
        self.__path = QPainterPath()
        self.__originPath = QPainterPath()
        self.__svgData = ''
        self.__originWidth = self.__originHeight = 20
        self.width, self.height = self.__originWidth, self.__originHeight
        self.path = path
        self.comm.sizeChanged.connect(self.scalePath)

    @property
    @returns(QPainterPath)
    def path(self):
        path = self.__path.translated(0, 0)
        return path

    @path.setter
    @accepts(QPainterPath)
    def path(self, path):
        self.__path = path.translated(0, 0)
        self.__originPath = path.translated(0, 0)
        rect = path.boundingRect()
        self.__originWidth, self.__originHeight = rect.width(), rect.height()
        self.width, self.height = self.__originWidth, self.__originHeight

    def setPath(self, path):
        self.__path = path

    @property
    @returns(str)
    def svgData(self):
        return self.__svgData

    @property
    def originPath(self):
        return self.__originPath

    @property
    def originWidth(self):
        return self.__originWidth

    @property
    def originHeight(self):
        return self.__originHeight

    def type(self):
        from const import DropItemType
        return DropItemType.EditablePath