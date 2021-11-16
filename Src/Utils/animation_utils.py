"""
=============================================================================
MODULE: animation_utils.py
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
import maya.mel as mel
import pymel as pm

from AkAnimShelf.Src.Utils import maya_widgets_utils; reload(maya_widgets_utils)

TIME_CONTROL_OBJ = "$gPlayBackSlider"
ANIMATION, PLAYBACK = 0, 1
ALL_RANGE, BEFORE_CURRENT_TIME, AFTER_CURRENT_TIME = 0, 1, 2
START_TIME, END_TIME = 0, 1
NEXT, PREVIOUS, FIRST, LAST = 'next', 'previous', 'first', 'last'


class AnimationUtils(object):
    time_control = maya_widgets_utils.MayaWidgetsUtils.get_maya_control(TIME_CONTROL_OBJ)

    @staticmethod
    def get_current_time():
        return cmd.currentTime(query=True)

    @staticmethod
    def set_current_time(current_time):
        cmd.currentTime(current_time, edit=True)

    @staticmethod
    def count_playback_range_keys():
        return len(AnimationUtils().get_playback_range_keytimes())

    @staticmethod
    def count_animation_range_keys():
        return len(AnimationUtils().get_animation_range_keytimes())

    @staticmethod
    def key_exists(time=int(AnimationUtils().get_current_time())):
        next_key = int(AnimationUtils().get_keytime(time, NEXT))
        prev_from_next_key = int(AnimationUtils().get_keytime(next_key, PREVIOUS))
        num_keys = AnimationUtils().count_playback_range_keys()

        if not num_keys:
            return False

        return True if time == prev_from_next_key else False


    @staticmethod
    def get_keytime(time, which):
        return cmd.findKeyframe(timeSlider=True, time=(time, time), which=which)

    @staticmethod
    def get_selection_range():
        timeline_range = cmd.timeControl(AnimationUtils.time_control, q=True, rangeArray=True)
        return [int(timeline_range[0]), int(timeline_range[1])]

    @staticmethod
    def get_selection_frames():
        timeline_range = cmd.timeControl(AnimationUtils.time_control, q=True, rangeArray=True)
        return range(int(timeline_range[0]), int(timeline_range[1]))

    @staticmethod
    def add_timeline_inbetween():
        mel.eval('timeSliderEditKeys addInbetween;')

    @staticmethod
    def remove_timeline_inbetween():
        mel.eval('timeSliderEditKeys removeInbetween;')

    @staticmethod
    def get_playback_range(option=ALL_RANGE):
        """
        Get the entire playback range, the playback range from start to the current frame or the playback range from
        current frame to the end.
        :param int option: entire playback range or just a part.
        :return: playback range
        :rtype: [int, int]
        """
        current_time = AnimationUtils().get_current_time()
        playback_start_time = cmd.playbackOptions(minTime=True, query=True)
        playback_end_time = cmd.playbackOptions(maxTime=True, query=True)

        if option == BEFORE_CURRENT_TIME:
            return [int(playback_start_time), int(current_time)]
        elif option == AFTER_CURRENT_TIME:
            return [int(current_time), int(playback_end_time)]
        else:
            return [int(playback_start_time), int(playback_end_time)]

    @staticmethod
    def get_animation_range(option=ALL_RANGE):
        """
        Get the entire animation range, the playback range from start to the current frame or the animation range from
        current frame to the end.
        :param int option: entire animation range or just a part.
        :return: animation range
        :rtype: [int, int]
        """
        current_time = AnimationUtils().get_current_time()
        animation_start_time = cmd.playbackOptions(animationStartTime=True, query=True)
        animation_end_time = cmd.playbackOptions(animationEndTime=True, query=True)

        if option == BEFORE_CURRENT_TIME:
            return [int(animation_start_time), int(current_time)]
        elif option == AFTER_CURRENT_TIME:
            return [int(current_time), int(animation_end_time)]
        else:
            return [int(animation_start_time), int(animation_end_time)]

    @staticmethod
    def set_playback_range(start, end):
        cmd.playbackOptions(minTime=start, maxTime=end)

    @staticmethod
    def set_animation_range(start, end):
        cmd.playbackOptions(animationStartTime=start, animationEndTime=end)

    @staticmethod
    def is_curve_selected():
        if cmd.animCurveEditor('graphEditor1GraphEd', query=True, acs=True):
            return True
        else:
            return False

    @staticmethod
    def count_keys(obj):
        num_keys = cmd.keyframe(query=True, keyframeCount=True)
        return num_keys

    @staticmethod
    def count_selected_keys():
        num_keys = cmd.keyframe(query=True, keyframeCount=True, selected=True)
        return num_keys

    # @staticmethod
    # def list_anim_curves():
    #     num_keys = AnimationUtils().count_selected_keys()
    #     anim_curves = []
    #
    #     selection = cmd.ls(selection=True)
    #     if not selection:
    #         return anim_curves
    #
    #     if num_keys != 0:
    #         connections = cmd.keyframe(query=True, name=True, selected=True)
    #     else:
    #         connections = cmd.listConnections(type='animCurve') or cmd.listConnections(type='mute') or []
    #
    #     for con in connections:
    #         if con.split('_')[0] == 'mute':
    #             anim_curves.append(con.replace('mute_', ''))
    #         else:
    #             anim_curves.append(con)
    #
    #     return anim_curves

    @staticmethod
    def list_anim_curves():
        num_keys = AnimationUtils().count_selected_keys()
        anim_curves = []

        selection = cmd.ls(selection=True)
        if not selection:
            return anim_curves

        if num_keys != 0:
            connections = cmd.keyframe(query=True, name=True, selected=True)
        else:
            connections = cmd.listConnections(type='animCurve') or cmd.listConnections(type='mute') or []

        for con in connections:
            if con.split('_')[0] == 'mute':
                anim_curves.append(con.replace('mute_', ''))
            else:
                anim_curves.append(con)

        return anim_curves

    @staticmethod
    def list_channels():
        anim_curves = AnimationUtils().list_anim_curves()
        anim_channels = []

        for curve in anim_curves:
            obj = curve.split('_')[0]
            attr = curve.split('_')[-1]
            anim_channels.append(obj + '.' + attr)

        return anim_channels

    @staticmethod
    def list_anim_attributes():
        anim_attrs = []
        selection = cmd.ls(selection=True)
        if not selection:
            return anim_attrs

        anim_attrs = cmd.listAnimatable(selection[0]) or []
        return anim_attrs

    @staticmethod
    def get_playback_range_keytimes(option=ALL_RANGE):
        keytimes = []
        selection = cmd.ls(selection=True)

        if not selection:
            return keytimes

        num_keys = AnimationUtils().count_keys(selection[0])
        if num_keys == 0:
            return keytimes

        next_key = start_key = cmd.findKeyframe(timeSlider=True, which="first")
        end_key = cmd.findKeyframe(timeSlider=True, which="last")
        keytimes.append(int(start_key))

        while next_key != end_key:
            next_key = cmd.findKeyframe(timeSlider=True, time=(next_key, next_key), which="next")
            if next_key not in keytimes:
                keytimes.append(int(next_key))

        return keytimes

    @staticmethod
    def get_animation_range_keytimes(option=ALL_RANGE):
        keytimes = []
        selection = cmd.ls(selection=True)
        playback_range = AnimationUtils().get_playback_range()
        animation_range = AnimationUtils().get_animation_range()
        AnimationUtils().set_playback_range(animation_range[START_TIME], animation_range[END_TIME])

        if not selection:
            return keytimes

        num_keys = AnimationUtils().count_keys(selection[0])
        if num_keys == 0:
            return keytimes

        next_key = start_key = cmd.findKeyframe(timeSlider=True, which="first")
        end_key = cmd.findKeyframe(timeSlider=True, which="last")
        keytimes.append(int(start_key))

        while next_key != end_key:
            next_key = cmd.findKeyframe(timeSlider=True, time=(next_key, next_key), which="next")
            if next_key not in keytimes:
                keytimes.append(int(next_key))

        AnimationUtils().set_playback_range(playback_range[START_TIME], playback_range[END_TIME])
        return keytimes







        # print next_key
        # object = cmd.ls(selection=True)
        # attr = "tx"
        #
        # print cmd.keyframe(str(object[0]) + "." + attr, q=True)
        # while next_key < playback_range[END_TIME]:
        #     print(next_key)
        #     next_key = cmd.findKeyframe(timeSlider=True, time=(next_key, next_key), which="next")

        # keys = cmd.findKeyframe(timeSlider=True, time=(10, 10), which="next")
        # print keys
        # key_times = []
        # anim_curves = AnimationUtils().list_anim_curves() or []
        #
        # for anim_curve in anim_curves:
        #     curve_times = cmd.keyframe(anim_curve, query=True, timeChange=1, time=(1, 40)) or []
        #     print curve_times


        # keys = cmd.findKeyframe(time=(1, 100), an="keys")
        # print keys
        #
        # timeList = self.keyframe(query=True, timeChange=True)
        # print timeList
        # graph_selection = AnimationUtils().count_selected_keys()
        # print graph_selection
        #
        # if graph_selection != 0:

        # keytimes = cmd.keyframe(query=True, timeChange=1, time=(1, 40)) or []
        # print keytimes





        # selection = cmd.ls(selection=True)
        # next_key = cmd.findKeyframe(timeSlider=True, which="next")
        # all_keys = cmd.keyframe('pCube1', sl=True, q=True, tc=True)
        # print next_key, all_keys
        #
        # print list(set(cmd.keyframe(query=True, timeChange=1, time=(1, 40))))

    # @staticmethod
    # def get_animation_data():
    #     anim_attrs = cmd.list_anim_attributes()
    #     print anim_attrs
    #
    #     # for attr in anim_attrs:
    #     #     num_keys = cmd.keyframe(attr, query=True, keyframeCount=True)
    #     #     if num_keys > 0:
