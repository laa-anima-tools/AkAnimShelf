# =========================================================================== #
# User Data                                                                   #
# ---------------------------------------------------------                   #
# SUMMARY:  Stores no persistent data.                                        #
# AUTHOR:   Leandro Adeodato                                                  #
# VERSION:  1.0.0 | Maya 2018 | Python 2                                      #
# =========================================================================== #
import os
import json

import os.path


MODE = 'Mode'
LOOP, STOP, MOVE, EXPAND = 0, 1, 2, 3
SCRIPT_PATH = '/maya/scripts/AkAnimShelf_Data/user_data.json'


class UserData(object):
    playback_mode = {}

    # ============================================================================= #
    # READ DATA                                                                     #
    # ============================================================================= #
    @classmethod
    def read_data(cls):
        homedir = os.path.expanduser("~") + SCRIPT_PATH
        print(homedir)

        # with open(script_path) as f:
        #     data = json.load(f)
        # print(data)
        #
        # flx = json.dumps(data, ensure_ascii=False, indent=4)
        # print(flx)
