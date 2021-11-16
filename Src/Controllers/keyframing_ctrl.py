# -*- coding: utf-8 -*-
"""
=============================================================================
MODULE: keyframing_ctrl.py
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

from AkAnimShelf.Src.Core.Keyframing.Timeline import timeline_tools
# from AkAnimShelf.Src.Core.Keyframing.GraphEditor import graph_editor
# from AkAnimShelf.Src.Core.Keyframing.AnimLayers import layer_tools
from AkAnimShelf.Src.Utils import info_utils
from AkAnimShelf.Src.Utils import maya_widgets_utils

reload(timeline_tools)
# reload(layer_tools)
# reload(graph_editor)
reload(info_utils)
reload(maya_widgets_utils)

KEY, BREAKDOWN, INBETWEEN = 0, 1, 2
TIME_CONTROL_OBJ = "$gPlayBackSlider"

global AK_FRAME_MARKER


class KeyframingController(cor.QObject):

    def __init__(self):
        """
        Initiates all the imported modules instances.
        """
        super(KeyframingController, self).__init__()
        self._timeline_tools = timeline_tools.TimelineTools()
        # self._frame_marker = frame_marker.FrameMarker()
        # self.load_frame_markers()

    # =========================================================================
    # TIMELINE
    # =========================================================================
    def push_next_timeline_key(self, frames=1):
        info_utils.show_message('Push Keys Forward: {0}F'.format(frames))
        self._timeline_tools.push_next_timeline_key()

    def push_next_timeline_keys(self, frames=1):
        info_utils.show_message('Push Keys Forward: {0}F'.format(frames))
        self._timeline_tools.push_next_timeline_keys()

    def pull_next_timeline_key(self, frames=1):
        info_utils.show_message('Push Keys Forward: {0}F'.format(frames))
        self._timeline_tools.pull_next_timeline_key()

    def pull_next_timeline_keys(self, frames=1):
        info_utils.show_message('Push Keys Forward: {0}F'.format(frames))
        self._timeline_tools.pull_next_timeline_keys()

    # # =========================================================================
    # # GRAPH EDITOR
    # # =========================================================================
    # def toggle_infinity(self):
    #     print('toggle_infinity')
    #
    # def toggle_buffer_curves(self):
    #     print('toggle_buffer_curves')
    #
    # def toggle_curves_view_mode(self):
    #     print('toggle_curves_view_mode')
    #
    # def toggle_pre_infinity_cycle_mode(self):
    #     print('toggle_pre_infinity_cycle_mode')
    #
    # def toggle_post_infinity_cycle_mode(self):
    #     print('toggle_post_infinity_cycle_mode')
    #
    # def toggle_mute_selected_channels_(self):
    #     print('toggle_mute_selected_channels_')
    #
    # def toggle_lock_selected_channels_(self):
    #     print('toggle_lock_selected_channels_')
    #
    # def toggle_buffer_selected_channels_(self):
    #     print('toggle_buffer_selected_channels_')
    #
    # def toggle_break_unify_tangents(self):
    #     print('toggle_break_unify_tangents')
    #
    # def toggle_free_lock_tangents(self):
    #     print('toggle_free_locked_tangents')
    #
    # def add_smart_key(self):
    #     print('add_smart_key')
    #
    # def add_breakdown_key(self):
    #     print('add_breakdown_key')
    #
    # def toggle_isolate_selection(self):
    #     print('toggle_isolate_selection')
    #
    # def toggle_tangent_types(self):
    #     print('toggle_isolate_selection')
    #
    # # =========================================================================
    # # LAYERS
    # # =========================================================================
    # def create_new_anim_layer(self, modifier=None, layer=DEFAULT_LAYER):
    #     print('create_new_anim_layer')
    #     self._layer_tools.create_new_anim_layer(layer)
    #
    # def delete_selected_anim_layers(self):
    #     print('delete_selected_anim_layers')
    #     self._layer_tools.delete_selected_anim_layers()
    #
    # def set_active_anim_layer(self, layer=BASE_LAYER):
    #     print('set_active_anim_layer')
    #     self._layer_tools.set_active_anim_layer(layer)
    #
    # def set_anim_layers_color(self, layer=BASE_LAYER, color=None):
    #     print('set_anim_layers_color')
    #     if color is None:
    #         self._layer_tools.set_active_anim_layer(layer, self._colors[RED])
    #     else:
    #         self._layer_tools.set_active_anim_layer(layer, color)
    #
    # def merge_selected_anim_layers(self):
    #     print('merge_selected_layers')
    #
    # def lock_anim_layers(self):
    #     print('lock_layers')
    #
    # def solo_anim_layers(self):
    #     print('solo_layers')
    #
    # def mute_anim_layers(self):
    #     print('mute_layers')
    #
    # def select_anim_layers(self):
    #     print('mute_layers')
    #
    # def activate_next_anim_layer(self):
    #     print('activate_next_layer')
    #
    # def activate_prev_anim_layer(self):
    #     print('activate_prev_layer')
    #
    # def set_anim_layers_color(self):
    #     print('set_layers_color')














