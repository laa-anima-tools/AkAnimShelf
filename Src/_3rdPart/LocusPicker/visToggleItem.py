# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\visToggleItem.py
try:
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QColor, QIcon, QPainter, QPen
    from PySide2.QtWidgets import QMenu, QGraphicsItem, QLineEdit
except:
    from PySide.QtCore import Qt
    from PySide.QtGui import QColor, QMenu, QIcon, QGraphicsItem, QPainter, QPen, QLineEdit

from functools import partial
from dropPathItem import PathDropItem, PathEditableDropItem
from const import SELECTED_BORDER_COLOR, MIME_COLOR, MIME_COLOR_MODIFIER, MIME_LABEL, MIME_CUSTOM_LABEL
from decorator import timestamp

class ToggleState(object):

    def __init__(self, name, state = False, color = QColor(Qt.red), targets = None, cmd = ''):
        if targets is None:
            targets = []
        self.__name = name
        self.__state = state
        self.__color = color
        self.__targets = targets[:]
        self.__cmd = cmd
        return

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        self.__state = state

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, color):
        self.__color = color

    @property
    def targets(self):
        return self.__targets

    @targets.setter
    def targets(self, targets):
        self.__targets[:] = targets

    @property
    def cmd(self):
        return self.__cmd

    @cmd.setter
    def cmd(self, cmd):
        self.__cmd = cmd


class VisToggleItem(PathDropItem):

    def __init__(self, path, color = QColor(Qt.red), states = None, parent = None):
        PathDropItem.__init__(self, path, color, parent=parent)
        if states is None:
            states = {0: ToggleState('IK', True),
             1: ToggleState('FK')}
        self.__states = {}
        self.states = states
        return

    @property
    def states(self):
        return self.__states

    @states.setter
    def states(self, states):
        self.__states = states
        for value in states.values():
            for item in value.targets:
                item.setVisible(value.state)

    def type(self):
        from const import DropItemType
        return DropItemType.VisToggle

    def createCustomContextMenu(self, event):
        menu = QMenu()
        items = sorted(self.states.items(), key=lambda x: x[0])
        for i, st in items:
            stateMenu = menu.addMenu(st.name)
            stateMenu.setIcon(st.state and QIcon(':/checkboxOn.png') or QIcon(':/checkboxOff.png'))
            showStateAct = stateMenu.addAction('Show')
            showStateAct.triggered.connect(partial(self.toggleVisibility, i))
            selectButtonAct = stateMenu.addAction('Select Containing Buttons')
            selectButtonAct.triggered.connect(partial(self.selectButtons, i))

        return menu

    def toggleVisibility(self, index, ignoreCommand = False):
        for k, st in self.states.items():
            if k == index:
                st.state = True
                for item in st.targets:
                    item.setVisible(True)

                if index == 0:
                    prevIndex = len(self.states) - 1
                else:
                    prevIndex = index - 1
                if not ignoreCommand and self.states[prevIndex].cmd:
                    self.emitCommmand('EXEC ' + self.states[prevIndex].cmd)
            else:
                st.state = False
                for item in st.targets:
                    item.setVisible(False)

    def selectButtons(self, index):
        for i, item in enumerate(self.states[index].targets):
            item.setSelected(True, bool(i))

    def getCurrentIndex(self):
        currentState = [ x for x in self.states.items() if x[1].state ][0]
        return currentState[0]

    def timeoutCalled(self):
        button = self.timer.button
        modifier = self.timer.modifier
        if button == Qt.LeftButton and modifier == Qt.NoModifier:
            currentStateIndex = self.getCurrentIndex()
            if currentStateIndex < len(self.states) - 1:
                nextIndex = currentStateIndex + 1
            else:
                nextIndex = 0
            self.toggleVisibility(nextIndex)

    def paint(self, painter, option, widget = None):
        painter.setClipRect(option.exposedRect.adjusted(-1, -1, 1, 1))
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        painter.setPen(self.isSelected() and QPen(SELECTED_BORDER_COLOR, 1.5, j=Qt.RoundJoin) or Qt.NoPen)
        index = self.getCurrentIndex()
        color = self.states[index].color
        painter.setBrush(self.isSelected() and color.lighter(105) or color)
        boundingRect = self.boundingRect().normalized()
        drawPath = self.path.translated(boundingRect.x(), boundingRect.y())
        painter.drawPath(drawPath)
        text = self.states[index].name
        painter.setPen(self.fontColor)
        painter.drawText(self.boundingRect(), Qt.AlignCenter, text)


