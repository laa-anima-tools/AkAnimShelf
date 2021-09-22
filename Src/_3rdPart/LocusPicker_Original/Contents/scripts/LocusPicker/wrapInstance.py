# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\wrapInstance.py
try:
    from shiboken2 import wrapInstance, getCppPointer
    from PySide2 import QtGui, QtCore
except:
    from shiboken import wrapInstance, getCppPointer
    from PySide import QtGui, QtCore

def wrapinstance(ptr, base = None):
    if ptr is None:
        return
    else:
        ptr = long(ptr)
        if base is None:
            qObj = wrapInstance(long(ptr), QtCore.QObject)
            metaObj = qObj.metaObject()
            cls = metaObj.className()
            superCls = metaObj.superClass().className()
            if hasattr(QtGui, cls):
                base = getattr(QtGui, cls)
            elif hasattr(QtGui, superCls):
                base = getattr(QtGui, superCls)
            else:
                base = QtGui.QWidget
        return wrapInstance(long(ptr), base)


def unwrapinstance(object):
    return long(getCppPointer(object)[0])