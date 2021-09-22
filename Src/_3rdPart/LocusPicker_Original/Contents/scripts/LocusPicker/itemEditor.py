# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\itemEditor.py
try:
    from PySide2.QtCore import QPoint, Signal, QRectF, QPointF, QSizeF, Qt, QSettings
    from PySide2.QtGui import QPalette, QColor, QIcon, QFont, QPixmap
    from PySide2.QtWidgets import QSizePolicy, QWidget, QSpinBox, QButtonGroup
except:
    from PySide.QtCore import QPoint, Signal, QRectF, QPointF, QSizeF, Qt, QSettings
    from PySide.QtGui import QSizePolicy, QPalette, QColor, QIcon, QFont, QWidget, QPixmap, QSpinBox, QButtonGroup

from loadUiType import loadUiType
from accordionWidget import AccordionWidget
from dropPathItem import PathDropItem
from decorator import accepts, returns, timestamp
from const import IMAGE_FILE_FILTER
import os, sys
try:
    import maya.cmds as mc
    INMAYA = int(mc.about(v=True))
except:
    INMAYA = 0

class KeyPressSpinBox(QSpinBox):

    def __init__(self, orient = Qt.Vertical, parent = None):
        QSpinBox.__init__(self, parent)
        self.setDisabled(True)
        self.setButtonSymbols(QSpinBox.NoButtons)
        self.setKeyboardTracking(False)
        self.__orient = orient

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if self.__orient == Qt.Vertical:
                self.stepDown()
            else:
                return
        elif event.key() == Qt.Key_Down:
            if self.__orient == Qt.Vertical:
                self.stepUp()
            else:
                return
        elif event.key() == Qt.Key_Left:
            if self.__orient == Qt.Vertical:
                return
            self.stepDown()
        elif event.key() == Qt.Key_Right:
            if self.__orient == Qt.Vertical:
                return
            self.stepUp()
        else:
            QSpinBox.keyPressEvent(self, event)


