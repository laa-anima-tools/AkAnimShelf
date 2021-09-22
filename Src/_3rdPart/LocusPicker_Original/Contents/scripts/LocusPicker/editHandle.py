# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\editHandle.py
try:
    from PySide2.QtCore import Qt, QPointF, QRectF
    from PySide2.QtGui import QColor, QPainter, QPainterPath, QPolygonF
    from PySide2.QtWidgets import QGraphicsItem
except:
    from PySide.QtCore import Qt, QPointF, QRectF
    from PySide.QtGui import QGraphicsItem, QColor, QPainter, QPainterPath, QPolygonF

from decorator import returns, accepts

class AbstractHandle(QGraphicsItem):
    kMouseReleased, kMouseDown, kMouseMoving = (0, 1, 2)

    def __init__(self, parent = None, scene = None):
        QGraphicsItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        if scene:
            scene.addItem(self)
        self.setZValue(65536)
        self.__width = self.__height = 0
        self.__mouseButtonState = AbstractHandle.kMouseReleased
        self.__mouseDownPos = QPointF()
        self.__color = QColor()
        self.__hoverColor = QColor()
        self.__isHover = False
        self.buffer = None
        self.setAcceptHoverEvents(True)
        self.color = QColor(Qt.yellow)
        return

    @property
    @returns(float)
    def width(self):
        return self.__width

    @width.setter
    @accepts(int)
    def width(self, width):
        self.__width = width

    @property
    @returns(float)
    def height(self):
        return self.__height

    @height.setter
    @accepts(float)
    def height(self, height):
        self.__height = height

    @property
    @returns(int)
    def mouseState(self):
        return self.__mouseButtonState

    @mouseState.setter
    @accepts(int)
    def mouseState(self, state):
        self.__mouseButtonState = state

    @property
    @returns(QPointF)
    def mousePos(self):
        return self.__mouseDownPos

    @mousePos.setter
    @accepts(QPointF)
    def mousePos(self, pos):
        self.__mouseDownPos = pos

    @property
    @returns(QColor)
    def color(self):
        return self.__color

    @color.setter
    @accepts(QColor)
    def color(self, color):
        self.__color = color
        self.__hoverColor = color.lighter(150)

    def hoverLeaveEvent(self, event):
        self.__isHover = False
        self.update()

    def hoverEnterEvent(self, event):
        self.__isHover = True
        self.update()

    def mouseMoveEvent(self, event):
        self.mouseState = self.kMouseMoving
        event.ignore()

    def mousePressEvent(self, event):
        self.mouseState = self.kMouseDown
        event.ignore()

    def mouseReleaseEvent(self, event):
        self.mouseState = self.kMouseReleased
        event.accept()

    def boundingRect(self):
        return QRectF(self.width / -2, self.height / -2, self.width, self.height)

    def paint(self, painter, option, widget = None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.__isHover and self.__hoverColor or self.__color)


class DiamondHandle(AbstractHandle):

    def __init__(self, width, height, parent = None, scene = None):
        AbstractHandle.__init__(self, parent, scene)
        self.width = width
        self.height = height

    def shape(self):
        path = QPainterPath()
        polygon = QPolygonF()
        for p in [QPointF(self.width / -2, 0),
         QPointF(0, self.height / -2),
         QPointF(self.width / 2, 0),
         QPointF(0, self.height / 2)]:
            polygon.append(p)

        path.addPolygon(polygon)
        return path

    def paint(self, painter, option, widget = None):
        AbstractHandle.paint(self, painter, option, widget=widget)
        painter.drawPath(self.shape())


class EllipseHandle(AbstractHandle):

    def __init__(self, width, height, parent = None, scene = None):
        AbstractHandle.__init__(self, parent, scene)
        self.width = width
        self.height = height

    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def paint(self, painter, option, widget = None):
        AbstractHandle.paint(self, painter, option, widget=widget)
        painter.drawEllipse(self.boundingRect())


class SizeMoveHandle(EllipseHandle):

    def __init__(self, width, height, orient = Qt.Horizontal, parent = None, scene = None):
        EllipseHandle.__init__(self, width, height, parent=parent, scene=scene)
        self.__orient = orient
        self.color = QColor(Qt.white)

    def paint(self, painter, option, widget = None):
        EllipseHandle.paint(self, painter, option, widget=widget)
        polygon = QPolygonF()
        painter.setBrush(Qt.black)
        if bool(self.__orient & Qt.Horizontal):
            for p in self.trianglePoints('left'):
                polygon.append(p)

            painter.drawPolygon(polygon)
            polygon.clear()
            for p in self.trianglePoints('right'):
                polygon.append(p)

            painter.drawPolygon(polygon)
            polygon.clear()
        if bool(self.__orient & Qt.Vertical):
            for p in self.trianglePoints('top'):
                polygon.append(p)

            painter.drawPolygon(polygon)
            polygon.clear()
            for p in self.trianglePoints('bottom'):
                polygon.append(p)

            painter.drawPolygon(polygon)
            polygon.clear()

    def trianglePoints(self, pos):
        rect = QRectF(0, 0, self.width / 3, self.height / 3)
        boundingRect = self.boundingRect()
        rect.moveCenter(boundingRect.center())
        if pos == 'top':
            rect.moveTop(boundingRect.top())
            return [QPointF(0, self.height / -2), rect.bottomLeft(), rect.bottomRight()]
        if pos == 'bottom':
            rect.moveBottom(boundingRect.bottom())
            return [QPointF(0, self.height / 2), rect.topLeft(), rect.topRight()]
        if pos == 'left':
            rect.moveLeft(boundingRect.left())
            return [QPointF(self.width / -2, 0), rect.topRight(), rect.bottomRight()]
        if pos == 'right':
            rect.moveRight(boundingRect.right())
            return [QPointF(self.width / 2, 0), rect.topLeft(), rect.bottomLeft()]


if __name__ == '__main__':
    from PySide.QtGui import QApplication
    import sys
    app = QApplication(sys.argv)
    handle = DiamondHandle(6, 4)
    sys.exit(app.exec_())