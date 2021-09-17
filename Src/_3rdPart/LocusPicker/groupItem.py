# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\groupItem.py
try:
    from PySide2.QtCore import Qt, QRectF, QPointF, QObject, Signal
    from PySide2.QtGui import QPainterPath, QPainter, QPen, QFont, QFontMetricsF, QColor, QTextOption, QPixmap
    from PySide2.QtWidgets import QGraphicsItem, QMenu, QActionGroup
except:
    from PySide.QtCore import Qt, QRectF, QPointF, QObject, Signal
    from PySide.QtGui import QGraphicsItem, QPainterPath, QPainter, QPen, QFont, QFontMetricsF, QColor, QTextOption, QPixmap, QMenu, QActionGroup

from decorator import accepts, returns
from locusPickerResources import *
from const import ButtonPosition, MIME_LABEL, MIME_CUSTOM_LABEL
import time
from copy import copy

class Communicator(QObject):
    undoOpen = Signal()
    undoClose = Signal()
    itemChanged = Signal()


class HoverRegion():
    NONE = 0
    LABEL = 1
    RESET = 2
    KEY = 4
    BASE = 8

    @classmethod
    def onLabel(cls, val):
        return bool(val & cls.LABEL)

    @classmethod
    def onReset(cls, val):
        return bool(val & cls.RESET)

    @classmethod
    def onKey(cls, val):
        return bool(val & cls.KEY)

    @classmethod
    def onBase(cls, val):
        return bool(val & cls.BASE)


