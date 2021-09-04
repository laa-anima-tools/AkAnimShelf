# =========================================================================== #
# Common Data                                                                 #
# ---------------------------------------------------------                   #
# SUMMARY:   Stores no persistent data.                                       #
# AUTHOR:   Leandro Adeodato                                                  #
# VERSION:  1.0.0 | Maya 2022 | Python 3                                      #
# =========================================================================== #
ICON, ENABLED, CHECKED, QSS_CLASS, MIN_SIZE, MAX_SIZE, TOOLTIP = 0, 1, 2, 3, 4, 5, 6
WIDTH, HEIGHT = 0, 1

comboboxes = {
    'list': {QSS_CLASS: 'ListComboBox', MIN_SIZE: [180, 20], MAX_SIZE: [180, 20]}
}

groupboxes = {
    'subtitle': {QSS_CLASS: 'SubtitleGroupBox', MIN_SIZE: [200, 50], MAX_SIZE: [200, 400]},
    'placeholder': {QSS_CLASS: 'PlaceholderGroupBox', MIN_SIZE: [200, 50], MAX_SIZE: [200, 400]}
}

sliders = {
    'zoom_slider': {QSS_CLASS: 'CameraSlider', MIN_SIZE: [150, 20], MAX_SIZE: [150, 20]},
    'hpan_slider': {QSS_CLASS: 'CameraSlider', MIN_SIZE: [150, 20], MAX_SIZE: [150, 20]},
    'vpan_slider': {QSS_CLASS: 'CameraSlider', MIN_SIZE: [150, 20], MAX_SIZE: [150, 20]}
}

labels = {
    'logo': {ICON: u":/_Logo/logo", ENABLED: True, QSS_CLASS: 'LogoLabel', MIN_SIZE: [200, 32], MAX_SIZE: [200, 32]},
    'title': {QSS_CLASS: 'TitleLabel', MIN_SIZE: [200, 24]},
    'text': {QSS_CLASS: 'TextLabel', MIN_SIZE: [136, 16]}
}

