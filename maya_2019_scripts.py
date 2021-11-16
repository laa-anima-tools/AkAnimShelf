# ============================================================================= #
# TOGGLE HOTKEY SET                                                             #
# ============================================================================= #
if cmds.hotkeySet(q=True, cu=True) == 'Maya_Default':
    cmds.hotkeySet('AS_HotkeySet', e=True, cu=True)
    cmds.inViewMessage(amg='HOTKEY SET: AS_HotkeySet', pos='topLeft', fade=True)
else:
    cmds.hotkeySet('Maya_Default', e=True, cu=True)
    cmds.inViewMessage(amg='HOTKEY SET: Maya_Default', pos='topLeft', fade=True)

# ============================================================================= #
# SET CHAR NAMESPACE                                                            #
# ============================================================================= #
import maya.cmds as cmds

def listAllNsp():
    ctrls_list = cmds.ls('*:*_ac_cn_upperbody')
    chars_list = []

    if not ctrls_list:
        return chars_list
    else:
        for ctrl in ctrls_list:
            char_nsp = ctrl.split(':')[0]
            ctrl_name = ctrl.split(':')[-1]
            char_prefix = ctrl_name.split('_')[0]
            chars_list.append(char_nsp + ':' + char_prefix)

    print char_nsp, ctrl_name, char_prefix

    return chars_list

def setCurrentNsp(*args):
    global charPrefix
    global charNsp

    existingChar = list(listAllNsp())

    try:
        for i, elmt in enumerate(existingChar):
            print charPrefix, elmt
            if (charPrefix == elmt.split(':')[0]):
                print elmt
                charNsp = existingChar[i + 1].split(':')[0]
                charPrefix = existingChar[i + 1].split(':')[-1]
                return charPrefix.upper()
            else:
                charNsp = existingChar[0].split(':')[0]
                charPrefix = existingChar[0].split(':')[-1]
                return charPrefix.upper()


    except:
        charNsp = existingChar[0].split(':')[0]
        charPrefix = existingChar[0].split(':')[-1]
        return charPrefix.upper()


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='setCurrentNsp()', ev='PreFileNewOrOpened')

# -----------------------------------------------------------------------------
# SCRIPT: prevUpperBodyCtrls
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Previous Upper Body Control
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def prevUpperBodyCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores the Spine Controls Names
    spineControls = [charNsp + ':' + charPrefix + '_ac_cn_upperbody',
                     charNsp + ':' + charPrefix + '_ac_cn_spineFK1',
                     charNsp + ':' + charPrefix + '_ac_cn_spineFK2',
                     charNsp + ':' + charPrefix + '_ac_cn_spineFK3',
                     charNsp + ':' + charPrefix + '_ac_cn_chest',
                     charNsp + ':' + charPrefix + '_ac_cn_neck',
                     charNsp + ':' + charPrefix + '_ac_cn_head']

    spineHuds = [charNsp.upper() + ' | ROOT',
                 charNsp.upper() + ' | SPINE',
                 charNsp.upper() + ' | NECK',
                 charNsp.upper() + ' | HEAD']

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # Select the Controls
    if (len(selectedControls) != 0):
        if (selectedControls[0] == spineControls[6]):
            cmds.select(spineControls[5])
            return spineHuds[2]
        elif (selectedControls[0] == spineControls[5]):
            cmds.select(spineControls[1], spineControls[2], spineControls[3], spineControls[4])
            return spineHuds[1]
        elif (selectedControls[0] == spineControls[1] or selectedControls[0] == spineControls[2] or selectedControls[
            0] == spineControls[3] or selectedControls[0] == spineControls[4]):
            cmds.select(spineControls[0])
            return spineHuds[0]
        else:
            cmds.select(spineControls[6])
            return spineHuds[3]
    else:
        cmds.select(spineControls[6])
        return spineHuds[3]


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='prevUpperBodyCtrl()',
                    ev='PreFileNewOrOpened')

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
    spineControls = [charNsp + ':' + charPrefix + '_ac_cn_upperbody',
                     charNsp + ':' + charPrefix + '_ac_cn_spineFK1',
                     charNsp + ':' + charPrefix + '_ac_cn_spineFK2',
                     charNsp + ':' + charPrefix + '_ac_cn_spineFK3',
                     charNsp + ':' + charPrefix + '_ac_cn_chest',
                     charNsp + ':' + charPrefix + '_ac_cn_neck',
                     charNsp + ':' + charPrefix + '_ac_cn_head']

    spineHuds = [charNsp.upper() + ' | ROOT',
                 charNsp.upper() + ' | SPINE',
                 charNsp.upper() + ' | NECK',
                 charNsp.upper() + ' | HEAD']

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # Select the Controls
    if (len(selectedControls) != 0):
        if (selectedControls[0] == spineControls[0]):
            cmds.select(spineControls[1], spineControls[2], spineControls[3], spineControls[4])
            return spineHuds[1]
        elif (selectedControls[0] == spineControls[1] or selectedControls[0] == spineControls[2] or selectedControls[
            0] == spineControls[3] or selectedControls[0] == spineControls[4]):
            cmds.select(spineControls[5])
            return spineHuds[2]
        elif (selectedControls[0] == spineControls[5]):
            cmds.select(spineControls[6])
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
    rtArmControls = [charNsp + ':' + charPrefix + '_ac_rt_shoulderFK',
                     charNsp + ':' + charPrefix + '_ac_rt_elbowFK',
                     charNsp + ':' + charPrefix + '_ac_rt_handFK',
                     charNsp + ':' + charPrefix + '_ac_rt_handIK',
                     charNsp + ':' + charPrefix + '_ac_rt_armPole',
                     charNsp + ':' + charPrefix + '_ac_rt_clavicle']

    rtArmHuds = [charNsp + ' | RT FK ARM',
                 charNsp + ' | RT FK ELBOW',
                 charNsp + ' | RT FK WRIST',
                 charNsp + ' | RT IK ARM',
                 charNsp + ' | RT IK ELBOW',
                 charNsp + ' | RT SHOULDER']

    rtArmSwitch = cmds.getAttr(charNsp + ':' + charPrefix + '_ac_rt_arm_settings.ik_arm')

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # RT FK Arm Controls
    if not rtArmSwitch:

        # Select the Controls
        if (len(selectedControls) == 1):

            if (selectedControls[0] == rtArmControls[1]):
                cmds.select(rtArmControls[0])
                return rtArmHuds[0]
            elif (selectedControls[0] == rtArmControls[2]):
                cmds.select(rtArmControls[1])
                return rtArmHuds[1]
            elif (selectedControls[0] == rtArmControls[5]):
                cmds.select(rtArmControls[2])
                return rtArmHuds[2]
            else:
                cmds.select(rtArmControls[5])
                return rtArmHuds[5]
        else:
            cmds.select(rtArmControls[5])
            return rtArmHuds[5]



    # RT IK Arm Controls
    else:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == rtArmControls[5]):
                cmds.select(rtArmControls[4])
                return rtArmHuds[4]
            elif (selectedControls[0] == rtArmControls[4]):
                cmds.select(rtArmControls[3])
                return rtArmHuds[3]
            else:
                cmds.select(rtArmControls[5])
                return rtArmHuds[5]
        else:
            cmds.select(rtArmControls[5])
            return rtArmHuds[5]


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='prevRtArmCtrl()', ev='PreFileNewOrOpened')

