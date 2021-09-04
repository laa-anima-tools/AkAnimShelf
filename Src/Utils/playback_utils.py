"""
=============================================================================
MODULE: keyframing_utils.py
-----------------------------------------------------------------------------
A set of helper static methods that can be used by any other module.
It contains common functionality related to Maya's keyframing system
but it does not do anything by itself.
-----------------------------------------------------------------------------
AUTHOR:   Leandro Adeodato
VERSION:  v1.0.0 | Maya 2018 | Python 2
=============================================================================
"""
import maya.cmds as cmd
import pymel as pm


class PlaybackUtils(object):

    @staticmethod
    def get_current_time():
        return cmd.currentTime(query=True)

    @staticmethod
    def set_current_time(current_time):
        cmd.currentTime(current_time, edit=True)

    @staticmethod
    def get_playback_range():
        playback_start_time = cmd.playbackOptions(minTime=True, query=True)
        playback_end_time = cmd.playbackOptions(maxTime=True, query=True)
        return [playback_start_time, playback_end_time]

    @staticmethod
    def get_animation_range():
        animation_start_time = cmd.playbackOptions(animationStartTime=True, query=True)
        animation_end_time = cmd.playbackOptions(animationEndTime=True, query=True)
        return [animation_start_time, animation_end_time]

    @staticmethod
    def get_selection_range():
        time_control = pm.lsUI(type='timeControl')[0]
        selection_range = pm.timeControl(time_control, rangeArray=True, query=True)
        return selection_range

    @staticmethod
    def set_playback_range(start, end):
        cmd.playbackOptions(minTime=start)
        cmd.playbackOptions(maxTime=end)

    @staticmethod
    def set_animation_range(start, end):
        cmd.playbackOptions(animationStartTime=start)
        cmd.playbackOptions(animationEndTime=end)

