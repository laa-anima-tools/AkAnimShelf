# ============================================================================= #
# SMART KEY | Alt + S                                                           #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger as trg

import Src.Triggers.trigger2


Src.Triggers.trigger2.Trigger().smart_key()

# ============================================================================= #
# TOGGLE MOVE MODE | W                                                          #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger

Src.Triggers.trigger2.Trigger().toggle_move_mode()

# ============================================================================= #
# TOGGLE MOVE MODE | E                                                          #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger

Src.Triggers.trigger2.Trigger().toggle_rotate_mode()

# ============================================================================= #
# TOGGLE MOVE MODE | R                                                          #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger

Src.Triggers.trigger2.Trigger().toggle_scale_mode()

# ============================================================================= #
# GO TO THE NEXT FRAME | x                                                      #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger as trg

Src.Triggers.trigger2.Trigger().go_to_the_next_frame()

# ============================================================================= #
# GO TO THE PREVIOUS FRAME | Z                                                  #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger as trg

Src.Triggers.trigger2.Trigger().go_to_the_prev_frame()

# ============================================================================= #
# GO TO THE NEXT KEY | V                                                        #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger as trg

Src.Triggers.trigger2.Trigger().go_to_the_next_key()

# ============================================================================= #
# GO TO THE PREVIOUS KEY | C                                                    #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger as trg

Src.Triggers.trigger2.Trigger().go_to_the_prev_key()

# ============================================================================= #
# LOAD FRAME MARKERS                                                            #
# ============================================================================= #
from AkAnimShelf.Src.Controllers import playback_ctrl

playback_ctrl.PlaybackController().load_frame_markers()

# ============================================================================= #
# ADD KEY MARKER | K                                                            #
# ============================================================================= #
from AkAnimShelf.Src.Controllers import playback_ctrl

KEY, BREAKDOWN, INBETWEEN = 0, 1, 2

playback_ctrl.PlaybackController().add_frame_markers(KEY)

# ============================================================================= #
# ADD BREAKDOWN MARKER | J                                                      #
# ============================================================================= #
from AkAnimShelf.Src.Controllers import playback_ctrl

KEY, BREAKDOWN, INBETWEEN = 0, 1, 2

playback_ctrl.PlaybackController().add_frame_markers(BREAKDOWN)

# ============================================================================= #
# ADD INBETWEEN MARKER | L                                                      #
# ============================================================================= #
from AkAnimShelf.Src.Controllers import playback_ctrl

KEY, BREAKDOWN, INBETWEEN = 0, 1, 2

playback_ctrl.PlaybackController().add_frame_markers(INBETWEEN)

# ============================================================================= #
# REMOVE FRAME MARKERS                                                          #
# ============================================================================= #
from AkAnimShelf.Src.Controllers import playback_ctrl

playback_ctrl.PlaybackController().remove_frame_markers()

# ============================================================================= #
# CLEAR ALL FRAME MARKERS                                                       #
# ============================================================================= #
from AkAnimShelf.Src.Controllers import playback_ctrl

playback_ctrl.PlaybackController().clear_all_frame_markers()


# ============================================================================= #
# SWITCH HOTKEYS SET                                                            #
# ============================================================================= #
from AkAnimShelf.Src.Controllers import navigation_ctrl

navigation_ctrl.NavigationController().switch_hotkey_set()











