# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\toolsDialog.py
try:
    from PySide2.QtCore import QRectF, Qt, QSize, QSizeF, QMimeData, Signal, QRect, QPoint, QPointF, QByteArray, QSettings, QEvent, QModelIndex, QPropertyAnimation, QEasingCurve, QUrl
    from PySide2.QtGui import QIcon, QPixmap, QPainter, QImage, QColor, QStandardItemModel, QStandardItem, QDrag, QTransform, QFontMetrics, QTextOption, QPen, QPalette, QMouseEvent, QKeyEvent
    from PySide2.QtWidgets import QStyledItemDelegate, QListView, QStyle, QButtonGroup, QLabel, QWidget, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QGridLayout, QAbstractScrollArea, QApplication, QLayout, QSizePolicy
except:
    from PySide.QtCore import QRectF, Qt, QSize, QSizeF, QMimeData, Signal, QRect, QPoint, QPointF, QByteArray, QSettings, QEvent, QModelIndex, QPropertyAnimation, QEasingCurve, QUrl
    from PySide.QtGui import QIcon, QPixmap, QPainter, QImage, QStyledItemDelegate, QColor, QListView, QStandardItemModel, QStandardItem, QDrag, QTransform, QStyle, QFontMetrics, QTextOption, QPen, QPalette, QButtonGroup, QLabel, QWidget, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QGridLayout, QMouseEvent, QAbstractScrollArea, QApplication, QKeyEvent, QLayout, QSizePolicy

from loadUiType import loadUiType
from locusPickerResources import *
from popupLineEdit import PressSendLineEdit
from sliderItemPreviewWidget import SliderItemPreviewWidget
from colorPaletteWidget import ColorPaletteWidget
from imageRegionWidget import ImageRegionWidget
from softLimitSliderSet import SoftLimitSliderSet
from const import IMAGE_FILE_FILTER, SVG_FILE_FILTER, FONT_FAMILIES, Attachment, MIME_TEMPLATE, MIME_TEMPLATE_SIZE, MIME_NEWBUTTON, MIME_COLOR, MIME_IMAGE, MIME_COMMAND, MIME_LABEL, MIME_FONT_SIZE, MIME_FONT_FAMILY, MIME_FONT_BOLD, MIME_FONT_ITALIC, MIME_CUSTOM_LABEL, warn, question
from decorator import accepts, returns
from idleQueueDispatcher import ThreadDispatcher
from codeEditor import CodeEditor
import os, glob, sys, re, shutil, math, base64, ctypes, tempfile
from functools import partial
try:
    import maya.mel as mm
    import maya.cmds as mc
    import maya.OpenMaya as om
    import maya.OpenMayaUI as omui
    INMAYA = int(mc.about(v=True))
except:
    INMAYA = 0

def getTempFile(ext):
    if not ext.startswith('.'):
        ext = '.' + ext
    return os.path.join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()) + ext).replace('\\', '/')


class AnimatedLabel(QLabel):

    def __init__(self, text = '', parent = None):
        QLabel.__init__(self, text, parent)
        font = self.font()
        font.setPointSize(18)
        font.setBold(True)
        self.setFont(font)
        self.setProperty('__opacity__', 0.0)
        self.animation = QPropertyAnimation(self, '__opacity__')
        self.animation.setDuration(800)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(0.0)
        self.animation.setKeyValueAt(0.3, 1.0)
        self.animation.setKeyValueAt(0.6, 1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.valueChanged.connect(self.setLabelOpacity)
        self.animation.finished.connect(self.hide)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self.property('__opacity__'))
        if self.text():
            painter.drawText(event.rect(), self.text())

    def showMessage(self, text):
        self.animation.stop()
        self.setText(text)
        parent = self.parent()
        if parent:
            if isinstance(parent, QAbstractScrollArea) and parent.verticalScrollBar().isVisible():
                self.move(parent.size().width() - self.fontMetrics().width(text) - 10 - parent.verticalScrollBar().width(), 0)
            else:
                self.move(parent.size().width() - self.fontMetrics().width(text) - 10, 0)
        self.animation.start()

    def setLabelOpacity(self, value):
        if self.animation.state() == QPropertyAnimation.Running:
            self.setVisible(value > 0)
            self.update()


class TemplateListView(QListView):
    AddTemplateDir = Signal(list)

    def __init__(self, parent = None):
        QListView.__init__(self, parent)
        self.setEditTriggers(QListView.NoEditTriggers)
        self.setDragEnabled(True)
        self.setDragDropMode(QListView.DragOnly)
        self.setDefaultDropAction(Qt.IgnoreAction)
        self.setAcceptDrops(True)
        self.setIconSize(QSize(120, 120))
        self.setViewMode(QListView.IconMode)
        self.setMovement(QListView.Snap)
        self.setResizeMode(QListView.Adjust)
        self.setUniformItemSizes(True)
        self.setMouseTracking(True)
        from const import TEMPLATE_LIST_TIP
        self.setToolTip(TEMPLATE_LIST_TIP)

    def startDrag(self, supportedActions):
        index = self.currentIndex()
        model = self.model()
        item = model.itemFromIndex(index)
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setData(MIME_TEMPLATE, QByteArray(str(item.text())))
        mimeData.setData(MIME_TEMPLATE_SIZE, QByteArray('%.1f %.1f' % (item.size.width(), item.size.height())))
        url = QUrl.fromLocalFile(item.text())
        mimeData.setUrls([url])
        drag.setMimeData(mimeData)
        pixmap = item.icon().pixmap(30, 30)
        drag.setDragCursor(pixmap, Qt.CopyAction)
        drag.start()

    def dragEnterEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            for path in map(lambda x: x.toLocalFile(), mimeData.urls()):
                if os.path.isdir(path) or os.path.isfile(path) and os.path.splitext(path)[-1].lower() == '.svg':
                    self.setDragDropMode(QListView.InternalMove)
                    event.accept()
                    break

        QListView.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        event.accept()
        QListView.dragMoveEvent(self, event)

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            sendData = []
            for path in map(lambda x: x.toLocalFile(), mimeData.urls()):
                if os.path.isdir(path) and glob.glob(os.path.join(path, '*.svg')) or os.path.isfile(path) and os.path.splitext(path)[-1].lower() == '.svg':
                    sendData.append(path)

            if sendData:
                self.AddTemplateDir.emit(sendData)
        self.setDragEnabled(True)
        self.setDragDropMode(QListView.DragOnly)
        self.setDefaultDropAction(Qt.IgnoreAction)
        self.setAcceptDrops(True)
        QListView.dropEvent(self, event)


class TemplateDelegate(QStyledItemDelegate):
    ICON_MARGIN = 4

    def paint(self, painter, option, index):
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        model = index.model()
        view = self.parent()
        if view.hasFocus() and option.state & QStyle.State_MouseOver:
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.gray)
            painter.drawRoundedRect(option.rect.adjusted(1, 1, -1, -1), self.ICON_MARGIN, self.ICON_MARGIN)
        pixmap = model.data(index, Qt.DecorationRole).pixmap(view.iconSize())
        pmRect = QRect(option.rect.topLeft() + QPoint(self.ICON_MARGIN + 1, self.ICON_MARGIN + 1), view.iconSize() - QSize(self.ICON_MARGIN * 2, self.ICON_MARGIN * 2))
        painter.drawPixmap(pmRect, pixmap)
        if option.state & QStyle.State_Selected:
            painter.setPen(QPen(Qt.red, 1.0, Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(option.rect.adjusted(2, 2, -2, -2))
        font = view.font()
        fm = QFontMetrics(font)
        text = os.path.splitext(os.path.basename(model.data(index, Qt.DisplayRole)))[0]
        text = fm.elidedText(text, Qt.ElideRight, view.iconSize().width() - 4)
        textOpt = QTextOption()
        textOpt.setAlignment(Qt.AlignHCenter)
        txtRect = QRectF(QPointF(pmRect.bottomLeft() + QPoint(0, 1)), QPointF(option.rect.bottomRight() - QPoint(4, 3)))
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(22, 22, 22, 220))
        painter.drawRoundedRect(txtRect.adjusted(-2, -2, 2, 2), 2, 2)
        painter.restore()
        painter.setPen(self.parent().palette().color(QPalette.WindowText))
        painter.drawText(txtRect, text, textOpt)
        font.setPointSize(8)
        fm = QFontMetrics(font)
        item = model.itemFromIndex(index)
        sizeText = '%d x %d' % (item.size.width(), item.size.height())
        sizeRect = fm.boundingRect(option.rect, Qt.AlignLeft | Qt.AlignTop, sizeText)
        sizeRect.translate(4, 4)
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(22, 22, 22, 220))
        painter.drawRoundedRect(sizeRect.adjusted(-2, -2, 2, 2), 2, 2)
        painter.restore()
        painter.setFont(font)
        painter.drawText(sizeRect, sizeText)

    def sizeHint(self, option, index):
        view = self.parent()
        return view.iconSize() + QSize(2, 14)


class TemplateDirListWidget(QListWidget):
    itemRemoved = Signal(int)
    ICON_MARGIN = 3

    def __init__(self, parent = None):
        QListWidget.__init__(self, parent)
        self.setMouseTracking(True)
        self.setEditTriggers(QListWidget.NoEditTriggers)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setWindowFlags(Qt.Popup)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setItemDelegate(RemoveDelegate(self))
        self.setIconSize(QSize(24, 24))
        palette = self.palette()
        palette.setColor(QPalette.Base, palette.color(QPalette.Window))
        self.setPalette(palette)
        self.buf = None
        self.hover = None
        return

    def visualItemRect(self, item):
        rect = QListWidget.visualItemRect(self, item)
        return rect

    def leaveEvent(self, event):
        self.hover = None
        self.buf = None
        self.update()
        QListWidget.leaveEvent(self, event)
        return

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            return
        pos = event.pos()
        index = self.indexAt(pos)
        row = index.row()
        rect = self.removeButtonRect(index)
        if rect.contains(pos):
            self.takeItem(row)
            self.itemRemoved.emit(row)
            self.updateGeometry()
            return
        if row < 0:
            self.setCurrentIndex(QModelIndex())
        QListWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        index = self.indexAt(pos)
        rect = self.removeButtonRect(index)
        self.hover = index
        if rect.contains(pos):
            if not self.buf == index:
                self.buf = index
                self.update(index)
        elif self.buf:
            self.buf = None
            self.update(index)
        QListWidget.mouseMoveEvent(self, event)
        return

    def removeButtonRect(self, index):
        item = self.itemFromIndex(index)
        r = self.visualItemRect(item)
        h = r.height()
        rect = QRect(0, 0, h - self.ICON_MARGIN * 2, h - self.ICON_MARGIN * 2)
        rect.moveTopLeft(r.topLeft() + QPoint(0, self.ICON_MARGIN))
        return rect


