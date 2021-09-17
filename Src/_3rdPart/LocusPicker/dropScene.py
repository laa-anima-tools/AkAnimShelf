# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\dropScene.py
try:
    from PySide2.QtCore import Qt, Signal, QPointF, QRectF, QByteArray, QSizeF, QSize
    from PySide2.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QFontMetrics, QTransform, QPolygonF, QKeySequence
    from PySide2.QtWidgets import QGraphicsScene, QToolTip, QGraphicsItem
except:
    from PySide.QtCore import Qt, Signal, QPointF, QRectF, QByteArray, QSizeF, QSize
    from PySide.QtGui import QGraphicsScene, QPainter, QToolTip, QPen, QBrush, QColor, QPixmap, QFontMetrics, QGraphicsItem, QTransform, QPolygonF, QKeySequence

from decorator import accepts, returns, timestamp
from dropItem import AbstractDropItem, RectangleDropItem, DragPoseDropItem, LineItem, getLinkedItems, RectangleEditableDropItem, DragPoseEditableDropItem
from dropSliderItem import Attachment, RectangleDropSliderItem, RectangleEditableDropSliderItem
from dropPathItem import PathDropItem, PathEditableDropItem
from visToggleItem import VisToggleItem, VisToggleEditableItem, ToggleState
from groupItem import GroupItem, EditableGroupItem
from const import getType, DropItemType, DEF_MAPBGCOLOR, MIME_TEMPLATE, MIME_TEMPLATE_SIZE, MIME_COLOR_MODIFIER, MIME_NEWBUTTON, MIME_COLOR, MIME_DRAGCOMBO_TEXT, MIME_COMMAND, MIME_LABEL, MIME_FONT_FAMILY, MIME_CUSTOM_LABEL, MIME_SLIDER_COMMAND, MIME_SLIDER_WIDTH, MIME_SLIDER_HEIGHT, MIME_SLIDER_ATTACH, MIME_SLIDER_INVERSE, MIME_SLIDER_CHANGETOOL, MIME_SLIDER_ATTRIBUTE, MIME_SLIDER_BUTTONNUMBER, MIME_IMAGE_PATH, warn, confirm, question, affixPrefix, generateHashcode
from editHandle import AbstractHandle
from copy import copy
import os, time