# -----------------------------------------------------------------------------
# SCRIPT: nextRtArmCtrls
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Next RT Arm Control
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def nextRtArmCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores the Spine Controls Names
    rtArmControls = [charNsp + ':' + charPrefix + '_ac_rt_shoulderFK',
                     charNsp + ':' + charPrefix + '_ac_rt_elbowFK',
                     charNsp + ':' + charPrefix + '_ac_rt_handFK',
                     charNsp + ':' + charPrefix + '_ac_rt_handIK',
                     charNsp + ':' + charPrefix + '_ac_rt_armPole',
                     charNsp + ':' + charPrefix + '_ac_rt_clavicle']

    rtArmHuds = [charNsp + ' | RT FK ARM',
                 charNsp + ' | RT FK ELBOW',
                 charNsp + ' | RT FK WRIST',
                 charNsp + ' | RT IK ARM',
                 charNsp + ' | RT IK ELBOW',
                 charNsp + ' | RT SHOULDER']

    rtArmSwitch = cmds.getAttr(charNsp + ':' + charPrefix + '_ac_rt_arm_settings.ik_arm')

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
                cmds.select(rtArmControls[5])
                return rtArmHuds[5]
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

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='nextRtArmCtrl()', ev='PreFileNewOrOpened')

# -----------------------------------------------------------------------------
# SCRIPT: prevLfArmCtrls
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Previous LF Arm Control
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def prevLfArmCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores the Spine Controls Names
    lfArmControls = [charNsp + ':' + charPrefix + '_ac_lf_shoulderFK',
                     charNsp + ':' + charPrefix + '_ac_lf_elbowFK',
                     charNsp + ':' + charPrefix + '_ac_lf_handFK',
                     charNsp + ':' + charPrefix + '_ac_lf_handIK',
                     charNsp + ':' + charPrefix + '_ac_lf_armPole',
                     charNsp + ':' + charPrefix + '_ac_lf_clavicle']

    lfArmHuds = [charNsp + ' | LF FK ARM',
                 charNsp + ' | LF FK ELBOW',
                 charNsp + ' | LF FK WRIST',
                 charNsp + ' | LF IK ARM',
                 charNsp + ' | LF IK ELBOW',
                 charNsp + ' | LF SHOULDER']

    lfArmSwitch = cmds.getAttr(charNsp + ':' + charPrefix + '_ac_lf_arm_settings.ik_arm')

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # LF FK Arm Controls
    if not lfArmSwitch:

        # Select the Controls
        if (len(selectedControls) == 1):

            if (selectedControls[0] == lfArmControls[1]):
                cmds.select(lfArmControls[0])
                return lfArmHuds[0]
            elif (selectedControls[0] == lfArmControls[2]):
                cmds.select(lfArmControls[1])
                return lfArmHuds[1]
            elif (selectedControls[0] == lfArmControls[5]):
                cmds.select(lfArmControls[2])
                return lfArmHuds[2]
            else:
                cmds.select(lfArmControls[5])
                return lfArmHuds[5]
        else:
            cmds.select(lfArmControls[5])
            return lfArmHuds[5]


    # LF IK Arm Controls
    else:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == lfArmControls[5]):
                cmds.select(lfArmControls[4])
                return lfArmHuds[4]
            elif (selectedControls[0] == lfArmControls[4]):
                cmds.select(lfArmControls[3])
                return lfArmHuds[3]
            else:
                cmds.select(lfArmControls[5])
                return lfArmHuds[5]
        else:
            cmds.select(lfArmControls[5])
            return lfArmHuds[5]


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='prevLfArmCtrl()', ev='PreFileNewOrOpened')

# -----------------------------------------------------------------------------
# SCRIPT: nextLfArmCtrls
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Next LF Arm Control
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def nextLfArmCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores the Spine Controls Names
    rtArmControls = [charNsp + ':' + charPrefix + '_ac_lf_shoulderFK',
                     charNsp + ':' + charPrefix + '_ac_lf_elbowFK',
                     charNsp + ':' + charPrefix + '_ac_lf_handFK',
                     charNsp + ':' + charPrefix + '_ac_lf_handIK',
                     charNsp + ':' + charPrefix + '_ac_lf_armPole',
                     charNsp + ':' + charPrefix + '_ac_lf_clavicle']

    rtArmHuds = [charNsp + ' | LF FK ARM',
                 charNsp + ' | LF FK ELBOW',
                 charNsp + ' | LF FK WRIST',
                 charNsp + ' | LF IK ARM',
                 charNsp + ' | LF IK ELBOW',
                 charNsp + ' | LF SHOULDER']

    rtArmSwitch = cmds.getAttr(charNsp + ':' + charPrefix + '_ac_lf_arm_settings.ik_arm')

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # LF FK Arm Controls
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
                cmds.select(rtArmControls[5])
                return rtArmHuds[5]
            else:
                cmds.select(rtArmControls[0])
                return rtArmHuds[0]
        else:
            cmds.select(rtArmControls[0])
            return rtArmHuds[0]



    # LF IK Arm Controls
    else:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == rtArmControls[3]):
                cmds.select(rtArmControls[4])
                return rtArmHuds[4]
            elif (selectedControls[0] == rtArmControls[4]):
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

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='nextLfArmCtrl()', ev='PreFileNewOrOpened')