buttons = {
    'menu': {
        ICON: u":/_Logo/menu", ENABLED: True, QSS_CLASS: 'MenuButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: """
        <html><head/><body>
        <p><span style=\" font-size:12px; font-weight:600; color:#FF9648;\">MENU </span></p><hr/>
        <p><span style=\" color:#aaaaaa;\">Not Implemented Yet.</span></p>
        </body></html>"""
    },
    'text': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'toggle': {
        ENABLED: True, QSS_CLASS: 'ToggleButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'tool': {
        ICON: u":/_Logo/menu", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'transform_axis': {
        CHECKED: True, QSS_CLASS: 'CheckButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [16, 16],
        TOOLTIP: 'Tooltip'
    },

    'toggle_move_mode': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: """
         <html><head/><body>
         <p><span style=\" font-size:12px; color:#FF9648;\">TOGGLE </span>
         <span style=\" font-size:12px; font-weight:600; color:#df6e41;\">MOVE </span>
         <span style=\" font-size:12px; color:#FF9648;\">MODE</span></p><hr/>
         <p><span style=\" color:#777777;\">Toggle between </span>
         <span style=\" color:#aaaaaa;\">LOCAL, WORLD and NORMAL</span>
         <span style=\" color:#777777;\">Move Modes.</span></p>
         </body></html>"""
    },
    'toggle_rotate_mode': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: """
         <html><head/><body>
         <p><span style=\" font-size:12px; color:#FF9648;\">TOGGLE </span>
         <span style=\" font-size:12px; font-weight:600; color:#df6e41;\">ROTATE </span>
         <span style=\" font-size:12px; color:#FF9648;\">MODE</span></p><hr/>
         <p><span style=\" color:#777777;\">Toggle between </span>
         <span style=\" color:#aaaaaa;\">LOCAL, WORLD and GIMBAL</span>
         <span style=\" color:#777777;\">Rotate Modes.</span></p>
         </body></html>"""
    },
    'toggle_scale_mode': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: """
         <html><head/><body>
         <p><span style=\" font-size:12px; color:#FF9648;\">TOGGLE </span>
         <span style=\" font-size:12px; font-weight:600; color:#df6e41;\">SCALE </span>
         <span style=\" font-size:12px; color:#FF9648;\">MODE</span></p><hr/>
         <p><span style=\" color:#777777;\">Toggle between </span>
         <span style=\" color:#aaaaaa;\">LOCAL and WORLD</span>
         <span style=\" color:#777777;\">Scale Modes.</span></p>
         </body></html>"""
    },
    'toggle_translate_channels': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: """
        <html><head/><body>
        <p><span style=\" color:#df6e41;\">TOGGLE </span>
        <span style=\" font-size:12px; font-weight:600; color:#FF9648;\">TRANSLATE </span>
        <span style=\" color:#df6e41;\">CHANNELS</span></p><hr/>
        <p><span style=\" color:#aaaaaa;\">Toggle the Translate Channels on the Channel Box.</span></p>
        <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Clic &nbsp;</b></span>
        <span style=\" color:#777777;\">Toggle All.</span></p>
        <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Ctrl + Clic &nbsp;</b></span>
        <span style=\" color:#777777;\">Toggle One by One.</span></p>
        <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Alt + Clic &nbsp;</b></span>
        <span style=\" color:#777777;\">Toggle Two by Two.</span></p>
        </body></html>"""
    },
    'toggle_rotate_channels': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: """
         <html><head/><body>
         <p><span style=\" color:#df6e41;\">TOGGLE </span>
         <span style=\" font-size:12px; font-weight:600; color:#FF9648;\">ROTATE </span>
         <span style=\" color:#df6e41;\">CHANNELS</span></p><hr/>
         <p><span style=\" color:#aaaaaa;\">Toggle the Rotate Channels on the Channel Box.</span></p>
         <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Clic &nbsp;</b></span>
         <span style=\" color:#777777;\">Toggle All.</span></p>
         <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Ctrl + Clic &nbsp;</b></span>
         <span style=\" color:#777777;\">Toggle One by One.</span></p>
         <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Alt + Clic &nbsp;</b></span>
         <span style=\" color:#777777;\">Toggle Two by Two.</span></p>
         </body></html>"""
    },
    'toggle_scale_channels': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: """
         <html><head/><body>
         <p><span style=\" color:#df6e41;\">TOGGLE </span>
         <span style=\" font-size:12px; font-weight:600; color:#FF9648;\">SCALE </span>
         <span style=\" color:#df6e41;\">CHANNELS</span></p><hr/>
         <p><span style=\" color:#aaaaaa;\">Toggle the Scale Channels on the Channel Box.</span></p>
         <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Clic &nbsp;</b></span>
         <span style=\" color:#777777;\">Toggle All.</span></p>
         <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Ctrl + Clic &nbsp;</b></span>
         <span style=\" color:#777777;\">Toggle One by One.</span></p>
         <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Alt + Clic &nbsp;</b></span>
         <span style=\" color:#777777;\">Toggle Two by Two.</span></p>
         </body></html>"""
    },
    'toggle_translate_x_channel': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'toggle_translate_y_channel': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'toggle_translate_z_channel': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'toggle_rotate_x_channel': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'toggle_rotate_y_channel': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'toggle_rotate_z_channel': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'toggle_scale_x_channel': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'toggle_scale_y_channel': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'toggle_scale_z_channel': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'toggle_sync_mode': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'select_all_channels': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: """
         <html><head/><body>
         <p><span style=\" font-size:12px; font-weight:600; color:#FF9648;\">SELECT ALL </span>
         <span style=\" color:#df6e41;\">CHANNELS</span></p><hr/>
         <p><span style=\" color:#aaaaaa;\">Selects All </span>
         <span style=\" color:#777777;\">Transforms Channels on the Channel Box.</span></p>
         </body></html>"""
    },
    'clear_all_channels': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: """
         <html><head/><body>
         <p><span style=\" font-size:12px; font-weight:600; color:#FF9648;\">CLEAR ALL </span>
         <span style=\" color:#df6e41;\">CHANNELS</span></p><hr/>
         <p><span style=\" color:#aaaaaa;\">Clears All </span>
         <span style=\" color:#777777;\">Transforms Channels on the Channel Box.</span></p>
         </body></html>"""
    },
    'set_anim_mode': {
        ENABLED: True, CHECKED: True, QSS_CLASS: 'ToggleButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'set_previs_mode': {
        ENABLED: True, CHECKED: False, QSS_CLASS: 'ToggleButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'toggle_camera_panzoom': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'reset_camera_panzoom': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'apply_transform_on_keys': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'apply_transform_on_frames': {
        ENABLED: True, QSS_CLASS: 'TextButton',
        MIN_SIZE: [16, 16], MAX_SIZE: [100, 16],
        TOOLTIP: 'Tooltip'
    },
    'pull_keys_back': {
        ICON: u":/Keyframing/pull_keys_back", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'nudge_key_back': {
        ICON: u":/Keyframing/nudge_key_back", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'nudge_key_forward': {
        ICON: u":/Keyframing/nudge_key_forward", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'push_keys_forward': {
        ICON: u":/Keyframing/push_keys_forward", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'copy_keys': {
        ICON: u":/Keyframing/copy_keys", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: """
        <html><head/><body>
        <p><span style=\" font-size:12px; font-weight:600; color:#FF9648;\">COPY </span>
        <span style=\" color:#df6e41;\">KEYS</span></p><hr/>
        <p><span style=\" color:#aaaaaa;\">Copy keys from timeline, channelbox or graph editor selection.</span></p>
        <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Clic &nbsp;</b></span>
        <span style=\" color:#777777;\">Copy Keys from Selection.</span></p>
        <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Ctrl + Clic &nbsp;</b></span>
        <span style=\" color:#777777;\">Copy Frames from Selection.</span></p>
        </body></html>"""
    },
    'cut_keys': {
        ICON: u":/Keyframing/cut_keys", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: """
        <html><head/><body>
        <p><span style=\" font-size:12px; font-weight:600; color:#FF9648;\">CUT </span>
        <span style=\" color:#df6e41;\">KEYS</span></p><hr/>
        <p><span style=\" color:#aaaaaa;\">Cut keys from timeline, channelbox or graph editor selection.</span></p>
        <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Clic &nbsp;</b></span>
        <span style=\" color:#777777;\">Cut Keys from Selection.</span></p>
        <p><span style=\" color:#2b2b2b; background:#df6e41;\"><b>&nbsp; Ctrl + Clic &nbsp;</b></span>
        <span style=\" color:#777777;\">Cut Frames from Selection.</span></p>
        </body></html>"""
    },
    'insert_keys': {
        ICON: u":/Keyframing/insert_keys", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: """
        <html><head/><body>
        <p><span style=\" font-size:12px; font-weight:600; color:#FF9648;\">INSERT </span>
        <span style=\" color:#df6e41;\">KEYS</span></p><hr/>
        <p><span style=\" color:#aaaaaa;\">Insert Copied keys on the Current Frame.</span></p>
        </body></html>"""
    },
    'replace_keys': {
        ICON: u":/Keyframing/replace_keys", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: """
        <html><head/><body>
        <p><span style=\" font-size:12px; font-weight:600; color:#FF9648;\">REPLACE </span>
        <span style=\" color:#df6e41;\">KEYS</span></p><hr/>
        <p><span style=\" color:#aaaaaa;\">Replace Existing Keys by the Copied Keys.</span></p>
        </body></html>"""
    },
    'bake_on_ones': {
        ICON: u":/Keyframing/bake_on_ones", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'bake_on_twos': {
        ICON: u":/Keyframing/bake_on_twos", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'bake_on_fours': {
        ICON: u":/Keyframing/bake_on_fours", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'bake_on_markers': {
        ICON: u":/Keyframing/bake_on_markers", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'bake_on_shared_keys': {
        ICON: u":/Keyframing/bake_on_shared_keys", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'bake_on_base_layer_keys': {
        ICON: u":/Keyframing/bake_on_base_layer_keys", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'store_selected_keytimes': {
        ICON: u":/Keyframing/store_selected_keytimes", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'bake_on_stored_keytimes': {
        ICON: u":/Keyframing/bake_on_stored_keytimes", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'next_left_control': {
        ICON: u":/Selection/next_left_control", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'next_up_control': {
        ICON: u":/Selection/next_up_control", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'next_down_control': {
        ICON: u":/Selection/next_down_control", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'next_right_control': {
        ICON: u":/Selection/next_right_control", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'select_all_set': {
        ICON: u":/Selection/select_all_set", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'select_upperbody_set': {
        ICON: u":/Selection/select_upperbody_set", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'select_right_hand_set': {
        ICON: u":/Selection/select_right_hand_set", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'select_left_hand_set': {
        ICON: u":/Selection/select_left_hand_set", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'select_right_arm_set': {
        ICON: u":/Selection/select_right_arm_set", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'select_left_arm_set': {
        ICON: u":/Selection/select_left_arm_set", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'select_right_leg_set': {
        ICON: u":/Selection/select_right_leg_set", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'select_left_leg_set': {
        ICON: u":/Selection/select_left_leg_set", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'toggle_move_all_mode': {
        ICON: u":/Transform/toggle_move_all_mode", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'toggle_ik_mover': {
        ICON: u":/Transform/toggle_ik_mover", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'change_pivot': {
        ICON: u":/Transform/change_pivot", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'micro_transform': {
        ICON: u":/Transform/micro_transform", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'increase_transform': {
        ICON: u":/Transform/increase_transform", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'decrease_transform': {
        ICON: u":/Transform/decrease_transform", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'reset_transforms': {
        ICON: u":/Transform/reset_transforms", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'snap_locator': {
        ICON: u":/Transform/snap_locator", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'copy_transforms': {
        ICON: u":/Transform/copy_transforms", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'paste_transforms': {
        ICON: u":/Transform/paste_transforms", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'align_transforms': {
        ICON: u":/Transform/align_transforms", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'mirror_transforms': {
        ICON: u":/Transform/mirror_transforms", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'transfer_xform': {
        ICON: u":/Transform/transfer_xform", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'flexible_constraints': {
        ICON: u":/Transform/flexible_constraints", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'rotate_character_base': {
        ICON: u":/Transform/rotate_character_base", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'rotate_character_pose': {
        ICON: u":/Transform/rotate_character_pose", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'snap_character_base': {
        ICON: u":/Transform/snap_character_base", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'snap_character_pose': {
        ICON: u":/Transform/snap_character_pose", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'copy_relationship': {
        ICON: u":/Transform/copy_relationship", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'paste_relationship': {
        ICON: u":/Transform/paste_relationship", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'reload_relationship': {
        ICON: u":/Transform/reload_relationship", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'remove_relationship': {
        ICON: u":/Transform/remove_relationship", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'toggle_viewport_mode': {
        ICON: u":/Viewport/toggle_viewport_mode", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'toggle_shot_cameras': {
        ICON: u":/Viewport/toggle_shot_cameras", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'toggle_workspace': {
        ICON: u":/Viewport/toggle_workspace", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'toggle_layout_mode': {
        ICON: u":/Viewport/toggle_layout_mode", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'toggle_hotkey_set': {
        ICON: u":/Viewport/toggle_hotkey_set", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'toggle_expert_mode': {
        ICON: u":/Viewport/toggle_expert_mode", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'filter_objects_visibility': {
        ICON: u":/Viewport/filter_objects_visibility", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'toggle_ortographic_views': {
        ICON: u":/Viewport/toggle_ortographic_views", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'toggle_image_plane_visibility': {
        ICON: u":/Viewport/toggle_image_plane_visibility", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'set_image_plane_to_blocking': {
        ICON: u":/Viewport/set_image_plane_to_blocking", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'create_image_plane': {
        ICON: u":/Viewport/create_image_plane", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'remove_image_plane': {
        ICON: u":/Viewport/remove_image_plane", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'cinematic_editor': {
        ICON: u":/Viewport/cinematic_editor", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'camera_noise_editor': {
        ICON: u":/Viewport/camera_noise_editor", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'tracker_tool': {
        ICON: u":/Viewport/tracker_tool", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'snapshot_tool': {
        ICON: u":/Viewport/snapshot_tool", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'prev_frame': {
        ICON: u":/Playback/prev_frame", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'playback': {
        ICON: u":/Playback/playback", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'play': {
        ICON: u":/Playback/play", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'next_frame': {
        ICON: u":/Playback/next_frame", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'start_frame': {
        ICON: u":/Playback/start_frame", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'prev_key': {
        ICON: u":/Playback/prev_key", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'next_key': {
        ICON: u":/Playback/next_key", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'end_frame': {
        ICON: u":/Playback/end_frame", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'prev_marker': {
        ICON: u":/Playback/prev_marker", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'prev_shot': {
        ICON: u":/Playback/prev_shot", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'next_shot': {
        ICON: u":/Playback/next_shot", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'next_marker': {
        ICON: u":/Playback/next_marker", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'swap_shot_left': {
        ICON: u":/Playback/swap_shot_left", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'prev_base_layer_key': {
        ICON: u":/Playback/prev_base_layer_key", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'next_base_layer_key': {
        ICON: u":/Playback/next_base_layer_key", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'swap_shot_right': {
        ICON: u":/Playback/swap_shot_right", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'crop_timeline_left': {
        ICON: u":/Playback/crop_timeline_left", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: """
        <html><head/><body>
        <p><span style=\" color:#df6e41;\">CROP TIMELINE </span>
        <span style=\" font-size:12px; font-weight:600; color:#FF9648;\">LEFT</span></p><hr/>
        <p><span style=\" color:#777777;\">Cuts the timeline on the
        <span style=\" color:#cccccc;\">Start Time.</span></span></span></p>
        </body></html>"""
    },
    'move_start_time_to_current_frame': {
        ICON: u":/Playback/move_start_time_to_current_frame", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: """
        <html><head/><body>
        <p><span style=\" color:#df6e41;\">MOVE </span>
        <span style=\" font-size:12px; font-weight:600; color:#FF9648;\">START TIME </span>
        <span style=\" color:#df6e41;\">TO CURRENT FRAME</span></p><hr/>
        <p><span style=\" color:#777777;\">Moves the time range until the 
        <span style=\" color:#cccccc;\">Start Time</span></span>
        <span style=\" color:#777777;\">matches the current frame.</span></span></p>
        </body></html>"""
    },
    'move_end_time_to_current_frame': {
        ICON: u":/Playback/move_end_time_to_current_frame", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: """
        <html><head/><body>
        <p><span style=\" color:#df6e41;\">MOVE </span>
        <span style=\" font-size:12px; font-weight:600; color:#FF9648;\">END TIME </span>
        <span style=\" color:#df6e41;\">TO CURRENT FRAME</span></p><hr/>
        <p><span style=\" color:#777777;\">Moves the time range until the 
        <span style=\" color:#cccccc;\">End Time</span></span>
        <span style=\" color:#777777;\">matches the current frame.</span></span></p>
        </body></html>"""
    },
    'crop_timeline_right': {
        ICON: u":/Playback/crop_timeline_right", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: """
        <html><head/><body>
        <p><span style=\" color:#df6e41;\">CROP TIMELINE </span>
        <span style=\" font-size:12px; font-weight:600; color:#FF9648;\">RIGHT</span></p><hr/>
        <p><span style=\" color:#777777;\">Cuts the timeline on the
        <span style=\" color:#cccccc;\">End Time.</span></span></span></p>
        </body></html>"""
    },
    'frame_prev_section': {
        ICON: u":/Playback/frame_prev_section", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'center_cursor_to_range': {
        ICON: u":/Playback/center_cursor_to_range", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'center_range_to_cursor': {
        ICON: u":/Playback/center_range_to_cursor", ENABLED: True, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'frame_next_section': {
        ICON: u":/Playback/frame_next_section", ENABLED: False, QSS_CLASS: 'ToolButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [32, 32],
        TOOLTIP: 'Tooltip'
    },
    'prev_stacked_widget': {
        ICON: u":/_Controls/prev_stacked_widget", ENABLED: True, QSS_CLASS: 'ArrowButton',
        MIN_SIZE: [20, 20], MAX_SIZE: [100, 20],
        TOOLTIP: """
        <html><head/><body>
        <p><span style=\" font-size:12px; font-weight:600; color:#FF9648;\">PREVIOUS SECTION </span></p><hr/>
        <p><span style=\" color:#aaaaaa;\">Go to the Previous Section.</span></p>
        </body></html>"""
    },
    'next_stacked_widget': {
        ICON: u":/_Controls/next_stacked_widget", ENABLED: True, QSS_CLASS: 'ArrowButton',
        MIN_SIZE: [20, 20], MAX_SIZE: [100, 20],
        TOOLTIP: """
        <html><head/><body>
        <p><span style=\" font-size:12px; font-weight:600; color:#FF9648;\">NEXT SECTION </span></p><hr/>
        <p><span style=\" color:#aaaaaa;\">Go to the Next Section.</span></p>
        </body></html>"""
    },
    'placeholder': {
        ENABLED: False, QSS_CLASS: 'PlaceholderButton',
        MIN_SIZE: [32, 32], MAX_SIZE: [28, 28],
        TOOLTIP: 'Tooltip'
    },
}

textedit = {
    'info': {QSS_CLASS: 'InfoTextedit', MIN_SIZE: [200, 50], MAX_SIZE: [200, 100]}
}
