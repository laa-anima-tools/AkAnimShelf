# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\dropSliderItem.py
try:
    from PySide2.QtCore import Qt, QRectF, QPointF, QTimer, Signal, QEvent, QSizeF
    from PySide2.QtGui import QColor, QLinearGradient, QPixmap
    from PySide2.QtWidgets import QGraphicsItem
except:
    from PySide.QtCore import Qt, QRectF, QPointF, QTimer, Signal, QEvent, QSizeF
    from PySide.QtGui import QColor, QGraphicsItem, QLinearGradient, QPixmap

from dropItem import RectangleDropItem, RectangleEditableDropItem, Communicator
from editHandle import DiamondHandle, EllipseHandle
from decorator import accepts, returns, timestamp
from const import Attachment
from locusPickerResources import *
import time

class SliderCommunicator(Communicator):
    valueChanged = Signal(float)
    sliderMousePressed = Signal()
    sliderMouseReleased = Signal()


class SliderPressRegion():
    NONE = 0
    HANDLE = 1
    BASE = 2


class SliderHoverRegion():
    NONE = 0
    HANDLE = 1
    RESET = 2

    @classmethod
    def onHandle(cls, val):
        return bool(val & cls.HANDLE)

    @classmethod
    def onReset(cls, val):
        return bool(val & cls.RESET)