class UnifiedSpinBox(QSpinBox):
    changeValue = Signal(unicode, int)

    def __init__(self, parent = None):
        QSpinBox.__init__(self, parent)
        self.setDisabled(True)
        self.setButtonSymbols(QSpinBox.NoButtons)
        self.setKeyboardTracking(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.changeValue.emit('ver', -1)
            return
        if event.key() == Qt.Key_Down:
            self.changeValue.emit('ver', 1)
            return
        if event.key() == Qt.Key_Left:
            self.changeValue.emit('hor', -1)
            return
        if event.key() == Qt.Key_Right:
            self.changeValue.emit('hor', 1)
            return
        QSpinBox.keyPressEvent(self, event)


labelUiFile = os.path.join(os.path.dirname(__file__), 'resources', 'labelWidget.ui')
label_base_class, label_form_class = loadUiType(labelUiFile)

class LabelWidget(label_base_class, label_form_class):

    def __init__(self, parent = None):
        super(label_base_class, self).__init__(parent)
        self.setupUi(self)
        self.xPos_spinBox = self.replaceSpinBox(self.xPos_spinBox, Qt.Horizontal)
        self.yPos_spinBox = self.replaceSpinBox(self.yPos_spinBox, Qt.Vertical)
        self.label_lineEdit.textChanged.connect(lambda x: self.xPos_spinBox.setEnabled(bool(x)))
        self.label_lineEdit.textChanged.connect(lambda x: self.yPos_spinBox.setEnabled(bool(x)))
        self.label_lineEdit.textChanged.connect(lambda x: self.bold_Button.setEnabled(bool(x)))
        self.label_lineEdit.textChanged.connect(lambda x: self.italic_Button.setEnabled(bool(x)))
        self.label_lineEdit.textChanged.connect(lambda x: self.fontFamily_comboBox.setEnabled(bool(x)))
        self.label_lineEdit.textChanged.connect(lambda x: self.buttons_widget.setEnabled(bool(x)))
        self.label_lineEdit.textChanged.connect(lambda x: self.editInteractive_checkBox.setEnabled(bool(x)))
        self.xPos_spinBox.changeValue.connect(self.changeLabelPos)
        self.yPos_spinBox.changeValue.connect(self.changeLabelPos)

    def replaceSpinBox(self, spinBox, orient):
        i = self.edit_layout.indexOf(spinBox)
        tooltip = spinBox.toolTip()
        minimum, maximum = spinBox.minimum(), spinBox.maximum()
        self.edit_layout.removeWidget(spinBox)
        spinBox.deleteLater()
        spinBox = UnifiedSpinBox()
        spinBox.setRange(minimum, maximum)
        spinBox.setToolTip(tooltip)
        self.edit_layout.insertWidget(i, spinBox)
        return spinBox

    def changeLabelPos(self, direction, increment):
        if direction == 'ver':
            self.yPos_spinBox.setValue(self.yPos_spinBox.value() + increment)
        elif direction == 'hor':
            self.xPos_spinBox.setValue(self.xPos_spinBox.value() + increment)


colorUiFile = os.path.join(os.path.dirname(__file__), 'resources', 'colorWidget.ui')
color_base_class, color_form_class = loadUiType(colorUiFile)

class ColorWidget(color_base_class, color_form_class):
    colorChanged = Signal(QColor)

    def __init__(self, parent = None):
        super(color_base_class, self).__init__(parent)
        self.setupUi(self)
        self.red_spinBox.valueChanged.connect(self.adjustColor)
        self.green_spinBox.valueChanged.connect(self.adjustColor)
        self.blue_spinBox.valueChanged.connect(self.adjustColor)

    def adjustColor(self):
        color = QColor.fromRgb(self.red_spinBox.value(), self.green_spinBox.value(), self.blue_spinBox.value())
        palette = self.color_Button.palette()
        palette.setColor(QPalette.Button, color)
        self.color_Button.setPalette(palette)
        self.colorChanged.emit(color)

    def color(self):
        palette = self.color_Button.palette()
        return palette.color(QPalette.Button)

    def setColor(self, color):
        red, green, blue = color.getRgb()[:3]
        self.red_spinBox.setValue(red)
        self.green_spinBox.setValue(green)
        self.blue_spinBox.setValue(blue)


moveUiFile = os.path.join(os.path.dirname(__file__), 'resources', 'moveWidget.ui')
move_base_class, move_form_class = loadUiType(moveUiFile)

class MoveWidget(move_base_class, move_form_class):
    moveItem = Signal(QPointF)

    def __init__(self, parent = None):
        super(move_base_class, self).__init__(parent)
        self.setupUi(self)
        self.moveUpLeft_Button.clicked.connect(lambda : self.changeValue(-1, -1))
        self.moveUp_Button.clicked.connect(lambda : self.changeValue(0, -1))
        self.moveUpRight_Button.clicked.connect(lambda : self.changeValue(1, -1))
        self.moveLeft_Button.clicked.connect(lambda : self.changeValue(-1, 0))
        self.moveRight_Button.clicked.connect(lambda : self.changeValue(1, 0))
        self.moveDownLeft_Button.clicked.connect(lambda : self.changeValue(-1, 1))
        self.moveDown_Button.clicked.connect(lambda : self.changeValue(0, 1))
        self.moveDownRight_Button.clicked.connect(lambda : self.changeValue(1, 1))
        self.xPos_spinBox.valueChanged.connect(self.emitValue)
        self.yPos_spinBox.valueChanged.connect(self.emitValue)

    def changeValue(self, x, y):
        nudge = self.nudge_slider.value()
        self.xPos_spinBox.setValue(self.xPos_spinBox.value() + x * nudge)
        self.yPos_spinBox.setValue(self.yPos_spinBox.value() + y * nudge)
        self.emitValue()

    def emitValue(self):
        self.moveItem.emit(QPointF(self.xPos_spinBox.value(), self.yPos_spinBox.value()))


scaleUiFile = os.path.join(os.path.dirname(__file__), 'resources', 'scaleWidget.ui')
scale_base_class, scale_form_class = loadUiType(scaleUiFile)

class ScaleWidget(scale_base_class, scale_form_class):
    scaleItem = Signal(float, float)
    moveItem = Signal(QPointF)

    def __init__(self, parent = None):
        super(scale_base_class, self).__init__(parent)
        self.setupUi(self)
        self.__expand = True
        self.toggleAct_Button.clicked.connect(self.toggleButtons)
        self.scaleUpLeft_Button.clicked.connect(lambda : self.changeValue(1, 1, True, True))
        self.scaleUp_Button.clicked.connect(lambda : self.changeValue(0, 1, False, True))
        self.scaleUpRight_Button.clicked.connect(lambda : self.changeValue(1, 1, False, True))
        self.scaleLeft_Button.clicked.connect(lambda : self.changeValue(1, 0, True, False))
        self.scaleRight_Button.clicked.connect(lambda : self.changeValue(1, 0, False, False))
        self.scaleDownLeft_Button.clicked.connect(lambda : self.changeValue(1, 1, True, False))
        self.scaleDown_Button.clicked.connect(lambda : self.changeValue(0, 1, False, False))
        self.scaleDownRight_Button.clicked.connect(lambda : self.changeValue(1, 1, False, False))
        self.scaleUp_radioButton.toggled.connect(lambda x: x and setattr(self, 'expand', True))
        self.scaleDown_radioButton.toggled.connect(lambda x: x and setattr(self, 'expand', False))
        self.width_spinBox.valueChanged.connect(self.emitValue)
        self.height_spinBox.valueChanged.connect(self.emitValue)

    @property
    def expand(self):
        return self.__expand

    @expand.setter
    def expand(self, expand):
        self.__expand = expand
        if self.expand:
            self.scaleUp_radioButton.setChecked(True)
        else:
            self.scaleDown_radioButton.setChecked(True)
        self.setExpandState()

    def toggleButtons(self):
        self.expand ^= True

    @staticmethod
    def generateIcon(normal, disabled):
        icon = QIcon(normal)
        icon.addPixmap(QPixmap(disabled), QIcon.Disabled)
        return icon

    def setExpandState(self):
        if self.expand:
            self.scaleUpLeft_Button.setIcon(self.generateIcon(':/northwest', ':/northwest_disabled'))
            self.scaleUp_Button.setIcon(self.generateIcon(':/north', ':/north_disabled'))
            self.scaleUpRight_Button.setIcon(self.generateIcon(':/northeast', ':/northeast_disabled'))
            self.scaleLeft_Button.setIcon(self.generateIcon(':/west', ':/west_disabled'))
            self.scaleRight_Button.setIcon(self.generateIcon(':/east', ':/east_disabled'))
            self.scaleDownLeft_Button.setIcon(self.generateIcon(':/southwest', ':/southwest_disabled'))
            self.scaleDown_Button.setIcon(self.generateIcon(':/south', ':/south_disabled'))
            self.scaleDownRight_Button.setIcon(self.generateIcon(':/southeast', ':/southeast_disabled'))
            self.toggleAct_Button.setIcon(self.generateIcon(':/plusMinus', ':/plusMinus_disabled'))
        else:
            self.scaleUpLeft_Button.setIcon(self.generateIcon(':/southeast', ':/southeast_disabled'))
            self.scaleUp_Button.setIcon(self.generateIcon(':/south', ':/south_disabled'))
            self.scaleUpRight_Button.setIcon(self.generateIcon(':/southwest', ':/southwest_disabled'))
            self.scaleLeft_Button.setIcon(self.generateIcon(':/east', ':/east_disabled'))
            self.scaleRight_Button.setIcon(self.generateIcon(':/west', ':/west_disabled'))
            self.scaleDownLeft_Button.setIcon(self.generateIcon(':/northeast', ':/northeast_disabled'))
            self.scaleDown_Button.setIcon(self.generateIcon(':/north', ':/north_disabled'))
            self.scaleDownRight_Button.setIcon(self.generateIcon(':/northwest', ':/northwest_disabled'))
            self.toggleAct_Button.setIcon(self.generateIcon(':/minusPlus', ':/minusPlus_disabled'))

    def changeValue(self, x, y, xFlag, yFlag):
        nudge = self.nudge_slider.value()
        if not self.__expand:
            nudge *= -1
        deltaX = x * nudge
        deltaY = y * nudge
        width = self.width_spinBox.value()
        height = self.height_spinBox.value()
        self.width_spinBox.setValue(width + deltaX)
        self.height_spinBox.setValue(height + deltaY)
        self.emitValue()
        deltaX = self.width_spinBox.value() - width
        deltaY = self.height_spinBox.value() - height
        if xFlag:
            deltaX *= -1
        else:
            deltaX = 0
        if yFlag:
            deltaY *= -1
        else:
            deltaY = 0
        offset = QPointF(deltaX, deltaY)
        if not offset.isNull():
            self.moveItem.emit(offset)

    def emitValue(self):
        self.scaleItem.emit(self.width_spinBox.value(), self.height_spinBox.value())


iconUiFile = os.path.join(os.path.dirname(__file__), 'resources', 'iconWidget.ui')
icon_base_class, icon_form_class = loadUiType(iconUiFile)

class IconWidget(icon_base_class, icon_form_class):

    def __init__(self, parent = None):
        super(icon_base_class, self).__init__(parent)
        self.setupUi(self)
        self.xPos_spinBox = self.replaceSpinBox(self.xPos_spinBox, Qt.Horizontal)
        self.yPos_spinBox = self.replaceSpinBox(self.yPos_spinBox, Qt.Vertical)
        self.load_Button.clicked.connect(self.showDialog)
        self.path_lineEdit.textChanged.connect(lambda x: self.xPos_spinBox.setEnabled(bool(x)))
        self.path_lineEdit.textChanged.connect(lambda x: self.yPos_spinBox.setEnabled(bool(x)))
        self.path_lineEdit.textChanged.connect(lambda x: self.width_spinBox.setEnabled(bool(x)))
        self.path_lineEdit.textChanged.connect(lambda x: self.height_spinBox.setEnabled(bool(x)))
        self.path_lineEdit.textChanged.connect(lambda x: self.buttons_widget.setEnabled(bool(x)))
        self.path_lineEdit.textChanged.connect(lambda x: self.editInteractive_checkBox.setEnabled(bool(x)))
        self.xPos_spinBox.changeValue.connect(self.changeIconPos)
        self.yPos_spinBox.changeValue.connect(self.changeIconPos)

    def replaceSpinBox(self, spinBox, orient):
        row, column, rowSpan, columnSpan = self.edit_layout.getItemPosition(self.edit_layout.indexOf(spinBox))
        minimum, maximum = spinBox.minimum(), spinBox.maximum()
        tooltip = spinBox.toolTip()
        self.edit_layout.removeWidget(spinBox)
        spinBox.deleteLater()
        spinBox = UnifiedSpinBox()
        spinBox.setRange(minimum, maximum)
        spinBox.setToolTip(tooltip)
        self.edit_layout.addWidget(spinBox, row, column, rowSpan, columnSpan)
        return spinBox

    def showDialog(self):
        from dialog import OpenFileDialog
        path = OpenFileDialog('Image File', os.path.dirname(self.path_lineEdit.text()), IMAGE_FILE_FILTER, IMAGE_FILE_FILTER.split(';;')[1], self)
        if path:
            self.path_lineEdit.setText(path)
            self.path_lineEdit.returnPressed.emit()

    def changeIconPos(self, direction, increment):
        if direction == 'ver':
            self.yPos_spinBox.setValue(self.yPos_spinBox.value() + increment)
        elif direction == 'hor':
            self.xPos_spinBox.setValue(self.xPos_spinBox.value() + increment)


sliderUiFile = os.path.join(os.path.dirname(__file__), 'resources', 'sliderWidget.ui')
slider_base_class, slider_form_class = loadUiType(sliderUiFile)

class SliderWidget(slider_base_class, slider_form_class):

    def __init__(self, parent = None):
        super(slider_base_class, self).__init__(parent)
        self.setupUi(self)


uiFile = os.path.join(os.path.dirname(__file__), 'resources', 'itemEditor.ui')
base_class, form_class = loadUiType(uiFile)

class ItemEditor(base_class, form_class):
    itemModified = Signal(bool)
    colorPick = Signal(QWidget)

    def __init__(self, parent = None):
        super(base_class, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.__close = False
        layout = self.layout()
        self.tools_widget = AccordionWidget(self)
        self.tools_widget.setRolloutStyle(AccordionWidget.Maya)
        self.tools_widget.setSpacing(1)
        self.tools_widget.setMargin([0,
         2,
         0,
         2])
        self.tools_widget.setDragDropMode(AccordionWidget.InternalMove)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tools_widget.sizePolicy().hasHeightForWidth())
        self.tools_widget.setSizePolicy(sizePolicy)
        layout.insertWidget(0, self.tools_widget)
        self.labelWidget = LabelWidget(self)
        self.tools_widget.addItem('Label', self.labelWidget)
        self.iconWidget = IconWidget(self)
        self.tools_widget.addItem('Icon', self.iconWidget)
        self.colorWidget = ColorWidget(self)
        self.tools_widget.addItem('Color', self.colorWidget)
        self.moveWidget = MoveWidget(self)
        self.tools_widget.addItem('Move', self.moveWidget)
        self.scaleWidget = ScaleWidget(self)
        self.tools_widget.addItem('Scale', self.scaleWidget)
        self.sliderWidget = SliderWidget(self)
        self.tools_widget.addItem('Slider', self.sliderWidget)
        self.__offset = QPoint(8, -30)
        self.__isParentModified = False
        self.moveItself = True
        self.__item = None
        self.__iconPath = ''
        self.__iconRect = QRectF()
        self.__color = QColor()
        self.__label = ''
        self.__labelRect = QRectF()
        self.__font = QFont()
        self.__pos = QPointF()
        self.__size = QSizeF()
        self.__minSize = QSizeF()
        self.restoreIniSettings()
        self.connectSignals()
        self.createButtonGroup()
        return

    def closeEvent(self, event):
        if self.sender() == None and not self.__close:
            self.restore()
        self.__close = False
        self.checkDataChanged()
        self.clearItemConnection()
        self.saveIniSettings()
        return

    def close(self):
        self.__close = True
        super(base_class, self).close()

    def getEnvPath(self):
        if INMAYA:
            return os.path.join(mc.internalVar(upd=1), 'locusPicker.ini')
        else:
            return os.path.join(os.path.dirname(sys.modules[self.__module__].__file__), '__setting.ini')

    def saveIniSettings(self):
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('ItemEditor')
        settings.setValue('Position', self.pos())
        settings.setValue('Size', self.size())
        settings.setValue('ToolsOrder', self.getToolsOrder())
        settings.setValue('Collapsed', self.toolsCollapsed())
        settings.beginGroup('Move')
        settings.setValue('NudgeSize', self.moveWidget.nudge_slider.value())
        settings.endGroup()
        settings.beginGroup('Scale')
        settings.setValue('NudgeSize', self.scaleWidget.nudge_slider.value())
        settings.setValue('Expand', self.scaleWidget.expand)
        settings.endGroup()
        settings.endGroup()

    def restoreIniSettings(self):
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('ItemEditor')
        value = settings.value('Position')
        if value is not None:
            self.move(value)
        value = settings.value('ToolsOrder')
        if value is not None:
            self.reorderTools(value)
        settings.beginGroup('Move')
        value = settings.value('NudgeSize')
        if value is not None:
            self.moveWidget.nudge_slider.setValue(int(value))
        settings.endGroup()
        settings.beginGroup('Scale')
        value = settings.value('NudgeSize')
        if value is not None:
            self.scaleWidget.nudge_slider.setValue(int(value))
        value = settings.value('Expand')
        if value is not None:
            self.scaleWidget.expand = value == 'true' and True or False
            self.scaleWidget.setExpandState()
        settings.endGroup()
        settings.endGroup()
        return

    @property
    @returns(QPoint)
    def offset(self):
        return self.__offset

    @offset.setter
    @accepts(QPoint)
    def offset(self, offset):
        self.__offset = offset

    def width(self):
        return self.size().width()

    def show(self, isParentModified):
        self.__isParentModified = isParentModified
        super(base_class, self).show()

    def setWindowModified(self, modified):
        super(base_class, self).setWindowModified(modified)
        palette = self.assign_Button.palette()
        palette.setColor(QPalette.Button, modified and Qt.red or self.palette().color(QPalette.Button))
        self.assign_Button.setPalette(palette)

    def clearItemConnection(self):
        if self.__item:
            self.__item.comm.itemChanged.disconnect(self.setEachData)
            self.__item.removeLabelHandle()
            self.labelWidget.editInteractive_checkBox.setChecked(False)
            self.__item.removeIconHandle()
            self.iconWidget.editInteractive_checkBox.setChecked(False)
            if hasattr(self.__item, 'attachment'):
                self.__item.removeSliderHandles()
                self.sliderWidget.editInteractive_checkBox.setChecked(False)
        self.__item = None
        return

    def hide(self):
        self.checkDataChanged()
        self.clearItemConnection()

    def createButtonGroup(self):
        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.setExclusive(False)
        self.buttonGroup.addButton(self.labelWidget.editInteractive_checkBox, 0)
        self.buttonGroup.addButton(self.iconWidget.editInteractive_checkBox, 0)
        self.buttonGroup.addButton(self.sliderWidget.editInteractive_checkBox, 0)
        self.buttonGroup.buttonClicked.connect(self.checkButtonsExclusive)

    def checkButtonsExclusive(self, button):
        if button.isChecked():
            for but in self.buttonGroup.buttons():
                if but != button:
                    but.setChecked(False)

    def connectSignals(self):
        self.connectLabelWidgetSignals()
        self.connectIconWidgetSignals()
        self.connectColorWidgetSignals()
        self.connectMoveWidgetSignals()
        self.connectScaleWidgetSignals()
        self.connectSliderWidgetSignals()
        self.assign_Button.clicked.connect(self.saveChanges)
        self.restore_Button.clicked.connect(self.restore)

    def connectLabelWidgetSignals(self):
        self.labelWidget.label_lineEdit.textEdited.connect(self.changeItemLabel)
        self.labelWidget.bold_Button.toggled.connect(lambda x: self.changeItemFont('Bold', x))
        self.labelWidget.italic_Button.toggled.connect(lambda x: self.changeItemFont('Italic', x))
        self.labelWidget.fontFamily_comboBox.currentFontChanged.connect(lambda x: self.changeItemFont('Familiy', x.family()))
        self.labelWidget.fontSize_spinBox.valueChanged.connect(lambda x: self.changeItemFont('Size', x))
        self.labelWidget.xPos_spinBox.valueChanged.connect(lambda x: self.changeItemLabelPos(x, 'X'))
        self.labelWidget.yPos_spinBox.valueChanged.connect(lambda x: self.changeItemLabelPos(x, 'Y'))
        self.labelWidget.moveLeft_Button.clicked.connect(lambda : self.moveBelongingTo('left', 'label'))
        self.labelWidget.moveRight_Button.clicked.connect(lambda : self.moveBelongingTo('right', 'label'))
        self.labelWidget.moveTop_Button.clicked.connect(lambda : self.moveBelongingTo('top', 'label'))
        self.labelWidget.moveBottom_Button.clicked.connect(lambda : self.moveBelongingTo('bottom', 'label'))
        self.labelWidget.moveHCenter_Button.clicked.connect(lambda : self.moveBelongingTo('hcenter', 'label'))
        self.labelWidget.moveVCenter_Button.clicked.connect(lambda : self.moveBelongingTo('vcenter', 'label'))
        self.labelWidget.editInteractive_checkBox.toggled.connect(self.toggleItemLabelHandles)

    def connectIconWidgetSignals(self):
        self.iconWidget.path_lineEdit.returnPressed.connect(self.changeItemIcon)
        self.iconWidget.xPos_spinBox.valueChanged.connect(lambda x: self.changeItemIconRect(x, 'X'))
        self.iconWidget.yPos_spinBox.valueChanged.connect(lambda x: self.changeItemIconRect(x, 'Y'))
        self.iconWidget.width_spinBox.valueChanged.connect(lambda x: self.changeItemIconRect(x, 'WIDTH'))
        self.iconWidget.height_spinBox.valueChanged.connect(lambda x: self.changeItemIconRect(x, 'HEIGHT'))
        self.iconWidget.moveLeft_Button.clicked.connect(lambda : self.moveBelongingTo('left', 'icon'))
        self.iconWidget.moveRight_Button.clicked.connect(lambda : self.moveBelongingTo('right', 'icon'))
        self.iconWidget.moveTop_Button.clicked.connect(lambda : self.moveBelongingTo('top', 'icon'))
        self.iconWidget.moveBottom_Button.clicked.connect(lambda : self.moveBelongingTo('bottom', 'icon'))
        self.iconWidget.moveHCenter_Button.clicked.connect(lambda : self.moveBelongingTo('hcenter', 'icon'))
        self.iconWidget.moveVCenter_Button.clicked.connect(lambda : self.moveBelongingTo('vcenter', 'icon'))
        self.iconWidget.editInteractive_checkBox.toggled.connect(self.toggleItemIconHandles)

    def connectColorWidgetSignals(self):
        self.colorWidget.color_Button.clicked.connect(lambda : self.colorPick.emit(self.colorWidget))
        self.colorWidget.colorChanged.connect(self.changeItemColor)

    def connectMoveWidgetSignals(self):
        self.moveWidget.moveItem.connect(self.moveItem)

    def connectScaleWidgetSignals(self):
        self.scaleWidget.moveItem.connect(self.moveByItem)
        self.scaleWidget.scaleItem.connect(self.scaleItem)

    def connectSliderWidgetSignals(self):
        self.sliderWidget.editInteractive_checkBox.toggled.connect(self.toggleItemSliderHandles)

    def checkDataChanged(self):
        changed = False
        if self.__item:
            if self.__color != self.__item.color:
                changed = True
            if self.__label != self.__item.label:
                changed = True
            if self.__font != self.__item.font:
                changed = True
            if self.__labelRect != self.__item.labelRect:
                changed = True
            if self.__iconPath != self.__item.iconPath:
                changed = True
            if self.__iconRect != self.__item.iconRect:
                changed = True
            if self.__pos != self.__item.pos():
                changed = True
            if self.__size.width() != self.__item.width:
                changed = True
            if self.__size.height() != self.__item.height:
                changed = True
        if changed:
            self.itemModified.emit(True)
            self.__isParentModified = True

    def saveChanges(self):
        if self.__item:
            self.checkDataChanged()
            self.setItem(self.__item)

    def restore(self):
        self.restoreItem()
        self.close()

    def restoreItem(self):
        if self.__item:
            self.__item.color = self.__color
            self.__item.label = self.__label
            self.__item.font = self.__font
            if self.__label:
                self.__item.labelRect = self.__labelRect.adjusted(0, 0, 0, 0)
            else:
                self.__item.labelRect = QRectF()
            self.__item.iconPath = self.__iconPath
            if self.__iconPath:
                self.__item.iconRect = self.__iconRect.adjusted(0, 0, 0, 0)
            else:
                self.__item.iconRect = QRectF()
            self.__item.setPos(self.__pos)
            self.__item.width = self.__size.width()
            self.__item.height = self.__size.height()
            self.__item.minWidth = self.__minSize.width()
            self.__item.minHeight = self.__minSize.height()
            if not self.__isParentModified:
                self.itemModified.emit(False)

    def blockControlsSignals(self, block):
        self.labelWidget.bold_Button.blockSignals(block)
        self.labelWidget.italic_Button.blockSignals(block)
        self.labelWidget.xPos_spinBox.blockSignals(block)
        self.labelWidget.yPos_spinBox.blockSignals(block)
        self.iconWidget.xPos_spinBox.blockSignals(block)
        self.iconWidget.yPos_spinBox.blockSignals(block)
        self.iconWidget.width_spinBox.blockSignals(block)
        self.iconWidget.height_spinBox.blockSignals(block)
        self.colorWidget.blockSignals(block)
        self.moveWidget.blockSignals(block)
        self.scaleWidget.blockSignals(block)

    def setItem(self, item):
        self.clearItemConnection()
        self.blockControlsSignals(True)
        self.__item = item
        for i in xrange(self.tools_widget.count()):
            self.tools_widget.widgetAt(i).setEnabled(True)

        if isinstance(item, PathDropItem):
            self.labelWidget.setDisabled(True)
            self.iconWidget.setDisabled(True)
        self.__item.comm.itemChanged.connect(self.setEachData)
        self.setColorData()
        self.setIconData()
        self.setLabelData()
        self.setPosData()
        self.setSizeData()
        self.setSliderData()
        self.blockControlsSignals(False)
        self.setWindowModified(False)
        self.assign_Button.setEnabled(True)

    def clearItem(self):
        self.clearItemConnection()
        self.__item = None
        for i in xrange(self.tools_widget.count()):
            self.tools_widget.widgetAt(i).setDisabled(True)

        self.assign_Button.setDisabled(True)
        return

    def setColorData(self):
        self.__color = QColor(self.__item.color)
        self.colorWidget.red_spinBox.setValue(self.__color.red())
        self.colorWidget.green_spinBox.setValue(self.__color.green())
        self.colorWidget.blue_spinBox.setValue(self.__color.blue())

    def setIconData(self):
        self.__iconPath = self.__item.iconPath
        self.__iconRect = self.__item.iconRect.adjusted(0, 0, 0, 0)
        self.iconWidget.path_lineEdit.setText(self.__iconPath)
        self.iconWidget.xPos_spinBox.setValue(self.__iconRect.left())
        self.iconWidget.yPos_spinBox.setValue(self.__iconRect.top())
        self.iconWidget.width_spinBox.setValue(self.__iconRect.width())
        self.iconWidget.height_spinBox.setValue(self.__iconRect.height())

    def setLabelData(self):
        self.__label = self.__item.label
        self.__font = QFont(self.__item.font)
        self.__labelRect = self.__item.labelRect.adjusted(0, 0, 0, 0)
        self.labelWidget.label_lineEdit.setText(self.__label)
        self.labelWidget.bold_Button.setChecked(self.__font.bold())
        self.labelWidget.italic_Button.setChecked(self.__font.italic())
        self.labelWidget.xPos_spinBox.setValue(self.__labelRect.left())
        self.labelWidget.yPos_spinBox.setValue(self.__labelRect.top())
        self.labelWidget.fontFamily_comboBox.setCurrentFont(self.__font)
        self.labelWidget.fontSize_spinBox.setValue(self.__font.pointSize())

    def setPosData(self):
        self.__pos = self.__item.pos()
        self.moveWidget.xPos_spinBox.setValue(self.__pos.x())
        self.moveWidget.yPos_spinBox.setValue(self.__pos.y())

    def setSizeData(self):
        self.__size = QSizeF(self.__item.width, self.__item.height)
        self.__minSize = QSizeF(self.__item.minWidth, self.__item.minHeight)
        self.scaleWidget.width_spinBox.setValue(self.__size.width())
        self.scaleWidget.height_spinBox.setValue(self.__size.height())

    def setSliderData(self):
        if hasattr(self.__item, 'attachment') and self.__item.attachment:
            self.sliderWidget.parent().show()
        else:
            self.sliderWidget.parent().hide()

    def setEachData(self, changedType):
        if changedType == 'position':
            self.setPosData()
        if changedType == 'size':
            self.setSizeData()
        if changedType == 'color':
            self.setColorData()
        if changedType == 'icon':
            self.setIconData()
        if changedType == 'label':
            self.setLabelData()

    def changeItemColor(self, color):
        if self.__item:
            self.__item.color = color
            self.__item.update()
            self.setWindowModified(True)

    def changeItemLabel(self, text):
        if self.__item:
            self.__item.label = text
            if self.__item.label:
                rect = self.__item.getDefaultLabelRect()[0]
                if rect:
                    if self.__item.labelRect.isValid():
                        rect.moveTopLeft(self.__item.labelRect.topLeft())
                        boundingRect = self.__item.inboundRect()
                        if boundingRect.right() < rect.right():
                            rect.adjust(boundingRect.right() - rect.right(), 0, boundingRect.right() - rect.right(), 0)
                        if boundingRect.left() > rect.left():
                            rect.adjust(boundingRect.left() - rect.left(), 0, boundingRect.left() - rect.left(), 0)
                    self.__item.labelRect = rect
            else:
                self.__item.labelRect = QRectF()
            self.__item.matchMinSizeToSubordinate()
            topLeft = self.__item.labelRect.topLeft()
            self.labelWidget.xPos_spinBox.setValue(topLeft.x())
            self.labelWidget.yPos_spinBox.setValue(topLeft.y())
            self.scaleWidget.width_spinBox.setValue(self.__item.width)
            self.scaleWidget.height_spinBox.setValue(self.__item.height)
            self.__item.update()
            self.setWindowModified(True)

    def changeItemFont(self, option, value):
        if self.__item:
            if option == 'Bold':
                self.__item.font.setBold(value)
            if option == 'Italic':
                self.__item.font.setItalic(value)
            if option == 'Familiy':
                self.__item.font.setFamily(value)
            if option == 'Size':
                self.__item.font.setPointSize(value)
                rect = self.__item.setDefaultLabelRect()
                if rect:
                    self.__item.labelRect = rect
                self.__item.matchMinSizeToSubordinate()
                topLeft = self.__item.labelRect.topLeft()
                self.labelWidget.xPos_spinBox.setValue(topLeft.x())
                self.labelWidget.yPos_spinBox.setValue(topLeft.y())
                self.scaleWidget.width_spinBox.setValue(self.__item.width)
                self.scaleWidget.height_spinBox.setValue(self.__item.height)
            self.__item.update()
            self.setWindowModified(True)

    def changeItemLabelPos(self, value, coord):
        if self.__item:
            inboundRect = self.__item.inboundRect()
            bufferRect = self.__item.labelRect.adjusted(0, 0, 0, 0)
            if coord == 'X':
                bufferRect.moveLeft(value)
                if inboundRect.contains(bufferRect):
                    self.__item.labelRect.moveLeft(value)
                else:
                    self.labelWidget.xPos_spinBox.setValue(self.__item.labelRect.left())
            if coord == 'Y':
                bufferRect.moveTop(value)
                if inboundRect.contains(bufferRect):
                    self.__item.labelRect.moveTop(value)
                else:
                    self.labelWidget.yPos_spinBox.setValue(self.__item.labelRect.top())
            self.__item.update()
            self.setWindowModified(True)

    def toggleItemLabelHandles(self, toggle):
        if self.__item.labelRect.isValid():
            if toggle:
                self.__item.addLabelHandle()
                self.__item.repositionLabelHandle()
            else:
                self.__item.removeLabelHandle()

    def changeItemIcon(self):
        if self.__item:
            path = self.iconWidget.path_lineEdit.text()
            if path:
                if not QPixmap(path).isNull():
                    self.__item.iconPath = path
                    rect = self.__item.iconRect
                    self.iconWidget.xPos_spinBox.setValue(rect.left())
                    self.iconWidget.yPos_spinBox.setValue(rect.top())
                    self.iconWidget.width_spinBox.setValue(rect.width())
                    self.iconWidget.height_spinBox.setValue(rect.height())
                    self.update()
                    self.setWindowModified(True)
                else:
                    print '>> %s is not valid' % path
            else:
                self.__item.iconPath = ''
                self.__item.iconRect = QRectF()
                self.__item.matchMinSizeToSubordinate()
                self.iconWidget.xPos_spinBox.setValue(0)
                self.iconWidget.yPos_spinBox.setValue(0)
                self.iconWidget.width_spinBox.setValue(0)
                self.iconWidget.height_spinBox.setValue(0)
                self.setWindowModified(True)

    def changeItemIconRect(self, value, option):
        if self.__item:
            inboundRect = self.__item.inboundRect()
            bufferRect = self.__item.iconRect.adjusted(0, 0, 0, 0)
            if option == 'X':
                bufferRect.moveLeft(value)
                if inboundRect.contains(bufferRect):
                    self.__item.iconRect.moveLeft(value)
                else:
                    self.iconWidget.xPos_spinBox.setValue(self.__item.iconRect.left())
            if option == 'Y':
                bufferRect.moveTop(value)
                if inboundRect.contains(bufferRect):
                    self.__item.iconRect.moveTop(value)
                else:
                    self.iconWidget.yPos_spinBox.setValue(self.__item.iconRect.top())
            if option == 'WIDTH':
                bufferRect.setWidth(value)
                if inboundRect.contains(bufferRect):
                    self.__item.iconRect.setWidth(value)
                else:
                    self.iconWidget.width_spinBox.setValue(self.__item.iconRect.width())
            if option == 'HEIGHT':
                bufferRect.setHeight(value)
                if inboundRect.contains(bufferRect):
                    self.__item.iconRect.setHeight(value)
                else:
                    self.iconWidget.height_spinBox.setValue(self.__item.iconRect.height())
            self.__item.update()
            self.setWindowModified(True)

    def toggleItemIconHandles(self, toggle):
        if self.__item.iconRect.isValid():
            if toggle:
                self.__item.addIconHandle()
                self.__item.repositionIconHandles()
            else:
                self.__item.removeIconHandle()

    def moveItem(self, pos):
        if self.__item:
            self.__item.comm.blockSignals(True)
            self.__item.setPos(pos)
            self.__item.comm.blockSignals(False)
            self.setWindowModified(True)

    def moveByItem(self, offset):
        if self.__item:
            self.__item.comm.blockSignals(True)
            self.__item.setPos(self.__item.pos() + offset)
            self.moveWidget.xPos_spinBox.setValue(self.moveWidget.xPos_spinBox.value() + offset.x())
            self.moveWidget.yPos_spinBox.setValue(self.moveWidget.yPos_spinBox.value() + offset.y())
            self.__item.comm.blockSignals(False)
            self.setWindowModified(True)

    def scaleItem(self, width, height):
        if self.__item:
            if width >= self.__item.minWidth:
                self.__item.width = width
            else:
                self.__item.width = self.__item.minWidth
                self.scaleWidget.width_spinBox.setValue(self.__item.width)
            if height >= self.__item.minHeight:
                self.__item.height = height
            else:
                self.__item.height = self.__item.minHeight
                self.scaleWidget.height_spinBox.setValue(self.__item.height)
            self.setWindowModified(True)

    def toggleItemSliderHandles(self, toggle):
        if toggle:
            self.__item.addSliderHandles()
            self.__item.repositionSliderHandles()
        else:
            self.__item.removeSliderHandles()

    def getToolsOrder(self):
        buffer_list = []
        for i in xrange(self.tools_widget.count()):
            buffer_list.append(self.tools_widget.itemAt(i).title())

        return buffer_list

    def reorderTools(self, order):
        toolsBuffer = []
        while self.tools_widget.count():
            toolsBuffer.append(self.tools_widget.takeAt(0))

        for mo in order:
            index = -1
            for t in toolsBuffer:
                if t.title() == mo:
                    index = toolsBuffer.index(t)
                    break

            if index > -1:
                tool = toolsBuffer[index]
                del toolsBuffer[index]
                self.tools_widget.addItem(tool.title(), tool.widget())

        if toolsBuffer:
            print 'Not Added:', toolsBuffer
            for t in toolsBuffer:
                self.tools_widget.addItem(t.title(), t.widget())

    def toolsCollapsed(self):
        collapse_buffer = []
        for i in xrange(self.tools_widget.count()):
            collapse_buffer.append(self.tools_widget.itemAt(i).isCollapsed())

        return collapse_buffer

    def setToolsCollasped(self, collapse_list):
        for i, collapse in enumerate(collapse_list):
            self.tools_widget.itemAt(i).setCollapsed(collapse)
            self.tools_widget.widgetAt(i).setVisible(not collapse)

    def moveBelongingTo(self, to, belonging):
        if self.__item:
            if belonging == 'label':
                rect = self.__item.labelRect.adjusted(0, 0, 0, 0)
                if to == 'left' or to == 'right' or to == 'hcenter':
                    widget = self.labelWidget.xPos_spinBox
                elif to == 'top' or to == 'bottom' or to == 'vcenter':
                    widget = self.labelWidget.yPos_spinBox
                else:
                    return
            elif belonging == 'icon':
                rect = self.__item.iconRect.adjusted(0, 0, 0, 0)
                if to == 'left' or to == 'right' or to == 'hcenter':
                    widget = self.iconWidget.xPos_spinBox
                elif to == 'top' or to == 'bottom' or to == 'vcenter':
                    widget = self.iconWidget.yPos_spinBox
                else:
                    return
            else:
                return
            margin = self.__item.BORDER_MARGIN
            width = self.__item.width
            height = self.__item.height
            inbound = self.__item.inboundRect()
            if to == 'left':
                rect.moveLeft(inbound.left())
                widget.setValue(rect.left())
            elif to == 'hcenter':
                rect.moveCenter(inbound.center())
                widget.setValue(rect.left())
            elif to == 'right':
                rect.moveRight(inbound.right())
                widget.setValue(rect.left())
            elif to == 'top':
                rect.moveTop(inbound.top())
                widget.setValue(rect.top())
            elif to == 'vcenter':
                rect.moveCenter(inbound.center())
                widget.setValue(rect.top())
            elif to == 'bottom':
                rect.moveBottom(inbound.bottom())
                widget.setValue(rect.top())
            self.setWindowModified(True)


if __name__ == '__main__':
    from PySide.QtGui import QApplication
    import sys
    app = QApplication(sys.argv)
    w = ItemEditor()
    w.show(False)
    sys.exit(app.exec_())