"""
=============================================================================
MODULE: playback_tools.py
-----------------------------------------------------------------------------
Add extra functionality to Maya's playback. This module must be used by the
trigger module, SHOULD NOT BE USED DIRECTLY.
-----------------------------------------------------------------------------
AUTHOR:   Leandro Adeodato
VERSION:  v1.0.0 | Maya 2018 | Python 2
=============================================================================
"""
import maya.cmds as cmd
import json
import PySide2.QtCore as cor

from AkAnimShelf.Src.Utils import playback_utils
from AkAnimShelf.Src.Data import playback_data
from timeline_marker.ui import TimelineMarker

reload(playback_utils)

TIMEOUT = 100
LOOP, STOP, MOVE, EXPAND = 0, 1, 2, 3
KEY, BREAKDOWN, INBETWEEN = 0, 1, 2
RED, GREEN, YELLOW = (255, 0, 0), (0, 255, 0), (255, 255, 0)
COLOR, TYPE = 0, 1

TIMELINE_MARKER = "timeline-marker"


class PlaybackTools(object):
    pressed = True

    def __init__(self):
        self._playback_utils = playback_utils.PlaybackUtils()
        self._playback_data = playback_data.PlaybackData()

        self.timer = cor.QTimer()
        self.timeout = TIMEOUT
        self._playback_mode = self._playback_data.get_playback_mode()

        self.timeline_markers = {
            KEY: [RED, 'key'],
            BREAKDOWN: [GREEN, 'breakdown'],
            INBETWEEN: [YELLOW, 'inbetween']
        }

    # ============================================================================= #
    # STATIC METHODS                                                                #
    # ============================================================================= #
    @staticmethod
    def get_pressed_state():
        return PlaybackTools.pressed

    @staticmethod
    def set_pressed_state(state=True):
        PlaybackTools.pressed = state

    @staticmethod
    def is_playing():
        return cmd.play(q=True, state=True)

    @staticmethod
    def play_timeline_forward():
        if PlaybackTools.get_pressed_state():
            cmd.play(forward=True)

    @staticmethod
    def play_timeline_back():
        if PlaybackTools.get_pressed_state():
            cmd.play(forward=False)

    @staticmethod
    def stop_timeline():
        cmd.play(state=False)

    # ============================================================================= #
    # SWITCH PLAYBACK MODE                                                          #
    # ============================================================================= #
    def switch_playback_mode(self):
        if self._playback_mode == LOOP:
            self._playback_mode = STOP
        elif self._playback_mode == STOP:
            self._playback_mode = MOVE
        elif self._playback_mode == MOVE:
            self._playback_mode = EXPAND
        else:
            self._playback_mode = LOOP

        self._playback_data.set_playback_mode(self._playback_mode)

    # ============================================================================= #
    # GO TO THE NEXT FRAME                                                          #
    # ============================================================================= #
    def go_to_the_next_frame(self):
        playback_start_time = self._playback_utils.get_playback_range()[0]
        playback_end_time = self._playback_utils.get_playback_range()[1]
        animation_end_time = self._playback_utils.get_animation_range()[1]
        next_time = self._playback_utils.get_current_time() + 1

        if self._playback_mode == LOOP:
            if next_time > playback_end_time:
                next_time = playback_start_time
        elif self._playback_mode == STOP:
            if next_time > playback_end_time:
                return
        elif self._playback_mode == MOVE:
            if next_time > animation_end_time:
                return
            if next_time > playback_end_time:
                self._playback_utils.set_playback_range(playback_start_time + 1, playback_end_time + 1)
        elif self._playback_mode == EXPAND:
            if next_time > animation_end_time:
                return
            if next_time > playback_end_time:
                self._playback_utils.set_playback_range(playback_start_time, playback_end_time + 1)
        else:
            cmd.warning('{0} playback mode not defined.'.format(self._playback_mode))

        cmd.undoInfo(state=False)
        self._playback_utils.set_current_time(next_time)
        cmd.undoInfo(state=True)

    # ============================================================================= #
    # GO TO THE PREV FRAME                                                          #
    # ============================================================================= #
    def go_to_the_prev_frame(self):
        playback_start_time = self._playback_utils.get_playback_range()[0]
        playback_end_time = self._playback_utils.get_playback_range()[1]
        animation_start_time = self._playback_utils.get_animation_range()[0]
        prev_time = self._playback_utils.get_current_time() - 1

        if self._playback_mode == LOOP:
            if prev_time < playback_start_time:
                prev_time = playback_end_time
        elif self._playback_mode == STOP:
            if prev_time < playback_start_time:
                return
        elif self._playback_mode == MOVE:
            if prev_time < animation_start_time:
                return
            if prev_time < playback_start_time:
                self._playback_utils.set_playback_range(playback_start_time - 1, playback_end_time - 1)
        elif self._playback_mode == EXPAND:
            if prev_time < animation_start_time:
                return
            if prev_time < playback_start_time:
                self._playback_utils.set_playback_range(playback_start_time - 1, playback_end_time)
        else:
            cmd.warning('{0} playback mode not defined.'.format(self._playback_mode))

        cmd.undoInfo(state=False)
        self._playback_utils.set_current_time(prev_time)
        cmd.undoInfo(state=True)

    # ============================================================================= #
    # NEXT FRAME PLAYBACK                                                           #
    # ============================================================================= #
    def next_frame_playback_press(self):
        cmd.undoInfo(state=False)
        PlaybackTools.set_pressed_state(True)
        self.go_to_the_next_frame()
        timer = cor.QTimer()
        timer.singleShot(TIMEOUT, PlaybackTools.play_timeline_forward)
        cmd.undoInfo(state=True)

    # ============================================================================= #
    # NEXT FRAME PLAYBACK RELEASE                                                   #
    # ============================================================================= #
    def next_frame_playback_release(self):
        cmd.undoInfo(state=False)
        PlaybackTools.set_pressed_state(False)
        if PlaybackTools.is_playing():
            PlaybackTools.stop_timeline()
        cmd.undoInfo(state=True)

    # ============================================================================= #
    # PREV FRAME PLAYBACK PRESS                                                     #
    # ============================================================================= #
    def prev_frame_playback_press(self):
        cmd.undoInfo(state=False)
        PlaybackTools.set_pressed_state(True)
        self.go_to_the_prev_frame()
        timer = cor.QTimer()
        timer.singleShot(TIMEOUT, PlaybackTools.play_timeline_back)
        cmd.undoInfo(state=True)

    # ============================================================================= #
    # PREV FRAME PLAYBACK RELEASE                                                   #
    # ============================================================================= #
    def prev_frame_playback_release(self):
        cmd.undoInfo(state=False)
        PlaybackTools.set_pressed_state(False)
        if PlaybackTools.is_playing():
            PlaybackTools.stop_timeline()
        cmd.undoInfo(state=False)

    # ============================================================================= #
    # NEXT KEY                                                                      #
    # ============================================================================= #
    def next_key(self):
        cmd.undoInfo(state=False)
        next_key = cmd.findKeyframe(timeSlider=True, which="next")
        self._playback_utils.set_current_time(next_key)
        cmd.undoInfo(state=True)

    # ============================================================================= #
    # PREV KEY                                                                      #
    # ============================================================================= #
    def prev_key(self):
        cmd.undoInfo(state=False)
        prev_key = cmd.findKeyframe(timeSlider=True, which="previous")
        self._playback_utils.set_current_time(prev_key)
        cmd.undoInfo(state=True)

    # ============================================================================= #
    # ADD TIMELINE MARKER                                                           #
    # ============================================================================= #
    def add_timeline_marker(self, marker):
        current_time = self._playback_utils.get_current_time()
        TimelineMarker.add(current_time, self.timeline_markers[marker][COLOR], self.timeline_markers[marker][TYPE])

    # ============================================================================= #
    # REMOVE TIMELINE MARKER                                                        #
    # ============================================================================= #
    def remove_timeline_marker(self):
        current_time = self._playback_utils.get_current_time()
        TimelineMarker.remove(current_time)

    # ============================================================================= #
    # LIST MARKERS KEYTIMES                                                          #
    # ============================================================================= #
    def list_markers_keytimes(self, marker_type=KEY):
        data = cmd.fileInfo(TIMELINE_MARKER, query=True)
        data = json.loads(data[0].replace('\\"', '"')) if data else {}
        frame_keytimes = []

        # for frame, frame_data in data.items():
        #     print "{0}{1}".format(frame, frame_data)

        for frame in data.items():
            # frame_keytimes.append(int(frame[0].split('.')[0]))
            frame_keytimes.append(float(frame[0]))

        return sorted(frame_keytimes)

    # ============================================================================= #
    # SHARE KEYS ON MARKERS                                                         #
    # ============================================================================= #
    def share_keys_on_markers(self, marker_type=KEY):
        print(type(self._playback_utils.get_current_time()))
        print(type(self.list_markers_keytimes()[0]))
        print(self.list_markers_keytimes()[0])
        # frame_keytimes = self.list_markers_keytimes()
        # print frame_keytimes

    # ============================================================================= #
    # GO TO THE NEXT MARKER                                                         #
    # ============================================================================= #
    def go_to_the_next_marker(self, marker_type=KEY):
        current_time = self._playback_utils.get_current_time()
        frame_keytimes = self.list_markers_keytimes()

        print "{0} --- {1}".format(current_time, frame_keytimes)

        if current_time in frame_keytimes:
            print ('in')
        else:
            print('out')

        try:
            if current_time == frame_keytimes[-1]:
                self._playback_utils.set_current_time(frame_keytimes[0])
            else:
                i = frame_keytimes.index(current_time)
                self._playback_utils.set_current_time(frame_keytimes[i+1])
        except:
            pass
            # while current_time not in frame_keytimes:
            #     self.go_to_the_next_frame()
            #     current_time = str(self._playback_utils.get_current_time())
            # print "error"

        # for frame in frame_keytimes:
        #
        # if current_time in frame_keytimes:
        #     print "next_marker_in"
        # else:
        #     print "next_marker_out"

    def crop_timeline_left(self):
        current_time = self._playback_utils.get_current_time()
        playback_end_time = self._playback_utils.get_playback_range()[1]
        self._playback_utils.set_playback_range(current_time, playback_end_time)

    def crop_timeline_right(self):
        current_time = self._playback_utils.get_current_time()
        playback_start_time = self._playback_utils.get_playback_range()[0]
        self._playback_utils.set_playback_range(playback_start_time, current_time)

    def center_range_to_cursor(self):
        current_time = self._playback_utils.get_current_time()
        playback_start_time = self._playback_utils.get_playback_range()[0]
        playback_end_time = self._playback_utils.get_playback_range()[1]
        range_length = playback_end_time - playback_start_time

        playback_start_time = current_time - int(range_length / 2)
        playback_end_time = current_time + int(range_length / 2)

        self._playback_utils.set_playback_range(playback_start_time, playback_end_time)

    def center_cursor_to_range(self):
        playback_start_time = self._playback_utils.get_playback_range()[0]
        playback_end_time = self._playback_utils.get_playback_range()[1]
        current_time = playback_start_time + int((playback_end_time - playback_start_time) / 2)

        self._playback_utils.set_current_time(current_time)

    def move_start_time_to_current_frame(self):
        current_time = self._playback_utils.get_current_time()
        playback_start_time = self._playback_utils.get_playback_range()[0]
        offset = current_time - playback_start_time
        playback_end_time = self._playback_utils.get_playback_range()[1] + offset

        self._playback_utils.set_playback_range(current_time, playback_end_time)

    def move_end_time_to_current_frame(self):
        current_time = self._playback_utils.get_current_time()
        playback_end_time = self._playback_utils.get_playback_range()[1]
        offset = playback_end_time - current_time
        playback_start_time = self._playback_utils.get_playback_range()[0] - offset

        self._playback_utils.set_playback_range(playback_start_time, current_time)

