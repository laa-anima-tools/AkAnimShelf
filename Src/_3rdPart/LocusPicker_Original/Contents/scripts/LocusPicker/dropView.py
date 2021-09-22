# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\dropView.py
try:
    from PySide2.QtCore import QRect, QRectF, QPoint, Qt, QPointF, QTimer, QPropertyAnimation, QEasingCurve
    from PySide2.QtGui import QPainter, QCursor, QPixmap, QVector2D, QKeySequence
    from PySide2.QtWidgets import QGraphicsView, QRubberBand, QGraphicsOpacityEffect, QScrollBar
except:
    from PySide.QtCore import QRect, QRectF, QPoint, Qt, QPointF, QTimer, QPropertyAnimation, QEasingCurve
    from PySide.QtGui import QGraphicsView, QPainter, QCursor, QRubberBand, QPixmap, QVector2D, QGraphicsOpacityEffect, QScrollBar, QKeySequence

from const import SCROLL_WAITING_TIME
import sys
if sys.exec_prefix.find('Maya') > 0:
    INMAYA = True
else:
    INMAYA = False
SCROLL_THICKNESS = 12

class DropView(QGraphicsView):

    def __init__(self, parent = None):
        QGraphicsView.__init__(self, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setFrameStyle(QGraphicsView.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.FACTOR_func = lambda x: self.matrix().scale(x, x).mapRect(QRectF(0, 0, 1, 1)).width()
        self.__midPos = QPointF()
        self.__isTrack = self.__isZoom = self.__blockContextMenu = False
        self.__currentZoomFactor = 1.0
        self.__rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.__pickerNode = None
        self.__loaded = False
        self.setAnimatableScroll()
        return

    def setAnimatableScroll(self):
        self.createScrollTimer()
        self.createScrollAnimation()
        self.createScrollEffect()
        self.createAnimatableScroll()

    def createScrollTimer(self):
        self.timer = QTimer()
        self.timer.setSingleShot(SCROLL_WAITING_TIME)
        self.timer.timeout.connect(self.hideScroll)

    def createScrollAnimation(self):
        self.setProperty('horScrollOpacity', float)
        self.horAnim = QPropertyAnimation(self, 'horScrollOpacity')
        self.horAnim.setDuration(200)
        self.horAnim.setEasingCurve(QEasingCurve.InOutQuad)
        self.horAnim.valueChanged.connect(lambda x: self.setScrollOpacity(x, Qt.Horizontal))
        self.setProperty('verScrollOpacity', float)
        self.verAnim = QPropertyAnimation(self, 'verScrollOpacity')
        self.verAnim.setDuration(200)
        self.verAnim.setEasingCurve(QEasingCurve.InOutQuad)
        self.verAnim.valueChanged.connect(lambda x: self.setScrollOpacity(x, Qt.Vertical))

    def createScrollEffect(self):
        self.horEffect = QGraphicsOpacityEffect(self)
        self.verEffect = QGraphicsOpacityEffect(self)
        self.horEffect.setOpacity(0.0)
        self.verEffect.setOpacity(0.0)

    def createAnimatableScroll(self):
        hScroll = self.horizontalScrollBar()
        self.hscrollBar = QScrollBar(Qt.Horizontal, self)
        self.hscrollBar.setGraphicsEffect(self.horEffect)
        self.hscrollBar.actionTriggered.connect(lambda : self.timer.start(SCROLL_WAITING_TIME))
        self.hscrollBar.valueChanged.connect(hScroll.setValue)
        self.hscrollBar.hide()
        self.hscrollBar.setCursor(Qt.ArrowCursor)
        hScroll.rangeChanged.connect(lambda x, y: self.matchScroll(hScroll, x, y))
        hScroll.valueChanged.connect(self.hscrollBar.setValue)
        hScroll.valueChanged.connect(self.showScroll)
        vScroll = self.verticalScrollBar()
        self.vscrollBar = QScrollBar(Qt.Vertical, self)
        self.vscrollBar.setGraphicsEffect(self.verEffect)
        self.vscrollBar.actionTriggered.connect(lambda : self.timer.start(SCROLL_WAITING_TIME))
        self.vscrollBar.valueChanged.connect(vScroll.setValue)
        self.vscrollBar.hide()
        self.vscrollBar.setCursor(Qt.ArrowCursor)
        vScroll.rangeChanged.connect(lambda x, y: self.matchScroll(vScroll, x, y))
        vScroll.valueChanged.connect(self.vscrollBar.setValue)
        vScroll.valueChanged.connect(self.showScroll)

    @property
    def pickerNode(self):
        return self.__pickerNode

    @pickerNode.setter
    def pickerNode(self, node):
        self.__pickerNode = node

    @property
    def loaded(self):
        return self.__loaded

    @loaded.setter
    def loaded(self, loaded):
        self.__loaded = loaded

    def setUpdateMode(self, smart = True):
        if smart:
            self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        else:
            self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

    def resizeEvent(self, event):
        QGraphicsView.resizeEvent(self, event)
        mapSize = self.scene().mapSize
        contentsSize = self.contentsRect().size()
        rect = QRectF(0.0, 0.0, max(mapSize.width(), contentsSize.width()), max(mapSize.height(), contentsSize.height()))
        self.setSceneRect(rect)
        w, h = self.width(), self.height()
        self.hscrollBar.setGeometry(QRect(0, h - SCROLL_THICKNESS, w - SCROLL_THICKNESS, SCROLL_THICKNESS))
        self.vscrollBar.setGeometry(QRect(w - SCROLL_THICKNESS, 0, SCROLL_THICKNESS, h - SCROLL_THICKNESS))

    def enterEvent(self, event):
        self.setFocus()
        QGraphicsView.enterEvent(self, event)

    def wheelEvent(self, event):
        from math import pow
        self.scaleView(pow(1.15, event.delta() / 240.0))

    def contextMenuEvent(self, event):
        if self.__blockContextMenu:
            self.__blockContextMenu = False
        else:
            QGraphicsView.contextMenuEvent(self, event)

    def mousePressEvent(self, event):
        pos = QPointF(event.pos())
        button = event.button()
        modifier = event.modifiers()
        if button == Qt.MiddleButton and modifier == Qt.AltModifier:
            self.__midPos = pos
            self.__blockContextMenu = self.__isTrack = True
            self.setCursor(QCursor(QPixmap(':/trackCursor')))
        elif button == Qt.RightButton and modifier == Qt.AltModifier:
            self.__midPos = pos
            self.__blockContextMenu = self.__isZoom = True
            self.__currentZoomFactor = self.FACTOR_func(1)
            self.setCursor(QCursor(QPixmap(':/dollyCursor')))
            self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
            self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        else:
            QGraphicsView.mousePressEvent(self, event)

    @staticmethod
    def distancePointToLine(p, v0, v1):
        v = QVector2D(v1 - v0)
        w = QVector2D(p - v0)
        c1 = QVector2D.dotProduct(w, v)
        c2 = QVector2D.dotProduct(v, v)
        b = c1 * 1.0 / c2
        pb = v0 + v.toPointF() * b
        return QVector2D(p - pb).length()

    def mouseMoveEvent(self, event):
        pos = QPointF(event.pos())
        if self.__isZoom:
            sign = QVector2D.dotProduct(QVector2D(1, 1).normalized(), QVector2D(pos - self.__midPos).normalized()) >= 0 and 1 or -1
            dist = self.distancePointToLine(pos, self.__midPos, self.__midPos + QPointF(1, -1))
            increment = sign * dist * 0.001
            self.setScaleView(self.__currentZoomFactor + increment)
        elif self.__isTrack:
            offset = pos - self.__midPos
            factor = 0.667 * self.FACTOR_func(1)
            hsb = self.horizontalScrollBar()
            vsb = self.verticalScrollBar()
            if abs(offset.x()) > 1:
                increment = offset.x() * factor
                hsb.setValue(hsb.value() - increment)
            if abs(offset.y()) > 1:
                increment = offset.y() * factor
                vsb.setValue(vsb.value() - increment)
            self.__midPos = pos
        QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.__midPos = QPointF()
        if self.__isTrack or self.__isZoom:
            self.__isTrack = False
            self.__isZoom = False
        else:
            QGraphicsView.mouseReleaseEvent(self, event)

    def keyPressEvent(self, event):
        key = event.key()
        modifier = event.modifiers()
        if modifier == Qt.NoModifier and (key == Qt.Key_A or key == Qt.Key_F):
            scene = self.scene()
            if key == Qt.Key_A:
                rect = scene.itemsBoundingRect()
            else:
                items = scene.selectedItems()
                if not items:
                    return
                rect = QRectF()
                for i in items:
                    rect = rect.united(i.sceneBoundingRect())

            rect.adjust(-10, -10, 10, 10)
            self.fitInView(rect, Qt.KeepAspectRatio)
        elif modifier == Qt.ControlModifier and key == Qt.Key_0:
            self.setScaleView(1)
        elif event.matches(QKeySequence.ZoomIn):
            self.setScaleView(self.FACTOR_func(1) + 0.1)
        elif event.matches(QKeySequence.ZoomOut):
            self.setScaleView(self.FACTOR_func(1) - 0.1)
        else:
            QGraphicsView.keyPressEvent(self, event)

    def scaleView(self, scaleFactor):
        factor = self.FACTOR_func(scaleFactor)
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)

    def setScaleView(self, scale):
        f = scale / self.FACTOR_func(1)
        self.scaleView(f)

    def dragEnterEvent(self, event):
        event.accept()
        QGraphicsView.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        event.accept()
        QGraphicsView.dragMoveEvent(self, event)

    def dropEvent(self, event):
        event.accept()
        QGraphicsView.dropEvent(self, event)

    def getScenePosFromGlobal(self):
        globalPos = QCursor.pos()
        localPos = self.mapFromGlobal(globalPos)
        localPos -= INMAYA and QPoint(2, 2) or QPoint(1, 1)
        return self.mapToScene(localPos)

    def showRubberBand(self, rect):
        pos1 = self.mapFromScene(rect.topLeft())
        pos2 = self.mapFromScene(rect.bottomRight())
        self.__rubberBand.setGeometry(QRect(pos1, pos2))
        self.__rubberBand.show()

    def hideRubberBand(self):
        self.__rubberBand.hide()

    def showScroll(self):
        if not self.isVisible():
            return
        hScroll = self.horizontalScrollBar()
        flag = False
        if hScroll.minimum() == hScroll.maximum() == 0:
            flag = flag or False
        else:
            flag = flag or True
            self.horAnim.setStartValue(self.horEffect.opacity())
            self.horAnim.setEndValue(1.0)
            self.horAnim.start()
        vScroll = self.verticalScrollBar()
        if vScroll.minimum() == vScroll.maximum() == 0:
            flag = flag or False
        else:
            flag = flag or True
            self.verAnim.setStartValue(self.verEffect.opacity())
            self.verAnim.setEndValue(1.0)
            self.verAnim.start()
        if flag:
            self.timer.start(SCROLL_WAITING_TIME)

    def hideScroll(self):
        self.horAnim.setStartValue(self.horEffect.opacity())
        self.horAnim.setEndValue(0.0)
        self.horAnim.start()
        self.verAnim.setStartValue(self.verEffect.opacity())
        self.verAnim.setEndValue(0.0)
        self.verAnim.start()

    def matchScroll(self, scroll, _min, _max):
        if scroll.orientation() == Qt.Horizontal:
            self.hscrollBar.setRange(_min, _max)
            self.hscrollBar.setSingleStep(scroll.singleStep())
            self.hscrollBar.setPageStep(scroll.pageStep())
        elif scroll.orientation() == Qt.Vertical:
            self.vscrollBar.setRange(_min, _max)
            self.vscrollBar.setSingleStep(scroll.singleStep())
            self.vscrollBar.setPageStep(scroll.pageStep())

    def setScrollOpacity(self, value, orient):
        if value != None and orient == Qt.Horizontal:
            self.horEffect.setOpacity(value)
            if value:
                if self.hscrollBar.isHidden():
                    self.hscrollBar.show()
            else:
                self.hscrollBar.hide()
        elif value != None and orient == Qt.Vertical:
            self.verEffect.setOpacity(value)
            if value:
                if self.vscrollBar.isHidden():
                    self.vscrollBar.show()
            else:
                self.vscrollBar.hide()
        return