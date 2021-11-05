import maya.cmds as cmd
import json

def store_markers(markers):
    cmd.fileInfo('ak_markers', markers)

def print_markers():
    print cmd.fileInfo('ak_markers', q=True)

def save_data():
    data = {
        "keys": [1, 3, 4],
        "breakdowns": [2, 6, 7],
        "inbetweens": [8, 9, 11]
    }
    encoded = json.dumps(data)
    cmd.fileInfo("markers", encoded)

def get_data():
    print cmd.fileInfo('markers', q=True)

store_markers("[1, 3, 5]")
print_markers()
save_data()
get_data()j

