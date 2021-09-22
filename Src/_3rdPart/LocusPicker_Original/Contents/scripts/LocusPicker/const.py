# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\const.py
try:
    from PySide2.QtCore import QLocale, QRectF, Qt, QRegExp
    from PySide2.QtGui import QColor, QFont, QPalette, QTransform, QFontDatabase
    from PySide2.QtWidgets import QGraphicsItem, QMessageBox
except:
    from PySide.QtCore import QLocale, QRectF, Qt, QRegExp
    from PySide.QtGui import QGraphicsItem, QColor, QFont, QPalette, QTransform, QFontDatabase, QMessageBox

from hashlib import sha224
from urllib import quote_plus
from time import time
from base64 import urlsafe_b64encode, urlsafe_b64decode
import re, os
VERSION = 1.135
FONT_DB = QFontDatabase()
FONT_FAMILIES = FONT_DB.families()
CommandTypes = ['Select',
 'Reset',
 'Key',
 'Toggle',
 'Pose',
 'Range']
DEF_CHARNAME = 'NewCharacter1'
DEF_MAPNAME = 'Map1'
DEF_MAPBGCOLOR = QColor(Qt.darkGray)
SELECTED_BORDER_COLOR = QColor(67, 255, 163)
SCROLL_WAITING_TIME = 3000
MASTER_WINDOW_NAME = 'LocusPickerWindow'
USER_WINDOW_NAME = 'LocusPickerLauncher'
MAP_FILE_FILTER = 'Map files (*.map);;'
IMAGE_FILE_FILTER = 'Images (*.png *.jpg);;PNG Files (*.png);;JPG Files(*.jpg *.jpeg);;'
SVG_FILE_FILTER = 'SVG files (*.svg);;'
TemplateDir = 'C:/Users/hgkim/workspace/LocusPicker/src/templates'
documentUrl = 'https://drive.google.com/file/d/1vFQihomfe01QKLpa5ihWZ_gxrUkZ6O5M'
REFRESH_TIP = 'Reload maps within current map group from picker nodes in scene.'
CREATE_CHAR_TIP = 'Create a new map within map group.\nTo load data file, click RMB.'
EDIT_MAP_TIP = 'Edit current selected map.'
SAVE_NODE_TIP = 'Save current map to picker node.\nTo Save map to picker node, click RMB.'
LOAD_FILE_TIP = 'Load a data file or files.\nYou can select multiple files.'
SAVE_FILE_TIP = 'Save the current map to a data file.\nTo save all the maps of the current map group, hold Alt and click'
TOOL_DIALOG_TIP = 'Show tools dialog.\nThis would give more options to manage.'
INFO_TIP = 'Open the link for documentation.'
INIT_CREATE_TIP = "Creates a new map based on the options you've given."
INIT_EDIT_TIP = "Edits a current selected map based on the options you've given."
INIT_IMPORT_TIP = 'Import a data file to create to map.'
INIT_EXPORT_TIP = 'Export current map to data file.'
COLOR_PICK_TIP = 'To create a new button, drag and drop onto map. \nTo create multi buttons horizontally, hold Alt and drag. \nTo create multi buttons vertically, hold Ctrl and drag.\nTo create multi buttons by a captured view from the camera, hold Ctrl+Alt and drag.\n-------------------------------------------------------------------------\nTo change Color, click this.\nIf click with holding Ctrl, you can use predefined palette.'
COMMAND_COMBOBOX_TIP = 'Select a designated command.\nTo change the command of a button, drag and drop over it.'
PREFIX_TIP = 'Toggle on/off prefix option.'
PREFIX_FIELD_TIP = 'Type in prefix.\nOr click the arrow button on the left to copy prefix from selected object.'
COPY_PREFIX_TIP = 'Copy prefix from selected object.'
SELECT_CHAR_TIP = 'To choose a map group, click and select one from the pull-down menu.\nTo rename, hold Alt and click, then type in.'
CHANGE_LABEL_TIP = 'To change the label, drag and drop onto a button '
REMOVE_LABEL_TIP = 'To remove the label, drag and drop onto a button'
CREATE_BUTTON_TIP = 'Drag and drop onto a map'
COLOR_PALETTE_TIP = 'To change a color, drag and drop onto a button.\nOr if you drop onto map, it changes background color.\nColor : '
TEMPLATE_LIST_TIP = 'To create buttons based on vector map, drag and drop onto map.'
TEAROFF_TIP = 'To tear-off a map, hold Ctrl and drag.'
ADD_BOOKMARK_TIP = 'To append current map as a new bookmark, click this.\n  (if the map has already been added, will not work.)'
MIME_TEMPLATE = 'LocusPicker/Template'
MIME_TEMPLATE_SIZE = 'LocusPicker/Template-Size'
MIME_COLOR_MODIFIER = 'ColorButton/Modifier'
MIME_NEWBUTTON = 'ToolDialog/NewButton'
MIME_COLOR = 'ToolDialog/Color'
MIME_IMAGE = 'ToolDialog/Image'
MIME_IMAGE_PATH = 'ToolDialog/Image-Path'
MIME_IMAGE_RECT = 'ToolDialog/Image-Rect'
MIME_IMAGE_BUTTONSIZE = 'ToolDialog/Image-ButtonSize'
MIME_COMMAND = 'ToolDialog/Command'
MIME_LABEL = 'ToolDialog/Label'
MIME_FONT_FAMILY = 'ToolDialog/Font-Family'
MIME_FONT_SIZE = 'ToolDialog/Font-Size'
MIME_FONT_BOLD = 'ToolDialog/Font-Bold'
MIME_FONT_ITALIC = 'ToolDialog/Font-Italic'
MIME_DRAGCOMBO_TEXT = 'DragComboBox/Text'
MIME_CUSTOM_LABEL = 'ToolDialog/Custom-Label'
MIME_SLIDER_COMMAND = 'ToolDialog/Slider-Command'
MIME_SLIDER_WIDTH = 'ToolDialog/Slider-Width'
MIME_SLIDER_HEIGHT = 'ToolDialog/Slider-Height'
MIME_SLIDER_ATTACH = 'ToolDialog/Slider-Attach'
MIME_SLIDER_INVERSE = 'ToolDialog/Slider-Inverse'
MIME_SLIDER_CHANGETOOL = 'ToolDialog/Slider-ChangeTool'
MIME_SLIDER_ATTRIBUTE = 'ToolDialog/Slider-AttributeOption'
MIME_SLIDER_BUTTONNUMBER = 'ToolDialog/Slider-NumberOfButtons'
nameRegExp = QRegExp('\\w+')