class DropScene(QGraphicsScene):
    sendCommandData = Signal(unicode, list, list, list, unicode, QGraphicsScene)
    redefineMember = Signal(AbstractDropItem)
    changeMember = Signal(AbstractDropItem, unicode, bool, unicode)
    editRemote = Signal(AbstractDropItem)
    sceneChanged = Signal()
    undoOpen = Signal()
    undoClose = Signal()
    poseGlobalVarSet = Signal(AbstractDropItem)
    poseGlobalVarUnset = Signal(AbstractDropItem)

    def __init__(self, parent = None):
        super(DropScene, self).__init__(parent)
        self.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.__pressPos = QPointF()
        self.__moveMarqueePos = QPointF()
        self.__moveMarqueeOffset = QPointF()
        self.__marqueeRect = QRectF()
        self.__marqueeModifier = Qt.NoModifier
        self.marquee = None
        self.imagePath = ''
        self.__mapSize = QSize(0, 0)
        self.__pixmap = QPixmap()
        self.__color = DEF_MAPBGCOLOR
        self.__useBGimage = False
        self.__coop = False
        self.isHandleWorking = False
        return

    @property
    def mapSize(self):
        return self.__mapSize

    @mapSize.setter
    def mapSize(self, size):
        self.__mapSize = size
        self.update()

    @property
    @returns(QColor)
    def color(self):
        return self.__color

    @color.setter
    @accepts(QColor)
    def color(self, color):
        self.__color = color
        self.update()

    @property
    @returns(QPixmap)
    def pixmap(self):
        return self.__pixmap

    @pixmap.setter
    @accepts(QPixmap)
    def pixmap(self, pixmap):
        self.__pixmap = pixmap

    @property
    @returns(bool)
    def coop(self):
        return self.__coop

    @coop.setter
    @accepts(bool)
    def coop(self, coop):
        self.__coop = coop

    @property
    @returns(bool)
    def useBGimage(self):
        return self.__useBGimage

    @useBGimage.setter
    @accepts(bool)
    def useBGimage(self, use):
        self.__useBGimage = use
        self.update()

    def primaryView(self):
        views = self.views()
        if views:
            return views[0]

    def window(self):
        view = self.primaryView()
        if view:
            return view.window()
        else:
            return ''

    def drawBackground(self, painter, rect):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(rect, self.__color)
        painter.setPen(QPen(Qt.black, 0.5, Qt.DashLine))
        painter.drawRect(QRectF(QPointF(0, 0), self.__mapSize))
        if self.__useBGimage and not self.__pixmap.isNull():
            painter.drawPixmap(QPointF(0, 0), self.__pixmap)
        if self.__coop:
            mapRect = QRectF(QPointF(0, 0), self.__mapSize)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(67, 255, 163))
            painter.drawPolygon(self.getCornerPolygon(mapRect.topLeft(), 0))
            painter.drawPolygon(self.getCornerPolygon(mapRect.topRight(), 1))
            painter.drawPolygon(self.getCornerPolygon(mapRect.bottomRight(), 2))
            painter.drawPolygon(self.getCornerPolygon(mapRect.bottomLeft(), 3))

    def getCornerPolygon(self, pos, coord = 0):
        if coord == 0:
            p1 = pos + QPointF(9, 0)
            p2 = p1 + QPointF(0, 3)
            p3 = p2 - QPointF(6, 0)
            p4 = p3 + QPointF(0, 6)
            p5 = p4 - QPointF(3, 0)
        elif coord == 1:
            p1 = pos + QPointF(0, 9)
            p2 = p1 - QPointF(3, 0)
            p3 = p2 - QPointF(0, 6)
            p4 = p3 - QPointF(6, 0)
            p5 = p4 - QPointF(0, 3)
        elif coord == 2:
            p1 = pos - QPointF(9, 0)
            p2 = p1 - QPointF(0, 3)
            p3 = p2 + QPointF(6, 0)
            p4 = p3 - QPointF(0, 6)
            p5 = p4 + QPointF(3, 0)
        else:
            p1 = pos - QPointF(0, 9)
            p2 = p1 + QPointF(3, 0)
            p3 = p2 + QPointF(0, 6)
            p4 = p3 + QPointF(6, 0)
            p5 = p4 + QPointF(0, 3)
        return QPolygonF.fromList([pos,
         p1,
         p2,
         p3,
         p4,
         p5])

    def enlargeUptoUnited(self, pos, rect):
        sceneRect = self.sceneRect()
        if not sceneRect.contains(rect):
            view = self.primaryView()
            answer = confirm('Items do not fit in current map size\nDo you want to expand window?', 'Expand Window', parent=view)
            if answer == -1:
                return pos
            if answer == 0:
                return None
            united = sceneRect.united(rect)
            widthDelta = united.width() - sceneRect.width()
            if widthDelta == int(widthDelta):
                widthDelta = int(widthDelta)
            else:
                widthDelta = int(widthDelta) + 1
            heightDelta = united.height() - sceneRect.height()
            if heightDelta == int(heightDelta):
                heightDelta = int(heightDelta)
            else:
                heightDelta = int(heightDelta) + 1
            window = view.window()
            window.resize(window.size() + QSize(widthDelta, heightDelta))
        return pos

    def setBackgroundPixmap(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.imagePath = path
            self.pixmap = pixmap
        else:
            self.imagePath = ''
            self.pixmap = QPixmap()
        self.useBGimage = True

    def helpEvent(self, event):
        pos = event.scenePos()
        item = self.itemAt(pos, QTransform())
        if item and isinstance(item, AbstractDropItem):
            cmd = item.command
            if cmd.startswith('EXEC'):
                splited = cmd.split(' ', 1)
                toolTipText = '<b>%s</b>' % splited[0]
                toolTipText += '<br>%s' % splited[1]
            elif cmd.startswith('Visibility'):
                toolTipText = '<b>%s</b>' % cmd
                toolTipText += '<br>%s' % item.states[item.getCurrentIndex()].name
            else:
                toolTipText = '<b>%s</b>' % cmd
                if item.targetNode:
                    toolTipText += '<br>' + item.targetNode[0] + (item.targetNode[1:] and '...' or '')
                if item.targetChannel:
                    toolTipText += '<br>%s' % self.elideText(', '.join(item.targetChannel), 120)
                if item.linkedItems:
                    toolTipText += '<br><font color=#ff0000>Has linked items</font>'
            QToolTip.showText(event.screenPos(), toolTipText)
        else:
            QToolTip.hideText()

    def elideText(self, text, width):
        fontMetrics = QFontMetrics(self.font())
        return fontMetrics.elidedText(text, Qt.ElideRight, width)

    def mousePressEvent(self, event):
        items = [ x for x in self.items(event.scenePos()) if isinstance(x, AbstractDropItem) ]
        if items:
            item = items[0]
        else:
            item = None
        selectedItems = []
        button = event.button()
        modifier = event.modifiers()
        if button != Qt.LeftButton and button != Qt.MiddleButton:
            return
        else:
            if button == Qt.LeftButton and (modifier == Qt.NoModifier or modifier == Qt.ShiftModifier or modifier == Qt.ControlModifier or modifier == Qt.ControlModifier | Qt.ShiftModifier):
                if hasattr(item, 'isInSliderRect') and item.isInSliderRect(item.mapFromScene(event.scenePos())):
                    QGraphicsScene.mousePressEvent(self, event)
                    return
                editHandle = [ x for x in self.items(event.scenePos()) if isinstance(x, AbstractHandle) ]
                if editHandle:
                    QGraphicsScene.mousePressEvent(self, event)
                    return
                selectedItems = [ x for x in list(set(self.selectedItems()) - set([item])) if isinstance(x, AbstractDropItem) ]
                for x in selectedItems:
                    x.setIgnore(True)

                self.__pressPos = event.scenePos()
                self.__marqueeModifier = modifier
            QGraphicsScene.mousePressEvent(self, event)
            for x in selectedItems:
                x.setSelected(True)
                x.setIgnore(False)

            return

    def mouseReleaseEvent(self, event):
        rect = QRectF()
        items = [ x for x in self.items(event.scenePos()) if isinstance(x, AbstractDropItem) ]
        if items:
            item = items[0]
        else:
            item = None
        modifier = event.modifiers()
        if not self.__marqueeRect.isNull():
            rect = self.__marqueeRect.normalized()
            self.__marqueeRect = QRectF()
            if self.__marqueeModifier == Qt.NoModifier:
                mode = 'replace'
            elif self.__marqueeModifier == Qt.ControlModifier:
                mode = 'remove'
            elif self.__marqueeModifier == Qt.ShiftModifier:
                mode = 'toggle'
            elif self.__marqueeModifier == Qt.ControlModifier | Qt.ShiftModifier:
                mode = 'add'
            else:
                mode = ''
            if mode:
                self.selectInRect(rect, mode)
            self.primaryView().hideRubberBand()
        elif not item and modifier == Qt.NoModifier and not self.isHandleWorking:
            self.clearSelection()
            self.sendCommandData.emit('Deselect', [None], [], [], 'No', self)
        self.__pressPos = QPointF()
        self.__moveMarqueePos = QPointF()
        self.__moveMarqueeOffset = QPointF()
        self.__marqueeModifier = Qt.NoModifier
        self.isHandleWorking = False
        if modifier == Qt.ShiftModifier:
            selectedItems = list(set(self.selectedItems()) - set([item]))
            for x in selectedItems:
                x.setIgnore(True)

        QGraphicsScene.mouseReleaseEvent(self, event)
        if modifier == Qt.ShiftModifier:
            for x in selectedItems:
                x.setSelected(True)
                x.setIgnore(False)

        return

    @staticmethod
    def floatDiv(a, b):
        if b > 0:
            return a / b
        else:
            return 0

    def mouseMoveEvent(self, event):
        if not self.__pressPos.isNull():
            pos2 = event.scenePos()
            if event.modifiers() == Qt.AltModifier:
                if self.__moveMarqueePos.isNull():
                    self.__moveMarqueePos = pos2
                else:
                    self.__moveMarqueeOffset = pos2 - self.__moveMarqueePos
                    self.__moveMarqueePos = pos2
                    self.__pressPos += self.__moveMarqueeOffset
            self.__marqueeRect = QRectF(self.__pressPos, pos2).normalized()
            self.primaryView().showRubberBand(self.__marqueeRect)
        QGraphicsScene.mouseMoveEvent(self, event)

    def selectInRect(self, rect, mode = 'add'):
        items = [ x for x in self.items(rect) if isinstance(x, AbstractDropItem) ]
        currentSelectedItems = [ x for x in self.selectedItems() if isinstance(x, AbstractDropItem) ]
        itemsSet = set(items)
        curSelSet = set(currentSelectedItems)
        if items and mode:
            self.undoOpen.emit()
            try:
                if mode == 'add':
                    items[0].setSelected(True)
                    for item in items[1:]:
                        item.setSelected(True, True)

                elif mode == 'replace':
                    self.clearSelection()
                    items[0].setSelected(True)
                    for item in items[1:]:
                        item.setSelected(True, True)

                elif mode == 'toggle':
                    select = list(itemsSet - curSelSet)
                    deselect = list(itemsSet & curSelSet)
                    for item in deselect:
                        item.setSelected(False, True)

                    for item in select:
                        item.setSelected(True, True)

                elif mode == 'remove':
                    deselect = list(itemsSet & curSelSet)
                    for item in deselect:
                        item.setSelected(False, True)

            finally:
                self.undoClose.emit()

        elif mode == 'add' or mode == 'replace':
            self.clearSelection()
            self.sendCommandData.emit('Deselect', [None], [], [], 'No', self)
        return

    def filterItemByCommand(self, command, targetNode = None, prefix = '', items = None):
        if not items:
            items = [ x for x in self.items() if isinstance(x, AbstractDropItem) and x.command.startswith(command) ]
        if targetNode:
            if prefix:
                items = [ x for x in items if x.targetNode and set(affixPrefix(prefix, x.targetNode)).issubset(set(targetNode)) ]
            else:
                items = [ x for x in items if x.targetNode and set(x.targetNode).issubset(set(targetNode)) ]
        return items

    def findHashcodeItems(self, hashcodes = None):
        if hashcodes is None:
            hashcodes = []
        items = [ x for x in self.items() if isinstance(x, AbstractDropItem) and x.hashcode in hashcodes ]
        return items

    def findLinkedParentItems(self, item):
        items = [ x for x in self.items() if isinstance(x, AbstractDropItem) and x.isVisible() and item in x.linkedItems ]
        return items

    def findVisToggleItem(self, target = ''):
        visItems = [ x for x in self.items() if isinstance(x, VisToggleItem) and x.states.values() ]
        if target:
            return [ x for x in visItems if target in x.states.values()[0].cmd ]
        else:
            return visItems

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Alt:
            if not self.__moveMarqueePos.isNull():
                self.__moveMarqueePos = QPointF()
                self.__moveMarqueeOffset = QPointF()
        QGraphicsScene.keyReleaseEvent(self, event)

    @staticmethod
    def complexStringData(listData):
        data = []
        for singleList in listData:
            data.append(','.join([ str(v) for v in singleList ]))

        return ';'.join(data)

    def clearBgImage(self):
        self.pixmap = QPixmap()
        self.imagePath = ''
        self.useBGimage = False

    def addVarsItem(self, **kwargs):
        if 'size' not in kwargs and 'width' in kwargs and 'height' in kwargs:
            w = kwargs['width']
            del kwargs['width']
            h = kwargs['height']
            del kwargs['height']
            kwargs['size'] = [w, h]
        itemType = getType(kwargs.get('type', None))
        if itemType == None:
            print 'Error'
            return
        else:
            if itemType in [DropItemType.Rectangle,
             DropItemType.RectangleSlider,
             DropItemType.DragPose,
             DropItemType.EditableRectangle,
             DropItemType.EditableRectangleSlider,
             DropItemType.EditableDragPose]:
                item = self.addRectangleItem(**kwargs)
            elif itemType in [DropItemType.Path, DropItemType.EditablePath]:
                item = self.addPathItem(**kwargs)
            elif itemType in [DropItemType.Group, DropItemType.EditableGroup]:
                item = self.addGroupItem(**kwargs)
            elif itemType in [DropItemType.VisToggle, DropItemType.EditableVisToggle]:
                item = self.addVisToggleItem(**kwargs)
            return item

    def addRectangleItem(self, **kwargs):
        if 'type' in kwargs:
            typeValue = getType(kwargs.get('type'))
            if typeValue == DropItemType.RectangleSlider or typeValue == DropItemType.EditableRectangleSlider:
                if isinstance(self, EditableDropScene):
                    item = RectangleEditableDropSliderItem(attachment=kwargs.get('attach', Attachment.TOP), color=kwargs.get('color', Qt.red))
                else:
                    item = RectangleDropSliderItem(attachment=kwargs.get('attach', Attachment.TOP), color=kwargs.get('color', Qt.red))
                margin1, margin2, thickness = kwargs.get('slider', [RectangleEditableDropSliderItem.BORDER_MARGIN, RectangleEditableDropSliderItem.BORDER_MARGIN, RectangleEditableDropSliderItem.SLIDER_THICKNESS])
                item.margin1 = margin1
                item.margin2 = margin2
                item.thickness = thickness
                item.invertedAppearance = kwargs.get('backward', False)
                item.matchMinSizeToSlider()
                self.setupSliderData(item, kwargs.get('command'))
            elif typeValue == DropItemType.DragPose or typeValue == DropItemType.EditableDragPose:
                if isinstance(self, EditableDropScene):
                    item = DragPoseEditableDropItem(kwargs.get('color', Qt.red))
                else:
                    item = DragPoseDropItem(kwargs.get('color', Qt.red))
            elif isinstance(self, EditableDropScene):
                item = RectangleEditableDropItem(kwargs.get('color', Qt.red))
            else:
                item = RectangleDropItem(kwargs.get('color', Qt.red))
            self.setupItemData(item, **kwargs)
            return item
        print 'Error: type is not defined'

    def setupItemData(self, item, **kwargs):
        if 'size' in kwargs:
            width, height = kwargs.get('size')
            item.width = width
            item.height = height
        if item.width < item.DEFAULT_MINSIZE:
            item.minWidth = item.width
        if item.height < item.DEFAULT_MINSIZE:
            item.minHeight = item.height
        if 'command' in kwargs:
            item.command = kwargs.get('command')
        if 'node' in kwargs:
            item.targetNode = kwargs.get('node')
        if 'channel' in kwargs:
            item.targetChannel = kwargs.get('channel')
        if 'value' in kwargs:
            item.targetValue = kwargs.get('value')
        if kwargs.get('type') != 'Path' and 'icon' in kwargs and kwargs.get('icon'):
            path, rect = kwargs.get('icon')
            item.iconPath = path
            if rect.isValid():
                item.iconRect = rect
                maxRect = item.inboundRect()
                if not maxRect.contains(item.iconRect):
                    item.setDefaultIconRect()
            else:
                item.setDefaultIconRect()
        if 'label' in kwargs and kwargs.get('label'):
            label, rect, font = kwargs.get('label')
            item.label = label
            if font:
                item.font = font
            if rect.isValid():
                item.labelRect = rect
                maxRect = item.boundingRect().adjusted(item.BORDER_MARGIN, item.BORDER_MARGIN, -item.BORDER_MARGIN, -item.BORDER_MARGIN)
                if not maxRect.contains(item.labelRect):
                    rect = item.setDefaultLabelRect()
                    if rect:
                        item.labelRect = rect
            else:
                rect = item.setDefaultLabelRect()
                if rect:
                    item.labelRect = rect
            item.matchMinSizeToSubordinate()
        topItem = self.getTopItem()
        self.addItem(item)
        item.setPos(kwargs.get('pos', QPointF(0, 0)))
        if 'hashcode' in kwargs and kwargs.get('hashcode'):
            item.hashcode = kwargs.get('hashcode')
        else:
            item.hashcode = generateHashcode(item)
        if topItem:
            item.setZValue(topItem.zValue() + 0.001)
        self.connectItemSignals(item)
        return item

    def getItemsByZValueOrder(self, rect = QRectF()):
        items = [ x for x in rect.isValid() and self.items(rect) or self.items() if isinstance(x, (AbstractDropItem, GroupItem)) ]
        if items:
            items.sort(key=lambda x: x.zValue())
        return items

    def getTopItem(self):
        items = self.getItemsByZValueOrder()
        if items:
            return items[-1]
        else:
            return None
            return None

    def connectItemSignals(self, item):
        item.comm.sendCommandData.connect(lambda *args: self.sendCommandData.emit(*(list(args) + [self])))
        item.comm.itemChanged.connect(lambda : self.sceneChanged.emit())
        item.comm.redefineMember.connect(self.redefineMember.emit)
        item.comm.changeMember.connect(self.changeMember.emit)
        item.comm.editRemote.connect(self.editRemote.emit)
        if item.command == 'Pose':
            item.comm.mousePressed.connect(lambda : self.poseGlobalVarSet.emit(item))
            item.comm.mouseReleased.connect(lambda : self.poseGlobalVarUnset.emit(item))

    def setupSliderData(self, item, command):
        if command == 'Range':
            item.setRange(-1, 1)
        self.connectSliderSignals(item, command)

    def connectSliderSignals(self, item, command):
        item.comm.sliderMousePressed.connect(self.undoOpen.emit)
        item.comm.sliderMouseReleased.connect(self.undoClose.emit)
        if command == 'Pose':
            item.comm.sliderMousePressed.connect(lambda : self.poseGlobalVarSet.emit(item))
            item.comm.sliderMouseReleased.connect(lambda : self.poseGlobalVarUnset.emit(item))

    def addPathItem(self, **kwargs):
        if 'icon' in kwargs and kwargs.get('icon'):
            from svgParser import decodeSvgPathStringReplace, createSvgPath
            pathOrder = decodeSvgPathStringReplace(kwargs.get('icon'))
            path = createSvgPath(pathOrder)
            path.translate(path.boundingRect().topLeft() * -1)
            if isinstance(self, EditableDropScene):
                item = PathEditableDropItem(path, QColor(kwargs.get('color', Qt.red)))
            else:
                item = PathDropItem(path, QColor(kwargs.get('color', Qt.red)))
            self.setupItemData(item, **kwargs)
            return item

    def addVisToggleItem(self, **kwargs):
        if 'path' in kwargs and kwargs.get('path'):
            path = kwargs.get('path')
            if isinstance(path, (unicode, str)):
                from svgParser import decodeSvgPathStringReplace, createSvgPath
                pathOrder = decodeSvgPathStringReplace(path)
                path = createSvgPath(pathOrder)
            color = QColor(kwargs.get('color', Qt.red))
            states = kwargs.get('states', {0: ToggleState('IK', True, color),
             1: ToggleState('FK', color=color)})
            if isinstance(self, EditableDropScene):
                item = VisToggleEditableItem(path, color, states)
            else:
                item = VisToggleItem(path, color, states)
            self.setupItemData(item, **kwargs)
            return item

    def setMovableSelectedItems(self, movable):
        for item in [ x for x in self.selectedItems() if isinstance(x, AbstractDropItem) ]:
            if movable:
                item.setFlags(item.flags() | QGraphicsItem.ItemIsMovable)
            else:
                item.setFlags(item.flags() & ~QGraphicsItem.ItemIsMovable)

    def selectedItemsRect(self):
        return self.rectForGivenItems(self.selectedItems())

    def rectForGivenItems(self, items = None):
        rect = QRectF()
        for item in items or []:
            rect = rect.united(item.sceneBoundingRect())

        return rect

    def doAllItems(self, command, channelFlag):
        items = [ x for x in self.items() if isinstance(x, AbstractDropItem) and x.targetNode ]
        if channelFlag == 'Defined':
            channelFlag = ''
            items = [ x for x in items if x.targetChannel ]
        if not items:
            return
        for item in items:
            item.emitCommmand(command, channelFlag)

    def addGroupItem(self, **kwargs):
        if 'type' in kwargs and getType(kwargs.get('type')) in [DropItemType.Group, DropItemType.EditableGroup]:
            item = EditableGroupItem(*kwargs.get('size'))
            self.setupGroupItemData(item, **kwargs)
            return item

    def setupGroupItemData(self, item, **kwargs):
        if 'label' in kwargs:
            item.label = kwargs.get('label')
        if 'doKey' in kwargs:
            item.doKey = kwargs.get('doKey')
        if 'doReset' in kwargs:
            item.doReset = kwargs.get('doReset')
        if 'labelPos' in kwargs:
            item.labelPosition = kwargs.get('labelPos')
        if 'buttonPos' in kwargs:
            item.buttonPosition = kwargs.get('buttonPos')
        if 'hashcode' in kwargs and kwargs.get('hashcode'):
            item.hashcode = kwargs.get('hashcode')
        else:
            item.hashcode = generateHashcode(item)
        self.addItem(item)
        item.setPos(kwargs.get('pos', QPointF(0, 0)))
        item.setZValue(0)
        self.connectGroupItemSignals(item)
        return item

    def connectGroupItemSignals(self, item):
        item.comm.undoOpen.connect(self.undoOpen.emit)
        item.comm.undoClose.connect(self.undoClose.emit)
        item.comm.itemChanged.connect(self.sceneChanged.emit)

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


class EditableDropScene(DropScene):
    addItemOn = Signal(QPointF, QColor, int)
    addItemWithSet = Signal(QPointF, QColor, unicode, dict)
    addPreviewedItem = Signal(QPointF, QColor, unicode, dict)
    copyItems = Signal(list)
    selectedItemsChanged = Signal(list)

    def __init__(self, parent = None):
        DropScene.__init__(self, parent)
        self.__editable = True
        self.__linkGuideLine = self.__linkBaseItem = None
        self.selectionChanged.connect(lambda : self.selectedItemsChanged.emit(self.selectedItems()))
        return

    @property
    @returns(bool)
    def editable(self):
        return self.__editable

    @editable.setter
    @accepts(bool)
    def editable(self, editable):
        self.__editable = editable
        self.update()

    def setAllItemsEditable(self, editable):
        self.editable = editable
        for item in [ x for x in self.items() if isinstance(x, AbstractDropItem) ]:
            item.editable = editable

    def dragEnterEvent(self, event):
        if not self.editable:
            event.ignore()
            return
        mimeData = event.mimeData()
        if mimeData.hasFormat(MIME_COLOR_MODIFIER) or mimeData.hasUrls() or mimeData.hasFormat(MIME_TEMPLATE) or mimeData.hasFormat(MIME_NEWBUTTON) or mimeData.hasFormat(MIME_COLOR) or mimeData.hasFormat(MIME_IMAGE_PATH) or mimeData.hasFormat(MIME_SLIDER_COMMAND):
            event.setDropAction(Qt.CopyAction)
            event.accept()
            if mimeData.hasFormat(MIME_TEMPLATE):
                sizeStr = unicode(mimeData.data(MIME_TEMPLATE_SIZE))
                size = QSizeF(*[ float(v) for v in sizeStr.split() ])
                pen = QPen(Qt.black, 0, Qt.DashLine)
                self.marquee = self.addRect(QRectF(QPointF(0, 0), size), pen, QBrush(Qt.NoBrush))
                self.marquee.setZValue(65536)
        elif mimeData.hasFormat('text/plain') or mimeData.hasFormat(MIME_DRAGCOMBO_TEXT) or mimeData.hasFormat(MIME_COMMAND) or mimeData.hasFormat(MIME_LABEL) or mimeData.hasFormat(MIME_FONT_FAMILY) or mimeData.hasFormat(MIME_CUSTOM_LABEL):
            event.setDropAction(Qt.CopyAction)
            event.ignore()
        else:
            for f in mimeData.formats():
                if f == 'application/x-maya-data':
                    pass
                else:
                    print f, mimeData.data(f), mimeData.data(f).length()

        QGraphicsScene.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        if not self.editable:
            event.ignore()
            return
        mimeData = event.mimeData()
        if mimeData.hasFormat(MIME_TEMPLATE) or mimeData.hasFormat(MIME_NEWBUTTON) or mimeData.hasFormat(MIME_SLIDER_COMMAND):
            event.setDropAction(Qt.CopyAction)
            event.accept()
            if mimeData.hasFormat(MIME_TEMPLATE):
                self.marquee.setPos(event.scenePos())
        elif mimeData.hasFormat(MIME_COLOR_MODIFIER) or mimeData.hasUrls() or mimeData.hasFormat(MIME_COLOR) or mimeData.hasFormat(MIME_IMAGE_PATH):
            event.setDropAction(Qt.CopyAction)
            event.accept()
            if self.itemAt(event.scenePos(), QTransform()):
                QGraphicsScene.dragMoveEvent(self, event)
        else:
            QGraphicsScene.dragMoveEvent(self, event)

    def dragLeaveEvent(self, event):
        mimeData = event.mimeData()
        QGraphicsScene.dragLeaveEvent(self, event)
        if mimeData.hasFormat(MIME_TEMPLATE):
            if self.marquee:
                self.removeItem(self.marquee)
                self.marquee = None
        return

    def dropEvent(self, event):
        mimeData = event.mimeData()
        pos = event.scenePos()
        if mimeData.hasFormat(MIME_COLOR_MODIFIER):
            if not self.itemAt(pos, QTransform()):
                modifier = mimeData.data(MIME_COLOR_MODIFIER).toLong()[0]
                self.addItemOn.emit(pos, mimeData.colorData(), modifier)
        elif mimeData.hasFormat(MIME_TEMPLATE):
            if self.marquee:
                self.removeItem(self.marquee)
                self.marquee = None
            if pos is None:
                return
            print mimeData.urls()[0].toLocalFile()
            path = mimeData.urls()[0].toLocalFile()
            self.addItemsFromSvgFile(path, pos)
        elif mimeData.hasUrls():
            if not self.itemAt(pos, QTransform()):
                path = [ y for y in [ x.toLocalFile() for x in mimeData.urls() ] if os.path.splitext(y)[-1].lower() in ('.jpg', '.png') ]
                if path:
                    self.setBackgroundPixmap(path[0])
                    self.sceneChanged.emit()
        elif mimeData.hasFormat(MIME_IMAGE_PATH):
            if not self.itemAt(pos, QTransform()):
                path = unicode(mimeData.data(MIME_IMAGE_PATH))
                self.setBackgroundPixmap(path)
                self.sceneChanged.emit()
        elif mimeData.hasFormat(MIME_NEWBUTTON):
            color = mimeData.colorData()
            command = unicode(mimeData.data(MIME_NEWBUTTON))
            datas = {}
            allFormats = set(mimeData.formats())
            alreadyTaken = set([MIME_NEWBUTTON, 'application/x-color'])
            for f in list(allFormats - alreadyTaken):
                datas[f.rsplit('-', 1)[1]] = mimeData.data(f)

            self.addItemWithSet.emit(pos, color, command, datas)
        elif mimeData.hasFormat(MIME_COLOR):
            if not self.itemAt(pos, QTransform()):
                color = mimeData.colorData()
                self.color = color
                self.sceneChanged.emit()
        elif mimeData.hasFormat(MIME_SLIDER_COMMAND):
            color = mimeData.colorData()
            command = unicode(mimeData.data(MIME_SLIDER_COMMAND))
            data = {}
            data['width'] = mimeData.data(MIME_SLIDER_WIDTH).toInt()[0]
            data['height'] = mimeData.data(MIME_SLIDER_HEIGHT).toInt()[0]
            if mimeData.hasFormat(MIME_SLIDER_CHANGETOOL):
                data[MIME_SLIDER_CHANGETOOL.rsplit('-', 1)[-1]] = unicode(mimeData.data(MIME_SLIDER_CHANGETOOL))
            if mimeData.hasFormat(MIME_SLIDER_ATTRIBUTE):
                data[MIME_SLIDER_ATTRIBUTE.rsplit('-', 1)[-1]] = unicode(mimeData.data(MIME_SLIDER_ATTRIBUTE))
            if mimeData.hasFormat(MIME_SLIDER_BUTTONNUMBER):
                data[MIME_SLIDER_BUTTONNUMBER.rsplit('-', 1)[-1]] = unicode(mimeData.data(MIME_SLIDER_BUTTONNUMBER))
            if mimeData.hasFormat(MIME_SLIDER_ATTACH):
                data['attach'] = mimeData.data(MIME_SLIDER_ATTACH).toInt()[0]
            if mimeData.hasFormat(MIME_SLIDER_INVERSE):
                data['backward'] = bool(mimeData.data(MIME_SLIDER_INVERSE).toInt()[0])
            self.addPreviewedItem.emit(pos, color, command, data)
        QGraphicsScene.dropEvent(self, event)
        return

    def mousePressEvent(self, event):
        items = [ x for x in self.items(event.scenePos()) if isinstance(x, AbstractDropItem) ]
        if items:
            item = items[0]
        else:
            item = None
        button = event.button()
        modifier = event.modifiers()
        if item and button == Qt.MiddleButton and modifier == Qt.ControlModifier:
            pos = event.scenePos()
            self.__linkGuideLine = LineItem(pos, pos)
            self.__linkGuideLine.setLineColor(Qt.red)
            self.__linkBaseItem = item
            self.addItem(self.__linkGuideLine)
            self.__linkGuideLine.setZValue(65536)
        else:
            DropScene.mousePressEvent(self, event)
        return

    def mouseReleaseEvent(self, event):
        items = [ x for x in self.items(event.scenePos()) if isinstance(x, AbstractDropItem) ]
        if items:
            item = items[0]
        else:
            item = None
        if self.__linkGuideLine and self.__linkBaseItem:
            if item and isinstance(item, AbstractDropItem):
                linked = [item] + getLinkedItems(item)
                if self.__linkBaseItem not in linked:
                    self.__linkBaseItem.linkedItems += [item]
            else:
                self.__linkBaseItem.linkedItems = []
            self.removeItem(self.__linkGuideLine)
            self.__linkGuideLine = self.__linkBaseItem = None
        else:
            DropScene.mouseReleaseEvent(self, event)
        return

    def mouseMoveEvent(self, event):
        if self.__linkGuideLine:
            self.__linkGuideLine.setP2(event.scenePos())
        else:
            DropScene.mouseMoveEvent(self, event)

    def keyPressEvent(self, event):
        if not self.editable:
            return
        if event.key() == Qt.Key_Delete:
            rnt = self.deleteSelectedItems()
            if isinstance(rnt, (str, unicode)):
                print rnt
        elif event.matches(QKeySequence.Copy):
            rnt = self.copyToWindowClipboard()
            if isinstance(rnt, (str, unicode)):
                print rnt
        elif event.matches(QKeySequence.Paste):
            rnt = self.pasteFromWindowClipboard()
            if isinstance(rnt, (str, unicode)):
                print rnt
        elif event.key() == Qt.Key_D and event.modifiers() == Qt.ControlModifier:
            rnt = self.duplicateSelectedItems()
            if isinstance(rnt, (str, unicode)):
                print rnt
        else:
            QGraphicsScene.keyPressEvent(self, event)

    def deleteSelectedItems(self):
        items = self.selectedItems()
        if not items:
            return '>> Error: Nothing selected!'
        if question('Remove selected items?', 'Remove', self.primaryView()):
            try:
                self.clearSelection()
                for item in items:
                    item.comm.aboutToRemove.emit(item)
                    item.linkedItems = []
                    self.removeItem(item)

                self.sceneChanged.emit()
            except:
                return ('>> Error : cannot remove item', item.__repr__())

        return True

    def copyToWindowClipboard(self):
        selectedItems = self.selectedItems()
        if not selectedItems:
            return '>> Error: Nothing selected!'
        data = []
        for item in selectedItems:
            valuesDict = item.properties()
            params = []
            for initParam in item.__init__.__func__.__code__.co_varnames[1:]:
                if initParam in valuesDict:
                    v = valuesDict[initParam]
                    del valuesDict[initParam]
                    params.append(v)

            data.append([type(item),
             item.scenePos(),
             params,
             valuesDict])

        self.copyItems.emit(data)
        return True

    def pasteFromWindowClipboard(self):
        if not self.window().clipboard:
            return '>> Error: Empty clipboard!'
        topItem = self.getTopItem()
        if topItem:
            zValue = topItem.zValue()
        else:
            zValue = -0.001
        self.clearSelection()
        for i, (itemClass, pos, params, valuesDict) in enumerate(self.window().clipboard):
            item = itemClass(*params)
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

            self.appendCopyItem(item, pos, zValue + 0.001 * (i + 1))
            item.hashcode = generateHashcode(item)

        self.sceneChanged.emit()
        return True

    def duplicateSelectedItems(self):
        items = self.selectedItems()
        if not items:
            return '>> Error: Nothing selected!'
        self.clearSelection()
        topItem = self.getTopItem()
        zValue = topItem.zValue()
        for i, item in enumerate(items):
            newItem = item.clone()
            self.appendCopyItem(newItem, item.pos() + QPointF(10, 10), zValue + 0.001 * (i + 1))
            item.hashcode = generateHashcode(item)

        self.sceneChanged.emit()
        return True

    def appendCopyItem(self, item, pos, zValue):
        self.addItem(item)
        item.setPos(pos)
        item.setZValue(zValue)
        self.connectItemSignals(item)
        if isinstance(item, RectangleDropSliderItem):
            item.resetSliderRects()
            self.connectSliderSignals(item, item.command)
        item.setSelected(True)

    def alignSelectedItems(self, alignType):
        if alignType == 'left':
            alignTo = self.selectedItemsRect().left()
        elif alignType == 'right':
            alignTo = self.selectedItemsRect().right()
        elif alignType == 'hcenter':
            alignTo = self.selectedItemsRect().center().x()
        elif alignType == 'top':
            alignTo = self.selectedItemsRect().top()
        elif alignType == 'bottom':
            alignTo = self.selectedItemsRect().bottom()
        elif alignType == 'vcenter':
            alignTo = self.selectedItemsRect().center().y()
        else:
            return
        for item in self.selectedItems():
            itemRect = item.sceneBoundingRect()
            if alignType == 'left':
                dx, dy = alignTo - itemRect.left(), 0
            elif alignType == 'right':
                dx, dy = alignTo - itemRect.right(), 0
            elif alignType == 'hcenter':
                dx, dy = alignTo - itemRect.center().x(), 0
            elif alignType == 'top':
                dx, dy = 0, alignTo - itemRect.top()
            elif alignType == 'bottom':
                dx, dy = 0, alignTo - itemRect.bottom()
            else:
                dx, dy = 0, alignTo - itemRect.center().y()
            item.moveBy(dx, dy)

    def averageGapSelectedItems(self, direction):
        items = self.selectedItems()
        count = len(items)
        if count < 3:
            return
        if direction == 'hor':
            isHorizontal = True
        elif direction == 'ver':
            isHorizontal = False
        else:
            return
        items.sort(cmp=lambda x, y: self.cmpCenterPosition(x, y, direction))
        length = isHorizontal and self.selectedItemsRect().width() or self.selectedItemsRect().height()
        lengthSum = 0.0
        for item in items:
            lengthSum += isHorizontal and item.width or item.height

        gap = (length - lengthSum) / (count - 1)
        for i in xrange(1, count - 1):
            if isHorizontal:
                dest = items[i - 1].sceneBoundingRect().right() + gap
                dx, dy = dest - items[i].sceneBoundingRect().left(), 0
            else:
                dest = items[i - 1].sceneBoundingRect().bottom() + gap
                dx, dy = 0, dest - items[i].sceneBoundingRect().top()
            items[i].moveBy(dx, dy)

    def averageSizeSelectedItems(self, direction):
        items = self.selectedItems()
        if not items:
            return
        if direction == 'width':
            isWidth = True
        elif direction == 'height':
            isWidth = False
        else:
            return
        values = [ isWidth and i.width or i.height for i in items ]
        avg = reduce(lambda x, y: x + y, values) / len(values)
        for item in items:
            if isWidth:
                item.width = avg
            else:
                item.height = avg

    def arrangeSelectedItems(self, options = ''):
        items = self.selectedItems()
        if not items:
            return
        for item in items:
            if options == 'bringFront':
                item.bringToFront()
            elif options == 'bringForward':
                item.bringForward()
            elif options == 'sendBackward':
                item.sendBackward()
            elif options == 'sendBack':
                item.sendToBack()

    def moveSelectedItemsToCenter(self, axis):
        items = self.selectedItems()
        if not items:
            return
        for item in items:
            if axis == 'hor':
                item.setX((self.mapSize.width() - item.width) / 2)
            elif axis == 'ver':
                item.setY((self.mapSize.height() - item.height) / 2)

    @staticmethod
    def cmpCenterPosition(x, y, direction):
        if direction == 'hor':
            xVal = x.sceneBoundingRect().center().x()
            yVal = y.sceneBoundingRect().center().x()
        elif direction == 'ver':
            xVal = x.sceneBoundingRect().center().y()
            yVal = y.sceneBoundingRect().center().y()
        else:
            return 0
        if xVal > yVal:
            return 1
        elif xVal < yVal:
            return -1
        else:
            return 0

    def mirrorSelectedItems(self, search = '', replace = '', changeColor = False):
        items = self.selectedItems()
        if not items:
            return
        from const import getMirrorColor
        mapRect = QRectF(QPointF(0, 0), self.mapSize)
        for item in items:
            itemRect = item.sceneBoundingRect()
            transform = QTransform()
            transform.translate(mapRect.width() / 2.0, 0)
            transform.scale(-1, 1)
            transform.translate(mapRect.width() / -2.0, 0)
            mirrorRect = transform.mapRect(itemRect)
            if changeColor:
                color = getMirrorColor(item.color)
            else:
                color = item.color
            mirrorItem = item.clone()
            mirrorItem.color = color
            topItem = self.getTopItem()
            self.addItem(mirrorItem)
            mirrorItem.setPos(mirrorRect.topLeft())
            mirrorItem.setZValue(topItem.zValue() + 0.001)
            if search:
                for i in xrange(len(mirrorItem.targetNode)):
                    mirrorItem.targetNode[i] = mirrorItem.targetNode[i].replace(search, replace)

            self.connectItemSignals(mirrorItem)
            if isinstance(mirrorItem, RectangleDropSliderItem):
                mirrorItem.resetSliderRects()
                self.connectSliderSignals(mirrorItem, mirrorItem.command)
            if isinstance(mirrorItem, PathDropItem):
                from const import getMirroredPath
                mirrorItem.path = getMirroredPath(mirrorItem.path)
            item.setIgnore(True)
            item.setSelected(False)
            item.setIgnore(False)
            mirrorItem.setIgnore(True)
            mirrorItem.setSelected(True)
            mirrorItem.setIgnore(False)

        self.sceneChanged.emit()

    def addItemsFromSvgFile(self, svgFile, pos = QPointF()):
        from svgParser import getPathOrderFromSvgFile, createSvgPath, createEllipsePath, createRectPath, createPolygonPath
        drawSet = []
        boundingRect = QRectF()
        for style, path, pathType, id in getPathOrderFromSvgFile(svgFile):
            if style.get('display') == 'none':
                continue
            if pathType == 'path':
                svgPath = createSvgPath(path)
            elif pathType in ('circle', 'ellipse'):
                svgPath = createEllipsePath(path)
            elif pathType == 'rect':
                svgPath = createRectPath(path)
            elif pathType == 'polygon':
                svgPath = createPolygonPath(path)
            else:
                print 'not supported for', pathType
            boundingRect = boundingRect.united(svgPath.boundingRect())
            drawSet.append({'id': id,
             'style': style,
             'svgPath': svgPath})

        for bundle in drawSet:
            path = bundle['svgPath']
            del bundle['svgPath']
            offset = path.boundingRect().topLeft() - boundingRect.topLeft()
            path.translate(path.boundingRect().topLeft() * -1)
            bundle['svgPath'] = path
            bundle['offset'] = offset

        for bundle in drawSet:
            item = PathEditableDropItem(bundle.get('svgPath'), QColor(bundle.get('style').get('fill', Qt.black)))
            self.setupItemData(item, pos=pos + bundle.get('offset'), command='Select', node=bundle.get('id') and [bundle.get('id')] or [])

        self.sceneChanged.emit()

    def createButtonGroupSelectedItems(self):
        items = self.selectedItems()
        if not items:
            return
        if [ i for i in items if i.parentItem() ]:
            return warn('Some of them already have been assigned', parent=self.primaryView())
        rect = self.selectedItemsRect().adjusted(-GroupItem.PADDING, -GroupItem.PADDING, GroupItem.PADDING, GroupItem.PADDING)
        pos = rect.topLeft()
        size = rect.size()
        grpItem = self.addGroupItem(type='Group', pos=pos, size=[size.width(), size.height()])
        for i in items:
            i.setParentItem(grpItem)

    def clone(self):
        valuesDict = self.properties()
        params = []
        for initParam in self.__init__.__func__.__code__.co_varnames[1:]:
            if initParam in valuesDict:
                v = valuesDict[initParam]
                del valuesDict[initParam]
                params.append(v)

        scene = self.__class__(*params)
        for k, v in valuesDict.items():
            try:
                setattr(scene, k, copy(v))
            except AttributeError:
                print ">> Can't set [%s]" % k

        return scene