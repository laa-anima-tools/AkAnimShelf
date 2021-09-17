# Embedded file name: C:\Users\hgkim\Documents\maya\2016\pythons\LocusPicker\locusPickerUITrial.py


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


import os, sys, traceback, time, re
from functools import partial
if module_exists('lxml'):
    from lxml.etree import Element, ElementTree, parse, tostring
else:
    from xml.etree.cElementTree import Element, ElementTree, parse, tostring
from PySide.QtCore import QObject, SIGNAL, Qt, QPointF, QTimer, QSize, QLocale, QSettings, QRectF, QPoint, QSizeF, QEvent, QRect
from PySide.QtGui import QWidget, QAction, QIcon, QColor, QApplication, QPixmap, QToolButton, QLineEdit, QImage, QDesktopServices, QGridLayout, QButtonGroup, QCheckBox, QMenu, QPushButton
from PySide.QtUiTools import QUiLoader
from loadUiType import loadUiType
from editableTab import EditableTabWidget
from colorButton import ColorButton
from popupLineEdit import PopupLineEdit
from arrowToggleButton import ArrowToggleButton, HoverIconButton
from dropItem import AbstractDropItem, RectangleDropItem
from dropSliderItem import Attachment, RectangleDropSliderItem
from dropPathItem import PathDropItem
from groupItem import GroupItem
from const import getTypeString, WaitState, LocaleText, encodeCommandStr, encodeIconStr, encodeLabelStr, decodeCommandStr, decodeIconStr, decodeLabelStr, SVG_FILE_FILTER, MAP_FILE_FILTER, IMAGE_FILE_FILTER, encodeGroupCommandStr, decodeGroupCommandStr, ButtonPosition, warn, error, info, confirm
from itemEditor import ItemEditor
from toolsDialog import ToolsDialog
from selectGuideDialog import SelectGuideDialog
from colorPaletteWidget import ColorPaletteDialog
from idleQueue import idle_add
from idleQueueDispatcher import ThreadDispatcher
from locusPickerResources import *
from decorator import sceneExists, timestamp
uiFile = os.path.join(os.path.dirname(__file__), 'resources', 'mainwindow.ui')
base_class, form_class = loadUiType(uiFile)
if sys.exec_prefix.find('Maya') > 0:
    import maya.cmds as mc
    import maya.mel as mel
    import maya.OpenMaya as api
    import maya.OpenMayaUI as apiUI
    from wrapInstance import wrapinstance, unwrapinstance
    mel.eval('source "%s";' % (os.path.dirname(__file__).replace('\\', '/') + '/locusPicker.mel'))

    def getMayaWindow():
        ptr = apiUI.MQtUtil.mainWindow()
        return wrapinstance(long(ptr), QWidget)


    def toQtObject(mayaName):
        ptr = apiUI.MQtUtil.findControl(mayaName)
        if ptr is None:
            ptr = apiUI.MQtUtil.findLayout(mayaName)
        if ptr is None:
            ptr = apiUI.MQtUtil.findMenuItem(mayaName)
        if ptr is not None:
            return wrapinstance(long(ptr), QObject)
        else:
            return


    def toMayaObject(qtObject):
        return apiUI.MQtUtil.fullName(unwrapinstance(qtObject))


    INMAYA = True
else:
    INMAYA = False
PLATFORM_PARENT = INMAYA and getMayaWindow() or None

