# -*- coding: utf-8 -*-
"""
=============================================================================
MODULE: playback_ctrl.py
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

from AkAnimShelf.Src.Core.Playback.PlaybackTools import playback_tools
from AkAnimShelf.Src.Core.Playback.FrameMarker import frame_marker
from AkAnimShelf.Src.Utils import info_utils
from AkAnimShelf.Src.Utils import maya_widgets_utils


KEY, BREAKDOWN, INBETWEEN = 0, 1, 2
TIME_CONTROL_OBJ = "$gPlayBackSlider"

global AK_FRAME_MARKER


class PlaybackController(cor.QObject):

    def __init__(self):
        """
        Initiates all the imported modules instances.
        """
        super(PlaybackController, self).__init__()
        self._playback_tools = playback_tools.PlaybackTools()
        self._frame_marker = frame_marker.FrameMarker()
        self.load_frame_markers()

    def go_to_the_next_frame(self):
        """
        Moves the timeline cursor to the next frame.
        """
        self._playback_tools.go_to_the_next_frame()
        info_utils.show_message('Next Frame >>')

    def go_to_the_prev_frame(self):
        """
        Moves the timeline cursor to the previous frame.
        """
        self._playback_tools.go_to_the_prev_frame()
        info_utils.show_message('<< Previous Frame')

    def go_to_the_next_key(self):
        """
        Move playback cursor to the next key.
        """
        self._playback_tools.go_to_the_next_key()
        info_utils.show_message('Next Key >>')

    def go_to_the_prev_key(self):
        """
        Move playback cursor to the previous key.
        """
        self._playback_tools.go_to_the_prev_key()
        info_utils.show_message('<< Previous Key')

    def next_frame_playback_press(self):
        """
        Keep moving playback cursor to the next frame util hotkey is released.
        """
        self._playback_tools.next_frame_playback_press()

    def next_frame_playback_release(self):
        """
        Stop moving playback cursor.
        """
        self._playback_tools.next_frame_playback_release()

    def prev_frame_playback_press(self):
        """
        Keep moving playback cursor to the previous frame util hotkey is released.
        """
        self._playback_tools.prev_frame_playback_press()

    def prev_frame_playback_release(self):
        """
        Stop moving playback cursor.
        """
        self._playback_tools.prev_frame_playback_release()

    def play(self):
        """
        Play the animation forward.
        """
        print('play')

    def play_back(self):
        """
        Play the animation back.
        """
        print('playback')

    def go_to_start_frame(self):
        """
        Go to the first playback frame.
        """
        print('start_frame')

    def go_to_end_frame(self):
        """
        Go to the end playback frame.
        """
        print('start_frame')

    def load_frame_markers(self):
        """
        Initiate scene frame markers.
        """
        info_utils.show_message('Frame Markers Loaded')
        global AK_FRAME_MARKER

        try:
            AK_FRAME_MARKER.setParent(None)
            AK_FRAME_MARKER.deleteLater()
            AK_FRAME_MARKER = None
        except:
            pass

        AK_FRAME_MARKER = frame_marker.FrameMarker()
        AK_FRAME_MARKER.setVisible(True)

    def add_frame_markers(self, type):
        """
        Add frame markers to the selected playback range.
        :param int type: frame marker type (0: key, 1: breakdown, 2: inbetween)
        """
        info_utils.show_message('Frame Marker Added')
        AK_FRAME_MARKER.add_frame_markers(type)

    def remove_frame_markers(self):
        """
        Remove frame markers from the selected playback range.
        """
        info_utils.show_message('Frame Marker Removed')
        AK_FRAME_MARKER.remove_frame_markers()

    def clear_all_frame_markers(self):
        """
        Clear all frame markers.
        """
        info_utils.show_message('Frame Markers Cleared')
        AK_FRAME_MARKER.clear_all_frame_markers()

    def add_markers_on_keys(self):
        """
        Clear all frame markers.
        """
        info_utils.show_message('Add Markers on Keys')
        AK_FRAME_MARKER.add_markers_on_keys(type)

    # def add_markers_on_keys(self):
    #     """
    #     Clear all frame markers.
    #     """
    #     info_utils.show_message('Add Markers on Keys')
    #     AK_FRAME_MARKER.add_markers_on_keys(type)














