# -*- coding: utf-8 -*-
"""
=============================================================================
MODULE: navigation_ctrl.py
-----------------------------------------------------------------------------
This is an intermidiate module that triggers all the user actions. It is the
module responsible for communicating with the GUI using the signal/slots
mechanism. That´s the module that need to be imported when the user defines
a hotkey.
-----------------------------------------------------------------------------
USAGE:
# GO TO THE NEXT FRAME (Default Hotkey: X)
from AkAnimShelf.Src.Controllers import playback_ctrl
playback_ctrl.PlaybackController().go_to_the_next_frame()
-----------------------------------------------------------------------------
AUTHOR:   Leandro Adeodato
VERSION:  v1.0.0 | Maya 2018 | Python 2
=============================================================================
"""
import maya.cmds as cmd
from PySide2 import QtCore as cor

from AkAnimShelf.Src.Utils import info_utils
from AkAnimShelf.Src.Utils import maya_widgets_utils
reload(info_utils)
reload(maya_widgets_utils)

from AkAnimShelf.Src.Core.Navigation import hotkeys_manager
reload(hotkeys_manager)

KEY, BREAKDOWN, INBETWEEN = 0, 1, 2
TIME_CONTROL_OBJ = "$gPlayBackSlider"

global AK_FRAME_MARKER


class NavigationController(cor.QObject):

    def __init__(self):
        super(NavigationController, self).__init__()
        self._hotkeys_manager = hotkeys_manager.HotkeysManager()

    def switch_hotkey_set(self):
        self._hotkeys_manager.switch_hotkey_set()