def error(msg, title = 'Error', parent = None):
    QMessageBox.critical(parent, title, msg)
    return False


def warn(msg, title = 'Warning', parent = None):
    QMessageBox.warning(parent, title, msg)
    return False


def info(msg, title = '', parent = None):
    QMessageBox.information(parent, title, msg)


def question(msg, title = '', parent = None):
    return QMessageBox.question(parent, title, msg, defaultButton=QMessageBox.Yes) == QMessageBox.Yes


def confirm(msg, title = '', buttonText = None, parent = None):
    if buttonText is None:
        buttonText = []
    from dialog import TriStateDialog
    if len(buttonText) == 3:
        dlg = TriStateDialog(title, msg, buttonText[0], buttonText[1], buttonText[2], parent)
    else:
        dlg = TriStateDialog(title, msg, parent=parent)
    answer = dlg.exec_()
    if answer == 0:
        return 1
    elif answer == 2:
        return 0
    else:
        return -1
        return


class Attachment:
    NotValid = 0
    TOP = 1
    BOTTOM = 2
    LEFT = 4
    RIGHT = 8

    @classmethod
    def isTop(cls, val):
        return bool(val & cls.TOP)

    @classmethod
    def isBottom(cls, val):
        return bool(val & cls.BOTTOM)

    @classmethod
    def isLeft(cls, val):
        return bool(val & cls.LEFT)

    @classmethod
    def isRight(cls, val):
        return bool(val & cls.RIGHT)

    @classmethod
    def isHorizontal(cls, val):
        return bool(val & 12)

    @classmethod
    def isVertical(cls, val):
        return bool(val & 3)

    @classmethod
    def getString(cls, attach):
        if cls.isTop(attach):
            return 'Top'
        elif cls.isBottom(attach):
            return 'Bottom'
        elif cls.isLeft(attach):
            return 'Left'
        elif cls.isRight(attach):
            return 'Right'
        else:
            return 'No'

    @classmethod
    def getAttachment(cls, strData):
        if strData == 'Left':
            return cls.LEFT
        elif strData == 'Right':
            return cls.RIGHT
        elif strData == 'Top':
            return cls.TOP
        elif strData == 'Bottom':
            return cls.BOTTOM
        else:
            return cls.NotValid