class RectangleDropSliderItem(RectangleDropItem):
    BORDER_MARGIN = 1
    SLIDER_THICKNESS = 18.0
    RESET_SPACING = 1.0
    HANDLE_THICKNESS = 6.0

    def __init__(self, attachment = Attachment.TOP, color = QColor(), width = 40, height = 40, parent = None):
        RectangleDropItem.__init__(self, color, width, height, parent)
        self.setFlags(self.flags() | QGraphicsItem.ItemClipsChildrenToShape)
        self.__attachment = self.__min = self.__max = self.__value = 0
        self.__decimal = 2
        self.__timerDirty = self.__invertedAppearance = False
        self.__hoverRegion = SliderHoverRegion.NONE
        self.__pressedSliderRegion = SliderPressRegion.NONE
        self.__margin1 = self.__margin2 = self.BORDER_MARGIN
        self.__thickness = self.SLIDER_THICKNESS
        self.setRange(0.0, 1.0)
        self.__sliderRect = QRectF()
        self.__resetRect = QRectF()
        self.__grooveRect = QRectF()
        self.__grooveBaseRect = QRectF()
        self.__handleRect = QRectF()
        self.comm = SliderCommunicator()
        self.sliderBaseColor = QColor(Qt.gray)
        self.sliderGrooveColor = QColor(Qt.darkGray)
        self.value = 0.0
        self.comm.sizeChanged.connect(self.resetSliderRects)
        self.comm.valueChanged.connect(self.emitRangeData)
        self.width = width
        self.height = height
        self.attachment = attachment

    def type(self):
        from const import DropItemType
        return DropItemType.RectangleSlider

    @property
    @returns(int)
    def attachment(self):
        return self.__attachment

    @attachment.setter
    @accepts(int)
    def attachment(self, attach):
        if self.__attachment and attach:
            beforeFlag = bool(self.__attachment / Attachment.LEFT)
            afterFlag = bool(attach / Attachment.LEFT)
            if beforeFlag ^ afterFlag:
                self.width, self.height = self.height, self.width
                self.minWidth, self.minHeight = self.minHeight, self.minWidth
        self.__attachment = attach
        self.resetSliderRects()
        self.matchMinSizeToSubordinate()

    def isInSliderRect(self, pos):
        return self.sliderRect.contains(pos)

    def inboundRect(self):
        rect = RectangleDropItem.inboundRect(self)
        if Attachment.isTop(self.attachment):
            rect.setTop(self.sliderRect.bottom() + self.BORDER_MARGIN)
        elif Attachment.isBottom(self.attachment):
            rect.setBottom(self.sliderRect.top() - self.BORDER_MARGIN)
        elif Attachment.isLeft(self.attachment):
            rect.setLeft(self.sliderRect.right() + self.BORDER_MARGIN)
        elif Attachment.isRight(self.attachment):
            rect.setRight(self.sliderRect.left() - self.BORDER_MARGIN)
        return rect

    def matchMinSizeToSubordinate(self):
        """
        self.prepareGeometryChange()
        if self.iconRect.intersects(self.labelRect):            
            rect = self.iconRect.united(self.labelRect)
            self.minWidth = max(rect.width()+self.BORDER_MARGIN*2, self.DEFAULT_MINSIZE)
            self.minHeight = max(rect.height()+self.BORDER_MARGIN*2, self.DEFAULT_MINSIZE)
        else:
            self.minWidth = max(self.iconRect.width()+self.labelRect.width()+self.BORDER_MARGIN*2, self.DEFAULT_MINSIZE)
            self.minHeight = max(self.iconRect.height()+self.labelRect.height()+self.BORDER_MARGIN*2, self.DEFAULT_MINSIZE)
        if Attachment.isHorizontal(self.__attachment):
            self.minWidth += self.__sliderRect.width()+self.BORDER_MARGIN
            self.minHeight = max(self.minHeight, self.__sliderRect.height())
        elif Attachment.isVertical(self.__attachment):
            self.minWidth = max(self.minWidth, self.__sliderRect.width())
            self.minHeight += self.__sliderRect.height()+self.BORDER_MARGIN        
        if self.minWidth > self.width: self.width = self.minWidth
        if self.minHeight > self.height: self.height = self.minHeight
        """
        self.prepareGeometryChange()
        rect = self.iconRect.united(self.labelRect).united(self.sliderRect)
        self.minWidth = min(max(rect.width() + self.BORDER_MARGIN * 2, self.DEFAULT_MINSIZE), 40)
        self.minHeight = min(max(rect.height() + self.BORDER_MARGIN * 2, self.DEFAULT_MINSIZE), 40)
        if self.minWidth > self.width:
            self.width = self.minWidth
        if self.minHeight > self.height:
            self.height = self.minHeight

    def matchMinSizeToSlider(self):
        if Attachment.isVertical(self.attachment):
            self.minWidth = max(self.minWidth, self.margin1 + self.margin2 + self.thickness)
            self.minHeight = max(self.minHeight, self.BORDER_MARGIN * 2 + self.thickness)
        elif Attachment.isHorizontal(self.attachment):
            self.minWidth = max(self.minWidth, self.BORDER_MARGIN * 2 + self.thickness)
            self.minHeight = max(self.minHeight, self.margin1 + self.margin2 + self.thickness)
        else:
            self.minWidth = self.minHeight = 20
        if self.minWidth > self.width:
            self.width = self.minWidth
        if self.minHeight > self.height:
            self.height = self.minHeight

    def setRange(self, minVal, maxVal):
        self.min = minVal
        self.max = maxVal

    def range(self):
        return (self.min, self.max)

    @property
    @returns(float)
    def min(self):
        return self.__min

    @min.setter
    @accepts(float)
    def min(self, val):
        self.__min = val

    @property
    @returns(float)
    def max(self):
        return self.__max

    @max.setter
    @accepts(float)
    def max(self, val):
        self.__max = val

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, val):
        val = round(val, self.__decimal)
        if self.__value != val:
            self.__value = val
            self.setHandleRect()
            self.comm.valueChanged.emit(val)
            self.update()

    def setValue(self, value, emit = True):
        if not emit:
            self.comm.blockSignals(True)
        self.value = value
        if not emit:
            self.comm.blockSignals(False)

    @property
    @returns(int)
    def hoverRegion(self):
        return self.__hoverRegion

    @hoverRegion.setter
    @accepts(int)
    def hoverRegion(self, region):
        if self.__hoverRegion != region:
            self.__hoverRegion = region
            self.update()

    @property
    @returns(bool)
    def invertedAppearance(self):
        return self.__invertedAppearance

    @invertedAppearance.setter
    @accepts(bool)
    def invertedAppearance(self, invert):
        self.__invertedAppearance = invert
        self.resetSliderRects()
        self.update()

    @property
    @returns(float)
    def margin1(self):
        return self.__margin1

    @margin1.setter
    @accepts(float)
    def margin1(self, margin):
        self.__margin1 = margin

    @property
    @returns(float)
    def margin2(self):
        return self.__margin2

    @margin2.setter
    @accepts(float)
    def margin2(self, margin):
        self.__margin2 = margin

    @property
    @returns(float)
    def thickness(self):
        return self.__thickness

    @thickness.setter
    @accepts(float)
    def thickness(self, thickness):
        self.__thickness = thickness

    @property
    def pressedSliderRegion(self):
        return self.__pressedSliderRegion

    @pressedSliderRegion.setter
    def pressedSliderRegion(self, region):
        self.__pressedSliderRegion = region

    @property
    def sliderRect(self):
        return self.__sliderRect

    @sliderRect.setter
    def sliderRect(self, rect):
        self.__sliderRect = rect

    @property
    def resetRect(self):
        return self.__resetRect

    @resetRect.setter
    def resetRect(self, rect):
        self.__resetRect = rect

    @property
    def grooveRect(self):
        return self.__grooveRect

    @grooveRect.setter
    def grooveRect(self, rect):
        self.__grooveRect = rect

    @property
    def grooveBaseRect(self):
        return self.__grooveBaseRect

    @grooveBaseRect.setter
    def grooveBaseRect(self, rect):
        self.__grooveBaseRect = rect

    @property
    def handleRect(self):
        return self.__handleRect

    @handleRect.setter
    def handleRect(self, rect):
        self.__handleRect = rect

    def resetSliderRects(self):
        self.setSliderRect()
        self.setResetRect()
        self.setGrooveRect()
        self.setHandleRect()

    def setSliderRect(self):
        rect = self.boundingRect().normalized()
        if Attachment.isTop(self.attachment):
            sliderRect = rect.adjusted(self.margin1, 0, -self.margin2, 0)
            sliderRect.setHeight(self.thickness)
            sliderRect.moveTopLeft(rect.topLeft() + QPointF(self.margin1, self.BORDER_MARGIN))
        elif Attachment.isLeft(self.attachment):
            sliderRect = rect.adjusted(0, self.margin1, 0, -self.margin2)
            sliderRect.setWidth(self.thickness)
            sliderRect.moveTopLeft(rect.topLeft() + QPointF(self.BORDER_MARGIN, self.margin1))
        elif Attachment.isBottom(self.attachment):
            sliderRect = rect.adjusted(self.margin1, 0, -self.margin2, 0)
            sliderRect.setHeight(self.thickness)
            sliderRect.moveBottomRight(rect.bottomRight() - QPointF(self.margin2, self.BORDER_MARGIN))
        elif Attachment.isRight(self.attachment):
            sliderRect = rect.adjusted(0, self.margin1, 0, -self.margin2)
            sliderRect.setWidth(self.thickness)
            sliderRect.moveBottomRight(rect.bottomRight() - QPointF(self.BORDER_MARGIN, self.margin2))
        else:
            sliderRect = QRectF()
        self.sliderRect = sliderRect

    def setResetRect(self):
        rect = self.sliderRect.adjusted(0, 0, 0, 0)
        if Attachment.isVertical(self.attachment):
            rect.setWidth(self.SLIDER_THICKNESS)
        else:
            rect.setHeight(self.SLIDER_THICKNESS)
        if self.invertedAppearance:
            rect.moveBottomRight(self.sliderRect.bottomRight())
        self.resetRect = rect

    def setGrooveRect(self):
        rect = self.sliderRect.adjusted(0, 0, 0, 0)
        if Attachment.isVertical(self.attachment):
            if self.invertedAppearance:
                rect.setRight(self.resetRect.left() - self.RESET_SPACING)
            else:
                rect.setLeft(self.resetRect.right() + self.RESET_SPACING)
            grooveRect = rect.adjusted(self.HANDLE_THICKNESS / 2, self.HANDLE_THICKNESS / 2, self.HANDLE_THICKNESS / -2, self.HANDLE_THICKNESS / -2)
            grooveRect.setHeight(self.HANDLE_THICKNESS / 2)
        else:
            if self.invertedAppearance:
                rect.setBottom(self.resetRect.top() - self.RESET_SPACING)
            else:
                rect.setTop(self.resetRect.bottom() + self.RESET_SPACING)
            grooveRect = rect.adjusted(self.HANDLE_THICKNESS / 2, self.HANDLE_THICKNESS / 2, self.HANDLE_THICKNESS / -2, self.HANDLE_THICKNESS / -2)
            grooveRect.setWidth(self.HANDLE_THICKNESS / 2)
        grooveRect.moveCenter(rect.center())
        self.grooveBaseRect = rect
        self.grooveRect = grooveRect

    def setHandleRect(self):
        normRect = self.boundingRect().normalized()
        center = self.grooveRect.center()
        val = self.value
        rangeData = self.max - self.min
        ratio = (val - self.min) / rangeData
        if Attachment.isVertical(self.attachment):
            handleRect = QRectF(0, 0, self.HANDLE_THICKNESS, self.sliderRect.height() - 2)
            if self.invertedAppearance:
                margin = self.margin2 + self.HANDLE_THICKNESS / 2
                handleRect.moveCenter(QPointF(normRect.right() - (margin + self.grooveRect.width() * ratio + self.SLIDER_THICKNESS + self.RESET_SPACING), center.y()))
            else:
                margin = self.margin1 + self.HANDLE_THICKNESS / 2
                handleRect.moveCenter(QPointF(normRect.left() + margin + self.grooveRect.width() * ratio + self.SLIDER_THICKNESS + self.RESET_SPACING, center.y()))
        else:
            handleRect = QRectF(0, 0, self.sliderRect.width() - 2, self.HANDLE_THICKNESS)
            if self.invertedAppearance:
                margin = self.margin2 + self.HANDLE_THICKNESS / 2
                handleRect.moveCenter(QPointF(center.x(), normRect.bottom() - (margin + self.grooveRect.height() * ratio + self.SLIDER_THICKNESS + self.RESET_SPACING)))
            else:
                margin = self.margin1 + self.HANDLE_THICKNESS / 2
                handleRect.moveCenter(QPointF(center.x(), normRect.top() + margin + self.grooveRect.height() * ratio + self.SLIDER_THICKNESS + self.RESET_SPACING))
        self.handleRect = handleRect

    def paint(self, painter, option, widget = None):
        RectangleDropItem.paint(self, painter, option, widget)
        if self.sliderRect.isValid():
            painter.setPen(self.sliderGrooveColor)
            painter.setBrush(self.sliderBaseColor)
            painter.drawRoundedRect(self.grooveBaseRect, 1, 1)
            if Attachment.isVertical(self.attachment):
                gradient = QLinearGradient(self.grooveRect.topLeft(), self.grooveRect.bottomLeft())
            else:
                gradient = QLinearGradient(self.grooveRect.topLeft(), self.grooveRect.topRight())
            gradient.setColorAt(0, self.sliderGrooveColor.darker(150))
            gradient.setColorAt(0.2, self.sliderGrooveColor.darker(150))
            gradient.setColorAt(0.8, self.sliderGrooveColor)
            gradient.setColorAt(1, self.sliderGrooveColor)
            painter.setBrush(gradient)
            painter.drawRect(self.grooveRect)
            painter.setPen(self.color.darker(150))
            painter.setBrush(SliderHoverRegion.onHandle(self.hoverRegion) and self.color.lighter(125) or self.color)
            painter.drawRoundedRect(self.handleRect, 2.0, 2.0)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(41, 41, 41))
            painter.drawRoundedRect(self.resetRect, 2, 2)
            pixmap = QPixmap(SliderHoverRegion.onReset(self.hoverRegion) and ':/reset_hover' or ':/reset')
            pixmapRect = self.resetRect.adjusted(1, 1, -1, -1)
            sizeFactor = min(pixmapRect.width(), pixmapRect.height())
            pixmapRect.setSize(QSizeF(sizeFactor, sizeFactor))
            pixmapRect.moveCenter(self.resetRect.center())
            painter.drawPixmap(pixmapRect, pixmap, pixmap.rect())

    def hoverMoveEvent(self, event):
        RectangleDropItem.hoverMoveEvent(self, event)
        pos = event.pos()
        if self.handleRect.contains(pos):
            self.hoverRegion = SliderHoverRegion.HANDLE
        elif self.resetRect.contains(pos):
            self.hoverRegion = SliderHoverRegion.RESET
        else:
            self.hoverRegion = SliderHoverRegion.NONE

    def hoverLeaveEvent(self, event):
        RectangleDropItem.hoverLeaveEvent(self, event)
        self.hoverRegion = SliderHoverRegion.NONE
        self.update()

    def mousePressEvent(self, event):
        pos = event.pos()
        if event.button() == Qt.LeftButton and event.modifiers() == Qt.NoModifier:
            if self.resetRect.contains(pos):
                self.emitCommmand('Reset')
            elif self.handleRect.contains(pos):
                self.pressedSliderRegion = SliderPressRegion.HANDLE
                self.comm.sliderMousePressed.emit()
            elif self.sliderRect.contains(pos):
                self.pressedSliderRegion = SliderPressRegion.BASE
                self.comm.sliderMousePressed.emit()
                self.calculateValueForMousePosition(pos)
            elif self.command == 'Pose':
                self.ignoreStartValue = True
                self.comm.mousePressed.emit()
                self.setValue(1.0)
            elif self.command == 'Range':
                _min, _max = self.range()
                if self.value > (_max + _min) / 2.0:
                    self.value = _min
                else:
                    self.value = _max
            else:
                RectangleDropItem.mousePressEvent(self, event)
        else:
            RectangleDropItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.pressedSliderRegion:
            self.pressedSliderRegion = SliderPressRegion.NONE
            self.comm.sliderMouseReleased.emit()
        else:
            RectangleDropItem.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        RectangleDropItem.mouseMoveEvent(self, event)
        if bool(self.pressedSliderRegion & (SliderPressRegion.HANDLE | SliderPressRegion.BASE)):
            self.calculateValueForMousePosition(event.pos())
            self.scene().isHandleWorking = True

    def calculateValueForMousePosition(self, pos):
        if Attachment.isVertical(self.attachment):
            x = pos.x()
            left = self.grooveRect.left()
            right = self.grooveRect.right()
            if x < left:
                if self.invertedAppearance:
                    val = self.max
                else:
                    val = self.min
            elif x > right:
                if self.invertedAppearance:
                    val = self.min
                else:
                    val = self.max
            else:
                ratio = (x - left) / (right - left)
                if self.invertedAppearance:
                    ratio = 1 - ratio
                val = (self.max - self.min) * ratio + self.min
        else:
            y = pos.y()
            top = self.grooveRect.top()
            bottom = self.grooveRect.bottom()
            if y < top:
                if self.invertedAppearance:
                    val = self.max
                else:
                    val = self.min
            elif y > bottom:
                if self.invertedAppearance:
                    val = self.min
                else:
                    val = self.max
            else:
                ratio = (y - top) / (bottom - top)
                if self.invertedAppearance:
                    ratio = 1 - ratio
                val = (self.max - self.min) * ratio + self.min
        self.value = val

    def matchToValue(self, val):
        diff = (val - self.value) / 2
        if abs(diff) < 0.1:
            self.value = val
            self.timer.stop()
        else:
            self.value += diff

    def emitRangeData(self, value):
        self.comm.sendCommandData.emit(self.command, self.targetNode, self.targetChannel, self.targetValue, unicode(value))

    def createCustomContextMenu(self, event):
        menu = RectangleDropItem.createCustomContextMenu(self, event)
        return menu

    def setDefaultValue(self):
        self.comm.sliderMousePressed.emit()
        self.setValue(0)
        self.comm.sliderMouseReleased.emit()


