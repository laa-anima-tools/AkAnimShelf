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
from AkAnimShelf.Src.Utils import info_utils


class HotkeysManager(object):

    def __init__(self):
        self._navigation_utils = navigation_utils.NavigationUtils()


    def get_current_hotkey_set(self):
        return cmd.hotkeySet(q=True, current=True)

    def set_current_hotkey_set(self, hotkey_set):
        cmd.hotkeySet(hotkey_set, current=True, e=True)


    def get_user_hotkey_sets(self):
        user_hotkeys = []
        all_hotkeys = cmd.hotkeySet(q=True, hotkeySetArray=True)
        for hotkey in all_hotkeys:
            if hotkey != 'Maya_Default':
                user_hotkeys.append(hotkey)

        return user_hotkeys


    def switch_hotkey_set(self):
        user_hotkeys = self.get_user_hotkey_sets()
        current_hotkey = self.get_current_hotkey_set()
        if len(user_hotkeys) <= 1:
            return

        for i, hotkey in enumerate(user_hotkeys):
            print i, hotkey
            if current_hotkey == user_hotkeys[-1]:
                self.set_current_hotkey_set(user_hotkeys[0])
                info_utils.show_message('Hotkey Set: {0}'.format(user_hotkeys[0]))
                return
            if current_hotkey == user_hotkeys[i]:
                self.set_current_hotkey_set(user_hotkeys[i+1])
                info_utils.show_message('Hotkey Set: {0}'.format(user_hotkeys[i+1]))
                return