class ButtonPosition:
    NORTH = 1
    SOUTH = 2
    WEST = 4
    EAST = 8

    @classmethod
    def isNorth(cls, val):
        return bool(val & cls.NORTH)

    @classmethod
    def isSouth(cls, val):
        return bool(val & cls.SOUTH)

    @classmethod
    def isWest(cls, val):
        return bool(val & cls.WEST)

    @classmethod
    def isEast(cls, val):
        return bool(val & cls.EAST)

    @classmethod
    def isLatitude(cls, val):
        return bool(val & 3)

    @classmethod
    def isLongitude(cls, val):
        return bool(val & 12)

    @classmethod
    def getString(cls, position):
        if cls.isNorth(position):
            return 'North'
        elif cls.isSouth(position):
            return 'South'
        elif cls.isWest(position):
            return 'West'
        elif cls.isEast(position):
            return 'East'
        else:
            return 'North'

    @classmethod
    def getPosition(cls, strData):
        if strData == 'North':
            return cls.NORTH
        elif strData == 'South':
            return cls.SOUTH
        elif strData == 'West':
            return cls.WEST
        elif strData == 'East':
            return cls.EAST
        else:
            return cls.NORTH


class CursorPos:
    NONE = 0
    TOP = 1
    BOTTOM = 2
    LEFT = 4
    RIGHT = 8

    @classmethod
    def isTop(cls, val):
        return bool(val & cls.TOP)

    @classmethod
    def isBottom(cls, val):
        return bool(val & cls.BOTTOM)

    @classmethod
    def isLeft(cls, val):
        return bool(val & cls.LEFT)

    @classmethod
    def isRight(cls, val):
        return bool(val & cls.RIGHT)

    @classmethod
    def isTopLeft(cls, val):
        return val == cls.TOP | cls.LEFT

    @classmethod
    def isTopRight(cls, val):
        return val == cls.TOP | cls.RIGHT

    @classmethod
    def isBottomLeft(cls, val):
        return val == cls.BOTTOM | cls.LEFT

    @classmethod
    def isBottomRight(cls, val):
        return val == cls.BOTTOM | cls.RIGHT

    @staticmethod
    def isOneSide(n):
        return n > 0 and not n & n - 1


class DropItemType:
    Rectangle = QGraphicsItem.UserType + 1
    EditableRectangle = QGraphicsItem.UserType + 2
    RectangleSlider = QGraphicsItem.UserType + 3
    EditableRectangleSlider = QGraphicsItem.UserType + 4
    Path = QGraphicsItem.UserType + 5
    EditablePath = QGraphicsItem.UserType + 6
    Group = QGraphicsItem.UserType + 7
    EditableGroup = QGraphicsItem.UserType + 8
    DragPose = QGraphicsItem.UserType + 9
    EditableDragPose = QGraphicsItem.UserType + 10
    Line = QGraphicsItem.UserType + 11
    VisToggle = QGraphicsItem.UserType + 12
    EditableVisToggle = QGraphicsItem.UserType + 13


