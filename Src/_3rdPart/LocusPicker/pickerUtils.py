# Embedded file name: C:/Users/hgkim/Documents/maya/2016/pythons\LocusPicker\pickerUtils.py
try:
    from locusPickerUI import LocusPickerUI
except:
    from LocusPicker.locusPickerUI import LocusPickerUI

try:
    from locusPickerLauncherUI import LocusPickerLauncherUI
except:
    from LocusPicker.locusPickerLauncherUI import LocusPickerLauncherUI

from decorator import timestamp
import re
import maya.cmds as mc

def syncVisToggle(target, name):
    win = LocusPickerLauncherUI.windowObj()
    if not win:
        win = LocusPickerUI.windowObj()
    if not win:
        return
    target = target.split('|')[-1].split(':')[-1]
    scene = win.tabWidget.currentScene()
    for item in scene.findVisToggleItem(target):
        index = [ k for k, v in item.states.items() if v.name == name ]
        if index:
            item.toggleVisibility(index[0], True)


def setVisToggleStates():
    win = LocusPickerLauncherUI.windowObj()
    if not win:
        win = LocusPickerUI.windowObj()
    if not win:
        return
    scene = win.tabWidget.currentScene()
    if not scene:
        return
    ns = win.prefix()
    c = re.compile("^.+\\'\\(%ns%\\)(.+?)\\',.+$")
    items = scene.findVisToggleItem()
    for item in items:
        cmd = item.states.values()[0].cmd
        if cmd:
            ctl = c.match(cmd).group(1)
            curr = item.getCurrentIndex()
            if mc.objExists(ns + ctl) and mc.attributeQuery('ikfk_switch', ex=1, n=ns + ctl):
                val = int(mc.getAttr(ns + ctl + '.ikfk_switch'))
                if curr != val:
                    item.toggleVisibility(val, True)