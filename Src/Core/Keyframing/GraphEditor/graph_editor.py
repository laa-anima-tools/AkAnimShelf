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
import maya.mel as mel

class GraphEditor(object):

    def __init__(self):
        pass

    # # ============================================================================= #
    # # SLICE CURVES                                                                  #
    # # ============================================================================= #
    # def smart_key(self):
    #     print('smart key')
    #     try:
    #         mel.eval('ackSliceCurves;')
    #     except:
    #         print('No object is selected.')

    # ============================================================================= #
    # SLICE CURVES                                                                  #
    # ============================================================================= #
    def smart_key(self):
        connection = cmd.editor('graphEditor1GraphEd', query=True, mainListConnection=True)
        print connection

