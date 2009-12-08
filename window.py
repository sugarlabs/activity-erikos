# -*- coding: utf-8 -*-
#Copyright (c) 2009, Walter Bender

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

from constants import *
from time import *
import pygtk
pygtk.require('2.0')
import gtk
import gobject
from sound import playWave, audioWrite
import os

from gettext import gettext as _
import math

try:
    from sugar.graphics import style
    GRID_CELL_SIZE = style.GRID_CELL_SIZE
except:
    GRID_CELL_SIZE = 0

from sprite_factory import *

class srWindow: pass

#
# handle launch from both within and without of Sugar environment 
#
def new_window(canvas, path, parent=None):
    tw = srWindow()
    tw.path = path
    tw.activity = parent

    # starting from command line
    # we have to do all the work that was done in CardSortActivity.py
    if parent is None:
        tw.sugar = False
        tw.canvas = canvas

    # starting from Sugar
    else:
        tw.sugar = True
        tw.canvas = canvas
        parent.show_all()

    tw.canvas.set_flags(gtk.CAN_FOCUS)
    tw.canvas.add_events(gtk.gdk.BUTTON_PRESS_MASK)
    tw.canvas.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
    tw.canvas.add_events(gtk.gdk.POINTER_MOTION_MASK)
    tw.canvas.connect("expose-event", _expose_cb, tw)
    tw.canvas.connect("button-press-event", _button_press_cb, tw)
    tw.canvas.connect("button-release-event", _button_release_cb, tw)
    tw.canvas.connect("motion-notify-event", _mouse_move_cb, tw)
    tw.width = gtk.gdk.screen_width()
    tw.height = gtk.gdk.screen_height()-GRID_CELL_SIZE
    tw.area = tw.canvas.window
    tw.gc = tw.area.new_gc()
    tw.cm = tw.gc.get_colormap()
    tw.msgcolor = tw.cm.alloc_color('black')
    tw.sprites = []
    tw.scale = 1
    tw.level = 0
    tw.seq = [[0,1],[0,1,0,1],[0,1,2,3,0,1,2,3],[0,1,2,3,0,1,2,3,0,1,2,3]]
    tw.counter = 0

    # Open the sliders
    tw.buttons_off = [Sprite(tw,"Aoff",tw.width/2-W/2,H/2,W/2,H/2),\
                      Sprite(tw,"Boff",tw.width/2-W,H,W/2,H/2),\
                      Sprite(tw,"Doff",tw.width/2,H,W/2,H/2),\
                      Sprite(tw,"Coff",tw.width/2-W/2,H+H/2,W/2,H/2)]
    tw.buttons_on  = [Sprite(tw,"Aon",tw.width/2-W/2,H/2,W/2,H/2),\
                      Sprite(tw,"Bon",tw.width/2-W,H,W/2,H/2),\
                      Sprite(tw,"Don",tw.width/2,H,W/2,H/2),\
                      Sprite(tw,"Con",tw.width/2-W/2,H+H/2,W/2,H/2)]
    tw.sounds = ['dog','sheep','cat','bird']
    tw.sound_files = []

    for i in tw.sounds:
        playWave(i)
        path = tw.activity.get_activity_root() + "/instance/" + i + ".csd"
        tw.sound_files.append(path)
        audioWrite(path)

    _all_off(tw)

    # Start calculating
    tw.press = None
    tw.dragpos = 0
    return tw

#
# Play
#
def play_the_game(tw):
    print "############################### " + str(tw.level)
    _all_on(tw)
    for i in tw.buttons_on:
        hide(i.spr)
    _stepper(tw,0)
    tw.counter = 0

#
# Display next sound/graphic in sequence
#
def _stepper(tw,i):
     if i > 0:
         hide(tw.buttons_on[tw.seq[tw.level][i-1]].spr)
     if i < len(tw.seq[tw.level]):
         tw.buttons_on[tw.seq[tw.level][i]].draw_sprite(1500)
         inval(tw.buttons_on[tw.seq[tw.level][i]].spr)
         gobject.idle_add(__play_sound_cb, tw.sound_files[tw.seq[tw.level][i]])
         tw.timeout_id = gobject.timeout_add(1000,_stepper,tw,i+1)
     else:
         tw.timeout_id = gobject.timeout_add(1000,_all_off,tw)

#
# Button press
#
def _button_press_cb(win, event, tw):
    win.grab_focus()
    x, y = map(int, event.get_coords())
    tw.dragpos = x
    spr = findsprite(tw,(x,y))
    tw.press = spr
    return True

#
# Mouse move
#
def _mouse_move_cb(win, event, tw):
    if tw.press is None:
        tw.dragpos = 0
        return True

    win.grab_focus()
    x, y = map(int, event.get_coords())

    dx = x-tw.dragpos

    # reset drag position
    tw.dragpos = x

#
# Button release
#
def __play_sound_cb(sound):
#    os.system('csound ' + sound + '/temp.csd >/dev/null 2>/dev/null')
    os.system('csound ' + sound)

def _button_release_cb(win, event, tw):
    if tw.press == None:
        return True
    for i in range (0,4):
        if tw.press == tw.buttons_off[i].spr:
            tw.buttons_on[i].draw_sprite(1500)
            inval(tw.buttons_on[i].spr)
            gobject.idle_add(__play_sound_cb, tw.sound_files[i])
            gobject.timeout_add(500,hide,tw.buttons_on[i].spr)
            print "level %d; counter %d; i is %d" % (tw.level,tw.counter,i)
            if tw.seq[tw.level][tw.counter] == i: # correct reponse
                tw.counter += 1
                if tw.counter == len(tw.seq[tw.level]):
                    print "solved level %d" % (tw.level)
                    _all_on(tw)
                    tw.counter = 0
                    tw.level += 1
                    if tw.level == len(tw.seq):
                        tw.level = 0
                    gobject.timeout_add(500, _all_off, tw)
            else: # incorrect response
                _all_gone(tw)
                gobject.timeout_add(1000, _all_off, tw)
                tw.counter = 0

    tw.press = None

def _all_on(tw):
    for i in tw.buttons_off:
        i.draw_sprite(1000)
    for i in tw.buttons_on:
        i.draw_sprite(1500)

def _all_off(tw):
    for i in tw.buttons_off:
        i.draw_sprite(1000)
    for i in tw.buttons_on:
        hide(i.spr)

def _all_gone(tw):
    for i in tw.buttons_off:
        hide(i.spr)
    for i in tw.buttons_on:
        hide(i.spr)

def _expose_cb(win, event, tw):
    redrawsprites(tw)
    return True

def _destroy_cb(win, event, tw):
    gtk.main_quit()
