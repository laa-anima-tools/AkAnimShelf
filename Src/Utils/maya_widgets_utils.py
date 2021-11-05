"""
=============================================================================
MODULE: maya_widgets_utils.py
-----------------------------------------------------------------------------
This class is responsible for showing info to the user. This module must
be used by the trigger module, SHOULD NOT BE USED DIRECTLY.
-----------------------------------------------------------------------------
AUTHOR:   Leandro Adeodato
VERSION:  v1.0.0 | Maya 2018 | Python 2
=============================================================================
"""
import maya.mel as mel
import maya.OpenMayaUI as mui

from shiboken2 import wrapInstance
from PySide2 import QtWidgets as wdg

time_control_obj = "$gPlayBackSlider"
shelf_obj = "$gShelfTopLevel"
status_line_obj = "$gStatusLine"
attribute_editor_obj = "$gAttributeEditorWindowName"
channel_box_obj = "$gChannelBoxName"
toolbox_obj = "$gToolBox"
command_line_obj = "$gCommandLine"
range_slider_obj = "$gTimeRangeSlider"
help_line_obj = "$gHelpLineForm"


class MayaWidgetsUtils(object):

    @staticmethod
    def get_maya_main_window():
        main_window_ptr = mui.MQtUtil.mainWindow()
        main_window_widget = wrapInstance(long(main_window_ptr), wdg.QWidget)
        return main_window_widget

    @staticmethod
    def get_maya_control(control_name):
        control = mel.eval("$tempVar = {0}".format(control_name))
        return control

    @staticmethod
    def get_maya_control_widget(control_name):
        control = mel.eval("$tempVar = {0}".format(control_name))
        control_ptr = mui.MQtUtil.findControl(control)
        control_widget = wrapInstance(long(control_ptr), wdg.QWidget)
        return control_widget


