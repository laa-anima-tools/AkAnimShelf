# -----------------------------------------------------------------------------
# SCRIPT: nextEyeCtrl
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Next Eye Control
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def nextEyeCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores Eyes Controls Names
    eyeControls = [charNsp + ':' + charPrefix + '_ac_cn_lookAt',
                   charNsp + ':' + charPrefix + '_ac_rt_lookAt',
                   charNsp + ':' + charPrefix + '_ac_lf_lookAt']

    eyeHuds = [charNsp.upper() + ' | EYES MASTER',
               charNsp.upper() + ' | RT EYE',
               charNsp.upper() + ' | LF EYE']

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # Select the Controls
    if (len(selectedControls) != 0):
        if (selectedControls[0] == eyeControls[0]):
            cmds.select(eyeControls[1])
            return eyeHuds[1]
        elif (selectedControls[0] == eyeControls[1]):
            cmds.select(eyeControls[2])
            return eyeHuds[2]
        else:
            cmds.select(eyeControls[0])
            return eyeHuds[0]
    else:
        cmds.select(eyeControls[0])
        return eyeHuds[0]


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='nextEyeCtrl()', ev='PreFileNewOrOpened')
