# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\svgParser.py
try:
    from PySide2.QtCore import QPointF, QRectF
    from PySide2.QtGui import QPainterPath, QPolygonF, QTransform
except:
    from PySide.QtCore import QPointF, QRectF
    from PySide.QtGui import QPainterPath, QPolygonF, QTransform

from xml.dom import minidom
import re, math
COMMANDS = set('MmZzLlHhVvCcSsQqTtAa')
COMMAND_RE = re.compile('([MmZzLlHhVvCcSsQqTtAa])')
FLOAT_RE = re.compile('[-+]?[0-9]*\\.?[0-9]+(?:[eE][-+]?[0-9]+)?')

def _tokenize_path(pathdef):
    for x in COMMAND_RE.split(pathdef):
        if x in COMMANDS:
            yield x
        for token in FLOAT_RE.findall(x):
            yield token


def _tokenize_path_replace(pathdef):
    pathdef = pathdef.replace('e-', 'NEGEXP').replace('E-', 'NEGEXP')
    pathdef = pathdef.replace(',', ' ').replace('-', ' -')
    pathdef = pathdef.replace('NEGEXP', 'e-')
    for c in COMMANDS:
        pathdef = pathdef.replace(c, ' %s ' % c)

    return pathdef.split()


def getAllSvgTags(doc):

    def checkTagName(root, list_data = []):
        if root.childNodes:
            for node in root.childNodes:
                if node.nodeType == node.ELEMENT_NODE:
                    if node.tagName in ('path', 'circle', 'ellipse', 'rect', 'polygon'):
                        list_data.append(node)
                    checkTagName(node, list_data)

    root = doc.documentElement
    l = []
    checkTagName(root, l)
    return l


def getStyleTag(doc):
    root = doc.documentElement
    for node in root.childNodes:
        if node.nodeType == node.ELEMENT_NODE and node.tagName == 'style':
            result = {}
            for data in node.firstChild.data.strip().split():
                m = re.match('^\\.(.+)\\{(.+)\\}$', data)
                if m:
                    result[m.group(1)] = dict([ s.split(':') for s in m.group(2).split(';') if s ])

            return ('styleElement', result)
    else:
        return ('styleAttribute', {})


def getPathOrderFromSvgFile(svgFile):
    doc = minidom.parse(svgFile)
    styleType, styleRef = getStyleTag(doc)
    allSvgTags = getAllSvgTags(doc)
    result = []
    for tag in allSvgTags:
        id = tag.getAttribute('id').replace('_x5F_', '_')
        if not id:
            id = None
        styleDict = {}
        if styleType == 'styleElement' and tag.hasAttribute('class'):
            style = tag.getAttribute('class')
            if style in styleRef:
                styleDict = styleRef[style]
        elif styleType == 'styleAttribute':
            if tag.hasAttribute('style'):
                style = tag.getAttribute('style')
                styleDict = dict([ s.split(':') for s in style.split(';') if s ])
            else:
                for attr in ['fill',
                 'stroke',
                 'stroke-width',
                 'display']:
                    if tag.hasAttribute(attr):
                        styleDict[attr] = tag.getAttribute(attr)

        if tag.tagName == 'path':
            path = tag.getAttribute('d')
            pathOrder = decodeSvgPathStringReplace(path)
        elif tag.tagName == 'circle':
            pathOrder = {}
            pathOrder['cx'] = float(tag.getAttribute('cx'))
            pathOrder['cy'] = float(tag.getAttribute('cy'))
            pathOrder['rx'] = float(tag.getAttribute('r'))
            pathOrder['ry'] = float(tag.getAttribute('r'))
        elif tag.tagName == 'ellipse':
            pathOrder = {}
            pathOrder['cx'] = float(tag.getAttribute('cx'))
            pathOrder['cy'] = float(tag.getAttribute('cy'))
            pathOrder['rx'] = float(tag.getAttribute('rx'))
            pathOrder['ry'] = float(tag.getAttribute('ry'))
            pathOrder['transform'] = tag.getAttribute('transform') or ''
        elif tag.tagName == 'rect':
            pathOrder = {}
            x = tag.getAttribute('x')
            pathOrder['x'] = x and float(x) or 0.0
            y = tag.getAttribute('y')
            pathOrder['y'] = y and float(y) or 0.0
            pathOrder['w'] = float(tag.getAttribute('width'))
            pathOrder['h'] = float(tag.getAttribute('height'))
            rx = tag.getAttribute('rx')
            pathOrder['rx'] = rx and float(rx) or 0.0
            ry = tag.getAttribute('ry')
            pathOrder['ry'] = ry and float(ry) or 0.0
            pathOrder['transform'] = tag.getAttribute('transform') or ''
        elif tag.tagName == 'polygon':
            pathOrder = {}
            points = tag.getAttribute('points').strip()
            pnt = []
            for seg in points.split(' '):
                x, y = seg.split(',')
                pnt.append(QPointF(float(x), float(y)))

            pathOrder['points'] = pnt
        result.append((styleDict,
         pathOrder,
         tag.tagName,
         id))

    doc.unlink()
    return result