def getTypeString(itemType):
    if itemType == DropItemType.Rectangle:
        return 'Rectangle'
    elif itemType == DropItemType.EditableRectangle:
        return 'Rectangle'
    elif itemType == DropItemType.RectangleSlider:
        return 'RectangleSlider'
    elif itemType == DropItemType.EditableRectangleSlider:
        return 'RectangleSlider'
    elif itemType == DropItemType.Path:
        return 'Path'
    elif itemType == DropItemType.EditablePath:
        return 'Path'
    elif itemType == DropItemType.Group:
        return 'Group'
    elif itemType == DropItemType.EditableGroup:
        return 'Group'
    elif itemType == DropItemType.DragPose:
        return 'DragPose'
    elif itemType == DropItemType.EditableDragPose:
        return 'DragPose'
    elif itemType == DropItemType.VisToggle:
        return 'VisToggle'
    elif itemType == DropItemType.EditableVisToggle:
        return 'VisToggle'
    else:
        return 'None'


def getType(typeStr, editable = True):
    if typeStr == 'Rectangle':
        if editable:
            return DropItemType.EditableRectangle
        else:
            return DropItemType.Rectangle
    if typeStr == 'RectangleSlider':
        if editable:
            return DropItemType.EditableRectangleSlider
        else:
            return DropItemType.RectangleSlider
    if typeStr == 'Path':
        if editable:
            return DropItemType.EditablePath
        else:
            return DropItemType.Path
    if typeStr == 'Group':
        if editable:
            return DropItemType.EditableGroup
        else:
            return DropItemType.Group
    if typeStr == 'DragPose':
        if editable:
            return DropItemType.EditableDragPose
        else:
            return DropItemType.DragPose
    if typeStr == 'VisToggle':
        if editable:
            return DropItemType.EditableVisToggle
        else:
            return DropItemType.VisToggle
    else:
        return None
    return None


def find_missing_items(int_list):
    original_set = set(int_list)
    smallest_item = min(original_set)
    largest_item = max(original_set)
    full_set = set(xrange(smallest_item, largest_item + 1))
    return sorted(list(full_set - original_set))


def getNumericName(text, names):
    if text in names:
        text = re.sub('\\d*$', '', text)
        names = [ n for n in names if n.startswith(text) ]
        int_list = []
        for name in names:
            m = re.match('^%s(\\d+)' % text, name)
            if m:
                int_list.append(int(m.group(1)))
            else:
                int_list.append(0)

        int_list.sort()
        missing_int = find_missing_items(int_list)
        if missing_int:
            _id = str(missing_int[0])
        else:
            _id = str(int_list[-1] + 1)
    else:
        _id = ''
    text += _id
    return text


class WaitState:
    Wait = 0
    GoBack = 1
    Proceed = 2


class LocaleText:

    def __init__(self, locale = QLocale(QLocale.English)):
        self.locale = locale

    def __call__(self, textType):
        if self.locale.language() == QLocale.Korean:
            if textType == 'NotSavedTitle':
                return u'\uc800\uc7a5\ub418\uc9c0 \uc54a\uc74c'
            if textType == 'NotSavedMessage':
                return u'\uc800\uc7a5\ub418\uc9c0 \uc54a\uc740 \ubcc0\uacbd\uc774 \uc788\uc2b5\ub2c8\ub2e4.\n\ub178\ub4dc\ub85c \uc800\uc7a5\ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?'
            if textType == 'HasItemTitle':
                return u'\uc544\uc774\ud15c \uc788\uc74c'
            if textType == 'HasItemMessage':
                return u'\ub9f5\uc5d0 \uc544\uc774\ud15c\uc774 \uc788\uc2b5\ub2c8\ub2e4.\n\uc815\ub9d0\ub85c \uc0ad\uc81c\ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?'
        else:
            if textType == 'NotSavedTitle':
                return 'Not Saved'
            if textType == 'NotSavedMessage':
                return 'There are some unsaved changes.\nDo you want to save them to node?'
            if textType == 'HasItemTitle':
                return 'Item existing'
            if textType == 'HasItemMessage':
                return 'Map has one or more items.\nDo you really remove this map?'


