from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui


def maya_main_window():
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


# class KeyMarkersDialog(QtWidgets.QDialog):
#
#     timeline_overlay = None
#
#     @classmethod
#     def delete_overlays(cls):
#         if KeyMarkersDialog.timeline_overlay:
#             KeyMarkersDialog.timeline_overlay.setParent(None)
#             KeyMarkersDialog.timeline_overlay.deleteLater()
#             KeyMarkersDialog.timeline_overlay = None
#
#     def __init__(self, parent=maya_main_window()):
#         super(KeyMarkersDialog, self).__init__(parent)
#         self.set_overlay_visible(True)
#
#
#     def set_overlay_visible(self, visible):
#         if visible:
#             if not KeyMarkersDialog.timeline_overlay:
#                 KeyMarkersDialog.timeline_overlay = KeyMarkers()
#
#         if KeyMarkersDialog.timeline_overlay:
#             KeyMarkersDialog.timeline_overlay.setVisible(visible)
#
#
# if __name__ == "__main__":
#
#     try:
#         overlay_dialog.close() # pylint: disable=E0601
#         overlay_dialog.deleteLater()
#     except:
#         pass
#
#     overlay_dialog = KeyMarkersDialog()


class KeyMarkersDialog(object):

    timeline_overlay = None

    @classmethod
    def delete_overlays(cls):
        if KeyMarkersDialog.timeline_overlay:
            KeyMarkersDialog.timeline_overlay = None

    def __init__(self):
        super(KeyMarkersDialog, self).__init__()
        self.set_overlay_visible(True)

    def set_overlay_visible(self, visible):
        if visible:
            if not KeyMarkersDialog.timeline_overlay:
                KeyMarkersDialog.timeline_overlay = KeyMarkers()

        if KeyMarkersDialog.timeline_overlay:
            KeyMarkersDialog.timeline_overlay.setVisible(visible)


if __name__ == "__main__":

    try:
        overlay_dialog.close() # pylint: disable=E0601
        overlay_dialog.deleteLater()
    except:
        pass

    overlay_dialog = KeyMarkersDialog()