class GroupItem(QGraphicsItem):
    DEFAULT_MINSIZE = 100
    PADDING = 10

    def __init__(self, width = DEFAULT_MINSIZE, height = DEFAULT_MINSIZE, parent = None):
        QGraphicsItem.__init__(self, parent)
        self.setFlags(QGraphicsItem.ItemSendsGeometryChanges | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.__font = QFont('Calibri', 9)
        self.__fontMetrics = QFontMetricsF(self.__font)
        self.comm = Communicator()
        self.__color = QColor(Qt.black)
        self.__label = ''
        self.__hashcode = ''
        self.__doReset = False
        self.__doKey = False
        self.__labelPosition = self.__buttonPosition = ButtonPosition.NORTH
        self.__hoverRegion = HoverRegion.NONE
        self.__width = self.__height = 0
        self.__editable = False
        self.__baseRect = QRectF()
        self.__resetRect = QRectF()
        self.__keyRect = QRectF()
        self.__labelRect = QRectF()
        self.width = width
        self.height = height

    @property
    @returns(QColor)
    def color(self):
        return self.__color

    @color.setter
    @accepts(QColor)
    def color(self, color):
        if self.__color != color:
            self.__color = color
            self.update()
            self.comm.itemChanged.emit()

    @property
    @returns(unicode)
    def label(self):
        return self.__label

    @label.setter
    @accepts(unicode)
    def label(self, label):
        if self.__label != label:
            self.__label = label
            self.refreshRect()
            self.comm.itemChanged.emit()

    @property
    @returns(str)
    def hashcode(self):
        return self.__hashcode

    @hashcode.setter
    @accepts(str)
    def hashcode(self, code):
        self.__hashcode = code

    @property
    @returns(bool)
    def doKey(self):
        return self.__doKey

    @doKey.setter
    @accepts(bool)
    def doKey(self, do):
        if self.__doKey != do:
            self.__doKey = do
            self.refreshRect()
            self.comm.itemChanged.emit()

    @property
    @returns(bool)
    def doReset(self):
        return self.__doReset

    @doReset.setter
    @accepts(bool)
    def doReset(self, do):
        if self.__doReset != do:
            self.__doReset = do
            self.refreshRect()
            self.comm.itemChanged.emit()

    @property
    @returns(float)
    def width(self):
        return self.__width

    @width.setter
    @accepts(float)
    def width(self, width):
        if self.__width != width:
            self.__width = width
            self.refreshRect()
            self.comm.itemChanged.emit()

    @property
    @returns(float)
    def height(self):
        return self.__height

    @height.setter
    @accepts(float)
    def height(self, height):
        if self.__height != height:
            self.__height = height
            self.refreshRect()
            self.comm.itemChanged.emit()

    @property
    @returns(int)
    def labelPosition(self):
        return self.__labelPosition

    @labelPosition.setter
    @accepts(int)
    def labelPosition(self, pos):
        if self.__labelPosition != pos:
            self.__labelPosition = pos
            self.refreshRect()
            self.comm.itemChanged.emit()

    @property
    @returns(int)
    def buttonPosition(self):
        return self.__buttonPosition

    @buttonPosition.setter
    @accepts(int)
    def buttonPosition(self, pos):
        if self.__buttonPosition != pos:
            self.__buttonPosition = pos
            self.refreshRect()
            self.comm.itemChanged.emit()

    @property
    @returns(bool)
    def editable(self):
        return self.__editable

    @editable.setter
    @accepts(bool)
    def editable(self, editable):
        self.__editable = editable
        for c in self.childItems():
            c.editable = not editable
            c.setIgnore(True)
            c.setSelected(False)
            c.setIgnore(False)

        self.setFocus()
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

    def type(self):
        from const import DropItemType
        return DropItemType.Group

    def boundingRect(self):
        return self.__baseRect.united(self.__labelRect).united(self.__resetRect).united(self.__keyRect)

    def refreshRect(self):
        self.baseRect()
        self.resetRect()
        self.keyRect()
        self.labelRect()
        self.update()

    def baseRect(self):
        self.__baseRect = QRectF(0, 0, self.width, self.height)

    def resetRect(self):
        if self.__doReset:
            rect = QRectF(0, 0, 20, 20)
            if ButtonPosition.isSouth(self.__buttonPosition):
                rect.moveTopRight(self.__baseRect.bottomRight())
            elif ButtonPosition.isWest(self.__buttonPosition):
                rect.moveBottomRight(self.__baseRect.bottomLeft())
            elif ButtonPosition.isEast(self.__buttonPosition):
                rect.moveBottomLeft(self.__baseRect.bottomRight())
            else:
                rect.moveBottomRight(self.__baseRect.topRight())
            self.__resetRect = rect
        else:
            self.__resetRect = QRectF()

    def keyRect(self):
        if self.__doKey:
            rect = QRectF(0, 0, 20, 20)
            if ButtonPosition.isSouth(self.__buttonPosition):
                if self.__doReset:
                    rect.moveTopRight(self.__resetRect.topLeft())
                else:
                    rect.moveTopRight(self.__baseRect.bottomRight())
            elif ButtonPosition.isWest(self.__buttonPosition):
                if self.__doReset:
                    rect.moveBottomRight(self.__resetRect.topRight())
                else:
                    rect.moveBottomRight(self.__baseRect.bottomLeft())
            elif ButtonPosition.isEast(self.__buttonPosition):
                if self.__doReset:
                    rect.moveBottomLeft(self.__resetRect.topLeft())
                else:
                    rect.moveBottomLeft(self.__baseRect.bottomRight())
            elif self.__doReset:
                rect.moveTopRight(self.__resetRect.topLeft())
            else:
                rect.moveBottomRight(self.__baseRect.topRight())
            self.__keyRect = rect
        else:
            self.__keyRect = QRectF()

    def labelRect(self):
        if self.__label:
            buttonRect = self.__resetRect.united(self.__keyRect)
            rect = self.__fontMetrics.boundingRect(self.__label).adjusted(-4, -2, 4, 2)
            if ButtonPosition.isSouth(self.__labelPosition):
                rect.moveTopLeft(self.__baseRect.bottomLeft())
                baseWidth = self.__baseRect.width()
                if rect.width() > baseWidth:
                    rect.setWidth(baseWidth)
                if rect.intersects(buttonRect):
                    rect.setRight(buttonRect.left())
            elif ButtonPosition.isWest(self.__labelPosition):
                width, height = rect.width(), rect.height()
                rect.setWidth(height)
                rect.setHeight(width)
                rect.moveTopRight(self.__baseRect.topLeft())
                baseHeight = self.__baseRect.height()
                if rect.height() > baseHeight:
                    rect.setHeight(baseHeight)
                if rect.intersects(buttonRect):
                    rect.setBottom(buttonRect.top())
            elif ButtonPosition.isEast(self.__labelPosition):
                width, height = rect.width(), rect.height()
                rect.setWidth(height)
                rect.setHeight(width)
                rect.moveTopLeft(self.__baseRect.topRight())
                baseHeight = self.__baseRect.height()
                if rect.height() > baseHeight:
                    rect.setHeight(baseHeight)
                if rect.intersects(buttonRect):
                    rect.setBottom(buttonRect.top())
            else:
                rect.moveBottomLeft(self.__baseRect.topLeft())
                baseWidth = self.__baseRect.width()
                if rect.width() > baseWidth:
                    rect.setWidth(baseWidth)
                if rect.intersects(buttonRect):
                    rect.setRight(buttonRect.left())
            self.__labelRect = rect
        else:
            self.__labelRect = QRectF()

    def shape(self):
        path = QPainterPath()
        path.addRect(self.__baseRect)
        path.addRect(self.__resetRect)
        path.addRect(self.__keyRect)
        path.addRect(self.__labelRect)
        return path

    def partialRoundedRectPath(self, rect, radius, region = None):
        if region is None:
            region = [False,
             False,
             True,
             True]
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, radius, radius)
        over_rect = QRectF(0, 0, radius, radius)
        if region[0]:
            over_rect.moveTopLeft(rect.topLeft())
            path.addRect(over_rect)
        if region[1]:
            over_rect.moveTopRight(rect.topRight())
            path.addRect(over_rect)
        if region[2]:
            over_rect.moveBottomLeft(rect.bottomLeft())
            path.addRect(over_rect)
        if region[3]:
            over_rect.moveBottomRight(rect.bottomRight())
            path.addRect(over_rect)
        return path.simplified()

    def paint(self, painter, option, widget = None):
        painter.setClipRect(option.exposedRect.adjusted(-1, -1, 1, 1))
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        painter.setPen(self.__editable and QPen(Qt.white, 1, Qt.DashLine) or Qt.NoPen)
        painter.setBrush(self.__color)
        path = QPainterPath()
        path.addRect(self.__baseRect)
        if self.__labelRect.isValid():
            if ButtonPosition.isSouth(self.__labelPosition):
                path = path.united(self.partialRoundedRectPath(self.__labelRect, 3, [True,
                 True,
                 False,
                 False]))
            elif ButtonPosition.isWest(self.__labelPosition):
                path = path.united(self.partialRoundedRectPath(self.__labelRect, 3, [False,
                 True,
                 False,
                 True]))
            elif ButtonPosition.isEast(self.__labelPosition):
                path = path.united(self.partialRoundedRectPath(self.__labelRect, 3, [True,
                 False,
                 True,
                 False]))
            else:
                path = path.united(self.partialRoundedRectPath(self.__labelRect, 3))
        if self.__resetRect:
            if ButtonPosition.isSouth(self.__buttonPosition):
                path = path.united(self.partialRoundedRectPath(self.__resetRect, 3, [True,
                 True,
                 False,
                 False]))
            elif ButtonPosition.isWest(self.__buttonPosition):
                path = path.united(self.partialRoundedRectPath(self.__resetRect, 3, [False,
                 True,
                 False,
                 True]))
            elif ButtonPosition.isEast(self.__buttonPosition):
                path = path.united(self.partialRoundedRectPath(self.__resetRect, 3, [True,
                 False,
                 True,
                 False]))
            else:
                path = path.united(self.partialRoundedRectPath(self.__resetRect, 3))
        if self.__keyRect:
            if ButtonPosition.isSouth(self.__buttonPosition):
                path = path.united(self.partialRoundedRectPath(self.__keyRect, 3, [True,
                 True,
                 False,
                 False]))
            elif ButtonPosition.isWest(self.__buttonPosition):
                path = path.united(self.partialRoundedRectPath(self.__keyRect, 3, [False,
                 True,
                 False,
                 True]))
            elif ButtonPosition.isEast(self.__buttonPosition):
                path = path.united(self.partialRoundedRectPath(self.__keyRect, 3, [True,
                 False,
                 True,
                 False]))
            else:
                path = path.united(self.partialRoundedRectPath(self.__keyRect, 3))
        path = path.simplified()
        painter.drawPath(path)
        if self.__labelRect.isValid():
            painter.setFont(self.__font)
            painter.setPen((HoverRegion.onLabel(self.__hoverRegion) or HoverRegion.onBase(self.__hoverRegion)) and Qt.white or Qt.lightGray)
            if ButtonPosition.isLongitude(self.__labelPosition):
                text = self.__fontMetrics.elidedText(self.label, Qt.ElideRight, self.__labelRect.height())
                drawRect = self.__labelRect.adjusted(0, 0, 0, 0)
                drawRect.setWidth(self.__labelRect.height())
                drawRect.setHeight(self.__labelRect.width())
                if ButtonPosition.isWest(self.__labelPosition):
                    drawRect.moveBottomRight(self.__baseRect.topLeft())
                else:
                    drawRect.moveBottomLeft(self.__baseRect.topLeft())
                painter.save()
                if ButtonPosition.isWest(self.__labelPosition):
                    painter.rotate(-90)
                else:
                    painter.rotate(90)
                    painter.translate(0, -self.width)
                painter.drawText(drawRect, text, QTextOption(Qt.AlignCenter))
                painter.restore()
            else:
                text = self.__fontMetrics.elidedText(self.label, Qt.ElideRight, self.__labelRect.width())
                painter.drawText(self.__labelRect, text, QTextOption(Qt.AlignCenter))
        if self.__resetRect:
            pixmap = QPixmap(HoverRegion.onReset(self.__hoverRegion) and ':/reset_hover' or ':/reset')
            painter.drawPixmap(self.__resetRect.adjusted(2, 2, -2, -2), pixmap, QRectF(QPointF(0, 0), pixmap.size()))
        if self.__keyRect:
            pixmap = QPixmap(HoverRegion.onKey(self.__hoverRegion) and ':/key_hover' or ':/key')
            painter.drawPixmap(self.__keyRect.adjusted(2, 2, -2, -2), pixmap, QRectF(QPointF(0, 0), pixmap.size()))

    def mousePressEvent(self, event):
        pos = event.pos()
        button = event.button()
        modifier = event.modifiers()
        if button == Qt.LeftButton and modifier == Qt.NoModifier and self.__keyRect.contains(pos):
            print '>> GROUP DO KEY'
            self.executeChildItems('Key')
        elif button == Qt.LeftButton and modifier == Qt.NoModifier and self.__resetRect.contains(pos):
            print '>> GROUP DO RESET'
            self.executeChildItems('Reset')
        QGraphicsItem.mousePressEvent(self, event)

    def hoverMoveEvent(self, event):
        pos = event.pos()
        if self.__labelRect.isValid() and self.__labelRect.contains(pos):
            self.hoverRegion = HoverRegion.LABEL
        elif self.__resetRect.isValid() and self.__resetRect.contains(pos):
            self.hoverRegion = HoverRegion.RESET
        elif self.__keyRect.isValid() and self.__keyRect.contains(pos):
            self.hoverRegion = HoverRegion.KEY
        elif self.__baseRect.isValid() and self.__baseRect.contains(pos):
            self.hoverRegion = HoverRegion.BASE
        else:
            self.hoverRegion = HoverRegion.NONE

    def hoverLeaveEvent(self, event):
        self.hoverRegion = HoverRegion.NONE

    def executeChildItems(self, command):
        self.comm.undoOpen.emit()
        for i in self.childItems():
            i.emitCommmand(command)

        self.comm.undoClose.emit()

    def properties(self, checkSettable = True):
        all_classes = self.__class__.mro()
        result_dict = {}
        for cls in all_classes:
            for k, v in cls.__dict__.iteritems():
                if isinstance(v, property):
                    if checkSettable and v.fset is None:
                        continue
                    result_dict[k] = getattr(self, k)

        return result_dict


