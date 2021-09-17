# Embedded file name: C:\Users\hgkim\Documents\maya\2016\pythons\LocusPicker\idleQueue.py
import Queue
idle_loop = Queue.Queue()

def idle_add(func, *args, **kwargs):

    def idle():
        func(*args, **kwargs)
        return False

    idle_loop.put(idle)


def idle_add_prioritry(func, *args, **kwargs):
    with idle_loop.mutex:
        idle_loop.queue.clear()
    idle_add(func, *args, **kwargs)