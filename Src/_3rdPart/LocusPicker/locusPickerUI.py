# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\locusPickerUI.py


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


import os, sys, traceback, time, shutil, re, ast
from functools import partial
if module_exists('lxml'):
    from lxml.etree import Element, ElementTree, parse, tostring
else:
    from xml.etree.cElementTree import Element, ElementTree, parse, tostring
try:
    from PySide2.QtCore import Qt, QPointF, QTimer, QSize, QSettings, QRectF, QPoint, QSizeF, QEvent, QRect
    from PySide2.QtGui import QColor
    from PySide2.QtWidgets import QWidget, QApplication, QToolButton, QButtonGroup, QMenu, QPushButton, QCheckBox, QLineEdit
    from PySide2.QtUiTools import QUiLoader
except:
    from PySide.QtCore import Qt, QPointF, QTimer, QSize, QSettings, QRectF, QPoint, QSizeF, QEvent, QRect
    from PySide.QtGui import QWidget, QColor, QApplication, QToolButton, QButtonGroup, QMenu, QPushButton, QCheckBox, QLineEdit
    from PySide.QtUiTools import QUiLoader

from loadUiType import loadUiType
from locusPickerLauncherUI import LocusPickerLauncherUI, complexStringData, complexListData, filterPickerNode, listToArray, undoOpenClose
from editableTab import EditableTabWidget
from colorButton import ColorButton
from popupLineEdit import PopupLineEdit
from arrowToggleButton import ArrowToggleButton, HoverIconButton
from dropItem import AbstractDropItem
from dropSliderItem import Attachment
from dropPathItem import PathDropItem
from const import SVG_FILE_FILTER, MAP_FILE_FILTER, IMAGE_FILE_FILTER, ButtonPosition, getTypeString, warn, error, info, confirm, question, WaitState, LocaleText, encodeCommandStr, encodeIconStr, encodeLabelStr, decodeCommandStr, decodeLabelStr, encodeVisToggleNodeStr, encodeVisToggleColorStr, encodeVisToggleChannelStr, getNumericName, DropItemType, MASTER_WINDOW_NAME, USER_WINDOW_NAME, getRelativePath
from itemEditor import ItemEditor
from toolsDialog import ToolsDialog
from colorPaletteWidget import ColorPaletteDialog
from idleQueueDispatcher import ThreadDispatcher
from locusPickerResources import *
from decorator import sceneExists, timestamp
uiFile = os.path.join(os.path.dirname(__file__), 'resources', 'mainwindow.ui')
base_class, form_class = loadUiType(uiFile)
try:
    import maya.cmds as mc
    import maya.mel as mm
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

def setMapInfo(pickerNode, mapEm, name, path):
    mapEm.attrib['character'] = name
    mapEm.attrib['name'] = mc.getAttr('%s.subSetName' % pickerNode)
    mapEm.attrib['prefix'] = mc.getAttr('%s.prefix' % pickerNode)
    mapEm.attrib['size'] = mc.getAttr('%s.bgSize' % pickerNode)
    bgImage = mc.getAttr('%s.bgImage' % pickerNode)
    if bgImage:
        movPath = os.path.join(os.path.dirname(path), 'images', os.path.basename(bgImage)).replace('\\', '/')
        if os.path.normpath(bgImage) != os.path.normpath(movPath):
            shutil.copy2(bgImage, movPath)
        mapEm.attrib['bgImage'] = movPath
    else:
        mapEm.attrib['bgImage'] = bgImage
    mapEm.attrib['bgColor'] = mc.getAttr('%s.bgColor' % pickerNode)
    mapEm.attrib['usePrefix'] = mc.getAttr('%s.usePrefix' % pickerNode) and '1' or '0'
    mapEm.attrib['useBgColor'] = mc.getAttr('%s.useBgColor' % pickerNode) and '1' or '0'


def setButtonInfo(type, pos, size, color, cmd, node, channel, val, label, icon, hashcode, mapEm):
    buttonEm = Element('button')
    buttonEm.attrib['type'] = type
    buttonEm.attrib['position'] = pos
    buttonEm.attrib['color'] = color
    buttonEm.attrib['size'] = size
    if type == 'Group':
        buttonEm.attrib['label'] = label
        splited = cmd.split(';')
        buttonEm.attrib['doKey'] = len(splited) > 1 and splited[0] or 'false'
        buttonEm.attrib['doReset'] = len(splited) > 2 and splited[1] or 'false'
        buttonEm.attrib['labelPos'] = len(splited) > 3 and splited[2] or 'North'
        buttonEm.attrib['buttonPos'] = len(splited) > 4 and splited[3] or 'North'
        buttonEm.attrib['children'] = node
    elif type == 'VisToggle':
        buttonEm.attrib['command'] = cmd
        buttonEm.attrib['targets'] = node
        buttonEm.attrib['execute'] = channel
        buttonEm.attrib['icon'] = icon
    else:
        buttonEm.attrib['command'] = cmd
        splited = node.split('&')
        buttonEm.attrib['node'] = len(splited) > 0 and splited[0] or ''
        buttonEm.attrib['channel'] = channel
        buttonEm.attrib['value'] = val
        buttonEm.attrib['label'] = label
        buttonEm.attrib['icon'] = icon
        buttonEm.attrib['linkedItem'] = len(splited) > 1 and splited[1] or ''
    buttonEm.attrib['hashCode'] = hashcode
    mapEm.append(buttonEm)


def createXMLFromNode(pickerNode, name, path):
    mapEm = Element('map')
    setMapInfo(pickerNode, mapEm, name, path)
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
    for type, pos, size, color, cmd, node, channel, val, label, icon, hashcode in zip(types, positions, sizes, colors, commands, nodes, channels, values, labels, icons, hashcodes):
        iconSplit = icon.split(';')
        if os.path.isfile(iconSplit[0]):
            movPath = os.path.join(os.path.dirname(path), 'images', os.path.basename(iconSplit[0])).replace('\\', '/')
            if os.path.normpath(iconSplit[0]) != os.path.normpath(movPath):
                shutil.copy2(iconSplit[0], movPath)
            iconSplit[0] = movPath
            icon = ';'.join(iconSplit)
        setButtonInfo(type, pos, size, color, cmd, node, channel, val, label, icon, hashcode, mapEm)

    return mapEm


def doSaveNodesToFile(path, pickerNodes, name):
    dataEm = Element('data')
    for node in pickerNodes:
        dataEm.append(createXMLFromNode(node, name, path))

    from const import indentXML
    indentXML(dataEm)
    if module_exists('lxml'):
        ElementTree(dataEm).write(path)
    else:
        with open(path, 'w') as f:
            f.write(tostring(dataEm))
            f.close()


def updateMap(mapEm, charName, namespace):
    mapName = mapEm.get('name')
    pickerNode = mm.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (listToArray(filterPickerNode()), charName, mapName))
    if pickerNode == 'None':
        pickerNode = mm.eval('locusPicker:createMapNode("%s", "%s")' % (charName, mapName))
    mm.eval('locusPicker:assignMapData("%s", "%s", %d, %d, "%s", "%s", %d, "%s");' % (pickerNode,
     mapEm.get('size'),
     0,
     int(mapEm.get('useBgColor')),
     mapEm.get('bgImage'),
     mapEm.get('bgColor'),
     namespace and 1 or int(mapEm.get('usePrefix')),
     namespace or mapEm.get('prefix')))
    return pickerNode


def getButtonsListVars(buttonEm, types, positions, sizes, colors, commands, nodes, channels, values, labels, icons, hashcodes):
    typeStr = buttonEm.get('type')
    types.append(typeStr)
    positions.append(buttonEm.get('position'))
    sizes.append(buttonEm.get('size'))
    colors.append(buttonEm.get('color'))
    if typeStr == 'Group':
        commands.append('')
        nodes.append(buttonEm.get('children'))
        channels.append('')
        values.append('')
        labelStr = ';'.join([buttonEm.get('doKey', 'false'),
         buttonEm.get('doReset', 'false'),
         buttonEm.get('labelPos', 'North'),
         buttonEm.get('buttonPos', 'North')])
        labels.append(labelStr)
        icons.append('')
    elif typeStr == 'VisToggle':
        commands.append(buttonEm.get('command'))
        nodes.append(buttonEm.get('targets'))
        channels.append(buttonEm.get('execute'))
        values.append('')
        labels.append('')
        icons.append(buttonEm.get('icon'))
    else:
        commands.append(buttonEm.get('command'))
        buf = [buttonEm.get('node', '')]
        if buttonEm.get('linkedItem', ''):
            buf.append(buttonEm.get('linkedItem', ''))
        nodes.append('&'.join(buf))
        channels.append(buttonEm.get('channel'))
        values.append(buttonEm.get('value'))
        labels.append(buttonEm.get('label'))
        icons.append(buttonEm.get('icon'))
    hashcodes.append(buttonEm.get('hashCode'))