def encodeIconStr(item):
    from svgParser import generatePathToSvg
    if getTypeString(item.type()) in ('Path', 'VisToggle'):
        iconStr = str(generatePathToSvg(item.path))
    else:
        iconStr = str(item.iconPath)
        if item.iconPath:
            iconRect = item.iconRect.getRect()
            iconStr += ';%.2f,%.2f,%.2f,%.2f' % (iconRect[0],
             iconRect[1],
             iconRect[2],
             iconRect[3])
    return iconStr


def decodeIconStr(iconStr, itemType):
    if itemType in ('Path', 'VisToggle'):
        return iconStr
    if iconStr:
        iconSplit = iconStr.split(';', 1)
        if len(iconSplit) == 2:
            path, rect = iconSplit
            rectSplit = rect.split(',')
            if len(rectSplit) == 4:
                rect = QRectF(*[ float(v) for v in rectSplit ])
            else:
                rect = QRectF()
            return [path, rect]
        elif len(iconSplit) == 1:
            return [iconSplit[0], QRectF()]
        else:
            return []
    else:
        return []


def encodeLabelStr(item):
    labelStr = str(item.label)
    if item.label:
        labelRect = item.labelRect.getRect()
        labelStr += ';%.2f,%.2f,%.2f,%.2f' % (labelRect[0],
         labelRect[1],
         labelRect[2],
         labelRect[3])
        labelFont = item.font
        isBold, isItalic = labelFont.bold(), labelFont.italic()
        try:
            family = urlsafe_b64encode(labelFont.family().encode('utf-8'))
        except:
            print ' >> Sorry, some kinds of fonts are not supported :', labelFont.family()
            family = 'Tahoma'

        pointSize = labelFont.pointSize()
        labelStr += ';%s,%d,%d,%d' % (family,
         pointSize,
         isBold and 1 or 0,
         isItalic and 1 or 0)
    return labelStr


def decodeLabelStr(ladelStr):
    if ladelStr:
        font = QFont()
        font.setPointSize(9)
        labelSplit = ladelStr.split(';', 2)
        if len(labelSplit) == 3:
            label, rect, fontStr = labelSplit
            rectSplit = rect.split(',')
            if len(rectSplit) == 4:
                rect = QRectF(*[ float(v) for v in rectSplit ])
            else:
                rect = QRectF()
            if fontStr:
                fontSplit = fontStr.split(',')
                if len(fontSplit) == 4:
                    try:
                        decoded = urlsafe_b64decode(str(fontSplit[0]))
                        font.setFamily(unicode(decoded, 'utf-8'))
                    except:
                        print ' >> Sorry, font data is not encoded in proper way.', fontSplit[0]

                    font.setPointSize(int(fontSplit[1]))
                    font.setBold(bool(int(fontSplit[2])))
                    font.setItalic(bool(int(fontSplit[3])))
            return [label, rect, font]
        elif len(labelSplit) == 2:
            label, rect = labelSplit
            rectSplit = rect.split(',')
            if len(rectSplit) == 4:
                rect = QRectF(*[ float(v) for v in rectSplit ])
            else:
                rect = QRectF()
            return [label, rect, font]
        elif len(labelSplit) == 1:
            return [labelSplit[0], QRectF(), font]
        else:
            return []
    else:
        return []


def encodeCommandStr(item):
    commandStr = str(item.command)
    if commandStr.startswith('EXEC'):
        return commandStr
    if getTypeString(item.type()) in ('Path', 'Rectangle', 'DragPose'):
        return commandStr
    if item.command in ('Range', 'Pose'):
        commandStr += str(' ' + Attachment.getString(item.attachment))
        commandStr += str(' ' + (item.invertedAppearance and 'backward' or 'forward'))
    return commandStr


