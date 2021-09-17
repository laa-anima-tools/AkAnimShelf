# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\dropItem.py
try:
    from PySide2.QtCore import QRectF, Qt, Signal, QObject, QPointF, QEvent, QByteArray, QLineF
    from PySide2.QtGui import QColor, QPixmap, QPainter, QPen, QPainterPath, QCursor, QFontMetricsF, QFont, QPolygonF
    from PySide2.QtWidgets import QGraphicsItem, QApplication, QMenu, QGraphicsBlurEffect
except:
    from PySide.QtCore import QRectF, Qt, Signal, QObject, QPointF, QEvent, QByteArray, QLineF
    from PySide.QtGui import QGraphicsItem, QColor, QPixmap, QPainter, QPen, QPainterPath, QApplication, QMenu, QCursor, QGraphicsBlurEffect, QFontMetricsF, QFont, QPolygonF

from decorator import accepts, returns, timestamp
from editHandle import SizeMoveHandle
from const import SELECTED_BORDER_COLOR, FONT_FAMILIES, MIME_COLOR_MODIFIER, MIME_COLOR, MIME_IMAGE, MIME_DRAGCOMBO_TEXT, MIME_COMMAND, MIME_LABEL, MIME_FONT_FAMILY, MIME_FONT_SIZE, MIME_FONT_BOLD, MIME_FONT_ITALIC, MIME_CUSTOM_LABEL, question, CursorPos, MIME_IMAGE_PATH, MIME_IMAGE_RECT, MIME_IMAGE_BUTTONSIZE, generateHashcode
import base64, os, time
from copy import copy

def getLinkedItems(item):
    result = []
    for item in item.linkedItems:
        if not item.isVisible():
            continue
        result.append(item)
        if item.linkedItems:
            for i in getLinkedItems(item):
                if i not in result:
                    result.append(i)

    return result


class Communicator(QObject):
    sendCommandData = Signal(unicode, list, list, list, unicode)
    itemChanged = Signal(str)
    sizeChanged = Signal()
    redefineMember = Signal(QGraphicsItem)
    changeMember = Signal(QGraphicsItem, unicode, bool, unicode)
    editRemote = Signal(QGraphicsItem)
    mousePressed = Signal()
    mouseReleased = Signal()
    aboutToRemove = Signal(QGraphicsItem)


class ClickTimer(QObject):
    EXECUTE = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.timerId = None
        self.initializeData()
        return

    def setData(self, button, modifier, pos, selected):
        self.button = button
        self.modifier = modifier
        self.pos = pos
        self.isSelected = selected

    def initializeData(self):
        self.button = None
        self.modifier = None
        self.pos = None
        self.isSelected = False
        return

    def start(self, interval):
        self.timerId = self.startTimer(interval)

    def timerEvent(self, event):
        if self.timerId == event.timerId():
            self.EXECUTE.emit()
        self.removeTimer()

    def removeTimer(self):
        if self.timerId:
            self.killTimer(self.timerId)
        self.timerId = None
        return


class GraphicsLayeredBlurEffect(QGraphicsBlurEffect):

    def __init__(self, parent = None):
        QGraphicsBlurEffect.__init__(self, parent)
        self.innerRadius = 0
        self.outerRadius = 0

    def setInnerRadius(self, radius):
        self.innerRadius = radius

    def setOuterRadius(self, radius):
        self.outerRadius = radius

    def draw(self, painter):
        if self.outerRadius > 0:
            self.setBlurRadius(self.outerRadius)
            QGraphicsBlurEffect.draw(self, painter)
        if self.innerRadius > 0:
            self.setBlurRadius(self.innerRadius)
            QGraphicsBlurEffect.draw(self, painter)
        QGraphicsBlurEffect.drawSource(self, painter)