def doUpdateNodesFromFile(path, name, namespace = '', **kwargs):
    result = []
    try:
        dataEm = parse(path).getroot()
    except:
        raise IOError, 'Error to open file:' + path

    for mapEm in dataEm.getchildren():
        ns = namespace
        if 'suffix' in kwargs:
            mapName = mapEm.get('name')
            for k, v in kwargs['suffix'].items():
                if mapName.endswith(k):
                    ns = v
                    break

        pickerNode = updateMap(mapEm, name, ns)
        types, positions, sizes, colors, commands, nodes, channels, values, labels, icons, hashcodes = ([] for i in xrange(11))
        for buttonEm in mapEm.findall('button'):
            getButtonsListVars(buttonEm, types, positions, sizes, colors, commands, nodes, channels, values, labels, icons, hashcodes)

        mm.eval('locusPicker:assignButtonData("%s", %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' % (pickerNode,
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
        result.append(pickerNode)

    return result


class LocusPickerUI(base_class, LocusPickerLauncherUI, form_class):
    __window__ = None
    __windows__ = []

    def __init__(self, parent = PLATFORM_PARENT, objName = MASTER_WINDOW_NAME):
        self.__bottomMenuVisible = True
        self.__mapMode = True
        self.__workingSize = QSize(400, 400)
        self.__guideWidget = self.__itemEditor = self.__toolDialog = self.__paletteDialog = None
        self.__clipboard = []
        LocusPickerLauncherUI.__init__(self, parent, objName)
        self.bgSnapshot_button.hide()
        return

    def setupUiEnv(self):
        self.replaceToggleButtons()
        self.replaceTabWidget()
        self.replaceBottomMenuWidget()
        self.setupInitPage()
        self.tabPoupMenuBuild()
        self.generateAction()
        self.setToolBarMenu()
        self.restoreIniSettings()
        self.dispatcher = ThreadDispatcher(self)
        self.dispatcher.start()
        self.connectTabSignal()
        self.connectToggleButtonsSignal()
        self.connectTopMenuSignal()
        self.connectBottomMenuSignal()
        self.connectInitPageSignal()
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

    @property
    def clipboard(self):
        return self.__clipboard

    @clipboard.setter
    def clipboard(self, data):
        self.__clipboard[:] = data

    def forceToClose(self, *args):
        self.setWindowModified(False)
        self.close()

    def showItemEditor(self, item):
        if not self.__itemEditor:
            self.__itemEditor = ItemEditor(self)
            self.connectItemEditorSignal()
        self.__itemEditor.setItem(item)
        self.__itemEditor.show(self.isWindowModified())
        self.__itemEditor.setWindowModified(False)
        self.__itemEditor.resize(282, 774)
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('ItemEditor')
        value = settings.value('Position')
        settings.endGroup()
        avaiableGeo = self.getAvailableScreen()
        if value is not None:
            if value.x() > avaiableGeo.left() and value.y() > avaiableGeo.top() + 30:
                return
        self.moveWidgetAccordingToWindow(self.__itemEditor)
        return

    def moveWidgetAccordingToWindow(self, widget):
        rect = self.geometry()
        geometry = widget.geometry()
        geometry.moveTopLeft(rect.topRight() + QPoint(8, 0))
        desktop = QApplication.desktop()
        if desktop.screenNumber(widget) != desktop.screenNumber(self) or not desktop.availableGeometry(widget).contains(geometry):
            geometry.moveRight(rect.left() - 24)
        widget.move(geometry.topLeft() - QPoint(0, 30))

    def refreshItemToItemEditor(self, items):
        if self.__itemEditor and self.__itemEditor.isVisible():
            self.__itemEditor.restoreItem()
            if items:
                self.__itemEditor.setItem(items[0])
            else:
                self.__itemEditor.clearItem()

    def showToolDialog(self):
        if not self.__toolDialog:
            self.__toolDialog = ToolsDialog(self)
            self.connectToolDialogSignal()
        self.__toolDialog.initializeUI()
        self.__toolDialog.resize(420, 329)
        self.__toolDialog.show()
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('ToolDialog')
        value = settings.value('Position')
        settings.endGroup()
        avaiableGeo = self.getAvailableScreen()
        if value is not None:
            if value.x() > avaiableGeo.left() and value.y() > avaiableGeo.top() + 30:
                return
        self.moveWidgetAccordingToWindow(self.__toolDialog)
        return

    def showImageWidget(self):
        from toolsDialog import ImageWidget
        width, height = self.mapWidth_spinBox.value(), self.mapHeight_spinBox.value()
        w = ImageWidget(self)
        w.setWindowFlags(Qt.Tool)
        w.setIconLabelSize(QSize(width + 2, height + 2), QRect(QPoint(1, 1), QSize(width, height)))
        w.availableIconSize_widget.hide()
        w.workType_widget.hide()
        button = QPushButton('Close', w)
        w.imageSnapshot_widget.layout().addWidget(button)
        w.show()
        w.path_lineEdit.textChanged.connect(self.bgImagePath_lineEdit.setText)
        button.clicked.connect(w.close)

    def resizeEvent(self, event):
        super(base_class, self).resizeEvent(event)
        if self.__guideWidget and self.__guideWidget.isVisible():
            self.setGuideWidgetGeometry()

    def eventFilter(self, widget, event):
        if widget == self.upperToolBar.widgetForAction(self.createCharacterAct):
            if event.type() == QEvent.ContextMenu:
                menu = QMenu(self)
                loadFileAct = menu.addAction('Load Map File')
                loadFileAct.triggered.connect(self.loadDataFromFile)
                menu.exec_(event.globalPos())
        elif widget == self.upperToolBar.widgetForAction(self.assignDataToNodeAct):
            if event.type() == QEvent.ContextMenu:
                menu = QMenu(self)
                saveMapAct = menu.addAction('Save Current Map to File')
                saveAllMapsAct = menu.addAction('Save All Maps to Files')
                saveMapAct.triggered.connect(self.saveCurrentToFile)
                saveAllMapsAct.triggered.connect(self.saveAllMapToFiles)
                menu.exec_(event.globalPos())
        return super(base_class, self).eventFilter(widget, event)

    def connectTabSignal(self):
        LocusPickerLauncherUI.connectTabSignal(self)
        self.tabWidget.tabAdded.connect(self.checkCharacterName)
        self.tabWidget.addItemOn.connect(self.addDropItems)
        self.tabWidget.addItemWithSet.connect(self.addItemFromToolDialog)
        self.tabWidget.addPreviewedItem.connect(self.addItemFromSet)
        self.tabWidget.redefineMember.connect(self.redefineMember)
        self.tabWidget.changeMember.connect(self.changeMember)
        self.tabWidget.editRemote.connect(self.showItemEditor)
        self.tabWidget.windowModified.connect(lambda : self.setWindowModified(True))
        self.tabWidget.tabLabelRenamed.connect(self.syncNodeSubset)
        self.tabWidget.tabRemovedText.connect(self.removeNode)
        self.tabWidget.undoOpen.connect(lambda : undoOpenClose(True))
        self.tabWidget.undoClose.connect(lambda : undoOpenClose(False))
        self.tabWidget.saveToFile.connect(self.saveDataToFile)
        self.tabWidget.selectedItemsChanged.connect(self.refreshItemToItemEditor)
        self.tabWidget.copyItems.connect(lambda x: setattr(self, 'clipboard', x))

    def connectToggleButtonsSignal(self):
        LocusPickerLauncherUI.connectToggleButtonsSignal(self)
        self.bottomMenuToggleButton.clicked.connect(self.toggleBottomMenu)

    def connectTopMenuSignal(self):
        LocusPickerLauncherUI.connectTopMenuSignal(self)
        self.characterLineEdit.labelRenamed.connect(self.syncNodeCharacter)

    def connectBottomMenuSignal(self):
        self.colorButton.clicked.connect(lambda : self.showColorPicker(self.colorButton))
        self.geo_toolButton.clicked.connect(self.convertMapToGeo)
        self.map_toolButton.clicked.connect(self.convertGeoToMap)
        self.alignHorizontal_Button.clicked.connect(lambda : self.alignSelectedByMode('horizontal'))
        self.alignVertical_Button.clicked.connect(lambda : self.alignSelectedByMode('vertical'))
        self.averageGapX_Button.clicked.connect(lambda : self.setAverageGapByMode('X'))
        self.averageGapY_Button.clicked.connect(lambda : self.setAverageGapByMode('Y'))
        self.toolBox_button.clicked.connect(self.showToolDialog)
        self.bringFront_Button.clicked.connect(lambda : self.arrangeSelectedItems('bringFront'))
        self.bringToForward_Button.clicked.connect(lambda : self.arrangeSelectedItems('bringForward'))
        self.sendToBackward_Button.clicked.connect(lambda : self.arrangeSelectedItems('sendBackward'))
        self.sendBack_Button.clicked.connect(lambda : self.arrangeSelectedItems('sendBack'))

    def connectItemEditorSignal(self):
        self.__itemEditor.itemModified.connect(self.setWindowModified)
        self.__itemEditor.colorPick.connect(self.showColorPicker)

    def connectToolDialogSignal(self):
        self.__toolDialog.colorPick.connect(self.showColorPicker)
        self.__toolDialog.mapToGeo_Button.clicked.connect(self.convertMapToGeo)
        self.__toolDialog.geoToMap_Button.clicked.connect(self.convertGeoToMap)
        self.__toolDialog.deleteAll_Button.clicked.connect(self.deleteAllGeoButtons)
        self.__toolDialog.alignLeft_Button.clicked.connect(lambda : self.alignSelectedByMode('left'))
        self.__toolDialog.alignRight_Button.clicked.connect(lambda : self.alignSelectedByMode('right'))
        self.__toolDialog.alignTop_Button.clicked.connect(lambda : self.alignSelectedByMode('top'))
        self.__toolDialog.alignBottom_Button.clicked.connect(lambda : self.alignSelectedByMode('bottom'))
        self.__toolDialog.alignHorizontal_Button.clicked.connect(lambda : self.alignSelectedByMode('horizontal'))
        self.__toolDialog.alignVertical_Button.clicked.connect(lambda : self.alignSelectedByMode('vertical'))
        self.__toolDialog.bringFront_Button.clicked.connect(lambda : self.arrangeSelectedItems('bringFront'))
        self.__toolDialog.bringToForward_Button.clicked.connect(lambda : self.arrangeSelectedItems('bringForward'))
        self.__toolDialog.sendToBackward_Button.clicked.connect(lambda : self.arrangeSelectedItems('sendBackward'))
        self.__toolDialog.sendBack_Button.clicked.connect(lambda : self.arrangeSelectedItems('sendBack'))
        self.__toolDialog.moveToHCenter_Button.clicked.connect(lambda : self.moveSelectedItemsToCenter('hor'))
        self.__toolDialog.moveToVCenter_Button.clicked.connect(lambda : self.moveSelectedItemsToCenter('ver'))
        self.__toolDialog.averageWidth_Button.clicked.connect(lambda : self.setAverageSizeByMode('X'))
        self.__toolDialog.averageHeight_Button.clicked.connect(lambda : self.setAverageSizeByMode('Y'))
        self.__toolDialog.averageGapX_Button.clicked.connect(lambda : self.setAverageGapByMode('X'))
        self.__toolDialog.averageGapY_Button.clicked.connect(lambda : self.setAverageGapByMode('Y'))
        self.__toolDialog.mirrorButtons.connect(self.mirrorButtonsByMode)

    def connectInitPageSignal(self):
        self.initCancel_button.clicked.connect(self.cancelInitPage)
        self.stackedWidget.currentChanged.connect(self.checkMainPage)
        self.bgColor_button.clicked.connect(lambda : self.showColorPicker(self.bgColor_button))
        self.bgColor_button.colorChanged.connect(lambda x: self.bgColorValue_slider.setValue(x.value()))
        self.bgColorValue_slider.valueChanged.connect(lambda x: self.changeButtonColorValue(self.bgColor_button, x))
        self.bgImagePathBrowse_button.clicked.connect(lambda : self.showImageBrowser(self.bgImagePath_lineEdit, self.bgImagePath_lineEdit.text()))
        self.info_button.clicked.connect(self.openInfoDocumentUrl)
        self.bgSnapshot_button.clicked.connect(self.showImageWidget)

    def savePalettePos(self):
        if self.__paletteDialog:
            settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
            settings.beginGroup('Window')
            settings.setValue('PalettePosition', self.__paletteDialog.pos())
            settings.endGroup()

    def generateAction(self):
        LocusPickerLauncherUI.generateAction(self)
        from const import CREATE_CHAR_TIP, EDIT_MAP_TIP, SAVE_NODE_TIP, SAVE_FILE_TIP
        self.createCharacterAct = self.createAction('Create Character', self.createCharacter, icon=':/create', tip=CREATE_CHAR_TIP)
        self.editCurrentMapAct = self.createAction('Edit Current Map', self.editCurrentMap, icon=':/edit', disable=True, tip=EDIT_MAP_TIP)
        self.assignDataToNodeAct = self.createAction('Assign Data to Node', self.assignDataToNode, icon=':/save_hilite', disable=':/save_disabled', tip=SAVE_NODE_TIP)
        self.assignDataToNodeAct.setEnabled(False)
        self.saveTabToFileAct = self.createAction('Save Map File', self.saveCurrentToFile, icon=':/save', disable=True, tip=SAVE_FILE_TIP)

    def setUpperToolBarMenu(self):
        for act in [self.createCharacterAct,
         self.editCurrentMapAct,
         self.assignDataToNodeAct,
         self.infoAct,
         self.refreshAct]:
            self.upperToolBar.addAction(act)
            self.upperToolBar.widgetForAction(act).setFixedSize(24, 24)

        self.setUpperCommonActions()
        self.upperToolBar.widgetForAction(self.createCharacterAct).installEventFilter(self)
        self.upperToolBar.widgetForAction(self.assignDataToNodeAct).installEventFilter(self)

    def setCurrentTabSize(self):
        self.mapSizeWidget.setSize(self.tabWidget.sceneAtIndex(self.tabWidget.currentIndex()).mapSize)

    def setWindowModified(self, modified):
        super(base_class, self).setWindowModified(modified)
        self.assignDataToNodeAct.setEnabled(modified)

    @property
    def bottomMenuVisible(self):
        return self.__bottomMenuVisible

    @bottomMenuVisible.setter
    def bottomMenuVisible(self, visible):
        doResize = isinstance(self.sender(), QToolButton) or self.tabWidget.count()
        adjustHeight = self.bottomMenuWidget.height()
        if visible:
            isModified = self.isWindowModified()
            self.bottomMenuWidget.show()
            if doResize:
                self.resize(self.width(), self.height() + adjustHeight)
            self.bottomMenuToggleButton.upsideDown = False
            if not isModified:
                self.setWindowModified(False)
        else:
            self.bottomMenuWidget.hide()
            if doResize:
                self.resize(self.width(), self.height() - adjustHeight)
            self.bottomMenuToggleButton.upsideDown = True
        self.__bottomMenuVisible = visible

    def toggleTopMenu(self):
        self.topMenuVisible = not self.topMenuVisible
        if self.__guideWidget and self.__guideWidget.isVisible():
            self.setGuideWidgetGeometry()

    def toggleBottomMenu(self):
        self.bottomMenuVisible = not self.bottomMenuVisible

    def replaceToggleButtons(self):
        LocusPickerLauncherUI.replaceToggleButtons(self)
        self.bottomMenuToggleButton = self.replaceWidget(self.bottomMenuToggle_layout, self.bottomMenuToggleButton, ArrowToggleButton)
        if INMAYA > 2015:
            self.bottomMenuToggle_layout.setContentsMargins(1, 1, 1, 0)

    def replaceTabWidget(self):
        self.tabWidget = self.replaceWidget(self.tabWidget.parent().layout(), self.tabWidget, EditableTabWidget)

    def replaceBottomMenuWidget(self):
        self.geo_toolButton.hide()
        self.map_toolButton.hide()
        layout = self.bottomMenuLayout
        self.colorButton = self.replaceWidget(layout, self.colorButton, ColorButton)
        self.bringFront_Button = self.replaceWidget(layout, self.bringFront_Button, HoverIconButton, [':/bringFront', ':/bringFront_hover'])
        self.bringToForward_Button = self.replaceWidget(layout, self.bringToForward_Button, HoverIconButton, [':/bringForward', ':/bringForward_hover'])
        self.sendToBackward_Button = self.replaceWidget(layout, self.sendToBackward_Button, HoverIconButton, [':/sendBackward', ':/sendBackward_hover'])
        self.sendBack_Button = self.replaceWidget(layout, self.sendBack_Button, HoverIconButton, [':/sendBack', ':/sendBack_hover'])
        self.alignHorizontal_Button = self.replaceWidget(layout, self.alignHorizontal_Button, HoverIconButton, [':/alignVCenter', ':/alignVCenter_hover'])
        self.alignVertical_Button = self.replaceWidget(layout, self.alignVertical_Button, HoverIconButton, [':/alignHCenter', ':/alignHCenter_hover'])
        self.averageGapX_Button = self.replaceWidget(layout, self.averageGapX_Button, HoverIconButton, [':/avgGapX', ':/avgGapX_hover'])
        self.averageGapY_Button = self.replaceWidget(layout, self.averageGapY_Button, HoverIconButton, [':/avgGapY', ':/avgGapY_hover'])
        self.toolBox_button = self.replaceWidget(layout, self.toolBox_button, HoverIconButton, [':/tool', ':/tool_hover'])
        from const import TOOL_DIALOG_TIP
        self.toolBox_button.setToolTip(TOOL_DIALOG_TIP)

    def setupInitPage(self):
        self.useBG_buttonGrp = QButtonGroup(self)
        self.useBG_buttonGrp.addButton(self.BGcolorOnly_radioButton, 0)
        self.useBG_buttonGrp.addButton(self.useBGimage_radioButton, 1)
        self.bgColor_button = self.replaceWidget(self.bgColor_layout, self.bgColor_button, ColorButton)
        self.bgColor_button.enableDragDrop(False)
        from const import DEF_MAPBGCOLOR, INFO_TIP, setButtonColor
        setButtonColor(self.bgColor_button, *DEF_MAPBGCOLOR.getRgbF()[:3])
        self.bgColorValue_slider.setValue(DEF_MAPBGCOLOR.value())
        self.info_button.setToolTip(INFO_TIP)

    def checkMainPage(self):
        if not self.__guideWidget:
            self.createGuideWidget()
        if self.stackedWidget.currentIndex() == 0 and not self.characterName():
            self.__guideWidget.show()
            self.setGuideWidgetGeometry()
            self.saveTabToFileAct.setEnabled(False)
            self.editCurrentMapAct.setEnabled(False)
        else:
            self.__guideWidget.hide()
            self.saveTabToFileAct.setEnabled(True)
            self.editCurrentMapAct.setEnabled(True)

    def createGuideWidget(self):
        guideUIFilePath = os.path.join(os.path.dirname(__file__), 'resources', 'guideWidget.ui')
        loader = QUiLoader()
        self.__guideWidget = loader.load(guideUIFilePath, self)
        self.__guideWidget.hide()

    def setGuideWidgetGeometry(self):
        if self.topMenuVisible:
            h = self.upperToolBar.height()
            self.__guideWidget.stackedWidget.setCurrentIndex(1)
        else:
            h = self.topMenuToggleButton.height()
            self.__guideWidget.stackedWidget.setCurrentIndex(0)
        size = self.size()
        self.__guideWidget.setGeometry(0, h, size.width(), size.height() - h)

    def closeEvent(self, event):
        if not self.checkUnsaved():
            event.ignore()
        else:
            super(base_class, self).closeEvent(event)
            if self.__toolDialog:
                self.__toolDialog.close()
            if self.__itemEditor:
                self.__itemEditor.saveIniSettings()

    def saveIniSettings(self):
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('Window')
        geometry = self.geometry()
        avaiableGeo = self.getAvailableScreen()
        if geometry.top() < avaiableGeo.top() + 30:
            geometry.moveTop(avaiableGeo.top() + 30)
        if geometry.left() < avaiableGeo.left() + 8:
            geometry.moveLeft(avaiableGeo.left() + 8)
        if self.stackedWidget.currentIndex():
            geometry.setSize(self.__workingSize)
        settings.setValue('Geometry', geometry)
        settings.setValue('State', self.saveState())
        settings.setValue('RecentDirectory', self.recentDirectory)
        if self.__paletteDialog:
            settings.setValue('PalettePosition', self.__paletteDialog.pos())
        settings.endGroup()
        settings.beginGroup('Menu')
        settings.setValue('ButtonColor', self.colorButton.color())
        settings.setValue('ButtonMode', self.commandTypeComboBox.currentText())
        settings.setValue('TopMenuVisible', self.topMenuVisible)
        settings.setValue('BottomMenuVisible', self.bottomMenuVisible)
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
        settings.beginGroup('Menu')
        value = settings.value('ButtonColor')
        if value is not None:
            self.colorButton.setColor(value)
        value = settings.value('ButtonMode')
        if value is not None:
            self.commandTypeComboBox.setCurrentIndex(max(0, self.commandTypeComboBox.findText(value)))
        value = settings.value('TopMenuVisible')
        if value is not None:
            if isinstance(value, bool):
                self.topMenuVisible = value
            else:
                self.topMenuVisible = ast.literal_eval(value.capitalize())
        value = settings.value('BottomMenuVisible')
        if value is not None:
            if isinstance(value, bool):
                self.bottomMenuVisible = value
            else:
                self.bottomMenuVisible = ast.literal_eval(value.capitalize())
        settings.endGroup()
        return

    def checkUnsaved(self):
        if self.isWindowModified():
            localeText = LocaleText(self.locale())
            yesOrNo = confirm(localeText('NotSavedMessage'), localeText('NotSavedTitle'), parent=self)
            if yesOrNo == 1:
                self.assignDataToNode()
            elif yesOrNo == 0:
                return False
        return True

    def determinePage(self):
        pickerNodes = filterPickerNode()
        if pickerNodes:
            self.stackedWidget.setCurrentIndex(0)
            self.resize(self.__workingSize)
        else:
            self.moveToInitPage()
        return pickerNodes

    def resizeToTab(self, size):
        margin = self.verticalLayout.contentsMargins()
        w = margin.left() + margin.right()
        h = margin.top() + margin.bottom() + self.topMenuToggleButton.height() + self.bottomMenuToggleButton.height()
        margin = self.topMenuToggle_layout.contentsMargins()
        h += margin.top() + margin.bottom()
        margin = self.bottomMenuToggle_layout.contentsMargins()
        h += margin.top() + margin.bottom()
        if self.topMenuVisible:
            h += self.upperToolBar.height() + self.lowerToolBar.height()
        if self.bottomMenuVisible:
            h += self.bottomMenuWidget.height()
        self.resize(size + QSize(w, h))

    def showColorPicker(self, colorButton):
        modifier = QApplication.keyboardModifiers()
        buttonColor = colorButton.color()
        if modifier == Qt.NoModifier:
            returnStr = mc.colorEditor(rgb=buttonColor.getRgbF()[:3])
            colorValues = [ ast.literal_eval(c) for c in returnStr.split() ]
            if colorValues[-1]:
                colorButton.setColor(QColor.fromRgbF(*colorValues[:3]))
        elif modifier == Qt.ControlModifier and (not self.__toolDialog or colorButton != self.__toolDialog.customColor_button):
            if not self.__paletteDialog:
                self.__paletteDialog = ColorPaletteDialog(self)
                self.__paletteDialog.saveINI.connect(self.savePalettePos)
                settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
                settings.beginGroup('Window')
                value = settings.value('PalettePosition')
                if value is not None:
                    self.__paletteDialog.move(value)
                settings.endGroup()
            self.__paletteDialog.clearSelection()
            self.__paletteDialog.show()
            self.__paletteDialog.designatedButton = colorButton
            settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
            settings.beginGroup('Window')
            value = settings.value('PalettePosition')
            settings.endGroup()
            avaiableGeo = self.getAvailableScreen()
            if value is not None:
                if value.x() > avaiableGeo.left() and value.y() > avaiableGeo.top() + 30:
                    return
            self.moveWidgetAccordingToWindow(self.__paletteDialog)
        return

    def changeButtonColorValue(self, button, value):
        hue = button.color().hue()
        sat = button.color().saturation()
        button.setColor(QColor.fromHsv(hue, sat, value))

    def setItemCommand(self, item):
        item.command = self.commandTypeComboBox.currentText()
        self.defineMember(item)

    def redefineMember(self, item):
        if not question('Are you sure to re-define the members?', 'Re-define Members', self):
            return
        if mc.ls(sl=1):
            if item.command in ('Toggle', 'Range'):
                if not self.getSelectedChannel():
                    warn('Please select attributes in Channel Box first, then try again.', parent=self)
            self.defineMember(item)
            self.setWindowModified(True)
        else:
            warn('Please select nodes first, then try again.', parent=self)

    def checkChangeMember(self, cmd, subCmd, item, keepObject, selected = None, selectedChannel = None):
        selected = mc.ls(sl=1)
        selectedChannel = self.getSelectedChannel()
        if cmd in ('Select', 'Key', 'Toggle', 'Reset', 'Range', 'Pose'):
            if not keepObject:
                if not selected:
                    return warn('Please select nodes first, then try again.', parent=self)
                else:
                    item.targetNode = selected
                    return True
        if (subCmd == 'Selected' or cmd in ('Toggle', 'Range')) and not selectedChannel:
            return warn('Please select attributes in Channel Box first, then try again.', parent=self)
        return True

    def reassignMember(self, item, itemType, cmd, subCmd, script, selectedChannel):
        if cmd in ('Select', 'Key', 'Toggle', 'Reset', 'Range', 'Pose'):
            item.command = cmd
            if subCmd in ('Move', 'Rotate', 'Scale'):
                item.command += ' ' + subCmd
            elif subCmd == 'Selected' or cmd in ('Toggle', 'Range'):
                item.targetChannel = selectedChannel
            elif subCmd == 'Transform':
                item.targetChannel = ['tx',
                 'ty',
                 'tz',
                 'rx',
                 'ry',
                 'rz',
                 'sx',
                 'sy',
                 'sz']
            elif subCmd == '':
                item.targetChannel = self.getKeyableAttr(item.targetNode, item.command)
            if item.command == 'Pose':
                self.defineValue(item, item.targetNode, item.targetChannel)
        elif cmd in ('Reference', 'Outliner', 'Graph', 'Dope', 'Custom'):
            if cmd == 'Reference':
                item.command = 'EXEC ReferenceEditor'
            elif cmd == 'Outliner':
                item.command = 'EXEC OutlinerWindow'
            elif cmd == 'Graph':
                item.command = 'EXEC GraphEditor'
            elif cmd == 'Dope':
                item.command = 'EXEC DopeSheetEditor'
            else:
                item.command = 'EXEC ' + script
            item.clearNodeChannleValue()
        elif itemType == DropItemType.EditableRectangleSlider and cmd == 'Slider':
            if subCmd == 'Right':
                item.changeSliderAttachment('Right')
            elif subCmd == 'Left':
                item.changeSliderAttachment('Left')
            elif subCmd == 'Below':
                item.changeSliderAttachment('Bottom')
            elif subCmd == 'Above':
                item.changeSliderAttachment('Top')
        else:
            if cmd == 'Visibility':
                return True
            return warn("Can't change %s button to %s" % (getTypeString(item.type()), cmd + ' ' + subCmd))
        return True

    def getReplacableItemType(self, itemType, cmd):
        if cmd == 'Visibility' and itemType != DropItemType.EditableVisToggle:
            return 'VisToggle'
        if itemType == DropItemType.EditableRectangleSlider and cmd not in ('Pose', 'Range', 'Slider'):
            if cmd == 'No':
                return 'DragPose'
            else:
                return 'Rectangle'
        elif itemType == DropItemType.EditableDragPose and cmd not in ('Pose', 'No'):
            if cmd in ('Slider', 'Range'):
                return 'RectangleSlider'
            else:
                return 'Rectangle'
        elif itemType == DropItemType.EditableRectangle and cmd in ('Range', 'Pose', 'Slider'):
            if cmd in ('Pose',):
                return 'DragPose'
            elif cmd in ('No', 'Slider'):
                return ''
            else:
                return 'RectangleSlider'
        return ''

    def replaceItemType(self, item, replaceType, cmd, subCmd):
        parentItem = item.parentItem()
        if parentItem:
            item.setParentItem(None)
        values = item.properties()
        scene = item.scene()
        values['type'] = replaceType
        iconPath = values['iconPath']
        del values['iconPath']
        iconRect = values['iconRect']
        del values['iconRect']
        values['icon'] = [iconPath, iconRect]
        label = values['label']
        del values['label']
        labelRect = values['labelRect']
        del values['labelRect']
        font = values['font']
        del values['font']
        values['label'] = [label, labelRect, font]
        values['pos'] = item.pos()
        if replaceType == 'VisToggle':
            values['path'] = item.shape()
            values['command'] = cmd + ' ' + subCmd
        else:
            values['node'] = values['targetNode']
            del values['targetNode']
            values['channel'] = values['targetChannel']
            del values['targetChannel']
            values['value'] = values['targetValue']
            del values['targetValue']
            if replaceType in ('RectangleSlider', 'DragPose'):
                if values['width'] < 40:
                    values['width'] = 40
                if values['height'] < 40:
                    values['height'] = 40
            if cmd == 'Slider':
                if subCmd == 'Below':
                    subCmd = 'Bottom'
                elif subCmd == 'Above':
                    subCmd = 'Top'
                values['attach'] = Attachment.getAttachment(subCmd)
        newItem = scene.addVarsItem(**values)
        scene.removeItem(item)
        return newItem

    def changeMember(self, item, command, keepObject, script):
        if item.type() == DropItemType.EditableVisToggle:
            if command == 'Custom' and script:
                item.editCommand(script)
            else:
                print "Can't change VisToggle yet."
            return
        itemType = item.type()
        splited = command.split()
        cmd = splited[0]
        if len(splited) > 1:
            subCmd = splited[1]
        else:
            subCmd = ''
        selected = []
        selectedChannel = []
        if not self.checkChangeMember(cmd, subCmd, item, keepObject, selected, selectedChannel):
            return
        if not self.reassignMember(item, itemType, cmd, subCmd, script, selectedChannel):
            return
        replaceType = self.getReplacableItemType(itemType, cmd)
        if replaceType:
            self.replaceItemType(item, replaceType, cmd, subCmd)
        self.setWindowModified(True)

    def defineMember(self, item, channel = None):
        try:
            item.targetNode = mc.ls(sl=1) or []
            if channel:
                item.targetChannel = channel[:]
            else:
                self.defineChannel(item, item.targetNode)
            self.defineValue(item, item.targetNode, item.targetChannel)
        except StandardError:
            traceback.print_exc()

    def defineChannel(self, item, nodes, channel = None):
        if not channel:
            channel = nodes and self.getKeyableAttr(nodes, item.command) or []
        item.targetChannel = channel

    def defineValue(self, item, nodes, channel):
        if item.command == 'Pose':
            dataBlock = []
            for node in nodes:
                dataBuffer = []
                for ch in channel:
                    if mc.objExists(node + '.' + ch):
                        value = mc.getAttr('%s.%s' % (node, ch))
                        if value is not None:
                            if isinstance(value, bool):
                                value = value and 1.0 or 0.0
                            dataBuffer.append(value)
                        else:
                            dataBuffer.append(0)
                    else:
                        dataBuffer.append(0)

                dataBlock.append(dataBuffer)

            item.targetValue = dataBlock
        return

    def getKeyableAttr(self, nodes, commandType):
        if commandType == 'Select':
            return []
        else:
            channel = self.getSelectedChannel()
            if channel is None:
                if commandType == 'Pose':
                    channel = []
                    for node in nodes:
                        channelBuf = mc.listAttr(node, k=1, s=1, sn=1)
                        if channelBuf is not None:
                            for ch in channelBuf:
                                if ch not in channel:
                                    channel.append(ch)

                else:
                    channel = []
            return channel

    def doWorkForScene(self, var):
        if var == 'Channel':
            self.checkProperChannel()
        elif var == 'Shape':
            self.checkItemShape()
        else:
            self.tabWidget.currentScene().wait = WaitState.Proceed

    def checkProperChannel(self, command = ''):
        try:
            if not command:
                command = self.commandTypeComboBox.currentText()
            if command in ('Select', 'Key', 'Reset', 'Pose'):
                return True
            if command in ('Toggle', 'Range'):
                channels = self.getSelectedChannel()
                if channels:
                    node = mc.ls(sl=1)[0]
                    for ch in channels:
                        if not mc.attributeQuery(ch, n=node, re=1):
                            return warn('Attribute does not have a range : ' + ch, parent=self)

                    return True
                else:
                    return warn('Please select attributes in Channel Box first, then try again.', parent=self)
        except:
            traceback.print_exc()
            return False

    def addDropItems(self, pos, color, modifier):
        try:
            selected = mc.ls(sl=1)
        except:
            selected = []

        if not self.checkProperChannel():
            return
        scene = self.tabWidget.currentScene()
        commandType = self.commandTypeComboBox.currentText()
        if commandType != 'Select' and not selected:
            return warn('Please select nodes first, then try again.', parent=self)
        if commandType in ('Select', 'Toggle', 'Key', 'Reset'):
            itemType = 'Rectangle'
        elif commandType == 'Pose':
            itemType = 'DragPose'
        else:
            itemType = 'RectangleSlider'
        if itemType == 'Rectangle':
            self.doAddItems(itemType, selected, scene, modifier, pos, color, commandType)
        else:
            self.doAddItems(itemType, selected, scene, modifier, pos, color, commandType, attach=Attachment.TOP)
        self.setWindowModified(True)

    def addItemFromToolDialog(self, pos, color, command, data):
        try:
            selected = mc.ls(sl=1)
        except:
            selected = []

        if not self.checkProperChannel(command):
            return
        else:
            scene = self.tabWidget.currentScene()
            if command in ('Select', 'Toggle', 'Key', 'Reset'):
                itemType = 'Rectangle'
            else:
                itemType = 'RectangleSlider'
            numberOfButtons = data.get('NumberOfButtons', 'One')
            if numberOfButtons == 'One':
                modifier = Qt.NoModifier
            elif numberOfButtons == 'Multi Horizontal':
                modifier = Qt.AltModifier
            elif numberOfButtons == 'Multi Vertical':
                modifier = Qt.ControlModifier
            elif numberOfButtons == 'Capture':
                modifier = Qt.AltModifier | Qt.ControlModifier
            sliderPosition = data.get('SliderPosition', 'Right')
            if sliderPosition == 'No Slider':
                itemType = 'Rectangle'
                attach = None
            elif sliderPosition == 'Right':
                attach = Attachment.RIGHT
            elif sliderPosition == 'Left':
                attach = Attachment.LEFT
            elif sliderPosition == 'Below':
                attach = Attachment.BOTTOM
            elif sliderPosition == 'Above':
                attach = Attachment.TOP
            changeTool = data.get('ChangeTool', 'No Change')
            if changeTool == 'Move tool':
                command += ' Move'
            elif changeTool == 'Rotate tool':
                command += ' Rotate'
            elif changeTool == 'Scale tool':
                command += ' Scale'
            attributeOption = data.get('AttributeOption', 'All Keyable')
            if attributeOption == 'Transform only':
                channel = ['tx',
                 'ty',
                 'tz',
                 'rx',
                 'ry',
                 'rz',
                 'sx',
                 'sy',
                 'sz']
            elif attributeOption == 'Selected only':
                channel = self.getSelectedChannel()
                if not channel:
                    return warn('Please select attributes in Channel Box first, then try again.', parent=warn)
            else:
                channel = []
            self.doAddItems(itemType, selected, scene, modifier, pos, color, command, attach, channel)
            self.setWindowModified(True)
            return

    def addItemFromSet(self, pos, color, command, data):
        selected = mc.ls(sl=True)
        if command != 'Select' and not selected:
            return warn('Please select nodes first, then try again.', parent=self)
        if not self.checkProperChannel(command):
            return
        scene = self.tabWidget.currentScene()
        if command in ('Select', 'Toggle', 'Key', 'Reset'):
            itemType = 'Rectangle'
        elif command == 'Pose' and data['attach'] == 0:
            itemType = 'DragPose'
        else:
            itemType = 'RectangleSlider'
        if 'AttributeOption' in data:
            attributeOption = data['AttributeOption']
            del data['AttributeOption']
        else:
            attributeOption = 'All Keyable'
        if attributeOption == 'Transform only':
            channel = ['tx',
             'ty',
             'tz',
             'rx',
             'ry',
             'rz',
             'sx',
             'sy',
             'sz']
        elif attributeOption == 'Selected only':
            channel = self.getSelectedChannel()
            if not channel:
                return warn('Please select attributes in Channel Box first, then try again.', parent=self)
        else:
            channel = []
        if 'ChangeTool' in data:
            changeTool = data['ChangeTool']
            del data['ChangeTool']
            if changeTool == 'Move tool':
                command += ' Move'
            elif changeTool == 'Rotate tool':
                command += ' Rotate'
            elif changeTool == 'Scale tool':
                command += ' Scale'
        if 'width' in data and 'height' in data:
            w = data['width']
            del data['width']
            h = data['height']
            del data['height']
            data['size'] = [w, h]
        if 'NumberOfButtons' in data:
            numberOfButtons = data['NumberOfButtons']
            del data['NumberOfButtons']
        else:
            numberOfButtons = 'One'
        if numberOfButtons == 'One':
            self.addSingleButton(itemType, selected, scene, pos, color, command, channel, **data)
        elif selected:
            if numberOfButtons == 'Multi Horizontal':
                self.addButtonHorizontally(itemType, selected, scene, pos, color, command, channel, **data)
            elif numberOfButtons == 'Multi Vertical':
                self.addButtonVertically(itemType, selected, scene, pos, color, command, channel, **data)
            elif numberOfButtons == 'Capture':
                self.addButtonMayaCapture(itemType, selected, scene, pos, color, command, channel, **data)
        else:
            return warn('You have to select targets', parent=self)
        self.setWindowModified(True)

    def doAddItems(self, itemType, selected, scene, modifier, pos, color, commandType, attach = None, channel = None):
        if channel is None:
            channel = []
        if modifier == Qt.NoModifier:
            self.addSingleButton(itemType, selected, scene, pos, color, commandType, channel, attach=attach)
        elif modifier == Qt.AltModifier:
            if not selected:
                return warn('Please select nodes first, then try again.', parent=self)
            self.addButtonHorizontally(itemType, selected, scene, pos, color, commandType, attach=attach, channel=channel)
        elif modifier == Qt.ControlModifier:
            if not selected:
                return warn('Please select nodes first, then try again.', parent=self)
            self.addButtonVertically(itemType, selected, scene, pos, color, commandType, attach=attach, channel=channel)
        elif modifier & Qt.AltModifier and modifier & Qt.ControlModifier:
            if not selected:
                return warn('Please select nodes first, then try again.', parent=self)
            self.addButtonMayaCapture(itemType, selected, scene, pos, color, commandType, attach=attach, channel=channel)
        return

    def addSingleButton(self, itemType, selected, scene, pos, color, commandType, channel = None, **kwargs):
        if channel is None:
            channel = []
        if itemType == 'Rectangle' or itemType == 'DragPose':
            item = scene.addVarsItem(type=itemType, pos=pos, color=color, command=commandType, **kwargs)
        elif itemType == 'RectangleSlider':
            if 'attach' not in kwargs:
                kwargs['attach'] = Attachment.NotValid
            if 'backward' not in kwargs:
                kwargs['backward'] = False
            if 'size' not in kwargs:
                if Attachment.isHorizontal(kwargs['attach']):
                    kwargs['size'] = [40, 60]
                elif Attachment.isVertical(kwargs['attach']):
                    kwargs['size'] = [60, 40]
                else:
                    kwargs['size'] = [60, 60]
            item = scene.addVarsItem(type=itemType, pos=pos, color=color, command=commandType, **kwargs)
        self.defineMember(item, channel)
        return

    def addButtonHorizontally(self, itemType, selected, scene, pos, color, commandType, channel = None, **kwargs):
        if channel is None:
            channel = []
        selected.sort(key=lambda x: mc.xform(x, q=1, ws=1, rp=1)[0])
        if itemType == 'Rectangle':
            if 'size' in kwargs:
                size = kwargs['size']
            else:
                size = kwargs.setdefault('size', [20, 20])
        elif itemType == 'RectangleSlider':
            if 'attach' not in kwargs or kwargs['attach'] == None:
                kwargs['attach'] = Attachment.NotValid
            if 'backward' not in kwargs:
                kwargs['backward'] = False
            if 'size' in kwargs:
                size = kwargs['size']
            elif Attachment.isHorizontal(kwargs['attach']):
                size = kwargs.setdefault('size', [40, 60])
            elif Attachment.isVertical(kwargs['attach']):
                size = kwargs.setdefault('size', [60, 40])
            else:
                size = kwargs.setdefault('size', [60, 60])
        pos = scene.enlargeUptoUnited(pos, QRectF(pos, QSizeF(size[0] * len(selected) + 3 * (len(selected) - 1), size[1])))
        if pos is None:
            return
        else:
            for sel in selected:
                item = self.addItemToScene(scene, itemType, pos, sel, color, commandType, channel, **kwargs)
                pos = item.sceneBoundingRect().topRight() + QPointF(3, 0)

            return

    def addButtonVertically(self, itemType, selected, scene, pos, color, commandType, channel = None, **kwargs):
        if channel is None:
            channel = []
        selected.sort(key=lambda x: mc.xform(x, q=1, ws=1, rp=1)[1], reverse=True)
        if itemType == 'Rectangle':
            if 'size' in kwargs:
                size = kwargs['size']
            else:
                size = kwargs.setdefault('size', [20, 20])
        elif itemType == 'RectangleSlider':
            if 'attach' not in kwargs or kwargs['attach'] == None:
                kwargs['attach'] = Attachment.NotValid
            if 'backward' not in kwargs:
                kwargs['backward'] = False
            if 'size' in kwargs:
                size = kwargs['size']
            elif Attachment.isHorizontal(kwargs['attach']):
                size = kwargs.setdefault('size', [40, 60])
            elif Attachment.isVertical(kwargs['attach']):
                size = kwargs.setdefault('size', [60, 40])
            else:
                size = kwargs.setdefault('size', [60, 60])
        pos = scene.enlargeUptoUnited(pos, QRectF(pos, QSizeF(size[0], size[1] * len(selected) + 3 * (len(selected) - 1))))
        if pos is None:
            return
        else:
            for sel in selected:
                item = self.addItemToScene(scene, itemType, pos, sel, color, commandType, channel, **kwargs)
                pos = item.sceneBoundingRect().bottomLeft() + QPointF(0, 3)

            return

    def addButtonMayaCapture(self, itemType, selected, scene, pos, color, commandType, channel = None, **kwargs):
        if channel is None:
            channel = []
        camera = mm.eval('locusPicker:getActiveCamera()')
        if not camera:
            print 'Camera Error'
            return
        else:
            if itemType == 'Rectangle':
                if 'size' in kwargs:
                    size = kwargs['size']
                else:
                    size = kwargs.setdefault('size', [20, 20])
            elif itemType == 'RectangleSlider':
                if 'attach' not in kwargs or kwargs['attach'] == None:
                    kwargs['attach'] = Attachment.NotValid
                if 'backward' not in kwargs:
                    kwargs['backward'] = False
                if 'size' in kwargs:
                    size = kwargs['size']
                elif Attachment.isHorizontal(kwargs['attach']):
                    size = kwargs.setdefault('size', [40, 60])
                elif Attachment.isVertical(kwargs['attach']):
                    size = kwargs.setdefault('size', [60, 40])
                else:
                    size = kwargs.setdefault('size', [60, 60])
            avgSize = reduce(lambda x, y: x + y, size) / (len(size) * 1.0) * 1.4
            points = mm.eval('locusPicker:getPositionsForCapture(%s, "%s", %d);' % (listToArray(selected), camera, avgSize))
            data = []
            for i, node in enumerate(selected):
                data.append([node, QPointF(round(points[i * 2] * 10), round(points[i * 2 + 1] * 10))])

            rect = QRectF()
            for node, offset in data:
                if rect.isValid():
                    rect = rect.united(QRectF(offset, QSizeF(*size)))
                else:
                    rect = QRectF(offset, QSizeF(*size))

            rect.translate(pos)
            pos = scene.enlargeUptoUnited(pos, rect)
            if pos is None:
                return
            for node, offset in data:
                self.addItemToScene(scene, itemType, (pos + offset), node, color, commandType, channel, **kwargs)

            return

    def addItemToScene(self, scene, itemType, pos, node, color, commandType, channel, **kwargs):
        item = scene.addVarsItem(type=itemType, pos=pos, node=[node], color=color, command=commandType, **kwargs)
        self.defineChannel(item, item.targetNode, channel)
        self.defineValue(item, item.targetNode, item.targetChannel)
        return item

    def loadEachMap(self, index):
        modified = self.isWindowModified()
        LocusPickerLauncherUI.loadEachMap(self, index)
        if not modified:
            self.setWindowModified(modified)

    def refresh(self, *args):
        if self.__itemEditor and self.__itemEditor.isVisible():
            self.__itemEditor.close()
        LocusPickerLauncherUI.refresh(self, *args)
        self.checkMainPage()
        self.setWindowModified(False)

    def createCharacter(self):
        if not self.checkUnsaved():
            return
        self.moveToInitPage(False)

    def editCurrentMap(self):
        self.moveToInitPage(True)

    def showImageBrowser(self, edit, path):
        dirPath = os.path.dirname(path)
        if not os.path.isdir(dirPath):
            dirPath = os.path.expanduser('~')
        from dialog import OpenFileDialog
        path = OpenFileDialog('Image File', dirPath, IMAGE_FILE_FILTER, IMAGE_FILE_FILTER.split(';;')[1], self)
        if path:
            if os.path.isfile(path):
                edit.setText(path)
            else:
                print 'not existing path'

    def moveToInitPage(self, edit = False):
        self.__workingSize = self.size()
        try:
            self.initDo_button.clicked.disconnect()
        except:
            pass

        try:
            self.initFileDo_button.clicked.disconnect()
        except:
            pass

        if edit:
            from const import INIT_EDIT_TIP, INIT_EXPORT_TIP
            self.type_label.setText('---- EDIT CURRENT MAP ----')
            self.initDo_button.setText('Save to Node')
            self.initDo_button.setToolTip(INIT_EDIT_TIP)
            self.initFileDo_button.setText('Export to Map File')
            self.initFileDo_button.setToolTip(INIT_EXPORT_TIP)
            self.characterName_lineEdit.setText(self.characterName())
            index = self.tabWidget.currentIndex()
            scene = self.tabWidget.currentScene()
            self.subSetName_lineEdit.setText(self.mapName(index))
            self.initDo_button.clicked.connect(self.doEditCurrentMap)
            self.initFileDo_button.clicked.connect(self.saveCurrentToFile)
            self.bgColor_button.setColor(scene.color)
            self.useBG_buttonGrp.button(scene.useBGimage and 1 or 0).setChecked(True)
            self.bgImagePath_lineEdit.setText(scene.imagePath)
            size = self.tabWidget.sceneAtIndex(index).mapSize
            self.mapWidth_spinBox.setValue(size.width())
            self.mapHeight_spinBox.setValue(size.height())
        else:
            from const import DEF_CHARNAME, DEF_MAPNAME, INIT_CREATE_TIP, INIT_IMPORT_TIP
            self.type_label.setText('---- CREATE NEW MAP ----')
            self.initDo_button.setText('Create New Map')
            self.initDo_button.setToolTip(INIT_CREATE_TIP)
            self.initFileDo_button.setText('Import Map File')
            self.initFileDo_button.setToolTip(INIT_IMPORT_TIP)
            if self.characterName():
                self.characterName_lineEdit.setText(self.characterName())
            else:
                self.characterName_lineEdit.setText(getNumericName(DEF_CHARNAME, self.characterLineEdit.labels))
            self.subSetName_lineEdit.setText(getNumericName(DEF_MAPNAME, [ self.mapName(i) for i in xrange(self.tabWidget.count()) ]))
            self.initDo_button.clicked.connect(self.doCreateCharacter)
            self.initFileDo_button.clicked.connect(self.loadDataFromFile)
        self.stackedWidget.setCurrentIndex(1)
        self.resize(300, 320)

    def doCreateCharacter(self):
        charName = self.characterName_lineEdit.text()
        if not charName:
            return warn('Need character name', parent=self)
        mapName = self.subSetName_lineEdit.text()
        if not mapName:
            return warn('Need map name', parent=self)
        if charName in self.characterLineEdit.labels:
            if mapName in [ self.mapName(i) for i in xrange(self.tabWidget.count()) ]:
                return warn('Map name already exists : ' + mapName, parent=self)
        else:
            self.characterLineEdit.appendLabel(charName)
            self.tabWidget.clear()
        width, height = self.mapWidth_spinBox.value(), self.mapHeight_spinBox.value()
        tab = self.tabWidget.addGraphicsTab(mapName)
        index = self.tabWidget.indexOf(tab)
        scene = self.tabWidget.sceneAtIndex(index)
        if self.useBG_buttonGrp.checkedId():
            imgPath = self.bgImagePath_lineEdit.text()
            if os.path.isfile(imgPath):
                scene.setBackgroundPixmap(imgPath)
        scene.color = self.bgColor_button.color()
        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget.sceneAtIndex(index).mapSize = QSize(width, height)
        self.resize(self.__workingSize)
        self.assignDataToNode(mapName)

    def doEditCurrentMap(self):
        charName = self.characterName_lineEdit.text()
        if not charName:
            return warn('Need character name', parent=self)
        mapName = self.subSetName_lineEdit.text()
        if not mapName:
            return warn('Need map name', parent=self)
        index = self.tabWidget.currentIndex()
        currentMapName = self.mapName(index)
        if charName == self.characterName():
            if mapName != currentMapName:
                self.tabWidget.setTabText(index, mapName)
                self.syncNodeSubset(currentMapName, mapName)
            self.editMapFromInitPage(index)
        else:
            allPickerNodesArray = listToArray(filterPickerNode())
            filteredNodes = mm.eval('locusPicker:filterMapNodeCharacter(%s, "%s")' % (allPickerNodesArray, charName))
            mapNames = [ mc.getAttr(n + '.subSetName') for n in filteredNodes ]
            tabOrders = sorted([ mc.getAttr(n + '.tabOrder') for n in filteredNodes ])
            if charName in self.characterLineEdit.labels:
                if mapName in mapNames:
                    return warn('Map name already exists : ' + mapName, parent=self)
            self.editMapFromInitPage(index)
            self.assignDataToNode(currentMapName)
            currentCharName = self.characterName()
            pickerNode = mm.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (allPickerNodesArray, currentCharName, currentMapName))
            pickerNode = mc.rename(pickerNode, 'locusPicker_%s_%s' % (charName, mapName))
            mc.setAttr('%s.characterName' % pickerNode, charName, type='string')
            mc.setAttr('%s.subSetName' % pickerNode, mapName, type='string')
            if tabOrders:
                mc.setAttr('%s.tabOrder' % pickerNode, tabOrders[-1] + 1)
            newCharNames = []
            for node in filterPickerNode():
                name = mc.getAttr(node + '.characterName')
                if name not in newCharNames:
                    newCharNames.append(name)

            self.characterLineEdit.labels[:] = newCharNames
            self.characterLineEdit.doSelectText(charName)
        self.stackedWidget.setCurrentIndex(0)
        self.resize(self.__workingSize)
        self.setWindowModified(True)

    def editMapFromInitPage(self, index):
        width, height = self.mapWidth_spinBox.value(), self.mapHeight_spinBox.value()
        self.tabWidget.sceneAtIndex(index).mapSize = QSize(width, height)
        scene = self.tabWidget.sceneAtIndex(index)
        scene.useBGimage = bool(self.useBG_buttonGrp.checkedId())
        imgPath = self.bgImagePath_lineEdit.text()
        if scene.useBGimage:
            if os.path.isfile(imgPath):
                scene.setBackgroundPixmap(imgPath)
        else:
            scene.imagePath = imgPath
        scene.color = self.bgColor_button.color()

    def cancelInitPage(self):
        self.stackedWidget.setCurrentIndex(0)
        self.resize(self.__workingSize)

    def beforeChangeCharacter(self):
        if self.checkUnsaved():
            self.characterLineEdit.wait = WaitState.Proceed
        else:
            self.characterLineEdit.wait = WaitState.GoBack

    def isCharacterRenamable(self, charName):
        for node in mm.eval('locusPicker:filterMapNodeCharacter(%s, "%s")' % (listToArray(filterPickerNode()), charName)):
            if mc.referenceQuery(node, inr=1):
                self.characterLineEdit.wait = WaitState.GoBack
                return

        self.characterLineEdit.wait = WaitState.Proceed

    def changeCharacter(self, charName):
        LocusPickerLauncherUI.changeCharacter(self, charName)
        self.setWindowModified(False)

    def assignDataToNode(self, specificMap = ''):
        result = LocusPickerLauncherUI.assignDataToNode(self, specificMap)
        self.setWindowModified(False)
        return result

    def loadSvgFileToItems(self):
        dirPath = os.path.expanduser('~')
        from dialog import OpenFileDialog
        fileName = OpenFileDialog('Open Svg file', dirPath, SVG_FILE_FILTER, parent=self)
        if fileName:
            LocusPickerUI.__window__.tabWidget.currentScene().addItemsFromSvgFile(fileName)

    def saveDataToFile(self, index):
        if self.recentDirectory:
            dirPath = self.recentDirectory
        else:
            dirPath = os.path.expanduser('~')
        from dialog import SaveFileDialog
        fileName = SaveFileDialog('Save Map to file', dirPath, MAP_FILE_FILTER, parent=self)
        if fileName:
            self.doSaveDataToFile(fileName, index)

    def saveCurrentToFile(self):
        index = self.tabWidget.currentIndex()
        if index > -1:
            self.saveDataToFile(index)

    def saveAllMapToFiles(self):
        if self.recentDirectory:
            dirPath = self.recentDirectory
        else:
            dirPath = os.path.expanduser('~')
        from dialog import SaveFileDialog
        fileName = SaveFileDialog('Save All Maps to files', dirPath, MAP_FILE_FILTER, parent=self)
        if fileName:
            base, ext = os.path.splitext(fileName)
            for i in xrange(self.tabWidget.count()):
                newName = base + '_' + self.mapName(i)
                self.doSaveDataToFile(newName + ext, i)

    def doSaveDataToFile(self, path, index):
        dataNode = Element('data')
        mapNode = Element('map')
        dataNode.append(mapNode)
        tab = self.tabWidget.widget(index)
        mapNode.attrib['character'] = self.characterName()
        mapNode.attrib['name'] = self.mapName(index)
        mapNode.attrib['prefix'] = tab.prefix
        size = self.tabWidget.sceneAtIndex(index).mapSize
        mapNode.attrib['size'] = '%d,%d' % (size.width(), size.height())
        scene = self.tabWidget.sceneAtIndex(index)
        mapNode.attrib['bgImage'] = scene.imagePath
        mapNode.attrib['bgColor'] = ','.join((unicode(v) for v in scene.color.getRgb()[:3]))
        mapNode.attrib['usePrefix'] = tab.usePrefix and '1' or '0'
        mapNode.attrib['useBgColor'] = not scene.useBGimage and '1' or '0'
        items = scene.getItemsByZValueOrder()
        for item in items:
            buttonNode = Element('button')
            mapNode.append(buttonNode)
            typeStr = getTypeString(item.type())
            buttonNode.attrib['type'] = typeStr
            pos = item.scenePos()
            buttonNode.attrib['position'] = '%.2f,%.2f' % (pos.x(), pos.y())
            color = item.color
            buttonNode.attrib['color'] = '%d,%d,%d' % (color.red(), color.green(), color.blue())
            sizeStr = '%.2f,%.2f' % (item.width, item.height)
            if typeStr == 'Group':
                buttonNode.attrib['label'] = item.label
                buttonNode.attrib['doKey'] = item.doKey and 'true' or 'false'
                buttonNode.attrib['doReset'] = item.doReset and 'true' or 'false'
                buttonNode.attrib['labelPos'] = ButtonPosition.getString(item.labelPosition)
                buttonNode.attrib['buttonPos'] = ButtonPosition.getString(item.buttonPosition)
                buttonNode.attrib['children'] = ','.join((i.hashcode for i in item.childItems()))
                buttonNode.attrib['size'] = sizeStr
            elif typeStr == 'VisToggle':
                buttonNode.attrib['size'] = sizeStr
                buttonNode.attrib['command'] = encodeCommandStr(item)
                buttonNode.attrib['targets'] = encodeVisToggleNodeStr(item)
                buttonNode.attrib['color'] = encodeVisToggleColorStr(item)
                buttonNode.attrib['execute'] = encodeVisToggleChannelStr(item)
                buttonNode.attrib['icon'] = encodeIconStr(item) or ''
            else:
                if item.command in ('Range', 'Pose') and getTypeString(item.type()) in ('RectangleSlider',):
                    sizeStr += ';%.2f,%.2f,%.2f' % (item.margin1, item.margin2, item.thickness)
                buttonNode.attrib['size'] = sizeStr
                buttonNode.attrib['command'] = encodeCommandStr(item)
                buttonNode.attrib['node'] = item.targetNode and ','.join(item.targetNode) or ''
                buttonNode.attrib['channel'] = item.targetChannel and ','.join(item.targetChannel) or ''
                buttonNode.attrib['value'] = item.targetValue and complexStringData(item.targetValue) or ''
                buttonNode.attrib['icon'] = encodeIconStr(item) or ''
                buttonNode.attrib['label'] = encodeLabelStr(item) or ''
                buttonNode.attrib['linkedItem'] = item.linkedItems and ','.join([ x.hashcode for x in item.linkedItems ]) or ''
            buttonNode.attrib['hashcode'] = item.hashcode

        from const import indentXML
        indentXML(dataNode)
        if module_exists('lxml'):
            ElementTree(dataNode).write(path)
        else:
            with open(path, 'w') as f:
                f.write(tostring(dataNode))
                f.close()
        self.recentDirectory = os.path.dirname(path).replace('\\', '/')

    def loadDataFromFile(self):
        if LocusPickerLauncherUI.loadDataFromFile(self):
            self.stackedWidget.setCurrentIndex(0)
            self.resize(self.__workingSize)
            self.checkMainPage()

    def checkMapNodeExists(self, character, subSet):
        if mm.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (listToArray(filterPickerNode()), character, subSet)) != 'None':
            yesOrNo = confirm('Map already exists : %s\nDo you want to replace it or add as a new map?' % subSet, 'Map Exists', ['Replace', 'Add', 'Cancel'], self)
            if yesOrNo == 1:
                index = -1
                for i in xrange(self.tabWidget.count()):
                    if self.mapName(i) == subSet:
                        index = i
                        break
                else:
                    error('No tab', parent=self)
                    return -1

                tab = self.tabWidget.widget(index)
                scene = self.tabWidget.sceneAtIndex(index)
                scene.clear()
            elif yesOrNo == -1:
                tab = self.tabWidget.addGraphicsTab(subSet, changeCurrent=False)
                index = self.tabWidget.count() - 1
                scene = self.tabWidget.sceneAtIndex(index)
            else:
                return -1
        else:
            tab = self.tabWidget.addGraphicsTab(subSet, changeCurrent=False)
            index = self.tabWidget.count() - 1
            scene = self.tabWidget.sceneAtIndex(index)
        return (tab, index, scene)

    def doLoadDataFromFile(self, path):
        index = LocusPickerLauncherUI.doLoadDataFromFile(self, path)
        self.setWindowModified(True)
        return index

    def syncNodeCharacter(self, oldCharName, newCharName):
        mc.select(cl=1)
        filteredNodes = mm.eval('locusPicker:filterMapNodeCharacter(%s, "%s")' % (listToArray(filterPickerNode()), oldCharName))
        for node in filteredNodes:
            subSet = mc.getAttr('%s.subSetName' % node)
            node = mc.rename(node, 'locusPicker_%s_%s' % (newCharName, subSet))
            mc.setAttr('%s.characterName' % node, newCharName, type='string')

    def syncNodeSubset(self, oldTabName, newTabName):
        charName = self.characterName()
        pickerNode = mm.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (listToArray(filterPickerNode()), charName, oldTabName))
        if pickerNode == 'None':
            return
        mc.select(cl=1)
        pickerNode = mc.rename(pickerNode, 'locusPicker_%s_%s' % (charName, newTabName))
        mc.setAttr('%s.subSetName' % pickerNode, newTabName, type='string')

    def checkCharacterName(self):
        if not self.characterLineEdit.labels:
            from const import DEF_CHARNAME
            self.characterLineEdit.labels = [DEF_CHARNAME]
        self.tabWidget.currentView().loaded = True
        self.assignDataToNode(self.mapName())
        self.setWindowModified(True)

    def removeNode(self, tabText):
        charName = self.characterName()
        subSetName = tabText
        pickerNode = mm.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (listToArray(filterPickerNode()), charName, subSetName))
        if pickerNode == 'None':
            return
        print 'Remove Character: [%s]\t Subset: [%s]\t Node: [%s]' % (charName, subSetName, pickerNode)
        mc.delete(pickerNode)

    def alignSelectedByMode(self, axis = 'horizontal'):
        if self.__mapMode:
            scene = self.tabWidget.currentScene()
            if not scene:
                return
            if scene.editable:
                if axis == 'horizontal':
                    axis = 'vcenter'
                elif axis == 'vertical':
                    axis = 'hcenter'
                self.alignSelectedItems(axis)
        else:
            mm.eval('locusPicker:alignGeoButtons("%s")' % axis)

    def setAverageGapByMode(self, axis = 'X'):
        if self.__mapMode:
            scene = self.tabWidget.currentScene()
            if not scene:
                return
            if scene.editable:
                self.averageGapSelectedItems(axis == 'X' and 'hor' or 'ver')
        else:
            mm.eval('locusPicker:setGeoButtonsAverageGap("%s")' % axis)

    def setAverageSizeByMode(self, axis = 'X'):
        if self.__mapMode:
            scene = self.tabWidget.currentScene()
            if not scene:
                return
            if scene.editable:
                self.averageSizeSelectedItems(axis == 'X' and 'width' or 'height')
        else:
            mm.eval('locusPicker:setGeoButtonsAverageSize("%s")' % axis)

    def mirrorButtonsByMode(self, search = '', replace = '', changeColor = False):
        if self.__mapMode:
            scene = self.tabWidget.currentScene()
            if not scene:
                return
            if scene.editable:
                scene.mirrorSelectedItems(search, replace, changeColor)
        else:
            self.mirrorGeoButtons()

    def convertMapToGeo(self):
        mm.eval('locusPicker:removeConvertedButtons()')
        tab = self.tabWidget
        index = tab.currentIndex()
        scene = tab.sceneAtIndex(index)
        width = scene.mapSize.width() / 10.0
        height = scene.mapSize.height() / 10.0
        base = mm.eval('locusPicker:createPlane("LocusPickerConvert_BG", %f, %f, %f, %f, 0, 0, 0)' % (width / -2.0,
         0,
         width,
         height))
        mc.setAttr('%s.characterName' % base, self.characterName(), type='string')
        mc.setAttr('%s.subSetName' % base, self.mapName(), type='string')
        scene = tab.currentScene()
        for i, item in enumerate([ x for x in scene.items() if isinstance(x, AbstractDropItem) ]):
            index = scene.getItemsByZValueOrder(item.sceneBoundingRect()).index(item)
            button = mm.eval('locusPicker:createPlane("%s", %f, %f, %f, %f, %f, %f, %f)' % ('LocusPickerConvert_Button%d' % i,
             item.x() / 10.0,
             item.y() / -10.0,
             item.width / 10.0,
             item.height / 10.0,
             item.minWidth / 10.0,
             item.minHeight / 10.0,
             1 + index / 10.0))
            col = tuple([ round(x, 2) for x in item.color.getRgbF()[:3] ])
            mm.eval('locusPicker:assignShader("%s", %f, %f, %f)' % ((button,) + col))
            typeStr, posStr, sizeStr, colorStr, commandStr, nodeStr, channelStr, valueStr, iconStr, labelStr = self.convertItemDataToString(item)
            iconStr = iconStr.split(';')[0]
            mm.eval('locusPicker:setAttrToGeoButton("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (button,
             typeStr,
             commandStr,
             nodeStr,
             channelStr,
             valueStr,
             iconStr,
             labelStr))
            if not item.icon.isNull():
                iconRect = item.iconRect.translated(item.x(), item.y())
                iconButton = mm.eval('locusPicker:createPlane("%s", %f, %f, %f, %f, 0, 0, 2)' % (button.replace('Button', 'Icon'),
                 iconRect.x() / 10.0,
                 iconRect.y() / -10.0,
                 iconRect.width() / 10.0,
                 iconRect.height() / 10.0))
                mm.eval('locusPicker:setAttachToButton("%s", "%s");' % (button, iconButton))
            if getTypeString(item.type()) == 'RectangleSlider':
                sliderButton = button.replace('Button', 'Slider')
                margin1, margin2, thickness = item.margin1 / 10.0, item.margin2 / 10.0, item.thickness / 10.0
                if item.attachment == Attachment.LEFT:
                    mm.eval('locusPicker:setSliderToButton("%s", "%s", %f, %f, %f, 0, 0);' % (button,
                     sliderButton,
                     margin1,
                     margin2,
                     thickness))
                elif item.attachment == Attachment.RIGHT:
                    mm.eval('locusPicker:setSliderToButton("%s", "%s", %f, %f, %f, 0, 1);' % (button,
                     sliderButton,
                     margin1,
                     margin2,
                     thickness))
                elif item.attachment == Attachment.TOP:
                    mm.eval('locusPicker:setSliderToButton("%s", "%s", %f, %f, %f, 1, 0);' % (button,
                     sliderButton,
                     margin1,
                     margin2,
                     thickness))
                elif item.attachment == Attachment.BOTTOM:
                    mm.eval('locusPicker:setSliderToButton("%s", "%s", %f, %f, %f, 1, 1);' % (button,
                     sliderButton,
                     margin1,
                     margin2,
                     thickness))
                else:
                    mm.eval('locusPicker:setSliderToButton("%s", "%s", %f, %f, %f, -1, 0);' % (button,
                     sliderButton,
                     margin1,
                     margin2,
                     thickness))

        mm.eval('locusPicker:setGeoModeModelView("%s")' % base)
        self.setWindowGeoMode(True)

    def setWindowGeoMode(self, geoMode):
        self.setWindowTitle(geoMode and 'Locus Picker - Geo Mode [*]' or 'Locus Picker - Map Mode [*]')
        self.__mapMode = not geoMode
        self.tabWidget.editable = self.__mapMode
        self.characterLineEdit.editable = self.__mapMode

    def convertGeoToMap(self):
        bg = mc.ls('LocusPickerConvert_BG', tr=1)
        if not bg:
            return warn('Not exist geo buttons', parent=self)
        subSetName = mc.getAttr('%s.subSetName' % bg[0])
        tab = self.tabWidget
        if self.mapName() == subSetName:
            scene = tab.currentScene()
        else:
            for i in xrange(tab.count()):
                if self.mapName(i) == subSetName:
                    tab.setCurrentIndex(i)
                    scene = tab.sceneAtIndex(i)
                    break
            else:
                return error('There is no tab matched', parent=self)

        w, h = mc.xform(bg[0], q=1, r=1, s=1)[:2]
        self.resizeToTab(QSize(w * 10, h * 10) + QSize(4, 23))
        buttons = mc.ls('LocusPickerConvert_BG*', tr=1)
        if buttons:
            try:
                scene.clear()
            except:
                traceback.print_exc()

            for i, button in enumerate(buttons):
                itemType = mc.getAttr('%s.type' % button)
                x, y = [ round(v * 10) for v in mc.xform(button, q=1, ws=1, t=1)[:2] ]
                y *= -1
                pos = QPointF(x, y)
                size = [ round(v * 10) for v in mc.xform(button, q=1, ws=1, r=1, s=1)[:2] ]
                color = QColor.fromRgbF(*mm.eval('locusPicker:getButtonColor("%s")' % button))
                command = mc.getAttr('%s.command' % button)
                node = mc.getAttr('%s.node' % button)
                channel = mc.getAttr('%s.channel' % button)
                value = mc.getAttr('%s.value' % button)
                label = mc.getAttr('%s.label' % button)
                icon = mc.getAttr('%s.icon' % button)
                node = node and node.split(',') or []
                channel = channel and channel.split(',') or []
                if itemType == 'Path':
                    icon = icon
                elif icon:
                    x = round(mc.getAttr('%s.attachPosX' % button) * 10.0)
                    y = round(mc.getAttr('%s.attachPosY' % button) * -10.0)
                    w = round(mc.getAttr('%s.attachScaleX' % button) * 10.0)
                    h = round(mc.getAttr('%s.attachScaleY' % button) * 10.0)
                    icon = [icon, QRectF(x, y, w, h)]
                else:
                    icon = []
                label = decodeLabelStr(label)
                if itemType == 'RectangleSlider':
                    command, attach, backward = decodeCommandStr(command)
                    margin1 = round(mc.getAttr('%s.margin1' % button) * 10.0)
                    margin2 = round(mc.getAttr('%s.margin2' % button) * 10.0)
                    thickness = round(mc.getAttr('%s.thickness' % button) * 10.0)
                    dataBlock = dict(type=itemType, pos=pos, size=size, color=color, command=command, node=node, channel=channel, value=complexListData(value), label=label, attach=Attachment.getAttachment(attach), slider=[margin1, margin2, thickness], backward=backward, icon=icon)
                else:
                    dataBlock = dict(type=itemType, pos=pos, size=size, color=color, command=command, node=node, channel=channel, value=complexListData(value), label=label, icon=icon)
                scene.addVarsItem(**dataBlock)

        self.deleteAllGeoButtons()
        self.setWindowModified(True)

    def deleteAllGeoButtons(self):
        mm.eval('locusPicker:removeConvertedButtons()')
        mm.eval('locusPicker:setMapModeModelView()')
        self.setWindowGeoMode(False)

    def mirrorGeoButtons(self):
        from const import getMirrorColor
        search, replace = self.__toolDialog.getReplaceString()
        mirroredButtons = mm.eval('locusPicker:mirrorGeoButtons("%s", "%s")' % (search, replace))
        for button in mirroredButtons:
            color = QColor.fromRgbF(*mm.eval('locusPicker:getButtonColor("%s")' % button))
            color = getMirrorColor(color)
            col = tuple([ round(x, 2) for x in color.getRgbF()[:3] ])
            mm.eval('locusPicker:assignShader("%s", %f, %f, %f)' % ((button,) + col))
            if mc.getAttr('%s.type' % button) == 'Path':
                from svgParser import createSvgPath, decodeSvgPathString, generatePathToSvg
                from const import getMirroredPath
                svgPath = mc.getAttr('%s.icon' % button)
                order = decodeSvgPathString(svgPath)
                path = createSvgPath(order)
                mrPath = getMirroredPath(path)
                d = generatePathToSvg(mrPath)
                mc.setAttr('%s.icon' % button, d, type='string')

    @staticmethod
    def getSelectedChannel():
        return mc.channelBox('mainChannelBox', q=1, sma=1)

    @classmethod
    def popWindow(cls, obj):
        for i, inst in enumerate(cls.__windows__):
            if inst.objectName() == obj.objectName():
                break
        else:
            i = -1

        if i > -1:
            inst = cls.__windows__[i]
            del cls.__windows__[i]
            inst.deleteLater()

    @classmethod
    def executeInstMethod(cls, objName, func):
        inst = None
        for inst in cls.__windows__:
            if inst.objectName() == objName:
                break
        else:
            inst = None

        if inst:
            return eval('inst.' + func)
        else:
            return

    @classmethod
    def showPicker(cls):
        if mc.window(USER_WINDOW_NAME, q=1, ex=1):
            mc.deleteUI(USER_WINDOW_NAME)
        if cls.__window__:
            if cls.__window__.isMinimized():
                cls.__window__.showNormal()
            else:
                cls.__window__.raise_()
        else:
            cls.__window__ = cls(PLATFORM_PARENT)
            cls.__window__.show()

    def isCurrentSceneHasBGImage(self):
        scene = self.tabWidget.currentScene()
        if not scene:
            return 0
        elif scene.imagePath and not scene.pixmap.isNull():
            return 1
        else:
            return 0

    @sceneExists
    def clearCurrentBgImage(self, scene = None):
        scene.clearBgImage()
        self.setWindowModified(True)

    def isCurrentSceneUseBGImage(self):
        scene = self.tabWidget.currentScene()
        if not scene:
            return 0
        return scene.useBGimage

    @sceneExists
    def toggleSceneBGImage(self, scene = None):
        if scene.imagePath and not scene.pixmap.isNull():
            scene.useBGimage ^= True
            self.setWindowModified(True)

    def isCurrentSceneCoop(self):
        scene = self.tabWidget.currentScene()
        if not scene:
            return 0
        return scene.coop

    @sceneExists
    def coopUpCurrentScene(self, scene = None):
        scene.coop ^= True
        scene.update()

    @sceneExists
    def alignSelectedItems(self, align, scene = None):
        if scene.editable:
            scene.alignSelectedItems(align)

    @sceneExists
    def averageGapSelectedItems(self, direction, scene = None):
        if scene.editable:
            scene.averageGapSelectedItems(direction)

    @sceneExists
    def averageSizeSelectedItems(self, direction, scene = None):
        if scene.editable:
            scene.averageSizeSelectedItems(direction)

    @sceneExists
    def arrangeSelectedItems(self, options, scene = None):
        if scene.editable:
            scene.arrangeSelectedItems(options)

    @sceneExists
    def moveSelectedItemsToCenter(self, axis, scene = None):
        if scene.editable:
            scene.moveSelectedItemsToCenter(axis)

    @sceneExists
    def mirrorItems(self, option = '', scene = None):
        if not scene.editable:
            return
        if option.startswith('Replace'):
            split = option.split()
            scene.mirrorSelectedItems(split[1], split[3])
        else:
            scene.mirrorSelectedItems()

    @sceneExists
    def matchTargetNode(self, scene = None):
        nodes = [ n for n in mm.eval('locusPicker:getAllHierachyTransform()') ]
        if not nodes:
            return warn('Select a top nodes to match', parent=self)
        arrayD = listToArray(nodes)
        for item in scene.items():
            for i, n in enumerate(item.targetNode):
                item.targetNode[i] = mm.eval('locusPicker:getMatchedTransform(%s, "%s")' % (arrayD, str(n)))

        info('Matching nodes is done!', parent=self)

    def isItemSelected(self):
        scene = self.tabWidget.currentScene()
        if not scene:
            return 0
        return bool(scene.selectedItems())

    @sceneExists
    def createSelectedButtonGroup(self, scene = None):
        scene.createButtonGroupSelectedItems()

    @sceneExists
    def getAvailableIconSize(self, scene = None):
        items = scene.selectedItems()
        if items:
            if isinstance(items[0], PathDropItem):
                return ('Not support for Vector Button yet.', 'Sorry')
            labelSize, iconRect = QSize(items[0].width, items[0].height), items[0].inboundRect().toRect()
            if iconRect.isEmpty():
                return ('Selected button does not have enough space to accommodate icon.\nYou have to enlarge the button before create icon image.', 'Not enough')
            return (labelSize, iconRect)
        else:
            return ('Select a button in the map.', 'Not selected')

    @sceneExists
    def getSceneSize(self, scene = None):
        return scene.mapSize

    @sceneExists
    def getScriptFromSelected(self, scene = None):
        items = [ x for x in scene.selectedItems() if x.command.startswith('EXEC ') ]
        if items:
            return re.sub('^EXEC ', '', items[0].command)
        return ''


if __name__ == '__main__':
    app = QApplication(sys.argv)
    LocusPickerUI.showPicker()
    sys.exit(app.exec_())