class VisToggleEditableItem(PathEditableDropItem, VisToggleItem):

    def __init__(self, path, color = QColor(Qt.red), states = None, parent = None):
        PathEditableDropItem.__init__(self, path, color, parent=parent)
        if states is None:
            states = {0: ToggleState('IK', True),
             1: ToggleState('FK')}
        self.__states = {}
        self.states = states
        self.comm.aboutToRemove.connect(self.clearButtons)
        return

    @property
    def states(self):
        return self.__states

    @states.setter
    def states(self, states):
        self.__states = states
        for value in states.values():
            for item in value.targets:
                item.setVisible(value.state)

    def type(self):
        from const import DropItemType
        return DropItemType.EditableVisToggle

    def createCustomContextMenu(self, event):
        menu = QMenu()
        addStateAct = menu.addAction('New State')
        addStateAct.setEnabled(False)
        items = sorted(self.states.items(), key=lambda x: x[0])
        for i, st in items:
            stateMenu = menu.addMenu(st.name or '[STATE-%d]' % i)
            stateMenu.setIcon(st.state and QIcon(':/checkboxOn.png') or QIcon(':/checkboxOff.png'))
            showStateAct = stateMenu.addAction('Show')
            showStateAct.triggered.connect(partial(self.toggleVisibility, i))
            addButtonAct = stateMenu.addAction('Add Selected Buttons')
            addButtonAct.triggered.connect(partial(self.addButtonsToState, i))
            selectButtonAct = stateMenu.addAction('Select Containing Buttons')
            selectButtonAct.triggered.connect(partial(self.selectButtons, i))
            emptyButtonAct = stateMenu.addAction('Empty State')
            emptyButtonAct.triggered.connect(partial(self.emptyButtons, i))

        return menu

    def addButtonsToState(self, index):
        scene = self.scene()
        add = False
        for item in [ x for x in scene.selectedItems() if x != self ]:
            if item not in self.states[index].targets:
                self.states[index].targets.append(item)
                item.setVisible(self.states[index].state)
                if not add:
                    add = True

        if add:
            self.comm.itemChanged.emit('target')

    def clearButtons(self):
        for x in self.states.keys():
            self.emptyButtons(x)

    def emptyButtons(self, index):
        if self.states[index].targets:
            for item in self.states[index].targets:
                item.setVisible(True)

            self.states[index].targets = []
            self.comm.itemChanged.emit('target')

    def editCommand(self, script):
        index = self.getCurrentIndex()
        print 'editCommand', index, script
        self.states[index].cmd = script

    def timeoutCalled(self):
        button = self.timer.button
        modifier = self.timer.modifier
        if self.editable and button == Qt.LeftButton and (modifier == Qt.AltModifier | Qt.ShiftModifier or modifier == Qt.AltModifier | Qt.ControlModifier):
            PathEditableDropItem.timeoutCalled(self)
        else:
            VisToggleItem.timeoutCalled(self)

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasFormat(MIME_COLOR_MODIFIER) or mimeData.hasFormat(MIME_COLOR):
            if self.contains(event.pos()):
                colorData = event.mimeData().colorData()
                self.states[self.getCurrentIndex()].color = colorData
                self.update()
                self.comm.itemChanged.emit('color')
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
                else:
                    text = unicode(mimeData.data(MIME_CUSTOM_LABEL)).strip()
                self.states[self.getCurrentIndex()].name = text
                self.update()
                self.comm.itemChanged.emit('label')
        else:
            PathEditableDropItem.dropEvent(self, event)