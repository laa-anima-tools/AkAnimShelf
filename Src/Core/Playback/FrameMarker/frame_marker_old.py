# =========================================================================== #
# frame_marker.py                                                             #
# ---------------------------------------------------------                   #
# SUMMARY:  Add, edit or delete markers on the selected frames.               #
# AUTHOR:   Leandro Adeodato                                                  #
# VERSION:  1.0.0 | Maya 2018 | Python 2                                      #
# =========================================================================== #
import json
import maya.cmds as cmd
import maya.mel as mel
import maya.OpenMaya as opm
import maya.OpenMayaUI as mui
from shiboken2 import wrapInstance

from PySide2 import QtWidgets as wdg
from PySide2 import QtGui as gui
from PySide2 import QtCore as cor

from AkAnimShelf.Src.Utils import maya_widgets_utils as mwu; reload(mwu)
from AkAnimShelf.Src.Data import scene_data as scn; reload(scn)

FRAMES, TYPES = 0, 1
KEY, BREAKDOWN, INBETWEEN, ALL = 0, 1, 2, 3
TIME_CONTROL_OBJ = "$gPlayBackSlider"

global AK_FRAME_MARKER


class FrameMarker(wdg.QWidget):

    def __init__(self):
        self.time_control = mwu.MayaWidgetsUtils.get_maya_control(TIME_CONTROL_OBJ)
        self.time_control_widget = mwu.MayaWidgetsUtils.get_maya_control_widget(TIME_CONTROL_OBJ)
        super(FrameMarker, self).__init__(self.time_control_widget)

        self.markers_colors = {
            KEY: gui.QColor(cor.Qt.red),
            BREAKDOWN: gui.QColor(cor.Qt.green),
            INBETWEEN: gui.QColor(cor.Qt.yellow)
        }

        self.markers = {
            FRAMES: [],
            TYPES: []
        }


        self._scene_data = scn.SceneData()
        # self._scene_data.store_scene_data('ak_frame_markers', self.markers)
        self.markers = self._scene_data.load_scene_data('ak_frame_markers')
        #print self.markers
        #self.markers = [[1, KEY], [4, BREAKDOWN], [7, INBETWEEN], [10, KEY]]
        # self.markers = {
        #     1: KEY,
        #     4: BREAKDOWN,
        #     7: INBETWEEN,
        #     10: KEY
        # }
        self.add_frame_marker(KEY)

    # =========================================================================== #
    # Refresh Markers                                                             #
    # =========================================================================== #
    def refresh_markers(self):
        self._scene_data.store_scene_data('ak_frame_markers', self.markers)
        self.update()

    # =========================================================================== #
    # Add Frame Marker                                                            #
    # =========================================================================== #
    def add_frame_marker(self, marker_type):
        markers_times = self.get_markers_times(KEY)
        frame_times = self.get_selected_frame_times()
        for frame_time in frame_times:
            if frame_time not in markers_times:
                self.markers[str(frame_time)] = marker_type
        print self.markers
        self.refresh_markers()

    def remove_frame_marker(self, marker_type):
        pass

    # =========================================================================== #
    # Clear Selected Frame Markers                                                #
    # =========================================================================== #
    def clear_selected_frame_markers(self):
        frame_times = self.get_selected_frame_times()
        for marker in self.markers:
            #print marker[FRAME]
            self.markers.remove(marker)
            # if marker[FRAME] in frame_times:
            #     del self.markers[index]
        self.refresh_markers()

    # =========================================================================== #
    # Clear All Frame Markers                                                     #
    # =========================================================================== #
    def clear_all_frame_markers(self):
        self.markers = []
        self.refresh_markers()



    def get_markers_times(self, marker_type):
        if marker_type == ALL:
            return sorted(self.markers.keys())
        markers_times = []
        for marker in sorted(self.markers.keys()):
            if self.markers[marker] == marker_type:
                markers_times.append(marker)
        return markers_times


    def get_selected_frame_times(self):
        selected_range = self.get_selected_range()
        frame_times = []
        for frame_time in range(selected_range[0], selected_range[1]):
            frame_times.append(frame_time)
        return frame_times

    def get_selected_range(self):
        selected_range = cmd.timeControl(self.time_control, q=True, rangeArray=True)
        return [int(selected_range[0]), int(selected_range[1])]


    def paintEvent(self, paint_event):
        pass
        # self.draw_frame_markers(KEY)
        # self.draw_frame_markers(BREAKDOWN)
        # self.draw_frame_markers(INBETWEEN)

    def draw_frame_markers(self, marker_type):
        parent = self.parentWidget()
        if parent:
            self.setGeometry(parent.geometry())

            range_start = cmd.playbackOptions(q=True, minTime=True)
            range_end = cmd.playbackOptions(q=True, maxTime=True)
            displayed_frame_count = range_end - range_start + 1

            padding = self.width() * 0.005
            frame_width = (self.width() * 0.99) / displayed_frame_count
            frame_height = 0.25 * self.height()
            frame_y = self.height() - frame_height

            painter = gui.QPainter(self)
            pen = painter.pen()
            pen.setWidth(1)
            pen.setColor(self.markers_colors[marker_type])
            painter.setPen(pen)

            fill_color = self.markers_colors[marker_type]
            fill_color.setAlpha(75)

            # for frame_time in self.data[marker_type]:
            marker_times = self.get_markers_times(marker_type)
            for marker_time in marker_times:
                print marker_time
                frame_x = padding + ((float(marker_time) - range_start) * frame_width) + 0.5
                painter.fillRect(frame_x, frame_y, frame_width, frame_height, fill_color)
                painter.drawRect(frame_x, frame_y, frame_width, frame_height)


def load_frame_markers():
    global AK_FRAME_MARKER

    try:
        AK_FRAME_MARKER.setParent(None)
        AK_FRAME_MARKER.deleteLater()
        AK_FRAME_MARKER = None
    except:
        pass

    parent = mwu.MayaWidgetsUtils.get_maya_control(TIME_CONTROL_OBJ)
    AK_FRAME_MARKER = FrameMarker()
    AK_FRAME_MARKER.setVisible(True)