class RectangleEditableDropSliderItem(RectangleEditableDropItem, RectangleDropSliderItem):

    def __init__(self, attachment = Attachment.TOP, color = QColor(), width = 40, height = 40, parent = None):
        RectangleEditableDropItem.__init__(self, color, width, height, parent)
        self.__attachment = self.__min = self.__max = self.__value = 0
        self.__decimal = 2
        self.__timerDirty = self.__invertedAppearance = False
        self.__hoverRegion = SliderHoverRegion.NONE
        self.__pressedSliderRegion = SliderPressRegion.NONE
        self.__marginHandle1 = self.__marginHandle2 = self.__thicknessHandle = None
        self.__margin1 = self.__margin2 = self.BORDER_MARGIN
        self.__thickness = self.SLIDER_THICKNESS
        self.setRange(0.0, 1.0)
        self.__sliderRect = QRectF()
        self.__resetRect = QRectF()
        self.__grooveRect = QRectF()
        self.__grooveBaseRect = QRectF()
        self.__handleRect = QRectF()
        self.comm = SliderCommunicator()
        self.sliderBaseColor = QColor(Qt.gray)
        self.sliderGrooveColor = QColor(Qt.darkGray)
        self.value = 0.0
        self.comm.sizeChanged.connect(self.resetSliderRects)
        self.comm.valueChanged.connect(self.emitRangeData)
        self.width = width
        self.height = height
        self.attachment = attachment
        return

    def type(self):
        from const import DropItemType
        return DropItemType.EditableRectangleSlider

    @property
    @returns(int)
    def attachment(self):
        return self.__attachment

    @attachment.setter
    @accepts(int)
    def attachment(self, attach):
        if self.__attachment and attach:
            beforeFlag = bool(self.__attachment / Attachment.LEFT)
            afterFlag = bool(attach / Attachment.LEFT)
            if beforeFlag ^ afterFlag:
                self.width, self.height = self.height, self.width
                self.minWidth, self.minHeight = self.minHeight, self.minWidth
        self.__attachment = attach
        self.resetSliderRects()
        self.matchMinSizeToSubordinate()

    @property
    @returns(float)
    def min(self):
        return self.__min

    @min.setter
    @accepts(float)
    def min(self, val):
        self.__min = val

    @property
    @returns(float)
    def max(self):
        return self.__max

    @max.setter
    @accepts(float)
    def max(self, val):
        self.__max = val

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, val):
        val = round(val, self.__decimal)
        if self.__value != val:
            self.__value = val
            self.setHandleRect()
            self.comm.valueChanged.emit(val)
            self.update()

    @property
    @returns(int)
    def hoverRegion(self):
        return self.__hoverRegion

    @hoverRegion.setter
    @accepts(int)
    def hoverRegion(self, region):
        if self.__hoverRegion != region:
            self.__hoverRegion = region
            self.update()

    @property
    @returns(bool)
    def invertedAppearance(self):
        return self.__invertedAppearance

    @invertedAppearance.setter
    @accepts(bool)
    def invertedAppearance(self, invert):
        self.__invertedAppearance = invert
        self.resetSliderRects()
        self.update()

    @property
    @returns(float)
    def margin1(self):
        return self.__margin1

    @margin1.setter
    @accepts(float)
    def margin1(self, margin):
        self.__margin1 = margin

    @property
    @returns(float)
    def margin2(self):
        return self.__margin2

    @margin2.setter
    @accepts(float)
    def margin2(self, margin):
        self.__margin2 = margin

    @property
    @returns(float)
    def thickness(self):
        return self.__thickness

    @thickness.setter
    @accepts(float)
    def thickness(self, thickness):
        self.__thickness = thickness

    @property
    def pressedSliderRegion(self):
        return self.__pressedSliderRegion

    @pressedSliderRegion.setter
    def pressedSliderRegion(self, region):
        self.__pressedSliderRegion = region

    @property
    def sliderRect(self):
        return self.__sliderRect

    @sliderRect.setter
    def sliderRect(self, rect):
        self.__sliderRect = rect

    @property
    def resetRect(self):
        return self.__resetRect

    @resetRect.setter
    def resetRect(self, rect):
        self.__resetRect = rect

    @property
    def grooveRect(self):
        return self.__grooveRect

    @grooveRect.setter
    def grooveRect(self, rect):
        self.__grooveRect = rect

    @property
    def grooveBaseRect(self):
        return self.__grooveBaseRect

    @grooveBaseRect.setter
    def grooveBaseRect(self, rect):
        self.__grooveBaseRect = rect

    @property
    def handleRect(self):
        return self.__handleRect

    @handleRect.setter
    def handleRect(self, rect):
        self.__handleRect = rect

    def paint(self, painter, option, widget = None):
        RectangleDropSliderItem.paint(self, painter, option, widget)

    def toggleSliderHandles(self):
        if self.__marginHandle1:
            self.removeSliderHandles()
        else:
            self.addSliderHandles()
            self.repositionSliderHandles()

    def addSliderHandles(self):
        if Attachment.isVertical(self.__attachment):
            self.__marginHandle1 = DiamondHandle(6, 8, self)
            self.__marginHandle2 = DiamondHandle(6, 8, self)
        else:
            self.__marginHandle1 = DiamondHandle(8, 6, self)
            self.__marginHandle2 = DiamondHandle(8, 6, self)
        self.__thicknessHandle = EllipseHandle(7, 7, self)
        color = self.color
        if color.red() > 223 and color.green() > 223 and color.blue() < 32:
            self.__marginHandle1.color = QColor(Qt.blue)
            self.__marginHandle2.color = QColor(Qt.blue)
            self.__thicknessHandle.color = QColor(Qt.blue)
        self.__marginHandle1.installSceneEventFilter(self)
        self.__marginHandle2.installSceneEventFilter(self)
        self.__thicknessHandle.installSceneEventFilter(self)

    def repositionSliderHandles(self):
        if not (self.__marginHandle1 and self.__marginHandle2 and self.__thicknessHandle):
            return
        normRect = self.boundingRect().normalized()
        if Attachment.isTop(self.__attachment):
            self.__marginHandle1.setPos(normRect.topLeft() + QPointF(self.margin1, self.BORDER_MARGIN))
            self.__marginHandle2.setPos(normRect.topRight() + QPointF(-self.margin2, self.BORDER_MARGIN))
            self.__thicknessHandle.setPos(normRect.topLeft() + QPointF(self.margin1, self.BORDER_MARGIN + self.thickness))
        elif Attachment.isLeft(self.__attachment):
            self.__marginHandle1.setPos(normRect.topLeft() + QPointF(self.BORDER_MARGIN, self.margin1))
            self.__marginHandle2.setPos(normRect.bottomLeft() + QPointF(self.BORDER_MARGIN, -self.margin2))
            self.__thicknessHandle.setPos(normRect.bottomLeft() + QPointF(self.BORDER_MARGIN + self.thickness, -self.margin2))
        elif Attachment.isBottom(self.__attachment):
            self.__marginHandle1.setPos(normRect.bottomLeft() + QPointF(self.margin1, -self.BORDER_MARGIN))
            self.__marginHandle2.setPos(normRect.bottomRight() + QPointF(-self.margin2, -self.BORDER_MARGIN))
            self.__thicknessHandle.setPos(normRect.bottomLeft() + QPointF(self.margin1, -(self.BORDER_MARGIN + self.thickness)))
        elif Attachment.isRight(self.__attachment):
            self.__marginHandle1.setPos(normRect.topRight() + QPointF(-self.BORDER_MARGIN, self.margin1))
            self.__marginHandle2.setPos(normRect.bottomRight() + QPointF(-self.BORDER_MARGIN, -self.margin2))
            self.__thicknessHandle.setPos(normRect.bottomRight() + QPointF(-(self.BORDER_MARGIN + self.thickness), -self.margin2))

    def removeSliderHandles(self):
        scene = self.scene()
        if self.__marginHandle1:
            scene.removeItem(self.__marginHandle1)
            self.__marginHandle1 = None
        if self.__marginHandle2:
            scene.removeItem(self.__marginHandle2)
            self.__marginHandle2 = None
        if self.__thicknessHandle:
            scene.removeItem(self.__thicknessHandle)
            self.__thicknessHandle = None
        return

    def mousePressEvent(self, event):
        if self.__marginHandle1:
            QGraphicsItem.mousePressEvent(self, event)
            return
        RectangleDropSliderItem.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        RectangleEditableDropItem.mouseMoveEvent(self, event)
        if bool(self.__pressedSliderRegion & (SliderPressRegion.HANDLE | SliderPressRegion.BASE)):
            self.calculateValueForMousePosition(event.pos())
            self.scene().isHandleWorking = True

    def mouseReleaseEvent(self, event):
        RectangleEditableDropItem.mouseReleaseEvent(self, event)

    def changeSliderAttachment(self, attach):
        if attach == 'No':
            self.attachment = Attachment.NotValid
        elif attach == 'Top':
            self.attachment = Attachment.TOP
        elif attach == 'Bottom':
            self.attachment = Attachment.BOTTOM
        elif attach == 'Left':
            self.attachment = Attachment.LEFT
        elif attach == 'Right':
            self.attachment = Attachment.RIGHT
        else:
            return
        self.comm.itemChanged.emit('attachment')

    def sceneEventFilter(self, watched, event):
        if watched in [self.__marginHandle1, self.__marginHandle2, self.__thicknessHandle]:
            if event.type() == QEvent.GraphicsSceneMousePress:
                watched.mousePos = event.pos()
            elif event.type() == QEvent.GraphicsSceneMouseRelease:
                pass
            elif event.type() == QEvent.GraphicsSceneMouseMove:
                offset = event.pos() - watched.mousePos
                self.changeSlider(watched, offset)
                self.scene().isHandleWorking = True
            else:
                return False
            return True
        else:
            return RectangleDropItem.sceneEventFilter(self, watched, event)

    def changeSlider(self, handle, offset):
        if handle == self.__marginHandle1:
            self.changeMargin('margin1', offset)
        elif handle == self.__marginHandle2:
            self.changeMargin('margin2', offset)
        elif handle == self.__thicknessHandle:
            self.changeThickness(offset)

    def changeMargin(self, target, offset):
        self.prepareGeometryChange()
        if target not in ('margin1', 'margin2'):
            return
        isMargin1 = bool(target == 'margin1')
        if Attachment.isHorizontal(self.__attachment):
            delta = offset.y() * (isMargin1 and 1 or -1)
        elif Attachment.isVertical(self.__attachment):
            delta = offset.x() * (isMargin1 and 1 or -1)
        else:
            return
        newMargin = max((isMargin1 and self.margin1 or self.margin2) + delta, self.BORDER_MARGIN)
        if Attachment.isHorizontal(self.__attachment):
            newMargin = min(newMargin, self.height - (isMargin1 and self.margin2 or self.margin1) - self.SLIDER_THICKNESS)
        elif Attachment.isVertical(self.__attachment):
            newMargin = min(newMargin, self.width - (isMargin1 and self.margin2 or self.margin1) - self.SLIDER_THICKNESS)
        if isMargin1:
            self.margin1 = newMargin
        else:
            self.margin2 = newMargin
        if Attachment.isVertical(self.__attachment):
            self.minWidth = self.margin1 + self.margin2 + self.thickness
        else:
            self.minHeight = self.margin1 + self.margin2 + self.thickness
        self.resetSliderRects()
        self.update()
        self.repositionSliderHandles()

    def changeThickness(self, offset):
        self.prepareGeometryChange()
        if Attachment.isLeft(self.__attachment):
            delta = offset.x()
        elif Attachment.isRight(self.__attachment):
            delta = -offset.x()
        elif Attachment.isTop(self.__attachment):
            delta = offset.y()
        elif Attachment.isBottom(self.__attachment):
            delta = -offset.y()
        else:
            return
        if Attachment.isHorizontal(self.__attachment):
            newThickness = min(max(self.thickness + delta, self.SLIDER_THICKNESS), self.width - self.BORDER_MARGIN * 2)
            self.minWidth = self.BORDER_MARGIN * 2 + self.thickness
        else:
            newThickness = min(max(self.thickness + delta, self.SLIDER_THICKNESS), self.height - self.BORDER_MARGIN * 2)
            self.minHeight = self.BORDER_MARGIN * 2 + self.thickness
        self.thickness = newThickness
        self.resetSliderRects()
        self.update()
        self.repositionSliderHandles()

    def resizeToPosition(self, pos):
        RectangleEditableDropItem.resizeToPosition(self, pos)
        self.resetSliderRects()
        self.repositionSliderHandles()