class AbstractDropItem(QGraphicsItem):
    BORDER_MARGIN = 0
    EDITABLE_MARGIN = 4
    BLUR_OUTERRADIUS = 6
    BLUR_INNERRADIUS = 2
    ICON_MINSIZE = 4
    DEFAULT_MINSIZE = 10

    def __init__(self, color = QColor(), width = 20, height = 20, parent = None):
        QGraphicsItem.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setFlags(QGraphicsItem.ItemClipsChildrenToShape | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.__effect = GraphicsLayeredBlurEffect()
        self.setGraphicsEffect(self.__effect)
        self.__command = ''
        self.__targetNode, self.__targetChannel, self.__targetValue = [], [], []
        self.__color = color
        self.__font = QFont('Tahoma', 9.0)
        self.__fontColor = QColor(Qt.black)
        self.__labelRect = QRectF()
        self.__label = ''
        self.__icon = QPixmap()
        self.__iconRect = QRectF()
        self.__iconPath = ''
        self.__hashcode__ = ''
        self.__width, self.__height = width, height
        self.__minWidth = self.__minHeight = self.DEFAULT_MINSIZE
        self.comm = Communicator()
        self.__add = self.__hover = self.__ignore = self.__dblClicking = False
        self.__pressRegion = 0
        self.__pressPos = QPointF()
        self.ignoreStartValue = False
        self.__timer = ClickTimer()
        self.__timer.EXECUTE.connect(self.timeoutCalled)
        self.__linkedItems = []
        self.__lines = {}

    @property
    @returns(str)
    def hashcode(self):
        return self.__hashcode__

    @hashcode.setter
    @accepts(str)
    def hashcode(self, code):
        self.__hashcode__ = code

    @property
    @returns(float)
    def width(self):
        return self.__width

    @width.setter
    @accepts(float)
    def width(self, width):
        self.prepareGeometryChange()
        self.__width = width
        self.comm.sizeChanged.emit()

    @property
    @returns(float)
    def height(self):
        return self.__height

    @height.setter
    @accepts(float)
    def height(self, height):
        self.prepareGeometryChange()
        self.__height = height
        self.comm.sizeChanged.emit()

    @property
    @returns(float)
    def minWidth(self):
        return self.__minWidth

    @minWidth.setter
    @accepts(float)
    def minWidth(self, width):
        self.__minWidth = width

    @property
    @returns(float)
    def minHeight(self):
        return self.__minHeight

    @minHeight.setter
    @accepts(float)
    def minHeight(self, height):
        self.__minHeight = height

    @property
    @returns(QFont)
    def font(self):
        return self.__font

    @font.setter
    @accepts(QFont)
    def font(self, font):
        if font.family() in FONT_FAMILIES:
            self.__font = font
            self.update()

    @property
    @returns(QColor)
    def fontColor(self):
        return self.__fontColor

    @fontColor.setter
    @accepts(QColor)
    def fontColor(self, color):
        self.__fontColor = color
        self.update()

    @property
    @returns(unicode)
    def label(self):
        return self.__label

    @label.setter
    @accepts(unicode)
    def label(self, label):
        self.__label = label
        self.update()

    @property
    @returns(QRectF)
    def labelRect(self):
        return self.__labelRect

    @labelRect.setter
    @accepts(QRectF)
    def labelRect(self, rect):
        self.prepareGeometryChange()
        self.__labelRect = rect

    @property
    @returns(QColor)
    def color(self):
        return self.__color

    @color.setter
    @accepts(QColor)
    def color(self, color):
        self.__color = color
        if color.lightnessF() > 0.5:
            self.fontColor = QColor(Qt.black)
        else:
            self.fontColor = QColor(Qt.white)

    @property
    @returns(unicode)
    def command(self):
        return self.__command

    @command.setter
    @accepts(unicode)
    def command(self, command):
        self.__command = command

    @property
    @returns(list)
    def targetNode(self):
        return self.__targetNode

    @targetNode.setter
    @accepts(list)
    def targetNode(self, node):
        self.__targetNode = node

    @property
    @returns(list)
    def targetChannel(self):
        return self.__targetChannel

    @targetChannel.setter
    @accepts(list)
    def targetChannel(self, channel):
        self.__targetChannel = channel

    @property
    @returns(list)
    def targetValue(self):
        return self.__targetValue

    @targetValue.setter
    @accepts(list)
    def targetValue(self, value):
        self.__targetValue = value

    @property
    @returns(bool)
    def hover(self):
        return self.__hover

    @hover.setter
    @accepts(bool)
    def hover(self, hover):
        self.__hover = hover

    def setIgnore(self, ignore):
        self.__ignore = ignore

    def isIgnore(self):
        return self.__ignore

    @property
    @returns(QPointF)
    def pressPos(self):
        return self.__pressPos

    @pressPos.setter
    @accepts(QPointF)
    def pressPos(self, pos):
        self.__pressPos = pos

    @property
    @returns(int)
    def pressRegion(self):
        return self.__pressRegion

    @pressRegion.setter
    @accepts(int)
    def pressRegion(self, region):
        self.__pressRegion = region

    @property
    @returns(QRectF)
    def iconRect(self):
        return self.__iconRect

    @iconRect.setter
    @accepts(QRectF)
    def iconRect(self, rect):
        self.prepareGeometryChange()
        self.__iconRect = rect

    @property
    @returns(unicode)
    def iconPath(self):
        return self.__iconPath

    @iconPath.setter
    @accepts(unicode)
    def iconPath(self, path):
        self.__iconPath = path
        self.icon = QPixmap(path)
        self.setDefaultIconRect()
        if self.__iconRect.isEmpty():
            self.__iconPath = ''
            self.icon = QPixmap()
        self.matchMinSizeToSubordinate()
        self.update()

    @property
    @returns(QPixmap)
    def icon(self):
        return self.__icon

    @icon.setter
    @accepts(QPixmap)
    def icon(self, iconPixmap):
        self.__icon = iconPixmap

    @property
    def effect(self):
        return self.__effect

    @property
    def timer(self):
        return self.__timer

    @property
    def linkedItems(self):
        return self.__linkedItems

    @linkedItems.setter
    def linkedItems(self, items):
        self.__linkedItems[:] = items
        scene = self.scene()
        keys = self.__lines.keys()
        for item in keys:
            if item not in self.__linkedItems:
                line = self.__lines[item]
                del self.__lines[item]
                scene.removeItem(line)
                item.comm.aboutToRemove.disconnect(self.popLinkedItem)

        keys = self.__lines.keys()
        for item in self.__linkedItems:
            if item not in keys:
                self.__lines[item] = LineItem(self, item, scene=scene)
                self.__lines[item].setZValue(0)
                item.comm.aboutToRemove.connect(self.popLinkedItem)

    def popLinkedItem(self, item):
        buf = self.linkedItems[:]
        del buf[buf.index(item)]
        self.linkedItems = buf

    @property
    def lines(self):
        return self.__lines

    def setVisible(self, visible):
        QGraphicsItem.setVisible(self, visible)
        for l in self.__lines.values():
            l.setVisible(visible)

        for i in self.scene().findLinkedParentItems(self):
            i.lines[self].setVisible(visible)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def inboundRect(self):
        return self.boundingRect().adjusted(self.BORDER_MARGIN, self.BORDER_MARGIN, -self.BORDER_MARGIN, -self.BORDER_MARGIN)

    def paint(self, painter, option, widget = None):
        painter.setClipRect(option.exposedRect.adjusted(-1, -1, 1, 1))
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        painter.setPen(self.isSelected() and QPen(SELECTED_BORDER_COLOR, 1.5, j=Qt.RoundJoin) or Qt.NoPen)
        painter.setBrush(self.isSelected() and self.color.lighter(105) or self.color)

    def setSelected(self, selected, add = False):
        self.__add = add
        QGraphicsItem.setSelected(self, selected)
        self.__add = False

    def setParentItem(self, item):
        if item:
            pos = self.scenePos() - item.pos()
        else:
            pos = self.scenePos()
        QGraphicsItem.setParentItem(self, item)
        self.setPos(pos)

    def getKeyboardModifier(self):
        if self.__add:
            return 'Ctrl+Shift'
        modifier = QApplication.keyboardModifiers()
        if modifier == Qt.NoModifier:
            return 'No'
        elif modifier == Qt.ControlModifier:
            return 'Ctrl'
        elif modifier == Qt.ShiftModifier:
            return 'Shift'
        elif modifier == Qt.AltModifier:
            return 'Alt'
        elif modifier == Qt.ControlModifier | Qt.ShiftModifier:
            return 'Ctrl+Shift'
        else:
            return 'No'

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            modifier = self.getKeyboardModifier()
            if self.isSelected() and self.command.startswith('Select'):
                if not self.__ignore:
                    self.emitCommmand(self.command, modifier=modifier)
            elif not self.isSelected() and self.command.startswith('Select'):
                if not self.__ignore:
                    self.emitCommmand(('De' + self.command).capitalize(), modifier=modifier)
        return QGraphicsItem.itemChange(self, change, value)

    def mouseDoubleClickEvent(self, event):
        self.__dblClicking = True
        self.__timer.removeTimer()
        for item in getLinkedItems(self):
            item.setSelected(True, True)

    def timeoutCalled(self):
        button = self.__timer.button
        modifier = self.__timer.modifier
        if button == Qt.LeftButton and modifier == Qt.NoModifier and not self.command.startswith('Select'):
            if self.command == 'Pose':
                self.ignoreStartValue = True
                self.comm.mousePressed.emit()
                self.emitCommmand(self.command, modifier='1.0')
            elif self.command == 'Range':
                self.emitCommmand('Toggle')
            else:
                self.emitCommmand(self.command)
        elif button == Qt.LeftButton and modifier == Qt.AltModifier:
            self.emitCommmand('Key')
        elif button == Qt.LeftButton and modifier == Qt.ShiftModifier:
            self.setIgnore(False)
            self.setSelected(not self.__timer.isSelected)

    def mousePressEvent(self, event):
        isSelected = self.isSelected()
        self.setIgnore(True)
        QGraphicsItem.mousePressEvent(self, event)
        self.setSelected(isSelected)
        self.setIgnore(False)
        self.__timer.setData(event.button(), event.modifiers(), event.pos(), isSelected)
        self.__timer.start(0)

    def mouseReleaseEvent(self, event):
        if self.__dblClicking:
            self.__dblClicking = False
            return False
        button = event.button()
        modifier = event.modifiers()
        if button == Qt.LeftButton and modifier == Qt.AltModifier | Qt.ControlModifier | Qt.ShiftModifier:
            self.comm.redefineMember.emit(self)
            return False
        if self.command == 'Pose':
            self.comm.mouseReleased.emit()
        isSelected = self.isSelected()
        if modifier == Qt.ControlModifier or modifier == Qt.ShiftModifier:
            if not isSelected:
                self.setIgnore(True)
        QGraphicsItem.mouseReleaseEvent(self, event)
        if modifier == Qt.ShiftModifier:
            if not isSelected:
                self.setSelected(False)
        elif modifier == Qt.ControlModifier | Qt.ShiftModifier:
            if isSelected:
                self.setSelected(True)
        self.setIgnore(False)
        if modifier == Qt.ControlModifier:
            self.setSelected(False)
        if button == Qt.LeftButton and modifier == Qt.AltModifier:
            if not isSelected:
                self.setSelected(False)
            self.__ignore = False
        return True

    def hoverEnterEvent(self, event):
        self.hover = True
        self.toggleShadow(True)

    def hoverLeaveEvent(self, event):
        self.hover = False
        self.toggleShadow(False)

    def toggleShadow(self, toggle):
        if toggle:
            self.effect.setOuterRadius(self.BLUR_OUTERRADIUS)
            self.effect.setInnerRadius(self.BLUR_INNERRADIUS)
            self.setFocus()
        else:
            self.effect.setOuterRadius(0)
            self.effect.setInnerRadius(0)
            self.clearFocus()
        self.update()

    def contextMenuEvent(self, event):
        menu = self.createCustomContextMenu(event)
        if menu:
            menu.exec_(event.screenPos())

    def createCustomContextMenu(self, event):
        menu = QMenu()
        self.createDefaultPopupMenu(menu)
        return menu

    def createDefaultPopupMenu(self, menu):
        if self.command != 'Select':
            selectAct = menu.addAction('Select')
            selectAct.triggered.connect(lambda : self.emitCommmand('Select'))
        if self.command != 'Key':
            keyAct = menu.addAction('Key')
            keyAct.triggered.connect(lambda : self.emitCommmand('Key'))
        keyTransformAct = menu.addAction('Key Transform')
        keyTransformAct.triggered.connect(lambda : self.emitCommmand('Key', 'Transform'))
        if self.command != 'Reset':
            resetAct = menu.addAction('Reset')
            resetAct.triggered.connect(lambda : self.emitCommmand('Reset'))
        resetTransformAct = menu.addAction('Reset Transform')
        resetTransformAct.triggered.connect(lambda : self.emitCommmand('Reset', 'Transform'))

    def emitCommmand(self, command = '', channelFlag = '', modifier = 'No'):
        if channelFlag == 'Transform':
            channel = ['tx',
             'ty',
             'tz',
             'rx',
             'ry',
             'rz',
             'sx',
             'sy',
             'sz']
        elif channelFlag == 'All':
            channel = ''
        elif channelFlag == '':
            channel = self.targetChannel
        if command == 'Reset' and hasattr(self, 'setValue'):
            self.setValue(0, False)
        self.comm.sendCommandData.emit(command, self.targetNode, channel, self.targetValue, modifier)

    def matchMinSizeToSubordinate(self):
        self.prepareGeometryChange()
        rect = self.iconRect.united(self.labelRect)
        self.minWidth = max(rect.width() + self.BORDER_MARGIN * 2, self.DEFAULT_MINSIZE)
        self.minHeight = max(rect.height() + self.BORDER_MARGIN * 2, self.DEFAULT_MINSIZE)
        if self.minWidth > self.width:
            self.width = self.minWidth
        if self.minHeight > self.height:
            self.height = self.minHeight

    def setDefaultIconRect(self):
        self.prepareGeometryChange()
        rect = self.inboundRect()
        if rect.isEmpty():
            self.iconRect = QRectF()
        else:
            if self.__icon:
                iconSize = self.__icon.size()
                iconRatio = iconSize.width() * 1.0 / iconSize.height()
                rectSize = rect.size()
                rectRatio = rectSize.width() * 1.0 / rectSize.height()
                if iconRatio > rectRatio:
                    offset = (rect.height() - rect.width() / iconRatio) / 2
                    rect.adjust(0, offset, 0, -offset)
                elif iconRatio < rectRatio:
                    offset = (rect.width() - rect.height() * iconRatio) / 2
                    rect.adjust(offset, 0, -offset, 0)
            self.iconRect = rect

    def getDefaultLabelRect(self):
        fontMetrics = QFontMetricsF(self.font)
        boundingRect = self.inboundRect()
        return (fontMetrics.boundingRect(boundingRect, Qt.AlignHCenter | Qt.AlignBottom | Qt.TextWordWrap, self.label + '*'), boundingRect)

    def setDefaultLabelRect(self):
        rect, boundingRect = self.getDefaultLabelRect()
        if boundingRect.contains(rect):
            self.labelRect = rect
        else:
            if rect.height() > boundingRect.height():
                rect.moveTopLeft(boundingRect.topLeft())
            else:
                rect.moveBottomLeft(boundingRect.bottomLeft())
            return rect

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


class AbstractEditableDropItem(AbstractDropItem):

    def __init__(self, color = QColor(), width = 20, height = 20, parent = None):
        AbstractDropItem.__init__(self, color, width, height, parent)
        self.__labelMoveHandle = None
        self.__iconTopHandle = self.__iconLeftHandle = self.__iconBottomHandle = self.__iconRightHandle = self.__iconCenterHandle = None
        self.__editable = True
        self.__isMoving = False
        return

    @property
    def editable(self):
        return self.__editable

    @editable.setter
    def editable(self, editable):
        self.__editable = editable

    @property
    def labelMoveHandle(self):
        return self.__labelMoveHandle

    def linkSelectedItems(self):
        scene = self.scene()
        selected = scene.selectedItems()
        for i in xrange(len(selected) - 1, -1, -1):
            if selected[i] == self:
                del selected[i]

        self.linkedItems = selected
        self.comm.itemChanged.emit('Link')

    def setZValue(self, value):
        QGraphicsItem.setZValue(self, value)
        self.comm.itemChanged.emit('zValue')

    def setParentItem(self, item):
        if item:
            pos = self.scenePos() - item.pos()
        else:
            pos = self.scenePos()
        QGraphicsItem.setParentItem(self, item)
        self.setPos(pos)

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
            self.comm.itemChanged.emit('position')
        return AbstractDropItem.itemChange(self, change, value)

    def dragEnterEvent(self, event):
        if self.editable:
            mimeData = event.mimeData()
            if mimeData.hasFormat(MIME_COLOR_MODIFIER) or mimeData.hasUrls() or mimeData.hasFormat('text/plain') or mimeData.hasFormat(MIME_DRAGCOMBO_TEXT) or mimeData.hasFormat(MIME_COLOR) or mimeData.hasFormat(MIME_COMMAND) or mimeData.hasFormat(MIME_LABEL) or mimeData.hasFormat(MIME_FONT_FAMILY) or mimeData.hasFormat(MIME_IMAGE_PATH) or mimeData.hasFormat(MIME_CUSTOM_LABEL):
                event.setDropAction(Qt.CopyAction)
                event.accept()
                self.toggleShadow(True)
            else:
                event.ignore()
        else:
            event.ignore()
        QGraphicsItem.dragEnterEvent(self, event)

    def dragLeaveEvent(self, event):
        QGraphicsItem.dragLeaveEvent(self, event)
        self.toggleShadow(False)

    def setIconImage(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.iconPath = path
            if self.iconPath:
                self.comm.itemChanged.emit('icon')

    def setLabelText(self, text):
        if bool(text):
            labelBuffer = self.label
            self.label = text
            rect = self.setDefaultLabelRect()
            if rect:
                if question('Extend Item to fit text and icon?'):
                    self.labelRect = rect
                else:
                    self.label = labelBuffer
                    return
            self.matchMinSizeToSubordinate()
            self.comm.itemChanged.emit('label')
        else:
            self.label = ''
            self.labelRect = QRectF()
            self.matchMinSizeToSubordinate()
            self.comm.itemChanged.emit('label')

    def setLabelFont(self, font):
        fontBuffer = self.font
        self.font = font
        rect = self.setDefaultLabelRect()
        if rect:
            if question('Extend Item to fit text and icon?'):
                self.labelRect = rect
            else:
                self.font = fontBuffer
                return
        self.matchMinSizeToSubordinate()
        self.comm.itemChanged.emit('label')

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasFormat(MIME_COLOR_MODIFIER):
            if self.contains(event.pos()):
                colorData = event.mimeData().colorData()
                if self.color != colorData:
                    self.color = colorData
                    self.update()
                    self.comm.itemChanged.emit('color')
        elif mimeData.hasUrls():
            if self.contains(event.pos()):
                path = [ y for y in [ x.toLocalFile() for x in mimeData.urls() ] if os.path.splitext(y)[-1].lower() in ('.jpg', '.png') ]
                if path:
                    self.setIconImage(path[0])
        elif mimeData.hasFormat(MIME_IMAGE_PATH):
            if self.contains(event.pos()):
                self.width, self.height = [ float(x) for x in unicode(mimeData.data(MIME_IMAGE_BUTTONSIZE)).split(',') ]
                path = str(mimeData.data(MIME_IMAGE_PATH)).decode('utf-8')
                rect = QRectF(*[ float(x) for x in unicode(mimeData.data(MIME_IMAGE_RECT)).split(',') ])
                self.setIconImage(path)
                if self.inboundRect().contains(rect):
                    self.iconRect = rect
        elif mimeData.hasFormat(MIME_FONT_FAMILY):
            if self.contains(event.pos()):
                family_id = mimeData.data(MIME_FONT_FAMILY).toInt()[0]
                if family_id < 0:
                    family_id = 0
                family = FONT_FAMILIES[family_id]
                pointSize = mimeData.data(MIME_FONT_SIZE).toInt()[0]
                bold = bool(mimeData.data(MIME_FONT_BOLD).toInt()[0])
                italic = bool(mimeData.data(MIME_FONT_ITALIC).toInt()[0])
                font = QFont(family, pointSize, italic=italic)
                font.setBold(bold)
                self.setLabelFont(font)
        elif mimeData.hasFormat('text/plain') or mimeData.hasFormat(MIME_LABEL) or mimeData.hasFormat(MIME_CUSTOM_LABEL):
            if self.contains(event.pos()):
                if mimeData.hasFormat('text/plain'):
                    try:
                        text = unicode(mimeData.data('text/plain')).strip()
                    except:
                        print ' >> Sorry, non-ascii characters are not supported yet.'
                        return

                elif mimeData.hasFormat(MIME_LABEL):
                    text = unicode(mimeData.data(MIME_LABEL)).strip()
                elif mimeData.hasFormat(MIME_CUSTOM_LABEL):
                    text = unicode(mimeData.data(MIME_CUSTOM_LABEL)).strip()
                self.setLabelText(text)
        elif mimeData.hasFormat(MIME_DRAGCOMBO_TEXT):
            print 'Not support anymore'
        elif mimeData.hasFormat(MIME_COLOR):
            if self.contains(event.pos()):
                self.color = event.mimeData().colorData()
                self.update()
                self.comm.itemChanged.emit('color')
        elif mimeData.hasFormat(MIME_COMMAND):
            if self.contains(event.pos()):
                command = unicode(mimeData.data(MIME_COMMAND)).replace('+', ' ')
                keepObjectName = mimeData.data('ToolDialog/Command-KeepObjectName').toInt()[0]
                script = unicode(mimeData.data('ToolDialog/Command-Script'))
                self.comm.changeMember.emit(self, command, bool(keepObjectName), script)
        self.toggleShadow(False)

    def clearNodeChannleValue(self):
        self.targetNode = []
        self.targetChannel = []
        self.targetValue = []
        self.comm.itemChanged.emit('target')

    def checkSignals(self, prevCommand):
        scene = self.scene()
        if prevCommand == 'Pose':
            self.comm.mousePressed.disconnect()
            self.comm.mouseReleased.disconnect()
            if hasattr(self.comm, 'sliderMousePressed'):
                self.comm.sliderMousePressed.disconnect()
                self.comm.sliderMouseReleased.disconnect()
        if self.command == 'Pose':
            self.comm.mousePressed.connect(lambda : scene.poseGlobalVarSet.emit(self))
            self.comm.mouseReleased.connect(lambda : scene.poseGlobalVarUnset.emit(self))
            if hasattr(self.comm, 'sliderMousePressed'):
                self.comm.sliderMousePressed.connect(lambda : scene.poseGlobalVarSet.emit(self))
                self.comm.sliderMouseReleased.connect(lambda : scene.poseGlobalVarUnset.emit(self))

    def setupItemResize(self, pos, cursorPos):
        self.pressPos = pos
        self.pressRegion = cursorPos
        self.effect.setOuterRadius(0)
        self.effect.setInnerRadius(0)
        self.comm.blockSignals(True)
        if CursorPos.isOneSide(self.pressRegion):
            if CursorPos.isTop(self.pressRegion):
                self.setPos(self.pos() + QPointF(0, self.height))
                self.height *= -1
                self.pressPos += QPointF(0, self.height)
            elif CursorPos.isBottom(self.pressRegion):
                pass
            elif CursorPos.isLeft(self.pressRegion):
                self.setPos(self.pos() + QPointF(self.width, 0))
                self.width *= -1
                self.pressPos += QPointF(self.width, 0)
            elif CursorPos.isRight(self.pressRegion):
                pass
        elif CursorPos.isTopLeft(self.pressRegion):
            self.setPos(self.pos() + QPointF(self.width, self.height))
            self.width *= -1
            self.height *= -1
            self.pressPos += QPointF(self.width, self.height)
        elif CursorPos.isBottomRight(self.pressRegion):
            pass
        elif CursorPos.isTopRight(self.pressRegion):
            self.setPos(self.pos() + QPointF(0, self.height))
            self.height *= -1
            self.pressPos += QPointF(0, self.height)
        elif CursorPos.isBottomLeft(self.pressRegion):
            self.setPos(self.pos() + QPointF(self.width, 0))
            self.width *= -1
            self.pressPos += QPointF(self.width, 0)
        self.comm.blockSignals(False)

    def timeoutCalled(self):
        button = self.timer.button
        modifier = self.timer.modifier
        if self.editable and button == Qt.LeftButton and modifier == Qt.AltModifier | Qt.ShiftModifier:
            self.scene().setMovableSelectedItems(True)
            self.setFlags(self.flags() | QGraphicsItem.ItemIsMovable)
            self.__isMoving = True
            self.setCursor(Qt.ClosedHandCursor)
        elif self.editable and button == Qt.LeftButton and modifier == Qt.AltModifier | Qt.ControlModifier:
            pos = self.timer.pos
            cursorPos = self.checkCursorPosition(pos)
            if cursorPos:
                self.setupItemResize(pos, cursorPos)
                self.resizeToPosition(pos)
        else:
            AbstractDropItem.timeoutCalled(self)

    def restoreItemGeometry(self):
        self.prepareGeometryChange()
        rect = self.sceneBoundingRect().normalized()
        parentItem = self.parentItem()
        self.setPos(parentItem and rect.topLeft() - parentItem.pos() or rect.topLeft())
        self.width = rect.width()
        self.height = rect.height()
        self.comm.itemChanged.emit('size')
        self.pressPos = QPointF()
        self.pressRegion = 0
        self.effect.setOuterRadius(self.BLUR_OUTERRADIUS)
        self.effect.setInnerRadius(self.BLUR_INNERRADIUS)

    def mouseReleaseEvent(self, event):
        if not AbstractDropItem.mouseReleaseEvent(self, event):
            return False
        if self.__isMoving:
            self.scene().setMovableSelectedItems(False)
            self.setFlags(self.flags() & ~QGraphicsItem.ItemIsMovable)
        self.__isMoving = False
        if self.pressRegion:
            self.restoreItemGeometry()
            self.scene()

    def mouseMoveEvent(self, event):
        if not self.editable:
            return
        if self.pressRegion:
            self.resizeToPosition(event.pos())
        else:
            if event.modifiers() == Qt.AltModifier | Qt.ShiftModifier:
                self.__isMoving = True
            AbstractDropItem.mouseMoveEvent(self, event)

    def resizeToPosition(self, pos):
        self.prepareGeometryChange()
        offset = pos - self.pressPos
        XaxisSign = YaxisSign = 0
        if CursorPos.isOneSide(self.pressRegion):
            if CursorPos.isTop(self.pressRegion):
                YaxisSign = 1
            elif CursorPos.isBottom(self.pressRegion):
                YaxisSign = 1
            elif CursorPos.isLeft(self.pressRegion):
                XaxisSign = 1
            else:
                XaxisSign = 1
        else:
            XaxisSign = 1
            YaxisSign = 1
        newWidth = self.width + XaxisSign * offset.x()
        if abs(newWidth) < self.minWidth:
            newWidth = self.width
        newHeight = self.height + YaxisSign * offset.y()
        if abs(newHeight) < self.minHeight:
            newHeight = self.height
        deltaWidth = newWidth - self.width
        deltaHeight = newHeight - self.height
        self.adjustSize(deltaWidth, deltaHeight)
        if CursorPos.isTop(self.pressRegion):
            deltaHeight *= -1
        if CursorPos.isLeft(self.pressRegion):
            deltaWidth *= -1
        self.keepIconIn(deltaWidth, deltaHeight)
        self.keepLabelIn(deltaWidth, deltaHeight)
        self.pressPos = pos
        self.update()

    def adjustSize(self, dw, dh):
        self.prepareGeometryChange()
        self.width += dw
        self.height += dh
        self.comm.itemChanged.emit('size')

    def hoverEnterEvent(self, event):
        if self.editable:
            modifier = event.modifiers()
            if modifier == Qt.AltModifier | Qt.ControlModifier:
                cursorPos = self.checkCursorPosition(event.pos())
                self.changeSizeCursor(cursorPos)
            elif modifier == Qt.AltModifier | Qt.ShiftModifier:
                self.setCursor(Qt.OpenHandCursor)
        AbstractDropItem.hoverEnterEvent(self, event)

    def hoverMoveEvent(self, event):
        if self.editable:
            modifier = event.modifiers()
            if modifier == Qt.AltModifier | Qt.ControlModifier:
                cursorPos = self.checkCursorPosition(event.pos())
                self.changeSizeCursor(cursorPos)
            elif modifier == Qt.AltModifier | Qt.ShiftModifier:
                self.setCursor(Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        if self.editable:
            self.changeSizeCursor(0)
        AbstractDropItem.hoverLeaveEvent(self, event)

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        if self.editable:
            if modifiers == Qt.AltModifier | Qt.ControlModifier:
                itemPos = self.mapFromGlobal()
                cursorPos = self.checkCursorPosition(itemPos)
                self.changeSizeCursor(cursorPos)
            elif modifiers == Qt.AltModifier | Qt.ShiftModifier:
                self.setCursor(Qt.OpenHandCursor)
            else:
                if self.__labelMoveHandle:
                    self.keyLabelMove(key)
                if self.__iconTopHandle:
                    self.keyIconMove(key, modifiers)
        AbstractDropItem.keyPressEvent(self, event)

    def keyLabelMove(self, key):
        self.prepareGeometryChange()
        if key == Qt.Key_Up:
            self.moveLabelRect(QPointF(0, -1))
        elif key == Qt.Key_Down:
            self.moveLabelRect(QPointF(0, 1))
        elif key == Qt.Key_Left:
            self.moveLabelRect(QPointF(-1, 0))
        elif key == Qt.Key_Right:
            self.moveLabelRect(QPointF(1, 0))

    def keyIconMove(self, key, modifiers):
        pass

    def mapFromGlobal(self):
        globalPos = QCursor.pos()
        view = self.scene().primaryView()
        viewPos = view.mapFromGlobal(globalPos)
        scenePos = view.mapToScene(viewPos)
        itemPos = self.mapFromScene(scenePos)
        return itemPos

    def keyReleaseEvent(self, event):
        if self.cursor().shape() != Qt.ArrowCursor:
            self.changeSizeCursor(0)
        AbstractDropItem.keyReleaseEvent(self, event)

    def sceneEventFilter(self, watched, event):
        if watched in [self.__iconLeftHandle,
         self.__iconTopHandle,
         self.__iconRightHandle,
         self.__iconBottomHandle,
         self.__iconCenterHandle]:
            if event.type() == QEvent.GraphicsSceneMousePress:
                watched.mousePos = event.pos()
            elif event.type() == QEvent.GraphicsSceneMouseRelease:
                self.matchMinSizeToSubordinate()
            elif event.type() == QEvent.GraphicsSceneMouseMove:
                offset = event.pos() - watched.mousePos
                self.chageIconRect(watched, offset)
                self.scene().isHandleWorking = True
            else:
                return False
            return True
        elif watched == self.__labelMoveHandle:
            if event.type() == QEvent.GraphicsSceneMousePress:
                watched.mousePos = event.pos()
            elif event.type() == QEvent.GraphicsSceneMouseRelease:
                self.matchMinSizeToSubordinate()
            elif event.type() == QEvent.GraphicsSceneMouseMove:
                offset = event.pos() - watched.mousePos
                self.moveLabelRect(offset)
                self.scene().isHandleWorking = True
            else:
                return False
            return True
        else:
            return QGraphicsItem.sceneEventFilter(self, watched, event)

    def checkCursorPosition(self, pos):
        x, y = pos.x(), pos.y()
        rect = self.boundingRect()
        width, height = rect.width(), rect.height()
        result = 0
        if x >= 0 and x <= self.EDITABLE_MARGIN:
            result |= CursorPos.LEFT
        elif x >= width - self.EDITABLE_MARGIN and x <= width:
            result |= CursorPos.RIGHT
        if y >= 0 and y <= self.EDITABLE_MARGIN:
            result |= CursorPos.TOP
        elif y >= height - self.EDITABLE_MARGIN and y <= height:
            result |= CursorPos.BOTTOM
        return result

    def changeSizeCursor(self, cursorPos):
        if cursorPos:
            if CursorPos.isOneSide(cursorPos):
                if CursorPos.isTop(cursorPos) or CursorPos.isBottom(cursorPos):
                    self.setCursor(Qt.SizeVerCursor)
                else:
                    self.setCursor(Qt.SizeHorCursor)
            elif CursorPos.isTopLeft(cursorPos) or CursorPos.isBottomRight(cursorPos):
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.SizeBDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def contextMenuEvent(self, event):
        menu = self.createCustomContextMenu(event)
        if menu:
            menu.exec_(event.screenPos())

    def createCustomContextMenu(self, event):
        menu = QMenu()
        self.createDefaultPopupMenu(menu)
        return menu

    def createDefaultPopupMenu(self, menu):
        AbstractDropItem.createDefaultPopupMenu(self, menu)
        if self.editable:
            redefineMembersAct = menu.addAction('Redefine Members')
            redefineMembersAct.triggered.connect(lambda : self.comm.redefineMember.emit(self))
            editOnRemoteAct = menu.addAction('Edit this button')
            editOnRemoteAct.triggered.connect(lambda : self.comm.editRemote.emit(self))
            linkItemsAct = menu.addAction('Link Items')
            linkItemsAct.triggered.connect(self.linkSelectedItems)

    def createIconPopupMenu(self, menu):
        menu.addSeparator()
        act = menu.addAction('ICON')
        act.setDisabled(True)
        self.addMoveMenu(menu, 'icon')

    def addMoveMenu(self, menu, TYPE):
        moveMenu = menu.addMenu('Move')
        moveLeftAct = moveMenu.addAction('To Left')
        moveLeftAct.triggered.connect(lambda : self.moveBelongingTo('left', TYPE))
        moveHCenterAct = moveMenu.addAction('To HCenter')
        moveHCenterAct.triggered.connect(lambda : self.moveBelongingTo('hcenter', TYPE))
        moveRightAct = moveMenu.addAction('To Right')
        moveRightAct.triggered.connect(lambda : self.moveBelongingTo('right', TYPE))
        moveTopAct = moveMenu.addAction('To Top')
        moveTopAct.triggered.connect(lambda : self.moveBelongingTo('top', TYPE))
        moveVCenterAct = moveMenu.addAction('To VCenter')
        moveVCenterAct.triggered.connect(lambda : self.moveBelongingTo('vcenter', TYPE))
        moveBottomAct = moveMenu.addAction('To Bottom')
        moveBottomAct.triggered.connect(lambda : self.moveBelongingTo('bottom', TYPE))

    def createLabelPopupMenu(self, menu):
        menu.addSeparator()
        act = menu.addAction('LABEL')
        act.setDisabled(True)
        fontMenu = menu.addMenu('Font')
        boldAct = fontMenu.addAction('Bold')
        boldAct.setCheckable(True)
        boldAct.setChecked(self.font.bold())
        boldAct.triggered[bool].connect(self.setFontBold)
        italicAct = fontMenu.addAction('Italic')
        italicAct.setCheckable(True)
        italicAct.setChecked(self.font.italic())
        italicAct.triggered[bool].connect(self.setFontItalic)
        self.addMoveMenu(menu, 'label')

    def setFontBold(self, bold):
        self.font.setBold(bold)
        self.comm.itemChanged.emit('label')

    def setFontItalic(self, italic):
        self.font.setItalic(italic)
        self.comm.itemChanged.emit('label')

    def toggleIconHandles(self):
        if self.__iconTopHandle:
            self.removeIconHandle()
        elif self.iconRect.isValid():
            self.addIconHandle()
            self.repositionIconHandles()

    def addIconHandle(self):
        self.__iconTopHandle = SizeMoveHandle(8, 8, Qt.Vertical, self)
        self.__iconBottomHandle = SizeMoveHandle(8, 8, Qt.Vertical, self)
        self.__iconLeftHandle = SizeMoveHandle(8, 8, Qt.Horizontal, self)
        self.__iconRightHandle = SizeMoveHandle(8, 8, Qt.Horizontal, self)
        self.__iconCenterHandle = SizeMoveHandle(12, 12, Qt.Horizontal | Qt.Vertical, self)
        self.__iconTopHandle.installSceneEventFilter(self)
        self.__iconBottomHandle.installSceneEventFilter(self)
        self.__iconLeftHandle.installSceneEventFilter(self)
        self.__iconRightHandle.installSceneEventFilter(self)
        self.__iconCenterHandle.installSceneEventFilter(self)

    def repositionIconHandles(self):
        rect = self.iconRect
        center = rect.center()
        self.__iconTopHandle.setPos(center.x(), rect.top())
        self.__iconBottomHandle.setPos(center.x(), rect.bottom())
        self.__iconLeftHandle.setPos(rect.left(), center.y())
        self.__iconRightHandle.setPos(rect.right(), center.y())
        self.__iconCenterHandle.setPos(center)

    def removeIconHandle(self):
        scene = self.scene()
        if self.__iconTopHandle:
            scene.removeItem(self.__iconTopHandle)
            self.__iconTopHandle = None
        if self.__iconBottomHandle:
            scene.removeItem(self.__iconBottomHandle)
            self.__iconBottomHandle = None
        if self.__iconLeftHandle:
            scene.removeItem(self.__iconLeftHandle)
            self.__iconLeftHandle = None
        if self.__iconRightHandle:
            scene.removeItem(self.__iconRightHandle)
            self.__iconRightHandle = None
        if self.__iconCenterHandle:
            scene.removeItem(self.__iconCenterHandle)
            self.__iconCenterHandle = None
        return

    def chageIconRect(self, handle, offset):
        self.prepareGeometryChange()
        inboundRect = self.inboundRect()
        if handle == self.__iconTopHandle:
            moved = -offset.y()
            rect = self.iconRect
            newHeight = max(rect.height() + moved, self.ICON_MINSIZE)
            delta = newHeight - rect.height()
            if self.iconRect.top() - delta > inboundRect.top():
                self.iconRect.adjust(0, 0, 0, delta)
                top = self.iconRect.top() - delta
                self.iconRect.moveTop(top)
        elif handle == self.__iconBottomHandle:
            moved = offset.y()
            rect = self.iconRect
            newHeight = max(rect.height() + moved, self.ICON_MINSIZE)
            delta = newHeight - rect.height()
            if self.iconRect.bottom() + delta < inboundRect.bottom():
                self.iconRect.adjust(0, 0, 0, delta)
        elif handle == self.__iconLeftHandle:
            moved = -offset.x()
            rect = self.iconRect
            newWidth = max(rect.width() + moved, self.ICON_MINSIZE)
            delta = newWidth - rect.width()
            if self.iconRect.left() - delta > inboundRect.left():
                self.iconRect.adjust(0, 0, delta, 0)
                left = self.iconRect.left() - delta
                self.iconRect.moveLeft(left)
        elif handle == self.__iconRightHandle:
            moved = offset.x()
            rect = self.iconRect
            newWidth = max(rect.width() + moved, self.ICON_MINSIZE)
            delta = newWidth - rect.width()
            if self.iconRect.right() + delta < inboundRect.right():
                self.iconRect.adjust(0, 0, delta, 0)
        elif handle == self.__iconCenterHandle:
            x, y = offset.x(), offset.y()
            if self.iconRect.left() + x < inboundRect.left():
                x = 0
            elif self.iconRect.right() + x > inboundRect.right():
                x = 0
            if self.iconRect.top() + y < inboundRect.top():
                y = 0
            elif self.iconRect.bottom() + y > inboundRect.bottom():
                y = 0
            self.iconRect.translate(x, y)
        self.repositionIconHandles()
        self.update()
        self.comm.itemChanged.emit('icon')

    def keepIconIn(self, dw, dh):
        if self.iconRect.isValid():
            self.prepareGeometryChange()
            if dh < 0:
                if self.iconRect.bottom() + self.BORDER_MARGIN > abs(self.height):
                    self.iconRect.translate(0, dh)
            if dw < 0:
                if self.iconRect.right() + self.BORDER_MARGIN > abs(self.width):
                    self.iconRect.translate(dw, 0)

    def moveBelongingTo(self, to, belonging = ''):
        if belonging == 'icon':
            rect = self.iconRect
        elif belonging == 'label':
            rect = self.labelRect
        else:
            return
        self.prepareGeometryChange()
        if to == 'left':
            rect.moveLeft(self.BORDER_MARGIN)
        elif to == 'hcenter':
            centerY = rect.center().y()
            rect.moveCenter(QPointF(self.width / 2, centerY))
        elif to == 'right':
            rect.moveRight(self.width - self.BORDER_MARGIN)
        elif to == 'top':
            rect.moveTop(self.BORDER_MARGIN)
        elif to == 'vcenter':
            centerX = rect.center().x()
            rect.moveCenter(QPointF(centerX, self.height / 2))
        elif to == 'bottom':
            rect.moveBottom(self.height - self.BORDER_MARGIN)
        self.comm.itemChanged.emit(belonging)
        self.update()

    def toggleLabelHandles(self):
        if self.__labelMoveHandle:
            self.removeLabelHandle()
        elif self.labelRect.isValid():
            self.addLabelHandle()
            self.repositionLabelHandle()
            self.update()

    def addLabelHandle(self):
        self.__labelMoveHandle = SizeMoveHandle(12, 12, Qt.Horizontal | Qt.Vertical, self)
        self.__labelMoveHandle.installSceneEventFilter(self)

    def repositionLabelHandle(self):
        rect = self.labelRect
        self.__labelMoveHandle.setPos(rect.topLeft())

    def removeLabelHandle(self):
        scene = self.scene()
        if self.__labelMoveHandle:
            scene.removeItem(self.__labelMoveHandle)
            self.__labelMoveHandle = None
        return

    def moveLabelRect(self, offset):
        x, y = offset.x(), offset.y()
        inboundRect = self.inboundRect()
        if self.labelRect.left() + x < inboundRect.left():
            x = 0
        elif self.labelRect.right() + x > inboundRect.right():
            x = 0
        if self.labelRect.top() + y < inboundRect.top():
            y = 0
        elif self.labelRect.bottom() + y > inboundRect.bottom():
            y = 0
        self.labelRect.translate(x, y)
        self.repositionLabelHandle()
        self.update()
        self.comm.itemChanged.emit('label')

    def keepLabelIn(self, dw, dh):
        if self.labelRect.isValid():
            if dh < 0:
                if self.labelRect.bottom() + self.BORDER_MARGIN > abs(self.height):
                    self.labelRect.translate(0, dh)
            if dw < 0:
                if self.labelRect.right() + self.BORDER_MARGIN > abs(self.width):
                    self.labelRect.translate(dw, 0)

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
                if k == 'linkedItems':
                    continue
                if k == 'iconPath':
                    prev_iconRect = item.iconRect
                setattr(item, k, copy(v))
                if k == 'iconPath' and not prev_iconRect.isEmpty():
                    item.iconRect = prev_iconRect
            except AttributeError:
                print ">> Can't set [%s]" % k

        item.hashcode = generateHashcode(item)
        return item

    def getSortedCollingItems(self):

        def getAllCollidingItems(item, data = None):
            if data is None:
                data = []
            colliding = item.collidingItems(Qt.IntersectsItemShape)
            newOne = list(set(colliding) - set(data))
            data.extend(newOne)
            for n in newOne:
                getAllCollidingItems(n, data)

            return

        items = []
        getAllCollidingItems(self, items)
        items.sort(key=lambda x: x.zValue())
        return items

    def bringToFront(self):
        scene = self.scene()
        items = scene.getItemsByZValueOrder()
        if items:
            zValue = items[-1].zValue() + 0.001
            self.setZValue(zValue)

    def sendToBack(self):
        scene = self.scene()
        items = scene.getItemsByZValueOrder()
        if items:
            zValue = items[0].zValue() - 0.001
            self.setZValue(zValue)

    def bringForward(self):
        items = self.getSortedCollingItems()
        if self not in items:
            return
        index = items.index(self)
        if index >= len(items) - 1:
            return
        swapItem = items[index + 1]
        zValue1 = self.zValue()
        zValue2 = swapItem.zValue()
        self.setZValue(zValue2)
        swapItem.setZValue(zValue1)

    def sendBackward(self):
        items = self.getSortedCollingItems()
        if self not in items:
            return
        index = items.index(self)
        if index == 0:
            return
        swapItem = items[index - 1]
        zValue1 = self.zValue()
        zValue2 = swapItem.zValue()
        self.setZValue(zValue2)
        swapItem.setZValue(zValue1)


class RectangleDropItem(AbstractDropItem):

    def paint(self, painter, option, widget = None):
        AbstractDropItem.paint(self, painter, option, widget)
        rect = self.boundingRect().normalized()
        painter.drawRect(rect)
        if self.icon:
            painter.setPen(Qt.NoPen)
            iconRect = self.iconRect.translated(rect.topLeft())
            sourceRect = QRectF(self.icon.rect())
            painter.drawPixmap(iconRect, self.icon, sourceRect)
        if self.label:
            labelRect = self.labelRect.translated(rect.topLeft())
            painter.setFont(self.font)
            painter.setPen(self.fontColor)
            painter.drawText(labelRect, Qt.AlignHCenter | Qt.AlignBottom | Qt.TextWordWrap, self.label)

    def type(self):
        from const import DropItemType
        return DropItemType.Rectangle

    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path


class RectangleEditableDropItem(RectangleDropItem, AbstractEditableDropItem):

    def paint(self, painter, option, widget = None):
        RectangleDropItem.paint(self, painter, option, widget)
        if self.labelMoveHandle:
            painter.setPen(QPen(Qt.black, 0.5, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.labelRect.adjusted(-2, -2, 2, 2))

    def type(self):
        from const import DropItemType
        return DropItemType.EditableRectangle


class DragPoseDropItem(RectangleDropItem):
    FONT = QFont('OpenSans', 12, 100)

    def __init__(self, color = QColor(), width = 40, height = 40, parent = None):
        RectangleDropItem.__init__(self, color, width, height, parent)
        self.startPos = QPointF()
        self.start = False
        self.poseVal = 0.0

    def type(self):
        from const import DropItemType
        return DropItemType.DragPose

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton and (event.modifiers() == Qt.NoModifier or event.modifiers() == Qt.ShiftModifier):
            self.startPos = event.pos()
            self.start = True
            self.comm.mousePressed.emit()
            self.setFocus()
        else:
            RectangleDropItem.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        RectangleDropItem.mouseMoveEvent(self, event)
        if self.start:
            offset = event.pos() - self.startPos
            self.poseVal = offset.x()
            if event.modifiers() == Qt.ShiftModifier:
                self.poseVal = int(self.poseVal) / 10 * 10
            self.comm.sendCommandData.emit(self.command, self.targetNode, self.targetChannel, self.targetValue, unicode(self.poseVal / 100.0))
            self.update()
            self.setFocus()

    def mouseReleaseEvent(self, event):
        if self.start:
            self.start = False
            self.startPos = QPointF()
            self.poseVal = 0.0
            self.comm.mouseReleased.emit()
            self.clearFocus()
        else:
            RectangleDropItem.mouseReleaseEvent(self, event)

    def paint(self, painter, option, widget = None):
        RectangleDropItem.paint(self, painter, option, widget)
        if self.start:
            rect = self.boundingRect()
            text = '%d%%' % self.poseVal
            fm = QFontMetricsF(self.FONT)
            baseRect = fm.boundingRect(text).adjusted(-4, -2, 4, 2)
            baseRect.moveCenter(rect.center())
            painter.save()
            painter.setPen(Qt.NoPen)
            if self.poseVal >= 0 and self.poseVal <= 100:
                painter.setBrush(QColor.fromHsvF(0.333, self.poseVal / 100.0, 0.9, 0.5))
            elif self.poseVal > 0:
                painter.setBrush(QColor.fromRgbF(0.9 * min(self.poseVal - 100, 100) / 100.0, 0.9, 0, 0.5))
            else:
                painter.setBrush(QColor.fromRgbF(0.9, 1 - 0.9 * max(self.poseVal, -100) / -100.0, 1 - 0.9 * max(self.poseVal, -100) / -100.0, 0.5))
            painter.drawRoundedRect(baseRect, 6.0, 6.0)
            painter.restore()
            painter.setFont(self.FONT)
            painter.setPen(Qt.black)
            painter.drawText(rect, Qt.AlignCenter, text)


class DragPoseEditableDropItem(RectangleEditableDropItem, DragPoseDropItem):

    def __init__(self, color = QColor(), width = 40, height = 40, parent = None):
        RectangleEditableDropItem.__init__(self, color, width, height, parent)
        self.startPos = QPointF()
        self.start = False
        self.poseVal = 0.0

    def type(self):
        from const import DropItemType
        return DropItemType.EditableDragPose

    def paint(self, painter, option, widget = None):
        DragPoseDropItem.paint(self, painter, option, widget)
        if self.labelMoveHandle:
            painter.setPen(QPen(Qt.black, 0.5, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.labelRect.adjusted(-2, -2, 2, 2))

    def mouseMoveEvent(self, event):
        if self.pressRegion:
            RectangleEditableDropItem.mouseMoveEvent(self, event)
        else:
            DragPoseDropItem.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.pressRegion:
            RectangleEditableDropItem.mouseReleaseEvent(self, event)
        else:
            DragPoseDropItem.mouseReleaseEvent(self, event)


class LineItem(QGraphicsItem):

    def __init__(self, source, dest, parent = None, scene = None):
        super(LineItem, self).__init__(parent)
        if scene:
            scene.addItem(self)
        self.__lineColor = Qt.black
        self.setFlags(QGraphicsItem.ItemClipsChildrenToShape)
        self.srcItem = self.destItem = None
        self.srcPnt = QPointF()
        self.destPnt = QPointF()
        if isinstance(source, AbstractDropItem):
            self.setSrcItem(source)
        elif isinstance(source, QPointF):
            self.setP1(source)
        if isinstance(dest, AbstractDropItem):
            self.setDestItem(dest)
        elif isinstance(dest, QPointF):
            self.setP2(dest)
        return

    def setLineColor(self, color):
        self.__lineColor = color
        self.update()

    def setP1(self, pnt):
        self.srcPnt = pnt

    def setP2(self, pnt):
        self.destPnt = pnt

    def setSrcItem(self, item):
        self.srcItem = item
        self.setP1(self.srcItem.sceneBoundingRect().center())

    def setDestItem(self, item):
        self.destItem = item
        self.setP2(self.destItem.sceneBoundingRect().center())

    def paint(self, painter, option, widget = None):
        painter.setRenderHints(QPainter.Antialiasing)
        if self.srcItem:
            self.srcPnt = self.srcItem.sceneBoundingRect().center()
        if self.destItem:
            self.destPnt = self.destItem.sceneBoundingRect().center()
        pen = QPen(self.__lineColor, 1.0)
        pen.setStyle(Qt.SolidLine)
        line = QLineF(self.srcPnt, self.destPnt)
        srcFound = False
        destFound = False
        if self.srcItem:
            path = self.srcItem.shape()
            path = path.simplified()
            poly = path.toFillPolygon()
            p1 = poly.first() + self.srcItem.pos()
            intersectPoint = QPointF()
            for i in poly:
                p2 = i + self.srcItem.pos()
                polyLine = QLineF(p1, p2)
                intersectType, intersectPoint = polyLine.intersect(line)
                if intersectType == QLineF.BoundedIntersection:
                    srcFound = True
                    break
                p1 = p2

            pnt1 = intersectPoint
        if self.destItem:
            path = self.destItem.shape()
            path = path.simplified()
            poly = path.toFillPolygon()
            p1 = poly.first() + self.destItem.pos()
            intersectPoint = QPointF()
            for i in poly:
                p2 = i + self.destItem.pos()
                polyLine = QLineF(p1, p2)
                intersectType, intersectPoint = polyLine.intersect(line)
                if intersectType == QLineF.BoundedIntersection:
                    destFound = True
                    break
                p1 = p2

            pnt2 = intersectPoint
        if srcFound:
            line.setP1(pnt1)
        if destFound:
            line.setP2(pnt2)
        if not line.isNull():
            painter.setPen(pen)
            painter.setBrush(self.__lineColor)
            painter.drawLine(line)
            angle = line.angle()
            cnt = line.pointAt(0.5)
            polygon = QPolygonF()
            l = QLineF(0, 0, 0, 3)
            l.setAngle(angle)
            polygon.append(cnt + l.p2())
            l.setAngle(angle + 120)
            polygon.append(cnt + l.p2())
            l.setAngle(angle - 120)
            polygon.append(cnt + l.p2())
            painter.drawPolygon(polygon)

    def type(self):
        from const import DropItemType
        return DropItemType.Line

    def boundingRect(self):
        return QRectF(self.srcPnt, self.destPnt).normalized()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    item = RectangleDropItem()
    for value in dir(item):
        print value

    sys.exit(app.exec_())