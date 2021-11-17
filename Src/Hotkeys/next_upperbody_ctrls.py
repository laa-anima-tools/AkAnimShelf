# -----------------------------------------------------------------------------
# SCRIPT: nextUpperBodyCtrls
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Switch Between All UpperBody Controls
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def nextUpperBodyCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores the Spine Controls Names
    spineControls = [charNsp + ':x_cog_000_ctrl',
                     charNsp + ':x_pelvis_000_ctrl',
                     charNsp + ':x_spineFK_000_ctrl',
                     charNsp + ':x_spineFK_001_ctrl',
                     charNsp + ':x_spineFK_002_ctrl',
                     charNsp + ':x_spineIK_004_ctrl']

    spineHuds = [charNsp.upper() + ' | COG',
                 charNsp.upper() + ' | PELVIS',
                 charNsp.upper() + ' | SPINE',
                 charNsp.upper() + ' | STRETCH']

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # Select the Controls
    if (len(selectedControls) != 0):
        if (selectedControls[0] == spineControls[0]):
            cmds.select(spineControls[1])
            return spineHuds[1]
        elif (selectedControls[0] == spineControls[1]):
            cmds.select(spineControls[2], spineControls[3], spineControls[4])
            return spineHuds[2]
        elif (selectedControls[0] == spineControls[2] or
              selectedControls[0] == spineControls[3] or
              selectedControls[0] == spineControls[4]):
            cmds.select(spineControls[5])
            return spineHuds[3]
        else:
            cmds.select(spineControls[0])
            return spineHuds[0]
    else:
        cmds.select(spineControls[0])
        return spineHuds[0]


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='nextUpperBodyCtrl()',
                    ev='PreFileNewOrOpened')