class LocusPickerUI(base_class, form_class):
    __window__ = None

    def __init__(self, parent = PLATFORM_PARENT):
        super(base_class, self).__init__(parent)
        self.setupUi(self)
        windowTitle = self.windowTitle()
        c = re.compile('.+(v\\d+\\.\\d+)')
        m = c.match(windowTitle)
        if m:
            substr = m.group(len(m.groups()))
            self.setWindowTitle(windowTitle.replace(substr, 'Trial'))
        else:
            self.setWindowTitle(windowTitle + ' Trial')
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowMaximizeButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setLocale(QLocale(QLocale.English))
        self.setFocusPolicy(Qt.StrongFocus)
        self.__topMenuVisible = self.__bottomMenuVisible = True
        self.__poseGloalData = []
        self.__poseNodes = None
        self.__poseChannels = None
        self.__poseStartValues = None
        self.__blockCallback = False
        self.__mapMode = True
        self.__guideWidget = None
        self.__recentDirectory = ''
        self.itemEditor = ItemEditor(self)
        self.toolDialog = ToolsDialog(self)
        self.selectGuideDialog = SelectGuideDialog(self)
        self.paletteDialog = ColorPaletteDialog(self)
        self.replaceToggleButtons()
        self.replaceTabWidget()
        self.replaceBottomMenuWidget()
        self.setupInitPage()
        self.tabPoupMenuBuild()
        self.createGuideWidget()
        self.generateAction()
        self.setToolBarMenu()
        self.restoreIniSettings()
        self.dispatcher = ThreadDispatcher(self)
        self.dispatcher.start()
        self.connectTabSignal()
        self.connectToggleButtonsSignal()
        self.connectTopMenuSignal()
        self.connectBottomMenuSignal()
        self.connectItemEditorSignal()
        self.connectToolDialogSignal()
        self.connectInitPageSignal()
        self.paletteDialog.saveINI.connect(self.savePalettePos)
        self.__callbacks = []
        try:
            self.__callbacks.append(api.MEventMessage.addEventCallback('SelectionChanged', partial(self.selectionChanged)))
        except:
            print 'Fail to add callback : SelectionChanged'

        try:
            self.__callbacks.append(api.MEventMessage.addEventCallback('SceneOpened', partial(self.refresh)))
        except:
            print 'Fail to add callback : SceneOpened'

        try:
            self.__callbacks.append(api.MEventMessage.addEventCallback('quitApplication', partial(self.forceToClose)))
        except:
            print 'Fail to add callback : quitApplication'

        QTimer.singleShot(1, partial(self.refresh))
        return

    def customEvent(self, event):
        event.callback()

    def forceToClose(self, *args):
        self.setWindowModified(False)
        self.close()

    def testMethod(self, *args, **kwargs):
        print self.sender(), args, kwargs

    def showItemEditor(self, item):
        self.itemEditor.setItem(item)
        self.itemEditor.show(self.isWindowModified())
        self.itemEditor.setWindowModified(False)
        self.itemEditor.resize(268, 774)
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('ItemEditor')
        value = settings.value('Position')
        settings.endGroup()
        if value:
            if value.x() > 0 and value.y() > 8:
                return
        self.moveWidgetAccordingToWindow(self.itemEditor)

    def moveWidgetAccordingToWindow(self, widget):
        rect = self.geometry()
        geometry = widget.geometry()
        geometry.moveTopLeft(rect.topRight() + QPoint(8, 0))
        desktop = QApplication.desktop()
        if desktop.screenNumber(widget) != desktop.screenNumber(self) or not desktop.availableGeometry(widget).contains(geometry):
            geometry.moveRight(rect.left() - 24)
        widget.move(geometry.topLeft() - QPoint(0, 30))

    def refreshItemToItemEditor(self, items):
        if self.itemEditor.isVisible():
            self.itemEditor.restoreItem()
            if items:
                self.itemEditor.setItem(items[0])
            else:
                self.itemEditor.clearItem()

    def showToolDialog(self):
        self.toolDialog.initializeUI()
        self.toolDialog.resize(420, 329)
        self.toolDialog.show()
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('ToolDialog')
        value = settings.value('Position')
        settings.endGroup()
        if value:
            if value.x() > 0 and value.y() > 8:
                return
        self.moveWidgetAccordingToWindow(self.toolDialog)

    def openInfoDocumentUrl(self):
        from const import documentUrl
        QDesktopServices.openUrl(documentUrl)

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
        self.tabWidget.tabSizeChange.connect(self.resizeToTab)
        self.tabWidget.currentChanged.connect(self.setPrefix)
        self.tabWidget.currentChanged.connect(self.selectionChanged)
        self.tabWidget.tabAdded.connect(self.checkCharacterName)
        self.tabWidget.addItemOn.connect(self.addDropItems)
        self.tabWidget.addItemWithSet.connect(self.addItemFromToolDialog)
        self.tabWidget.addPreviewedItem.connect(self.addItemFromSet)
        self.tabWidget.sendCommandData.connect(self.doCommand)
        self.tabWidget.poseGlobalVarSet.connect(lambda x: self.setPoseGlobalVariable(True, x))
        self.tabWidget.poseGlobalVarUnset.connect(lambda x: self.setPoseGlobalVariable(False, x))
        self.tabWidget.redefineMember.connect(self.redefineMember)
        self.tabWidget.changeMember.connect(self.changeMember)
        self.tabWidget.editRemote.connect(self.showItemEditor)
        self.tabWidget.windowModified.connect(lambda : self.setWindowModified(True))
        self.tabWidget.tabLabelRenamed.connect(self.syncNodeSubset)
        self.tabWidget.tabRemovedText.connect(self.removeNode)
        self.tabWidget.undoOpen.connect(lambda : self.undoOpenClose(True))
        self.tabWidget.undoClose.connect(lambda : self.undoOpenClose(False))
        self.tabWidget.saveToFile.connect(self.saveDataToFile)
        self.tabWidget.selectMapNode.connect(self.selectMapNode)
        self.tabWidget.selectedItemsChanged.connect(self.refreshItemToItemEditor)

    def connectToggleButtonsSignal(self):
        self.topMenuToggleButton.clicked.connect(self.toggleTopMenu)
        self.bottomMenuToggleButton.clicked.connect(self.toggleBottomMenu)

    def connectTopMenuSignal(self):
        self.characterLineEdit.labelRenamed.connect(self.syncNodeCharacter)
        self.characterLineEdit.waitStart.connect(self.beforeChangeCharacter)
        self.characterLineEdit.labelSelected.connect(self.changeCharacter)
        self.prefix_button.toggled.connect(self.storeUsePrefix)
        self.copyPrefix_button.clicked.connect(self.setPrefixFromSelectedNode)
        self.prefiex_lineEdit.textChanged.connect(self.storePrefix)

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
        self.itemEditor.itemModified.connect(self.setWindowModified)
        self.itemEditor.colorPick.connect(self.showColorPicker)

    def connectToolDialogSignal(self):
        self.toolDialog.colorPick.connect(self.showColorPicker)
        self.toolDialog.mapToGeo_Button.clicked.connect(self.convertMapToGeo)
        self.toolDialog.geoToMap_Button.clicked.connect(self.convertGeoToMap)
        self.toolDialog.deleteAll_Button.clicked.connect(self.deleteAllGeoButtons)
        self.toolDialog.alignLeft_Button.clicked.connect(lambda : self.alignSelectedByMode('left'))
        self.toolDialog.alignRight_Button.clicked.connect(lambda : self.alignSelectedByMode('right'))
        self.toolDialog.alignTop_Button.clicked.connect(lambda : self.alignSelectedByMode('top'))
        self.toolDialog.alignBottom_Button.clicked.connect(lambda : self.alignSelectedByMode('bottom'))
        self.toolDialog.alignHorizontal_Button.clicked.connect(lambda : self.alignSelectedByMode('horizontal'))
        self.toolDialog.alignVertical_Button.clicked.connect(lambda : self.alignSelectedByMode('vertical'))
        self.toolDialog.bringFront_Button.clicked.connect(lambda : self.arrangeSelectedItems('bringFront'))
        self.toolDialog.bringToForward_Button.clicked.connect(lambda : self.arrangeSelectedItems('bringForward'))
        self.toolDialog.sendToBackward_Button.clicked.connect(lambda : self.arrangeSelectedItems('sendBackward'))
        self.toolDialog.sendBack_Button.clicked.connect(lambda : self.arrangeSelectedItems('sendBack'))
        self.toolDialog.moveToHCenter_Button.clicked.connect(lambda : self.moveSelectedItemsToCenter('hor'))
        self.toolDialog.moveToVCenter_Button.clicked.connect(lambda : self.moveSelectedItemsToCenter('ver'))
        self.toolDialog.averageWidth_Button.clicked.connect(lambda : self.setAverageSizeByMode('X'))
        self.toolDialog.averageHeight_Button.clicked.connect(lambda : self.setAverageSizeByMode('Y'))
        self.toolDialog.averageGapX_Button.clicked.connect(lambda : self.setAverageGapByMode('X'))
        self.toolDialog.averageGapY_Button.clicked.connect(lambda : self.setAverageGapByMode('Y'))
        self.toolDialog.mirrorButtons.connect(self.mirrorButtonsByMode)

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
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('Window')
        settings.setValue('PalettePosition', self.paletteDialog.pos())
        settings.endGroup()

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
        from const import REFRESH_TIP, CREATE_CHAR_TIP, EDIT_MAP_TIP, SAVE_NODE_TIP, LOAD_FILE_TIP, SAVE_FILE_TIP, INFO_TIP
        self.refreshAct = self.createAction('Refresh', self.refresh, icon=':/refresh', disable=True, tip=REFRESH_TIP)
        self.createCharacterAct = self.createAction('Create Character', self.createCharacter, icon=':/create', tip=CREATE_CHAR_TIP)
        self.editCurrentMapAct = self.createAction('Edit Current Map', self.editCurrentMap, icon=':/edit', disable=True, tip=EDIT_MAP_TIP)
        self.assignDataToNodeAct = self.createAction('Assign Data to Node', self.assignDataToNode, icon=':/save_hilite', disable=':/save_disabled', tip=SAVE_NODE_TIP)
        self.assignDataToNodeAct.setEnabled(False)
        self.loadFileToTabAct = self.createAction('Load Map File', self.loadDataFromFile, icon=':/open', tip=LOAD_FILE_TIP)
        self.saveTabToFileAct = self.createAction('Save Map File', self.saveCurrentToFile, icon=':/save', disable=True, tip=SAVE_FILE_TIP)
        self.infoAct = self.createAction('Info', self.openInfoDocumentUrl, icon=':/infoDocu', tip=INFO_TIP)

    def setToolBarMenu(self):
        self.geo_toolButton.hide()
        self.map_toolButton.hide()
        for act in [self.createCharacterAct,
         self.editCurrentMapAct,
         self.assignDataToNodeAct,
         self.refreshAct]:
            self.upperToolBar.addAction(act)
            self.upperToolBar.widgetForAction(act).setFixedSize(24, 24)

        self.characterLineEdit = PopupLineEdit(self)
        self.upperToolBar.addWidget(self.characterLineEdit)
        self.upperToolBar.widgetForAction(self.createCharacterAct).installEventFilter(self)
        self.upperToolBar.widgetForAction(self.assignDataToNodeAct).installEventFilter(self)
        self.lowerToolBar.addAction(self.infoAct)
        self.lowerToolBar.widgetForAction(self.infoAct).setFixedSize(24, 24)
        separator = QWidget(self)
        separator.setFixedWidth(5)
        self.lowerToolBar.addWidget(separator)
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
        self.prefiex_lineEdit = QLineEdit(self)
        self.prefiex_lineEdit.setFocusPolicy(Qt.StrongFocus)
        self.prefiex_lineEdit.setEnabled(False)
        self.prefiex_lineEdit.setToolTip(PREFIX_FIELD_TIP)
        self.lowerToolBar.addWidget(self.prefix_button)
        self.lowerToolBar.addWidget(self.copyPrefix_button)
        self.lowerToolBar.addWidget(self.prefiex_lineEdit)
        self.copyPrefix_button.setAutoRaise(False)
        self.prefix_button.toggled.connect(self.prefiex_lineEdit.setEnabled)
        self.prefix_button.toggled.connect(self.copyPrefix_button.setEnabled)

    def setCurrentTabSize(self):
        self.mapSizeWidget.setSize(self.tabWidget.tabSizes[self.tabWidget.currentIndex()])

    def setWindowModified(self, modified):
        super(base_class, self).setWindowModified(modified)
        self.assignDataToNodeAct.setEnabled(modified)

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
        self.topMenuToggleButton = self.replaceWidget(self.mainPage_layout, self.topMenuToggleButton, ArrowToggleButton)
        self.bottomMenuToggleButton = self.replaceWidget(self.mainPage_layout, self.bottomMenuToggleButton, ArrowToggleButton)

    def replaceTabWidget(self):
        self.tabWidget = self.replaceWidget(self.tabWidget.parent().layout(), self.tabWidget, EditableTabWidget)

    def replaceBottomMenuWidget(self):
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
        if self.stackedWidget.currentIndex() == 0 and not self.characterLineEdit.text():
            self.__guideWidget.show()
            self.setGuideWidgetGeometry()
            self.saveTabToFileAct.setEnabled(False)
            self.editCurrentMapAct.setEnabled(False)
        else:
            self.__guideWidget.hide()
            self.saveTabToFileAct.setEnabled(True)
            self.editCurrentMapAct.setEnabled(True)

    def tabPoupMenuBuild(self):
        try:
            self.mayaLayout = toMayaObject(self.tabWidget)
            self.__mayaPopupMenu__ = mel.eval('locusPicker:buildMapPopupMenu("%s", "LocusPickerUI.__window__")' % self.mayaLayout)
        except:
            pass

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

    def getEnvPath(self):
        if INMAYA:
            return os.path.join(mel.eval('internalVar -userPrefDir'), 'locusPicker.ini')
        else:
            return os.path.join(os.path.dirname(sys.modules[self.__module__].__file__), '__setting.ini')

    def closeEvent(self, event):
        if not self.checkUnsaved():
            event.ignore()
        else:
            self.toolDialog.close()
            self.itemEditor.saveIniSettings()
            self.saveIniSettings()
            self.tabWidget.tabSizeChange.disconnect()
            self.tabWidget.clear()
            self.setWindowObj(None)
            for cb in self.__callbacks:
                api.MMessage.removeCallback(cb)

            if hasattr(self, '__mayaPopupMenu__') and self.__mayaPopupMenu__:
                mc.deleteUI(self.__mayaPopupMenu__)
            self.dispatcher.stop()
        return

    def saveIniSettings(self):
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('Window')
        geometry = self.geometry()
        if geometry.top() < 30:
            geometry.moveTop(30)
        if geometry.left() < 8:
            geometry.moveLeft(8)
        settings.setValue('Geometry', geometry)
        settings.setValue('State', self.saveState())
        settings.setValue('RecentDirectory', self.__recentDirectory)
        settings.setValue('PalettePosition', self.paletteDialog.pos())
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
        if value:
            self.setGeometry(value)
        value = settings.value('RecentDirectory')
        if value:
            self.__recentDirectory = value
        value = settings.value('PalettePosition')
        if value:
            self.paletteDialog.move(value)
        settings.endGroup()
        settings.beginGroup('Menu')
        value = settings.value('ButtonColor')
        if value:
            self.colorButton.setColor(value)
        value = settings.value('ButtonMode')
        if value:
            self.commandTypeComboBox.setCurrentIndex(max(0, self.commandTypeComboBox.findText(value)))
        value = settings.value('TopMenuVisible')
        if value:
            self.topMenuVisible = eval(value.capitalize())
        value = settings.value('BottomMenuVisible')
        if value:
            self.bottomMenuVisible = eval(value.capitalize())
        settings.endGroup()

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
        pickerNodes = self.filterPickerNode()
        if pickerNodes:
            self.stackedWidget.setCurrentIndex(0)
        else:
            self.moveToInitPage()
        return pickerNodes

    def resizeToTab(self, size):
        margin = self.verticalLayout.contentsMargins()
        w = margin.left() + margin.right()
        h = margin.top() + margin.bottom() + self.topMenuToggleButton.height() + self.bottomMenuToggleButton.height()
        if self.topMenuVisible:
            h += self.upperToolBar.height() + self.lowerToolBar.height()
        if self.bottomMenuVisible:
            h += self.bottomMenuWidget.height()
        self.resize(size + QSize(w, h))

    def setPrefix(self, index):
        tab = self.tabWidget.widget(index)
        if not tab:
            return
        if tab.usePrefix:
            self.prefix_button.setChecked(True)
            self.prefiex_lineEdit.setText(tab.prefix)
        else:
            self.prefix_button.setChecked(False)
            self.prefiex_lineEdit.setText('')
            self.matchPrefixToCurrentMap()

    def matchPrefixToCurrentMap(self):
        try:
            charName = self.characterLineEdit.text()
            subSetName = self.tabWidget.tabText(self.tabWidget.currentIndex())
            pickerNode = mel.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (self.listToArray(self.filterPickerNode()), charName, subSetName))
            if pickerNode != 'None':
                self.getPrefixFromPickerNode(pickerNode)
        except:
            pass

    def getPrefixFromPickerNode(self, node):
        usePrefix = mel.eval('getAttr %s.usePrefix' % node)
        self.prefix_button.setChecked(usePrefix)
        prefix = mel.eval('getAttr %s.prefix' % node)
        if prefix:
            self.prefiex_lineEdit.setText(prefix)
        else:
            split = node.rsplit(':', 1)
            if len(split) == 2:
                self.prefiex_lineEdit.setText(split[0] + ':')
                self.prefix_button.setChecked(True)
            else:
                self.prefiex_lineEdit.setText('')

    def setPrefixFromSelectedNode(self):
        node = mel.eval('ls -sl')
        if node:
            node = node[0]
        else:
            return
        split = node.rsplit(':', 1)
        if len(split) == 2:
            self.prefiex_lineEdit.setText(split[0] + ':')
        else:
            self.prefiex_lineEdit.setText('')

    def storeUsePrefix(self, toggle):
        tab = self.tabWidget.currentWidget()
        tab.usePrefix = toggle

    def storePrefix(self, text):
        tab = self.tabWidget.currentWidget()
        tab.prefix = text

    def showColorPicker(self, colorButton):
        modifier = QApplication.keyboardModifiers()
        buttonColor = colorButton.color()
        if modifier == Qt.NoModifier:
            returnStr = mel.eval('colorEditor -rgb %f %f %f;' % buttonColor.getRgbF()[:3])
            colorValues = [ eval(c) for c in returnStr.split() ]
            if colorValues[-1]:
                colorButton.setColor(QColor.fromRgbF(*colorValues[:3]))
        elif modifier == Qt.ControlModifier and colorButton != self.toolDialog.customColor_button:
            self.paletteDialog.clearSelection()
            self.paletteDialog.show()
            self.paletteDialog.designatedButton = colorButton
            settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
            settings.beginGroup('Window')
            value = settings.value('PalettePosition')
            settings.endGroup()
            if value:
                if value.x() > 0 and value.y() > 8:
                    return
            self.moveWidgetAccordingToWindow(self.paletteDialog)

    def changeButtonColorValue(self, button, value):
        hue = button.color().hue()
        sat = button.color().saturation()
        button.setColor(QColor.fromHsv(hue, sat, value))

    def setItemCommand(self, item):
        item.command = self.commandTypeComboBox.currentText()
        self.defineMember(item)

    def redefineMember(self, item):
        from const import question
        if not question('Are you sure to re-define the members?', 'Re-define Members', self):
            return
        if mel.eval('ls -sl;'):
            if item.command in ('Toggle', 'Range'):
                if not self.getSelectedChannel():
                    warn('Please select attributes in Channel Box first, then try again.', parent=self)
            self.defineMember(item)
            self.setWindowModified(True)
        else:
            warn('Please select nodes first, then try again.', parent=self)

    def changeMember(self, item, changeNode, changeChannel, prevCommand):
        if changeNode:
            selected = mel.eval('ls -sl;')
            if not selected:
                item.command = prevCommand
                warn('Please select nodes first, then try again.', parent=self)
            item.targetNode = selected
        if changeChannel == 0:
            if item.targetNode:
                item.targetChannel = self.getKeyableAttr(item.targetNode, item.command)
        elif changeChannel == 1:
            item.targetChannel = ['tx',
             'ty',
             'tz',
             'rx',
             'ry',
             'rz',
             'sx',
             'sy',
             'sz']
        elif changeChannel == 2:
            selectedChannel = self.getSelectedChannel()
            if selectedChannel:
                item.targetChannel = selectedChannel
            else:
                item.command = prevCommand
                warn('Please select attributes in Channel Box first, then try again.', parent=self)
        if item.command == 'Pose':
            self.defineValue(item, item.targetNode, item.targetChannel)
        item.checkSignals(prevCommand)
        replaceType = ''
        if prevCommand not in ('Pose', 'Range') and item.command in ('Pose', 'Range'):
            replaceType = 'RectangleSlider'
        elif prevCommand in ('Pose', 'Range') and item.command not in ('Pose', 'Range'):
            replaceType = 'Rectangle'
        if replaceType:
            scene = self.tabWidget.currentScene()
            width, height = item.width, item.height
            if replaceType == 'RectangleSlider' and width < 40:
                width = 40
            newItem = scene.addVarsItem(type=replaceType, pos=item.pos(), color=item.color, command=item.command, node=item.targetNode, channel=item.targetChannel, value=item.targetValue, width=width, height=height)
            scene.removeItem(item)
        self.setWindowModified(True)

    def defineMember(self, item, channel = []):
        try:
            selected = mel.eval('ls -sl;')
            item.targetNode = selected and selected or []
            if channel:
                item.targetChannel = channel[:]
            else:
                self.defineChannel(item, item.targetNode)
            self.defineValue(item, item.targetNode, item.targetChannel)
        except StandardError:
            traceback.print_exc()

    def defineChannel(self, item, nodes, channel = []):
        if not channel:
            channel = nodes and self.getKeyableAttr(nodes, item.command) or []
        item.targetChannel = channel

    def defineValue(self, item, nodes, channel):
        if item.command == 'Pose':
            dataBlock = []
            for node in nodes:
                dataBuffer = []
                for ch in channel:
                    if mel.eval('attributeQuery -ex -n %s %s;' % (node, ch)):
                        value = mel.eval('getAttr %s.%s' % (node, ch))
                        if value is not None:
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
                        channelBuf = mel.eval('listAttr -k -s -sn %s' % node)
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
                    node = mel.eval('ls -sl')[0]
                    for ch in channels:
                        if not mel.eval('attributeQuery -n %s -rangeExists %s' % (node, ch)):
                            return bool(warn('Attribute does not have a range : ' + ch, parent=self))

                    return True
                else:
                    return bool(warn('Please select attributes in Channel Box first, then try again.', parent=self))
        except:
            traceback.print_exc()
            return False

    def addDropItems(self, pos, color, modifier):
        try:
            selected = mel.eval('ls -sl;')
        except:
            selected = []

        if not self.checkProperChannel():
            return
        scene = self.tabWidget.currentScene()
        commandType = self.commandTypeComboBox.currentText()
        if commandType in ('Select', 'Toggle', 'Key', 'Reset'):
            itemType = 'Rectangle'
        else:
            itemType = 'RectangleSlider'
        if itemType == 'RectangleSlider':
            self.doAddItems(itemType, selected, scene, modifier, pos, color, commandType, attach=Attachment.BOTTOM)
        else:
            self.doAddItems(itemType, selected, scene, modifier, pos, color, commandType)
        self.setWindowModified(True)

    def addItemFromToolDialog(self, pos, color, command, data):
        try:
            selected = mel.eval('ls -sl;')
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
        if not self.checkProperChannel(command):
            return
        scene = self.tabWidget.currentScene()
        if command in ('Select', 'Toggle', 'Key', 'Reset'):
            itemType = 'Rectangle'
        else:
            itemType = 'RectangleSlider'
        if 'AttributeOption' in data:
            attributeOption = data.pop('AttributeOption')
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
            changeTool = data.pop('ChangeTool')
            if changeTool == 'Move tool':
                command += ' Move'
            elif changeTool == 'Rotate tool':
                command += ' Rotate'
            elif changeTool == 'Scale tool':
                command += ' Scale'
        if 'width' in data and 'height' in data:
            data['size'] = [data.pop('width'), data.pop('height')]
        if 'NumberOfButtons' in data:
            numberOfButtons = data.pop('NumberOfButtons')
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
            warn('You have to select targets', parent=self)

    def doAddItems(self, itemType, selected, scene, modifier, pos, color, commandType, attach = None, channel = []):
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

    def addSingleButton(self, itemType, selected, scene, pos, color, commandType, channel = [], **kwargs):
        if itemType == 'Rectangle':
            item = scene.addVarsItem(type=itemType, pos=pos, color=color, command=commandType, **kwargs)
        elif itemType == 'RectangleSlider':
            if 'attach' not in kwargs:
                kwargs['attach'] = Attachment.BOTTOM
            if 'backward' not in kwargs:
                kwargs['backward'] = False
            if 'size' not in kwargs:
                if Attachment.isHorizontal(kwargs['attach']):
                    kwargs['size'] = [40, 60]
                else:
                    kwargs['size'] = [60, 40]
            item = scene.addVarsItem(type=itemType, pos=pos, color=color, command=commandType, **kwargs)
        self.defineMember(item, channel)

    def addButtonHorizontally(self, itemType, selected, scene, pos, color, commandType, channel = [], **kwargs):
        selected.sort(key=lambda x: mc.xform(x, q=1, ws=1, rp=1)[0])
        if itemType == 'Rectangle':
            if 'size' in kwargs:
                size = kwargs['size']
            else:
                size = kwargs.setdefault('size', [20, 20])
        elif itemType == 'RectangleSlider':
            if 'attach' not in kwargs or kwargs['attach'] == None:
                kwargs['attach'] = Attachment.RIGHT
            if 'backward' not in kwargs:
                kwargs['backward'] = False
            if Attachment.isHorizontal(kwargs['attach']):
                if 'size' in kwargs:
                    size = kwargs['size']
                else:
                    size = kwargs.setdefault('size', [20, 60])
            elif 'size' in kwargs:
                size = kwargs['size']
            else:
                size = kwargs.setdefault('size', [60, 20])
        pos = scene.enlargeUptoUnited(pos, QRectF(pos, QSizeF(size[0] * len(selected) + 3 * (len(selected) - 1), size[1])))
        if pos is None:
            return
        else:
            for sel in selected:
                item = self.addItemToScene(scene, itemType, pos, sel, color, commandType, channel, **kwargs)
                pos = item.sceneBoundingRect().topRight() + QPointF(3, 0)

            return

    def addButtonVertically(self, itemType, selected, scene, pos, color, commandType, channel = [], **kwargs):
        selected.sort(key=lambda x: mc.xform(x, q=1, ws=1, rp=1)[1], reverse=True)
        if itemType == 'Rectangle':
            if 'size' in kwargs:
                size = kwargs['size']
            else:
                size = kwargs.setdefault('size', [20, 20])
        elif itemType == 'RectangleSlider':
            if 'attach' not in kwargs or kwargs['attach'] == None:
                kwargs['attach'] = Attachment.BOTTOM
            if 'backward' not in kwargs:
                kwargs['backward'] = False
            if Attachment.isHorizontal(kwargs['attach']):
                if 'size' in kwargs:
                    size = kwargs['size']
                else:
                    size = kwargs.setdefault('size', [20, 60])
            elif 'size' in kwargs:
                size = kwargs['size']
            else:
                size = kwargs.setdefault('size', [60, 20])
        pos = scene.enlargeUptoUnited(pos, QRectF(pos, QSizeF(size[0], size[1] * len(selected) + 3 * (len(selected) - 1))))
        if pos is None:
            return
        else:
            for sel in selected:
                item = self.addItemToScene(scene, itemType, pos, sel, color, commandType, channel, **kwargs)
                pos = item.sceneBoundingRect().bottomLeft() + QPointF(0, 3)

            return

    def addButtonMayaCapture(self, itemType, selected, scene, pos, color, commandType, channel = [], **kwargs):
        camera = mel.eval('locusPicker:getActiveCamera()')
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
                    kwargs['attach'] = Attachment.RIGHT
                if 'backward' not in kwargs:
                    kwargs['backward'] = False
                if Attachment.isHorizontal(kwargs['attach']):
                    if 'size' in kwargs:
                        size = kwargs['size']
                    else:
                        size = kwargs.setdefault('size', [20, 60])
                elif 'size' in kwargs:
                    size = kwargs['size']
                else:
                    size = kwargs.setdefault('size', [60, 20])
            avgSize = reduce(lambda x, y: x + y, size) / (len(size) * 1.0) * 1.4
            points = mel.eval('locusPicker:getPositionsForCapture(%s, "%s", %d);' % (self.listToArray(selected), camera, avgSize))
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

    def loadNodeData(self, nodes):
        for tab_index, node in enumerate(nodes):
            subSet = mel.eval('getAttr %s.subSetName' % node)
            self.tabWidget.addGraphicsTab(subSet, changeCurrent=False)
            size = mel.eval('getAttr %s.bgSize' % node)
            if size:
                size = QSize(*[ int(v) for v in size.split(',') ])
                self.tabWidget.tabSizes.append(size)
            scene = self.tabWidget.sceneAtIndex(tab_index)
            useBgColor = mel.eval('getAttr %s.useBgColor' % node)
            bgColor = mel.eval('getAttr %s.bgColor' % node)
            if bgColor:
                self.tabWidget.sceneAtIndex(tab_index).color = QColor.fromRgb(*[ int(v) for v in bgColor.split(',') ])
            bgImage = mel.eval('getAttr %s.bgImage' % node)
            if bgImage:
                scene.setBackgroundPixmap(bgImage)
            scene.useBGimage = not useBgColor
            types = mel.eval('locusPicker:getStringArray("%s", "type")' % node)
            positions = mel.eval('locusPicker:getStringArray("%s", "position")' % node)
            sizes = mel.eval('locusPicker:getStringArray("%s", "size")' % node)
            colors = mel.eval('locusPicker:getStringArray("%s", "color")' % node)
            commands = mel.eval('locusPicker:getStringArray("%s", "command")' % node)
            nodes = mel.eval('locusPicker:getStringArray("%s", "node")' % node)
            channels = mel.eval('locusPicker:getStringArray("%s", "channel")' % node)
            values = mel.eval('locusPicker:getStringArray("%s", "value")' % node)
            labels = mel.eval('locusPicker:getStringArray("%s", "label")' % node)
            icons = mel.eval('locusPicker:getStringArray("%s", "icon")' % node)
            hashcodes = mel.eval('locusPicker:getStringArray("%s", "hashcode")' % node)
            groupAssembly = {}
            for i in range(len(types)):
                node = nodes[i] and nodes[i].split(',') or []
                hashcode = i < len(hashcodes) and hashcodes[i] or ''
                if types[i] == 'Group':
                    doKey, doReset, labelPos, buttonPos = decodeGroupCommandStr(commands[i])
                    dataBlock = dict(type=types[i], pos=QPointF(*[ float(v) for v in positions[i].split(',') ]), size=[ float(v) for v in sizes[i].split(',') ], label=labels[i], doKey=doKey, doReset=doReset, hashcode=hashcode, labelPos=labelPos, buttonPos=buttonPos)
                else:
                    channel = channels[i] and channels[i].split(',') or []
                    icon = decodeIconStr(icons[i], types[i])
                    label = decodeLabelStr(labels[i])
                    if commands[i].startswith('Range') or commands[i].startswith('Pose'):
                        command, attach, backward = decodeCommandStr(commands[i])
                        sizeSplit = sizes[i].split(';', 1)
                        if len(sizeSplit) == 2:
                            size, slider = sizeSplit
                        else:
                            size, slider = sizeSplit[0], '3,3,16'
                        dataBlock = dict(type=types[i], pos=QPointF(*[ float(v) for v in positions[i].split(',') ]), size=[ float(v) for v in size.split(',') ], color=QColor.fromRgb(*[ int(v) for v in colors[i].split(',') ]), command=command, node=node, channel=channel, value=self.complexListData(values[i]), label=label, attach=Attachment.getAttachment(attach), slider=[ float(v) for v in slider.split(',') ], backward=backward, icon=icon, hashcode=hashcode)
                    else:
                        dataBlock = dict(type=types[i], pos=QPointF(*[ float(v) for v in positions[i].split(',') ]), size=[ float(v) for v in sizes[i].split(',') ], color=QColor.fromRgb(*[ int(v) for v in colors[i].split(',') ]), command=commands[i], node=node, channel=channel, value=self.complexListData(values[i]), label=label, icon=icon, hashcode=hashcode)
                item = self.tabWidget.sceneAtIndex(tab_index).addVarsItem(**dataBlock)
                if types[i] == 'Group':
                    groupAssembly[item] = node[:]

            for item, child_hash in groupAssembly.items():
                for child in scene.findHashcodeItems(child_hash):
                    child.setParentItem(item)

    def refresh(self, *args):
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
            curCharName = self.characterLineEdit.text()
            characterNames = [ mel.eval('getAttr %s.characterName' % node) for node in nodes ]
            if not characterNames:
                return
            characterNames = list(set(characterNames))
            characterNames.sort()
            index = not characterNames.count(curCharName) and -1 or characterNames.index(curCharName)
            charName = index >= 0 and characterNames[index] or characterNames[0]
            self.characterLineEdit.labels = characterNames
            self.characterLineEdit.setText(charName)
            filteredNodes = mel.eval('locusPicker:filterMapNodeCharacter(%s, "%s")' % (self.listToArray(self.filterPickerNode()), charName))
            filteredNodes.sort(key=lambda x: mc.getAttr(x + '.tabOrder'))
            self.loadNodeData(filteredNodes)
            if currentIndex > 0:
                self.tabWidget.setCurrentIndex(currentIndex)
            else:
                self.tabWidget.emitTabSizeChange(0)
            self.checkMainPage()
            self.setWindowModified(False)
            return

    def createCharacter(self):
        if not self.checkUnsaved():
            return
        self.moveToInitPage(False)

    def editCurrentMap(self):
        self.moveToInitPage(True)

    def showImageBrowser(self, edit, path):
        dirPath = os.path.dirname(path)
        if not os.path.exists(dirPath):
            dirPath = os.path.expanduser('~')
        from dialog import OpenFileDialog
        path = OpenFileDialog('Image File', dirPath, IMAGE_FILE_FILTER, IMAGE_FILE_FILTER.split(';;')[1], self)
        if path:
            if os.path.exists(path):
                edit.setText(path)
            else:
                print 'not existing path'

    def moveToInitPage(self, edit = False):
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
            self.characterName_lineEdit.setText(self.characterLineEdit.text())
            index = self.tabWidget.currentIndex()
            scene = self.tabWidget.currentScene()
            self.subSetName_lineEdit.setText(self.tabWidget.tabText(index))
            self.initDo_button.clicked.connect(self.doEditCurrentMap)
            self.initFileDo_button.clicked.connect(self.saveCurrentToFile)
            self.bgColor_button.setColor(scene.color)
            self.useBG_buttonGrp.button(scene.useBGimage and 1 or 0).setChecked(True)
            self.bgImagePath_lineEdit.setText(scene.imagePath)
            size = self.tabWidget.tabSizes[index]
            self.mapWidth_spinBox.setValue(size.width())
            self.mapHeight_spinBox.setValue(size.height())
        else:
            from const import DEF_CHARNAME, DEF_MAPNAME, getNumericName, INIT_CREATE_TIP, INIT_IMPORT_TIP
            self.type_label.setText('---- CREATE NEW MAP ----')
            self.initDo_button.setText('Create New Map')
            self.initDo_button.setToolTip(INIT_CREATE_TIP)
            self.initFileDo_button.setText('Import Map File')
            self.initFileDo_button.setToolTip(INIT_IMPORT_TIP)
            if self.characterLineEdit.text():
                self.characterName_lineEdit.setText(self.characterLineEdit.text())
            else:
                self.characterName_lineEdit.setText(getNumericName(DEF_CHARNAME, self.characterLineEdit.labels))
            self.subSetName_lineEdit.setText(getNumericName(DEF_MAPNAME, [ self.tabWidget.tabText(i) for i in range(self.tabWidget.count()) ]))
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
            if mapName in [ self.tabWidget.tabText(i) for i in range(self.tabWidget.count()) ]:
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
            if os.path.exists(imgPath):
                scene.setBackgroundPixmap(imgPath)
        scene.color = self.bgColor_button.color()
        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget.tabSizes[index] = QSize(width, height)
        self.tabWidget.emitTabSizeChange(index)
        self.assignDataToNode(mapName)

    def doEditCurrentMap(self):
        charName = self.characterName_lineEdit.text()
        if not charName:
            return warn('Need character name', parent=self)
        mapName = self.subSetName_lineEdit.text()
        if not mapName:
            return warn('Need map name', parent=self)
        index = self.tabWidget.currentIndex()
        currentMapName = self.tabWidget.tabText(index)
        if charName == self.characterLineEdit.text():
            if mapName != currentMapName:
                self.tabWidget.setTabText(index, mapName)
                self.syncNodeSubset(currentMapName, mapName)
            self.editMapFromInitPage(index)
        else:
            allPickerNodesArray = self.listToArray(self.filterPickerNode())
            filteredNodes = mel.eval('locusPicker:filterMapNodeCharacter(%s, "%s")' % (allPickerNodesArray, charName))
            mapNames = [ mc.getAttr(n + '.subSetName') for n in filteredNodes ]
            tabOrders = [ mc.getAttr(n + '.tabOrder') for n in filteredNodes ]
            if charName in self.characterLineEdit.labels:
                if mapName in mapNames:
                    return warn('Map name already exists : ' + mapName, parent=self)
            self.editMapFromInitPage(index)
            self.assignDataToNode(currentMapName)
            currentCharName = self.characterLineEdit.text()
            pickerNode = mel.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (allPickerNodesArray, currentCharName, currentMapName))
            pickerNode = mel.eval('rename %s "locusPicker_%s_%s";' % (pickerNode, charName, mapName))
            mel.eval('setAttr %s.characterName -type "string" "%s";' % (pickerNode, charName))
            mel.eval('setAttr %s.subSetName -type "string" "%s";' % (pickerNode, mapName))
            if tabOrders:
                mel.eval('setAttr %s.tabOrder %d;' % (pickerNode, tabOrders[-1] + 1))
            newCharNames = []
            for node in self.filterPickerNode():
                name = mc.getAttr(node + '.characterName')
                if name not in newCharNames:
                    newCharNames.append(name)

            self.characterLineEdit.labels[:] = newCharNames
            self.characterLineEdit.doSelectText(charName)
        self.stackedWidget.setCurrentIndex(0)
        self.setWindowModified(True)

    def editMapFromInitPage(self, index):
        width, height = self.mapWidth_spinBox.value(), self.mapHeight_spinBox.value()
        self.tabWidget.tabSizes[index] = QSize(width, height)
        self.tabWidget.emitTabSizeChange(index)
        scene = self.tabWidget.sceneAtIndex(index)
        scene.useBGimage = bool(self.useBG_buttonGrp.checkedId())
        imgPath = self.bgImagePath_lineEdit.text()
        if scene.useBGimage:
            if os.path.exists(imgPath):
                scene.setBackgroundPixmap(imgPath)
        else:
            scene.imagePath = imgPath
        scene.color = self.bgColor_button.color()

    def cancelInitPage(self):
        index = self.tabWidget.currentIndex()
        self.tabWidget.emitTabSizeChange(index)
        self.stackedWidget.setCurrentIndex(0)

    def createCharacter_obsolete(self):
        from const import DEF_CHARNAME
        if not self.characterLineEdit.labels:
            self.tabWidget.clear()
            self.characterLineEdit.labels = [DEF_CHARNAME]
            self.setWindowModified(True)
        else:
            if not self.checkUnsaved():
                return
            self.tabWidget.clear()
            from const import getNumericName
            charName = getNumericName(DEF_CHARNAME, self.characterLineEdit.labels)
            self.characterLineEdit.appendLabel(charName)
            self.setWindowModified(True)

    def beforeChangeCharacter(self):
        if self.checkUnsaved():
            self.characterLineEdit.wait = WaitState.Proceed
        else:
            self.characterLineEdit.wait = WaitState.GoBack

    def changeCharacter(self, charName):
        nodes = self.filterPickerNode()
        if nodes is None:
            return
        else:
            self.tabWidget.clear()
            filteredNodes = mel.eval('locusPicker:filterMapNodeCharacter(%s, "%s")' % (self.listToArray(self.filterPickerNode()), charName))
            filteredNodes.sort(key=lambda x: mc.getAttr(x + '.tabOrder'))
            if filteredNodes:
                self.loadNodeData(filteredNodes)
                self.tabWidget.emitTabSizeChange(0)
            self.setWindowModified(False)
            return

    def assignDataToNode(self, specificMap = ''):
        if not isinstance(self.sender(), QPushButton):
            from dialog import WarnTrialDialog
            return WarnTrialDialog(self)

    def assignTabData(self, node, index):
        size = self.tabWidget.tabSizes[index]
        scene = self.tabWidget.sceneAtIndex(index)
        bgSize = '%d,%d' % (size.width(), size.height())
        useBgColor = not scene.useBGimage and 1 or 0
        bgImage = scene.imagePath
        bgColor = ','.join((unicode(v) for v in scene.color.getRgb()[:3]))
        tab = self.tabWidget.widget(index)
        usePrefix = tab.usePrefix and 1 or 0
        prefix = tab.prefix
        mel.eval('locusPicker:assignMapData("%s", "%s", %d, %d, "%s", "%s", %d, "%s");' % (node,
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
        types, positions, sizes, colors, commands, hashcodes = ([],
         [],
         [],
         [],
         [],
         [])
        nodes, channels, values, labels, icons = ([],
         [],
         [],
         [],
         [])
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

        mel.eval('locusPicker:assignButtonData("%s", %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' % (node,
         self.listToArray(types),
         self.listToArray(positions),
         self.listToArray(sizes),
         self.listToArray(colors),
         self.listToArray(commands),
         self.listToArray(nodes),
         self.listToArray(channels),
         self.listToArray(values),
         self.listToArray(labels),
         self.listToArray(icons),
         self.listToArray(hashcodes)))

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
        else:
            if item.command in ('Range', 'Pose') and typeStr in ('RectangleSlider',):
                sizeStr += ';%.2f,%.2f,%.2f' % (item.margin1, item.margin2, item.thickness)
            commandStr = encodeCommandStr(item)
            nodeStr = ','.join((str(tn) for tn in item.targetNode))
            channelStr = ','.join((str(tc) for tc in item.targetChannel))
            valueStr = self.complexStringData(item.targetValue)
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

    def loadSvgFileToItems(self):
        dirPath = os.path.expanduser('~')
        from dialog import OpenFileDialog
        fileName = OpenFileDialog('Open Svg file', dirPath, SVG_FILE_FILTER, parent=self)
        if fileName:
            LocusPickerUI.__window__.tabWidget.currentScene().addItemsFromSvgFile(fileName)

    def saveDataToFile(self, index):
        from dialog import WarnTrialDialog
        WarnTrialDialog(self)

    def saveCurrentToFile(self):
        index = self.tabWidget.currentIndex()
        if index > -1:
            self.saveDataToFile(index)

    def saveAllMapToFiles(self):
        from dialog import WarnTrialDialog
        WarnTrialDialog(self)

    def doSaveDataToFile(self, path, index):
        dataNode = Element('data')
        mapNode = Element('map')
        dataNode.append(mapNode)
        tab = self.tabWidget.widget(index)
        mapNode.attrib['character'] = self.characterLineEdit.text()
        mapNode.attrib['name'] = self.tabWidget.tabText(index)
        mapNode.attrib['prefix'] = tab.prefix
        size = self.tabWidget.tabSizes[index]
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
            else:
                if item.command in ('Range', 'Pose') and getTypeString(item.type()) in ('RectangleSlider',):
                    sizeStr += ';%.2f,%.2f,%.2f' % (item.margin1, item.margin2, item.thickness)
                buttonNode.attrib['size'] = sizeStr
                buttonNode.attrib['command'] = encodeCommandStr(item)
                buttonNode.attrib['node'] = item.targetNode and ','.join(item.targetNode) or ''
                buttonNode.attrib['channel'] = item.targetChannel and ','.join(item.targetChannel) or ''
                buttonNode.attrib['value'] = item.targetValue and self.complexStringData(item.targetValue) or ''
                iconStr = encodeIconStr(item)
                buttonNode.attrib['icon'] = iconStr and iconStr or ''
                labelStr = encodeLabelStr(item)
                buttonNode.attrib['label'] = labelStr and labelStr or ''
            buttonNode.attrib['hashcode'] = item.hashcode

        from const import indentXML
        indentXML(dataNode)
        if module_exists('lxml'):
            ElementTree(dataNode).write(path)
        else:
            with open(path, 'w') as f:
                f.write(tostring(dataNode))
                f.close()
        self.__recentDirectory = os.path.dirname(path).replace('\\', '/')

    def loadDataFromFile(self):
        if self.__recentDirectory:
            dirPath = self.__recentDirectory
        else:
            dirPath = os.path.expanduser('~')
        from dialog import OpenMultiFilesDialog
        fileNames = OpenMultiFilesDialog('Open Map file', dirPath, MAP_FILE_FILTER, parent=self)
        if fileNames:
            for fn in fileNames:
                self.doLoadDataFromFile(fn)
                self.assignDataToNode(self.tabWidget.tabText(self.tabWidget.count() - 1))

            self.stackedWidget.setCurrentIndex(0)
            self.checkMainPage()
            if self.tabWidget.count() == 1:
                self.tabWidget.emitTabSizeChange(0)

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
        bgImage = mapNode.get('bgImage')
        bgColor = mapNode.get('bgColor')
        usePrefix = mapNode.get('usePrefix')
        useBgColor = mapNode.get('useBgColor')
        if character in self.characterLineEdit.labels:
            if self.characterLineEdit.text() == character:
                pass
            else:
                self.assignDataToNode()
                self.characterLineEdit.doSelectText(character)
        else:
            self.assignDataToNode()
            self.characterLineEdit.appendLabel(character)
            self.characterLineEdit.doSelectText(character)
        if mel.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (self.listToArray(self.filterPickerNode()), character, subSet)) != 'None':
            yesOrNo = confirm('Map already exists : %s\nDo you want to replace it or add as a new map?' % subSet, 'Map Exists', ['Replace', 'Add', 'Cancel'], self)
            if yesOrNo == 1:
                index = -1
                for i in range(self.tabWidget.count()):
                    if self.tabWidget.tabText(i) == subSet:
                        index = i
                        break
                    else:
                        return error('No tab', parent=self)

                tab = self.tabWidget.widget(index)
                size = QSize(*[ int(v) for v in size.split(',') ])
                self.tabWidget.tabSizes[index] = size
                if i == self.tabWidget.currentIndex():
                    self.tabWidget.emitTabSizeChange(index)
                scene = self.tabWidget.sceneAtIndex(index)
                scene.clear()
            elif yesOrNo == -1:
                tab = self.tabWidget.addGraphicsTab(subSet, changeCurrent=False)
                size = QSize(*[ int(v) for v in size.split(',') ])
                self.tabWidget.tabSizes.append(size)
                scene = self.tabWidget.sceneAtIndex(self.tabWidget.count() - 1)
            else:
                return
        else:
            tab = self.tabWidget.addGraphicsTab(subSet, changeCurrent=False)
            size = QSize(*[ int(v) for v in size.split(',') ])
            self.tabWidget.tabSizes.append(size)
            scene = self.tabWidget.sceneAtIndex(self.tabWidget.count() - 1)
        tab.prefix = prefix
        tab.usePrefix = bool(int(usePrefix))
        scene.color = QColor.fromRgb(*[ int(v) for v in bgColor.split(',') ])
        if not eval(useBgColor):
            scene.setBackgroundPixmap(bgImage)
        groupAssembly = {}
        for buttonNode in mapNode.findall('button'):
            data = dict(buttonNode.attrib)
            if data and 'type' in data:
                typeStr = data['type']
                data['pos'] = QPointF(*[ float(v) for v in data.setdefault('position', '0.0,0.0').split(',') ])
                data['color'] = QColor.fromRgb(*[ int(v) for v in data.setdefault('color', '255,0,0').split(',') ])
                if typeStr == 'Group':
                    data['size'] = [ float(v) for v in data.setdefault('size', '100,100').split(',') ]
                    data['doKey'] = data.setdefault('doKey', 'false') == 'true' and True or False
                    data['doReset'] = data.setdefault('doReset', 'false') == 'true' and True or False
                    data['labelPos'] = ButtonPosition.getPosition(data.setdefault('labelPos', 'North'))
                    data['buttonPos'] = ButtonPosition.getPosition(data.setdefault('buttonPos', 'North'))
                else:
                    if 'command' not in data:
                        continue
                    command = data['command']
                    node = data.setdefault('node', '')
                    data['node'] = node and node.split(',') or []
                    channel = data.setdefault('channel', '')
                    data['channel'] = channel and channel.split(',') or []
                    data['icon'] = decodeIconStr(data.setdefault('icon', ''), data['type'])
                    data['label'] = decodeLabelStr(data.setdefault('label', ''))
                    data['value'] = self.complexListData(data.setdefault('value', ''))
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
                if typeStr == 'Group':
                    groupAssembly[item] = data.setdefault('children', '').split(',')

        for item, child_hash in groupAssembly.items():
            for child in scene.findHashcodeItems(child_hash):
                child.setParentItem(item)

        self.__recentDirectory = os.path.dirname(path).replace('\\', '/')
        self.setWindowModified(True)

    def doLoadDataFromFile_obsolete(self, path):
        f = open(path)
        try:
            character = self.getEndLineFromFile(f)
            subSet = self.getEndLineFromFile(f)
            prefix = self.getEndLineFromFile(f)
            size = self.getEndLineFromFile(f)
            bgImage = self.getEndLineFromFile(f)
            bgColor = self.getEndLineFromFile(f)
            usePrefix = self.getEndLineFromFile(f)
            useBgColor = self.getEndLineFromFile(f)
            if character in self.characterLineEdit.labels:
                if self.characterLineEdit.text() == character:
                    pass
                else:
                    self.assignDataToNode()
                    self.characterLineEdit.doSelectText(character)
            else:
                self.assignDataToNode()
                self.characterLineEdit.appendLabel(character)
                self.characterLineEdit.doSelectText(character)
            tab = self.tabWidget.addGraphicsTab(subSet, changeCurrent=False)
            size = QSize(*[ int(v) for v in size.split(',') ])
            self.tabWidget.tabSizes.append(size)
            tab.prefix = prefix
            tab.usePrefix = bool(int(usePrefix))
            scene = self.tabWidget.sceneAtIndex(self.tabWidget.count() - 1)
            if eval(useBgColor):
                if bgColor:
                    scene.color = QColor.fromRgb(*[ int(v) for v in bgColor.split(',') ])
            else:
                pixmap = QPixmap(bgImage)
                if not pixmap.isNull():
                    scene.pixmap = pixmap
                    scene.imagePath = bgImage
            data = f.readline()
            while data:
                data = self.getDictFromFile(f)
                if data:
                    node = data['node']
                    data['node'] = node and node.split(',') or []
                    channel = data['channel']
                    data['channel'] = channel and channel.split(',') or []
                    data['icon'] = decodeIconStr(data['icon'], data['type'])
                    data['label'] = decodeLabelStr(data['label'])
                    data['color'] = QColor.fromRgb(*[ int(v) for v in data['color'].split(',') ])
                    data['value'] = self.complexListData(data['value'])
                    data['pos'] = QPointF(*[ float(v) for v in data['position'].split(',') ])
                    command = data['command']
                    if command.startswith('Range') or command.startswith('Pose'):
                        command, attach, backward = decodeCommandStr(command)
                        data['command'] = command
                        data['attach'] = Attachment.getAttachment(attach)
                        data['backward'] = backward
                        sizeSplit = data['size'].split(';', 1)
                        if len(sizeSplit) == 2:
                            size, slider = sizeSplit
                        else:
                            size, slider = sizeSplit[0], '3,3,16'
                        data['size'] = [ float(v) for v in size.split(',') ]
                        data['slider'] = [ float(v) for v in slider.split(',') ]
                    else:
                        data['size'] = [ float(v) for v in data['size'].split(',') ]
                    scene.addVarsItem(**data)

            self.setWindowModified(True)
        except StandardError:
            traceback.print_exc()
        finally:
            f.close()

    @staticmethod
    def getEndLineFromFile(f):
        data = f.readline().split(':', 1)
        if data[1]:
            result = data[1].strip()
            if result == 'N/A':
                return ''
            else:
                return result
        else:
            return ''

    @staticmethod
    def getDictFromFile(f):
        d = {}
        for data in f.readline().split('|'):
            if len(data.strip()):
                key, value = data.split(':', 1)
                key, value = key.strip().lower(), value.strip()
                if key == 'buttontype':
                    key = 'type'
                d[key] = not value == 'N/A' and value or ''

        return d

    @staticmethod
    def complexStringData(listData):
        data = []
        for singleList in listData:
            data.append(','.join([ str(v) for v in singleList ]))

        return ';'.join(data)

    @staticmethod
    def complexListData(stringData):
        data = []
        if not stringData:
            return data
        for singleData in stringData.split(';'):
            data.append([ float(v) for v in singleData.split(',') ])

        return data

    def syncNodeCharacter(self, oldCharName, newCharName):
        filteredNodes = mel.eval('locusPicker:filterMapNodeCharacter(%s, "%s")' % (self.listToArray(self.filterPickerNode()), oldCharName))
        for node in filteredNodes:
            subSet = mel.eval('getAttr %s.subSetName' % node)
            node = mel.eval('rename %s "locusPicker_%s_%s";' % (node, newCharName, subSet))
            mel.eval('setAttr %s.characterName -type "string" "%s";' % (node, newCharName))

    def syncNodeSubset(self, oldTabName, newTabName):
        charName = self.characterLineEdit.text()
        pickerNode = mel.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (self.listToArray(self.filterPickerNode()), charName, oldTabName))
        if pickerNode == 'None':
            return
        pickerNode = mel.eval('rename %s "locusPicker_%s_%s";' % (pickerNode, charName, newTabName))
        mel.eval('setAttr %s.subSetName -type "string" "%s";' % (pickerNode, newTabName))

    def checkCharacterName(self):
        if not self.characterLineEdit.labels:
            from const import DEF_CHARNAME
            self.characterLineEdit.labels = [DEF_CHARNAME]
        self.assignDataToNode(self.tabWidget.tabText(self.tabWidget.currentIndex()))
        self.setWindowModified(True)

    def removeNode(self, tabText):
        charName = self.characterLineEdit.text()
        subSetName = tabText
        pickerNode = mel.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (self.listToArray(self.filterPickerNode()), charName, subSetName))
        if pickerNode == 'None':
            return
        print 'Remove Character: [%s]\t Subset: [%s]\t Node: [%s]' % (charName, subSetName, pickerNode)
        mel.eval('delete %s;' % pickerNode)

    def selectMapNode(self, index):
        charName = self.characterLineEdit.text()
        subSetName = self.tabWidget.tabText(index)
        pickerNode = mel.eval('locusPicker:filterMapNode(%s, "%s", "%s")' % (self.listToArray(self.filterPickerNode()), charName, subSetName))
        if pickerNode == 'None':
            return
        mel.eval('select -r %s;' % pickerNode)

    @staticmethod
    def cmpNodeChannel(x, y, channelName):
        xVal = mel.eval('getAttr %s.%s' % (x, channelName))
        yVal = mel.eval('getAttr %s.%s' % (y, channelName))
        if xVal > yVal:
            return 1
        elif xVal < yVal:
            return -1
        else:
            return 0

    @staticmethod
    def filterPickerNode():
        try:
            filtered = mel.eval('ls "*.locusPickerMap"')
            if not filtered:
                filtered = []
            prefixFiltered = mel.eval('ls "*:*.locusPickerMap"')
            if prefixFiltered:
                filtered += prefixFiltered
            if filtered:
                filtered = [ str(name.split('.')[0]) for name in filtered ]
            return filtered
        except StandardError:
            return []

    @staticmethod
    def listToArray(listData):
        listData = [ str(d) for d in listData ]
        if listData:
            return str(listData).replace('[', '{').replace(']', '}').replace("'", '"')
        else:
            return '{}'

    def doCommand(self, commandType, nodes, channels, values, modifier):
        if self.prefix_button.isChecked():
            prefix = str(self.prefiex_lineEdit.text())
            if nodes and nodes != [None]:
                nodes = [ n.rsplit(':', 1)[-1] for n in nodes ]
                nodes = [ prefix + n for n in nodes ]
        try:
            if commandType == 'Deselect':
                self.__blockCallback = True
                if nodes == [None]:
                    mel.eval('select -cl;')
                elif nodes:
                    nodes = self.listToArray(nodes)
                    mel.eval('locusPicker:doSelect(%s, "deselect")' % nodes)
                self.__blockCallback = False
            elif commandType.startswith('Select'):
                self.__blockCallback = True
                if nodes:
                    nodes = self.listToArray(nodes)
                    if modifier == 'No' or modifier == 'Alt':
                        mel.eval('locusPicker:doSelect(%s, "replace")' % nodes)
                    elif modifier == 'Shift':
                        mel.eval('locusPicker:doSelect(%s, "toggle")' % nodes)
                    elif modifier == 'Ctrl+Shift':
                        mel.eval('locusPicker:doSelect(%s, "add")' % nodes)
                commandSplit = commandType.split()
                if len(commandSplit) == 2:
                    if commandSplit[1] == 'Move':
                        mel.eval('setToolTo "moveSuperContext"')
                    elif commandSplit[1] == 'Rotate':
                        mel.eval('setToolTo "RotateSuperContext"')
                    elif commandSplit[1] == 'Scale':
                        mel.eval('setToolTo "scaleSuperContext"')
                self.__blockCallback = False
            elif commandType == 'Toggle':
                self.doToggleCommand(nodes, channels)
            elif commandType == 'Key':
                self.doKeyCommand(nodes, channels)
            elif commandType == 'Reset':
                self.doResetCommand(nodes, channels)
            elif commandType == 'Range':
                idle_add(lambda : self.doRangeCommand(nodes, channels, float(modifier)))
            elif commandType == 'Pose':
                if nodes and channels and values:
                    idle_add(lambda : self.doPoseCommand(values, float(modifier)))
            elif commandType.startswith('EXEC'):
                command = commandType.split(' ', 1)[1]
                mel.eval(command)
            else:
                print 'doCommand', commandType, nodes, channels
        except StandardError:
            traceback.print_exc()

        return

    def doToggleCommand(self, nodes, channels):
        nodes = self.listToArray([ node.split('.')[0] for node in nodes ])
        channels = self.listToArray([ ch.split('.')[0] for ch in channels ])
        failed = mel.eval('locusPicker:doToggle(%s, %s)' % (nodes, channels))
        if failed:
            print '------ Toggle Failed ------'
            print '\n'.join(failed)

    def doKeyCommand(self, nodes, channels):
        nodes = self.listToArray([ node.split('.')[0] for node in nodes ])
        channels = self.listToArray([ ch.split('.')[0] for ch in channels ])
        failed = mel.eval('locusPicker:doKey(%s, %s)' % (nodes, channels))
        if failed:
            print '------ Key Failed ------'
            print '\n'.join(failed)

    def doResetCommand(self, nodes, channels):
        nodes = self.listToArray([ node.split('.')[0] for node in nodes ])
        channels = self.listToArray([ ch.split('.')[0] for ch in channels ])
        failed = mel.eval('locusPicker:doReset(%s, %s)' % (nodes, channels))
        if failed:
            print '------ Reset Failed ------'
            print '\n'.join(failed)

    def doRangeCommand(self, nodes, channels, value):
        nodes = self.listToArray([ node.split('.')[0] for node in nodes ])
        channels = self.listToArray([ ch.split('.')[0] for ch in channels ])
        failed = mel.eval('locusPicker:doRange(%s, %s, %f)' % (nodes, channels, value))
        if failed:
            print '------ Range Failed ------'
            print '\n'.join(failed)

    def doPoseCommand(self, values, modifier):
        """
        if len(values) != len(self.__poseGloalData) or len(values[0]) != len(self.__poseGloalData[0]):            
            print ">> Error : pose global variable is not matching with value"
            return
        targetValues = self.floatListToMatrix(values)
        mel.eval("locusPicker:doPose(%s, %s, %s, %s, %f)" % (self.__poseNodes, self.__poseChannels, self.__poseStartValues, targetValues, modifier))
        """
        targetValues = self.floatListToMatrix(values)
        mel.eval('locusPicker:doPoseFromDefault(%s, %s, %s, %f)' % (self.__poseNodes,
         self.__poseChannels,
         targetValues,
         modifier))

    @staticmethod
    def floatListToMatrix(listData):
        strVal = '<<' + ';'.join((','.join((unicode(s) for s in single)) for single in listData)) + '>>'
        return strVal

    def setDefaultValueExceptCurrentItem(self, item):
        scene = self.tabWidget.currentScene()
        if self.prefix_button.isChecked():
            prefix = self.prefiex_lineEdit.text()
        else:
            prefix = ''
        parentItem = item.parentItem()
        if parentItem and isinstance(parentItem, GroupItem):
            sameTargetItems = filter(lambda x: isinstance(x, RectangleDropSliderItem), scene.filterItemByCommand('Pose', item.targetNode, prefix, parentItem.childItems()))
        else:
            sameTargetItems = filter(lambda x: isinstance(x, RectangleDropSliderItem) and x.parentItem() == None, scene.filterItemByCommand('Pose', item.targetNode, prefix))
        if item in sameTargetItems:
            sameTargetItems.remove(item)
        try:
            for sameTargetItem in sameTargetItems:
                sameTargetItem.setValue(0, False)

        except:
            print 'error sameTarget', sameTargetItem

    def setPoseGlobalVariable(self, toSet, item):
        if toSet:
            idle_add(lambda : self.doSetPoseGlobalVariable(item))
        else:
            idle_add(lambda : self.doUnsetPoseGlobalVariable(item))

    def doSetPoseGlobalVariable(self, item):
        nodes = item.targetNode[:]
        if self.prefix_button.isChecked():
            prefix = str(self.prefiex_lineEdit.text())
            if nodes and nodes != [None]:
                nodes = [ n.rsplit(':', 1)[-1] for n in nodes ]
                nodes = [ prefix + n for n in nodes ]
        self.__poseNodes = self.listToArray([ node.split('.')[0] for node in nodes ])
        self.__poseChannels = self.listToArray([ ch.split('.')[0] for ch in item.targetChannel ])
        return

    def doUnsetPoseGlobalVariable(self, item):
        self.setDefaultValueExceptCurrentItem(item)
        self.__poseGloalData = []
        self.__poseNodes = None
        self.__poseChannels = None
        self.__poseStartValues = None
        return

    def alignSelectedByMode(self, axis = 'horizontal'):
        if self.__mapMode:
            if axis == 'horizontal':
                axis = 'vcenter'
            elif axis == 'vertical':
                axis = 'hcenter'
            self.alignSelectedItems(axis)
        else:
            mel.eval('locusPicker:alignGeoButtons("%s")' % axis)

    def setAverageGapByMode(self, axis = 'X'):
        if self.__mapMode:
            self.averageGapSelectedItems(axis == 'X' and 'hor' or 'ver')
        else:
            mel.eval('locusPicker:setGeoButtonsAverageGap("%s")' % axis)

    def setAverageSizeByMode(self, axis = 'X'):
        if self.__mapMode:
            self.averageSizeSelectedItems(axis == 'X' and 'width' or 'height')
        else:
            mel.eval('locusPicker:setGeoButtonsAverageSize("%s")' % axis)

    def mirrorButtonsByMode(self, search = '', replace = '', changeColor = False):
        if self.__mapMode:
            scene = self.tabWidget.currentScene()
            if not scene:
                return
            scene.mirrorSelectedItems(search, replace, changeColor)
        else:
            self.mirrorGeoButtons()

    def convertMapToGeo(self):
        mel.eval('locusPicker:removeConvertedButtons()')
        tab = self.tabWidget
        index = tab.currentIndex()
        width = tab.tabSizes[index].width() / 10.0
        height = tab.tabSizes[index].height() / 10.0
        base = mel.eval('locusPicker:createPlane("LocusPickerConvert_BG", %f, %f, %f, %f, 0, 0, 0)' % (width / -2.0,
         0,
         width,
         height))
        mel.eval('setAttr %s.characterName -type "string" "%s";' % (base, self.characterLineEdit.text()))
        mel.eval('setAttr %s.subSetName -type "string" "%s";' % (base, tab.tabText(tab.currentIndex())))
        scene = tab.currentScene()
        for i, item in enumerate(filter(lambda x: isinstance(x, AbstractDropItem), scene.items())):
            index = scene.getItemsByZValueOrder(item.sceneBoundingRect()).index(item)
            button = mel.eval('locusPicker:createPlane("%s", %f, %f, %f, %f, %f, %f, %f)' % ('LocusPickerConvert_Button%d' % i,
             item.x() / 10.0,
             item.y() / -10.0,
             item.width / 10.0,
             item.height / 10.0,
             item.minWidth / 10.0,
             item.minHeight / 10.0,
             1 + index / 10.0))
            col = tuple(map(lambda x: round(x, 2), item.color.getRgbF()[:3]))
            mel.eval('locusPicker:assignShader("%s", %f, %f, %f)' % ((button,) + col))
            typeStr, posStr, sizeStr, colorStr, commandStr, nodeStr, channelStr, valueStr, iconStr, labelStr = self.convertItemDataToString(item)
            iconStr = iconStr.split(';')[0]
            mel.eval('locusPicker:setAttrToGeoButton("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (button,
             typeStr,
             commandStr,
             nodeStr,
             channelStr,
             valueStr,
             iconStr,
             labelStr))
            if not item.icon.isNull():
                iconRect = item.iconRect.translated(item.x(), item.y())
                iconButton = mel.eval('locusPicker:createPlane("%s", %f, %f, %f, %f, 0, 0, 2)' % (button.replace('Button', 'Icon'),
                 iconRect.x() / 10.0,
                 iconRect.y() / -10.0,
                 iconRect.width() / 10.0,
                 iconRect.height() / 10.0))
                mel.eval('locusPicker:setAttachToButton("%s", "%s");' % (button, iconButton))
            if getTypeString(item.type()) == 'RectangleSlider':
                sliderButton = button.replace('Button', 'Slider')
                margin1, margin2, thickness = item.margin1 / 10.0, item.margin2 / 10.0, item.thickness / 10.0
                if item.attachment == Attachment.LEFT:
                    mel.eval('locusPicker:setSliderToButton("%s", "%s", %f, %f, %f, 0, 0);' % (button,
                     sliderButton,
                     margin1,
                     margin2,
                     thickness))
                elif item.attachment == Attachment.RIGHT:
                    mel.eval('locusPicker:setSliderToButton("%s", "%s", %f, %f, %f, 0, 1);' % (button,
                     sliderButton,
                     margin1,
                     margin2,
                     thickness))
                elif item.attachment == Attachment.TOP:
                    mel.eval('locusPicker:setSliderToButton("%s", "%s", %f, %f, %f, 1, 0);' % (button,
                     sliderButton,
                     margin1,
                     margin2,
                     thickness))
                elif item.attachment == Attachment.BOTTOM:
                    mel.eval('locusPicker:setSliderToButton("%s", "%s", %f, %f, %f, 1, 1);' % (button,
                     sliderButton,
                     margin1,
                     margin2,
                     thickness))
                else:
                    mel.eval('locusPicker:setSliderToButton("%s", "%s", %f, %f, %f, -1, 0);' % (button,
                     sliderButton,
                     margin1,
                     margin2,
                     thickness))

        mel.eval('locusPicker:setGeoModeModelView("%s")' % base)
        self.setWindowGeoMode(True)

    def setWindowGeoMode(self, geoMode):
        self.setWindowTitle(geoMode and 'Locus Picker - Geo Mode [*]' or 'Locus Picker - Map Mode [*]')
        self.__mapMode = not geoMode
        self.tabWidget.editable = self.__mapMode
        self.characterLineEdit.editable = self.__mapMode

    def convertGeoToMap(self):
        bg = mel.eval('ls -tr "LocusPickerConvert_BG";')
        if not bg:
            return warn('Not exist geo buttons', parent=self)
        subSetName = mel.eval('getAttr %s.subSetName' % bg[0])
        tab = self.tabWidget
        if tab.tabText(tab.currentIndex()) == subSetName:
            scene = tab.currentScene()
        else:
            for i in range(tab.count()):
                if tab.tabText(i) == subSetName:
                    tab.setCurrentIndex(i)
                    scene = tab.sceneAtIndex(i)
                    break
            else:
                return error('There is no tab matched', parent=self)

        w, h = mel.eval('xform -q -r -s ' + bg[0])[:2]
        self.resizeToTab(QSize(w * 10, h * 10) + QSize(4, 23))
        buttons = mel.eval('ls -tr "LocusPickerConvert_Button*";')
        if buttons:
            try:
                scene.clear()
            except:
                traceback.print_exc()

            for i, button in enumerate(buttons):
                itemType = mel.eval('getAttr %s.type' % button)
                x, y = [ round(v * 10) for v in mel.eval('xform -q -ws -t ' + button)[:2] ]
                y *= -1
                pos = QPointF(x, y)
                size = [ round(v * 10) for v in mel.eval('xform -q -ws -r -s ' + button)[:2] ]
                color = QColor.fromRgbF(*mel.eval('locusPicker:getButtonColor("%s")' % button))
                command = mel.eval('getAttr %s.command' % button)
                node = mel.eval('getAttr %s.node' % button)
                channel = mel.eval('getAttr %s.channel' % button)
                value = mel.eval('getAttr %s.value' % button)
                label = mel.eval('getAttr %s.label' % button)
                icon = mel.eval('getAttr %s.icon' % button)
                node = node and node.split(',') or []
                channel = channel and channel.split(',') or []
                if itemType == 'Path':
                    icon = icon
                elif icon:
                    x = round(mel.eval('getAttr %s.attachPosX' % button) * 10.0)
                    y = round(mel.eval('getAttr %s.attachPosY' % button) * -10.0)
                    w = round(mel.eval('getAttr %s.attachScaleX' % button) * 10.0)
                    h = round(mel.eval('getAttr %s.attachScaleY' % button) * 10.0)
                    icon = [icon, QRectF(x, y, w, h)]
                else:
                    icon = []
                label = decodeLabelStr(label)
                if itemType == 'RectangleSlider':
                    command, attach, backward = decodeCommandStr(command)
                    margin1 = round(mel.eval('getAttr %s.margin1' % button) * 10.0)
                    margin2 = round(mel.eval('getAttr %s.margin2' % button) * 10.0)
                    thickness = round(mel.eval('getAttr %s.thickness' % button) * 10.0)
                    dataBlock = dict(type=itemType, pos=pos, size=size, color=color, command=command, node=node, channel=channel, value=self.complexListData(value), label=label, attach=Attachment.getAttachment(attach), slider=[margin1, margin2, thickness], backward=backward, icon=icon)
                else:
                    dataBlock = dict(type=itemType, pos=pos, size=size, color=color, command=command, node=node, channel=channel, value=self.complexListData(value), label=label, icon=icon)
                scene.addVarsItem(**dataBlock)

        self.deleteAllGeoButtons()
        self.setWindowModified(True)

    def deleteAllGeoButtons(self):
        mel.eval('locusPicker:removeConvertedButtons()')
        mel.eval('locusPicker:setMapModeModelView()')
        self.setWindowGeoMode(False)

    def mirrorGeoButtons(self):
        from const import getMirrorColor
        search, replace = self.toolDialog.getReplaceString()
        mirroredButtons = mel.eval('locusPicker:mirrorGeoButtons("%s", "%s")' % (search, replace))
        for button in mirroredButtons:
            color = QColor.fromRgbF(*mel.eval('locusPicker:getButtonColor("%s")' % button))
            color = getMirrorColor(color)
            col = tuple(map(lambda x: round(x, 2), color.getRgbF()[:3]))
            mel.eval('locusPicker:assignShader("%s", %f, %f, %f)' % ((button,) + col))
            if mel.eval('getAttr %s.type' % button) == 'Path':
                from svgParser import createSvgPath, decodeSvgPathString, generatePathToSvg
                from const import getMirroredPath
                svgPath = mel.eval('getAttr %s.icon' % button)
                order = decodeSvgPathString(svgPath)
                path = createSvgPath(order)
                mrPath = getMirroredPath(path)
                d = generatePathToSvg(mrPath)
                mel.eval('setAttr %s.icon -type "string" "%s";' % (button, d))

    @staticmethod
    def getSelectedChannel():
        return mel.eval('channelBox -q -sma mainChannelBox;')

    @staticmethod
    def undoOpenClose(undoOpen):
        if undoOpen:
            mel.eval('undoInfo -openChunk')
        else:
            mel.eval('undoInfo -closeChunk')

    def selectionChanged(self, *args):
        if self.__blockCallback:
            return
        selected = mel.eval('ls -sl -o;')
        scene = self.tabWidget.currentScene()
        if not scene:
            return
        scene.blockSignals(True)
        scene.clearSelection()
        if selected:
            if self.prefix_button.isChecked():
                prefix = self.prefiex_lineEdit.text()
            else:
                prefix = ''
            items = scene.filterItemByCommand('Select', selected, prefix)
            for item in items:
                item.setSelected(True)

        scene.blockSignals(False)

    @classmethod
    def setWindowObj(cls, window):
        cls.__window__ = window

    @classmethod
    def windowObj(cls):
        return cls.__window__

    @classmethod
    def showPicker(cls):
        if cls.__window__:
            cls.__window__.close()
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
        self.selectGuideDialog.show()
        self.selectGuideDialog.getSelectedList()

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
        scene.alignSelectedItems(align)

    @sceneExists
    def averageGapSelectedItems(self, direction, scene = None):
        scene.averageGapSelectedItems(direction)

    @sceneExists
    def averageSizeSelectedItems(self, direction, scene = None):
        scene.averageSizeSelectedItems(direction)

    @sceneExists
    def arrangeSelectedItems(self, options, scene = None):
        scene.arrangeSelectedItems(options)

    @sceneExists
    def moveSelectedItemsToCenter(self, axis, scene = None):
        scene.moveSelectedItemsToCenter(axis)

    @sceneExists
    def mirrorItems(self, option = '', scene = None):
        if option.startswith('Replace'):
            split = option.split()
            scene.mirrorSelectedItems(split[1], split[3])
        else:
            scene.mirrorSelectedItems()

    @sceneExists
    def matchTargetNode(self, scene = None):
        nodes = [ n for n in mel.eval('locusPicker:getAllHierachyTransform()') ]
        if not nodes:
            return warn('Select a top nodes to match', parent=self)
        arrayD = self.listToArray(nodes)
        for item in scene.items():
            for i, n in enumerate(item.targetNode):
                item.targetNode[i] = mel.eval('locusPicker:getMatchedTransform(%s, "%s")' % (arrayD, str(n)))

        info('Matching nodes is done!', parent=self)

    def isToolBarVisible(self, toolBar):
        if toolBar == 'upper':
            return self.upperToolBar.isVisible()
        if toolBar == 'lower':
            return self.lowerToolBar.isVisible()

    def toggleToolBarVisible(self, toolBar):
        if toolBar == 'upper':
            self.upperToolBar.setVisible(not self.upperToolBar.isVisible())
        elif toolBar == 'lower':
            self.lowerToolBar.setVisible(not self.lowerToolBar.isVisible())

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
        return scene.sceneRect().size()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    LocusPickerUI.showPicker()
    sys.exit(app.exec_())