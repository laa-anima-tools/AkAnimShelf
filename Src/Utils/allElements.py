import maya.cmds as cmds

def objectPosition(*args):
    try:
        selectedNodes = cmds.selectedNodes()
        mainObj = selectedNodes[-1]
        positionList = cmds.getAttr('%s.translate' % mainObj)
        return positionList[0]
    except:
        return (0.0, 0.0, 0.0)

cmds.headsUpDisplay('HUDObjectPosition', section=1, block=0, blockSize='medium', label='Position',
                    labelFontSize='large', command=objectPosition, event='SelectionChanged',
                    nodeChanges='attributeChange')

cmds.headsUpDisplay('HUDCameraName', s=2, b=0, ba='center', dw=50, pre='cameraNames')
cmds.headsUpDisplay('HUDObjectPosition', rem=True)
cmds.headsUpDisplay(rp=(7, 0))
