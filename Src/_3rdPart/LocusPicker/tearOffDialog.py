# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\tearOffDialog.py
try:
    from PySide2.QtCore import Qt, QSize, Signal
    from PySide2.QtWidgets import QDialog
except:
    from PySide.QtCore import Qt, QSize, Signal
    from PySide.QtGui import QDialog

from loadUiType import loadUiType
import os
uiFile = os.path.join(os.path.dirname(__file__), 'resources', 'tearOffDialog.ui')
base_class, form_class = loadUiType(uiFile)

class TearOffDialog(base_class, form_class):
    closed = Signal(QDialog)

    def __init__(self, charName, mapName, parent = None):
        super(base_class, self).__init__(parent, Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(charName + ' : ' + mapName)
        self.__characterName = charName
        self.__mapName = mapName
        self.__tabWidget = None
        self.__view = None
        self.__isSceneEditable = True
        self.__index = -1
        return

    @property
    def characterName(self):
        return self.__characterName

    @property
    def mapName(self):
        return self.__mapName

    def isUsePrefix(self):
        return self.usePrefix_checkBox.isChecked()

    def prefix(self):
        return self.prefix_lineEdit.text()

    def scene(self):
        return self.__view.scene()

    def setOriginalState(self, index, tabWidget, usePrefix, prefix):
        self.__index = index
        self.__tabWidget = tabWidget
        self.usePrefix_checkBox.setChecked(usePrefix)
        self.prefix_lineEdit.setText(prefix)

    def addView(self, view):
        self.layout().addWidget(view)
        self.__view = view
        scene = view.scene()
        if hasattr(scene, 'editable'):
            self.__isSceneEditable = scene.editable
            scene.setAllItemsEditable(False)
        else:
            self.__isSceneEditable = False

    def resize(self, *args):
        if len(args) == 1 and isinstance(args[0], QSize):
            size = args[0] + QSize(6, self.prefix_widget.height())
            args = tuple([size])
        super(base_class, self).resize(*args)

    def closeEvent(self, event):
        mainWindow = self.__tabWidget.window()
        mainCharName = mainWindow.characterName()
        mainMapNames = [ self.__tabWidget.tabText(i) for i in xrange(self.__tabWidget.count()) ]
        if mainCharName == self.__characterName and self.__mapName not in mainMapNames:
            scene = self.__view.scene()
            if self.__isSceneEditable and hasattr(scene, 'editable'):
                scene.setAllItemsEditable(True)
            self.__tabWidget.addView(self.__mapName, self.__index, self.__view, self.prefix_lineEdit.text(), self.usePrefix_checkBox.isChecked())
        self.closed.emit(self)
        super(base_class, self).closeEvent(event)