def decodeCommandStr(commandStr):
    commandSplit = commandStr.split(' ', 2)
    if len(commandSplit) == 3:
        command, attach, fwd_bwd = commandSplit
    elif len(commandSplit) == 2:
        command, attach, fwd_bwd = commandSplit + ['forward']
    else:
        command, attach, fwd_bwd = commandSplit + ['Top', 'forward']
    if fwd_bwd == 'forward':
        backward = False
    else:
        backward = True
    return (command, attach, backward)


def encodeGroupCommandStr(item):
    data = []
    data.append(item.doKey and 'true' or 'false')
    data.append(item.doReset and 'true' or 'false')
    data.append(ButtonPosition.getString(item.labelPosition))
    data.append(ButtonPosition.getString(item.buttonPosition))
    return ';'.join(data)


def decodeGroupCommandStr(commandStr):
    commandSplit = commandStr.split(';', 3)
    if len(commandSplit) == 4:
        doKey, doReset, labelPos, buttonPos = commandSplit
    elif len(commandSplit) == 3:
        doKey, doReset, labelPos, buttonPos = commandSplit + ['North']
    elif len(commandSplit) == 2:
        doKey, doReset, labelPos, buttonPos = commandSplit + ['North', 'North']
    else:
        doKey, doReset, labelPos, buttonPos = ('false', 'false', 'North', 'North')
    doKey = doKey == 'true'
    doReset = doReset == 'true'
    labelPos = ButtonPosition.getPosition(labelPos)
    buttonPos = ButtonPosition.getPosition(buttonPos)
    return (doKey,
     doReset,
     labelPos,
     buttonPos)


def encodeVisToggleNodeStr(item):
    states = [ i[1] for i in sorted(item.states.items(), key=lambda x: x[0]) ]
    return ','.join([ x.name + ':' + ';'.join([ t.hashcode for t in x.targets if t.scene() ]) for x in states ])


def decodeVisToggleNodeStr(nodeStr):
    name, targets = nodeStr.split(':')
    targets = targets and targets.split(';') or []
    return (name, targets)


def encodeVisToggleChannelStr(item):
    states = [ i[1] for i in sorted(item.states.items(), key=lambda x: x[0]) ]
    return '@'.join([ x.cmd for x in states ])


def decodeVisToggleChannelStr(channelStr):
    return channelStr.split('@')


def encodeVisToggleColorStr(item):
    states = [ i[1] for i in sorted(item.states.items(), key=lambda x: x[0]) ]
    return ','.join([ '%d;%d;%d' % (x.color.red(), x.color.green(), x.color.blue()) for x in states ])


def decodeVisToggleColorStr(colorStr):
    result = []
    for cs in colorStr.split(','):
        result.append(QColor.fromRgb(*[ int(v) for v in cs.split(';') ]))

    return result


def generateHashcode(item):
    pos = item.pos()
    digest = sha224(str(time()) + str(pos.x()) + str(pos.y())).hexdigest()[:10]
    return quote_plus(digest)


def getComplementaryColor(color):
    hsl_h = color.hslHueF()
    hsl_s = color.hslSaturationF()
    lightness = color.lightnessF()
    lightness = 1.0 - lightness
    hsl_h += 0.5
    if hsl_h >= 1.0:
        hsl_h -= 1.0
    return QColor.fromHslF(hsl_h, hsl_s, lightness)