class RemoveDelegate(QStyledItemDelegate):

    def __init__(self, parent = None):
        QStyledItemDelegate.__init__(self, parent)
        palette = parent.palette()
        self.__textColor = palette.color(QPalette.WindowText)
        self.__hiliteTextColor = palette.color(QPalette.HighlightedText)
        self.__textOption = QTextOption()
        self.__textOption.setAlignment(Qt.AlignVCenter)
        self.__textOption.setWrapMode(QTextOption.NoWrap)

    def paint(self, painter, option, index):
        listWidget = self.parent()
        if index == self.parent().hover:
            painter.save()
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(103, 141, 178))
            painter.drawRect(option.rect)
            painter.restore()
        pm = index == listWidget.buf and QPixmap(':/closeEnabled') or QPixmap(':/closeDisabled')
        rect = self.parent().removeButtonRect(index)
        if rect.isValid():
            pos = rect.topLeft()
            pm = index == listWidget.buf and QPixmap(':/closeEnabled') or QPixmap(':/closeDisabled')
            if pm.width() > rect.width():
                pm = pm.scaledToWidth(rect.width(), Qt.SmoothTransformation)
            elif pm.width() < rect.width():
                pos += QPoint((rect.width() - pm.width()) / 2, (rect.height() - pm.height()) / 2)
            painter.drawPixmap(pos, pm)
        item = listWidget.itemFromIndex(index)
        text = item.text()
        txtRect = QRectF(option.rect)
        txtRect.moveLeft(rect.right() + 3)
        painter.setPen(index == self.parent().hover and self.__hiliteTextColor or self.__textColor)
        painter.drawText(txtRect, text, self.__textOption)


newButtonUiFile = os.path.join(os.path.dirname(__file__), 'resources', 'newButtonWidget.ui')
newButton_base_class, newButton_form_class = loadUiType(newButtonUiFile)

class NewButtonWidget(newButton_base_class, newButton_form_class):

    def __init__(self, parent = None):
        super(newButton_base_class, self).__init__(parent)
        self.setupUi(self)
        self.createButtonGroups()
        self.command_buttonGroup.buttonClicked[int].connect(self.changeUI)
        self.changeUI(0)
        self.generateColorButtons()

    def createButtonGroups(self):
        self.command_buttonGroup = QButtonGroup(self)
        self.command_buttonGroup.addButton(self.select_radioButton, 0)
        self.command_buttonGroup.addButton(self.key_radioButton, 1)
        self.command_buttonGroup.addButton(self.reset_radioButton, 2)
        self.command_buttonGroup.addButton(self.toggle_radioButton, 3)
        self.command_buttonGroup.addButton(self.pose_radioButton, 4)
        self.command_buttonGroup.addButton(self.range_radioButton, 5)
        self.changeTool_buttonGroup = QButtonGroup(self)
        self.changeTool_buttonGroup.addButton(self.noChange_radioButton, 0)
        self.changeTool_buttonGroup.addButton(self.moveTool_radioButton, 1)
        self.changeTool_buttonGroup.addButton(self.rotateTool_radioButton, 2)
        self.changeTool_buttonGroup.addButton(self.scaleTool_radioButton, 3)
        self.numberOfButton_buttonGroup = QButtonGroup(self)
        self.numberOfButton_buttonGroup.addButton(self.one_radioButton, 0)
        self.numberOfButton_buttonGroup.addButton(self.multiHorizontal_radioButton, 1)
        self.numberOfButton_buttonGroup.addButton(self.multiVertical_radioButton, 2)
        self.numberOfButton_buttonGroup.addButton(self.capture_radioButton, 3)
        self.sliderPosition_buttonGroup = QButtonGroup(self)
        self.sliderPosition_buttonGroup.addButton(self.noSlider_radioButton, 0)
        self.sliderPosition_buttonGroup.addButton(self.rightSlider_radioButton, 1)
        self.sliderPosition_buttonGroup.addButton(self.leftSlider_radioButton, 2)
        self.sliderPosition_buttonGroup.addButton(self.belowSlider_radioButton, 3)
        self.sliderPosition_buttonGroup.addButton(self.aboveSlider_radioButton, 4)
        self.attributeOption_buttonGroup = QButtonGroup(self)
        self.attributeOption_buttonGroup.addButton(self.allKeyable_radioButton, 0)
        self.attributeOption_buttonGroup.addButton(self.transformOnly_radioButton, 1)
        self.attributeOption_buttonGroup.addButton(self.selectedOnly_radioButton, 2)

    def changeUI(self, index):
        if index == 0:
            self.changeTool_widget.show()
            self.sliderPosition_widget.hide()
            self.attributeOption_widget.hide()
            self.numberOfButtons_widget.show()
        elif index in (1, 2, 3):
            self.changeTool_widget.hide()
            self.sliderPosition_widget.hide()
            self.attributeOption_widget.show()
            self.numberOfButtons_widget.hide()
            if index == 3:
                self.attributeOption_widget.setDisabled(True)
            else:
                self.attributeOption_widget.setEnabled(True)
        elif index == 4:
            self.changeTool_widget.hide()
            self.sliderPosition_widget.show()
            self.attributeOption_widget.show()
            self.attributeOption_widget.setEnabled(True)
            self.numberOfButtons_widget.hide()
        elif index == 5:
            self.changeTool_widget.hide()
            self.sliderPosition_widget.show()
            self.attributeOption_widget.show()
            self.attributeOption_widget.setDisabled(True)
            self.numberOfButtons_widget.show()

    def getButtonColors(self):
        from const import getDefaultColor as gdc
        return (gdc('RtIK'),
         gdc('RtFK'),
         gdc('CnIK'),
         gdc('CnFK'),
         gdc('LfIK'),
         gdc('LfFK'),
         QColor.fromRgbF(0, 0, 0),
         QColor.fromRgbF(0.2, 0.2, 0.2),
         QColor.fromRgbF(0.4, 0.4, 0.4),
         QColor.fromRgbF(0.6, 0.6, 0.6),
         QColor.fromRgbF(0.8, 0.8, 0.8),
         QColor.fromRgbF(1, 1, 1))

    def generateColorButtons(self):
        from const import CREATE_BUTTON_TIP
        for i, color in enumerate(self.getButtonColors()):
            label = QLabel(self)
            label.setFixedSize(16, 16)
            label.setAutoFillBackground(True)
            palette = label.palette()
            palette.setColor(label.backgroundRole(), color)
            label.setPalette(palette)
            self.colorButtons_Layout.insertWidget(i, label)
            label.__drag__ = True
            label.setToolTip(CREATE_BUTTON_TIP)

    def mousePressEvent(self, event):
        widget = self.childAt(event.pos())
        if hasattr(widget, '__drag__'):
            palette = widget.palette()
            color = palette.color(widget.backgroundRole())
            drag = QDrag(self)
            data = QMimeData()
            command = self.command_buttonGroup.checkedButton().text()
            data.setData(MIME_NEWBUTTON, QByteArray(str(command)))
            data.setColorData(color)
            if self.changeTool_widget.isVisible():
                data.setData('ToolDialog/NewButton-ChangeTool', QByteArray(str(self.changeTool_buttonGroup.checkedButton().text())))
            if self.sliderPosition_widget.isVisible():
                data.setData('ToolDialog/NewButton-SliderPosition', QByteArray(str(self.sliderPosition_buttonGroup.checkedButton().text())))
            if self.attributeOption_widget.isVisible() and self.attributeOption_widget.isEnabled():
                data.setData('ToolDialog/NewButton-AttributeOption', QByteArray(str(self.attributeOption_buttonGroup.checkedButton().text())))
            if self.numberOfButtons_widget.isVisible():
                data.setData('ToolDialog/NewButton-NumberOfButtons', QByteArray(str(self.numberOfButton_buttonGroup.checkedButton().text())))
            drag.setMimeData(data)
            pixmap = QPixmap(20, 20)
            pixmap.fill(color)
            drag.setDragCursor(pixmap, Qt.CopyAction)
            drag.start()
        super(newButton_base_class, self).mousePressEvent(event)


