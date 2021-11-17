# ============================================================================= #
# SET CHAR NAMESPACE                                                            #
# ============================================================================= #
import maya.cmds as cmd

def listAllNsp():
    chars_list = []
    ctrls_list = cmd.ls('*:x_main_000_ctrl')

    if not ctrls_list:
        return chars_list

    for ctrl in ctrls_list:
        char_nsp = ctrl.split(':')[0]
        chars_list.append(char_nsp)

    return chars_list

def setCurrentNsp(*args):
    global charNsp

    existingChar = list(listAllNsp())

    try:
        for i, elmt in enumerate(existingChar):
            print i, elmt, charNsp

            if charNsp == existingChar[-1]:
                charNsp = existingChar[0]
                return charNsp.upper()
            if charNsp == existingChar[i]:
                charNsp = existingChar[i+1]
                return charNsp.upper()
    except:
        charNsp = existingChar[0]
        return charNsp.upper()


# Shows HUDs on viewport
if (cmd.headsUpDisplay('HUDActiveChar', ex=True)):
    cmd.headsUpDisplay('HUDActiveChar', rem=True)

cmd.headsUpDisplay('HUDActiveChar', s=2, b=0, bs='large', lfs='small', c='setCurrentNsp()', ev='PreFileNewOrOpened')
