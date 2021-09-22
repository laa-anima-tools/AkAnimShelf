"""
=============================================================================
MODULE: graph_editor.py
-----------------------------------------------------------------------------
Add extra functionality to Maya's graph editor. This module must be used by the
trigger module, SHOULD NOT BE USED DIRECTLY.
-----------------------------------------------------------------------------
AUTHOR:   Leandro Adeodato
VERSION:  v1.0.0 | Maya 2018 | Python 2
=============================================================================
"""
import maya.cmds as cmd
from AkAnimShelf.Src.Utils import navigation_utils

MOVE, ROTATE, SCALE = 'Move', 'Rotate', 'Scale'
LOCAL, WORLD, NORMAL, GIMBAL, PARENT, COMPONENT = 'Local', 'World', 'Normal', 'Gimbal', 'Parent', 'Component'
TX, TY, TZ, RX, RY, RZ, SX, SY, SZ = 'tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'
NAME, INDEX = 0, 1


class TransformModes(object):

    def __init__(self):
        self._navigation_utils = navigation_utils.NavigationUtils()

        self._transform_modes = {
            MOVE: [[LOCAL, 0], [WORLD, 2], [NORMAL, 3]],
            ROTATE: [[LOCAL, 0], [WORLD, 1], [GIMBAL, 2]],
            SCALE: [[LOCAL, 0], [WORLD, 2]]
        }
        self._transform_attrs = {
            MOVE: [TX, TY, TZ],
            ROTATE: [RX, RY, RZ],
            SCALE: [SX, SY, SZ]
        }

    # ============================================================================= #
    # TOGGLE MOVE MODE                                                              #
    # ============================================================================= #
    def toggle_move_mode(self):
        current_mode = self._navigation_utils.get_current_move_mode()
        self._navigation_utils.reset_rotate_mode(self._transform_modes[ROTATE][-1][INDEX])
        self._navigation_utils.reset_scale_mode(self._transform_modes[SCALE][-1][INDEX])
        cmd.setToolTo(MOVE)

        for i, mode in enumerate(self._transform_modes[MOVE]):
            if not current_mode == self._transform_modes[MOVE][-1][INDEX]:
                if current_mode == self._transform_modes[MOVE][i][INDEX]:
                    self._navigation_utils.set_current_move_mode(self._transform_modes[MOVE][i + 1][INDEX])
                    return self._transform_modes[MOVE][i + 1][NAME]

        self._navigation_utils.set_current_move_mode(self._transform_modes[MOVE][0][INDEX])
        return self._transform_modes[MOVE][0][NAME]

    # ============================================================================= #
    # TOGGLE ROTATE MODE                                                            #
    # ============================================================================= #
    def toggle_rotate_mode(self):
        current_mode = self._navigation_utils.get_current_rotate_mode()
        self._navigation_utils.reset_move_mode(self._transform_modes[ROTATE][-1][INDEX])
        self._navigation_utils.reset_scale_mode(self._transform_modes[SCALE][-1][INDEX])
        cmd.setToolTo(ROTATE)

        for i, mode in enumerate(self._transform_modes[ROTATE]):
            if not current_mode == self._transform_modes[ROTATE][-1][INDEX]:
                if current_mode == self._transform_modes[ROTATE][i][INDEX]:
                    self._navigation_utils.set_current_rotate_mode(self._transform_modes[ROTATE][i + 1][INDEX])
                    return self._transform_modes[ROTATE][i + 1][NAME]

        self._navigation_utils.set_current_rotate_mode(self._transform_modes[ROTATE][0][INDEX])
        return self._transform_modes[ROTATE][0][NAME]

    # ============================================================================= #
    # TOGGLE SCALE MODE                                                             #
    # ============================================================================= #
    def toggle_scale_mode(self):
        current_mode = self._navigation_utils.get_current_scale_mode()
        self._navigation_utils.reset_move_mode(self._transform_modes[MOVE][-1][INDEX])
        self._navigation_utils.reset_rotate_mode(self._transform_modes[ROTATE][-1][INDEX])
        cmd.setToolTo(SCALE)

        for i, mode in enumerate(self._transform_modes[SCALE]):
            if not current_mode == self._transform_modes[SCALE][-1][INDEX]:
                if current_mode == self._transform_modes[SCALE][i][INDEX]:
                    self._navigation_utils.set_current_scale_mode(self._transform_modes[SCALE][i + 1][INDEX])
                    return self._transform_modes[SCALE][i + 1][NAME]

        self._navigation_utils.set_current_scale_mode(self._transform_modes[SCALE][0][INDEX])
        return self._transform_modes[SCALE][0][NAME]

