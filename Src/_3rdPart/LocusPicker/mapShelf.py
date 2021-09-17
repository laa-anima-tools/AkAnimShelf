# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\mapShelf.py
try:
    from PySide2.QtCore import QSize, Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QRect, QEvent
    from PySide2.QtGui import QPainter, QPalette, QColor, QPen, QPainterPath, QTextCursor
    from PySide2.QtWidgets import QListWidget, QStyledItemDelegate, QMenu, QGraphicsOpacityEffect, QScrollBar, QLineEdit, QPlainTextEdit, QStyle
except:
    from PySide.QtCore import QSize, Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QRect, QEvent
    from PySide.QtGui import QListWidget, QStyledItemDelegate, QPainter, QStyle, QMenu, QGraphicsOpacityEffect, QScrollBar, QPalette, QColor, QPen, QPainterPath, QLineEdit, QPlainTextEdit, QTextCursor

SCROLL_WAITING_TIME = 1500
SCROLL_THICKNESS = 12
SCROLL_STYLESHEET = '\nQScrollBar:horizontal {\n    border: 0px solid black;\n    border-radius: 3px;\n    background-color: rgba(24, 32, 48, 64);\n    margin: 0px 20px 0px 20px;\n    max-height: 18px;\n}\n\nQScrollBar:vertical {\n    border: 0px solid black;\n    border-radius: 3px;\n    background-color: rgba(134, 154, 191, 64);\n    margin: 20px 0px 20px 0px;\n    max-width: 18px;\n}\n\nQScrollBar::handle:horizontal {\n    border: 0px solid black;\n    border-radius: 3px;\n    background-color: rgba(82, 88, 102, 180);\n    min-width: 15px;\n}\n\nQScrollBar::handle:vertical {\n    border: 0px solid black;\n    border-radius: 3px;\n    background-color: rgba(137, 171, 227, 180);\n    min-height: 15px;\n}\n\nQScrollBar::add-line:horizontal {\n    border: 0px solid black;\n    border-radius: 3px;\n    background-color: rgba(24, 32, 48, 210);\n    width: 16px;\n    margin: 0px;\n    subcontrol-position: right;\n    subcontrol-origin: margin;\n}\n\nQScrollBar::add-line:vertical {\n    border: 0px solid black;\n    border-radius: 3px;\n    background-color: rgba(134, 154, 191, 210);\n    height: 16px;\n    margin: 0px;\n    subcontrol-position: bottom;\n    subcontrol-origin: margin;\n}\n\nQScrollBar::add-line:hover {\n    background-color: rgba(146, 168, 209, 240);\n}\n\nQScrollBar::sub-line:horizontal {\n    border: 0px solid black;\n    border-radius: 3px;\n    background-color: rgba(24, 32, 48, 210);\n    width: 16px;\n    margin: 0px;\n    subcontrol-position: left;\n    subcontrol-origin: margin;\n}\n\nQScrollBar::sub-line:vertical {\n    border: 0px solid black;\n    border-radius: 3px;\n    background-color: rgba(134, 154, 191, 210);\n    height: 16px;\n    margin: 0px;\n    subcontrol-position: top;\n    subcontrol-origin: margin;\n}\n\nQScrollBar::sub-line:hover {\n    background-color: rgba(146, 168, 209, 240);\n}\n\nQScrollBar::left-arrow {\n    border: 0px solid black;\n    width: 8px;\n    height: 8px;\n    background-image: url(":/left");\n}\n\nQScrollBar::right-arrow {\n    border: 0px solid black;\n    width: 8px;\n    height: 8px;\n    background-image: url(":/right");\n}\n\nQScrollBar::up-arrow {\n    border: 0px solid black;\n    width: 8px;\n    height: 8px;\n    background-image: url(":/up");\n}\n\nQScrollBar::down-arrow {\n    border: 0px solid black;\n    width: 8px;\n    height: 8px;\n    background-image: url(":/down");\n}\n\nQScrollBar::add-page, QScrollBar::sub-page {\n    background-color: transparent;\n}\n'

class EditorStyle:
    LineEdit = 0
    TextEdit = 1