def decodeSvgPathStringReplace(path_string):
    d = _tokenize_path_replace(path_string)
    pathOrder = []
    popData = d[0]
    del d[0]
    while d:
        if popData and popData.isalpha():
            numericBuffer = []
            try:
                num = d[0]
                del d[0]
                while not num.isalpha():
                    numericBuffer.append(float(num))
                    num = d[0]
                    del d[0]

                pathOrder.append((popData, numericBuffer))
                popData = num
            except IndexError:
                pathOrder.append((popData, numericBuffer))

    return pathOrder


def decodeSvgPathString(path_string):
    token = _tokenize_path(path_string)
    pathOrder = []
    d = token.next()
    while token:
        try:
            if d.isalpha():
                numericBuffer = []
                num = token.next()
                while not num.isalpha():
                    numericBuffer.append(float(num))
                    num = token.next()

                pathOrder.append((d, numericBuffer))
                d = num
        except:
            pathOrder.append((d, numericBuffer))
            break

    return pathOrder


def calculateStartAngle(x1, y1, rx, ry, coordAngle, largeArcFlag, sweepFlag, x2, y2):

    def dotproduct(v1, v2):
        return sum((a * b for a, b in zip(v1, v2)))

    def length(v):
        return math.sqrt(dotproduct(v, v))

    def angle(v1, v2):
        return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

    rotatedX1 = math.cos(math.radians(coordAngle)) * ((x1 - x2) / 2) + math.sin(math.radians(coordAngle)) * ((y1 - y2) / 2)
    rotatedY1 = -math.sin(math.radians(coordAngle)) * ((x1 - x2) / 2) + math.cos(math.radians(coordAngle)) * ((y1 - y2) / 2)
    delta = rotatedX1 ** 2 / rx ** 2 + rotatedY1 ** 2 / ry ** 2
    if delta > 1:
        rx *= math.sqrt(delta)
        ry *= math.sqrt(delta)
    var = math.sqrt((rx ** 2 * ry ** 2 - rx ** 2 * rotatedY1 ** 2 - ry ** 2 * rotatedX1 ** 2) / (rx ** 2 * rotatedY1 ** 2 + ry ** 2 * rotatedX1 ** 2))
    if largeArcFlag == sweepFlag:
        var *= -1
    ccx = var * (rx * rotatedY1 / ry)
    ccy = var * -(ry * rotatedX1 / rx)
    cx = math.cos(math.radians(coordAngle)) * ccx - math.sin(math.radians(coordAngle)) * ccy + (x1 + x2) / 2
    cy = math.sin(math.radians(coordAngle)) * ccx + math.cos(math.radians(coordAngle)) * ccy + (y1 + y2) / 2
    startAngle = math.degrees(angle([1, 0], [(rotatedX1 - ccx) / rx, (rotatedY1 - ccy) / ry]))
    startAngleSign = 1 * (rotatedY1 - ccy) / ry - 0 * (rotatedX1 - ccx) / rx
    if startAngleSign == 0:
        startAngleSign = 1.0
    startAngleSign /= abs(startAngleSign)
    startAngle *= startAngleSign
    try:
        sweepAngle = math.degrees(angle([(rotatedX1 - ccx) / rx, (rotatedY1 - ccy) / ry], [(-rotatedX1 - ccx) / rx, (-rotatedY1 - ccy) / ry]))
    except ValueError:
        sweepAngle = 180.0

    sweepAngleSign = (rotatedX1 - ccx) / rx * (-rotatedY1 - ccy) / ry - (rotatedY1 - ccy) / ry * (-rotatedX1 - ccx) / rx
    if sweepAngleSign == 0:
        sweepAngleSign = 1.0
    sweepAngleSign /= abs(sweepAngleSign)
    sweepAngle *= sweepAngleSign
    if sweepFlag == 0 and sweepAngle > 0:
        sweepAngle -= 360
    elif sweepFlag == 1 and sweepAngle < 0:
        sweepAngle += 360
    rect = QRectF(0, 0, rx * 2, ry * 2)
    rect.moveCenter(QPointF(cx, cy))
    return (startAngle, sweepAngle, rect)