def getDefaultColor(option):
    if option == 'RtIK':
        color = QColor.fromRgbF(0.7, 0.4, 0.7)
    elif option == 'RtFK':
        color = QColor.fromRgbF(0.7, 0.4, 0.4)
    elif option == 'CnIK':
        color = QColor.fromRgbF(0.4, 0.7, 0.4)
    elif option == 'CnFK':
        color = QColor.fromRgbF(0.7, 0.7, 0.4)
    elif option == 'LfIK':
        color = QColor.fromRgbF(0.4, 0.5, 0.7)
    elif option == 'LfFK':
        color = QColor.fromRgbF(0.4, 0.6, 0.6)
    elif option == 'Grey':
        color = QColor.fromRgbF(0.4, 0.4, 0.4)
    elif option == 'OK':
        color = QColor.fromRgbF(0.5, 0.7, 0.8)
    elif option == 'Cancel':
        color = QColor.fromRgbF(0.7, 0.5, 0.4)
    elif option == 'Warn':
        color = QColor.fromRgbF(0.7, 0.2, 0.2)
    elif option == 'Collapse':
        color = QColor.fromRgbF(0.15, 0.15, 0.15)
    elif option == 'Subtle':
        color = QColor.fromRgbF(0.48, 0.48, 0.6)
    else:
        return QColor.fromRgbF(0.0, 0.0, 0.0)
    if option:
        color.ann = option + ' Color'
    return color


def getMirrorColor(color):
    RtIK = getDefaultColor('RtIK')
    RtFK = getDefaultColor('RtFK')
    LfIK = getDefaultColor('LfIK')
    LfFK = getDefaultColor('LfFK')
    if color == RtIK:
        return LfIK
    elif color == RtFK:
        return LfFK
    elif color == LfIK:
        return RtIK
    elif color == LfFK:
        return RtFK
    elif color == RtIK.lighter():
        return LfIK.lighter()
    elif color == RtFK.lighter():
        return LfFK.lighter()
    elif color == LfIK.lighter():
        return RtIK.lighter()
    elif color == LfFK.lighter():
        return RtFK.lighter()
    elif color == RtIK.darker():
        return LfIK.darker()
    elif color == RtFK.darker():
        return LfFK.darker()
    elif color == LfIK.darker():
        return RtIK.darker()
    elif color == LfFK.darker():
        return RtFK.darker()
    else:
        return getComplementaryColor(color)


def setButtonColor(button, r, g, b):
    palette = button.palette()
    palette.setColor(QPalette.Button, QColor.fromRgbF(r, g, b))
    palette.setColor(QPalette.Window, QColor.fromRgbF(r, g, b))
    palette.setColor(QPalette.ButtonText, QColor(Qt.black))
    button.setPalette(palette)


def getMirroredPath(path):
    trans = QTransform()
    boundingRect = path.boundingRect()
    trans.translate(boundingRect.width(), 0)
    trans.scale(-1, 1)
    mrPath = trans.map(path)
    return mrPath


def indentXML(elem, level = 0):
    i = '\n' + level * '    '
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + '    '
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indentXML(elem, level + 1)

        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    elif level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


def affixPrefix(prefix, nodes = None):
    if not isinstance(nodes, (list, tuple)):
        if isinstance(nodes, (str, unicode)):
            nodes = [nodes]
        else:
            return []
    if not prefix.endswith(':'):
        prefix += ':'
    return [ prefix + x.rsplit(':', 1)[-1] for x in nodes ]


def splitCapitalized(s):
    m = re.match('.*?(\\d+)$', s)
    if m:
        digit = m.group(1)
        s = s[:s.rfind(digit)]
    else:
        digit = ''
    buf = ['']
    for i in xrange(len(s) - 1, -1, -1):
        buf[0] = s[i] + buf[0]
        if s[i].isupper():
            buf.insert(0, '')

    return buf[0] + ''.join([ c[0] for c in buf[1:] ]) + digit


def getRelativePath(path, start):
    if os.path.splitext(start)[-1]:
        start = os.path.dirname(start).replace('\\', '/')
    relpath = os.path.relpath(path, start).replace('\\', '/')
    if not relpath.startswith('../'):
        relpath = './' + relpath
    return relpath


def getAbsolutePath(path, start):
    path = path.replace('\\', '/')
    if not os.path.isdir(start):
        start = os.path.dirname(start).replace('\\', '/')
    else:
        start = start.replace('\\', '/')
    return os.path.abspath(os.path.join(start, path)).replace('\\', '/')