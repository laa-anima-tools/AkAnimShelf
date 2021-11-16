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

from AkAnimShelf.Src.Utils import animation_utils
reload(animation_utils)

NEXT, PREVIOUS, FIRST, LAST = 'next', 'previous', 'first', 'last'

class TimelineTools(cor.QObject):

    def __init__(self):
        """
        Initiates all the imported modules instances.
        """
        super(TimelineTools, self).__init__()
        self._animation_utils = animation_utils.AnimationUtils()

    def push_next_timeline_key(self):
        current_time = int(self._animation_utils.get_current_time())
        first_key = int(self._animation_utils.get_keytime(current_time, NEXT))
        second_key = int(self._animation_utils.get_keytime(first_key, NEXT))

        if second_key > first_key:
            self._animation_utils.add_timeline_inbetween()
            self._animation_utils.set_current_time(second_key)
            self._animation_utils.remove_timeline_inbetween()
            self._animation_utils.set_current_time(current_time)
        else:
            self._animation_utils.add_timeline_inbetween()


    def push_next_timeline_keys(self):
        self._animation_utils.add_timeline_inbetween()

    def pull_next_timeline_key(self):
        current_time = int(self._animation_utils.get_current_time())
        first_key = int(self._animation_utils.get_keytime(current_time, NEXT))
        second_key = int(self._animation_utils.get_keytime(first_key, NEXT))

        print first_key, current_time
        if current_time == first_key - 1 or first_key < current_time:
            return

        self._animation_utils.remove_timeline_inbetween()
        self._animation_utils.set_current_time(first_key)
        self._animation_utils.add_timeline_inbetween()
        self._animation_utils.set_current_time(current_time)

    def pull_next_timeline_keys(self):
        current_time = int(self._animation_utils.get_current_time())
        first_key = int(self._animation_utils.get_keytime(current_time, NEXT))

        if current_time >= first_key-1:
            return
        self._animation_utils.remove_timeline_inbetween()


        """
        Moves the timeline cursor to the next frame.
        """
        # cmd.keyframe(edit=True, relative=True, timeChange=1, time=(10, 20))
        # current_time = self._animation_utils.get_current_time()
        # next_key = cmd.findKeyframe(timeSlider=True, which="next")
        #
        # playback_start_time = self._playback_utils.get_playback_range()[0]
        # playback_end_time = self._playback_utils.get_playback_range()[1]
        # animation_start_time = self._playback_utils.get_animation_range()[0]
        # prev_time = self._playback_utils.get_current_time() - 1
        # print current_time

        # keys = cmd.keyframe('pCube1', time=(1, 100), query=True, valueChange=True, timeChange=True)
        # print keys
        # cmd.keyframe(edit=True, relative=True, time=(60, 70), timeChange=1)
        # print('test')

        # selected = cmd.ls(selection=True)
        # print selected
        # amount = 2
        #
        # for obj in selected:
        #     nodes = cmd.keyframe(obj, q=True, name=True, sl=True)
        #     print nodes
        #     # for node in nodes:
        #     #     activeKeyTimes = cmd.keyframe(node, q=True, sl=True, tc=True)
        #     #     for t in activeKeyTimes:
        #     #         cmds.keyframe(node, edit=True, time=(t, t), relative=True, timeChange=amount)
        #
        #

    def pull_next_keys(self):
        pass











