# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\editableTab.py
try:
    from PySide2.QtCore import Signal, Qt, QEvent, QRect, QPoint, QSize, QPointF, QObject
    from PySide2.QtGui import QPainter, QPixmap, QColor, QPalette, QHelpEvent, QRegExpValidator, QIcon, QCursor, QPainterPath, QPen
    from PySide2.QtWidgets import QTabBar, QLineEdit, QTabWidget, QWidget, QHBoxLayout, QMenu, QToolTip, QGraphicsScene
except:
    from PySide.QtCore import Signal, Qt, QEvent, QRect, QPoint, QSize, QPointF, QObject
    from PySide.QtGui import QTabBar, QLineEdit, QTabWidget, QWidget, QHBoxLayout, QPainter, QPixmap, QColor, QPalette, QMenu, QHelpEvent, QToolTip, QRegExpValidator, QGraphicsScene, QIcon, QCursor, QPainterPath, QPen

import sys
from dropView import DropView
from dropScene import DropScene, EditableDropScene
from dropItem import AbstractDropItem
from decorator import accepts, returns, timestamp
from const import getNumericName, LocaleText, nameRegExp, warn, question, DEF_MAPNAME, TEAROFF_TIP
from locusPickerResources import *
try:
    import maya.cmds as mc
    INMAYA = int(mc.about(v=True))
except:
    INMAYA = 0

def getSignals(classObj):
    result = [ x for x in vars(classObj).iteritems() if isinstance(x[1], Signal) ]
    if classObj.__base__ and classObj.__base__ != QObject:
        result.extend(getSignals(classObj.__base__))
    return result


class TearoffTabBar(QTabBar):
    saveToFile = Signal(int)
    selectMapNode = Signal(int)
    tearOff = Signal(int, QPoint)

    def __init__(self, parent = None):
        QTabBar.__init__(self, parent)
        self.setCursor(Qt.ArrowCursor)
        self.setMouseTracking(True)
        self.setMovable(True)
        self.setIconSize(QSize(12, 12))
        self.__pressedIndex = -1

    def mousePressEvent(self, event):
        button = event.button()
        modifier = event.modifiers()
        if not (button == Qt.LeftButton and (modifier == Qt.NoModifier or modifier == Qt.ControlModifier)):
            return
        if modifier == Qt.ControlModifier:
            pos = event.pos()
            self.__pressedIndex = self.tabAt(pos)
            rect = self.tabRect(self.__pressedIndex)
            pixmap = QPixmap.grabWidget(self, rect)
            painter = QPainter(pixmap)
            cursorPm = QPixmap(':/closedHand')
            cursorPos = QPoint(*[ (x - y) / 2 for x, y in zip(rect.size().toTuple(), QSize(32, 24).toTuple()) ])
            painter.drawPixmap(cursorPos, cursorPm)
            painter.end()
            cursor = QCursor(pixmap)
            self.setCursor(cursor)
        QTabBar.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.__pressedIndex > -1:
            pass
        else:
            if event.modifiers() == Qt.ControlModifier:
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            QTabBar.mouseMoveEvent(self, event)

    def enterEvent(self, event):
        self.grabKeyboard()
        QTabBar.enterEvent(self, event)

    def leaveEvent(self, event):
        self.releaseKeyboard()
        QTabBar.leaveEvent(self, event)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            self.setCursor(Qt.OpenHandCursor)
        QTabBar.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if self.cursor().shape() != Qt.ArrowCursor:
            self.setCursor(Qt.ArrowCursor)
        QTabBar.keyReleaseEvent(self, event)

    def event(self, event):
        if event.type() == QEvent.MouseButtonRelease:
            if self.__pressedIndex > -1:
                self.tearOff.emit(self.__pressedIndex, event.globalPos())
                self.__pressedIndex = -1
                self.setCursor(Qt.ArrowCursor)
        return QTabBar.event(self, event)