class EditableGroupItem(GroupItem):

    def __init__(self, width = GroupItem.DEFAULT_MINSIZE, height = GroupItem.DEFAULT_MINSIZE, parent = None):
        GroupItem.__init__(self, width, height, parent)
        self.setAcceptDrops(True)
        self.__isMoving = False

    def itemChange(self, change, value):
        scene = self.scene()
        if change == QGraphicsItem.ItemPositionChange:
            if scene and scene.primaryView().isVisible() and scene.coop:
                rect = QRectF(QPointF(0, 0), scene.mapSize).adjusted(0, 0, -self.width, -self.height)
                if not rect.contains(value):
                    value.setX(min(max(value.x(), rect.left()), rect.right()))
                    value.setY(min(max(value.y(), rect.top()), rect.bottom()))
                    return value
        elif change == QGraphicsItem.ItemPositionHasChanged:
            self.comm.itemChanged.emit()
        return QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        button = event.button()
        modifier = event.modifiers()
        if self.editable and button == Qt.LeftButton and modifier == Qt.AltModifier | Qt.ShiftModifier:
            self.setFlags(self.flags() | QGraphicsItem.ItemIsMovable)
            self.__isMoving = True
            self.setCursor(Qt.ClosedHandCursor)
        GroupItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.__isMoving:
            self.setFlags(self.flags() ^ QGraphicsItem.ItemIsMovable)
        self.__isMoving = False
        GroupItem.mouseReleaseEvent(self, event)

    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        if self.editable and modifiers == Qt.AltModifier | Qt.ShiftModifier:
            self.setCursor(Qt.OpenHandCursor)
        GroupItem.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if self.cursor().shape() != Qt.ArrowCursor:
            self.setCursor(Qt.ArrowCursor)
        QGraphicsItem.keyReleaseEvent(self, event)

    def hoverEnterEvent(self, event):
        modifier = event.modifiers()
        if self.editable and modifier == Qt.AltModifier | Qt.ShiftModifier:
            self.setCursor(Qt.OpenHandCursor)
            self.setFocus()

    def hoverMoveEvent(self, event):
        modifier = event.modifiers()
        if self.editable and modifier == Qt.AltModifier | Qt.ShiftModifier:
            self.setCursor(Qt.OpenHandCursor)
        GroupItem.hoverMoveEvent(self, event)

    def hoverLeaveEvent(self, event):
        if self.editable:
            self.setCursor(Qt.ArrowCursor)
            self.clearFocus()
        GroupItem.hoverLeaveEvent(self, event)

    def dragEnterEvent(self, event):
        mimeData = event.mimeData()
        if self.editable and (mimeData.hasFormat('text/plain') or mimeData.hasFormat(MIME_LABEL) or mimeData.hasFormat(MIME_CUSTOM_LABEL)):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
        GroupItem.dragEnterEvent(self, event)

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if self.editable and (mimeData.hasFormat('text/plain') or mimeData.hasFormat(MIME_LABEL) or mimeData.hasFormat(MIME_CUSTOM_LABEL)):
            if self.contains(event.pos()):
                if mimeData.hasFormat('text/plain'):
                    text = unicode(mimeData.data('text/plain')).strip()
                elif mimeData.hasFormat(MIME_LABEL):
                    text = unicode(mimeData.data(MIME_LABEL)).strip()
                elif mimeData.hasFormat(MIME_CUSTOM_LABEL):
                    text = unicode(mimeData.data(MIME_CUSTOM_LABEL)).strip()
                self.label = text

    def contextMenuEvent(self, event):
        scene = self.scene()
        if scene.editable:
            menu = QMenu()
            editModeAct = menu.addAction('Group Edit Mode')
            editModeAct.setCheckable(True)
            editModeAct.setChecked(self.editable)
            editModeAct.toggled.connect(lambda x: setattr(self, 'editable', x))
            removeAct = menu.addAction('Remove Group')
            removeAct.triggered.connect(self.removeByItself)
            fitToChildrenAct = menu.addAction('Fit to Children')
            fitToChildrenAct.triggered.connect(self.adjustSizeToFitChildItems)
            menu.addSeparator()
            resetAct = menu.addAction('Reset Button')
            resetAct.setCheckable(True)
            resetAct.setChecked(self.doReset)
            resetAct.toggled.connect(lambda x: setattr(self, 'doReset', x))
            keyAct = menu.addAction('Key Button')
            keyAct.setCheckable(True)
            keyAct.setChecked(self.doKey)
            keyAct.toggled.connect(lambda x: setattr(self, 'doKey', x))
            self.addLabelPositionRadioActions(menu)
            self.addButtonPositionRadioActions(menu)
            menu.exec_(event.screenPos())

    def addLabelPositionRadioActions(self, menu):
        positionSep = menu.addAction('Label Position')
        positionSep.setSeparator(True)
        northAct = menu.addAction('North')
        northAct.pos = ButtonPosition.NORTH
        northAct.setCheckable(True)
        southAct = menu.addAction('South')
        southAct.pos = ButtonPosition.SOUTH
        southAct.setCheckable(True)
        westAct = menu.addAction('West')
        westAct.pos = ButtonPosition.WEST
        westAct.setCheckable(True)
        eastAct = menu.addAction('East')
        eastAct.pos = ButtonPosition.EAST
        eastAct.setCheckable(True)
        buttonPosGrp = QActionGroup(menu)
        buttonPosGrp.addAction(northAct)
        buttonPosGrp.addAction(southAct)
        buttonPosGrp.addAction(westAct)
        buttonPosGrp.addAction(eastAct)
        if ButtonPosition.isSouth(self.labelPosition):
            southAct.setChecked(True)
        elif ButtonPosition.isWest(self.labelPosition):
            westAct.setChecked(True)
        elif ButtonPosition.isEast(self.labelPosition):
            eastAct.setChecked(True)
        else:
            northAct.setChecked(True)
        buttonPosGrp.triggered.connect(lambda x: setattr(self, 'labelPosition', x.pos))

    def addButtonPositionRadioActions(self, menu):
        positionSep = menu.addAction('Button Position')
        positionSep.setSeparator(True)
        northAct = menu.addAction('North')
        northAct.pos = ButtonPosition.NORTH
        northAct.setCheckable(True)
        southAct = menu.addAction('South')
        southAct.pos = ButtonPosition.SOUTH
        southAct.setCheckable(True)
        westAct = menu.addAction('West')
        westAct.pos = ButtonPosition.WEST
        westAct.setCheckable(True)
        eastAct = menu.addAction('East')
        eastAct.pos = ButtonPosition.EAST
        eastAct.setCheckable(True)
        buttonPosGrp = QActionGroup(menu)
        buttonPosGrp.addAction(northAct)
        buttonPosGrp.addAction(southAct)
        buttonPosGrp.addAction(westAct)
        buttonPosGrp.addAction(eastAct)
        if ButtonPosition.isSouth(self.buttonPosition):
            southAct.setChecked(True)
        elif ButtonPosition.isWest(self.buttonPosition):
            westAct.setChecked(True)
        elif ButtonPosition.isEast(self.buttonPosition):
            eastAct.setChecked(True)
        else:
            northAct.setChecked(True)
        buttonPosGrp.triggered.connect(lambda x: setattr(self, 'buttonPosition', x.pos))

    def adjustSizeToFitChildItems(self):
        rect = QRectF()
        for item in self.childItems():
            rect = rect.united(item.sceneBoundingRect())

        rect.adjust(-self.PADDING, -self.PADDING, self.PADDING, self.PADDING)
        offset = self.pos() - rect.topLeft()
        self.setPos(rect.topLeft())
        self.width, self.height = rect.width(), rect.height()
        for item in self.childItems():
            item.moveBy(offset.x(), offset.y())

    def removeByItself(self):
        scene = self.scene()
        view = scene.primaryView()
        from dialog import TriStateDialog
        dlg = TriStateDialog('Remove', 'Do you want to remove all of child items as well?', 'Remove All', 'Leave them', 'Cancel', view)
        answer = dlg.exec_()
        if answer == 1:
            for i in self.childItems():
                i.setParentItem(None)

        if answer == 0 or answer == 1:
            collidingItems = self.collidingItems(Qt.IntersectsItemBoundingRect)
            for ci in collidingItems:
                ci.hide()

            scene.removeItem(self)
            for ci in collidingItems:
                ci.show()

            self.comm.itemChanged.emit()
        return

    def clone(self):
        valuesDict = self.properties()
        params = []
        for initParam in self.__init__.__func__.__code__.co_varnames[1:]:
            if initParam in valuesDict:
                v = valuesDict[initParam]
                del valuesDict[initParam]
                params.append(v)

        item = self.__class__(*params)
        for k, v in valuesDict.items():
            try:
                setattr(item, k, copy(v))
            except AttributeError:
                print ">> Can't set [%s]" % k

        return item