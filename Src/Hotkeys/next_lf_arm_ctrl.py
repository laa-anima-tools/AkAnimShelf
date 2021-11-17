# -----------------------------------------------------------------------------
# SCRIPT: prevlfArmCtrls
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Previous LF Arm Control
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def prevlfArmCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores the Spine Controls Names
    lfArmControls = [charNsp + ':l_upperArmFK_000_ctrl',
                     charNsp + ':l_lowerArmFK_000_ctrl',
                     charNsp + ':l_handFK_000_ctrl',
                     charNsp + ':l_armIK_000_ctrl',
                     charNsp + ':l_elbowIK_000_ctrl',
                     charNsp + ':l_armRootIK_000_ctrl',
                     charNsp + ':l_shoulder_000_ctrl']

    lfArmHuds = [charNsp + ' | RT FK ARM',
                 charNsp + ' | RT FK ELBOW',
                 charNsp + ' | RT FK WRIST',
                 charNsp + ' | RT IK ARM',
                 charNsp + ' | RT IK ELBOW',
                 charNsp + ' | RT IK ROOT',
                 charNsp + ' | RT SHOULDER']

    lfArmSwitch = cmds.getAttr(charNsp + ':l_armSwitch_000_ctrl.fk_ik')

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # RT FK Arm Controls
    if not lfArmSwitch:

        # Select the Controls
        if (len(selectedControls) == 1):

            if (selectedControls[0] == lfArmControls[0]):
                cmds.select(lfArmControls[1])
                return lfArmHuds[1]
            elif (selectedControls[0] == lfArmControls[1]):
                cmds.select(lfArmControls[2])
                return lfArmHuds[2]
            elif (selectedControls[0] == lfArmControls[2]):
                cmds.select(lfArmControls[6])
                return lfArmHuds[6]
            else:
                cmds.select(lfArmControls[0])
                return lfArmHuds[0]
        else:
            cmds.select(lfArmControls[0])
            return lfArmHuds[0]



    # RT IK Arm Controls
    else:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == lfArmControls[3]):
                cmds.select(lfArmControls[4])
                return lfArmHuds[4]
            elif (selectedControls[0] == lfArmControls[4]):
                cmds.select(lfArmControls[6])
                return lfArmHuds[6]
            elif (selectedControls[0] == lfArmControls[6]):
                cmds.select(lfArmControls[5])
                return lfArmHuds[5]
            else:
                cmds.select(lfArmControls[3])
                return lfArmHuds[3]
        else:
            cmds.select(lfArmControls[3])
            return lfArmHuds[3]


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='prevlfArmCtrl()', ev='PreFileNewOrOpened')
