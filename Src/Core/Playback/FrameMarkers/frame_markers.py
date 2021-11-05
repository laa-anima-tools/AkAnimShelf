from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

from AkAnimShelf.Src.Data import scene_data
reload(scene_data)

KEY, BREAKDOWN, INBETWEEN = 0, 1, 2


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class FrameMarkers(QtWidgets.QWidget):

    KEYFRAME_COLOR = QtGui.QColor(QtCore.Qt.green)

    def __init__(self):
        self.time_control = mel.eval("$tempVar = $gPlayBackSlider")
        time_control_ptr = omui.MQtUtil.findControl(self.time_control)
        time_control_widget = wrapInstance(long(time_control_ptr), QtWidgets.QWidget)

        self._scene_data = scene_data.SceneData()

        super(FrameMarkers, self).__init__(time_control_widget)

        self.markers_colors = {
            KEY: QtGui.QColor(QtCore.Qt.red),
            BREAKDOWN: QtGui.QColor(QtCore.Qt.green),
            INBETWEEN: QtGui.QColor(QtCore.Qt.yellow)
        }

        self.data = self._scene_data.load_scene_data('markers')

        self.frame_times = [1, 4, 7, 10, 19, 30, 39, 50, 51, 52, 53, 54, 120]
        # self.frame_times = self._scene_data.store_scene_data('markers', self.data)
        # self.frame_times = self._scene_data.load_scene_data('markers')
        print self.frame_times

    def add_frame_marker(self, marker_type):
        frame_times = self.get_selected_frame_times()
        try:
            markers = self._scene_data.load_scene_data('markers')[marker_type]
            markers = list(set(markers + frame_times))
        except:
            markers = frame_times

        self.data[marker_type] = sorted(markers)
        self._scene_data.store_scene_data('markers', self.data)
        print self.data
        self.update()

    def add_frame_markers_on_keys(self, marker_type):
        pass

    def remove_frame_marker(self):
        pass


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

    def get_selected_frame_times(self):
        selected_range = self.get_selected_range()
        frame_times = []
        for frame_time in range(selected_range[0], selected_range[1]):
            frame_times.append(frame_time)
        return frame_times


    def paintEvent(self, paint_event):
        # self.draw_frame_markers(KEY)
        self.draw_frame_markers(BREAKDOWN)
        # self.draw_frame_markers(INBETWEEN)

    def draw_frame_markers(self, marker_type):
        parent = self.parentWidget()
        if parent:
            self.setGeometry(parent.geometry())

            range_start = cmds.playbackOptions(q=True, minTime=True)
            range_end = cmds.playbackOptions(q=True, maxTime=True)
            displayed_frame_count = range_end - range_start + 1

            padding = self.width() * 0.005
            frame_width = (self.width() * 0.99) / displayed_frame_count
            frame_height = 0.25 * self.height()
            frame_y = self.height() - frame_height

            painter = QtGui.QPainter(self)
            pen = painter.pen()
            pen.setWidth(1)
            pen.setColor(self.markers_colors[marker_type])
            painter.setPen(pen)

            fill_color = self.markers_colors[marker_type]
            fill_color.setAlpha(75)

            for frame_time in self.data[marker_type]:
                frame_x = padding + ((frame_time - range_start) * frame_width) + 0.5
                painter.fillRect(frame_x, frame_y, frame_width, frame_height, fill_color)
                painter.drawRect(frame_x, frame_y, frame_width, frame_height)

if __name__ == "__main__":
    try:
        frame_markers.setParent(None)
        frame_markers.deleteLater()
        frame_markers = None
    except:
        pass

    frame_markers = FrameMarkers()
    frame_markers.setVisible(True)
    # frame_markers.add_frame_marker(KEY)
    frame_markers.add_frame_marker(BREAKDOWN)
    # frame_markers.add_frame_marker(INBETWEEN)
    # frame_markers.add_frame()
    # frame_markers.remove_frames()
    # print frame_markers.get_selected_range()


