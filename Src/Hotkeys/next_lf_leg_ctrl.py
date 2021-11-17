# -----------------------------------------------------------------------------
# SCRIPT: nextlfLegCtrls
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Switch Between All LF Leg Controls
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def nextlfLegCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores the Spine Controls Names
    lfLegControls = [charNsp + ':l_legIK_000_ctrl',
                     charNsp + ':l_kneeIK_000_ctrl',
                     charNsp + ':l_legRootIK_000_ctrl',
                     charNsp + ':l_upperLegFK_000_ctrl',
                     charNsp + ':l_lowerLegFK_000_ctrl',
                     charNsp + ':l_footFK_000_ctrl',
                     charNsp + ':l_toesFK_000_ctrl']

    lfLegHuds = [charNsp.upper() + ' | LF IK FOOT',
                 charNsp.upper() + ' | LF IK KNEE',
                 charNsp.upper() + ' | LF IK KNEE STRETCH',
                 charNsp.upper() + ' | LF FK LEG',
                 charNsp.upper() + ' | LF FK KNEE',
                 charNsp.upper() + ' | LF FK FOOT',
                 charNsp.upper() + ' | LF FK TOE']

    lfLegSwitch = cmds.getAttr(charNsp + ':l_legSwitch_000_ctrl.fk_ik')

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # RT IK Leg Controls
    if lfLegSwitch:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == lfLegControls[0]):
                cmds.select(lfLegControls[1])
                return lfLegHuds[1]
            elif (selectedControls[0] == lfLegControls[1]):
                cmds.select(lfLegControls[2])
                return lfLegHuds[2]
            elif (selectedControls[0] == lfLegControls[2]):
                cmds.select(lfLegControls[6])
                return lfLegHuds[6]
            else:
                cmds.select(lfLegControls[0])
                return lfLegHuds[0]
        else:
            cmds.select(lfLegControls[0])
            return lfLegHuds[0]




    # RT FK Leg Controls
    else:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == lfLegControls[3]):
                cmds.select(lfLegControls[4])
                return lfLegHuds[4]
            elif (selectedControls[0] == lfLegControls[4]):
                cmds.select(lfLegControls[5])
                return lfLegHuds[5]
            elif (selectedControls[0] == lfLegControls[5]):
                cmds.select(lfLegControls[6])
                return lfLegHuds[6]
            else:
                cmds.select(lfLegControls[3])
                return lfLegHuds[3]
        else:
            cmds.select(lfLegControls[3])
            return lfLegHuds[3]


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='nextlfLegCtrl()', ev='PreFileNewOrOpened')
