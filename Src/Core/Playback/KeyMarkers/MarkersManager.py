# -*- coding: utf-8 -*-
"""
=============================================================================
MODULE: trigger.py
-----------------------------------------------------------------------------
This is an intermidiate module that triggers all the user actions. It is the
module responsible for communicating with the GUI using the signal/slots
mechanism. That´s the module that need to be imported when the user defines
a hotkey.
-----------------------------------------------------------------------------
USAGE:
# GO TO THE NEXT FRAME (Default Hotkey: X)
from AkAnimShelf.Src.Triggers import trigger as trg
trg.Trigger().go_to_the_next_frame()
-----------------------------------------------------------------------------
AUTHOR:   Leandro Adeodato
VERSION:  v1.0.0 | Maya 2022 | Python 3
=============================================================================
"""