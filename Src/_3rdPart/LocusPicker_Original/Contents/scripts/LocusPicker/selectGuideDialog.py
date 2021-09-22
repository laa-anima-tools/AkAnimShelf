# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\selectGuideDialog.py
from loadUiType import loadUiType
import sys, os
if sys.exec_prefix.find('Maya') > 0:
    import maya.cmds as cmds
    INMAYA = True
else:
    INMAYA = False
uiFile = os.path.join(os.path.dirname(__file__), 'resources', 'selectGuideDialog.ui')
base_class, form_class = loadUiType(uiFile)

class SelectGuideDialog(base_class, form_class):

    def __init__(self, parent = None):
        super(base_class, self).__init__(parent)
        self.setupUi(self)
        self.connectSignals()

    def connectSignals(self):
        self.refreshList_Button.clicked.connect(self.getSelectedList)
        self.selection_listWidget.itemSelectionChanged.connect(self.selectInMaya)
        self.selectAll_Button.clicked.connect(self.selection_listWidget.selectAll)

    def getSelectedList(self):
        if INMAYA:
            selected = cmds.ls(sl=1)
            self.selection_listWidget.clear()
            self.selection_listWidget.addItems(selected)
            self.selection_listWidget.selectAll()

    def selectInMaya(self):
        if INMAYA:
            alreadySelected = set(cmds.ls(sl=1))
            uiSelected = set([ i.text() for i in self.selection_listWidget.selectedItems() ])
            cmds.select(list(uiSelected - alreadySelected), add=True)
            cmds.select(list(alreadySelected - uiSelected), d=True)


if __name__ == '__main__':
    from PySide.QtGui import QApplication
    app = QApplication(sys.argv)
    w = SelectGuideDialog()
    w.show()
    sys.exit(app.exec_())