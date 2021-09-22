# Embedded file name: C:\Users\hgkim\Documents\maya\2016\pythons\LocusPicker\svgGenTest.py
from PySide.QtCore import QPointF
from PySide.QtGui import QPainterPath
from svgParser import getPathOrderFromSvgFile

def createSvgPath(orders, showProgress = False):
    path = QPainterPath()
    for k, order in enumerate(orders):
        if order[0] == 'M':
            if showProgress:
                print k, 'MOVE TO', order[1],
            path.moveTo(*order[1])
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'm':
            if showProgress:
                print k, 'move to', order[1],
            currentPos = path.currentPosition()
            target = currentPos + QPointF(*order[1])
            path.moveTo(*order[1])
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'C':
            if showProgress:
                print k, 'CUBIC TO', order[1],
            path.cubicTo(*order[1])
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'c':
            if showProgress:
                print k, 'cubic to', order[1],
            currentPos = path.currentPosition()
            new1stPos = currentPos + QPointF(order[1][0], order[1][1])
            new2stPos = currentPos + QPointF(order[1][2], order[1][3])
            newEndPos = currentPos + QPointF(order[1][4], order[1][5])
            path.cubicTo(new1stPos, new2stPos, newEndPos)
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'S':
            if showProgress:
                print k, 'SMOOTH CUBIC TO', order[1],
            elemCount = path.elementCount()
            prevEndX, prevEndY = path.elementAt(elemCount - 1).x, path.elementAt(elemCount - 1).y
            prev2ndX, prev2ndY = path.elementAt(elemCount - 2).x, path.elementAt(elemCount - 2).y
            new1stX, new1stY = 2 * prevEndX - prev2ndX, 2 * prevEndY - prev2ndY
            path.cubicTo(*([new1stX, new1stY] + order[1]))
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 's':
            if showProgress:
                print k, 'smooth cubic to', order[1],
            elemCount = path.elementCount()
            currentPos = path.currentPosition()
            prevEndX, prevEndY = path.elementAt(elemCount - 1).x, path.elementAt(elemCount - 1).y
            prev2ndX, prev2ndY = path.elementAt(elemCount - 2).x, path.elementAt(elemCount - 2).y
            new1stPos = QPointF(2 * prevEndX - prev2ndX, 2 * prevEndY - prev2ndY)
            new2stPos = currentPos + QPointF(order[1][0], order[1][1])
            newEndPos = currentPos + QPointF(order[1][2], order[1][3])
            path.cubicTo(new1stPos, new2stPos, newEndPos)
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'Q':
            if showProgress:
                print k, 'QUAD TO', order[1],
            path.quadTo(*order[1])
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'q':
            if showProgress:
                print k, 'quad to', order[1],
            currentPos = path.currentPosition()
            new1stPos = currentPos + QPointF(order[1][0], order[1][1])
            newEndPos = currentPos + QPointF(order[1][2], order[1][3])
            path.quadTo(new1stPos, newEndPos)
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'T':
            if showProgress:
                print k, 'SMOOTH QUAD TO', order[1],
            elemCount = path.elementCount()
            prevEndX, prevEndY = path.elementAt(elemCount - 1).x, path.elementAt(elemCount - 1).y
            prev1stX, prev1stY = path.elementAt(elemCount - 2).x, path.elementAt(elemCount - 2).y
            new1stX, new1stY = 2 * prevEndX - prev1stX, 2 * prevEndY - prev1stY
            path.quadTo(*([new1stX, new1stY] + order[1]))
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 't':
            if showProgress:
                print k, 'smooth quad to', order[1],
            elemCount = path.elementCount()
            currentPos = path.currentPosition()
            prevEndX, prevEndY = path.elementAt(elemCount - 1).x, path.elementAt(elemCount - 1).y
            prev1stX, prev1stY = path.elementAt(elemCount - 2).x, path.elementAt(elemCount - 2).y
            new1stPos = QPointF(2 * prevEndX - prev1stX, 2 * prevEndY - prev1stY)
            newEndPos = currentPos + QPointF(order[1][0], order[1][1])
            path.quadTo(new1stPos, newEndPos)
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'H':
            if showProgress:
                print k, 'HORIZONTAL LINE TO', order[1],
            currentPos = path.currentPosition()
            target = QPointF(order[1][0], currentPos.y())
            path.lineTo(target)
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'h':
            if showProgress:
                print k, 'horizontal line to', order[1],
            currentPos = path.currentPosition()
            target = currentPos + QPointF(order[1][0], 0)
            path.lineTo(target)
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'V':
            if showProgress:
                print k, 'VERTICAL LINE TO', order[1],
            currentPos = path.currentPosition()
            target = QPointF(currentPos.x(), order[1][0])
            path.lineTo(target)
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'v':
            if showProgress:
                print k, 'vertical line to', order[1],
            currentPos = path.currentPosition()
            target = currentPos + QPointF(0, order[1][0])
            path.lineTo(target)
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'L':
            if showProgress:
                print k, 'LINE TO', order[1],
            path.lineTo(*order[1])
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'l':
            if showProgress:
                print k, 'line to', order[1],
            currentPos = path.currentPosition()
            target = currentPos + QPointF(*order[1])
            path.lineTo(target)
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif order[0] == 'z' or order[0] == 'Z':
            if showProgress:
                print k, 'close sub path',
            path.closeSubpath()
            if showProgress:
                print path.elementAt(path.elementCount() - 1).type
        elif showProgress:
            print k, order

    if showProgress:
        print '------------end-------------'
    return path


for style, path in getPathOrderFromSvgFile('C:/Users/hgkim/workspace/LocusPicker/src/resources/icons/test_vector_icons.svg'):
    madePath = createSvgPath(path)
    madePath.translate(madePath.boundingRect().topLeft() * -1)
    print style, madePath.boundingRect()