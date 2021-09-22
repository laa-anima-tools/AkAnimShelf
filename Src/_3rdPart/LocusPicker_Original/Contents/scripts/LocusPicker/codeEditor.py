# Embedded file name: C:/ProgramData/Autodesk/ApplicationPlugins/LocusPicker/Contents/scripts\LocusPicker\codeEditor.py
try:
    from PySide2.QtCore import Qt, QSize, QRect
    from PySide2.QtWidgets import QPlainTextEdit, QWidget, QTextEdit, QApplication
    from PySide2.QtGui import QColor, QTextFormat, QPainter, QKeySequence, QTextCursor, QFont, QFontMetrics, QFontDatabase
except:
    from PySide.QtCore import Qt, QSize, QRect
    from PySide.QtGui import QPlainTextEdit, QWidget, QTextEdit, QColor, QTextFormat, QPainter, QKeySequence, QApplication, QTextCursor, QFont, QFontMetrics, QFontDatabase, QDropEvent

import sys

class CodeEditor(QPlainTextEdit):
    MARGIN = 2
    MEL = 1
    PYTHON = 2

    def __init__(self, parent = None):
        super(CodeEditor, self).__init__(parent)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        db = QFontDatabase()
        allFonts = db.families(QFontDatabase.Latin)
        for family in ['Source Code Pro', 'Consolas', 'Courier New']:
            if family in allFonts:
                font = QFont(family, 9)
                self.setFont(font)
                fm = QFontMetrics(font)
                self.setTabStopWidth(fm.width('9') * 2)
                break

        self.mode = CodeEditor.MEL
        self.lineNumerArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumerArea)
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top()) + CodeEditor.MARGIN
        if sys.exec_prefix.find('Maya') > 0:
            top -= 1
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = unicode(blockNumber + 1)
                painter.setPen(sys.exec_prefix.find('Maya') > 0 and Qt.lightGray or Qt.black)
                painter.drawText(0, top, self.lineNumerArea.width(), self.fontMetrics().height(), Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def lineNumberAreaWidth(self):
        digits = 1
        _max = max(1, self.blockCount())
        while _max >= 10:
            _max /= 10
            digits += 1

        space = self.fontMetrics().width('9') * digits + CodeEditor.MARGIN
        return space

    def resizeEvent(self, event):
        super(CodeEditor, self).resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumerArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def updateLineNumberAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.lineNumberAreaWidth() + CodeEditor.MARGIN, 0, 0, 0)

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = sys.exec_prefix.find('Maya') > 0 and QColor(Qt.yellow).darker(180) or QColor(Qt.yellow).lighter(150)
            lineColor.setAlpha(225)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumerArea.scroll(0, dy)
        else:
            self.lineNumerArea.update(0, rect.y(), self.lineNumerArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def setMode(self, mode):
        self.mode = mode

    def keyPressEvent(self, event):
        key = event.key()
        isEnter = key == Qt.Key_Return or key == Qt.Key_Enter
        if isEnter:
            tab = False
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            tabCount = 0
            while text.startswith('\t'):
                text = text[1:]
                tabCount += 1

            if self.textCursor().atBlockEnd():
                if self.mode == CodeEditor.PYTHON and text and text[-1] == ':' or self.mode == CodeEditor.MEL and text and text[-1] == '{':
                    tab = True
        elif event.matches(QKeySequence.Paste):
            clipboard = QApplication.clipboard()
            text = clipboard.text().replace('    ', '\t')
            clipboard.clear()
            clipboard.setText(text)
        super(CodeEditor, self).keyPressEvent(event)
        if isEnter:
            self.textCursor().insertText('\t' * tabCount)
            if tab:
                self.textCursor().insertText('\t')
                if self.mode == CodeEditor.MEL:
                    self.textCursor().insertText('\n}')
                    self.moveCursor(QTextCursor.Up)
                    self.moveCursor(QTextCursor.EndOfLine)


class LineNumberArea(QWidget):

    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = CodeEditor()
    w.show()
    w.setMode(CodeEditor.PYTHON)
    app.exec_()