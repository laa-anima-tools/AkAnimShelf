from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class KeyMarkers(QtWidgets.QWidget):

    KEYFRAME_COLOR = QtGui.QColor(QtCore.Qt.green)

    def __init__(self):
        self.time_control = mel.eval("$tempVar = $gPlayBackSlider")
        time_control_ptr = omui.MQtUtil.findControl(self.time_control)
        time_control_widget = wrapInstance(long(time_control_ptr), QtWidgets.QWidget)

        super(KeyMarkers, self).__init__(time_control_widget)

        self.frame_times = [1, 6, 8, 10, 19, 30, 39, 50, 51, 52, 53, 54, 120]

        self.set_context_menu_enabled(False)

    def add_frame(self):
        current_time = cmds.currentTime(q=True)
        if current_time not in self.frame_times:
            self.frame_times.append(current_time)
            self.update()

    def add_frames(self):
        selected_range = self.get_selected_range()
        for frame_time in range(selected_range[0], selected_range[1]):
            if frame_time not in self.frame_times:
                self.frame_times.append(frame_time)

        self.update()

    def remove_frame(self):
        current_time = cmds.currentTime(q=True)
        if current_time in self.frame_times:
            self.frame_times.remove(current_time)
            self.update()

    def remove_frames(self):
        selected_range = self.get_selected_range()
        for frame_time in range(selected_range[0], selected_range[1]):
            if frame_time in self.frame_times:
                self.frame_times.remove(frame_time)

        self.update()

    def get_selected_range(self):
        selected_range = cmds.timeControl(self.time_control, q=True, rangeArray=True)
        return [int(selected_range[0]), int(selected_range[1])]

    def set_context_menu_enabled(self, enabled):
        self.context_menu_enabled = enabled

    def mousePressEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.RightButton:
            if self.context_menu_enabled:

                context_menu = QtWidgets.QMenu()

                title_action = context_menu.addAction("Timeline Overlay")
                title_action.setDisabled(True)
                context_menu.addSeparator()

                action = context_menu.addAction("Add Frame")
                action.triggered.connect(self.add_frame)

                action = context_menu.addAction("Add Frames")
                action.triggered.connect(self.add_frames)

                context_menu.addSeparator()

                action = context_menu.addAction("Remove Frame")
                action.triggered.connect(self.remove_frame)

                action = context_menu.addAction("Remove Frames")
                action.triggered.connect(self.remove_frames)

                context_menu.exec_(self.mapToGlobal(mouse_event.pos()))

                return

        mouse_event.ignore()

    def mouseReleaseEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.RightButton:
            if self.context_menu_enabled:

                return

        mouse_event.ignore()

    def paintEvent(self, paint_event):
        parent = self.parentWidget()
        if parent:
            self.setGeometry(parent.geometry())

            range_start = cmds.playbackOptions(q=True, minTime=True)
            range_end = cmds.playbackOptions(q=True, maxTime=True)
            displayed_frame_count = range_end - range_start + 1

            padding = self.width() * 0.005
            frame_width = (self.width() * 0.99) / displayed_frame_count

            frame_height = 0.333 * self.height()
            frame_y = self.height() - frame_height

            painter = QtGui.QPainter(self)

            pen = painter.pen()
            pen.setWidth(1)
            pen.setColor(KeyMarkers.KEYFRAME_COLOR)
            painter.setPen(pen)

            fill_color = QtGui.QColor(KeyMarkers.KEYFRAME_COLOR)
            fill_color.setAlpha(63)

            for frame_time in self.frame_times:
                frame_x = padding + ((frame_time - range_start) * frame_width) + 0.5

                painter.fillRect(frame_x, frame_y, frame_width, frame_height, fill_color)
                painter.drawRect(frame_x, frame_y, frame_width, frame_height)



if __name__ == "__main__":
    try:
        KeyMarkersDialog.delete_overlays() # pylint: disable=E0601
    except:
        pass


class KeyMarkersDialog(QtWidgets.QDialog):

    WINDOW_TITLE = "Timeline Overlay"

    timeline_overlay = None

    @classmethod
    def delete_overlays(cls):
        if KeyMarkersDialog.timeline_overlay:
            KeyMarkersDialog.timeline_overlay.setParent(None)
            KeyMarkersDialog.timeline_overlay.deleteLater()
            KeyMarkersDialog.timeline_overlay = None

    def __init__(self, parent=maya_main_window()):
        super(KeyMarkersDialog, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumSize(280, 160)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.set_overlay_visible(True)

    def create_widgets(self):
        self.overlay_visible_cb = QtWidgets.QCheckBox("Show Overlay")

        self.context_menu_cb = QtWidgets.QCheckBox("Context Menu Enabled")
        self.context_menu_cb.setChecked(True)

        self.add_frame_btn = QtWidgets.QPushButton("Add Frame")
        self.remove_frame_btn = QtWidgets.QPushButton("Remove Frame")

        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layout(self):
        frame_layout = QtWidgets.QHBoxLayout()
        frame_layout.setSpacing(4)
        frame_layout.addWidget(self.add_frame_btn)
        frame_layout.addWidget(self.remove_frame_btn)
        frame_layout.addStretch()

        overlay_layout = QtWidgets.QVBoxLayout()
        overlay_layout.addWidget(self.overlay_visible_cb)
        overlay_layout.addWidget(self.context_menu_cb)
        overlay_layout.addLayout(frame_layout)

        options_grp = QtWidgets.QGroupBox("Overlay Options")
        options_grp.setLayout(overlay_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(options_grp)
        main_layout.addStretch()
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.overlay_visible_cb.toggled.connect(self.set_overlay_visible)

        self.close_btn.clicked.connect(self.close)

    def set_overlay_visible(self, visible):
        if visible:
            if not KeyMarkersDialog.timeline_overlay:
                KeyMarkersDialog.timeline_overlay = KeyMarkers()
                KeyMarkersDialog.timeline_overlay.set_context_menu_enabled(self.context_menu_cb.isChecked())

                self.context_menu_cb.toggled.connect(KeyMarkersDialog.timeline_overlay.set_context_menu_enabled)
                self.add_frame_btn.clicked.connect(KeyMarkersDialog.timeline_overlay.add_frame)
                self.remove_frame_btn.clicked.connect(KeyMarkersDialog.timeline_overlay.remove_frame)


        if KeyMarkersDialog.timeline_overlay:
            KeyMarkersDialog.timeline_overlay.setVisible(visible)

        self.overlay_visible_cb.setChecked(visible)



if __name__ == "__main__":

    try:
        overlay_dialog.close() # pylint: disable=E0601
        overlay_dialog.deleteLater()
    except:
        pass

    overlay_dialog = KeyMarkersDialog()
    overlay_dialog.show()
