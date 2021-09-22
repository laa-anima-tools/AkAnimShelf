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


class AnimationUtils(object):

    # ============================================================================= #
    # IS CURVE SELECTED                                                             #
    # ============================================================================= #
    @staticmethod
    def is_curve_selected():
        if cmd.animCurveEditor('graphEditor1GraphEd', query=True, acs=True):
            return True
        else:
            return False

    # ============================================================================= #
    # COUNT SELECTED KEYS                                                           #
    # ============================================================================= #
    @staticmethod
    def count_selected_keys():
        num_keys = cmd.keyframe(q=True, kc=True, sl=True)
        return num_keys

    # ============================================================================= #
    # LIST ANIM CURVES                                                              #
    # ============================================================================= #
    @staticmethod
    def list_anim_curves():
        num_keys = AnimationUtils().count_selected_keys()
        anim_curves = []

        if num_keys != 0:
            connections = cmd.keyframe(q=True, n=True, sl=True)
        else:
            connections = cmd.listConnections(t='animCurve')
            if connections is None:
                connections = cmd.listConnections(t='mute')

        for con in connections:
            if con.split('_')[0] == 'mute':
                anim_curves.append(con.replace('mute_', ''))
            else:
                anim_curves.append(con)

        return anim_curves

    # ============================================================================= #
    # LIST CHANNELS                                                                 #
    # ============================================================================= #
    @staticmethod
    def list_channels():
        anim_curves = AnimationUtils().list_anim_curves()
        anim_channels = []

        for curve in anim_curves:
            obj = curve.split('_')[0]
            attr = curve.split('_')[-1]
            anim_channels.append(obj + '.' + attr)

        return anim_channels
