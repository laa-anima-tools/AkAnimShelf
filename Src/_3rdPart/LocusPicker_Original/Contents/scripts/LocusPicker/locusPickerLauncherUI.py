# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\locusPickerLauncherUI.py


def module_exists(module_name):
    import imp
    try:
        module_info = imp.find_module(module_name)
        module = imp.load_module(module_name, *module_info)
        imp.find_module('__init__', module.__path__)
        hasModule = True
    except:
        hasModule = False

    return hasModule


import os, sys, traceback, time, re, urllib2, ast
from functools import partial
if module_exists('lxml'):
    from lxml.etree import Element, ElementTree, parse, tostring
else:
    from xml.etree.cElementTree import Element, ElementTree, parse, tostring
try:
    from PySide2.QtCore import SIGNAL, Qt, QPointF, QTimer, QSize, QLocale, QSettings, QPoint, QRect
    from PySide2.QtGui import QIcon, QColor, QPixmap, QImage
    from PySide2.QtWidgets import QWidget, QAction, QApplication, QToolButton, QLineEdit, QGridLayout, QCheckBox, QListWidgetItem, QSizePolicy
except:
    from PySide.QtCore import SIGNAL, Qt, QPointF, QTimer, QSize, QLocale, QSettings, QPoint, QRect
    from PySide.QtGui import QWidget, QAction, QIcon, QColor, QApplication, QPixmap, QToolButton, QLineEdit, QImage, QDesktopServices, QGridLayout, QCheckBox, QListWidgetItem, QSizePolicy

from loadUiType import loadUiType
from const import VERSION, MAP_FILE_FILTER, ButtonPosition, affixPrefix, WaitState, warn, error, question, getTypeString, decodeCommandStr, encodeIconStr, decodeIconStr, encodeLabelStr, decodeLabelStr, encodeGroupCommandStr, decodeGroupCommandStr, encodeCommandStr, encodeVisToggleNodeStr, decodeVisToggleNodeStr, encodeVisToggleChannelStr, decodeVisToggleChannelStr, encodeVisToggleColorStr, decodeVisToggleColorStr, MASTER_WINDOW_NAME, USER_WINDOW_NAME, splitCapitalized, getAbsolutePath
from dropItem import DragPoseDropItem, AbstractDropItem
from dropSliderItem import Attachment, RectangleDropSliderItem
from visToggleItem import ToggleState
from groupItem import GroupItem
from arrowToggleButton import ArrowToggleButton, HoverIconButton
from editableTab import TabWidget
from popupLineEdit import PopupLineEdit
from selectGuideDialog import SelectGuideDialog
from idleQueueDispatcher import ThreadDispatcher
from locusPickerResources import *
from decorator import sceneExists, timestamp
from tearOffDialog import TearOffDialog
from mapShelf import ShelfListWidget
uiFile = os.path.join(os.path.dirname(__file__), 'resources', 'launcher.ui')
base_class, form_class = loadUiType(uiFile)
try:
    import maya.cmds as mc
    import maya.mel as mm
    import maya.utils as mu
    import maya.OpenMaya as om
    import maya.OpenMayaUI as omui
    from wrapInstance import wrapinstance, unwrapinstance
    mm.eval('source "%s";' % (os.path.dirname(__file__).replace('\\', '/') + '/locusPicker.mel'))

    def getMayaWindow():
        ptr = omui.MQtUtil.mainWindow()
        return wrapinstance(long(ptr), QWidget)


    def toQtObject(mayaName):
        ptr = omui.MQtUtil.findControl(mayaName)
        if ptr is None:
            ptr = omui.MQtUtil.findLayout(mayaName)
        if ptr is None:
            ptr = omui.MQtUtil.findMenuItem(mayaName)
        if ptr is not None:
            return wrapinstance(long(ptr), QWidget)
        else:
            return


    def toMayaObject(qtObject):
        return omui.MQtUtil.fullName(unwrapinstance(qtObject))


    INMAYA = int(mc.about(v=True))
except:
    INMAYA = 0

PLATFORM_PARENT = INMAYA and getMayaWindow() or None

def complexStringData(listData):
    data = []
    for singleList in listData:
        data.append(','.join([ str(v) for v in singleList ]))

    return ';'.join(data)


def complexListData(stringData):
    data = []
    if not stringData:
        return data
    for singleData in stringData.split(';'):
        data.append([ float(v) for v in singleData.split(',') ])

    return data


def filterPickerNode():
    return [ n for n in mc.ls(type='geometryVarGroup') if mc.objExists(n + '.locusPickerMap') ]


def filterShelfNode():
    return [ n for n in mc.ls(type='dof') if mc.objExists(n + '.bookmarkList') ]


def listToArray(listData):
    listData = [ str(x) for x in listData ]
    if listData:
        return ('{' + ','.join([ '"' + x.replace('"', '\\"') + '"' for x in listData ]) + '}').replace('\n', ';')
    else:
        return '{}'


def floatListToMatrix(listData):
    return '<<' + ';'.join([ ','.join([ unicode(y) for y in x ]) for x in listData ]) + '>>'


def undoOpenClose(undoOpen):
    if undoOpen:
        mc.undoInfo(ock=1)
    else:
        mc.undoInfo(cck=1)


class LocusPickerLauncherUI(base_class, form_class):
    __window__ = None

    def __init__(self, parent = PLATFORM_PARENT, objName = USER_WINDOW_NAME):
        super(base_class, self).__init__(parent)
        self.setupUi(self)
        self.setObjectName(objName)
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(self.windowTitle() + ' v%.3f' % VERSION)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setLocale(QLocale(QLocale.English))
        self.setFocusPolicy(Qt.StrongFocus)
        self.__topMenuVisible = True
        self.__poseGloalData = []
        self.__poseNodes = None
        self.__poseChannels = None
        self.__poseStartValues = None
        self.__blockCallback = False
        self.__recentDirectory = ''
        self.__autokeyState = False
        self.__selectGuideDialog = None
        self.__callbacks = []
        self.setupUiEnv()
        return

    @property
    def recentDirectory(self):
        return self.__recentDirectory

    @recentDirectory.setter
    def recentDirectory(self, dirPath):
        self.__recentDirectory = dirPath

    def resizeEvent(self, event):
        super(base_class, self).resizeEvent(event)
        self.fitShelfWidget()

    def fitShelfWidget(self):
        width = min(self.shelf_listWidget.count() * (ShelfListWidget.GRID_SIZE.width() + ShelfListWidget.SPACING), self.lowerToolBar.width() - self.addBookmark_button.width() - 4)
        self.shelf_listWidget.setFixedWidth(width)

    def setupUiEnv(self):
        self.replaceToggleButtons()
        self.replaceTabWidget()
        self.tabPoupMenuBuild()
        self.generateAction()
        self.setToolBarMenu()
        self.restoreIniSettings()
        self.dispatcher = ThreadDispatcher(self)
        self.dispatcher.start()
        self.connectTabSignal()
        self.connectToggleButtonsSignal()
        self.connectTopMenuSignal()
        try:
            self.addCallback(om.MEventMessage.addEventCallback('SelectionChanged', partial(self.selectionChanged)))
        except:
            print 'Fail to add callback : SelectionChanged'

        try:
            self.addCallback(om.MEventMessage.addEventCallback('SceneOpened', partial(self.refresh, True)))
        except:
            print 'Fail to add callback : SceneOpened'

        mc.scriptJob(p=toMayaObject(self), tc=lambda *args: self.setVisToggleStates())
        QTimer.singleShot(1, partial(self.refresh))

    def addCallback(self, callbackObj):
        self.__callbacks.append(callbackObj)

    def customEvent(self, event):
        event.callback()

    def isUsePrefix(self):
        return self.prefix_button.isChecked()

    def prefix(self):
        return self.prefix_lineEdit.text()

    def characterName(self):
        return self.characterLineEdit.text()

    def mapName(self, index = -1):
        if index < 0:
            index = self.tabWidget.currentIndex()
        return self.tabWidget.tabText(index)

    def openInfoDocumentUrl(self):
        from const import documentUrl
        if 'QDesktopServices' in locals():
            QDesktopServices.openUrl(documentUrl)
        else:
            import webbrowser
            webbrowser.open(documentUrl, new=2)

    def connectTabSignal(self):
        self.tabWidget.currentChanged.connect(self.setTabData)
        self.tabWidget.currentChanged.connect(self.selectionChanged)
        self.tabWidget.sendCommandData.connect(self.doCommand)
        self.tabWidget.poseGlobalVarSet.connect(lambda x: self.setPoseGlobalVariable(True, x))
        self.tabWidget.poseGlobalVarUnset.connect(lambda x: self.setPoseGlobalVariable(False, x))
        self.tabWidget.undoOpen.connect(lambda : undoOpenClose(True))
        self.tabWidget.undoClose.connect(lambda : undoOpenClose(False))
        self.tabWidget.selectMapNode.connect(self.selectMapNode)
        self.tabWidget.tearOff.connect(self.tearOff)

    def connectToggleButtonsSignal(self):
        self.topMenuToggleButton.clicked.connect(self.toggleTopMenu)

    def connectTopMenuSignal(self):
        self.characterLineEdit.waitStart.connect(self.beforeChangeCharacter)
        self.characterLineEdit.labelSelected.connect(self.changeCharacter)
        self.characterLineEdit.requestRenamable.connect(self.isCharacterRenamable)
        self.prefix_button.toggled.connect(self.storeUsePrefix)
        self.prefix_button.toggled.connect(self.toggleMapUsePrefix)
        self.copyPrefix_button.clicked.connect(self.setPrefixFromSelectedNode)
        self.prefix_lineEdit.textChanged.connect(self.storePrefix)
        self.prefix_lineEdit.editingFinished.connect(self.updateMapPrefix)
        self.addBookmark_button.clicked.connect(self.appendMapBookmark)
        self.shelf_listWidget.selected.connect(self.seekMap)
        self.shelf_listWidget.rename.connect(self.renameMap)
        self.shelf_listWidget.remove.connect(self.eliminateMap)
        self.shelf_listWidget.reorder.connect(self.reorderMap)

    def createAction(self, text, slot = None, shortcut = None, icon = None, tip = None, checkable = False, signal = 'triggered()', disable = False):
        action = QAction(text, self)
        if icon is not None:
            if disable:
                if isinstance(disable, bool):
                    image = QImage(icon)
                    image.invertPixels()
                    dis_pm = QPixmap.fromImage(image)
                elif isinstance(disable, (str, unicode)):
                    dis_pm = QPixmap(disable)
                ic = QIcon(icon)
                ic.addPixmap(dis_pm, QIcon.Disabled)
                action.setIcon(ic)
            else:
                action.setIcon(QIcon(icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def generateAction(self):
        from const import REFRESH_TIP, LOAD_FILE_TIP, INFO_TIP
        self.refreshAct = self.createAction('Refresh', self.refresh, icon=':/refresh', disable=True, tip=REFRESH_TIP)
        self.loadFileToTabAct = self.createAction('Load Map File', self.loadDataFromFile, icon=':/open', tip=LOAD_FILE_TIP)
        self.infoAct = self.createAction('Info', self.openInfoDocumentUrl, icon=':/infoDocu', tip=INFO_TIP)

    def setUpperToolBarMenu(self):
        for act in [self.loadFileToTabAct, self.infoAct, self.refreshAct]:
            self.upperToolBar.addAction(act)
            self.upperToolBar.widgetForAction(act).setFixedSize(24, 24)

        self.setUpperCommonActions()

    def setUpperCommonActions(self):
        self.characterLineEdit = PopupLineEdit(self)
        self.upperToolBar.addWidget(self.characterLineEdit)
        self.prefix_button = QCheckBox('Prefix', self)
        self.prefix_button.setFixedSize(47, 18)
        from const import PREFIX_TIP, COPY_PREFIX_TIP, PREFIX_FIELD_TIP
        self.prefix_button.setToolTip(PREFIX_TIP)
        self.copyPrefix_button = HoverIconButton()
        self.copyPrefix_button.setDisabledPixmap(':play_disabled')
        self.copyPrefix_button.setCustomIcon(':/play', ':/play_hover')
        self.copyPrefix_button.setFixedSize(20, 20)
        self.copyPrefix_button.setToolTip(COPY_PREFIX_TIP)
        self.copyPrefix_button.setEnabled(False)
        self.copyPrefix_button.setAutoRaise(False)
        self.prefix_lineEdit = QLineEdit(self)
        self.prefix_lineEdit.setFocusPolicy(Qt.StrongFocus)
        self.prefix_lineEdit.setEnabled(False)
        self.prefix_lineEdit.setToolTip(PREFIX_FIELD_TIP)
        self.prefix_lineEdit.setFixedWidth(96)
        self.upperToolBar.addWidget(self.prefix_button)
        self.upperToolBar.addWidget(self.copyPrefix_button)
        self.upperToolBar.addWidget(self.prefix_lineEdit)

    def setLowerToolBarMenu(self):
        self.shelf_listWidget = ShelfListWidget()
        self.lowerToolBar.addWidget(self.shelf_listWidget)
        self.addBookmark_button = HoverIconButton()
        self.addBookmark_button.setFixedSize(32, 32)
        self.addBookmark_button.setCustomIcon(':/appendBookmark', ':/appendBookmark_hover')
        from const import ADD_BOOKMARK_TIP
        self.addBookmark_button.setToolTip(ADD_BOOKMARK_TIP)
        self.lowerToolBar.addWidget(self.addBookmark_button)
        spacer = QWidget()
        spacer.setMinimumWidth(0)
        spacer.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.lowerToolBar.addWidget(spacer)
        self.prefix_button.toggled.connect(self.prefix_lineEdit.setEnabled)
        self.prefix_button.toggled.connect(self.copyPrefix_button.setEnabled)

    def setToolBarMenu(self):
        self.setUpperToolBarMenu()
        self.setLowerToolBarMenu()

    @property
    def topMenuVisible(self):
        return self.__topMenuVisible

    @topMenuVisible.setter
    def topMenuVisible(self, visible):
        doResize = isinstance(self.sender(), QToolButton) or self.tabWidget.count()
        adjustHeight = self.upperToolBar.height() + self.lowerToolBar.height()
        if visible:
            isModified = self.isWindowModified()
            self.upperToolBar.show()
            self.lowerToolBar.show()
            adjustHeight = self.upperToolBar.height() + self.lowerToolBar.height()
            if doResize:
                self.resize(self.width(), self.height() + adjustHeight)
            self.topMenuToggleButton.upsideDown = False
            if not isModified:
                self.setWindowModified(False)
        else:
            self.upperToolBar.hide()
            self.lowerToolBar.hide()
            if doResize:
                self.resize(self.width(), self.height() - adjustHeight)
            self.topMenuToggleButton.upsideDown = True
        self.__topMenuVisible = visible

    def toggleTopMenu(self):
        self.topMenuVisible = not self.topMenuVisible

    def replaceWidget(self, layout, widget, itemClass, args = []):
        index = layout.indexOf(widget)
        tooltip = widget.toolTip()
        if isinstance(layout, QGridLayout):
            position = layout.getItemPosition(index)
        layout.removeWidget(widget)
        widget.deleteLater()
        widget = itemClass(*(args + [self]))
        widget.setToolTip(tooltip)
        if locals().has_key('position'):
            layout.addWidget(widget, *position)
        else:
            layout.insertWidget(index, widget)
        return widget

    def replaceToggleButtons(self):
        self.topMenuToggleButton = self.replaceWidget(self.topMenuToggle_layout, self.topMenuToggleButton, ArrowToggleButton)
        self.topMenuToggleButton.upsideDown = False
        if INMAYA > 2015:
            self.topMenuToggle_layout.setContentsMargins(1, 0, 1, 1)

    def replaceTabWidget(self):
        self.tabWidget = self.replaceWidget(self.tabWidget.parent().layout(), self.tabWidget, TabWidget)

    def tabPoupMenuBuild(self):
        try:
            self.mayaLayout = toMayaObject(self.tabWidget)
            className = self.__class__.__name__
            isMaster = self.isWindowMaster()
            self.__mayaPopupMenu__ = mm.eval('locusPicker:buildMapPopupMenu("%s", "%s.__window__", %d)' % (self.mayaLayout, className, isMaster))
        except:
            traceback.print_exc()

    def isWindowMaster(self):
        return hasattr(self, 'clipboard')

    def getEnvPath(self):
        if INMAYA:
            return os.path.join(mc.internalVar(upd=1), 'locusPicker.ini')
        else:
            return os.path.join(os.path.dirname(sys.modules[self.__module__].__file__), '__setting.ini')

    def closeEvent(self, event):
        super(base_class, self).closeEvent(event)
        self.dispatcher.stop()
        self.saveIniSettings()
        self.tabWidget.clear()
        self.__class__.setWindowObj(None)
        for cb in self.__callbacks:
            om.MMessage.removeCallback(cb)

        if hasattr(self, '__mayaPopupMenu__') and self.__mayaPopupMenu__:
            mc.deleteUI(self.__mayaPopupMenu__)
        mc.evalDeferred("if mc.window('%(win)s', ex=1): mc.deleteUI('%(win)s')" % {'win': toMayaObject(self)})
        return

    def getAvailableScreen(self):
        desktop = QApplication.desktop()
        r = QRect()
        for i in xrange(desktop.screenCount()):
            r = r.united(desktop.availableGeometry(i))

        return r

    def saveIniSettings(self):
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('Window')
        geometry = self.geometry()
        avaiableGeo = self.getAvailableScreen()
        if geometry.top() < avaiableGeo.top() + 30:
            geometry.moveTop(avaiableGeo.top() + 30)
        if geometry.left() < avaiableGeo.left() + 8:
            geometry.moveLeft(avaiableGeo.left() + 8)
        settings.setValue('Geometry', geometry)
        settings.setValue('State', self.saveState())
        settings.setValue('RecentDirectory', self.recentDirectory)
        settings.endGroup()

    def restoreIniSettings(self):
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('Window')
        value = settings.value('Geometry')
        if value is not None:
            self.setGeometry(value)
            self.__workingSize = value.size()
        value = settings.value('RecentDirectory')
        if value is not None:
            self.recentDirectory = value
        settings.endGroup()
        return

    def determinePage(self):
        pickerNodes = filterPickerNode()
        return pickerNodes

    def setTabData(self, index):
        tab = self.tabWidget.widget(index)
        if not tab:
            return
        if tab.usePrefix:
            self.prefix_button.setChecked(True)
            self.prefix_lineEdit.setText(tab.prefix)
        else:
            self.prefix_button.setChecked(False)
            self.prefix_lineEdit.setText('')
            self.matchPrefixToMap(index)
        self.loadEachMap(index)

    def matchPrefixToMap(self, index):
        try:
            charName = self.characterName()
            subSetName = self.mapName(index)
            pickerNode = mm.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (listToArray(filterPickerNode()), charName, subSetName))
            if pickerNode != 'None':
                self.getPrefixFromPickerNode(pickerNode)
        except:
            pass

    def getPrefixFromPickerNode(self, node):
        usePrefix = mc.getAttr('%s.usePrefix' % node)
        self.prefix_button.setChecked(usePrefix)
        prefix = mc.getAttr('%s.prefix' % node)
        if prefix:
            self.prefix_lineEdit.setText(prefix)
        else:
            split = node.rsplit(':', 1)
            if len(split) == 2:
                self.prefix_lineEdit.setText(split[0] + ':')
                self.prefix_button.setChecked(True)
            else:
                self.prefix_lineEdit.setText('')

    def setPrefixFromSelectedNode(self):
        node = mc.ls(sl=1)
        if node:
            node = node[0]
        else:
            return
        split = node.rsplit(':', 1)
        if len(split) == 2:
            self.prefix_lineEdit.setText(split[0] + ':')
        else:
            self.prefix_lineEdit.setText('')
        self.prefix_lineEdit.editingFinished.emit()

    @sceneExists
    def toggleMapUsePrefix(self, toggle, scene = None):
        if not scene:
            return
        view = scene.primaryView()
        if not view:
            return
        if not view.pickerNode:
            return
        mc.setAttr(view.pickerNode + '.usePrefix', toggle)

    @sceneExists
    def updateMapPrefix(self, scene = None):
        if not scene:
            return
        view = scene.primaryView()
        if not view:
            return
        if not view.pickerNode:
            return
        mc.setAttr(view.pickerNode + '.prefix', self.prefix_lineEdit.text(), type='string')

    def storeUsePrefix(self, toggle):
        tab = self.tabWidget.currentWidget()
        tab.usePrefix = toggle

    def storePrefix(self, text):
        tab = self.tabWidget.currentWidget()
        tab.prefix = text

    def appendMapBookmark(self):
        shelfNode = filterShelfNode()
        if shelfNode:
            shelfNode = shelfNode[0]
        else:
            shelfNode = mm.eval('locusPicker:createShelfNode()')
        charName = self.characterName()
        mapName = self.mapName()
        pickerNode = mm.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (listToArray(filterPickerNode()), charName, mapName))
        connected = mc.listConnections(shelfNode + '.bookmarkList')
        if not connected or pickerNode not in connected:
            indices = mc.getAttr('locusPicker_shelf.bookmarkList', mi=1)
            if not indices:
                index = 0
            else:
                index = sorted(indices)[-1] + 1
            label = splitCapitalized(charName) + ' ' + mapName
            mc.connectAttr(pickerNode + '.message', shelfNode + '.bookmarkList[%d]' % index, f=1)
            mc.setAttr(shelfNode + '.bookmarkLabel[%d]' % index, label, type='string')
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, pickerNode)
            item.setToolTip('Character: ' + charName + '\nMap: ' + mapName)
            self.shelf_listWidget.addItem(item)
        self.fitShelfWidget()

    def loadBookmark(self):
        self.shelf_listWidget.clear()
        shelfNode = filterShelfNode()
        if shelfNode:
            connected = mc.listConnections(shelfNode[0] + '.bookmarkList', c=1)
            if connected:
                for i in xrange(0, len(connected), 2):
                    plug = connected[i]
                    labelPlug = plug.replace('bookmarkList', 'bookmarkLabel')
                    node = connected[i + 1]
                    if not mc.objExists(node + '.locusPickerMap'):
                        continue
                    label = mc.getAttr(labelPlug)
                    charName = mc.getAttr(node + '.characterName')
                    mapName = mc.getAttr(node + '.subSetName')
                    item = QListWidgetItem(label)
                    item.setData(Qt.UserRole, node)
                    item.setToolTip('Character: ' + charName + '\nMap: ' + mapName)
                    item.setFlags(item.flags() | Qt.ItemIsDragEnabled)
                    self.shelf_listWidget.addItem(item)

        self.fitShelfWidget()

    def seekMap(self, nodeName):
        if not mc.objExists(nodeName):
            return
        charName = mc.getAttr(nodeName + '.characterName')
        mapName = mc.getAttr(nodeName + '.subSetName')
        founded = [ x for x in self.getTearoffDialogs() if x.characterName == charName and x.mapName == mapName ]
        if founded:
            founded[0].raise_()
            return
        self.characterLineEdit.doSelectText(charName)
        for i in xrange(self.tabWidget.count()):
            if self.mapName(i) == mapName:
                self.tabWidget.setCurrentIndex(i)
                break

    def renameMap(self, nodeName, newName):
        shelfNode = filterShelfNode()
        if shelfNode:
            connectedPlug = mc.listConnections(nodeName + '.message', s=0, d=1, p=1)[0]
            labelPlug = connectedPlug.replace('bookmarkList', 'bookmarkLabel')
            mc.setAttr(labelPlug, newName, type='string')

    def eliminateMap(self, nodeName):
        shelfNode = filterShelfNode()
        if shelfNode:
            connectedPlug = mc.listConnections(nodeName + '.message', s=0, d=1, p=1)[0]
            labelPlug = connectedPlug.replace('bookmarkList', 'bookmarkLabel')
            mc.disconnectAttr(nodeName + '.message', connectedPlug)
            mc.evalDeferred("mc.removeMultiInstance('%s', b=True)" % connectedPlug)
            mc.evalDeferred("mc.removeMultiInstance('%s', b=True)" % labelPlug)
        self.fitShelfWidget()

    def reorderMap(self):
        shelfNode = filterShelfNode()
        if shelfNode:
            labels = []
            nodes = []
            for i in xrange(self.shelf_listWidget.count()):
                item = self.shelf_listWidget.item(i)
                labels.append(item.text())
                nodes.append(item.data(Qt.UserRole))

            mm.eval('locusPicker:reorderShelfNode("%s", %s, %s)' % (shelfNode[0], listToArray(labels), listToArray(nodes)))

    @sceneExists
    def setVisToggleStates(self, scene = None):
        ns = self.prefix()
        c = re.compile("^.+\\'\\(%ns%\\)(.+?)\\',.+$")
        items = scene.findVisToggleItem()
        for item in items:
            cmd = item.states.values()[0].cmd
            if cmd:
                ctl = c.match(cmd).group(1)
                curr = item.getCurrentIndex()
                if mc.objExists(ns + ctl) and mc.objExists(ns + ctl + '.ikfk_switch'):
                    val = int(mc.getAttr(ns + ctl + '.ikfk_switch'))
                    if curr != val:
                        item.toggleVisibility(val, True)

    def loadPickerNodeToMap(self, nodes):
        self.tabWidget.blockSignals(True)
        index = 0
        compares = [ (dlg.characterName, dlg.mapName) for dlg in self.getTearoffDialogs() ]
        for pickerNode in nodes:
            charName = mc.getAttr('%s.characterName' % pickerNode)
            subSet = mc.getAttr('%s.subSetName' % pickerNode)
            if (charName, subSet) in compares:
                continue
            self.tabWidget.addGraphicsTab(subSet, changeCurrent=False)
            size = mc.getAttr('%s.bgSize' % pickerNode)
            if size:
                size = QSize(*[ int(v) for v in size.split(',') ])
                scene = self.tabWidget.sceneAtIndex(index)
                scene.mapSize = size
            view = self.tabWidget.viewAtIndex(index)
            view.pickerNode = pickerNode
            tab = self.tabWidget.widget(index)
            tab.usePrefix = mc.getAttr('%s.usePrefix' % pickerNode)
            tab.prefix = mc.getAttr('%s.prefix' % pickerNode, asString=True)
            if mc.referenceQuery(pickerNode, inr=1):
                self.tabWidget.setTabIcon(index, QIcon(':/locked'))
            index += 1

        self.tabWidget.blockSignals(False)

    def loadEachMap(self, index):
        view = self.tabWidget.viewAtIndex(index)
        if view and not view.loaded:
            pickerNode = view.pickerNode
            scene = self.tabWidget.sceneAtIndex(index)
            useBgColor = mc.getAttr('%s.useBgColor' % pickerNode)
            bgColor = mc.getAttr('%s.bgColor' % pickerNode)
            if bgColor:
                scene.color = QColor.fromRgb(*[ int(v) for v in bgColor.split(',') ])
            bgImage = mc.getAttr('%s.bgImage' % pickerNode)
            if bgImage:
                scene.setBackgroundPixmap(bgImage)
            scene.useBGimage = not useBgColor
            types = mm.eval('locusPicker:getStringArray("%s", "type")' % pickerNode)
            positions = mm.eval('locusPicker:getStringArray("%s", "position")' % pickerNode)
            sizes = mm.eval('locusPicker:getStringArray("%s", "size")' % pickerNode)
            colors = mm.eval('locusPicker:getStringArray("%s", "color")' % pickerNode)
            commands = mm.eval('locusPicker:getStringArray("%s", "command")' % pickerNode)
            nodes = mm.eval('locusPicker:getStringArray("%s", "node")' % pickerNode)
            channels = mm.eval('locusPicker:getStringArray("%s", "channel")' % pickerNode)
            values = mm.eval('locusPicker:getStringArray("%s", "value")' % pickerNode)
            labels = mm.eval('locusPicker:getStringArray("%s", "label")' % pickerNode)
            icons = mm.eval('locusPicker:getStringArray("%s", "icon")' % pickerNode)
            hashcodes = mm.eval('locusPicker:getStringArray("%s", "hashcode")' % pickerNode)
            groupAssembly = {}
            linkAssembly = {}
            visToggleAssembly = {}
            for i in xrange(len(types)):
                splited = nodes[i].split('&')
                node = splited[0] and splited[0].split(',') or []
                hashcode = i < len(hashcodes) and hashcodes[i] or ''
                if types[i] == 'Group':
                    doKey, doReset, labelPos, buttonPos = decodeGroupCommandStr(commands[i])
                    dataBlock = dict(type=types[i], pos=QPointF(*[ float(v) for v in positions[i].split(',') ]), size=[ float(v) for v in sizes[i].split(',') ], label=labels[i], doKey=doKey, doReset=doReset, hashcode=hashcode, labelPos=labelPos, buttonPos=buttonPos)
                else:
                    if types[i] != 'VisToggle':
                        channel = channels[i] and channels[i].split(',') or []
                    icon = decodeIconStr(icons[i], types[i])
                    label = decodeLabelStr(labels[i])
                    if types[i] == 'RectangleSlider' and (commands[i].startswith('Range') or commands[i].startswith('Pose')):
                        command, attach, backward = decodeCommandStr(commands[i])
                        sizeSplit = sizes[i].split(';', 1)
                        if len(sizeSplit) == 2:
                            size, slider = sizeSplit
                        else:
                            size, slider = sizeSplit[0], '3,3,16'
                        dataBlock = dict(type=types[i], pos=QPointF(*[ float(v) for v in positions[i].split(',') ]), size=[ float(v) for v in size.split(',') ], color=QColor.fromRgb(*[ int(v) for v in colors[i].split(',') ]), command=command, node=node, channel=channel, value=complexListData(values[i]), label=label, attach=Attachment.getAttachment(attach), slider=[ float(v) for v in slider.split(',') ], backward=backward, icon=icon, hashcode=hashcode)
                    elif types[i] == 'VisToggle':
                        dataBlock = dict(type=types[i], pos=QPointF(*[ float(v) for v in positions[i].split(',') ]), size=[ float(v) for v in sizes[i].split(',') ], command=commands[i], path=icon, hashcode=hashcode)
                    else:
                        if commands[i].startswith('EXEC'):
                            commands[i] = str(commands[i]).encode('string_escape')
                        dataBlock = dict(type=types[i], pos=QPointF(*[ float(v) for v in positions[i].split(',') ]), size=[ float(v) for v in sizes[i].split(',') ], color=QColor.fromRgb(*[ int(v) for v in colors[i].split(',') ]), command=commands[i], node=node, channel=channel, value=complexListData(values[i]), label=label, icon=icon, hashcode=hashcode)
                item = scene.addVarsItem(**dataBlock)
                if len(splited) > 1:
                    linkAssembly[item] = splited[1] and splited[1].split(',') or []
                if types[i] == 'Group':
                    groupAssembly[item] = node[:]
                elif types[i] == 'VisToggle':
                    visToggleAssembly[item] = [node[:], decodeVisToggleColorStr(colors[i]), decodeVisToggleChannelStr(channels[i])]

            for item, link_hash in linkAssembly.items():
                item.linkedItems = scene.findHashcodeItems(link_hash)

            for item, child_hash in groupAssembly.items():
                for child in scene.findHashcodeItems(child_hash):
                    child.setParentItem(item)

            for item, (nodes, colors, cmds) in visToggleAssembly.items():
                states = {}
                for i, nodeStr in enumerate(nodes):
                    name, targets = decodeVisToggleNodeStr(nodeStr)
                    if i < len(colors):
                        states[i] = ToggleState(name, i == 0, colors[i], scene.findHashcodeItems(targets), i < len(cmds) and cmds[i] or '')
                    else:
                        states[i] = ToggleState(name, i == 0, targets=scene.findHashcodeItems(targets), cmd=i < len(cmds) and cmds[i] or '')

                item.states = states

            if mc.referenceQuery(pickerNode, inr=1):
                if hasattr(scene, 'editable'):
                    scene.setAllItemsEditable(False)
                self.tabWidget.setTabIcon(index, QIcon(':/locked'))
            view.loaded = True
        self.setVisToggleStates()

    def refresh(self, *args):
        if args and args[0]:
            for dlg in self.getTearoffDialogs():
                dlg.setParent(None)
                dlg.close()

        self.loadBookmark()
        if isinstance(self.sender(), QAction):
            currentIndex = self.tabWidget.currentIndex()
        else:
            currentIndex = -1
        self.tabWidget.clear()
        nodes = self.determinePage()
        if nodes is None:
            return
        else:
            if nodes == []:
                self.characterLineEdit.clear()
            curCharName = self.characterName()
            characterNames = [ mc.getAttr('%s.characterName' % node) for node in nodes ]
            if not characterNames:
                return
            characterNames = list(set(characterNames))
            characterNames.sort()
            index = not characterNames.count(curCharName) and -1 or characterNames.index(curCharName)
            charName = index >= 0 and characterNames[index] or characterNames[0]
            self.characterLineEdit.labels = characterNames
            self.characterLineEdit.setText(charName)
            filteredNodes = mm.eval('locusPicker:filterMapNodeCharacter(%s, "%s")' % (listToArray(nodes), charName))
            filteredNodes.sort(key=lambda x: mc.getAttr(x + '.tabOrder'))
            self.loadPickerNodeToMap(filteredNodes)
            if currentIndex > 0:
                self.tabWidget.setCurrentIndex(currentIndex)
            else:
                currentIndex = 0
            self.setTabData(currentIndex)
            return

    def beforeChangeCharacter(self):
        self.characterLineEdit.wait = WaitState.Proceed

    def isCharacterRenamable(self, charName):
        self.characterLineEdit.wait = WaitState.GoBack

    def changeCharacter(self, charName):
        nodes = filterPickerNode()
        if nodes is None:
            return
        else:
            self.tabWidget.clear()
            filteredNodes = mm.eval('locusPicker:filterMapNodeCharacter(%s, "%s")' % (listToArray(filterPickerNode()), charName))
            filteredNodes.sort(key=lambda x: mc.getAttr(x + '.tabOrder'))
            if filteredNodes:
                self.loadPickerNodeToMap(filteredNodes)
                self.setTabData(0)
            return

    def assignDataToNode(self, specificMap = ''):
        result = []
        undoOpenClose(True)
        try:
            charName = self.characterName()
            if specificMap:
                index = -1
                for i in xrange(self.tabWidget.count()):
                    if specificMap == self.mapName(i):
                        index = i
                        break
                else:
                    print 'tab is not exists:', specificMap
                    return warn('Tab is not existing : ' + specificMap, parent=self)

                pickerNode = mm.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (listToArray(filterPickerNode()), charName, specificMap))
                if pickerNode == 'None':
                    pickerNode = mm.eval('locusPicker:createMapNode("%s", "%s")' % (charName, specificMap))
                self.assignTabData(pickerNode, index)
                if mc.referenceQuery(pickerNode, inr=True):
                    pass
                else:
                    self.assignButtonData(pickerNode, index)
                    result.append(pickerNode)
            else:
                referenced = []
                for index in xrange(self.tabWidget.count()):
                    view = self.tabWidget.viewAtIndex(index)
                    subSetName = self.mapName(index)
                    pickerNode = mm.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (listToArray(filterPickerNode()), charName, subSetName))
                    if pickerNode:
                        mc.setAttr(pickerNode + '.tabOrder', index)
                    if not view.loaded:
                        continue
                    if pickerNode == 'None':
                        pickerNode = mm.eval('locusPicker:createMapNode("%s", "%s")' % (charName, subSetName))
                    self.assignTabData(pickerNode, index)
                    if mc.referenceQuery(pickerNode, inr=True):
                        continue
                    self.assignButtonData(pickerNode, index)
                    result.append(pickerNode)

                if referenced:
                    warn("Can't save button data to node if referenced\n\n  " + '\n  '.join(referenced), parent=self)
        except StandardError:
            traceback.print_exc()
        finally:
            undoOpenClose(False)

        return result

    def assignTabData(self, node, index):
        size = self.tabWidget.sceneAtIndex(index).mapSize
        scene = self.tabWidget.sceneAtIndex(index)
        bgSize = '%d,%d' % (size.width(), size.height())
        useBgColor = not scene.useBGimage and 1 or 0
        bgImage = scene.imagePath
        bgColor = ','.join((unicode(v) for v in scene.color.getRgb()[:3]))
        tab = self.tabWidget.widget(index)
        usePrefix = tab.usePrefix and 1 or 0
        prefix = tab.prefix
        mm.eval('locusPicker:assignMapData("%s", "%s", %d, %d, "%s", "%s", %d, "%s");' % (node,
         bgSize,
         index,
         useBgColor,
         bgImage,
         bgColor,
         usePrefix,
         prefix))

    def assignButtonData(self, node, index):
        scene = self.tabWidget.sceneAtIndex(index)
        items = scene.getItemsByZValueOrder()
        types, positions, sizes, colors, commands, hashcodes, nodes, channels, values, labels, icons = ([] for i in xrange(11))
        for item in items:
            typeStr, posStr, sizeStr, colorStr, commandStr, nodeStr, channelStr, valueStr, iconStr, labelStr, hashcode = self.convertItemDataToString(item)
            types.append(typeStr)
            positions.append(posStr)
            sizes.append(sizeStr)
            colors.append(colorStr)
            commands.append(commandStr)
            nodes.append(nodeStr)
            channels.append(channelStr)
            values.append(valueStr)
            icons.append(iconStr)
            labels.append(labelStr)
            hashcodes.append(hashcode)

        mm.eval('locusPicker:assignButtonData("%s", %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' % (node,
         listToArray(types),
         listToArray(positions),
         listToArray(sizes),
         listToArray(colors),
         listToArray(commands),
         listToArray(nodes),
         listToArray(channels),
         listToArray(values),
         listToArray(labels),
         listToArray(icons),
         listToArray(hashcodes)))

    def convertItemDataToString(self, item):
        typeStr = getTypeString(item.type())
        pos = item.scenePos()
        posStr = '%.2f,%.2f' % (pos.x(), pos.y())
        sizeStr = '%.2f,%.2f' % (item.width, item.height)
        hashcode = item.hashcode
        color = item.color
        colorStr = '%d,%d,%d' % (color.red(), color.green(), color.blue())
        if typeStr == 'Group':
            commandStr = encodeGroupCommandStr(item)
            nodeStr = ','.join([ c.hashcode for c in item.childItems() ])
            channelStr = ''
            valueStr = ''
            iconStr = ''
            labelStr = str(item.label)
        elif typeStr == 'VisToggle':
            commandStr = encodeCommandStr(item)
            colorStr = encodeVisToggleColorStr(item)
            nodeStr = encodeVisToggleNodeStr(item)
            channelStr = encodeVisToggleChannelStr(item)
            valueStr = ''
            iconStr = encodeIconStr(item)
            labelStr = ''
        else:
            if item.command in ('Range', 'Pose') and typeStr in ('RectangleSlider',):
                sizeStr += ';%.2f,%.2f,%.2f' % (item.margin1, item.margin2, item.thickness)
            commandStr = encodeCommandStr(item)
            nodeStr = ','.join((str(tn) for tn in item.targetNode))
            if commandStr.startswith('Select') and item.linkedItems:
                nodeStr += '&' + ','.join([ i.hashcode for i in item.linkedItems if i.scene() ])
            channelStr = ','.join((str(tc) for tc in item.targetChannel))
            valueStr = complexStringData(item.targetValue)
            iconStr = encodeIconStr(item)
            labelStr = encodeLabelStr(item)
        return (typeStr,
         posStr,
         sizeStr,
         colorStr,
         commandStr,
         nodeStr,
         channelStr,
         valueStr,
         iconStr,
         labelStr,
         hashcode)

    def loadDataFromFile(self):
        if self.recentDirectory:
            dirPath = self.recentDirectory
        else:
            dirPath = os.path.expanduser('~')
        from dialog import OpenMultiFilesDialog
        fileNames = OpenMultiFilesDialog('Open Map file', dirPath, MAP_FILE_FILTER, parent=self)
        if fileNames:
            for fn in fileNames:
                index = self.doLoadDataFromFile(fn)
                if index < 0:
                    continue
                node = self.assignDataToNode(self.mapName(index))
                if node:
                    self.tabWidget.viewAtIndex(index).pickerNode = node[0]

            return True
        return False

    def checkMapNodeExists(self, character, subSet):
        if mm.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (listToArray(filterPickerNode()), character, subSet)) != 'None':
            if question('Map already exists : %s\nDo you want to replace it?' % subSet, 'Map Exists', self):
                index = -1
                for i in xrange(self.tabWidget.count()):
                    print self.mapName(i)
                    if self.mapName(i) == subSet:
                        index = i
                        break
                else:
                    error('No tab', parent=self)
                    return -1

                tab = self.tabWidget.widget(index)
                scene = self.tabWidget.sceneAtIndex(index)
                scene.clear()
            else:
                return -1
        else:
            tab = self.tabWidget.addGraphicsTab(subSet, changeCurrent=False)
            index = self.tabWidget.count() - 1
            scene = self.tabWidget.sceneAtIndex(index)
        return (tab, index, scene)

    def doLoadDataFromFile(self, path):
        try:
            dataNode = parse(path).getroot()
        except:
            raise IOError, 'Error to open file:', path

        mapNode = dataNode.find('map')
        character = mapNode.get('character')
        subSet = mapNode.get('name')
        prefix = mapNode.get('prefix')
        size = mapNode.get('size')
        size = QSize(*[ int(v) for v in size.split(',') ])
        bgImage = mapNode.get('bgImage')
        bgColor = mapNode.get('bgColor')
        usePrefix = mapNode.get('usePrefix')
        useBgColor = mapNode.get('useBgColor')
        if character in self.characterLineEdit.labels:
            if self.characterName() == character:
                pass
            else:
                self.assignDataToNode()
                self.characterLineEdit.doSelectText(character)
        else:
            self.assignDataToNode()
            self.characterLineEdit.appendLabel(character)
            self.characterLineEdit.doSelectText(character)
        tab, index, scene = self.checkMapNodeExists(character, subSet)
        tab.prefix = prefix
        tab.usePrefix = bool(int(usePrefix))
        scene.mapSize = size
        scene.color = QColor.fromRgb(*[ int(v) for v in bgColor.split(',') ])
        if not ast.literal_eval(useBgColor):
            scene.setBackgroundPixmap(bgImage)
        linkAssembly = {}
        groupAssembly = {}
        visToggleAssembly = {}
        for buttonNode in mapNode.findall('button'):
            data = dict(buttonNode.attrib)
            if data and 'type' in data:
                typeStr = data['type']
                if 'position' in data:
                    position = data['position']
                    del data['position']
                else:
                    position = '0.0,0.0'
                data['pos'] = QPointF(*[ float(v) for v in position.split(',') ])
                if typeStr == 'Group':
                    data['color'] = QColor.fromRgb(*[ int(v) for v in data.setdefault('color', '255,0,0').split(',') ])
                    data['size'] = [ float(v) for v in data.setdefault('size', '100,100').split(',') ]
                    data['doKey'] = data.setdefault('doKey', 'false') == 'true' and True or False
                    data['doReset'] = data.setdefault('doReset', 'false') == 'true' and True or False
                    data['labelPos'] = ButtonPosition.getPosition(data.setdefault('labelPos', 'North'))
                    data['buttonPos'] = ButtonPosition.getPosition(data.setdefault('buttonPos', 'North'))
                elif typeStr == 'VisToggle':
                    if 'command' not in data:
                        continue
                    data['size'] = [ float(v) for v in data.setdefault('size', '20,20').split(',') ]
                    if 'icon' in data:
                        icon = data['icon']
                        del data['icon']
                    else:
                        icon = ''
                    data['path'] = decodeIconStr(icon, data['type'])
                else:
                    if 'command' not in data:
                        continue
                    data['color'] = QColor.fromRgb(*[ int(v) for v in data.setdefault('color', '255,0,0').split(',') ])
                    command = data['command']
                    node = data.setdefault('node', '')
                    data['node'] = node and node.split(',') or []
                    channel = data.setdefault('channel', '')
                    data['channel'] = channel and channel.split(',') or []
                    data['icon'] = decodeIconStr(data.setdefault('icon', ''), data['type'])
                    data['label'] = decodeLabelStr(data.setdefault('label', ''))
                    data['value'] = complexListData(data.setdefault('value', ''))
                    if command.startswith('Range') or command.startswith('Pose'):
                        command, attach, backward = decodeCommandStr(command)
                        data['command'] = command
                        data['attach'] = Attachment.getAttachment(attach)
                        data['backward'] = backward
                        sizeSplit = data.setdefault('size', '60,30;3,3,16').split(';', 1)
                        if len(sizeSplit) == 2:
                            size, slider = sizeSplit
                        else:
                            size, slider = sizeSplit[0], '3,3,16'
                        data['size'] = [ float(v) for v in size.split(',') ]
                        data['slider'] = [ float(v) for v in slider.split(',') ]
                    else:
                        data['size'] = [ float(v) for v in data.setdefault('size', '20,20').split(',') ]
                item = scene.addVarsItem(**data)
                if 'linkedItem' in data and data['linkedItem']:
                    linkAssembly[item] = data['linkedItem'].split(',')
                if typeStr == 'Group':
                    groupAssembly[item] = data.setdefault('children', '').split(',')
                elif typeStr == 'VisToggle':
                    visToggleAssembly[item] = [data.setdefault('targets', 'IK:,FK:').split(','), decodeVisToggleColorStr(data.setdefault('color', '')), data.setdefault('execute', '@').split('@')]

        for item, link_hash in linkAssembly.items():
            item.linkedItems = scene.findHashcodeItems(link_hash)

        for item, child_hash in groupAssembly.items():
            for child in scene.findHashcodeItems(child_hash):
                child.setParentItem(item)

        for item, (nodes, colors, cmds) in visToggleAssembly.items():
            states = {}
            for i, nodeStr in enumerate(nodes):
                name, targets = decodeVisToggleNodeStr(nodeStr)
                if i < len(colors):
                    states[i] = ToggleState(name, i == 0, colors[i], scene.findHashcodeItems(targets), i < len(cmds) and cmds[i] or '')
                else:
                    states[i] = ToggleState(name, i == 0, targets=scene.findHashcodeItems(targets), cmd=i < len(cmds) and cmds[i] or '')

            item.states = states

        self.recentDirectory = os.path.dirname(path).replace('\\', '/')
        scene.primaryView().loaded = True
        return index

    def selectMapNode(self, index):
        charName = self.characterName()
        subSetName = self.mapName(index)
        pickerNode = mm.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (listToArray(filterPickerNode()), charName, subSetName))
        if pickerNode == 'None':
            return
        mc.select(pickerNode, r=1)

    def tearOff(self, index, pos = QPoint()):
        tab = self.tabWidget.widget(index)
        view = self.tabWidget.viewAtIndex(index)
        mapSize = self.tabWidget.sceneAtIndex(index).mapSize
        dlg = TearOffDialog(self.characterName(), self.mapName(index), self)
        dlg.addView(view)
        dlg.setOriginalState(index, self.tabWidget, tab.usePrefix, tab.prefix)
        if pos.y() > -1:
            dlg.move(pos)
        dlg.resize(mapSize)
        dlg.show()
        self.tabWidget.removeTab(index)

    def getTearoffDialogs(self):
        return self.findChildren(TearOffDialog)

    def doCommand(self, commandType, nodes, channels, values, modifier, scene):
        window = scene.window()
        if window.isUsePrefix():
            prefix = str(window.prefix())
            if nodes and nodes != [None]:
                nodes = affixPrefix(prefix, nodes)
        else:
            prefix = ''
        try:
            if commandType == 'Deselect':
                self.dispatcher.idle_add(lambda : self.doDeselectCommand(nodes))
            elif commandType.startswith('Select'):
                self.dispatcher.idle_add(lambda : self.doSelectCommand(nodes, modifier, commandType))
            elif commandType == 'Toggle':
                self.doToggleCommand(nodes, channels)
            elif commandType == 'Key':
                self.doKeyCommand(nodes, channels)
            elif commandType == 'Reset':
                self.doResetCommand(nodes, channels)
            elif commandType == 'Range':
                self.dispatcher.idle_add(lambda : self.doRangeCommand(nodes, channels, float(modifier)))
            elif commandType == 'Pose':
                if nodes and channels and values:
                    self.dispatcher.idle_add(lambda : self.doPoseCommand(values, float(modifier)))
            elif commandType.startswith('EXEC'):
                command = commandType.split(' ', 1)[1]
                command = command.replace('(%ns%)', prefix)
                self.__blockCallback = True
                mm.eval(command)
                self.__blockCallback = False
            else:
                print 'doCommand', commandType, nodes, channels
        except StandardError:
            traceback.print_exc()

        return

    def doSelectCommand(self, nodes, modifier, commandType):
        self.__blockCallback = True
        if nodes:
            nodes = listToArray(nodes)
            if modifier == 'No' or modifier == 'Alt':
                mm.eval('locusPicker:doSelect(%s, "replace")' % nodes)
            elif modifier == 'Shift':
                mm.eval('locusPicker:doSelect(%s, "toggle")' % nodes)
            elif modifier == 'Ctrl+Shift':
                mm.eval('locusPicker:doSelect(%s, "add")' % nodes)
        commandSplit = commandType.split()
        if len(commandSplit) == 2:
            if commandSplit[1] == 'Move':
                mc.setToolTo('moveSuperContext')
            elif commandSplit[1] == 'Rotate':
                mc.setToolTo('RotateSuperContext')
            elif commandSplit[1] == 'Scale':
                mc.setToolTo('scaleSuperContext')
        self.__blockCallback = False

    def doDeselectCommand(self, nodes):
        self.__blockCallback = True
        if nodes == [None]:
            mc.select(cl=1)
        elif nodes:
            nodes = listToArray(nodes)
            mm.eval('locusPicker:doSelect(%s, "deselect")' % nodes)
        self.__blockCallback = False
        return

    def doToggleCommand(self, nodes, channels):
        nodes = listToArray([ node.split('.')[0] for node in nodes ])
        channels = listToArray([ ch.split('.')[0] for ch in channels ])
        failed = mm.eval('locusPicker:doToggle(%s, %s)' % (nodes, channels))
        if failed:
            print '------ Toggle Failed ------'
            print '\n'.join(failed)

    def doKeyCommand(self, nodes, channels):
        nodes = listToArray([ node.split('.')[0] for node in nodes ])
        channels = listToArray([ ch.split('.')[0] for ch in channels ])
        failed = mm.eval('locusPicker:doKey(%s, %s)' % (nodes, channels))
        if failed:
            print '------ Key Failed ------'
            print '\n'.join(failed)

    def doResetCommand(self, nodes, channels):
        nodes = listToArray([ node.split('.')[0] for node in nodes ])
        channels = listToArray([ ch.split('.')[0] for ch in channels ])
        failed = mm.eval('locusPicker:doReset(%s, %s)' % (nodes, channels))
        if failed:
            print '------ Reset Failed ------'
            print '\n'.join(failed)

    def doRangeCommand(self, nodes, channels, value):
        nodes = listToArray([ node.split('.')[0] for node in nodes ])
        channels = listToArray([ ch.split('.')[0] for ch in channels ])
        failed = mm.eval('locusPicker:doRange(%s, %s, %f)' % (nodes, channels, value))
        if failed:
            print '------ Range Failed ------'
            print '\n'.join(failed)

    def doPoseCommand(self, values, modifier):
        targetValues = floatListToMatrix(values)
        if len(values) != len(self.__poseGloalData) or len(values[0]) != len(self.__poseGloalData[0]):
            mm.eval('locusPicker:doPoseFromDefault(%s, %s, %s, %f)' % (self.__poseNodes,
             self.__poseChannels,
             targetValues,
             modifier))
        else:
            mm.eval('locusPicker:doPose(%s, %s, %s, %s, %f)' % (self.__poseNodes,
             self.__poseChannels,
             self.__poseStartValues,
             targetValues,
             modifier))

    def setDefaultValueExceptCurrentItem(self, item):
        scene = item.scene()
        window = scene.window()
        if window.isUsePrefix():
            prefix = window.prefix()
        else:
            prefix = ''
        parentItem = item.parentItem()
        if parentItem and isinstance(parentItem, GroupItem):
            sameTargetItems = [ x for x in scene.filterItemByCommand('Pose', item.targetNode, prefix, parentItem.childItems()) if isinstance(x, RectangleDropSliderItem) ]
        else:
            sameTargetItems = [ x for x in scene.filterItemByCommand('Pose', item.targetNode, prefix) if isinstance(x, RectangleDropSliderItem) and x.parentItem() == None ]
        if item in sameTargetItems:
            sameTargetItems.remove(item)
        try:
            for sameTargetItem in sameTargetItems:
                sameTargetItem.setValue(0, False)

        except:
            print 'error sameTarget', sameTargetItem

        return

    def setPoseGlobalVariable(self, toSet, item):
        if toSet:
            self.dispatcher.idle_add(lambda : self.doSetPoseGlobalVariable(item))
        else:
            self.dispatcher.idle_add(lambda : self.doUnsetPoseGlobalVariable(item))

    def doSetPoseGlobalVariable(self, item):
        self.__autokeyState = mc.autoKeyframe(q=1, st=1)
        mc.autoKeyframe(st=0)
        window = item.scene().window()
        nodes = item.targetNode[:]
        if window.isUsePrefix():
            prefix = str(window.prefix())
            if nodes and nodes != [None]:
                nodes = affixPrefix(prefix, nodes)
        self.__poseNodes = listToArray([ node.split('.')[0] for node in nodes ])
        self.__poseChannels = listToArray([ ch.split('.')[0] for ch in item.targetChannel ])
        if not item.ignoreStartValue:
            startValues = floatListToMatrix([ [ 0 for j in xrange(len(item.targetChannel)) ] for i in xrange(len(nodes)) ])
            if isinstance(item, DragPoseDropItem):
                self.__poseGloalData = mm.eval('locusPicker:getStartValues(%s,%s,%s)' % (self.__poseNodes, self.__poseChannels, startValues))
            elif isinstance(item, RectangleDropSliderItem):
                self.__poseGloalData = mm.eval('locusPicker:getAllDefaultValues(%s,%s,%s)' % (self.__poseNodes, self.__poseChannels, startValues))
            self.__poseStartValues = floatListToMatrix(self.__poseGloalData)
        item.ignoreStartValue = False
        return

    def doUnsetPoseGlobalVariable(self, item):
        if self.__autokeyState:
            mc.autoKeyframe(st=1)
            item.emitCommmand('Key')
        self.setDefaultValueExceptCurrentItem(item)
        self.__poseGloalData = []
        self.__poseNodes = None
        self.__poseChannels = None
        self.__poseStartValues = None
        return

    def selectionChanged(self, *args):
        if self.__blockCallback:
            return
        selected = mc.ls(selection=True, objectsOnly=True)
        scene = self.tabWidget.currentScene()
        scenes = scene and [scene] or []
        scenes += [ dlg.scene() for dlg in self.getTearoffDialogs() ]
        if not scenes:
            return
        for scene in scenes:
            items = [ x for x in scene.items() if isinstance(x, AbstractDropItem) ]
            for x in items:
                x.setIgnore(True)

            scene.blockSignals(True)
            scene.clearSelection()
            if selected:
                window = scene.window()
                if window.isUsePrefix():
                    prefix = window.prefix()
                else:
                    prefix = ''
                for x in scene.filterItemByCommand('Select', selected, prefix):
                    x.setSelected(True)

            scene.blockSignals(False)
            for x in items:
                x.setIgnore(False)

    @classmethod
    def setWindowObj(cls, window):
        cls.__window__ = window

    @classmethod
    def windowObj(cls):
        return cls.__window__

    @classmethod
    def showPicker(cls):
        if mc.window(MASTER_WINDOW_NAME, q=1, ex=1):
            mc.deleteUI(MASTER_WINDOW_NAME)
        if cls.__window__:
            if cls.__window__.isMinimized():
                cls.__window__.showNormal()
            else:
                cls.__window__.raise_()
        else:
            cls.__window__ = cls(PLATFORM_PARENT)
            cls.__window__.show()

    @sceneExists
    def selectCurrentAllItems(self, scene = None):
        scene.selectInRect(scene.itemsBoundingRect())
        scene.doAllItems('Select', 'All')

    @sceneExists
    def resetAll(self, scene = None):
        scene.doAllItems('Reset', 'All')

    @sceneExists
    def resetTransform(self, scene = None):
        scene.doAllItems('Reset', 'Transform')

    @sceneExists
    def resetDefined(self, scene = None):
        scene.doAllItems('Reset', 'Defined')

    @sceneExists
    def keyAll(self, scene = None):
        scene.doAllItems('Key', 'All')

    @sceneExists
    def keyTrasnform(self, scene = None):
        scene.doAllItems('Key', 'Transform')

    @sceneExists
    def keyDefined(self, scene = None):
        scene.doAllItems('Key', 'Defined')

    def showSelectedList(self):
        if not self.__selectGuideDialog:
            self.__selectGuideDialog = SelectGuideDialog(self)
        self.__selectGuideDialog.show()
        self.__selectGuideDialog.getSelectedList()