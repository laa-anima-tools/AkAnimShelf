# -----------------------------------------------------------------------------
# SCRIPT: prevRtArmCtrls
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Previous RT Arm Control
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def prevRtArmCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores the Spine Controls Names
    rtArmControls = [charNsp + ':r_upperArmFK_000_ctrl',
                     charNsp + ':r_lowerArmFK_000_ctrl',
                     charNsp + ':r_handFK_000_ctrl',
                     charNsp + ':r_armIK_000_ctrl',
                     charNsp + ':r_elbowIK_000_ctrl',
                     charNsp + ':r_armRootIK_000_ctrl',
                     charNsp + ':r_shoulder_000_ctrl']

    rtArmHuds = [charNsp + ' | RT FK ARM',
                 charNsp + ' | RT FK ELBOW',
                 charNsp + ' | RT FK WRIST',
                 charNsp + ' | RT IK ARM',
                 charNsp + ' | RT IK ELBOW',
                 charNsp + ' | RT IK ROOT',
                 charNsp + ' | RT SHOULDER']

    rtArmSwitch = cmds.getAttr(charNsp + ':r_armSwitch_000_ctrl.fk_ik')

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # RT FK Arm Controls
    if not rtArmSwitch:

        # Select the Controls
        if (len(selectedControls) == 1):

            if (selectedControls[0] == rtArmControls[0]):
                cmds.select(rtArmControls[1])
                return rtArmHuds[1]
            elif (selectedControls[0] == rtArmControls[1]):
                cmds.select(rtArmControls[2])
                return rtArmHuds[2]
            elif (selectedControls[0] == rtArmControls[2]):
                cmds.select(rtArmControls[6])
                return rtArmHuds[6]
            else:
                cmds.select(rtArmControls[0])
                return rtArmHuds[0]
        else:
            cmds.select(rtArmControls[0])
            return rtArmHuds[0]



    # RT IK Arm Controls
    else:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == rtArmControls[3]):
                cmds.select(rtArmControls[4])
                return rtArmHuds[4]
            elif (selectedControls[0] == rtArmControls[4]):
                cmds.select(rtArmControls[6])
                return rtArmHuds[6]
            elif (selectedControls[0] == rtArmControls[6]):
                cmds.select(rtArmControls[5])
                return rtArmHuds[5]
            else:
                cmds.select(rtArmControls[3])
                return rtArmHuds[3]
        else:
            cmds.select(rtArmControls[3])
            return rtArmHuds[3]


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='prevRtArmCtrl()', ev='PreFileNewOrOpened')