class ColorPickButton(QPushButton):
    colorChanged = Signal(QColor)

    def __init__(self, mimeTypeString = '', parent = None):
        QPushButton.__init__(self, parent)
        self.setAcceptDrops(True)
        self.__pressed = False
        self.__blockDrag = False
        self.__mimeTypeString = mimeTypeString

    @property
    def blockDrag(self):
        return self.__blockDrag

    @blockDrag.setter
    def blockDrag(self, block):
        self.__blockDrag = block

    def color(self):
        palette = self.palette()
        return palette.color(QPalette.Button)

    def setColor(self, color):
        _c = self.color()
        if _c != color:
            palette = self.palette()
            palette.setColor(QPalette.Button, color)
            self.setPalette(palette)
            self.colorChanged.emit(color)

    def mousePressEvent(self, event):
        if not self.__blockDrag:
            self.__pressed = True
        QPushButton.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.__pressed:
            drag = QDrag(self)
            data = QMimeData()
            data.setData(self.__mimeTypeString, 'color')
            data.setColorData(self.color())
            drag.setMimeData(data)
            pixmap = QPixmap(18, 18)
            pixmap.fill(self.color())
            drag.setDragCursor(pixmap, Qt.CopyAction)
            drag.start()
            self.__pressed = False
            if self.isDown():
                self.setDown(False)
        QPushButton.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.__pressed = False
        QPushButton.mouseReleaseEvent(self, event)

    def childEvent(self, event):
        if event.type() == QEvent.ChildRemoved:
            self.__pressed = False
            if self.isDown():
                self.setDown(False)
        QPushButton.childEvent(self, event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(self.__mimeTypeString):
            event.accept()
        QPushButton.dragEnterEvent(self, event)

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasFormat(self.__mimeTypeString):
            pos = event.pos()
            mouseEvent = QMouseEvent(QEvent.MouseButtonRelease, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
            QPushButton.mouseReleaseEvent(self, mouseEvent)
            if self.isDown():
                self.setDown(False)
        else:
            QPushButton.dropEvent(self, event)

    def paintEvent(self, event):
        if INMAYA > 2015:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            rect = event.rect()
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.color().darker())
            painter.setOpacity(0.35)
            painter.drawRoundedRect(rect, 2, 2)
            if self.__pressed:
                rect.adjust(1, 1, 0, 0)
            else:
                rect.adjust(0, 0, -1, -1)
            painter.setBrush(self.color())
            painter.setOpacity(1.0)
            painter.drawRoundedRect(rect, 2, 2)
        else:
            QPushButton.paintEvent(self, event)


class ImageDragButton(QPushButton):

    def __init__(self, parent = None):
        QPushButton.__init__(self, parent)
        self.__pressed = False
        self.__path = ''
        self.__pixmap = QPixmap()
        self.setFixedSize(38, 38)

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        self.__path = path

    @property
    def pixmap(self):
        return self.__pixmap

    @pixmap.setter
    def pixmap(self, pm):
        self.__pixmap = pm

    def mousePressEvent(self, event):
        self.__pressed = True
        super(ImageDragButton, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.__pressed and self.__path:
            drag = QDrag(self)
            data = QMimeData()
            data.setData(MIME_IMAGE, QByteArray(str(self.__path)))
            drag.setMimeData(data)
            drag.start()
            self.__pressed = False
        super(ImageDragButton, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.__pressed = False
        super(ImageDragButton, self).mouseReleaseEvent(event)

    def paintEvent(self, event):
        rect = self.rect()
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.black)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(rect)
        if self.pixmap:
            painter.drawPixmap(rect, self.pixmap)
        else:
            drawRect = rect.adjusted(0, 0, 0, 0)
            width, height = drawRect.width(), drawRect.height()
            if width > height:
                drawRect.setWidth(height)
                drawRect.translate((width - height) / 2, 0)
                factor = math.log(height, 2)
            else:
                drawRect.setHeight(width)
                drawRect.translate(0, (height - width) / 2)
                factor = math.log(width, 2)
            if factor <= 5:
                painter.drawPixmap(drawRect, ':/shutter32')
            elif factor <= 7:
                painter.drawPixmap(drawRect, ':/shutter128')
            else:
                painter.drawPixmap(drawRect, ':/shutter512')


imageUiFile = os.path.join(os.path.dirname(__file__), 'resources', 'imageWidget.ui')
image_base_class, image_form_class = loadUiType(imageUiFile)

class ImageWidget(image_base_class, image_form_class):

    def __init__(self, parent = None):
        super(image_base_class, self).__init__(parent)
        self.setupUi(self)
        self.__pixmap = QPixmap()
        self.__recentCaptureDir = ''
        self.replaceImageLabel()
        self.replaceSlider()
        self.loadImagePath_widget.hide()
        self.workType_buttonGrp = QButtonGroup(self)
        self.workType_buttonGrp.addButton(self.snapshot_radioButton, 0)
        self.workType_buttonGrp.addButton(self.loadImage_radioButton, 1)
        self.connectSignals()

    @property
    @returns(unicode)
    def recentCaptureDir(self):
        return self.__recentCaptureDir

    @recentCaptureDir.setter
    @accepts(unicode)
    def recentCaptureDir(self, path):
        if os.path.isdir(path):
            self.__recentCaptureDir = path.replace('\\', '/')

    def clearPath(self):
        self.path_lineEdit.clear()
        self.loadPath_lineEdit.clear()

    def prettifyPath(self):
        path = self.path_lineEdit.text().replace('\\', '/')
        self.path_lineEdit.setText(path)
        if self.workType_buttonGrp.checkedId():
            if not os.path.isfile(path):
                warn('File is not existing', 'Not Exists', self)
        elif not os.path.isdir(os.path.dirname(path)):
            warn('Directory is not existing', 'Not Exists', self)

    def replaceImageLabel(self):
        layout = self.preview_layout
        index = layout.indexOf(self.image_label)
        tooltip = self.image_label.toolTip()
        layout.removeWidget(self.image_label)
        self.image_label.deleteLater()
        self.image_label = ImageRegionWidget(self)
        self.image_label.setFixedSize(20, 20)
        self.image_label.boundaryRect = QRect(1, 1, 18, 18)
        self.image_label.imageRect = QRect(1, 1, 18, 18)
        self.image_label.setToolTip(tooltip)
        layout.insertWidget(index, self.image_label)

    def replaceSlider(self):
        self.xPos_sliderSet = SoftLimitSliderSet(self, False)
        self.xPos_layout.addWidget(self.xPos_sliderSet)
        self.yPos_sliderSet = SoftLimitSliderSet(self, False)
        self.yPos_layout.addWidget(self.yPos_sliderSet)
        self.width_sliderSet = SoftLimitSliderSet(self)
        self.width_layout.addWidget(self.width_sliderSet)
        self.height_sliderSet = SoftLimitSliderSet(self)
        self.height_layout.addWidget(self.height_sliderSet)

    def connectSignals(self):
        self.workType_buttonGrp.buttonClicked[int].connect(lambda x: self.image_label.setAcceptDrops(bool(x)))
        self.xPos_sliderSet.valueChanged.connect(self.image_label.setIconXPos)
        self.yPos_sliderSet.valueChanged.connect(self.image_label.setIconYPos)
        self.width_sliderSet.valueChanged.connect(self.image_label.setIconWidth)
        self.height_sliderSet.valueChanged.connect(self.image_label.setIconHeight)
        self.path_lineEdit.returnPressed.connect(self.prettifyPath)
        self.browse_Button.clicked.connect(self.showPathDialog)
        self.snapshot_Button.clicked.connect(self.snapShot)
        self.editMode_checkBox.toggled.connect(lambda x: setattr(self.image_label, 'editable', x))
        self.image_label.clicked.connect(self.snapShot)
        self.image_label.regionChanged.connect(self.syncToIconSize)
        self.image_label.imageChanged.connect(self.path_lineEdit.setText)
        self.width_sliderSet.maximumChanged.connect(lambda x: self.increaseIconLabelSize(x, 'width'))
        self.height_sliderSet.maximumChanged.connect(lambda x: self.increaseIconLabelSize(x, 'height'))

    def setIconLabelSize(self, size, iconRect = QRect()):
        self.image_label.setFixedSize(size)
        if iconRect.isValid():
            self.image_label.boundaryRect = iconRect
            self.image_label.imageRect = iconRect

    def increaseIconLabelSize(self, value, axis):
        if axis == 'width':
            width = self.image_label.width()
            self.image_label.setFixedWidth(width + value)
            self.image_label.boundaryRect = self.image_label.boundaryRect.adjusted(0, 0, value, 0)
        elif axis == 'height':
            height = self.image_label.height()
            self.image_label.setFixedHeight(height + value)
            self.image_label.boundaryRect = self.image_label.boundaryRect.adjusted(0, 0, 0, value)

    def syncToIconSize(self, rect):
        bound = self.image_label.boundaryRect
        self.xPos_sliderSet.setMaximum(bound.width() - rect.width())
        self.yPos_sliderSet.setMaximum(bound.height() - rect.height())
        self.width_sliderSet.setMaximum(bound.width() - rect.left() + bound.left())
        self.height_sliderSet.setMaximum(bound.height() - rect.top() + bound.top())
        self.xPos_sliderSet.setValue(rect.left() - bound.left())
        self.yPos_sliderSet.setValue(rect.top() - bound.top())
        self.width_sliderSet.setValue(rect.width())
        self.height_sliderSet.setValue(rect.height())

    def showImageOpenDialog(self):
        from dialog import OpenFileDialog
        p = self.path_lineEdit.text()
        dirPath = os.path.isfile(p) and os.path.dirname(p) or os.path.dirname(__file__)
        path = OpenFileDialog('Open image file', dirPath, IMAGE_FILE_FILTER, IMAGE_FILE_FILTER.split(';;')[1], self)
        if path:
            self.path_lineEdit.setText(path)
            self.loadImage(path)

    def loadImage(self, path):
        if not os.path.isfile(path):
            return warn('File is not existing', 'Not Exists', self)
        ext = os.path.splitext(path)[-1].lower()
        if ext != '.jpg' and ext != '.png':
            return warn('Have to input image file', 'Type Error', self)
        self.image_label.imagePath = path.replace('\\', '/')

    def setPixmap(self, pixmap):
        path = self.path_lineEdit.text()
        self.__pixmap = pixmap
        originalWidth, originalHeight = self.__pixmap.width() * 1.0, self.__pixmap.height() * 1.0
        targetWidth, targetHeight = self.width_sliderSet.value() * 1.0, self.height_sliderSet.value() * 1.0
        originalRatio = originalWidth / originalHeight
        targetRatio = targetWidth / targetHeight
        if originalRatio > targetRatio:
            pixmap = self.__pixmap.scaledToHeight(targetHeight, Qt.SmoothTransformation)
            cropOffset = (pixmap.width() - targetWidth) / 2
            pixmap = pixmap.copy(cropOffset, 0, pixmap.width() - 2 * cropOffset, pixmap.height())
        else:
            pixmap = self.__pixmap.scaledToWidth(targetWidth, Qt.SmoothTransformation)
            cropOffset = (pixmap.height() - targetHeight) / 2
            pixmap = pixmap.copy(0, cropOffset, pixmap.width(), pixmap.height() - 2 * cropOffset)
        pixmap.save(path)
        self.image_label.imagePath = path

    def showPathDialog(self):
        if self.workType_buttonGrp.checkedId():
            self.showImageOpenDialog()
        else:
            self.showImageSaveDialog()

    def showImageSaveDialog(self):
        dirPath = self.path_lineEdit.text()
        if dirPath:
            if os.path.splitext(os.path.basename(dirPath)):
                dirPath = os.path.dirname(dirPath)
        if not os.path.isdir(dirPath):
            if self.__recentCaptureDir:
                dirPath = self.__recentCaptureDir
            else:
                dirPath = os.path.dirname(__file__)
        from dialog import SaveFileDialog
        path = SaveFileDialog('Set image file', dirPath, IMAGE_FILE_FILTER, IMAGE_FILE_FILTER.split(';;')[1], self)
        if path:
            self.path_lineEdit.setText(path)
            self.recentCaptureDir = os.path.dirname(path)

    def captureView(self, ext):
        modelPanel = mc.getPanel(wf=1)
        if not mc.modelPanel(modelPanel, q=1, ex=1):
            modelPanel = mc.playblast(ae=1)
            modelPanel = modelPanel.split('|')[-1]
        tmpFile = getTempFile(ext[1:])
        mc.refresh(cv=True, fe=ext[1:], fn=tmpFile)
        pixmap = QPixmap(tmpFile)
        os.remove(tmpFile)
        return pixmap
        modelPanel = mc.getPanel(wf=1)
        if not mc.modelPanel(modelPanel, q=1, ex=1):
            modelPanel = mc.playblast(ae=1)
            modelPanel = modelPanel.split('|')[-1]
        view = omui.M3dView()
        omui.M3dView.getM3dViewFromModelPanel(modelPanel, view)
        width = view.portWidth()
        height = view.portHeight()
        image = om.MImage()
        view.refresh()
        if view.getRendererName() == view.kViewport2Renderer:
            image.create(width, height, 4, om.MImage.kFloat)
            view.readColorBuffer(image, True)
            image.convertPixelFormat(om.MImage.kByte)
        else:
            view.readColorBuffer(image, True)
        pixelPtr = image.pixels()
        pA = ctypes.cast(pixelPtr.__long__(), ctypes.POINTER(ctypes.c_char))
        pAstring = ctypes.string_at(pA, width * height * 4)
        im = QImage(pAstring, width, height, QImage.Format_ARGB32).mirrored().rgbSwapped()
        pixmap = QPixmap(im)
        return pixmap

    def snapShot(self):
        if self.workType_buttonGrp.checkedId():
            return
        path = self.path_lineEdit.text().replace('\\', '/')
        if not path:
            return warn('Browse and choose/type in an icon file', parent=self)
        if not os.path.isdir(os.path.dirname(path)):
            return warn('Target directory is not existing', parent=self)
        if os.path.isfile(path) and not question('Override file : ' + os.path.basename(path), 'File Exists', parent=self):
            return
        ext = os.path.splitext(path)[-1].lower()
        if ext != '.jpg' and ext != '.png':
            return warn('Browse and choose/type in an icon file', parent=self)
        self.path_lineEdit.setText(path)
        pixmap = self.captureView(ext)
        self.setPixmap(pixmap)


commandUiFile = os.path.join(os.path.dirname(__file__), 'resources', 'commandWidget.ui')
command_base_class, command_form_class = loadUiType(commandUiFile)

class CommandWidget(command_base_class, command_form_class):

    def __init__(self, parent = None):
        super(command_base_class, self).__init__(parent)
        self.setupUi(self)
        self.customCommand_label.__drag__ = 'Custom'
        self.SPACING = self.customCommand_layout.spacing()
        index = self.verticalLayout.indexOf(self.command_listView)
        self.verticalLayout.removeWidget(self.command_listView)
        self.command_listView.deleteLater()
        self.flowLayout = FlowLayout()
        self.flowLayout.setContentsMargins(2, 2, 2, 2)
        self.flowLayout.setSpacing(2)
        self.verticalLayout.insertLayout(index, self.flowLayout)
        self.script_textEdit = CodeEditor(self)
        self.customCommand_layout.addWidget(self.script_textEdit, 1, 1)
        self.setCustomLabelColor()
        self.addItems()
        self.codeType_buttonGrp = QButtonGroup(self)
        self.codeType_buttonGrp.addButton(self.mel_radioButton, 1)
        self.codeType_buttonGrp.addButton(self.python_radioButton, 2)
        self.codeType_buttonGrp.buttonClicked[int].connect(self.script_textEdit.setMode)
        self.execCode_button.clicked.connect(self.testExecute)

    def mousePressEvent(self, event):
        widget = self.childAt(event.pos())
        if hasattr(widget, '__drag__'):
            self.startDrag(widget.__drag__)
        super(command_base_class, self).mousePressEvent(event)

    def setCustomLabelColor(self):
        palette = self.customCommand_label.palette()
        palette.setColor(QPalette.Window, QColor(242, 242, 242))
        palette.setColor(QPalette.WindowText, QColor(Qt.black))
        self.customCommand_label.setPalette(palette)

    def addItems(self):
        for text, color, toolTip in self.getButtons():
            label = QLabel(text)
            label.setAutoFillBackground(True)
            label.setFixedSize(90, 28)
            label.setAlignment(Qt.AlignCenter)
            label.setToolTip(toolTip)
            label.__drag__ = text
            palette = label.palette()
            palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
            palette.setColor(QPalette.Background, color)
            label.setPalette(palette)
            self.flowLayout.addWidget(label)

    def getButtons(self):
        return (('Select', QColor.fromRgbF(0.98, 0.88, 0.88), 'Change to Select command.'),
         ('Select+Move', QColor.fromRgbF(0.98, 0.88, 0.88), 'Change to Select command and set to Move tool.'),
         ('Select+Rotate', QColor.fromRgbF(0.98, 0.88, 0.88), 'Change to Select command and set to Rotate tool.'),
         ('Select+Scale', QColor.fromRgbF(0.98, 0.88, 0.88), 'Change to Select command and set to Scale tool.'),
         ('Key', QColor.fromRgbF(0.88, 0.98, 0.88), 'Key all keyable attributes.'),
         ('Key Transform', QColor.fromRgbF(0.88, 0.98, 0.88), 'Key transform attributes.'),
         ('Key Selected', QColor.fromRgbF(0.88, 0.98, 0.88), 'Key only selected attributes in the ChannelBox.'),
         ('Toggle', QColor.fromRgbF(0.8, 0.92, 0.99), 'Set a new Toggle with the selected atttributes in the ChannelBox.'),
         ('Reset', QColor.fromRgbF(0.85, 0.88, 0.98), 'Reset all keyable attributes.'),
         ('Reset Transform', QColor.fromRgbF(0.85, 0.88, 0.98), 'Reset transform attributes.'),
         ('Reset Selected', QColor.fromRgbF(0.85, 0.88, 0.98), 'Reset only selected attributes in the ChannelBox.'),
         ('Range', QColor.fromRgbF(0.92, 0.92, 0.6), 'Set a new Range with the selected atttributes in the ChannelBox.'),
         ('Pose', QColor.fromRgbF(0.98, 0.98, 0.88), 'Set a new Pose of the selected nodes.'),
         ('Pose Transform', QColor.fromRgbF(0.98, 0.98, 0.88), 'Set a new Pose with transform attributes of the selected nodes.'),
         ('Pose Selected', QColor.fromRgbF(0.98, 0.98, 0.88), 'Set a new Pose with the selected attributes in the ChannelBox.'),
         ('No Slider', QColor.fromRgbF(0.88, 0.8, 0.98), 'Remove the slider and make it a button.'),
         ('Slider Right', QColor.fromRgbF(0.88, 0.8, 0.98), 'Place a slider to the right side of the button.'),
         ('Slider Left', QColor.fromRgbF(0.88, 0.8, 0.98), 'Place a slider to the left side of the button.'),
         ('Slider Below', QColor.fromRgbF(0.88, 0.8, 0.98), 'Place a slider below the button.'),
         ('Slider Above', QColor.fromRgbF(0.88, 0.8, 0.98), 'Place a slider group above the button.'),
         ('Visibility Toggle', QColor.fromRgbF(0.98, 0.8, 0.8), 'Change to Visibility Toggle Button.'),
         ('Reference Editor', QColor.fromRgbF(0.75, 0.98, 0.8), 'Open ReferenceEditor'),
         ('Outliner', QColor.fromRgbF(0.75, 0.98, 0.8), 'Open Outliner'),
         ('Graph Editor', QColor.fromRgbF(0.75, 0.98, 0.8), 'Open GraphEditor'),
         ('Dope Sheet', QColor.fromRgbF(0.75, 0.98, 0.8), 'Open DopeSheet'))

    def startDrag(self, command):
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setData(MIME_COMMAND, QByteArray(str(command)))
        if self.keepObjectName_checkBox.isChecked():
            mimeData.setData('ToolDialog/Command-KeepObjectName', QByteArray.number(1))
        if command == 'Custom':
            customCommand = self.script_textEdit.toPlainText().replace('    ', '\t')
            if not customCommand:
                return
            try:
                if self.python_radioButton.isChecked():
                    customCommand = customCommand.replace('"', "'")
                    customCommand = 'python("' + str(customCommand).encode('string_escape') + '")'
                else:
                    customCommand = re.sub('[\t\n\r\x0c\x0b]', '', customCommand)
                customCommand = str(customCommand)
            except:
                print ' >> Sorry, non-ascii characters are not supported yet.'
                return

            mimeData.setData('ToolDialog/Command-Script', QByteArray(customCommand))
        drag.setMimeData(mimeData)
        drag.start()

    def testExecute(self):
        customCommand = self.script_textEdit.toPlainText().replace('    ', '\t')
        if not customCommand:
            return
        print 'EXECUTE TYPE:', self.python_radioButton.isChecked() and 'Python' or 'MEL'
        print '--------------------------------'
        print customCommand
        print '--------------------------------'
        try:
            if self.python_radioButton.isChecked():
                customCommand = customCommand.replace('"', "'")
                customCommand = 'python("' + str(customCommand).encode('string_escape') + '")'
            else:
                customCommand = re.sub('[\t\n\r\x0c\x0b]', '', customCommand)
            customCommand = str(customCommand)
        except:
            print ' >> Sorry, non-ascii characters are not supported yet.'
            return

        mm.eval(customCommand)

    def clearCommand(self):
        self.script_textEdit.clear()


labelUiFile = os.path.join(os.path.dirname(__file__), 'resources', 'labelEditWidget.ui')
label_base_class, label_form_class = loadUiType(labelUiFile)

class LabelWidget(label_base_class, label_form_class):

    def __init__(self, parent = None):
        super(label_base_class, self).__init__(parent)
        self.setupUi(self)
        self.customLabel_label.__labelDrag__ = True
        self.font_label.__fontDrag__ = True
        self.SPACING = self.customLabel_layout.spacing()
        index = self.verticalLayout.indexOf(self.prefixLabel_listView)
        self.verticalLayout.removeWidget(self.prefixLabel_listView)
        self.prefixLabel_listView.deleteLater()
        self.flowLayout = FlowLayout()
        self.flowLayout.setContentsMargins(2, 2, 2, 0)
        self.flowLayout.setSpacing(2)
        self.verticalLayout.insertLayout(index, self.flowLayout)
        self.setCustomLabelColor()
        self.addItems()
        self.bold_Button.toggled.connect(self.changeFontBold)
        self.italic_Button.toggled.connect(self.changeFontItalic)
        self.fontSize_spinBox.valueChanged.connect(self.changeFontSize)
        self.fontFamily_comboBox.currentFontChanged.connect(self.changeFontFamily)

    def mousePressEvent(self, event):
        widget = self.childAt(event.pos())
        if hasattr(widget, '__fontDrag__'):
            drag = QDrag(self)
            font = widget.font()
            mimeData = QMimeData()
            family = font.family()
            if family in FONT_FAMILIES:
                family_id = FONT_FAMILIES.index(family)
            else:
                family_id = 0
            size = font.pointSize()
            bold = font.bold() and 1 or 0
            italic = font.italic() and 1 or 0
            mimeData.setData(MIME_FONT_FAMILY, QByteArray.number(family_id))
            mimeData.setData(MIME_FONT_SIZE, QByteArray.number(size))
            mimeData.setData(MIME_FONT_BOLD, QByteArray.number(bold))
            mimeData.setData(MIME_FONT_ITALIC, QByteArray.number(italic))
            drag.setMimeData(mimeData)
            drag.start()
        elif hasattr(widget, '__labelDrag__'):
            drag = QDrag(self)
            label = self.customLabel_lineEdit.text()
            try:
                str(label)
            except:
                print ' >> Sorry, non-ascii characters are not supported yet.'
                return

            mimeData = QMimeData()
            mimeData.setData(MIME_CUSTOM_LABEL, QByteArray(str(label)))
            drag.setMimeData(mimeData)
            drag.start()
        elif hasattr(widget, '__label__'):
            self.startDrag(widget.__label__)
        super(label_base_class, self).mousePressEvent(event)

    def changeFontBold(self, bold):
        font = self.font_label.font()
        font.setBold(bold)
        self.font_label.setFont(font)

    def changeFontItalic(self, italic):
        font = self.font_label.font()
        font.setItalic(italic)
        self.font_label.setFont(font)

    def changeFontSize(self, pointSize):
        font = self.font_label.font()
        font.setPointSize(pointSize)
        self.font_label.setFont(font)

    def changeFontFamily(self, font):
        font.setPointSize(self.fontSize_spinBox.value())
        self.font_label.setFont(font)

    def setCustomLabelColor(self):
        palette = self.customLabel_label.palette()
        palette.setColor(QPalette.Window, QColor(242, 242, 242))
        palette.setColor(QPalette.WindowText, QColor(Qt.black))
        self.customLabel_label.setPalette(palette)
        self.font_label.setPalette(palette)

    def addItems(self):
        from const import CHANGE_LABEL_TIP, REMOVE_LABEL_TIP
        for text, color in self.getButtons():
            label = QLabel(text)
            label.setAutoFillBackground(True)
            label.setFixedSize(90, 28)
            label.setAlignment(Qt.AlignCenter)
            label.__label__ = text
            if text:
                label.setToolTip(CHANGE_LABEL_TIP)
            else:
                label.setToolTip(REMOVE_LABEL_TIP)
            palette = label.palette()
            palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
            palette.setColor(QPalette.Background, color)
            label.setPalette(palette)
            self.flowLayout.addWidget(label)

    def getButtons(self):
        return (('Select All', QColor.fromRgbF(0.88, 0.98, 0.88)),
         ('Key All', QColor.fromRgbF(0.88, 0.98, 0.88)),
         ('Key Trans', QColor.fromRgbF(0.88, 0.98, 0.88)),
         ('Key', QColor.fromRgbF(0.88, 0.98, 0.88)),
         ('Reset Trans', QColor.fromRgbF(0.88, 0.98, 0.88)),
         ('Reset', QColor.fromRgbF(0.88, 0.98, 0.88)),
         ('Toggle', QColor.fromRgbF(0.88, 0.98, 0.88)),
         ('Pose', QColor.fromRgbF(0.88, 0.98, 0.88)),
         ('Reference Editor', QColor.fromRgbF(0.98, 0.98, 0.88)),
         ('Outliner', QColor.fromRgbF(0.98, 0.98, 0.88)),
         ('Graph Editor', QColor.fromRgbF(0.98, 0.98, 0.88)),
         ('Dope Sheet', QColor.fromRgbF(0.98, 0.98, 0.88)),
         ('Group', QColor.fromRgbF(0.88, 0.98, 0.98)),
         ('', QColor.fromRgbF(0.95, 0.95, 0.95)))

    def startDrag(self, label):
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setData(MIME_LABEL, QByteArray(str(label)))
        drag.setMimeData(mimeData)
        drag.start()


class FlowLayout(QLayout):

    def __init__(self, margin = -1, hSpacing = -1, vSpacing = -1, parent = None):
        super(FlowLayout, self).__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.__hSpace = hSpacing
        self.__vSpace = vSpacing
        self.__itemList = []
        return

    def __del__(self):
        while self.count():
            self.takeAt(0)

    def addItem(self, item):
        self.__itemList.append(item)

    def horizontalSpacing(self):
        if self.__hSpace >= 0:
            return self.__hSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutHorizontalSpacing)

    def setHorizontalSpacing(self, spacing):
        if isinstance(spacing, int) and spacing >= -1:
            self.__hSpace = spacing

    def verticalSpacing(self):
        if self.__vSpace >= 0:
            return self.__vSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutVerticalSpacing)

    def setVerticalSpacing(self, spacing):
        if isinstance(spacing, int) and spacing >= -1:
            self.__vSpace = spacing

    def setSpacing(self, spacing):
        if isinstance(spacing, int) and spacing >= -1:
            self.setHorizontalSpacing(spacing)
            self.setVerticalSpacing(spacing)

    def count(self):
        return len(self.__itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.__itemList):
            return self.__itemList[index]
        else:
            return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.__itemList):
            item = self.__itemList[index]
            del self.__itemList[index]
            return item
        else:
            return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        QLayout.setGeometry(self, rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.__itemList:
            size = size.expandedTo(item.minimumSize())

        size += QSize(2 * self.margin(), 2 * self.margin())
        return size

    def doLayout(self, rect, testOnly):
        left, top, right, bottom = self.getContentsMargins()
        effectiveRect = rect.adjusted(left, top, -right, -bottom)
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0
        for item in self.__itemList:
            w = item.widget()
            spaceX = self.horizontalSpacing()
            if spaceX == -1:
                spaceX = w.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = self.verticalSpacing()
            if spaceY == -1:
                spaceY = w.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > effectiveRect.right() and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y() + bottom

    def smartSpacing(self, pm):
        parent = self.parent()
        if not parent:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()
            return None


uiFile = os.path.join(os.path.dirname(__file__), 'resources', 'toolsDialog.ui')
base_class, form_class = loadUiType(uiFile)

class ToolsDialog(base_class, form_class):
    colorPick = Signal(QWidget)
    mirrorButtons = Signal(unicode, unicode, bool)

    def __init__(self, parent = None):
        super(base_class, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.__moveWindow = False
        self.snapRegion = ''
        self.clickedAttrOpt = 0
        self.__recentDirs = []
        self.dispatcher = ThreadDispatcher(self)
        self.dispatcher.start()
        self.setColorPalette()
        self.makeTabs()
        self.connectSignals()
        self.restoreIniSettings()
        self.setTemplatePath()
        self.setProperty('__opacity__', 0.0)
        self.animation = QPropertyAnimation(self, '__opacity__')
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.valueChanged.connect(self.setCustomTemplateListOpacity)

    def customEvent(self, event):
        event.callback()

    def closeEvent(self, event):
        self.__colorPalette.close()
        for i in xrange(self.tabWidget.count()):
            self.tabWidget.setTabEnabled(i, True)

        self.saveIniSettings()
        self.dispatcher.stop()

    def getEnvPath(self):
        if INMAYA:
            return os.path.join(mc.internalVar(upd=1), 'locusPicker.ini')
        else:
            return os.path.join(os.path.dirname(sys.modules[self.__module__].__file__), '__setting.ini')

    def saveIniSettings(self):
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('ToolDialog')
        settings.setValue('Position', self.pos())
        settings.setValue('Size', self.size())
        settings.setValue('TabIndex', self.tabWidget.currentIndex())
        settings.beginGroup('Template')
        settings.setValue('IconSize', self.templateIconSize().width())
        settings.setValue('CustomTemplateDirectory', self.__recentDirs)
        settings.endGroup()
        settings.beginGroup('Modify')
        settings.setValue('ChangeColor', self.changeMirroredColor_checkBox.isChecked())
        settings.endGroup()
        settings.beginGroup('Color')
        settings.setValue('ColorButton', self.customColor_button.color())
        settings.endGroup()
        settings.beginGroup('Image')
        settings.setValue('WorkType', self.image_scrollContentWidget.workType_buttonGrp.checkedId() and 'LoadImage' or 'Snapshot')
        settings.setValue('IconLabelSize', self.image_scrollContentWidget.image_label.size())
        settings.setValue('BoundX', self.image_scrollContentWidget.image_label.boundaryRect.left())
        settings.setValue('BoundY', self.image_scrollContentWidget.image_label.boundaryRect.top())
        settings.setValue('IconXPos', self.image_scrollContentWidget.xPos_sliderSet.value())
        settings.setValue('IconYPos', self.image_scrollContentWidget.yPos_sliderSet.value())
        settings.setValue('IconWidth', self.image_scrollContentWidget.width_sliderSet.value())
        settings.setValue('IconHeight', self.image_scrollContentWidget.height_sliderSet.value())
        settings.setValue('RecentCaptureDirectory', self.image_scrollContentWidget.recentCaptureDir)
        settings.endGroup()
        settings.beginGroup('Command')
        settings.setValue('KeepObject', self.command_scrollContentWidget.keepObjectName_checkBox.isChecked())
        settings.endGroup()
        settings.beginGroup('Slider')
        settings.setValue('Command', self.command_buttonGrp.checkedId())
        settings.setValue('Width', self.sliderWidth_spinBox.value())
        settings.setValue('Height', self.sliderHeight_spinBox.value())
        settings.setValue('Color', self.sliderColor_button.color())
        settings.setValue('Attach', Attachment.getString(self.sliderAttach_buttonGrp.checkedId()))
        settings.setValue('HorizontalReversed', bool(self.horizontalDirection_buttonGrp.checkedId()))
        settings.setValue('VerticalReversed', bool(self.verticalDirection_buttonGrp.checkedId()))
        settings.setValue('ChangeTool', self.changeTool_buttonGroup.checkedId())
        settings.setValue('NumberOfButtons', self.numberOfButton_buttonGroup.checkedId())
        settings.setValue('AttributeOption', self.attributeOption_buttonGroup.checkedId())
        settings.endGroup()
        settings.endGroup()

    def restoreIniSettings(self):
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('ToolDialog')
        value = settings.value('Position')
        if value is not None:
            self.move(value)
        value = settings.value('TabIndex')
        if value is not None:
            self.tabWidget.setCurrentIndex(int(value))
        settings.beginGroup('Template')
        value = settings.value('IconSize')
        if value is not None:
            self.setTemplateIconSize(QSize(int(value), int(value)))
        value = settings.value('CustomTemplateDirectory')
        if value is not None:
            if type(value) == unicode:
                value = [value]
            self.__recentDirs = value
        settings.endGroup()
        settings.beginGroup('Modify')
        value = settings.value('ChangeColor')
        if value is not None:
            self.changeMirroredColor_checkBox.setChecked(value == 'true' and True or False)
        settings.endGroup()
        settings.beginGroup('Color')
        value = settings.value('ColorButton')
        if value is not None:
            self.customColor_button.setColor(value)
        settings.endGroup()
        settings.beginGroup('Image')
        value = settings.value('WorkType')
        if value is not None:
            value = value == 'LoadImage' and 1 or 0
            self.image_scrollContentWidget.workType_buttonGrp.button(value).setChecked(True)
            self.image_scrollContentWidget.image_label.setAcceptDrops(bool(value))
        iconLabelSize = settings.value('IconLabelSize')
        boundX = settings.value('BoundX')
        boundY = settings.value('BoundY')
        if iconLabelSize and boundX and boundY:
            rect = QRect(QPoint(0, 0), iconLabelSize).adjusted(1, 1, -1, -1)
            rect.setTopLeft(QPoint(int(boundX), int(boundY)))
            self.image_scrollContentWidget.setIconLabelSize(iconLabelSize, rect)
            xPos = settings.value('IconXPos')
            yPos = settings.value('IconYPos')
            width = settings.value('IconWidth')
            height = settings.value('IconHeight')
            if xPos and yPos and width and height:
                iconRect = rect.adjusted(int(xPos), int(yPos), 0, 0)
                iconRect.setWidth(int(width))
                iconRect.setHeight(int(height))
                self.image_scrollContentWidget.image_label.imageRect = iconRect
        value = settings.value('RecentCaptureDirectory')
        if value is not None:
            self.image_scrollContentWidget.recentCaptureDir = value
        settings.endGroup()
        settings.beginGroup('Command')
        value = settings.value('KeepObject')
        if value is not None:
            self.command_scrollContentWidget.keepObjectName_checkBox.setChecked(value == 'true' and True or False)
        settings.endGroup()
        settings.beginGroup('Slider')
        value = settings.value('Color')
        if value is not None:
            self.sliderColor_button.setColor(value)
        value = settings.value('HorizontalReversed')
        if value is not None:
            self.horizontalDirection_buttonGrp.button(value == 'true' and 1 or 0).setChecked(True)
        value = settings.value('VerticalReversed')
        if value is not None:
            self.verticalDirection_buttonGrp.button(value == 'true' and 1 or 0).setChecked(True)
        value = settings.value('Attach')
        if value is not None:
            self.sliderAttach_buttonGrp.button(Attachment.getAttachment(value)).setChecked(True)
        value = settings.value('ChangeTool')
        if value is not None:
            self.changeTool_buttonGroup.button(int(value)).setChecked(True)
            self.sliderPreview_widget.changeTool = self.changeTool_buttonGroup.button(int(value)).text()
        value = settings.value('NumberOfButtons')
        if value is not None:
            self.numberOfButton_buttonGroup.button(int(value)).setChecked(True)
            self.sliderPreview_widget.numberOfButtons = self.numberOfButton_buttonGroup.button(int(value)).text()
        value = settings.value('AttributeOption')
        if value is not None:
            self.attributeOption_buttonGroup.button(int(value)).setChecked(True)
            self.sliderPreview_widget.attributeOption = self.attributeOption_buttonGroup.button(int(value)).text()
        value = settings.value('Command')
        if value is not None:
            self.command_buttonGrp.button(int(value)).setChecked(True)
            self.changeSliderTabUI(int(value))
        value = settings.value('Width')
        if value is not None:
            self.sliderWidth_spinBox.setValue(int(value))
        value = settings.value('Height')
        if value is not None:
            self.sliderHeight_spinBox.setValue(int(value))
        settings.endGroup()
        return

    def eventFilter(self, widget, event):
        if widget == self.customTemplate_listWidget:
            eventType = event.type()
            if eventType == QEvent.MouseButtonPress:
                globalPos = event.globalPos()
                if not widget.geometry().contains(globalPos):
                    pos = self.templateDir_lineEdit.mapFromGlobal(globalPos)
                    if self.templateDir_lineEdit.rect().contains(pos):
                        event.ignore()
                        return False
                    self.showCustomTemplateDialog(False)
                    event.ignore()
                    return True
            elif eventType == QEvent.KeyPress and event.key() == Qt.Key_Escape:
                self.showCustomTemplateDialog(False)
                event.ignore()
                return True
        return super(base_class, self).eventFilter(widget, event)

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

    def makeTabs(self):
        self.makeTemplateTab()
        self.makeMapGeoTab()
        self.makeColorTab()
        self.makeImageTab()
        self.makeCommandTab()
        self.makeLabelTab()
        self.makeSliderButtonTab()

    def makeTemplateTab(self):
        self.template_listView = TemplateListView(self)
        self.template_model = QStandardItemModel(self.template_listView)
        self.template_listView.setModel(self.template_model)
        self.template_listView.setItemDelegate(TemplateDelegate(self.template_listView))
        self.template_Layout.addWidget(self.template_listView)
        self.customTemplate_listWidget = TemplateDirListWidget(self)
        self.customTemplate_listWidget.installEventFilter(self)
        self.templateDir_lineEdit = self.replaceWidget(self.templateDirPath_layout, self.templateDir_lineEdit, PressSendLineEdit)
        self.templateDir_button.hide()
        self.addTemplateDir_button.hide()
        self.addTemplateSVGFile_button.hide()
        self.messageLabel = AnimatedLabel('120 px', self.template_listView)

    def makeNewButtonTab(self):
        self.newButton_scrollContentWidget = NewButtonWidget(self)
        self.newButton_scrollArea.setWidget(self.newButton_scrollContentWidget)

    def makeSliderButtonTab(self):
        self.command_buttonGrp = QButtonGroup(self)
        self.command_buttonGrp.addButton(self.select_radioButton, 0)
        self.command_buttonGrp.addButton(self.key_radioButton, 1)
        self.command_buttonGrp.addButton(self.reset_radioButton, 2)
        self.command_buttonGrp.addButton(self.toggle_radioButton, 3)
        self.command_buttonGrp.addButton(self.pose_radioButton, 4)
        self.command_buttonGrp.addButton(self.range_radioButton, 5)
        self.sliderAttach_buttonGrp = QButtonGroup(self)
        self.sliderAttach_buttonGrp.addButton(self.attachToTop_radioButton, Attachment.TOP)
        self.sliderAttach_buttonGrp.addButton(self.attachToBottom_radioButton, Attachment.BOTTOM)
        self.sliderAttach_buttonGrp.addButton(self.attachToLeft_radioButton, Attachment.LEFT)
        self.sliderAttach_buttonGrp.addButton(self.attachToRight_radioButton, Attachment.RIGHT)
        self.sliderAttach_buttonGrp.addButton(self.attachNo_radioButton, Attachment.NotValid)
        self.attachToBottom_radioButton.setChecked(True)
        self.verticalDirection_buttonGrp = QButtonGroup(self)
        self.verticalDirection_buttonGrp.addButton(self.zeroToBottom_radioButton, 0)
        self.verticalDirection_buttonGrp.addButton(self.topToZero_radioButton, 1)
        self.horizontalDirection_buttonGrp = QButtonGroup(self)
        self.horizontalDirection_buttonGrp.addButton(self.zeroToRight_radioButton, 0)
        self.horizontalDirection_buttonGrp.addButton(self.leftToZero_radioButton, 1)
        self.verticalSliderDirection_widget.hide()
        self.changeTool_buttonGroup = QButtonGroup(self)
        self.changeTool_buttonGroup.addButton(self.noChange_radioButton, 0)
        self.changeTool_buttonGroup.addButton(self.moveTool_radioButton, 1)
        self.changeTool_buttonGroup.addButton(self.rotateTool_radioButton, 2)
        self.changeTool_buttonGroup.addButton(self.scaleTool_radioButton, 3)
        self.numberOfButton_buttonGroup = QButtonGroup(self)
        self.numberOfButton_buttonGroup.addButton(self.one_radioButton, 0)
        self.numberOfButton_buttonGroup.addButton(self.multiHorizontal_radioButton, 1)
        self.numberOfButton_buttonGroup.addButton(self.multiVertical_radioButton, 2)
        self.numberOfButton_buttonGroup.addButton(self.capture_radioButton, 3)
        self.attributeOption_buttonGroup = QButtonGroup(self)
        self.attributeOption_buttonGroup.addButton(self.allKeyable_radioButton, 0)
        self.attributeOption_buttonGroup.addButton(self.transformOnly_radioButton, 1)
        self.attributeOption_buttonGroup.addButton(self.selectedOnly_radioButton, 2)
        self.sliderPreview_widget = self.replaceWidget(self.sliderPreview_layout, self.sliderPreview_widget, SliderItemPreviewWidget)
        self.sliderColor_button = self.replaceWidget(self.sliderColor_layout, self.sliderColor_button, ColorPickButton, ['ToolDialog/SliderColor'])
        self.sliderColor_button.blockDrag = True
        self.sliderColor_button.setColor(Qt.red)
        self.sliderPreview_widget.changeToolWidget = self.changeTool_widget
        self.sliderPreview_widget.attributeOptionWidget = self.attributeOption_widget
        self.sliderPreview_widget.numberOfButtonsWidget = self.numberOfButtons_widget
        self.sliderPreview_widget.sliderAttachWidget = self.sliderAttach_widget

    def makeColorTab(self):
        self.colorWidget = ColorPaletteWidget(self)
        self.color_scrollContentWidget.layout().insertWidget(0, self.colorWidget)
        size = self.customColor_button.size()
        self.customColor_button = self.replaceWidget(self.customColor_Layout, self.customColor_button, ColorPickButton, [MIME_COLOR])
        self.customColor_button.setFixedSize(size)
        self.customColor_button.setColor(Qt.red)

    def makeImageTab(self):
        self.image_scrollContentWidget = ImageWidget(self)
        self.image_scrollArea.setWidget(self.image_scrollContentWidget)

    def makeCommandTab(self):
        self.command_scrollContentWidget = CommandWidget(self)
        self.command_scrollArea.setWidget(self.command_scrollContentWidget)

    def makeLabelTab(self):
        self.label_scrollContentWidget = LabelWidget(self)
        self.label_scrollArea.setWidget(self.label_scrollContentWidget)

    def makeMapGeoTab(self):
        for widget in [self.label_2,
         self.mapToGeo_Button,
         self.geoToMap_Button,
         self.deleteAll_Button,
         self.line]:
            widget.hide()

        from const import setButtonColor, getDefaultColor
        setButtonColor(self.mapToGeo_Button, 0.5, 0.7, 0.6)
        setButtonColor(self.geoToMap_Button, 0.7, 0.7, 0.5)
        setButtonColor(self.deleteAll_Button, *getDefaultColor('OK').getRgbF()[:3])
        self.fromTo_Button.leftToRight = True

    def connectSignals(self):
        self.tabWidget.currentChanged.connect(self.wrapUpTab)
        self.connectTemplateTabSignals()
        self.connectMapGeoTabSignals()
        self.connectColorTabSignals()
        self.connectImageTabSignals()
        self.connectCommandTabSignals()
        self.connectSliderTabSignals()
        self.mirror_Button.clicked.connect(self.sendmirrorButtons)

    def connectTemplateTabSignals(self):
        self.template_listView.AddTemplateDir.connect(self.addTemplateDir)
        self.templateDir_lineEdit.pressed.connect(self.showCustomTemplateDialog)
        self.templateDirBrowse_Button.clicked.connect(self.browseTemplateDir)
        self.zoomIn_Button.clicked.connect(lambda : self.setTemplateIconSize(self.templateIconSize() + QSize(10, 10)))
        self.zoomOut_Button.clicked.connect(lambda : self.setTemplateIconSize(self.templateIconSize() - QSize(10, 10)))
        self.templateDir_lineEdit.textChanged.connect(self.loadTemplate)
        self.customTemplate_listWidget.itemClicked.connect(self.selectRecentDir)
        self.customTemplate_listWidget.itemRemoved.connect(self.popRecentDir)

    def connectNewButtonTabSignals(self):
        pass

    def connectMapGeoTabSignals(self):
        self.fromTo_Button.clicked.connect(self.toggleFromToButton)

    def connectColorTabSignals(self):
        self.customColor_button.clicked.connect(lambda : self.colorPick.emit(self.customColor_button))

    def connectImageTabSignals(self):
        self.image_scrollContentWidget.loadIconSize_Button.clicked.connect(lambda : self.getAvailableIconSize(False))
        self.image_scrollContentWidget.loadMapSize_Button.clicked.connect(lambda : self.getAvailableIconSize(True))

    def connectCommandTabSignals(self):
        self.command_scrollContentWidget.pickCode_button.clicked.connect(self.getScriptFromSelected)

    def connectLabelTabSignals(self):
        pass

    def connectSliderTabSignals(self):
        self.command_buttonGrp.buttonClicked[int].connect(self.changeSliderTabUI)
        self.sliderWidth_spinBox.valueChanged.connect(lambda x: self.sliderPreview_widget.setFixedWidth(x))
        self.sliderHeight_spinBox.valueChanged.connect(lambda x: self.sliderPreview_widget.setFixedHeight(x))
        self.sliderColor_button.clicked.connect(lambda : self.colorPick.emit(self.sliderColor_button))
        self.sliderColor_button.colorChanged.connect(lambda x: setattr(self.sliderPreview_widget, 'color', x))
        self.showPalette_Button.clicked.connect(lambda : self.showColorPalette(self.sliderColor_button))
        self.sliderAttach_buttonGrp.buttonClicked[int].connect(self.toggleSliderDirectionWidget)
        self.sliderAttach_buttonGrp.buttonClicked[int].connect(self.setSliderAttachment)
        self.verticalDirection_buttonGrp.buttonClicked[int].connect(self.setSliderAppearance)
        self.horizontalDirection_buttonGrp.buttonClicked[int].connect(self.setSliderAppearance)
        self.changeTool_buttonGroup.buttonClicked.connect(lambda x: setattr(self.sliderPreview_widget, 'changeTool', x.text()))
        self.attributeOption_buttonGroup.buttonClicked.connect(lambda x: setattr(self.sliderPreview_widget, 'attributeOption', x.text()))
        self.attributeOption_buttonGroup.buttonClicked[int].connect(lambda x: setattr(self, 'clickedAttrOpt', x))
        self.numberOfButton_buttonGroup.buttonClicked.connect(lambda x: setattr(self.sliderPreview_widget, 'numberOfButtons', x.text()))

    def disguiseButton(self):
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Control, Qt.ControlModifier)
        QApplication.postEvent(self.sliderColor_button, event)
        self.sliderColor_button.clicked.emit()

    def sendmirrorButtons(self):
        self.mirrorButtons.emit(*(self.getReplaceString() + (self.changeMirroredColor_checkBox.isChecked(),)))

    def changeSliderTabUI(self, index):
        self.sliderPreview_widget.command = self.command_buttonGrp.button(index).text()
        if index == 0:
            self.changeTool_widget.show()
            self.sliderAttach_widget.hide()
            self.sliderDirection_widget.hide()
            self.attributeOption_widget.hide()
            self.numberOfButtons_widget.show()
            self.toggleSliderDirectionWidget(0)
            self.setSliderAttachment(0)
        elif index in (1, 2, 3):
            self.changeTool_widget.hide()
            self.sliderAttach_widget.hide()
            self.sliderDirection_widget.hide()
            self.attributeOption_widget.show()
            self.numberOfButtons_widget.hide()
            if index == 3:
                self.attributeOption_widget.setDisabled(True)
                self.selectedOnly_radioButton.setChecked(True)
            else:
                self.attributeOption_widget.setEnabled(True)
                self.attributeOption_buttonGroup.button(self.clickedAttrOpt).setChecked(True)
            self.toggleSliderDirectionWidget(0)
            self.setSliderAttachment(0)
        elif index == 4:
            self.changeTool_widget.hide()
            self.sliderAttach_widget.show()
            self.sliderDirection_widget.show()
            self.attributeOption_widget.show()
            self.attributeOption_widget.setEnabled(True)
            self.numberOfButtons_widget.hide()
            self.sliderPreview_widget.min = 0
            self.toggleSliderDirectionWidget(self.sliderAttach_buttonGrp.checkedId())
            self.setSliderAttachment(self.sliderAttach_buttonGrp.checkedId())
            self.attributeOption_buttonGroup.button(self.clickedAttrOpt).setChecked(True)
        elif index == 5:
            self.changeTool_widget.hide()
            self.sliderAttach_widget.show()
            self.sliderDirection_widget.show()
            self.attributeOption_widget.show()
            self.attributeOption_widget.setDisabled(True)
            self.numberOfButtons_widget.hide()
            self.sliderPreview_widget.min = -1
            self.toggleSliderDirectionWidget(self.sliderAttach_buttonGrp.checkedId())
            self.setSliderAttachment(self.sliderAttach_buttonGrp.checkedId())
            self.selectedOnly_radioButton.setChecked(True)

    def toggleFromToButton(self):
        self.fromTo_Button.leftToRight = not self.fromTo_Button.leftToRight
        if self.fromTo_Button.leftToRight:
            self.fromTo_Button.setText('>>')
        else:
            self.fromTo_Button.setText('<<')

    @staticmethod
    def generateSvg(svgFile):
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
                continue
            boundingRect = boundingRect.united(svgPath.boundingRect())
            drawSet.append([style, svgPath])

        for bundle in drawSet:
            path = bundle[-1]
            del bundle[-1]
            offset = path.boundingRect().topLeft() - boundingRect.topLeft()
            path.translate(path.boundingRect().topLeft() * -1)
            path.translate(offset)
            bundle.append(path)

        return (boundingRect, drawSet)

    def setTemplatePath(self):
        if not self.__recentDirs:
            self.__recentDirs.append(os.path.join(os.path.dirname(__file__), 'templates').replace('\\', '/'))
        self.templateDir_lineEdit.setText(self.__recentDirs[0].replace('\\', '/'))

    def browseTemplateDir(self):
        from dialog import SelectDirectoryDialog
        directory = SelectDirectoryDialog('Template Directory', os.path.dirname(__file__), SVG_FILE_FILTER, parent=self)
        if directory:
            if glob.glob(os.path.join(directory, '*.svg')):
                self.addTemplateDir([directory])
            else:
                mc.warning('There is not svg files')

    def addTemplateDir(self, tempDirs):
        if not tempDirs:
            return
        add = False
        for tempDir in filter(lambda x: os.path.isdir(x), tempDirs):
            tempDir = tempDir.replace('\\', '/')
            if tempDir not in self.__recentDirs:
                self.__recentDirs.insert(0, tempDir)
                add = True

        files = filter(lambda x: os.path.isfile(x), tempDirs)
        refresh = False
        force = False
        override = False
        if files:
            DIV = '\n  '
            if question('Do you want to copy the files?' + DIV + DIV.join(map(lambda x: os.path.basename(x), files)), 'Copy SVG file', self):
                dst = self.templateDir_lineEdit.text()
                refresh = True
                for src in files:
                    basename = os.path.basename(src)
                    if os.path.isfile(os.path.join(dst, basename)):
                        if force and not override:
                            continue
                        elif not force:
                            from dialog import DialogWithCheckBox
                            dialog = DialogWithCheckBox('Override File', 'Do you want to override file?' + DIV + basename, parent=self, checkBoxText='Do same operation for the rest of files')
                            over, force = dialog.exec_()
                            if over == QMessageBox.Ok:
                                override = True
                            else:
                                continue
                    print '>> copy file', dst, 'to', src
                    shutil.copy2(src, dst)

        if add:
            self.templateDir_lineEdit.setText(self.__recentDirs[0])
        elif refresh:
            self.loadTemplate()

    def selectRecentDir(self, item):
        index = self.customTemplate_listWidget.row(item) + 1
        dir_path = item.text()
        path = self.__recentDirs[index]
        del self.__recentDirs[index]
        if os.path.isdir(dir_path):
            self.templateDir_lineEdit.setText(dir_path)
            self.__recentDirs.insert(0, path)
            self.showCustomTemplateDialog(False)
        else:
            QMessageBox.critical(self, 'Oops!', 'Select directory is not existing!')

    def popRecentDir(self, index):
        del self.__recentDirs[index + 1]
        if self.__recentDirs:
            self.templateDir_lineEdit.setText(self.__recentDirs[0])
        else:
            self.templateDir_lineEdit.clear()

    def loadTemplate(self):
        self.dispatcher.idle_add(partial(self.template_model.clear))
        svgFiles = sorted(glob.glob(os.path.join(self.templateDir_lineEdit.text(), '*.svg')))
        for svgFile in svgFiles:
            self.dispatcher.idle_add(partial(self.addSingleSvgItem, svgFile))

    def addSingleSvgItem(self, svgFile):
        br, drawSet = self.generateSvg(svgFile)
        if not br.isValid() or not drawSet:
            return
        width, height = [max(br.width(), br.height())] * 2
        image = QImage(120, 120, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        transform = QTransform()
        transform.scale(120.0 / width, 120.0 / height)
        for style, path in drawSet:
            scaledPath = transform.map(path)
            painter.setBrush(QColor(style.get('fill', Qt.black)))
            painter.drawPath(scaledPath)

        painter.end()
        pixmap = QPixmap.fromImage(image)
        icon = QIcon(pixmap)
        item = QStandardItem(icon, svgFile)
        item.size = br.size()
        self.template_model.appendRow(item)

    def addTemplateItems(self, items):
        self.template_model.clear()
        for item in items:
            self.template_model.appendRow(item)

    def showCustomTemplateDialog(self, toggle = True):
        if toggle:
            label = self.templateDir_label
            lineEdit = self.templateDir_lineEdit
            self.customTemplate_listWidget.move(label.mapToGlobal(label.geometry().bottomLeft() - QPoint(12, 6)))
            self.customTemplate_listWidget.setFixedWidth(label.width() + lineEdit.width() + 6)
            self.customTemplate_listWidget.clear()
            for d in self.__recentDirs[1:]:
                item = QListWidgetItem(d)
                item.setIcon(QIcon(':/create'))
                self.customTemplate_listWidget.addItem(item)

            self.animation.setStartValue(0.0)
            self.animation.setEndValue(1.0)
            self.animation.start()
        else:
            self.animation.setStartValue(1.0)
            self.animation.setEndValue(0.0)
            self.animation.start()

    def setCustomTemplateListOpacity(self, value):
        if self.animation.state() == QPropertyAnimation.Running:
            self.customTemplate_listWidget.setVisible(value > 0)
            self.customTemplate_listWidget.setWindowOpacity(value)

    def browseTemplateSVGFile(self):
        from dialog import OpenMultiFilesDialog
        files = OpenMultiFilesDialog('Template Files', os.path.dirname(__file__), SVG_FILE_FILTER, parent=self)
        if files:
            self.addTemplateDir(files)

    def wrapUpTab(self, index):
        if index == 5 or index == 6:
            widget = self.tabWidget.currentWidget()
            widget.resize(widget.size() + QSize(0, 1))

    def getReplaceString(self):
        if self.fromTo_Button.leftToRight:
            return (self.replace_lineEdit1.text(), self.replace_lineEdit2.text())
        else:
            return (self.replace_lineEdit2.text(), self.replace_lineEdit1.text())

    def initializeUI(self):
        self.clearSnapshotLabel()
        self.clearColorPaletteSelection()
        self.image_scrollContentWidget.clearPath()
        self.loadTemplate()
        self.command_scrollContentWidget.clearCommand()

    def clearSnapshotLabel(self):
        self.image_scrollContentWidget.path_lineEdit.clear()
        self.image_scrollContentWidget.image_label.path = ''
        self.image_scrollContentWidget.image_label.pixmap = QPixmap()

    def clearColorPaletteSelection(self):
        self.colorWidget.clearSelection()

    def templateIconSize(self):
        return self.template_listView.iconSize()

    def setTemplateIconSize(self, size):
        width = size.width()
        self.zoomOut_Button.setEnabled(width > 60)
        self.zoomIn_Button.setEnabled(width < 240)
        if width >= 60 and width <= 240:
            self.template_listView.setIconSize(size)
            if self.isVisible():
                self.messageLabel.showMessage('%d px' % width)

    def toggleSliderDirectionWidget(self, checked):
        isHorizontal = self.horizontalSliderDirection_widget.isVisible()
        if Attachment.isHorizontal(checked):
            if isHorizontal:
                width = self.sliderWidth_spinBox.value()
                height = self.sliderHeight_spinBox.value()
            self.verticalSliderDirection_widget.setEnabled(True)
            self.horizontalSliderDirection_widget.setEnabled(True)
            self.verticalSliderDirection_widget.show()
            self.horizontalSliderDirection_widget.hide()
            self.sliderWidth_slider.setMinimum(40)
            self.sliderWidth_spinBox.setMinimum(40)
            self.sliderHeight_slider.setMinimum(60)
            self.sliderHeight_spinBox.setMinimum(60)
            if isHorizontal:
                self.sliderWidth_spinBox.setValue(height)
                self.sliderHeight_spinBox.setValue(width)
        elif Attachment.isVertical(checked):
            if not isHorizontal:
                width = self.sliderWidth_spinBox.value()
                height = self.sliderHeight_spinBox.value()
            self.verticalSliderDirection_widget.setEnabled(True)
            self.horizontalSliderDirection_widget.setEnabled(True)
            self.verticalSliderDirection_widget.hide()
            self.horizontalSliderDirection_widget.show()
            self.sliderWidth_slider.setMinimum(60)
            self.sliderWidth_spinBox.setMinimum(60)
            self.sliderHeight_slider.setMinimum(40)
            self.sliderHeight_spinBox.setMinimum(40)
            if not isHorizontal:
                self.sliderWidth_spinBox.setValue(height)
                self.sliderHeight_spinBox.setValue(width)
        else:
            self.verticalSliderDirection_widget.setDisabled(True)
            self.horizontalSliderDirection_widget.setDisabled(True)
            self.sliderWidth_slider.setMinimum(10)
            self.sliderWidth_spinBox.setMinimum(10)
            self.sliderHeight_slider.setMinimum(10)
            self.sliderHeight_spinBox.setMinimum(10)

    def setSliderAttachment(self, value):
        self.sliderPreview_widget.attachment = value
        if Attachment.isVertical(value):
            self.setSliderAppearance(self.horizontalDirection_buttonGrp.checkedId())
        elif Attachment.isHorizontal(value):
            self.setSliderAppearance(self.verticalDirection_buttonGrp.checkedId())

    def setSliderAppearance(self, value):
        self.sliderPreview_widget.invertedAppearance = bool(value)

    def getAvailableIconSize(self, fromMap = False):
        if fromMap:
            size = self.parent().getSceneSize()
            if isinstance(size, QSizeF):
                size = size.toSize()
            self.image_scrollContentWidget.setIconLabelSize(size + QSize(2, 2), QRect(QPoint(1, 1), size))
        else:
            results = self.parent().getAvailableIconSize()
            if isinstance(results[0], (unicode, str)):
                return warn(*results)
            self.image_scrollContentWidget.setIconLabelSize(*results)

    def getScriptFromSelected(self):
        script = self.parent().getScriptFromSelected()
        if script:
            c = re.compile('python\\("(.+)"\\)', re.S)
            m = c.match(script)
            if m:
                script = m.group(1).replace("\\'", '"').replace('\\n', '\n').replace('\\t', '\t')
            else:
                script = script.replace(';', ';\n')
            self.command_scrollContentWidget.codeType_buttonGrp.button(m and 2 or 1).setChecked(True)
            self.command_scrollContentWidget.script_textEdit.setPlainText(script)

    def setColorPalette(self):
        from colorPaletteWidget import ColorPaletteDialog
        self.__colorPalette = ColorPaletteDialog(self)
        self.__colorPalette.hide()

    def showColorPalette(self, changeButton = None):
        self.restorePaletteGeometry(self.__colorPalette)
        if changeButton and isinstance(changeButton, QPushButton):
            self.__colorPalette.designatedButton = changeButton
        self.__colorPalette.saveINI.connect(lambda : self.savePaletteGeometry(self.__colorPalette))
        self.__colorPalette.show()

    def restorePaletteGeometry(self, palette):
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('ToolDialog')
        settings.beginGroup('Slider')
        value = settings.value('PaletteGeometry')
        if value is not None:
            palette.setGeometry(value)
        settings.endGroup()
        settings.endGroup()
        return

    def savePaletteGeometry(self, palette):
        settings = QSettings(self.getEnvPath(), QSettings.IniFormat)
        settings.beginGroup('ToolDialog')
        settings.beginGroup('Slider')
        geometry = palette.geometry()
        if geometry.top() < 26:
            geometry.moveTop(26)
        if geometry.left() < 8:
            geometry.moveLeft(8)
        settings.setValue('PaletteGeometry', geometry)
        settings.endGroup()
        settings.endGroup()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = ToolsDialog()
    dlg.show()
    sys.exit(app.exec_())