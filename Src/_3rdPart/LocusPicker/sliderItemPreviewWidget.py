# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\sliderItemPreviewWidget.py
try:
    from PySide2.QtCore import Qt, QPointF, QRectF, QMimeData, QByteArray
    from PySide2.QtGui import QColor, QPainter, QPixmap, QDrag, QLinearGradient
    from PySide2.QtWidgets import QWidget
except:
    from PySide.QtCore import Qt, QPointF, QRectF, QMimeData, QByteArray
    from PySide.QtGui import QWidget, QColor, QPainter, QLinearGradient, QPixmap, QDrag

from dropSliderItem import RectangleDropSliderItem
from const import Attachment, MIME_SLIDER_COMMAND, MIME_SLIDER_WIDTH, MIME_SLIDER_HEIGHT, MIME_SLIDER_ATTACH, MIME_SLIDER_INVERSE, MIME_SLIDER_CHANGETOOL, MIME_SLIDER_ATTRIBUTE, MIME_SLIDER_BUTTONNUMBER
from decorator import accepts, returns

class SliderItemPreviewWidget(QWidget):

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.__color = QColor(Qt.red)
        self.__attachment = Attachment.NotValid
        self.__invertedAppearance = False
        self.__margin = RectangleDropSliderItem.BORDER_MARGIN
        self.__thickness = RectangleDropSliderItem.SLIDER_THICKNESS
        self.__spacing = RectangleDropSliderItem.RESET_SPACING
        self.__handleThickness = RectangleDropSliderItem.HANDLE_THICKNESS
        self.__sliderRect = QRectF()
        self.__resetRect = QRectF()
        self.__grooveRect = QRectF()
        self.__grooveBaseRect = QRectF()
        self.__handleRect = QRectF()
        self.__min = 0
        self.__max = 1
        self.__command = 'Select'
        self.changeToolWidget = self.attributeOptionWidget = self.numberOfButtonsWidget = self.sliderAttachWidget = None
        self.__changeTool = 'No Change'
        self.__attributeOption = 'All Keyable'
        self.__numberOfButtons = 'One'
        self.sliderBaseColor = QColor(Qt.gray)
        self.sliderGrooveColor = QColor(Qt.darkGray)
        self.setFixedSize(20, 20)
        return

    @property
    @returns(str)
    def command(self):
        return self.__command

    @command.setter
    @accepts(str)
    def command(self, cmd):
        self.__command = cmd

    @property
    @returns(str)
    def changeTool(self):
        return self.__changeTool

    @changeTool.setter
    @accepts(str)
    def changeTool(self, tool):
        self.__changeTool = tool

    @property
    @returns(str)
    def attributeOption(self):
        return self.__attributeOption

    @attributeOption.setter
    @accepts(str)
    def attributeOption(self, opt):
        self.__attributeOption = opt

    @property
    @returns(str)
    def numberOfButtons(self):
        return self.__numberOfButtons

    @numberOfButtons.setter
    @accepts(str)
    def numberOfButtons(self, opt):
        self.__numberOfButtons = opt

    @property
    def min(self):
        return self.__min

    @min.setter
    def min(self, min):
        self.__min = min
        self.resetSliderRects()

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, color):
        self.__color = color
        self.update()

    @property
    def attachment(self):
        return self.__attachment

    @attachment.setter
    def attachment(self, attach):
        self.__attachment = attach
        self.resetSliderRects()

    @property
    def invertedAppearance(self):
        return self.__invertedAppearance

    @invertedAppearance.setter
    def invertedAppearance(self, invert):
        self.__invertedAppearance = invert
        self.resetSliderRects()
        self.update()

    def setFixedSize(self, *args, **kwargs):
        QWidget.setFixedSize(self, *args, **kwargs)
        self.resetSliderRects()

    def setFixedWidth(self, *args, **kwargs):
        QWidget.setFixedWidth(self, *args, **kwargs)
        self.resetSliderRects()

    def setFixedHeight(self, *args, **kwargs):
        QWidget.setFixedHeight(self, *args, **kwargs)
        self.resetSliderRects()

    def resetSliderRects(self):
        self.setSliderRect()
        self.setResetRect()
        self.setGrooveRect()
        self.setHandleRect()
        self.update()

    def setSliderRect(self):
        rect = QRectF(self.rect())
        if Attachment.isTop(self.attachment):
            sliderRect = rect.adjusted(self.__margin, 0, -self.__margin, 0)
            sliderRect.setHeight(self.__thickness)
            sliderRect.moveTopLeft(rect.topLeft() + QPointF(self.__margin, self.__margin))
        elif Attachment.isLeft(self.attachment):
            sliderRect = rect.adjusted(0, self.__margin, 0, -self.__margin)
            sliderRect.setWidth(self.__thickness)
            sliderRect.moveTopLeft(rect.topLeft() + QPointF(self.__margin, self.__margin))
        elif Attachment.isBottom(self.attachment):
            sliderRect = rect.adjusted(self.__margin, 0, -self.__margin, 0)
            sliderRect.setHeight(self.__thickness)
            sliderRect.moveBottomRight(rect.bottomRight() - QPointF(self.__margin, self.__margin))
        elif Attachment.isRight(self.attachment):
            sliderRect = rect.adjusted(0, self.__margin, 0, -self.__margin)
            sliderRect.setWidth(self.__thickness)
            sliderRect.moveBottomRight(rect.bottomRight() - QPointF(self.__margin, self.__margin))
        else:
            sliderRect = QRectF()
        self.__sliderRect = sliderRect

    def setResetRect(self):
        rect = self.__sliderRect.adjusted(0, 0, 0, 0)
        if Attachment.isVertical(self.attachment):
            rect.setWidth(self.__thickness)
        else:
            rect.setHeight(self.__thickness)
        if self.invertedAppearance:
            rect.moveBottomRight(self.__sliderRect.bottomRight())
        self.__resetRect = rect

    def setGrooveRect(self):
        rect = self.__sliderRect.adjusted(0, 0, 0, 0)
        if Attachment.isVertical(self.attachment):
            if self.invertedAppearance:
                rect.setRight(self.__resetRect.left() - self.__spacing)
            else:
                rect.setLeft(self.__resetRect.right() + self.__spacing)
            grooveRect = rect.adjusted(self.__handleThickness / 2, self.__handleThickness / 2, self.__handleThickness / -2, self.__handleThickness / -2)
            grooveRect.setHeight(self.__handleThickness / 2)
        else:
            if self.invertedAppearance:
                rect.setBottom(self.__resetRect.top() - self.__spacing)
            else:
                rect.setTop(self.__resetRect.bottom() + self.__spacing)
            grooveRect = rect.adjusted(self.__handleThickness / 2, self.__handleThickness / 2, self.__handleThickness / -2, self.__handleThickness / -2)
            grooveRect.setWidth(self.__handleThickness / 2)
        grooveRect.moveCenter(rect.center())
        self.__grooveBaseRect = rect
        self.__grooveRect = grooveRect

    def setHandleRect(self):
        normRect = self.rect()
        center = self.__grooveRect.center()
        rangeData = self.__max - self.__min
        ratio = self.__min * -1.0 / rangeData
        if Attachment.isVertical(self.attachment):
            handleRect = QRectF(0, 0, self.__handleThickness, self.__sliderRect.height() - 2)
            if self.invertedAppearance:
                margin = self.__margin + self.__handleThickness / 2
                handleRect.moveCenter(QPointF(normRect.right() - (margin + self.__grooveRect.width() * ratio + self.__thickness + self.__spacing), center.y()))
            else:
                margin = self.__margin + self.__handleThickness / 2
                handleRect.moveCenter(QPointF(normRect.left() + margin + self.__grooveRect.width() * ratio + self.__thickness + self.__spacing, center.y()))
        else:
            handleRect = QRectF(0, 0, self.__sliderRect.width() - 2, self.__handleThickness)
            if self.invertedAppearance:
                margin = self.__margin + self.__handleThickness / 2
                handleRect.moveCenter(QPointF(center.x(), normRect.bottom() - (margin + self.__grooveRect.height() * ratio + self.__thickness + self.__spacing)))
            else:
                margin = self.__margin + self.__handleThickness / 2
                handleRect.moveCenter(QPointF(center.x(), normRect.top() + margin + self.__grooveRect.height() * ratio + self.__thickness + self.__spacing))
        self.__handleRect = handleRect

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.__color)
        painter.drawRect(event.rect())
        if self.__sliderRect.isValid():
            painter.setPen(self.sliderGrooveColor)
            painter.setBrush(self.sliderBaseColor)
            painter.drawRoundedRect(self.__grooveBaseRect, 1, 1)
            if Attachment.isVertical(self.attachment):
                gradient = QLinearGradient(self.__grooveRect.topLeft(), self.__grooveRect.bottomLeft())
            else:
                gradient = QLinearGradient(self.__grooveRect.topLeft(), self.__grooveRect.topRight())
            gradient.setColorAt(0, self.sliderGrooveColor.darker(150))
            gradient.setColorAt(0.2, self.sliderGrooveColor.darker(150))
            gradient.setColorAt(0.8, self.sliderGrooveColor)
            gradient.setColorAt(1, self.sliderGrooveColor)
            painter.setBrush(gradient)
            painter.drawRect(self.__grooveRect)
            painter.setPen(self.__color.darker(150))
            painter.setBrush(self.__color)
            painter.drawRoundedRect(self.__handleRect, 2.0, 2.0)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(41, 41, 41))
            painter.drawRoundedRect(self.__resetRect, 2, 2)
            pixmap = QPixmap(':/reset')
            painter.drawPixmap(self.__resetRect.adjusted(1, 1, -1, -1), pixmap, pixmap.rect())

    def mousePressEvent(self, event):
        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        drag = QDrag(self)
        data = QMimeData()
        data.setColorData(self.color)
        data.setData(MIME_SLIDER_COMMAND, QByteArray(str(self.__command)))
        data.setData(MIME_SLIDER_WIDTH, QByteArray.number(self.width()))
        data.setData(MIME_SLIDER_HEIGHT, QByteArray.number(self.height()))
        if self.changeToolWidget.isVisible():
            data.setData(MIME_SLIDER_CHANGETOOL, QByteArray(str(self.changeTool)))
        if self.attributeOptionWidget.isVisible() and self.attributeOptionWidget.isEnabled():
            data.setData(MIME_SLIDER_ATTRIBUTE, QByteArray(str(self.attributeOption)))
        if self.numberOfButtonsWidget.isVisible():
            data.setData(MIME_SLIDER_BUTTONNUMBER, QByteArray(str(self.numberOfButtons)))
        if self.sliderAttachWidget.isVisible():
            data.setData(MIME_SLIDER_ATTACH, QByteArray.number(self.attachment))
            data.setData(MIME_SLIDER_INVERSE, QByteArray.number(self.invertedAppearance))
        drag.setMimeData(data)
        pixmap = QPixmap.grabWidget(self)
        drag.setDragCursor(pixmap, Qt.CopyAction)
        drag.start()
        QWidget.mouseMoveEvent(self, event)


if __name__ == '__main__':
    from PySide.QtGui import QApplication, QHBoxLayout
    import sys
    app = QApplication(sys.argv)
    container = QWidget()
    w = SliderItemPreviewWidget(container)
    w.setFixedSize(60, 22)
    layout = QHBoxLayout()
    layout.addWidget(w)
    container.setLayout(layout)
    container.show()
    sys.exit(app.exec_())