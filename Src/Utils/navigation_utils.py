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

MOVE, ROTATE, SCALE = 'Move', 'Rotate', 'Scale'
LOCAL, WORLD, NORMAL, GIMBAL, PARENT, COMPONENT = 'Local', 'World', 'Normal', 'Gimbal', 'Parent', 'Component'


class NavigationUtils(object):

    # ============================================================================= #
    # GET CURRENT MOVE MODE                                                         #
    # ============================================================================= #
    @staticmethod
    def get_current_move_mode():
        return cmd.manipMoveContext(MOVE, q=True, mode=True)

    # ============================================================================= #
    # SET CURRENT MOVE MODE                                                         #
    # ============================================================================= #
    @staticmethod
    def set_current_move_mode(mode):
        cmd.manipMoveContext(MOVE, e=True, mode=mode)

    # ============================================================================= #
    # GET CURRENT ROTATE MODE                                                       #
    # ============================================================================= #
    @staticmethod
    def get_current_rotate_mode():
        return cmd.manipRotateContext(ROTATE, q=True, mode=True)

    # ============================================================================= #
    # SET CURRENT MOVE MODE                                                         #
    # ============================================================================= #
    @staticmethod
    def set_current_rotate_mode(mode):
        cmd.manipRotateContext(ROTATE, e=True, mode=mode)

    # ============================================================================= #
    # GET CURRENT SCALE MODE                                                        #
    # ============================================================================= #
    @staticmethod
    def get_current_scale_mode():
        return cmd.manipScaleContext(SCALE, q=True, mode=True)

    # ============================================================================= #
    # GET CURRENT SCALE MODE                                                        #
    # ============================================================================= #
    @staticmethod
    def set_current_scale_mode(mode):
        cmd.manipScaleContext(SCALE, e=True, mode=mode)

    # ============================================================================= #
    # RESET MOVE MODE                                                               #
    # ============================================================================= #
    @staticmethod
    def reset_move_mode(mode):
        cmd.manipMoveContext(MOVE, e=True, mode=mode)

    # ============================================================================= #
    # RESET ROTATE MODE                                                             #
    # ============================================================================= #
    @staticmethod
    def reset_rotate_mode(mode):
        cmd.manipRotateContext(ROTATE, e=True, mode=mode)

    # ============================================================================= #
    # RESET SCALE MODE                                                              #
    # ============================================================================= #
    @staticmethod
    def reset_scale_mode(mode):
        cmd.manipScaleContext(SCALE, e=True, mode=mode)


