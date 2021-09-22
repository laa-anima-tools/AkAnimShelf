# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\imageRegionWidget.py
try:
    from PySide2.QtCore import Qt, QRect, QRectF, QPoint, Signal, QMimeData, QByteArray, QEvent, QSizeF, QPointF
    from PySide2.QtGui import QPainter, QPen, QPixmap, QPolygon, QColor, QDrag, QPainterPath, QVector2D, QTransform
    from PySide2.QtWidgets import QPushButton
except:
    from PySide.QtCore import Qt, QRect, QRectF, QPoint, Signal, QMimeData, QByteArray, QEvent, QSizeF, QPointF
    from PySide.QtGui import QPushButton, QPainter, QPen, QPixmap, QPolygon, QColor, QDrag, QPainterPath, QVector2D, QTransform

from const import CursorPos, MIME_IMAGE_PATH, MIME_IMAGE_RECT, MIME_IMAGE_BUTTONSIZE
from dropItem import AbstractDropItem
import math, os

class ImageRegionWidget(QPushButton):
    regionChanged = Signal(QRect)
    imageChanged = Signal(unicode)

    def __init__(self, parent = None):
        QPushButton.__init__(self, parent)
        self.setMouseTracking(True)
        self.setAcceptDrops(False)
        self.__boundaryRect = QRect()
        self.__imageRect = QRect()
        self.__imageRectBuffer = QRect()
        self.__shiftDist = self.__shiftAngle = 0.0
        self.__editable = True
        self.__imageMoveRect = QRectF(0, 0, 6, 6)
        self.__onImageMove = False
        self.__imageMoving = False
        self.__pressRegion = CursorPos.NONE
        self.__pressedPos = QPoint()
        self.__startPoint = None
        self.__imagePath = ''
        self.__pixmap = QPixmap()
        self.__drag = False
        return

    @property
    def editable(self):
        return self.__editable

    @editable.setter
    def editable(self, editable):
        self.__editable = editable
        self.update()

    @property
    def boundaryRect(self):
        return self.__boundaryRect

    @boundaryRect.setter
    def boundaryRect(self, rect):
        self.__boundaryRect = rect

    @property
    def imageRect(self):
        return self.__imageRect

    @imageRect.setter
    def imageRect(self, rect):
        if self.__imageRect != rect:
            self.__imageRect = rect
            minSide = min(self.__imageRect.width(), self.__imageRect.height())
            if minSide > 0:
                factor = math.log(minSide, 1.4)
            else:
                factor = 0
            if factor < 9:
                self.__imageMoveRect.setSize(QSizeF(0, 0))
            else:
                self.__imageMoveRect.setSize(QSizeF(factor, factor))
            self.__imageMoveRect.moveCenter(QRectF(self.__imageRect).center())
            self.update()
            self.regionChanged.emit(rect)

    @property
    def imagePath(self):
        return self.__imagePath

    @imagePath.setter
    def imagePath(self, path):
        self.__imagePath = path
        self.pixmap = QPixmap(path)
        self.imageChanged.emit(path)

    @property
    def pixmap(self):
        return self.__pixmap

    @pixmap.setter
    def pixmap(self, pixmap):
        self.__pixmap = pixmap
        self.update()

    @property
    def onImageMove(self):
        return self.__onImageMove

    @onImageMove.setter
    def onImageMove(self, on):
        self.__onImageMove = on
        self.update()

    def setIconXPos(self, val):
        bufferRect = self.__imageRect.adjusted(0, 0, 0, 0)
        bufferRect.moveLeft(val + self.__boundaryRect.left())
        self.imageRect = bufferRect

    def setIconYPos(self, val):
        bufferRect = self.__imageRect.adjusted(0, 0, 0, 0)
        bufferRect.moveTop(val + self.__boundaryRect.top())
        self.imageRect = bufferRect

    def setIconWidth(self, val):
        bufferRect = self.__imageRect.adjusted(0, 0, 0, 0)
        bufferRect.setWidth(val)
        self.imageRect = bufferRect

    def setIconHeight(self, val):
        bufferRect = self.__imageRect.adjusted(0, 0, 0, 0)
        bufferRect.setHeight(val)
        self.imageRect = bufferRect

    def mousePressEvent(self, event):
        pos = event.pos()
        pressPos = self.getCursorPos(pos)
        if self.__editable:
            if pressPos:
                self.__pressedPos = pos
                self.__pressRegion = pressPos
                if CursorPos.isTopLeft(self.__pressRegion):
                    self.__startPoint = self.__imageRect.bottomRight()
                elif CursorPos.isTopRight(self.__pressRegion):
                    self.__startPoint = self.__imageRect.bottomLeft()
                elif CursorPos.isBottomLeft(self.__pressRegion):
                    self.__startPoint = self.__imageRect.topRight()
                elif CursorPos.isBottomRight(self.__pressRegion):
                    self.__startPoint = self.__imageRect.topLeft()
                else:
                    self.__startPoint = None
                self.__imageRectBuffer = self.__imageRect.adjusted(0, 0, 0, 0)
                bufX = self.__imageRectBuffer.width()
                bufY = self.__imageRectBuffer.height()
                self.__shiftDist = math.sqrt(bufX * bufX + bufY * bufY)
                self.__shiftAngle = math.atan(bufY * 1.0 / bufX)
            elif self.__imageMoveRect.contains(pos):
                self.__imageMoving = True
                self.__pressedPos = pos
                self.__imageRectBuffer = self.__imageRect.adjusted(0, 0, 0, 0)
                self.setCursor(Qt.ClosedHandCursor)
            else:
                self.__drag = True
        else:
            self.__drag = True
        QPushButton.mousePressEvent(self, event)
        return

    def mouseReleaseEvent(self, event):
        if self.__imageMoving or self.__pressRegion:
            pass
        else:
            QPushButton.mouseReleaseEvent(self, event)
        self.imageRect = self.imageRect.normalized()
        self.__pressed = QPoint()
        self.__pressRegion = CursorPos.NONE
        self.__startPoint = None
        self.__imageRectBuffer = QRect()
        self.__shiftAngle = self.__shiftDist = 0.0
        self.__imageMoving = False
        self.__drag = False
        if self.__imageMoveRect.contains(event.pos()):
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        return

    @staticmethod
    def getDeltaByAngle(delta, dist, angle):
        deltaDist = math.sqrt(delta.x() * delta.x() + delta.y() * delta.y())
        dx = math.cos(angle) * (dist - deltaDist)
        dy = math.sin(angle) * (dist - deltaDist)
        return (dx, dy)

    @staticmethod
    def getIntersectPoint(ps1, pe1, ps2, pe2):
        a1 = pe1.y() - ps1.y()
        b1 = pe1.x() - ps1.x()
        c1 = a1 * ps1.x() - b1 * ps1.y()
        a2 = pe2.y() - ps2.y()
        b2 = pe2.x() - ps2.x()
        c2 = a2 * ps2.x() - b2 * ps2.y()
        delta = a2 * b1 - a1 * b2
        if delta == 0:
            return QPoint(-1, -1)
        return QPoint((b1 * c2 - b2 * c1) / delta, (a1 * c2 - a2 * c1) / delta)

    def getShiftAdjustedRect_obsolete(self, region, rect, pos):
        if CursorPos.isTopLeft(region):
            delta = self.__imageRectBuffer.bottomRight() - pos
            dx, dy = self.getDeltaByAngle(delta, self.__shiftDist, self.__shiftAngle)
            return rect.adjusted(dx, dy, 0, 0)
        elif CursorPos.isTopRight(region):
            delta = self.__imageRectBuffer.bottomLeft() - pos
            dx, dy = self.getDeltaByAngle(delta, self.__shiftDist, self.__shiftAngle)
            return rect.adjusted(0, dy, -dx, 0)
        elif CursorPos.isBottomLeft(region):
            delta = self.__imageRectBuffer.topRight() - pos
            dx, dy = self.getDeltaByAngle(delta, self.__shiftDist, self.__shiftAngle)
            return rect.adjusted(dx, 0, 0, -dy)
        else:
            delta = self.__imageRectBuffer.topLeft() - pos
            if self.__imageRectBuffer.top() > pos.y() and self.__imageRectBuffer.left() > pos.x():
                pass
            dx, dy = self.getDeltaByAngle(delta, self.__shiftDist, self.__shiftAngle)
            return rect.adjusted(0, 0, -dx, -dy)

    def getDiagonalPoints(self, region, rect):
        if CursorPos.isTopLeft(region):
            p0 = rect.bottomRight()
            p1 = rect.topLeft()
        elif CursorPos.isTopRight(region):
            p0 = rect.bottomLeft()
            p1 = rect.topRight()
        elif CursorPos.isBottomLeft(region):
            p0 = rect.topRight()
            p1 = rect.bottomLeft()
        else:
            p0 = rect.topLeft()
            p1 = rect.bottomRight()
        return (p0, p1)

    def getShiftAdjustedRect(self, region, pos, rect):
        rect = QRectF(rect)
        pos = QPointF(pos)
        trans = QTransform()
        trans.rotate(90)
        p0, p1 = self.getDiagonalPoints(region, rect)
        pn = p0 + trans.map(p1 - p0)
        dist = self.distancePointToLine(QPointF(pos), p0, pn)
        sign = QVector2D.dotProduct(QVector2D(p1 - p0).normalized(), QVector2D(pos - p0).normalized())
        dx = math.cos(self.__shiftAngle) * dist
        dy = math.sin(self.__shiftAngle) * dist
        if CursorPos.isTopLeft(region):
            if sign >= 0:
                return self.getRectFromTwoPoints(self.__startPoint, self.__startPoint - QPoint(dx, dy))
            else:
                return self.getRectFromTwoPoints(self.__startPoint, self.__startPoint + QPoint(dx, dy))
        elif CursorPos.isTopRight(region):
            if sign >= 0:
                return self.getRectFromTwoPoints(self.__startPoint, self.__startPoint - QPoint(-dx, dy))
            else:
                return self.getRectFromTwoPoints(self.__startPoint, self.__startPoint + QPoint(-dx, dy))
        elif CursorPos.isBottomLeft(region):
            if sign >= 0:
                return self.getRectFromTwoPoints(self.__startPoint, self.__startPoint - QPoint(dx, -dy))
            else:
                return self.getRectFromTwoPoints(self.__startPoint, self.__startPoint + QPoint(dx, -dy))
        else:
            if sign >= 0:
                return self.getRectFromTwoPoints(self.__startPoint, self.__startPoint + QPoint(dx, dy))
            return self.getRectFromTwoPoints(self.__startPoint, self.__startPoint - QPoint(dx, dy))

    @staticmethod
    def distancePointToLine(p, v0, v1):
        v = QVector2D(v1 - v0)
        w = QVector2D(p - v0)
        c1 = QVector2D.dotProduct(w, v)
        c2 = QVector2D.dotProduct(v, v)
        b = c1 * 1.0 / c2
        pb = v0 + v.toPointF() * b
        return QVector2D(p - pb).length()

    def getAdjustedRect(self, region, rect, offset):
        if CursorPos.isTop(region):
            rect.adjust(0, offset.y(), 0, 0)
        elif CursorPos.isBottom(region):
            rect.adjust(0, 0, 0, offset.y())
        if CursorPos.isLeft(region):
            rect.adjust(offset.x(), 0, 0, 0)
        elif CursorPos.isRight(region):
            rect.adjust(0, 0, offset.x(), 0)
        return rect

    def intersectOnTopLeft(self, start, end, boundRect, rect):
        point = self.getIntersectPoint(start, end, boundRect.topRight(), boundRect.topLeft())
        if not boundRect.contains(point):
            point = self.getIntersectPoint(start, end, boundRect.bottomLeft(), boundRect.topLeft())
        if boundRect.contains(point):
            rect.setTopLeft(point)

    def intersectOnBottomRight(self, start, end, boundRect, rect):
        point = self.getIntersectPoint(start, end, boundRect.bottomLeft(), boundRect.bottomRight())
        if not boundRect.contains(point):
            point = self.getIntersectPoint(start, end, boundRect.topRight(), boundRect.bottomRight())
        if boundRect.contains(point):
            rect.setBottomRight(point)

    def intersectOnTopRight(self, start, end, boundRect, rect):
        point = self.getIntersectPoint(start, end, boundRect.topLeft(), boundRect.topRight())
        if not boundRect.contains(point):
            point = self.getIntersectPoint(start, end, boundRect.bottomRight(), boundRect.topRight())
        if boundRect.contains(point):
            rect.setTopRight(point)

    def intersectOnBottomLeft(self, start, end, boundRect, rect):
        point = self.getIntersectPoint(start, end, boundRect.bottomRight(), boundRect.bottomLeft())
        if not boundRect.contains(point):
            point = self.getIntersectPoint(start, end, boundRect.topLeft(), boundRect.bottomLeft())
        if boundRect.contains(point):
            rect.setBottomLeft(point)

    def getShiftMaximumRect(self, region, imageRect, boundRect, pos):
        rect = imageRect.adjusted(0, 0, 0, 0)
        p0, p1 = self.getDiagonalPoints(region, imageRect)
        sign = QVector2D.dotProduct(QVector2D(p1 - p0).normalized(), QVector2D(pos - p0).normalized())
        if CursorPos.isTopLeft(region):
            if sign >= 0:
                self.intersectOnTopLeft(p0, p1, boundRect, rect)
            else:
                self.intersectOnBottomRight(p1, p0, boundRect, rect)
        elif CursorPos.isTopRight(region):
            if sign >= 0:
                self.intersectOnTopRight(p0, p1, boundRect, rect)
            else:
                self.intersectOnBottomLeft(p1, p0, boundRect, rect)
        elif CursorPos.isBottomLeft(region):
            if sign >= 0:
                self.intersectOnBottomLeft(p0, p1, boundRect, rect)
            else:
                self.intersectOnTopRight(p1, p0, boundRect, rect)
        elif sign >= 0:
            self.intersectOnBottomRight(p0, p1, boundRect, rect)
        else:
            self.intersectOnTopLeft(p1, p0, boundRect, rect)
        return rect

    @staticmethod
    def getRectFromTwoPoints(start, end):
        path = QPainterPath(QPointF(start))
        path.lineTo(QPointF(end))
        return path.boundingRect().toRect()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        modifier = event.modifiers()
        if self.__pressRegion:
            if modifier == Qt.ShiftModifier and not CursorPos.isOneSide(self.__pressRegion):
                bufferRect = self.getShiftAdjustedRect(self.__pressRegion, pos, self.__imageRectBuffer)
                if self.__boundaryRect.contains(bufferRect) or bufferRect.isNull():
                    self.imageRect = bufferRect
                else:
                    self.imageRect = self.getShiftMaximumRect(self.__pressRegion, self.__imageRect, self.__boundaryRect, pos)
            else:
                if self.__startPoint != None:
                    bufferRect = self.getRectFromTwoPoints(self.__startPoint, pos)
                else:
                    offset = pos - self.__pressedPos
                    bufferRect = self.getAdjustedRect(self.__pressRegion, self.__imageRectBuffer.adjusted(0, 0, 0, 0), offset)
                self.imageRect = self.__boundaryRect.intersected(bufferRect)
        elif self.__imageMoving:
            offset = pos - self.__pressedPos
            bufferRect = self.__imageRectBuffer.translated(offset)
            if self.__boundaryRect.contains(bufferRect):
                self.imageRect = bufferRect
            else:
                if bufferRect.left() < self.__boundaryRect.left():
                    bufferRect.moveLeft(self.__boundaryRect.left())
                elif bufferRect.right() > self.__boundaryRect.right():
                    bufferRect.moveRight(self.__boundaryRect.right())
                if bufferRect.top() < self.__boundaryRect.top():
                    bufferRect.moveTop(self.__boundaryRect.top())
                elif bufferRect.bottom() > self.__boundaryRect.bottom():
                    bufferRect.moveBottom(self.__boundaryRect.bottom())
                self.imageRect = bufferRect
        elif self.__drag and self.__imagePath:
            drag = QDrag(self)
            data = QMimeData()
            data.setData(MIME_IMAGE_PATH, QByteArray(str(self.__imagePath.encode('utf-8'))))
            data.setData(MIME_IMAGE_RECT, QByteArray('%d,%d,%d,%d' % self.__imageRect.getRect()))
            data.setData(MIME_IMAGE_BUTTONSIZE, QByteArray('%d,%d' % self.size().toTuple()))
            drag.setMimeData(data)
            drag.start()
            self.__pressed = False
        elif self.__editable:
            cursorPos = self.getCursorPos(pos)
            if CursorPos.isOneSide(cursorPos):
                if CursorPos.isTop(cursorPos) or CursorPos.isBottom(cursorPos):
                    self.setCursor(Qt.SizeVerCursor)
                else:
                    self.setCursor(Qt.SizeHorCursor)
            elif cursorPos:
                if CursorPos.isTopLeft(cursorPos) or CursorPos.isBottomRight(cursorPos):
                    self.setCursor(Qt.SizeFDiagCursor)
                else:
                    self.setCursor(Qt.SizeBDiagCursor)
            elif self.__imageMoveRect.contains(pos):
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        return

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        QPushButton.leaveEvent(self, event)

    def childEvent(self, event):
        if event.type() == QEvent.ChildRemoved:
            self.__drag = False
        QPushButton.childEvent(self, event)

    def dragEnterEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            event.accept()
        QPushButton.dragEnterEvent(self, event)

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            path = [ y for y in [ x.toLocalFile() for x in mimeData.urls() ] if os.path.splitext(y)[-1].lower() in ('.jpg', '.png') ]
            if path:
                self.imagePath = path[0]
        QPushButton.dropEvent(self, event)

    def getCursorPos(self, pos):
        region = CursorPos.NONE
        if self.__imageRect.adjusted(-3, -3, 3, 3).contains(pos):
            x, y = pos.x(), pos.y()
            top, bottom = self.__imageRect.top(), self.__imageRect.bottom()
            left, right = self.__imageRect.left(), self.__imageRect.right()
            if y < top + 3 and y > top - 3:
                region |= CursorPos.TOP
            elif y < bottom + 3 and y > bottom - 3:
                region |= CursorPos.BOTTOM
            if x < left + 3 and x > left - 3:
                region |= CursorPos.LEFT
            elif x < right + 3 and x > right - 3:
                region |= CursorPos.RIGHT
        return region

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        rect = self.rect()
        painter.setPen(Qt.black)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(rect)
        pen = QPen(Qt.red, 0, Qt.DotLine)
        painter.setPen(pen)
        painter.drawRect(self.__boundaryRect)
        if self.__pixmap.isNull():
            painter.setPen(Qt.blue)
            painter.drawRect(self.__imageRect)
        else:
            painter.drawPixmap(self.__imageRect, self.__pixmap)
        if self.__editable:
            painter.setOpacity(0.5)
            if self.__imageMoveRect.isValid():
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(67, 255, 163))
                painter.drawRect(self.__imageMoveRect.adjusted(-2, -2, 2, 2))
            if self.__imageRect:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(67, 255, 163))
                painter.drawPolygon(self.getCornerPolygon(self.__imageRect.topLeft(), 0))
                painter.drawPolygon(self.getCornerPolygon(self.__imageRect.topRight(), 1))
                painter.drawPolygon(self.getCornerPolygon(self.__imageRect.bottomRight(), 2))
                painter.drawPolygon(self.getCornerPolygon(self.__imageRect.bottomLeft(), 3))

    def getCornerPolygon(self, pos, coord = 0):
        if coord == 0:
            p1 = pos + QPoint(9, 0)
            p2 = p1 + QPoint(0, 3)
            p3 = p2 - QPoint(6, 0)
            p4 = p3 + QPoint(0, 6)
            p5 = p4 - QPoint(3, 0)
        elif coord == 1:
            p1 = pos + QPoint(0, 9)
            p2 = p1 - QPoint(3, 0)
            p3 = p2 - QPoint(0, 6)
            p4 = p3 - QPoint(6, 0)
            p5 = p4 - QPoint(0, 3)
        elif coord == 2:
            p1 = pos - QPoint(9, 0)
            p2 = p1 - QPoint(0, 3)
            p3 = p2 + QPoint(6, 0)
            p4 = p3 - QPoint(0, 6)
            p5 = p4 + QPoint(3, 0)
        else:
            p1 = pos - QPoint(0, 9)
            p2 = p1 + QPoint(3, 0)
            p3 = p2 + QPoint(0, 6)
            p4 = p3 + QPoint(6, 0)
            p5 = p4 + QPoint(0, 3)
        return QPolygon.fromList([pos,
         p1,
         p2,
         p3,
         p4,
         p5])


if __name__ == '__main__':
    from PySide.QtGui import QApplication
    import sys

    def print_args(*args, **kwargs):
        print args, kwargs


    app = QApplication(sys.argv)
    w = ImageRegionWidget()
    w.setFixedSize(120, 120)
    w.clicked.connect(print_args)
    w.show()
    w.boundaryRect = w.rect().adjusted(3, 3, -3, -3)
    w.imageRect = w.boundaryRect.adjusted(30, 20, -15, -5)
    w.imagePath = 'C:/Users/hgkim/Desktop/Frozen-Behind-the-Scenes-5.jpg'
    sys.exit(app.exec_())