# -----------------------------------------------------------------------------
# SCRIPT: prevRtLegCtrl
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Prev RT Leg Controls
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def prevRtLegCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores the Spine Controls Names
    rtLegControls = [charNsp + ':' + charPrefix + '_ac_rt_footIK',
                     charNsp + ':' + charPrefix + '_ac_rt_legPole',
                     charNsp + ':' + charPrefix + '_ac_rt_kneeIK',
                     charNsp + ':' + charPrefix + '_ac_rt_hipFK',
                     charNsp + ':' + charPrefix + '_ac_rt_kneeFK',
                     charNsp + ':' + charPrefix + '_ac_rt_footFK',
                     charNsp + ':' + charPrefix + '_ac_rt_toe']

    rtLegHuds = [charNsp.upper() + ' | RT IK FOOT',
                 charNsp.upper() + ' | RT IK KNEE',
                 charNsp.upper() + ' | RT IK KNEE STRETCH',
                 charNsp.upper() + ' | RT FK LEG',
                 charNsp.upper() + ' | RT FK KNEE',
                 charNsp.upper() + ' | RT FK FOOT',
                 charNsp.upper() + ' | RT FK TOE']

    rtLegSwitch = cmds.getAttr(charNsp + ':' + charPrefix + '_ac_rt_leg_settings.ik_leg')

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # RT IK Leg Controls
    if rtLegSwitch:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == rtLegControls[6]):
                cmds.select(rtLegControls[2])
                return rtLegHuds[2]
            elif (selectedControls[0] == rtLegControls[2]):
                cmds.select(rtLegControls[1])
                return rtLegHuds[1]
            elif (selectedControls[0] == rtLegControls[1]):
                cmds.select(rtLegControls[0])
                return rtLegHuds[0]
            else:
                cmds.select(rtLegControls[6])
                return rtLegHuds[6]
        else:
            cmds.select(rtLegControls[6])
            return rtLegHuds[6]




    # RT FK Leg Controls
    else:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == rtLegControls[6]):
                cmds.select(rtLegControls[5])
                return rtLegHuds[4]
            elif (selectedControls[0] == rtLegControls[5]):
                cmds.select(rtLegControls[4])
                return rtLegHuds[4]
            elif (selectedControls[0] == rtLegControls[4]):
                cmds.select(rtLegControls[3])
                return rtLegHuds[3]
            else:
                cmds.select(rtLegControls[6])
                return rtLegHuds[6]
        else:
            cmds.select(rtLegControls[6])
            return rtLegHuds[6]


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='prevRtLegCtrl()', ev='PreFileNewOrOpened')

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
    rtLegControls = [charNsp + ':' + charPrefix + '_ac_rt_footIK',
                     charNsp + ':' + charPrefix + '_ac_rt_legPole',
                     charNsp + ':' + charPrefix + '_ac_rt_kneeIK',
                     charNsp + ':' + charPrefix + '_ac_rt_hipFK',
                     charNsp + ':' + charPrefix + '_ac_rt_kneeFK',
                     charNsp + ':' + charPrefix + '_ac_rt_footFK',
                     charNsp + ':' + charPrefix + '_ac_rt_toe']

    rtLegHuds = [charNsp.upper() + ' | RT IK FOOT',
                 charNsp.upper() + ' | RT IK KNEE',
                 charNsp.upper() + ' | RT IK KNEE STRETCH',
                 charNsp.upper() + ' | RT FK LEG',
                 charNsp.upper() + ' | RT FK KNEE',
                 charNsp.upper() + ' | RT FK FOOT',
                 charNsp.upper() + ' | RT FK TOE']

    rtLegSwitch = cmds.getAttr(charNsp + ':' + charPrefix + '_ac_rt_leg_settings.ik_leg')

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

# -----------------------------------------------------------------------------
# SCRIPT: prevLfLegCtrl
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Prev LF Leg Controls
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def prevLfLegCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores the Spine Controls Names
    lfLegControls = [charNsp + ':' + charPrefix + '_ac_lf_footIK',
                     charNsp + ':' + charPrefix + '_ac_lf_legPole',
                     charNsp + ':' + charPrefix + '_ac_lf_kneeIK',
                     charNsp + ':' + charPrefix + '_ac_lf_hipFK',
                     charNsp + ':' + charPrefix + '_ac_lf_kneeFK',
                     charNsp + ':' + charPrefix + '_ac_lf_footFK',
                     charNsp + ':' + charPrefix + '_ac_lf_toe']

    lfLegHuds = [charNsp.upper() + ' | LF IK FOOT',
                 charNsp.upper() + ' | LF IK KNEE',
                 charNsp.upper() + ' | LF IK KNEE STRETCH',
                 charNsp.upper() + ' | LF FK LEG',
                 charNsp.upper() + ' | LF FK KNEE',
                 charNsp.upper() + ' | LF FK FOOT',
                 charNsp.upper() + ' | LF FK TOE']

    lfLegSwitch = cmds.getAttr(charNsp + ':' + charPrefix + '_ac_lf_leg_settings.ik_leg')

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # LF IK Leg Controls
    if lfLegSwitch:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == lfLegControls[6]):
                cmds.select(lfLegControls[2])
                return lfLegHuds[2]
            elif (selectedControls[0] == lfLegControls[2]):
                cmds.select(lfLegControls[1])
                return lfLegHuds[1]
            elif (selectedControls[0] == lfLegControls[1]):
                cmds.select(lfLegControls[0])
                return lfLegHuds[0]
            else:
                cmds.select(lfLegControls[6])
                return lfLegHuds[6]
        else:
            cmds.select(lfLegControls[6])
            return lfLegHuds[6]



    # LF FK Leg Controls
    else:

        # Select the Controls
        if (len(selectedControls) == 1):
            if (selectedControls[0] == lfLegControls[6]):
                cmds.select(lfLegControls[5])
                return lfLegHuds[4]
            elif (selectedControls[0] == lfLegControls[5]):
                cmds.select(lfLegControls[4])
                return lfLegHuds[4]
            elif (selectedControls[0] == lfLegControls[4]):
                cmds.select(lfLegControls[3])
                return lfLegHuds[3]
            else:
                cmds.select(lfLegControls[6])
                return lfLegHuds[6]
        else:
            cmds.select(lfLegControls[6])
            return lfLegHuds[6]


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='prevLfLegCtrl()', ev='PreFileNewOrOpened')

