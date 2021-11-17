# -----------------------------------------------------------------------------
# SCRIPT: nextRtLegCtrls
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Switch Between All RT Leg Controls
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def nextRtLegCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores the Spine Controls Names
    rtLegControls = [charNsp + ':r_legIK_000_ctrl',
                     charNsp + ':r_kneeIK_000_ctrl',
                     charNsp + ':r_legRootIK_000_ctrl',
                     charNsp + ':r_upperLegFK_000_ctrl',
                     charNsp + ':r_lowerLegFK_000_ctrl',
                     charNsp + ':r_footFK_000_ctrl',
                     charNsp + ':r_toesFK_000_ctrl']

    rtLegHuds = [charNsp.upper() + ' | RT IK FOOT',
                 charNsp.upper() + ' | RT IK KNEE',
                 charNsp.upper() + ' | RT IK KNEE STRETCH',
                 charNsp.upper() + ' | RT FK LEG',
                 charNsp.upper() + ' | RT FK KNEE',
                 charNsp.upper() + ' | RT FK FOOT',
                 charNsp.upper() + ' | RT FK TOE']

    rtLegSwitch = cmds.getAttr(charNsp + ':r_legSwitch_000_ctrl.fk_ik')

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # RT IK Leg Controls
    if rtLegSwitch:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == rtLegControls[0]):
                cmds.select(rtLegControls[1])
                return rtLegHuds[1]
            elif (selectedControls[0] == rtLegControls[1]):
                cmds.select(rtLegControls[2])
                return rtLegHuds[2]
            elif (selectedControls[0] == rtLegControls[2]):
                cmds.select(rtLegControls[6])
                return rtLegHuds[6]
            else:
                cmds.select(rtLegControls[0])
                return rtLegHuds[0]
        else:
            cmds.select(rtLegControls[0])
            return rtLegHuds[0]




    # RT FK Leg Controls
    else:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == rtLegControls[3]):
                cmds.select(rtLegControls[4])
                return rtLegHuds[4]
            elif (selectedControls[0] == rtLegControls[4]):
                cmds.select(rtLegControls[5])
                return rtLegHuds[5]
            elif (selectedControls[0] == rtLegControls[5]):
                cmds.select(rtLegControls[6])
                return rtLegHuds[6]
            else:
                cmds.select(rtLegControls[3])
                return rtLegHuds[3]
        else:
            cmds.select(rtLegControls[3])
            return rtLegHuds[3]


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='nextRtLegCtrl()', ev='PreFileNewOrOpened')
