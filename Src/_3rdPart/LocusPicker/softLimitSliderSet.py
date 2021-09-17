# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\softLimitSliderSet.py
try:
    from PySide2.QtCore import Signal
except:
    from PySide.QtCore import Signal

from loadUiType import loadUiType
import os, math
uiFile = os.path.join(os.path.dirname(__file__), 'resources', 'softLimitSliderSet.ui')
base_class, form_class = loadUiType(uiFile)

class SoftLimitSliderSet(base_class, form_class):
    maximumChanged = Signal(int)
    valueChanged = Signal(int)

    def __init__(self, parent = None, softMax = True):
        super(base_class, self).__init__(parent)
        self.setupUi(self)
        self.__softMax = softMax
        self.connectSignals()

    def connectSignals(self):
        self.slider.valueChanged.connect(self.valueChanged.emit)
        if self.__softMax:
            self.spinBox.valueChanged.connect(self.setSliderLimit)
        else:
            self.spinBox.valueChanged.connect(self.slider.setValue)

    def setSliderLimit(self, value):
        oldMax = self.slider.maximum()
        if value > oldMax:
            newMax = value
            self.slider.setMaximum(max(oldMax, newMax))
            self.maximumChanged.emit(newMax - oldMax)
        self.slider.setValue(value)

    def value(self):
        return self.slider.value()

    def setValue(self, val):
        self.slider.setValue(val)
        self.spinBox.setValue(val)

    def setMaximum(self, val):
        self.slider.setMaximum(val)
        if not self.__softMax:
            self.spinBox.setMaximum(val)


if __name__ == '__main__':
    from PySide.QtGui import QApplication
    import sys
    app = QApplication(sys.argv)
    w = SoftLimitSliderSet()
    w.show()
    w.setValue(240)
    sys.exit(app.exec_())