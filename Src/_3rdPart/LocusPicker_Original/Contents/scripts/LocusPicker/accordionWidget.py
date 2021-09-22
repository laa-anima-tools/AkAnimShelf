# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\accordionWidget.py
try:
    from PySide2.QtCore import Qt, QRect, QMimeData, Signal, Property, QEvent, QPoint
    from PySide2.QtGui import QDrag, QPixmap, QPainter, QPalette, QPen, QCursor, QColor, QPolygon, QBrush
    from PySide2.QtWidgets import QScrollArea, QGroupBox, QVBoxLayout, QWidget
except:
    from PySide.QtCore import Qt, QRect, QMimeData, Signal, Property, QEvent, QPoint
    from PySide.QtGui import QDrag, QPixmap, QScrollArea, QGroupBox, QVBoxLayout, QPainter, QPalette, QPen, QWidget, QCursor, QColor, QPolygon, QBrush

class AccordionItem(QGroupBox):

    def __init__(self, accordion, title, widget):
        QGroupBox.__init__(self, accordion)
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        layout.addWidget(widget)
        self._accordianWidget = accordion
        self._rolloutStyle = AccordionWidget.Rounded
        self._dragDropMode = AccordionWidget.NoDragDrop
        self.setAcceptDrops(True)
        self.setLayout(layout)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        self._widget = widget
        self._collapsed = False
        self._collapsible = True
        self._clicked = False
        self._customData = {}
        self._margin = 2
        self.setTitle(title)

    def accordionWidget(self):
        return self._accordianWidget

    def customData(self, key, default = None):
        return self._customData.get(str(key), default)

    def dragEnterEvent(self, event):
        if not self._dragDropMode:
            return
        source = event.source()
        if source and source != self and source.parent() == self.parent() and isinstance(source, AccordionItem):
            event.acceptProposedAction()

    def dragDropRect(self):
        return QRect(21, 8, 10, 6)

    def dragDropMode(self):
        return self._dragDropMode

    def dragMoveEvent(self, event):
        if not self._dragDropMode:
            return
        source = event.source()
        if source != self and source.parent() == self.parent() and isinstance(source, AccordionItem):
            event.acceptProposedAction()

    def dropEvent(self, event):
        widget = event.source()
        layout = self.parent().layout()
        layout.insertWidget(layout.indexOf(self), widget)
        self._accordianWidget.emitItemsReordered()

    def expandCollapseRect(self):
        return QRect(0, 0, self.width(), 20)

    def enterEvent(self, event):
        self.accordionWidget().leaveEvent(event)
        event.accept()

    def leaveEvent(self, event):
        self.accordionWidget().enterEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._clicked and self.expandCollapseRect().contains(event.pos()):
            self.toggleCollapsed()
            event.accept()
        else:
            event.ignore()
        self._clicked = False

    def mouseMoveEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        if self.dragDropMode() and event.button() == Qt.LeftButton and self.dragDropRect().contains(event.pos()):
            pixmap = QPixmap.grabWidget(self, self.rect())
            mimeData = QMimeData()
            mimeData.setText('ItemTitle::%s' % self.title())
            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            if not drag.exec_():
                self._accordianWidget.emitItemDragFailed(self)
            event.accept()
        elif event.button() == Qt.LeftButton and self.expandCollapseRect().contains(event.pos()):
            self._clicked = True
            event.accept()
        else:
            event.ignore()

    def isCollapsed(self):
        return self._collapsed

    def isCollapsible(self):
        return self._collapsible

    def __drawTriangle(self, painter, x, y):
        if self.rolloutStyle() == AccordionWidget.Maya:
            brush = QBrush(QColor(255, 0, 0, 160), Qt.SolidPattern)
        else:
            brush = QBrush(QColor(255, 255, 255, 160), Qt.SolidPattern)
        if not self.isCollapsed():
            tl, tr, tp = QPoint(x + 9, y + 8), QPoint(x + 19, y + 8), QPoint(x + 14, y + 13)
            points = [tl, tr, tp]
            triangle = QPolygon(points)
        else:
            tl, tr, tp = QPoint(x + 11, y + 5), QPoint(x + 16, y + 10), QPoint(x + 11, y + 15)
            points = [tl, tr, tp]
            triangle = QPolygon(points)
        currentPen = painter.pen()
        currentBrush = painter.brush()
        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        painter.drawPolygon(triangle)
        painter.setPen(currentPen)
        painter.setBrush(currentBrush)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(painter.Antialiasing)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        x = self.rect().x()
        y = self.rect().y()
        w = self.rect().width() - 1
        h = self.rect().height() - 1
        r = 8
        if self._rolloutStyle == AccordionWidget.Rounded:
            painter.drawText(x + 33, y + 3, w, 16, Qt.AlignLeft | Qt.AlignTop, self.title())
            self.__drawTriangle(painter, x, y)
            pen = QPen(self.palette().color(QPalette.Light))
            pen.setWidthF(0.6)
            painter.setPen(pen)
            painter.drawRoundedRect(x + 1, y + 1, w - 1, h - 1, r, r)
            pen.setColor(self.palette().color(QPalette.Shadow))
            painter.setPen(pen)
            painter.drawRoundedRect(x, y, w - 1, h - 1, r, r)
        if self._rolloutStyle == AccordionWidget.Square:
            painter.drawText(x + 33, y + 3, w, 16, Qt.AlignLeft | Qt.AlignTop, self.title())
            self.__drawTriangle(painter, x, y)
            pen = QPen(self.palette().color(QPalette.Light))
            pen.setWidthF(0.6)
            painter.setPen(pen)
            painter.drawRect(x + 1, y + 1, w - 1, h - 1)
            pen.setColor(self.palette().color(QPalette.Shadow))
            painter.setPen(pen)
            painter.drawRect(x, y, w - 1, h - 1)
        if self._rolloutStyle == AccordionWidget.Maya:
            painter.drawText(x + (self.dragDropMode() == AccordionWidget.InternalMove and 33 or 22), y + 3, w, 16, Qt.AlignLeft | Qt.AlignTop, self.title())
            painter.setRenderHint(QPainter.Antialiasing, False)
            self.__drawTriangle(painter, x, y)
            headerHeight = 20
            headerRect = QRect(x + 1, y + 1, w - 1, headerHeight)
            headerRectShadow = QRect(x - 1, y - 1, w + 1, headerHeight + 2)
            pen = QPen(self.palette().color(QPalette.Light))
            pen.setWidthF(0.4)
            painter.setPen(pen)
            painter.drawRect(headerRect)
            painter.fillRect(headerRect, QColor(255, 255, 255, 18))
            pen.setColor(self.palette().color(QPalette.Dark))
            painter.setPen(pen)
            painter.drawRect(headerRectShadow)
            if not self.isCollapsed():
                pen = QPen(self.palette().color(QPalette.Dark))
                pen.setWidthF(0.8)
                painter.setPen(pen)
                offSet = headerHeight + 3
                bodyRect = QRect(x, y + offSet, w, h - offSet)
                bodyRectShadow = QRect(x + 1, y + offSet, w + 1, h - offSet + 1)
                painter.drawRect(bodyRect)
                pen.setColor(self.palette().color(QPalette.Light))
                pen.setWidthF(0.4)
                painter.setPen(pen)
                painter.drawRect(bodyRectShadow)
        elif self._rolloutStyle == AccordionWidget.Box:
            if self.isCollapsed():
                arect = QRect(x + 1, y + 9, w - 1, 4)
                brect = QRect(x, y + 8, w - 1, 4)
                text = '+'
            else:
                arect = QRect(x + 1, y + 9, w - 1, h - 9)
                brect = QRect(x, y + 8, w - 1, h - 9)
                text = '-'
            pen = QPen(self.palette().color(QPalette.Light))
            pen.setWidthF(0.6)
            painter.setPen(pen)
            painter.drawRect(arect)
            pen.setColor(self.palette().color(QPalette.Shadow))
            painter.setPen(pen)
            painter.drawRect(brect)
            painter.setRenderHint(painter.Antialiasing, False)
            painter.setBrush(self.palette().color(QPalette.Window).darker(120))
            painter.drawRect(x + 10, y + 1, w - 20, 16)
            painter.drawText(x + 16, y + 1, w - 32, 16, Qt.AlignLeft | Qt.AlignVCenter, text)
            painter.drawText(x + 10, y + 1, w - 20, 16, Qt.AlignCenter, self.title())
        if self.dragDropMode():
            rect = self.dragDropRect()
            l = rect.left()
            r = rect.right()
            cy = rect.center().y()
            pen = QPen(self.palette().color(self.isCollapsed() and QPalette.Shadow or QPalette.Mid))
            painter.setPen(pen)
            for y in (cy - 3, cy, cy + 3):
                painter.drawLine(l, y, r, y)

        painter.end()

    def setCollapsed(self, state = True):
        if self.isCollapsible():
            accord = self.accordionWidget()
            accord.setUpdatesEnabled(False)
            self._collapsed = state
            if state:
                self.setMinimumHeight(22)
                self.setMaximumHeight(22)
                self.widget().setVisible(False)
            else:
                self.setMinimumHeight(0)
                self.setMaximumHeight(1000000)
                self.widget().setVisible(True)
            self._accordianWidget.emitItemCollapsed(self)
            accord.setUpdatesEnabled(True)

    def setCollapsible(self, state = True):
        self._collapsible = state

    def setCustomData(self, key, value):
        self._customData[str(key)] = value

    def setDragDropMode(self, mode):
        self._dragDropMode = mode

    def setRolloutStyle(self, style):
        self._rolloutStyle = style
        m = self.margin()
        if style == AccordionWidget.Maya:
            self.layout().setContentsMargins(m, m + 9, m, m)
        else:
            self.layout().setContentsMargins(m, m, m, m)

    def setMargin(self, margin):
        self._margin = margin
        self.setRolloutStyle(self.rolloutStyle())

    def margin(self):
        return self._margin

    def showMenu(self):
        if QRect(0, 0, self.width(), 20).contains(self.mapFromGlobal(QCursor.pos())):
            self._accordianWidget.emitItemMenuRequested(self)

    def rolloutStyle(self):
        return self._rolloutStyle

    def toggleCollapsed(self):
        self.setCollapsed(not self.isCollapsed())

    def widget(self):
        return self._widget


