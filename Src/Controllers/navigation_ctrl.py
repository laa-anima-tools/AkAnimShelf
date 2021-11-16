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

from AkAnimShelf.Src.Core.Keyframing.GraphEditor import graph_editor
from AkAnimShelf.Src.Core.Keyframing import timeline_tools
from AkAnimShelf.Src.Core.Keyframing import layer_tools
from AkAnimShelf.Src.Utils import info_utils
from AkAnimShelf.Src.Utils import maya_widgets_utils

reload(timeline_tools)
reload(layer_tools)
reload(graph_editor)
reload(info_utils)
reload(maya_widgets_utils)

KEY, BREAKDOWN, INBETWEEN = 0, 1, 2
TIME_CONTROL_OBJ = "$gPlayBackSlider"

global AK_FRAME_MARKER


class NavigationController(cor.QObject):

    def __init__(self):
        """
        Initiates all the imported modules instances.
        """
        super(NavigationController, self).__init__()
        self._playback_tools = playback_tools.PlaybackTools()
        self._frame_marker = frame_marker.FrameMarker()
        self.load_frame_markers()

    def switch_manipulator_mode(self):
        self._common_tools.switch_manipulator_mode()

    def toggle_move_mode(self):
        result = self._common_tools.toggle_move_mode()
        self.info_sent.emit('> Move Mode: {0}'.format(result))
        self.transform_mode_changed.emit(result)

    def toggle_rotate_mode(self):
        result = self._common_tools.toggle_rotate_mode()
        self.info_sent.emit('> Rotate Mode: {0}'.format(result))
        self.transform_mode_changed.emit(result)

    def toggle_scale_mode(self):
        result = self._common_tools.toggle_scale_mode()
        self.info_sent.emit('> Scale Mode: {0}'.format(result))
        self.transform_mode_changed.emit(result)

    def toggle_translate_channels(self):
        self._selected_channels = self._common_tools.toggle_translate_channels(modifier)
        self.info_sent.emit('> Toogle Translate Channels')
        self.coordinate_system_changed.emit(self._selected_channels)

    def toggle_rotate_channels(self):
        self._selected_channels = self._common_tools.toggle_rotate_channels(modifier)
        self.info_sent.emit('> Toogle Rotate Channels')
        self.coordinate_system_changed.emit(self._selected_channels)

    def toggle_scale_channels(self):
        self._selected_channels = self._common_tools.toggle_scale_channels(modifier)
        self.info_sent.emit('> Toogle Scale Channels')
        self.coordinate_system_changed.emit(self._selected_channels)

    def toggle_all_channels(self):
        self._common_tools.toggle_all_channels(modifier)
        self.info_sent.emit('> Toggle All Channels')
        self.coordinate_system_changed.emit(self._selected_channels)

    def select_all_channels(self):
        self._selected_channels = self._common_tools.select_all_channels(modifier)
        self.info_sent.emit('> All channels selected')
        self.coordinate_system_changed.emit(self._selected_channels)

    def clear_all_channels(self):
        self._selected_channels = self._common_tools.clear_all_channels(modifier)
        self.info_sent.emit('> Channels cleared')
        self.coordinate_system_changed.emit(self._selected_channels)

    def activate_sync_mode(self, modifier, state):
        self._selected_channels = self._common_tools.activate_sync_mode(modifier, state)
        self.info_sent.emit('> Channels cleared')
        self.coordinate_system_changed.emit(self._selected_channels)

    def set_anim_mode(self):
        self._selected_channels = self._common_tools.set_anim_mode(modifier)
        self.info_sent.emit('> Channels cleared')
        self.coordinate_system_changed.emit(self._selected_channels)

    def set_previs_mode(self):
        self._selected_channels = self._common_tools.set_previs_mode(modifier)
        self.info_sent.emit('> Channels cleared')
        self.coordinate_system_changed.emit(self._selected_channels)