# -----------------------------------------------------------------------------
# SCRIPT: nextLfLegCtrls
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Switch Between All LF Leg Controls
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def nextLfLegCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # Stores the Spine Controls Names
    lfLegControls = [charNsp + ':' + charPrefix + '_ac_lf_footIK',
                     charNsp + ':' + charPrefix + '_ac_lf_legPole',
                     charNsp + ':' + charPrefix + '_ac_lf_kneeIK',
                     charNsp + ':' + charPrefix + '_ac_lf_hipFK',
                     charNsp + ':' + charPrefix + '_ac_lf_kneeFK',
                     charNsp + ':' + charPrefix + '_ac_lf_footFK',
                     charNsp + ':' + charPrefix + '_ac_lf_toe']

    lfLegHuds = [charNsp.upper() + ' | LF IK FOOT',
                 charNsp.upper() + ' | LF IK KNEE',
                 charNsp.upper() + ' | LF IK KNEE STRETCH',
                 charNsp.upper() + ' | LF FK LEG',
                 charNsp.upper() + ' | LF FK KNEE',
                 charNsp.upper() + ' | LF FK FOOT',
                 charNsp.upper() + ' | LF FK TOE']

    lfLegSwitch = cmds.getAttr(charNsp + ':' + charPrefix + '_ac_lf_leg_settings.ik_leg')

    # Gets All Selected Controls
    selectedControls = cmds.ls(sl=True)

    # LF IK Leg Controls
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



    # LF FK Leg Controls
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

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='nextLfLegCtrl()', ev='PreFileNewOrOpened')

# -----------------------------------------------------------------------------
# SCRIPT: prevEyeCtrl
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Prev Eye Control
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def prevEyeCtrl(*args):
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
        if (selectedControls[0] == eyeControls[2]):
            cmds.select(eyeControls[1])
            return eyeHuds[1]
        elif (selectedControls[0] == eyeControls[1]):
            cmds.select(eyeControls[0])
            return eyeHuds[0]
        else:
            cmds.select(eyeControls[2])
            return eyeHuds[2]
    else:
        cmds.select(eyeControls[2])
        return eyeHuds[2]


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='prevEyeCtrl()', ev='PreFileNewOrOpened')

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


# -----------------------------------------------------------------------------
# SCRIPT: selectBaseCtrl
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Base Control
# -----------------------------------------------------------------------------
import maya.cmds as cmds

def selectBaseCtrl (*args):

	# Check if a character is active
	if charNsp == None:
		cmds.warning('No Active Character')
		return

	# Stores the Spine Controls Names
	baseControl = charNsp + ':' + charPrefix + '_ac_cn_base'
	baseHud = charNsp.upper() + ' | MAIN'

	# Select the Control
	cmds.select(baseControl)
	return baseHud


# Shows HUDs on viewport
if (cmds.headsUpDisplay( 'HUDActiveChar', ex=True )):
	cmds.headsUpDisplay( 'HUDActiveChar', rem=True )

