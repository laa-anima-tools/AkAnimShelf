# Embedded file name: C:/Users/hgkim/workspace/LocusPicker/src\mapSizeWidget.py
from PySide.QtCore import Signal, QSize
from PySide.QtGui import QWidget, QHBoxLayout, QSpinBox, QLabel, QPixmap

class MapSizeWidget(QWidget):
    sizeChanged = Signal(QSize)

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.setContentsMargins(2, 0, 0, 0)
        label = QLabel(self)
        label.setFixedSize(14, 14)
        label.setPixmap(QPixmap(':/size'))
        label.setScaledContents(True)
        self.horizontalLayout.addWidget(label)
        self.width_spinBox = QSpinBox(self)
        self.width_spinBox.setButtonSymbols(QSpinBox.NoButtons)
        self.width_spinBox.setMinimum(1)
        self.width_spinBox.setMaximum(999)
        self.width_spinBox.setKeyboardTracking(False)
        self.horizontalLayout.addWidget(self.width_spinBox)
        label = QLabel('x', self)
        self.horizontalLayout.addWidget(label)
        self.height_spinBox = QSpinBox(self)
        self.height_spinBox.setButtonSymbols(QSpinBox.NoButtons)
        self.height_spinBox.setMinimum(1)
        self.height_spinBox.setMaximum(999)
        self.height_spinBox.setKeyboardTracking(False)
        self.horizontalLayout.addWidget(self.height_spinBox)
        self.width_spinBox.valueChanged.connect(self.emitSize)
        self.height_spinBox.valueChanged.connect(self.emitSize)

    def emitSize(self):
        self.sizeChanged.emit(QSize(self.width_spinBox.value(), self.height_spinBox.value()))

    def setSize(self, size):
        self.blockSignals(True)
        self.width_spinBox.setValue(size.width())
        self.height_spinBox.setValue(size.height())
        self.blockSignals(False)