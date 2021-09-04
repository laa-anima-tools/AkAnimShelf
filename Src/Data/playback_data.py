# =========================================================================== #
# Playback Data                                                               #
# ---------------------------------------------------------                   #
# SUMMARY:  Stores no persistent data.                                        #
# AUTHOR:   Leandro Adeodato                                                  #
# VERSION:  1.0.0 | Maya 2018 | Python 2                                      #
# =========================================================================== #
MODE = 'Mode'
LOOP, STOP, MOVE, EXPAND = 0, 1, 2, 3


class PlaybackData(object):
    playback_mode = {}

    @classmethod
    def get_playback_mode(cls):
        return cls.playback_mode.setdefault(MODE, LOOP)

    @classmethod
    def set_playback_mode(cls, mode):
        cls.playback_mode[MODE] = mode

