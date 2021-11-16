import maya.cmds as cmd
import maya.mel as mel
import os
import getpass

VISIBLE_ELEMENTS = ['polymeshes', 'headsUpDisplay']
INVISIBLE_ELEMENTS = ['allObjects', 'grid', 'manipulators', 'sel', 'hos']
VIEW_AXIS_ON = 'setViewAxisVisibility(1);'
VIEW_AXIS_OFF = 'setViewAxisVisibility(0);'
TIME_CONTROL = '$tmpVar=$gPlayBackSlider'
NUM_SECTIONS, NUM_BLOCKS = 9, 4


def get_active_panel():
    return cmd.getPanel(withFocus=True)


def is_panel_of_type(panel, type):
    if cmd.getPanel(typeOf=panel) == type:
        return True
    else:
        return False


def get_playback_range():
    playback_start_time = cmd.playbackOptions(minTime=True, query=True)
    playback_end_time = cmd.playbackOptions(maxTime=True, query=True)
    return [playback_start_time, playback_end_time]


def turn_viewport_elements_on_off(elements_type, state, panel=cmd.getPanel(wf=True)):
    exec ('cmd.modelEditor(panel, edit=True, {0}=state)'.format(elements_type))


def turn_camera_frames_on_off(panel, state):
    current_camera = cmd.modelEditor(panel, query=True, camera=True)
    cmd.camera(current_camera,
               edit=True,
               displayFilmGate=state,
               displaySafeAction=state,
               displaySafeTitle=state,
               displayGateMask=state,
               displayFieldChart=state,
               displayResolution=0,
               overscan=1.3)


def get_user_name():
    return getpass.getuser()


def get_scene_name():
    scene_full_name = cmd.file(query=True, sn=True)
    scene_name_ext = scene_full_name.split('/')[-1]
    scene_name = scene_name_ext.split('.')[0]
    return scene_name


def get_frame_counter():
    return cmd.currentTime(query=True)


def show_user_name_hud():
    if (cmd.headsUpDisplay('HUDUserName', ex=True)):
        cmd.headsUpDisplay('HUDUserName', rem=True)

    cmd.headsUpDisplay(rp=(7, 0))
    cmd.headsUpDisplay(rp=(5, 0))
    cmd.headsUpDisplay('HUDUserName', dataFontSize='large', s=5, b=0, c=get_user_name, ev='timeChanged')

def show_scene_name_hud():
    if (cmd.headsUpDisplay('HUDSceneName', ex=True)):
        cmd.headsUpDisplay('HUDSceneName', rem=True)

    cmd.headsUpDisplay(rp=(7, 0))
    cmd.headsUpDisplay(rp=(0, 0))
    cmd.headsUpDisplay('HUDSceneName', dataFontSize='large', s=0, b=0, c=get_scene_name, ev='timeChanged')


def show_frame_counter_hud():
    if (cmd.headsUpDisplay('HUDFrameCounter', ex=True)):
        cmd.headsUpDisplay('HUDFrameCounter', rem=True)

    cmd.headsUpDisplay(rp=(7, 0))
    cmd.headsUpDisplay(rp=(4, 0))
    cmd.headsUpDisplay(
        'HUDFrameCounter',
        dataFontSize='large',
        section=4,
        block=0,
        command=get_frame_counter,
        attachToRefresh=True
    )


def playblast_shot():
    scene_full_name = cmd.file(query=True, sn=True)
    scene_name_ext = scene_full_name.split('/')[-1]
    scene_name = scene_name_ext.split('.')[0]
    scene_path = scene_full_name.replace(scene_name_ext, '')
    video_name = scene_path + scene_name + '.mov'

    print scene_name
    print scene_path
    print video_name

    playback_range = get_playback_range()
    start_frame = cmd.playbackOptions(q=True, min=True)
    end_frame = cmd.playbackOptions(q=True, max=True)

    if playback_range[0] != playback_range[1] - 1:
        start_frame = playback_range[0]
        end_frame = playback_range[1] - 1

    time_control = mel.eval(TIME_CONTROL)
    audio_node = cmd.timeControl(time_control, q=True, s=True)

    cmd.playblast(fmt='qt', f=video_name, s=audio_node, fo=True, sqt=False, cc=True, v=True, orn=True, fp=4, p=100,
                   c='H.264', qlt=100, wh=[1280, 720], st=start_frame, et=end_frame)


print get_user_name()
print get_scene_name()
model_panel = get_active_panel()
if is_panel_of_type(model_panel, "modelPanel"):
    for elmt in INVISIBLE_ELEMENTS:
        turn_viewport_elements_on_off(elmt, False)
    for elmt in VISIBLE_ELEMENTS:
        turn_viewport_elements_on_off(elmt, True)
    turn_camera_frames_on_off(model_panel, 0)
    show_user_name_hud()
    show_scene_name_hud()
    show_frame_counter_hud()
    playblast_shot()
else:
    cmd.warning('No Panel on Focus.')
