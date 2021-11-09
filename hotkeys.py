# ============================================================================= #
# SMART KEY | Alt + S                                                           #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger as trg

import Src.Triggers.trigger2

reload(trg)

Src.Triggers.trigger2.Trigger().smart_key()

# ============================================================================= #
# TOGGLE MOVE MODE | W                                                          #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger
reload(trigger)

Src.Triggers.trigger2.Trigger().toggle_move_mode()

# ============================================================================= #
# TOGGLE MOVE MODE | E                                                          #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger
reload(trigger)

Src.Triggers.trigger2.Trigger().toggle_rotate_mode()

# ============================================================================= #
# TOGGLE MOVE MODE | R                                                          #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger
reload(trigger)

Src.Triggers.trigger2.Trigger().toggle_scale_mode()

# ============================================================================= #
# GO TO THE NEXT FRAME | x                                                      #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger as trg
reload(trg)

Src.Triggers.trigger2.Trigger().go_to_the_next_frame()

# ============================================================================= #
# GO TO THE PREVIOUS FRAME | Z                                                  #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger as trg
reload(trg)

Src.Triggers.trigger2.Trigger().go_to_the_prev_frame()

# ============================================================================= #
# GO TO THE NEXT KEY | V                                                        #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger as trg
reload(trg)

Src.Triggers.trigger2.Trigger().go_to_the_next_key()

# ============================================================================= #
# GO TO THE PREVIOUS KEY | C                                                    #
# ============================================================================= #
from AkAnimShelf.Src.Triggers import trigger as trg
reload(trg)

Src.Triggers.trigger2.Trigger().go_to_the_prev_key()