cmds.headsUpDisplay ('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='selectBaseCtrl()', ev='PreFileNewOrOpened')


# -----------------------------------------------------------------------------
# SCRIPT: selectBaseCtrl
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Base Control
# -----------------------------------------------------------------------------
import maya.cmds as cmds

def selectBaseCtrl (*args):

	# Check if a character is active
	if charNsp == None:
		cmds.warning('No Active Character')
		return

	# Stores the Spine Controls Names
	baseControl = charNsp + ':' + charPrefix + '_ac_cn_base'
	baseHud = charNsp.upper() + ' | MAIN'

	# Select the Control
	cmds.select(baseControl)
	return baseHud


# Shows HUDs on viewport
if (cmds.headsUpDisplay( 'HUDActiveChar', ex=True )):
	cmds.headsUpDisplay( 'HUDActiveChar', rem=True )

cmds.headsUpDisplay ('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='selectBaseCtrl()', ev='PreFileNewOrOpened')

# -----------------------------------------------------------------------------
# SCRIPT: prevMinorControls
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Prev Minor Control
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def prevMinorCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # ===== HAND CONTROLS =====================================================
    rtHandControls = [charNsp + ':' + charPrefix + '_ac_rt_index0', charNsp + ':' + charPrefix + '_ac_rt_index1',
                      charNsp + ':' + charPrefix + '_ac_rt_index2', charNsp + ':' + charPrefix + '_ac_rt_index3',
                      charNsp + ':' + charPrefix + '_ac_rt_middle0', charNsp + ':' + charPrefix + '_ac_rt_middle1',
                      charNsp + ':' + charPrefix + '_ac_rt_middle2', charNsp + ':' + charPrefix + '_ac_rt_middle3',
                      charNsp + ':' + charPrefix + '_ac_rt_ring0', charNsp + ':' + charPrefix + '_ac_rt_ring1',
                      charNsp + ':' + charPrefix + '_ac_rt_ring2', charNsp + ':' + charPrefix + '_ac_rt_ring3',
                      charNsp + ':' + charPrefix + '_ac_rt_pinkey0', charNsp + ':' + charPrefix + '_ac_rt_pinkey1',
                      charNsp + ':' + charPrefix + '_ac_rt_pinkey2', charNsp + ':' + charPrefix + '_ac_rt_pinkey3',
                      charNsp + ':' + charPrefix + '_ac_rt_thumb1', charNsp + ':' + charPrefix + '_ac_rt_thumb2',
                      charNsp + ':' + charPrefix + '_ac_rt_thumb3']

    lfHandControls = [charNsp + ':' + charPrefix + '_ac_lf_index0', charNsp + ':' + charPrefix + '_ac_lf_index1',
                      charNsp + ':' + charPrefix + '_ac_lf_index2', charNsp + ':' + charPrefix + '_ac_lf_index3',
                      charNsp + ':' + charPrefix + '_ac_lf_middle0', charNsp + ':' + charPrefix + '_ac_lf_middle1',
                      charNsp + ':' + charPrefix + '_ac_lf_middle2', charNsp + ':' + charPrefix + '_ac_lf_middle3',
                      charNsp + ':' + charPrefix + '_ac_lf_ring0', charNsp + ':' + charPrefix + '_ac_lf_ring1',
                      charNsp + ':' + charPrefix + '_ac_lf_ring2', charNsp + ':' + charPrefix + '_ac_lf_ring3',
                      charNsp + ':' + charPrefix + '_ac_lf_pinkey0', charNsp + ':' + charPrefix + '_ac_lf_pinkey1',
                      charNsp + ':' + charPrefix + '_ac_lf_pinkey2', charNsp + ':' + charPrefix + '_ac_lf_pinkey3',
                      charNsp + ':' + charPrefix + '_ac_lf_thumb1', charNsp + ':' + charPrefix + '_ac_lf_thumb2',
                      charNsp + ':' + charPrefix + '_ac_lf_thumb3']

    rtHandHud = charNsp.upper() + ' | RT HAND'
    lfHandHud = charNsp.upper() + ' | LF HAND'

    # ===== ROOT CHILD CONTROLS ===============================================
    rootChildControls = [charNsp + ':' + charPrefix + '_ac_cn_upperbody',
                         charNsp + ':' + charPrefix + '_ac_cn_pelvis']

    rootChildHuds = [charNsp.upper() + ' | ROOT',
                     charNsp.upper() + ' | PELVIS']

    # ===== SPINE CHILD CONTROLS ==============================================
    spineChildControls = [charNsp + ':' + charPrefix + '_ac_cn_spineFK1',
                          charNsp + ':' + charPrefix + '_ac_cn_spineFK2',
                          charNsp + ':' + charPrefix + '_ac_cn_spineFK3',
                          charNsp + ':' + charPrefix + '_ac_cn_chest']

    spineChildHuds = [charNsp.upper() + ' | SPINE BOT',
                      charNsp.upper() + ' | SPINE MID',
                      charNsp.upper() + ' | SPINE TOP',
                      charNsp.upper() + ' | IK SPINE']

    # ===== RT ARM CONTROLS ===================================================
    rtArmControls = [charNsp + ':' + charPrefix + '_ac_rt_shoulderFK',
                     charNsp + ':' + charPrefix + '_ac_rt_elbowFK',
                     charNsp + ':' + charPrefix + '_ac_rt_handFK',
                     charNsp + ':' + charPrefix + '_ac_rt_handIK',
                     charNsp + ':' + charPrefix + '_ac_rt_armPole',
                     charNsp + ':' + charPrefix + '_ac_rt_clavicle']

    rtArmBendControls = [charNsp + ':' + charPrefix + '_ac_rt_arm_bend',
                         charNsp + ':' + charPrefix + '_ac_rt_elbow_bend',
                         charNsp + ':' + charPrefix + '_ac_rt_forearm_bend']

    rtArmBendHuds = [charNsp.upper() + ' | RT ARM BEND',
                     charNsp.upper() + ' | RT ELBOW BEND',
                     charNsp.upper() + ' | RT FOREARM BEND']

    # ===== LF ARM CONTROLS ===================================================
    lfArmControls = [charNsp + ':' + charPrefix + '_ac_lf_shoulderFK',
                     charNsp + ':' + charPrefix + '_ac_lf_elbowFK',
                     charNsp + ':' + charPrefix + '_ac_lf_handFK',
                     charNsp + ':' + charPrefix + '_ac_lf_handIK',
                     charNsp + ':' + charPrefix + '_ac_lf_armPole',
                     charNsp + ':' + charPrefix + '_ac_lf_clavicle']

    lfArmBendControls = [charNsp + ':' + charPrefix + '_ac_lf_arm_bend',
                         charNsp + ':' + charPrefix + '_ac_lf_elbow_bend',
                         charNsp + ':' + charPrefix + '_ac_lf_forearm_bend']

    lfArmBendHuds = [charNsp.upper() + ' | LF ARM BEND',
                     charNsp.upper() + ' | LF ELBOW BEND',
                     charNsp.upper() + ' | LF FOREARM BEND']

    # ===== RT LEG CONTROLS ===================================================
    rtLegControls = [charNsp + ':' + charPrefix + '_ac_rt_footIK',
                     charNsp + ':' + charPrefix + '_ac_rt_legPole',
                     charNsp + ':' + charPrefix + '_ac_rt_kneeIK',
                     charNsp + ':' + charPrefix + '_ac_rt_hipFK',
                     charNsp + ':' + charPrefix + '_ac_rt_kneeFK',
                     charNsp + ':' + charPrefix + '_ac_rt_footFK',
                     charNsp + ':' + charPrefix + '_ac_rt_toe']

    rtLegBendControls = [charNsp + ':' + charPrefix + '_ac_rt_upleg_bend',
                         charNsp + ':' + charPrefix + '_ac_rt_knee_bend',
                         charNsp + ':' + charPrefix + '_ac_rt_lowleg_bend']

    rtLegBendHuds = [charNsp.upper() + ' | RT THIGH BEND',
                     charNsp.upper() + ' | RT KNEE BEND',
                     charNsp.upper() + ' | RT CALF BEND']

    # ===== LF LEG CONTROLS ===================================================
    lfLegControls = [charNsp + ':' + charPrefix + '_ac_lf_footIK',
                     charNsp + ':' + charPrefix + '_ac_lf_legPole',
                     charNsp + ':' + charPrefix + '_ac_lf_kneeIK',
                     charNsp + ':' + charPrefix + '_ac_lf_hipFK',
                     charNsp + ':' + charPrefix + '_ac_lf_kneeFK',
                     charNsp + ':' + charPrefix + '_ac_lf_footFK',
                     charNsp + ':' + charPrefix + '_ac_lf_toe']

    lfLegBendControls = [charNsp + ':' + charPrefix + '_ac_lf_upleg_bend',
                         charNsp + ':' + charPrefix + '_ac_lf_knee_bend',
                         charNsp + ':' + charPrefix + '_ac_lf_lowleg_bend']

    lfLegBendHuds = [charNsp.upper() + ' | LF THIGH BEND',
                     charNsp.upper() + ' | LF KNEE BEND',
                     charNsp.upper() + ' | LF CALF BEND']

    # ===== SELECT CONTROLS ===================================================
    selectedControls = cmds.ls(sl=True)

    if (len(selectedControls) == 0):
        for ctrl in rtHandControls:
            cmds.select(ctrl, add=True)
        return rtHandHud

    elif (len(selectedControls) == 1):

        # ===== ROOT ==========================================================
        if (selectedControls[0] == rootChildControls[0]):
            cmds.select(rootChildControls[1])
            return rootChildHuds[1]

        elif (selectedControls[0] == rootChildControls[1]):
            cmds.select(rootChildControls[0])
            return rootChildHuds[0]



        # ===== SPINE ==========================================================
        elif (selectedControls[0] == spineChildControls[3]):
            cmds.select(spineChildControls[2])
            return spineChildHuds[2]


        elif (selectedControls[0] == spineChildControls[2]):
            cmds.select(spineChildControls[1])
            return spineChildHuds[1]

        elif (selectedControls[0] == spineChildControls[1]):
            cmds.select(spineChildControls[0])
            return spineChildHuds[0]


        elif (selectedControls[0] == spineChildControls[0]):
            cmds.select(spineChildControls[3])
            return spineChildHuds[3]

        # ===== RT ARM BEND BOWS =============================================
        for ctrl in rtArmControls:
            if (selectedControls[0] == ctrl):
                cmds.select(rtArmBendControls[2])
                return rtArmBendHuds[2]

        if (selectedControls[0] == rtArmBendControls[2]):
            cmds.select(rtArmBendControls[1])
            return rtArmBendHuds[1]



        elif (selectedControls[0] == rtArmBendControls[1]):
            cmds.select(rtArmBendControls[0])
            return rtArmBendHuds[0]



        elif (selectedControls[0] == rtArmBendControls[0]):
            cmds.select(rtArmBendControls[2])
            return rtArmBendHuds[2]

        # ===== LF ARM BEND BOWS =============================================
        for ctrl in lfArmControls:
            if (selectedControls[0] == ctrl):
                cmds.select(lfArmBendControls[2])
                return lfArmBendHuds[2]

        if (selectedControls[0] == lfArmBendControls[2]):
            cmds.select(lfArmBendControls[1])
            return lfArmBendHuds[1]



        elif (selectedControls[0] == lfArmBendControls[1]):
            cmds.select(lfArmBendControls[0])
            return lfArmBendHuds[0]



        elif (selectedControls[0] == lfArmBendControls[0]):
            cmds.select(lfArmBendControls[2])
            return lfArmBendHuds[2]

        # ===== RT LEG BEND BOWS =============================================
        for ctrl in rtLegControls:
            if (selectedControls[0] == ctrl):
                cmds.select(rtLegBendControls[2])
                return rtLegBendHuds[2]

        if (selectedControls[0] == rtLegBendControls[2]):
            cmds.select(rtLegBendControls[1])
            return rtLegBendHuds[1]



        elif (selectedControls[0] == rtLegBendControls[1]):
            cmds.select(rtLegBendControls[0])
            return rtLegBendHuds[0]



        elif (selectedControls[0] == rtLegBendControls[0]):
            cmds.select(rtLegBendControls[2])
            return rtLegBendHuds[2]

        # ===== LF LEG BEND BOWS =============================================
        for ctrl in lfLegControls:
            if (selectedControls[0] == ctrl):
                cmds.select(lfLegBendControls[2])
                return lfLegBendHuds[2]

        if (selectedControls[0] == lfLegBendControls[2]):
            cmds.select(lfLegBendControls[1])
            return lfLegBendHuds[1]



        elif (selectedControls[0] == lfLegBendControls[1]):
            cmds.select(lfLegBendControls[0])
            return lfLegBendHuds[0]



        elif (selectedControls[0] == lfLegBendControls[0]):
            cmds.select(lfLegBendControls[2])
            return lfLegBendHuds[2]




    elif (len(selectedControls) > 1):

        # SPINE SELECTED > SWITCH TO SPINE BOT
        if (selectedControls[0] == spineChildControls[0] or selectedControls[0] == spineChildControls[1] or
                selectedControls[0] == spineChildControls[2] or selectedControls[0] == spineChildControls[3]):
            cmds.select(spineChildControls[3])
            return spineChildControls[3]

    # IN CASE ANY OTHER COMBINATION OF CONTROLS ARE SELECTED
    cmds.select(cl=True)
    for ctrl in rtHandControls:
        cmds.select(ctrl, add=True)
    return rtHandHud


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='prevMinorCtrl()', ev='PreFileNewOrOpened')

# -----------------------------------------------------------------------------
# SCRIPT: nextMinorControls
# AUTHOR: Leandro Adeodato
# -----------------------------------------------------------------------------
# Select Next Minor Control
# -----------------------------------------------------------------------------
import maya.cmds as cmds


def nextMinorCtrl(*args):
    # Check if a character is active
    if charNsp == None:
        cmds.warning('No Active Character')
        return

    # ===== HAND CONTROLS =====================================================
    rtHandControls = [charNsp + ':' + charPrefix + '_ac_rt_index0', charNsp + ':' + charPrefix + '_ac_rt_index1',
                      charNsp + ':' + charPrefix + '_ac_rt_index2', charNsp + ':' + charPrefix + '_ac_rt_index3',
                      charNsp + ':' + charPrefix + '_ac_rt_middle0', charNsp + ':' + charPrefix + '_ac_rt_middle1',
                      charNsp + ':' + charPrefix + '_ac_rt_middle2', charNsp + ':' + charPrefix + '_ac_rt_middle3',
                      charNsp + ':' + charPrefix + '_ac_rt_ring0', charNsp + ':' + charPrefix + '_ac_rt_ring1',
                      charNsp + ':' + charPrefix + '_ac_rt_ring2', charNsp + ':' + charPrefix + '_ac_rt_ring3',
                      charNsp + ':' + charPrefix + '_ac_rt_pinkey0', charNsp + ':' + charPrefix + '_ac_rt_pinkey1',
                      charNsp + ':' + charPrefix + '_ac_rt_pinkey2', charNsp + ':' + charPrefix + '_ac_rt_pinkey3',
                      charNsp + ':' + charPrefix + '_ac_rt_thumb1', charNsp + ':' + charPrefix + '_ac_rt_thumb2',
                      charNsp + ':' + charPrefix + '_ac_rt_thumb3']

    lfHandControls = [charNsp + ':' + charPrefix + '_ac_lf_index0', charNsp + ':' + charPrefix + '_ac_lf_index1',
                      charNsp + ':' + charPrefix + '_ac_lf_index2', charNsp + ':' + charPrefix + '_ac_lf_index3',
                      charNsp + ':' + charPrefix + '_ac_lf_middle0', charNsp + ':' + charPrefix + '_ac_lf_middle1',
                      charNsp + ':' + charPrefix + '_ac_lf_middle2', charNsp + ':' + charPrefix + '_ac_lf_middle3',
                      charNsp + ':' + charPrefix + '_ac_lf_ring0', charNsp + ':' + charPrefix + '_ac_lf_ring1',
                      charNsp + ':' + charPrefix + '_ac_lf_ring2', charNsp + ':' + charPrefix + '_ac_lf_ring3',
                      charNsp + ':' + charPrefix + '_ac_lf_pinkey0', charNsp + ':' + charPrefix + '_ac_lf_pinkey1',
                      charNsp + ':' + charPrefix + '_ac_lf_pinkey2', charNsp + ':' + charPrefix + '_ac_lf_pinkey3',
                      charNsp + ':' + charPrefix + '_ac_lf_thumb1', charNsp + ':' + charPrefix + '_ac_lf_thumb2',
                      charNsp + ':' + charPrefix + '_ac_lf_thumb3']

    rtHandHud = charNsp.upper() + ' | RT HAND'
    lfHandHud = charNsp.upper() + ' | LF HAND'

    # ===== ROOT CHILD CONTROLS ===============================================
    rootChildControls = [charNsp + ':' + charPrefix + '_ac_cn_upperbody',
                         charNsp + ':' + charPrefix + '_ac_cn_pelvis']

    rootChildHuds = [charNsp.upper() + ' | ROOT',
                     charNsp.upper() + ' | PELVIS']

    # ===== SPINE CHILD CONTROLS ==============================================
    spineChildControls = [charNsp + ':' + charPrefix + '_ac_cn_spineFK1',
                          charNsp + ':' + charPrefix + '_ac_cn_spineFK2',
                          charNsp + ':' + charPrefix + '_ac_cn_spineFK3',
                          charNsp + ':' + charPrefix + '_ac_cn_chest']

    spineChildHuds = [charNsp.upper() + ' | SPINE BOT',
                      charNsp.upper() + ' | SPINE MID',
                      charNsp.upper() + ' | SPINE TOP',
                      charNsp.upper() + ' | IK SPINE']

    # ===== RT ARM CONTROLS ===================================================
    rtArmControls = [charNsp + ':' + charPrefix + '_ac_rt_shoulderFK',
                     charNsp + ':' + charPrefix + '_ac_rt_elbowFK',
                     charNsp + ':' + charPrefix + '_ac_rt_handFK',
                     charNsp + ':' + charPrefix + '_ac_rt_handIK',
                     charNsp + ':' + charPrefix + '_ac_rt_armPole',
                     charNsp + ':' + charPrefix + '_ac_rt_clavicle']

    rtArmBendControls = [charNsp + ':' + charPrefix + '_ac_rt_arm_bend',
                         charNsp + ':' + charPrefix + '_ac_rt_elbow_bend',
                         charNsp + ':' + charPrefix + '_ac_rt_forearm_bend']

    rtArmBendHuds = [charNsp.upper() + ' | RT ARM BEND',
                     charNsp.upper() + ' | RT ELBOW BEND',
                     charNsp.upper() + ' | RT FOREARM BEND']

    # ===== LF ARM CONTROLS ===================================================
    lfArmControls = [charNsp + ':' + charPrefix + '_ac_lf_shoulderFK',
                     charNsp + ':' + charPrefix + '_ac_lf_elbowFK',
                     charNsp + ':' + charPrefix + '_ac_lf_handFK',
                     charNsp + ':' + charPrefix + '_ac_lf_handIK',
                     charNsp + ':' + charPrefix + '_ac_lf_armPole',
                     charNsp + ':' + charPrefix + '_ac_lf_clavicle']

    lfArmBendControls = [charNsp + ':' + charPrefix + '_ac_lf_arm_bend',
                         charNsp + ':' + charPrefix + '_ac_lf_elbow_bend',
                         charNsp + ':' + charPrefix + '_ac_lf_forearm_bend']

    lfArmBendHuds = [charNsp.upper() + ' | LF ARM BEND',
                     charNsp.upper() + ' | LF ELBOW BEND',
                     charNsp.upper() + ' | LF FOREARM BEND']

    # ===== RT LEG CONTROLS ===================================================
    rtLegControls = [charNsp + ':' + charPrefix + '_ac_rt_footIK',
                     charNsp + ':' + charPrefix + '_ac_rt_legPole',
                     charNsp + ':' + charPrefix + '_ac_rt_kneeIK',
                     charNsp + ':' + charPrefix + '_ac_rt_hipFK',
                     charNsp + ':' + charPrefix + '_ac_rt_kneeFK',
                     charNsp + ':' + charPrefix + '_ac_rt_footFK',
                     charNsp + ':' + charPrefix + '_ac_rt_toe']

    rtLegBendControls = [charNsp + ':' + charPrefix + '_ac_rt_upleg_bend',
                         charNsp + ':' + charPrefix + '_ac_rt_knee_bend',
                         charNsp + ':' + charPrefix + '_ac_rt_lowleg_bend']

    rtLegBendHuds = [charNsp.upper() + ' | RT THIGH BEND',
                     charNsp.upper() + ' | RT KNEE BEND',
                     charNsp.upper() + ' | RT CALF BEND']

    # ===== LF LEG CONTROLS ===================================================
    lfLegControls = [charNsp + ':' + charPrefix + '_ac_lf_footIK',
                     charNsp + ':' + charPrefix + '_ac_lf_legPole',
                     charNsp + ':' + charPrefix + '_ac_lf_kneeIK',
                     charNsp + ':' + charPrefix + '_ac_lf_hipFK',
                     charNsp + ':' + charPrefix + '_ac_lf_kneeFK',
                     charNsp + ':' + charPrefix + '_ac_lf_footFK',
                     charNsp + ':' + charPrefix + '_ac_lf_toe']

    lfLegBendControls = [charNsp + ':' + charPrefix + '_ac_lf_upleg_bend',
                         charNsp + ':' + charPrefix + '_ac_lf_knee_bend',
                         charNsp + ':' + charPrefix + '_ac_lf_lowleg_bend']

    lfLegBendHuds = [charNsp.upper() + ' | LF THIGH BEND',
                     charNsp.upper() + ' | LF KNEE BEND',
                     charNsp.upper() + ' | LF CALF BEND']

    # ===== SELECT CONTROLS ===================================================
    selectedControls = cmds.ls(sl=True)

    if (len(selectedControls) == 0):
        for ctrl in lfHandControls:
            cmds.select(ctrl, add=True)
        return lfHandHud

    elif (len(selectedControls) == 1):

        # ===== ROOT ==========================================================
        if (selectedControls[0] == rootChildControls[0]):
            cmds.select(rootChildControls[1])
            return rootChildHuds[1]

        elif (selectedControls[0] == rootChildControls[1]):
            cmds.select(rootChildControls[0])
            return rootChildHuds[0]



        # ===== SPINE ==========================================================
        elif (selectedControls[0] == spineChildControls[0]):
            cmds.select(spineChildControls[1])
            return spineChildHuds[1]

        elif (selectedControls[0] == spineChildControls[1]):
            cmds.select(spineChildControls[2])
            return spineChildHuds[2]


        elif (selectedControls[0] == spineChildControls[2]):
            cmds.select(spineChildControls[3])
            return spineChildHuds[3]


        elif (selectedControls[0] == spineChildControls[3]):
            cmds.select(spineChildControls[0])
            return spineChildHuds[0]

        # ===== RT ARM BEND BOWS =============================================
        for ctrl in rtArmControls:
            if (selectedControls[0] == ctrl):
                cmds.select(rtArmBendControls[0])
                return rtArmBendHuds[0]

        if (selectedControls[0] == rtArmBendControls[0]):
            cmds.select(rtArmBendControls[1])
            return rtArmBendHuds[1]



        elif (selectedControls[0] == rtArmBendControls[1]):
            cmds.select(rtArmBendControls[2])
            return rtArmBendHuds[2]



        elif (selectedControls[0] == rtArmBendControls[2]):
            cmds.select(rtArmBendControls[0])
            return rtArmBendHuds[0]

        # ===== LF ARM BEND BOWS =============================================
        for ctrl in lfArmControls:
            if (selectedControls[0] == ctrl):
                cmds.select(lfArmBendControls[0])
                return lfArmBendHuds[0]

        if (selectedControls[0] == lfArmBendControls[0]):
            cmds.select(lfArmBendControls[1])
            return lfArmBendHuds[1]



        elif (selectedControls[0] == lfArmBendControls[1]):
            cmds.select(lfArmBendControls[2])
            return lfArmBendHuds[2]



        elif (selectedControls[0] == lfArmBendControls[2]):
            cmds.select(lfArmBendControls[0])
            return lfArmBendHuds[0]

        # ===== RT LEG BEND BOWS =============================================
        for ctrl in rtLegControls:
            if (selectedControls[0] == ctrl):
                cmds.select(rtLegBendControls[0])
                return rtLegBendHuds[0]

        if (selectedControls[0] == rtLegBendControls[0]):
            cmds.select(rtLegBendControls[1])
            return rtLegBendHuds[1]



        elif (selectedControls[0] == rtLegBendControls[1]):
            cmds.select(rtLegBendControls[2])
            return rtLegBendHuds[2]



        elif (selectedControls[0] == rtLegBendControls[2]):
            cmds.select(rtLegBendControls[0])
            return rtLegBendHuds[0]

        # ===== LF LEG BEND BOWS =============================================
        for ctrl in lfLegControls:
            if (selectedControls[0] == ctrl):
                cmds.select(lfLegBendControls[0])
                return lfLegBendHuds[0]

        if (selectedControls[0] == lfLegBendControls[0]):
            cmds.select(lfLegBendControls[1])
            return lfLegBendHuds[1]



        elif (selectedControls[0] == lfLegBendControls[1]):
            cmds.select(lfLegBendControls[2])
            return lfLegBendHuds[2]



        elif (selectedControls[0] == lfLegBendControls[2]):
            cmds.select(lfLegBendControls[0])
            return lfLegBendHuds[0]




    elif (len(selectedControls) > 1):

        # SPINE SELECTED > SWITCH TO SPINE BOT
        if (selectedControls[0] == spineChildControls[0] or selectedControls[0] == spineChildControls[1] or
                selectedControls[0] == spineChildControls[2] or selectedControls[0] == spineChildControls[3]):
            cmds.select(spineChildControls[0])
            return spineChildControls[0]

    # IN CASE ANY OTHER COMBINATION OF CONTROLS ARE SELECTED
    cmds.select(cl=True)
    for ctrl in lfHandControls:
        cmds.select(ctrl, add=True)
    return lfHandHud


# Shows HUDs on viewport
if (cmds.headsUpDisplay('HUDActiveChar', ex=True)):
    cmds.headsUpDisplay('HUDActiveChar', rem=True)

cmds.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='nextMinorCtrl()', ev='PreFileNewOrOpened')



ackPushPull "push";
ackPushPull "pull";
ackConvergeBuffer "snap";
ackConvergeBuffer "toward"
ackConvergeBuffer "away";
timeSliderEditKeys addInbetween;
timeSliderEditKeys removeInbetween;