def createSvgPath(orders, verbose = False):
    path = QPainterPath()
    for k, order in enumerate(orders):
        if order[0] == 'M' or order[0] == 'm':
            if verbose:
                print k, 'MOVE TO', order[1],
            moveTo(path, *order)
            if verbose:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'C' or order[0] == 'c':
            if verbose:
                print k, 'CUBIC TO', order[1],
            cubicTo(path, *order)
            if verbose:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'S' or order[0] == 's':
            if verbose:
                print k, 'SMOOTH CUBIC TO', order[1],
            smoothCubicTo(path, *order)
            if verbose:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'Q' or order[0] == 'q':
            if verbose:
                print k, 'QUAD TO', order[1],
            quadTo(path, *order)
            if verbose:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'T' or order[0] == 't':
            if verbose:
                print k, 'SMOOTH QUAD TO', order[1],
            smoothQuadTo(path, *order)
            if verbose:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'H' or order[0] == 'h':
            if verbose:
                print k, 'HORIZONTAL LINE TO', order[1],
            horizontalLineTo(path, *order)
            if verbose:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'V' or order[0] == 'v':
            if verbose:
                print k, 'VERTICAL LINE TO', order[1],
            verticalLineTo(path, *order)
            if verbose:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'L' or order[0] == 'l':
            if verbose:
                print k, 'LINE TO', order[1],
            lineTo(path, *order)
            if verbose:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'A' or order[0] == 'a':
            if verbose:
                print k, 'ARC TO', order[1],
            arcTo(path, *order)
            if verbose:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'z' or order[0] == 'Z':
            if verbose:
                print k, 'close sub path',
            path.closeSubpath()
            if verbose:
                print path.elementAt(path.elementCount() - 1).type
        elif verbose:
            print k, order

    if verbose:
        print '------------end-------------'
    return path


def createEllipsePath(data):
    path = QPainterPath()
    path.addEllipse(QPointF(data.get('cx'), data.get('cy')), data.get('rx'), data.get('ry'))
    if 'transform' in data:
        m = re.match('^matrix\\((.+)\\)$', data.get('transform'))
        if m:
            args = [ float(x) for x in m.group(1).split() ]
            if len(args) == 6:
                transform = QTransform(*args)
                path *= transform
    return path


def createRectPath(data):
    path = QPainterPath()
    if data.get('rx') > 0 or data.get('ry'):
        path.addRoundedRect(data.get('x'), data.get('y'), data.get('w'), data.get('h'), data.get('rx'), data.get('ry'))
    else:
        path.addRect(data.get('x'), data.get('y'), data.get('w'), data.get('h'))
    if 'transform' in data:
        m = re.match('^matrix\\((.+)\\)$', data.get('transform'))
        if m:
            args = [ float(x) for x in m.group(1).split() ]
            if len(args) == 6:
                transform = QTransform(*args)
                path *= transform
    return path


def createPolygonPath(data):
    path = QPainterPath()
    polygon = QPolygonF()
    for pt in data.get('points'):
        polygon.append(pt)

    path.addPolygon(polygon)
    return path


def generatePathToSvg(path):
    d = ''
    for i in xrange(path.elementCount()):
        element = path.elementAt(i)
        if element.type == QPainterPath.ElementType.MoveToElement:
            d += 'M%.3f,%.3f' % (element.x, element.y)
        elif element.type == QPainterPath.ElementType.CurveToElement:
            d += 'C%.3f,%.3f,' % (element.x, element.y)
        elif element.type == QPainterPath.ElementType.CurveToDataElement:
            d += '%.3f,%.3f' % (element.x, element.y)
            if path.elementAt(i + 1).type == QPainterPath.ElementType.CurveToDataElement:
                d += ','
        elif element.type == QPainterPath.ElementType.LineToElement:
            d += 'L%.3f,%.3f' % (element.x, element.y)
        else:
            print element.type

    d += 'Z'
    return d


def moveTo(path, cmd, data):
    target = QPointF(*data)
    if cmd.islower():
        currentPos = path.currentPosition()
        target += currentPos
    path.moveTo(target)


def cubicTo(path, cmd, data):
    new1stPos = QPointF(data[0], data[1])
    new2stPos = QPointF(data[2], data[3])
    newEndPos = QPointF(data[4], data[5])
    if cmd.islower():
        currentPos = path.currentPosition()
        new1stPos += currentPos
        new2stPos += currentPos
        newEndPos += currentPos
    path.cubicTo(new1stPos, new2stPos, newEndPos)


