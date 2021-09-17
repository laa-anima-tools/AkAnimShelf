# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\loadUiType.py
try:
    from pyside2uic import compileUi
    from PySide2 import QtGui, QtWidgets
except:
    from pysideuic import compileUi
    from PySide import QtGui

from xml.etree import ElementTree
from cStringIO import StringIO
import logging

class DisableLogger:

    def __enter__(self):
        logging.disable(logging.CRITICAL)

    def __exit__(self, *args):
        logging.disable(logging.NOTSET)


def loadUiType(uiFile):
    parsed = ElementTree.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text
    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}
        with DisableLogger():
            compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame
        form_class = frame['Ui_%s' % form_class]
        try:
            base_class = eval('QtGui.%s' % widget_class)
        except:
            base_class = eval('QtWidgets.%s' % widget_class)

    return (form_class, base_class)