class ShelfListWidget(QListWidget):
    GRID_SIZE = QSize(48, 32)
    SPACING = 2
    selected = Signal(unicode)
    rename = Signal(unicode, unicode)
    remove = Signal(unicode)
    reorder = Signal()

    def __init__(self, editorStyle = EditorStyle.LineEdit, parent = None):
        QListWidget.__init__(self, parent)
        self.setItemDelegate(ShelfItemDelegate(self))
        self.setFixedHeight(32)
        self.setFrameStyle(QListWidget.NoFrame)
        self.setFlow(QListWidget.LeftToRight)
        self.setEditTriggers(QListWidget.NoEditTriggers)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setMouseTracking(True)
        self.setWrapping(False)
        self.setStyleSheet(SCROLL_STYLESHEET)
        self.setGridSize(self.GRID_SIZE + QSize(self.SPACING, 0))
        self.focused = False
        self.pressedIndex = None
        self.__currentItems = None
        self.__editorStyle = editorStyle
        self.setEditor()
        self.setAnimatableScroll()
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor(0, 0, 0, 0))
        self.setPalette(palette)
        return

    def enterEvent(self, event):
        QListWidget.enterEvent(self, event)
        self.focused = True
        self.viewport().update()

    def leaveEvent(self, event):
        QListWidget.leaveEvent(self, event)
        self.focused = False
        self.viewport().update()

    def mousePressEvent(self, event):
        QListWidget.mousePressEvent(self, event)
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos())
            if index.row() > -1:
                self.pressedIndex = index
                self.viewport().update()

    def mouseReleaseEvent(self, event):
        QListWidget.mouseReleaseEvent(self, event)
        if event.button() == Qt.LeftButton:
            if self.pressedIndex == self.indexAt(event.pos()):
                self.selected.emit(self.itemAt(event.pos()).data(Qt.UserRole))
            self.pressedIndex = None
            self.viewport().update()
        return

    def startDrag(self, supportedActions):
        self.pressedIndex = None
        self.viewport().update()
        self.__currentItems = [ self.item(i) for i in xrange(self.count()) ]
        QListWidget.startDrag(self, supportedActions)
        return

    def dropEvent(self, event):
        QListWidget.dropEvent(self, event)
        if event.source() == self and event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            for i in xrange(self.count()):
                if self.__currentItems[i].__repr__() != self.item(i).__repr__():
                    self.reorder.emit()
                    break

        self.__currentItems = None
        return

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        item = self.itemAt(event.pos())
        menu.addAction('Rename').triggered.connect(lambda : self.showItemRenamePopup(item))
        menu.addAction('Remove').triggered.connect(lambda : self.eliminateItem(item))
        menu.exec_(event.globalPos())

    def setEditor(self):
        if bool(self.__editorStyle & EditorStyle.TextEdit):
            self.__editor = QPlainTextEdit(self)
            self.__editor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.__editor.setStyleSheet('padding: -3px;')
        else:
            self.__editor = QLineEdit(self)
        self.__editor.setWindowFlags(Qt.Popup)
        self.__editor.setFocusPolicy(Qt.StrongFocus)
        if not bool(self.__editorStyle & EditorStyle.TextEdit):
            self.__editor.setFocusProxy(self)
            self.__editor.editingFinished.connect(self.handleEditingFinished)
        self.__editor.installEventFilter(self)
        self.__editItem = None
        return

    def eventFilter(self, widget, event):
        eventType = event.type()
        if eventType == QEvent.MouseButtonPress and not self.__editor.geometry().contains(event.globalPos()) or eventType == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.__editor.hide()
            return False
        if hasattr(self, '_ShelfListWidget__editorStyle') and bool(self.__editorStyle & EditorStyle.TextEdit) and eventType == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Tab or key == Qt.Key_Enter or key == Qt.Key_Return:
                self.handleEditingFinished()
                return False
        return QListWidget.eventFilter(self, widget, event)

    def showItemRenamePopup(self, item):
        rect = self.visualItemRect(item)
        self.__editor.setFixedSize(rect.size())
        self.__editor.move(self.mapToGlobal(rect.topLeft()))
        if bool(self.__editorStyle & EditorStyle.TextEdit):
            self.__editor.setPlainText('\n'.join(item.text().split(' ')))
            self.__editor.moveCursor(QTextCursor.Start)
        else:
            self.__editor.setText(item.text())
        if not self.__editor.isVisible():
            self.__editor.show()
            self.__editItem = item

    def handleEditingFinished(self):
        if self.__editItem:
            self.__editor.hide()
            oldText = self.__editItem.text()
            if bool(self.__editorStyle & EditorStyle.TextEdit):
                newText = ' '.join(self.__editor.toPlainText().split())
            else:
                newText = self.__editor.text()
            if oldText != newText:
                self.__editItem.setText(newText)
                self.rename.emit(self.__editItem.data(Qt.UserRole), newText)
                self.__editItem = None
        return

    def eliminateItem(self, item):
        self.takeItem(self.row(item))
        self.remove.emit(item.data(Qt.UserRole))

    def setAnimatableScroll(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.createScrollTimer()
        self.createScrollAnimation()
        self.createScrollEffect()
        self.createAnimatableScroll()
        self.AnimatingScroll = True

    def createScrollTimer(self):
        self.timer = QTimer()
        self.timer.setSingleShot(SCROLL_WAITING_TIME)
        self.timer.timeout.connect(self.hideScroll)

    def createScrollAnimation(self):
        self.setProperty('scrollOpacity', float)
        self.scrollAnim = QPropertyAnimation(self, 'scrollOpacity')
        self.scrollAnim.setDuration(200)
        self.scrollAnim.setEasingCurve(QEasingCurve.InOutQuad)
        self.scrollAnim.valueChanged.connect(self.setScrollOpacity)

    def createScrollEffect(self):
        self.scrollEffect = QGraphicsOpacityEffect(self)
        self.scrollEffect.setOpacity(0.0)

    def createAnimatableScroll(self):
        scroll = self.horizontalScrollBar()
        self.hscrollBar = QScrollBar(Qt.Horizontal, self)
        self.hscrollBar.setGraphicsEffect(self.scrollEffect)
        self.hscrollBar.actionTriggered.connect(lambda : self.timer.start(SCROLL_WAITING_TIME))
        self.hscrollBar.valueChanged.connect(scroll.setValue)
        self.hscrollBar.hide()
        self.hscrollBar.setCursor(Qt.ArrowCursor)
        scroll.rangeChanged.connect(lambda x, y: self.matchScroll(scroll, x, y))
        scroll.valueChanged.connect(self.hscrollBar.setValue)
        scroll.valueChanged.connect(self.showScroll)

    def showScroll(self):
        if not self.isVisible():
            return
        scroll = self.horizontalScrollBar()
        flag = False
        if scroll.minimum() == scroll.maximum() == 0:
            flag = flag or False
        else:
            flag = flag or True
            self.scrollAnim.setStartValue(self.scrollEffect.opacity())
            self.scrollAnim.setEndValue(1.0)
            self.scrollAnim.start()
        if flag:
            self.timer.start(SCROLL_WAITING_TIME)

    def hideScroll(self):
        self.scrollAnim.setStartValue(self.scrollEffect.opacity())
        self.scrollAnim.setEndValue(0.0)
        self.scrollAnim.start()

    def matchScroll(self, scroll, _min, _max):
        self.hscrollBar.setRange(_min, _max)
        self.hscrollBar.setSingleStep(scroll.singleStep())
        self.hscrollBar.setPageStep(scroll.pageStep())

    def setScrollOpacity(self, value):
        if value != None:
            self.scrollEffect.setOpacity(value)
            if value:
                if self.hscrollBar.isHidden():
                    self.hscrollBar.show()
            else:
                self.hscrollBar.hide()
        return

    def resizeEvent(self, event):
        QListWidget.resizeEvent(self, event)
        if hasattr(self, 'AnimatingScroll') and self.AnimatingScroll:
            w, h = self.width(), self.height()
            self.hscrollBar.setGeometry(QRect(0, h - SCROLL_THICKNESS, w, SCROLL_THICKNESS))

    def wheelEvent(self, event):
        scrollBar = self.horizontalScrollBar()
        if scrollBar.minimum() == scrollBar.maximum() == 0:
            return
        scrollBar.setValue(scrollBar.value() - event.delta() / 6)


class ShelfItemDelegate(QStyledItemDelegate):
    BORDER_COLOR = QColor(25, 25, 25, 220)
    HOVER_COLOR = QColor(145, 168, 208, 177)
    PRESSED_COLOR = QColor(90, 91, 159, 177)
    BASE_COLOR = QColor(109, 109, 109)
    TEXT_COLOR = QColor(240, 240, 240)
    ROUND_RADIUS = 4

    def __init__(self, parent = None):
        QStyledItemDelegate.__init__(self, parent)

    def sizeHint(self, option, index):
        return ShelfListWidget.GRID_SIZE

    def paint(self, painter, option, index):
        view = self.parent()
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(22, 22, 22))
        painter.drawPath(self.getDrawPath(option.rect.adjusted(2, 1, 0, 0)))
        painter.setPen(QPen(self.BORDER_COLOR, 0.5))
        if view.pressedIndex == index:
            painter.setBrush(self.PRESSED_COLOR)
        elif view.focused and bool(option.state & QStyle.State_MouseOver):
            painter.setBrush(self.HOVER_COLOR)
        else:
            painter.setBrush(self.BASE_COLOR)
        rect = option.rect.adjusted(0, 0, -2, 0)
        painter.drawPath(self.getDrawPath(rect))
        painter.setPen(self.TEXT_COLOR)
        text = '\n'.join([ option.fontMetrics.elidedText(x, Qt.ElideRight, ShelfListWidget.GRID_SIZE.width() - 4) for x in index.data().split(' ', 1) ])
        painter.drawText(rect, Qt.AlignCenter, text)

    def getDrawPath(self, rect):
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, self.ROUND_RADIUS, self.ROUND_RADIUS)
        subRect = QRect(0, 0, self.ROUND_RADIUS, self.ROUND_RADIUS)
        subRect.moveBottomLeft(rect.bottomLeft())
        path.addRect(subRect)
        subRect.moveBottomRight(rect.bottomRight())
        path.addRect(subRect)
        return path.simplified()