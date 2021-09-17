# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\dialog.py
try:
    from PySide2.QtWidgets import QMessageBox, QCheckBox, QFileDialog
except:
    from PySide.QtGui import QMessageBox, QCheckBox, QFileDialog

import sys
if sys.exec_prefix.find('Maya') > 0:
    import maya.cmds as mc
    MAYA_LOADED = True
else:
    MAYA_LOADED = False

class DialogWithCheckBox(QMessageBox):

    def __init__(self, title = 'Confirm', text = 'Are you sure?', buttons = QMessageBox.Ok | QMessageBox.Cancel, defaultButton = QMessageBox.Cancel, parent = None, checkBoxText = 'Do not ask again'):
        super(DialogWithCheckBox, self).__init__(parent)
        self.setWindowTitle(title)
        self.setText(text)
        self.setStandardButtons(buttons)
        self.setDefaultButton(defaultButton)
        self.setIcon(QMessageBox.Question)
        self.checkbox = QCheckBox(checkBoxText, self)
        layout = self.layout()
        layout.addWidget(self.checkbox, 1, 1)

    def exec_(self, *args, **kwargs):
        """
        Override the exec_ method so you can return the value of the checkbox
        """
        return (QMessageBox.exec_(self, *args, **kwargs), self.checkbox.isChecked())


class TriStateDialog(QMessageBox):

    def __init__(self, title = 'Confirm', text = '', button1Text = 'Yes', button2Text = 'No', button3Text = 'Cancel', parent = None):
        QMessageBox.__init__(self, parent=parent)
        self.setWindowTitle(title)
        self.setText(text)
        self.addButton(button1Text, QMessageBox.AcceptRole)
        self.addButton(button2Text, QMessageBox.NoRole)
        self.addButton(button3Text, QMessageBox.RejectRole)


def OpenFileDialog(caption = 'Open', dirPath = '', fileFilter = 'All Files (*.*)', selectedFileFilter = '', parent = None):
    file = mc.fileDialog2(ff=fileFilter, fm=1, ds=2, cap=caption, dir=dirPath, sff=selectedFileFilter)
    if file:
        return file[0]
    else:
        return ''


def OpenMultiFilesDialog(caption = 'Open', dirPath = '', fileFilter = 'All Files (*.*)', selectedFileFilter = '', parent = None):
    files = mc.fileDialog2(ff=fileFilter, fm=4, ds=2, cap=caption, dir=dirPath, sff=selectedFileFilter, okc='Open')
    if files:
        return files
    else:
        return ''


def SaveFileDialog(caption = 'Save', dirPath = '', fileFilter = 'All Files (*.*)', selectedFileFilter = '', parent = None):
    file = mc.fileDialog2(ff=fileFilter, fm=0, ds=2, cap=caption, dir=dirPath, sff=selectedFileFilter)
    if file:
        return file[0]
    else:
        return ''


def SelectDirectoryDialog(caption = 'Select Directory', dirPath = '', fileFilter = 'All Files (*.*)', selectedFileFilter = '', parent = None):
    directory = mc.fileDialog2(ff=fileFilter, fm=2, ds=2, cap=caption, dir=dirPath, sff=selectedFileFilter, okc='  Select Directory  ')
    if directory:
        return directory[0]
    else:
        return ''


def WarnTrialDialog(parent = None):
    return QMessageBox.critical(parent, 'Sorry', 'Saving data is disabled in a trial version.')


if __name__ == '__main__':
    from PySide.QtGui import QApplication
    app = QApplication(sys.argv)
    dialog = TriStateDialog()
    answer = dialog.exec_()
    print answer == QMessageBox.AcceptRole
    app.exec_()