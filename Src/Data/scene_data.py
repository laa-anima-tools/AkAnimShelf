import maya.cmds as cmd
import json

KEY, BREAKDOWN, INBETWEEN = 0, 1, 2


class SceneData(object):

    @classmethod
    def load_scene_data(cls, key):
        data = []
        stored_data = cmd.fileInfo(key, q=True)
        if stored_data:
            data = json.loads(stored_data[0].replace('\\"', '"'))
        return data

    @classmethod
    def store_scene_data(cls, key, value):
        encoded_data = json.dumps(value)
        cmd.fileInfo(key, encoded_data)
