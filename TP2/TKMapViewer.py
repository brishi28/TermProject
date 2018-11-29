# Copyright (c) 2016-2017 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''This module provides a simple GUI viewer for Cozmo's camera.
It uses Tkinter, the standard Python GUI toolkit which is optionally available
on most platforms, and also depends on the Pillow and numpy libraries for
image processing.
See the online SDK documentation for details on how to install these extra
packages on your platform.
The easiest way to make use of this viewer is to call
:func:`cozmo.run.connect_with_tkviewer`.
Warning:
    This package requires Python to have Tkinter installed to display the GUI.
'''


# __all__ should order by constants, event classes, other classes, functions.

import cozmo
import collections
import functools
import queue
import platform
import time

import tkinter

from cozmo import world


class TkThreadable:
    '''A mixin for adding threadsafe calls to tkinter methods.'''
    #pylint: disable=no-member
    # no-member errors are raised in pylint regarding members/methods called but not defined in our mixin.
    def __init__(self, *a, **kw):
        self._thread_queue = queue.Queue()
        self.after(50, self._thread_call_dispatch)

    def call_threadsafe(self, method, *a, **kw):
        self._thread_queue.put((method, a, kw))

    def _thread_call_dispatch(self):
        while True:
            try:
                method, a, kw = self._thread_queue.get(block=False)
                self.after_idle(method, *a, **kw)
            except queue.Empty:
                break
        self.after(50, self._thread_call_dispatch)


class CozmoView(tkinter.Frame, TkThreadable):
    '''Simple Tkinter camera viewer.'''

    # TODO: rewrite this whole thing.  Make a generic camera widget
    # that can be used in other Tk applications.  Also handle resizing
    # the window properly.
    def __init__(self,
            tk_root=None, refresh_interval=10, image_scale = 2,
            window_name = "CozmoView", force_on_top=True):
        if tk_root is None:
            tk_root = tkinter.Tk()
        tkinter.Frame.__init__(self, tk_root)
        TkThreadable.__init__(self)

        self._refresh_interval = refresh_interval
        self.scale = image_scale
        self.width = 400
        self.height = 400
        self.currentMap = None
        self.path = None
        self.currentLoc = None

        self.tk_root = tk_root
        tk_root.wm_title(window_name)
        # Tell the TK root not to resize based on the contents of the window.
        # Necessary to get the resizing to function properly
        tk_root.pack_propagate(False)
        # Set the starting window size
        tk_root.geometry('{}x{}'.format(720, 540))

        self.tk_root.protocol("WM_DELETE_WINDOW", self._delete_window)
        self._isRunning = True
        tk_root.aspect(4,3,4,3)

        if force_on_top:
            # force window on top of all others, regardless of focus
            tk_root.wm_attributes("-topmost", 1)

        self.tk_root.bind("<Configure>", self.configure)
        self.canvas = Canvas(self.root, width=data.width, height=data.height)
        self.canvas.configure(bd=0, highlightthickness=0)
        self.canvas.pack()
        self._repeat_draw_frame()


    def disconnect(self):
        self.call_threadsafe(self.quit)

    # The base class configure doesn't take an event
    #pylint: disable=arguments-differ
    def configure(self, event):
        if event.width < 50 or event.height < 50:
            return
        self.height = event.height
        self.width = event.width

    def updateMap(self, newMap):
        self.currentMap = newMap

    def updatePath(self, path):
        self.path = path

    def updateLoc(self, loc):
        self.currentLoc = loc

    def _delete_window(self):
        self.tk_root.destroy()
        self.quit()
        self._isRunning = False

    def _draw_frame(self):
        self.canvas.delete(ALL)
        self.canvas.create_rectangle(0, 0, self.width, self.height,
                                    fill='white', width=0)
        if self.currentMap:
            cellWidth = self.width / len(self.currentMap[0])
            cellHeight = self.height / len(self.currentMap)
            for y in range(len(self.currentMap)):
                for x in range(len(self.currentMap[y])):
                    if self.currentLoc and (x, y) == self.currentLoc:
                        color = 'blue'
                    elif self.path and (x, y) in self.path:
                        color = 'red'
                    elif self.currentMap[y][x]:
                        color = 'green'
                    else:
                        color = 'black'
                    x0 = x * data.cellWidth
                    y0 = y * data.cellHeight
                    x1 = x0 + data.cellWidth
                    y1 = y0 + data.cellHeight
                    self.canvas.create_rectangle(x0, y0, x1, y1, color)
            self.canvas.update()

    def _repeat_draw_frame(self, event=None):
        self._draw_frame()
        self.after(self._refresh_interval, self._repeat_draw_frame)