class EditableTabBar(TearoffTabBar):
    tabLabelRenamed = Signal(unicode, unicode)
    requestRemove = Signal(int)
    tabChanged = Signal(int)

    def __init__(self, parent = None):
        TearoffTabBar.__init__(self, parent)
        self.__editor = QLineEdit(self)
        self.__editor.setWindowFlags(Qt.Popup)
        self.__editor.setFocusProxy(self)
        self.__editor.setFocusPolicy(Qt.StrongFocus)
        self.__editor.editingFinished.connect(self.handleEditingFinished)
        self.__editor.installEventFilter(self)
        self.__editor.setValidator(QRegExpValidator(nameRegExp))
        self.__editIndex = -1

    def eventFilter(self, widget, event):
        if event.type() == QEvent.MouseButtonPress and not self.__editor.geometry().contains(event.globalPos()) or event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.__editor.hide()
            return False
        return QTabBar.eventFilter(self, widget, event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self.tabAt(event.pos())
            if index >= 0:
                self.selectMapNode.emit(index)

    def editTab(self, index):
        rect = self.tabRect(index)
        self.__editor.setFixedSize(rect.size())
        self.__editor.move(self.parent().mapToGlobal(rect.topLeft()))
        self.__editor.setText(self.tabText(index))
        if not self.__editor.isVisible():
            self.__editor.show()
            self.__editIndex = index

    def handleEditingFinished(self):
        if self.__editIndex >= 0:
            self.__editor.hide()
            oldText = self.tabText(self.__editIndex)
            newText = self.__editor.text()
            if oldText != newText:
                names = [ self.tabText(i) for i in xrange(self.count()) ]
                newText = getNumericName(newText, names)
                self.setTabText(self.__editIndex, newText)
                self.tabLabelRenamed.emit(oldText, newText)
                self.__editIndex = -1

    def contextMenuEvent(self, event):
        index = self.tabAt(event.pos())
        if index == self.currentIndex():
            menu = QMenu()
            saveToFileAct = menu.addAction('Save [%s] to File' % self.tabText(index))
            saveToFileAct.triggered.connect(lambda : self.saveToFile.emit(index))
            parent = self.parent()
            if parent and parent.sceneAtIndex(index).editable:
                renameTabNameAct = menu.addAction('Rename')
                renameTabNameAct.triggered.connect(lambda : self.editTab(index))
                removeTabAct = menu.addAction('Delete Map')
                removeTabAct.triggered.connect(lambda : self.requestRemove.emit(index))
            menu.exec_(event.globalPos())


class TabWidget(QTabWidget):
    tabAdded = Signal()
    sendCommandData = Signal(unicode, list, list, list, unicode, QGraphicsScene)
    redefineMember = Signal(AbstractDropItem)
    changeMember = Signal(AbstractDropItem, unicode, bool, unicode)
    editRemote = Signal(AbstractDropItem)
    undoOpen = Signal()
    undoClose = Signal()
    poseGlobalVarSet = Signal(AbstractDropItem)
    poseGlobalVarUnset = Signal(AbstractDropItem)
    saveToFile = Signal(int)
    selectMapNode = Signal(int)
    tearOff = Signal(int, QPoint)

    def __init__(self, parent = None):
        super(TabWidget, self).__init__(parent)
        self.setTabsClosable(False)
        self.setMouseTracking(True)
        self.setObjectName('TabWidget')
        self.getPaletteColor()
        self.setCustomTabBar()

    def setCustomTabBar(self):
        tabBar = TearoffTabBar(self)
        self.setTabBar(tabBar)
        tabBar.saveToFile.connect(self.saveToFile.emit)
        tabBar.selectMapNode.connect(self.selectMapNode.emit)
        tabBar.tearOff.connect(self.tearOff.emit)

    def getPaletteColor(self):
        palette = self.palette()
        self.borderC = QColor(Qt.black)
        self.buttonC = palette.color(QPalette.Window)
        self.fillC = palette.color(QPalette.Button)
        self.hiliteC = palette.color(QPalette.Highlight)
        self.baseC = palette.color(QPalette.Midlight)
        self.baseBorderC = palette.color(QPalette.Dark)
        self.baseButtonC = palette.color(QPalette.Mid)

    def addGraphicsTab(self, text = DEF_MAPNAME, changeCurrent = True):
        names = [ self.tabText(i) for i in xrange(self.count()) ]
        text = getNumericName(text, names)
        tab = QWidget()
        tab.prefix = ''
        tab.usePrefix = False
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(3, 3, 3, 3)
        if changeCurrent:
            index = self.currentIndex()
            index = self.insertTab(index + 1, tab, text)
            self.setCurrentIndex(index)
        else:
            index = self.count()
            index = self.insertTab(index, tab, text)
        self.setTabToolTip(index, 'Map : %s\n' % text + TEAROFF_TIP)
        view = DropView(tab)
        view.installEventFilter(self)
        if isinstance(self, EditableTabWidget):
            scene = EditableDropScene()
        else:
            scene = DropScene()
        view.setScene(scene)
        layout.addWidget(view)
        if changeCurrent:
            self.tabAdded.emit()
        for signalName in [ d[0] for d in getSignals(scene.__class__) ]:
            if hasattr(self, signalName):
                eval('scene.%(SIGNAL)s.connect(self.%(SIGNAL)s.emit)' % {'SIGNAL': signalName})

        if isinstance(self, EditableTabWidget):
            scene.sceneChanged.connect(self.windowModified.emit)
        return tab

    def addView(self, text, index, view, prefix, usePrefix):
        tab = QWidget()
        tab.prefix = prefix
        tab.usePrefix = usePrefix
        index = self.insertTab(index, tab, text)
        self.setCurrentIndex(index)
        self.setTabToolTip(index, 'Map : %s\n' % text + TEAROFF_TIP)
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.addWidget(view)
        scene = view.scene()
        if hasattr(scene, 'editable') and not scene.editable:
            self.setTabIcon(index, QIcon(':/locked'))

    def clear(self):
        allTabs = [ self.widget(i) for i in xrange(self.count()) ]
        self.blockSignals(True)
        for tab in allTabs:
            tab.deleteLater()

        QTabWidget.clear(self)
        self.blockSignals(False)

    def currentView(self):
        if self.currentWidget():
            return self.currentWidget().findChild(DropView)
        else:
            return None
            return None

    def currentScene(self):
        view = self.currentView()
        if view:
            return view.scene()
        else:
            return None
            return None

    def viewAtIndex(self, index):
        if self.widget(index):
            return self.widget(index).findChild(DropView)
        else:
            return None
            return None

    def sceneAtIndex(self, index):
        view = self.viewAtIndex(index)
        if view:
            return view.scene()
        else:
            return None
            return None

    def allViews(self):
        views = []
        for i in xrange(self.count()):
            view = self.widget(i).findChild(DropView)
            if view:
                views.append(view)

        return views

    def dragEnterEvent(self, event):
        event.accept()
        QTabWidget.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        event.accept()
        QTabWidget.dragMoveEvent(self, event)


class EditableTabWidget(TabWidget):
    tabSizeChange = Signal(QSize)
    tabLabelRenamed = Signal(unicode, unicode)
    tabRemovedText = Signal(unicode)
    windowModified = Signal()
    addItemOn = Signal(QPointF, QColor, int)
    addItemWithSet = Signal(QPointF, QColor, unicode, dict)
    addPreviewedItem = Signal(QPointF, QColor, unicode, dict)
    copyItems = Signal(list)
    selectedItemsChanged = Signal(list)

    def __init__(self, parent = None):
        TabWidget.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setObjectName('EditableTabWidget')
        palette = self.palette()
        palette.setColor(QPalette.Midlight, QColor(0, 0, 0, 0))
        self.setPalette(palette)
        self.__editable = True
        self.__hilite = False
        self.__hoverTab = -1

    @property
    @returns(bool)
    def editable(self):
        return self.__editable

    @editable.setter
    @accepts(bool)
    def editable(self, editable):
        self.__editable = editable
        self.setMovable(editable)
        for view in self.allViews():
            view.scene().setAllItemsEditable(editable)

        self.update()

    def toggleEditable(self):
        self.editable = not self.editable

    @property
    @returns(bool)
    def hilite(self):
        return self.__hilite

    @hilite.setter
    @accepts(bool)
    def hilite(self, hilite):
        if self.__hilite != hilite:
            self.__hilite = hilite
            self.setCursor(self.__hilite and Qt.PointingHandCursor or Qt.ArrowCursor)
            self.update()

    @property
    @returns(int)
    def hoverTab(self):
        return self.__hoverTab

    @hoverTab.setter
    @accepts(int)
    def hoverTab(self, index):
        if self.__hoverTab != index:
            self.__hoverTab = index
            self.update()

    def setCustomTabBar(self):
        tabBar = EditableTabBar(self)
        self.setTabBar(tabBar)
        tabBar.tabMoved.connect(lambda : self.windowModified.emit())
        tabBar.tabLabelRenamed.connect(lambda : self.windowModified.emit())
        tabBar.tabLabelRenamed.connect(self.tabLabelRenamed.emit)
        tabBar.saveToFile.connect(self.saveToFile.emit)
        tabBar.selectMapNode.connect(self.selectMapNode.emit)
        tabBar.requestRemove.connect(self.eliminateTab)
        tabBar.tearOff.connect(self.tearOff.emit)

    def eventFilter(self, widget, event):
        if isinstance(widget, DropView):
            if event.type() == QEvent.Enter:
                self.hilite = False
        return QTabWidget.eventFilter(self, widget, event)

    def eliminateTab(self, index):
        if index < 0:
            return
        widget = self.widget(index)
        scene = self.sceneAtIndex(index)
        if scene.items():
            localeText = LocaleText(self.locale())
            if not question(localeText('HasItemMessage'), localeText('HasItemTitle'), self):
                return
        tabText = self.tabText(index)
        super(EditableTabWidget, self).removeTab(index)
        widget.deleteLater()
        self.windowModified.emit()
        self.tabRemovedText.emit(tabText)

    def mousePressEvent(self, event):
        pos = event.pos()
        rect = self.buttonRect()
        if rect.contains(pos) and self.editable and event.button() == Qt.LeftButton and event.modifiers() == Qt.NoModifier:
            index = self.indexOf(self.addGraphicsTab())
            scene = self.sceneAtIndex(index)
            scene.mapSize = QSize(400, 400)
            self.tabBar().editTab(index)
        else:
            QTabWidget.mousePressEvent(self, event)

    def event(self, event):
        if isinstance(event, QHelpEvent):
            pos = event.pos()
            rect = self.buttonRect()
            if rect.contains(pos):
                QToolTip.showText(event.globalPos(), 'Add Map:\nClick this to add a new map')
            else:
                QToolTip.hideText()
        return QTabWidget.event(self, event)

    def paintEvent(self, event):
        rect = self.buttonRect()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.editable:
            painter.setPen(QPen(self.baseBorderC, 0.1))
            painter.setBrush(self.__hilite and self.baseButtonC.lighter(115) or self.baseButtonC)
            painter.drawPath(self.buttonPath(rect))
            crossHair = QRect(0, 0, 7, 7)
            crossHair.moveCenter(rect.center() + QPoint(1, 1))
            painter.setPen(QPen(self.__hilite and Qt.white or Qt.lightGray, 2, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(QPoint(crossHair.center().x(), crossHair.top()), QPoint(crossHair.center().x(), crossHair.bottom()))
            painter.drawLine(QPoint(crossHair.left(), crossHair.center().y()), QPoint(crossHair.right(), crossHair.center().y()))
        if self.count():
            painter.setPen(Qt.NoPen)
            currentIndex = self.currentIndex()
            for i in xrange(self.count()):
                brush = currentIndex == i and self.baseC.darker(120) or self.baseC
                painter.setBrush(self.__hoverTab == i and brush.lighter(110) or brush)
                rect = self.tabBar().tabRect(i).adjusted(*(currentIndex == i and (0, 1, 0, 0) or (1, 2, -1, 0)))
                path = self.buttonPath(rect)
                painter.drawPath(path)

            QTabWidget.paintEvent(self, event)
        elif self.editable:
            r = event.rect()
            r.setTop(rect.bottom())
            painter.setPen(self.borderC)
            painter.setBrush(self.fillC)
            painter.drawRoundedRect(r, 2, 2)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.buttonRect().contains(pos):
            self.hilite = True
            self.hoverTab = -1
        else:
            self.hilite = False
            for i in xrange(self.count()):
                if self.tabBar().tabRect(i).contains(pos):
                    self.hoverTab = i
                    break

        QTabWidget.mouseMoveEvent(self, event)

    def leaveEvent(self, event):
        self.hoverTab = -1
        QTabWidget.leaveEvent(self, event)

    def buttonRect(self):
        r = self.tabBar().tabRect(self.count() - 1)
        if r.isValid():
            rect = QRect(0, 0, 30, r.height())
            rect.moveTopLeft(r.topRight() + QPoint(2, 2))
        else:
            rect = QRect(2, 2, 30, 19)
        return rect

    def buttonPath(self, rect):
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, 2, 2)
        path.addRect(rect.adjusted(0, 4, 0, 0))
        return path.simplified()

    def dropEvent(self, event):
        if not self.count():
            warn('To create item, have to create a map first.', 'No map', self)


if __name__ == '__main__':
    from PySide.QtGui import QApplication
    app = QApplication(sys.argv)
    w = EditableTabWidget()
    w.show()
    sys.exit(app.exec_())