class AccordionWidget(QScrollArea):
    itemCollapsed = Signal(AccordionItem)
    itemMenuRequested = Signal(AccordionItem)
    itemDragFailed = Signal(AccordionItem)
    itemsReordered = Signal()
    Boxed = 1
    Rounded = 2
    Square = 3
    Maya = 4
    NoDragDrop = 0
    InternalMove = 1

    def __init__(self, parent):
        QScrollArea.__init__(self, parent)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setAutoFillBackground(False)
        self.setWidgetResizable(True)
        self.setMouseTracking(True)
        widget = QWidget(self)
        self._rolloutStyle = AccordionWidget.Rounded
        self._dragDropMode = AccordionWidget.NoDragDrop
        self._scrolling = False
        self._scrollInitY = 0
        self._scrollInitVal = 0
        self._itemClass = AccordionItem
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        layout.addStretch(1)
        widget.setLayout(layout)
        self.setWidget(widget)

    def setSpacing(self, spaceInt):
        self.widget().layout().setSpacing(spaceInt)

    def setMargin(self, margin):
        if type(margin) == type(0):
            self.widget().layout().setContentsMargins(margin, margin, margin, margin)
        elif type(margin) == type([]) and len(margin) == 4:
            self.widget().layout().setContentsMargins(*margin)

    def addItem(self, title, widget, collapsed = False):
        self.setUpdatesEnabled(False)
        item = self.itemClass()(self, title, widget)
        item.setRolloutStyle(self.rolloutStyle())
        item.setDragDropMode(self.dragDropMode())
        layout = self.widget().layout()
        layout.insertWidget(layout.count() - 1, item)
        layout.setStretchFactor(item, 0)
        if collapsed:
            item.setCollapsed(collapsed)
        self.setUpdatesEnabled(True)
        return item

    def clear(self):
        self.setUpdatesEnabled(False)
        layout = self.widget().layout()
        while layout.count() > 1:
            item = layout.itemAt(0)
            w = item.widget()
            layout.removeItem(item)
            w.close()
            w.deleteLater()

        self.setUpdatesEnabled(True)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
            return True
        if event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
            return True
        if event.type() == QEvent.MouseButtonRelease:
            self.mouseReleaseEvent(event)
            return True
        return False

    def canScroll(self):
        return self.verticalScrollBar().maximum() > 0

    def count(self):
        return self.widget().layout().count() - 1

    def dragDropMode(self):
        return self._dragDropMode

    def indexOf(self, widget):
        layout = self.widget().layout()
        for index in xrange(layout.count()):
            if layout.itemAt(index).widget().widget() == widget:
                return index

        return -1

    def isBoxedMode(self):
        return self._rolloutStyle == AccordionWidget.Boxed

    def itemClass(self):
        return self._itemClass

    def itemAt(self, index):
        layout = self.widget().layout()
        if 0 <= index and index < layout.count() - 1:
            return layout.itemAt(index).widget()
        else:
            return None

    def emitItemCollapsed(self, item):
        if not self.signalsBlocked():
            self.itemCollapsed.emit(item)

    def emitItemDragFailed(self, item):
        if not self.signalsBlocked():
            self.itemDragFailed.emit(item)

    def emitItemMenuRequested(self, item):
        if not self.signalsBlocked():
            self.itemMenuRequested.emit(item)

    def emitItemsReordered(self):
        if not self.signalsBlocked():
            self.itemsReordered.emit()

    def mouseMoveEvent(self, event):
        if self._scrolling:
            sbar = self.verticalScrollBar()
            smax = sbar.maximum()
            dy = event.globalY() - self._scrollInitY
            dval = smax * (dy / float(sbar.height()))
            sbar.setValue(self._scrollInitVal - dval)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.canScroll():
            self._scrolling = True
            self._scrollInitY = event.globalY()
            self._scrollInitVal = self.verticalScrollBar().value()
            self.setCursor(Qt.ClosedHandCursor)
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._scrolling:
            self.setCursor(Qt.ArrowCursor)
        self._scrolling = False
        self._scrollInitY = 0
        self._scrollInitVal = 0
        event.accept()

    def moveItemDown(self, index):
        layout = self.widget().layout()
        if layout.count() - 1 > index + 1:
            widget = layout.takeAt(index).widget()
            layout.insertWidget(index + 1, widget)

    def moveItemUp(self, index):
        if index > 0:
            layout = self.widget().layout()
            widget = layout.takeAt(index).widget()
            layout.insertWidget(index - 1, widget)

    def setBoxedMode(self, state):
        if state:
            self._rolloutStyle = AccordionWidget.Boxed
        else:
            self._rolloutStyle = AccordionWidget.Rounded

    def setDragDropMode(self, dragDropMode):
        self._dragDropMode = dragDropMode
        for item in self.findChildren(AccordionItem):
            item.setDragDropMode(self._dragDropMode)

    def setItemClass(self, itemClass):
        self._itemClass = itemClass

    def setRolloutStyle(self, rolloutStyle):
        self._rolloutStyle = rolloutStyle
        for item in self.findChildren(AccordionItem):
            item.setRolloutStyle(self._rolloutStyle)

    def rolloutStyle(self):
        return self._rolloutStyle

    def takeAt(self, index):
        self.setUpdatesEnabled(False)
        layout = self.widget().layout()
        widget = None
        if 0 <= index and index < layout.count() - 1:
            item = layout.itemAt(index)
            widget = item.widget()
            layout.removeItem(item)
            widget.close()
        self.setUpdatesEnabled(True)
        return widget

    def widgetAt(self, index):
        item = self.itemAt(index)
        if item:
            return item.widget()
        else:
            return None

    pyBoxedMode = Property('bool', isBoxedMode, setBoxedMode)