def smoothCubicTo(path, cmd, data):
    elemCount = path.elementCount()
    prevEndX, prevEndY = path.elementAt(elemCount - 1).x, path.elementAt(elemCount - 1).y
    prev2ndX, prev2ndY = path.elementAt(elemCount - 2).x, path.elementAt(elemCount - 2).y
    new1stPos = QPointF(2 * prevEndX - prev2ndX, 2 * prevEndY - prev2ndY)
    new2stPos = QPointF(data[0], data[1])
    newEndPos = QPointF(data[2], data[3])
    if cmd.islower():
        currentPos = path.currentPosition()
        new2stPos += currentPos
        newEndPos += currentPos
    path.cubicTo(new1stPos, new2stPos, newEndPos)


def quadTo(path, cmd, data):
    new1stPos = QPointF(data[0], data[1])
    newEndPos = QPointF(data[2], data[3])
    path.quadTo(new1stPos, newEndPos)
    if cmd.islower():
        currentPos = path.currentPosition()
        new1stPos += currentPos
        newEndPos += currentPos
    path.quadTo(new1stPos, newEndPos)


def smoothQuadTo(path, cmd, data):
    elemCount = path.elementCount()
    prevEndX, prevEndY = path.elementAt(elemCount - 1).x, path.elementAt(elemCount - 1).y
    prev1stX, prev1stY = path.elementAt(elemCount - 2).x, path.elementAt(elemCount - 2).y
    new1stPos = QPointF(2 * prevEndX - prev1stX, 2 * prevEndY - prev1stY)
    newEndPos = QPointF(data[0], data[1])
    if cmd.islower():
        currentPos = path.currentPosition()
        newEndPos += currentPos
    path.quadTo(new1stPos, newEndPos)


def horizontalLineTo(path, cmd, data):
    currentPos = path.currentPosition()
    if cmd.islower():
        target = currentPos + QPointF(data[0], 0)
    else:
        target = QPointF(data[0], currentPos.y())
    path.lineTo(target)


def verticalLineTo(path, cmd, data):
    currentPos = path.currentPosition()
    if cmd.islower():
        target = currentPos + QPointF(0, data[0])
    else:
        target = QPointF(currentPos.x(), data[0])
    path.lineTo(target)


def lineTo(path, cmd, data):
    target = QPointF(*data)
    if cmd.islower():
        currentPos = path.currentPosition()
        target += currentPos
    path.lineTo(target)


def arcTo(path, cmd, data):
    currentPos = path.currentPosition()
    x1, y1 = currentPos.x(), currentPos.y()
    rx, ry, angle, fa, fs, x2, y2 = data
    if cmd.islower():
        x2 += x1
        y2 += y1
    startAngle, sweepAngle, rect = calculateStartAngle(x1, y1, rx, ry, angle, fa, fs, x2, y2)
    path.arcTo(rect, -startAngle, -sweepAngle)


path_string = '\nM97.637,112.634c-13.809,0-25.003,11.194-25.003,25.003\n        c0,13.809,11.194,25.003,25.003,25.003c13.809,0,25.003-11.194,25.003-25.003C122.641,123.828,111.446,112.634,97.637,112.634z\n         M111,153.734c0,0.497,0.231,1.266-0.266,1.266h-7.2c-0.497,0-1.534-0.769-1.534-1.266v-10.2c0-0.497,0.231-0.534-0.266-0.534h-8.2\n        c-0.497,0-1.534,0.037-1.534,0.534v10.2c0,0.497,0.231,1.266-0.266,1.266h-7.2c-0.497,0-1.534-0.769-1.534-1.266v-13.708\n        c0-0.25,0.421-0.489,0.605-0.659l13.253-12.164c0.345-0.321,0.959-0.321,1.304,0l12.828,12.164c0.183,0.17,0.01,0.409,0.01,0.66\n        V153.734z M98.236,125.196c-0.345-0.318-0.875-0.317-1.22,0l-15.401,14.2c-0.166,0.153-0.384,0.238-0.61,0.238h-2.769\n        c-0.82,0-1.213-1.006-0.61-1.562l19.389-17.876c0.345-0.318,0.875-0.318,1.22,0l6.399,5.895v-3.557c0-0.497,0.403-0.9,0.9-0.9h3.2\n        c0.497,0,0.9,0.403,0.9,0.9v8.163l8.006,7.375c0.603,0.555,0.21,1.562-0.61,1.562h-2.77c-0.226,0-0.444-0.085-0.61-0.238\n        '
if __name__ == '__main__':
    print getPathOrderFromSvgFile('C:/2nd_picker_interface.svg')