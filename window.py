# -*- coding: utf-8 -*-
#Copyright (c) 2009, 2011 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA


from constants import *
from time import *
import pygtk
pygtk.require('2.0')
import gtk
import gobject
from sound import playWave, audioWrite
import os
import random
from gettext import gettext as _

try:
    from sugar.graphics import style
    GRID_CELL_SIZE = style.GRID_CELL_SIZE
except:
    GRID_CELL_SIZE = 0

from sprites import Sprites
from sprite_factory import Sprite

class swWindow: pass

#
# handle launch from both within and without of Sugar environment 
#
def new_window(canvas, path, parent=None):
    sw = swWindow()
    sw.path = path
    sw.activity = parent

    # starting from command line
    # we have to do all the work that was done in CardSortActivity.py
    if parent is None:
        sw.sugar = False
        sw.canvas = canvas

    # starting from Sugar
    else:
        sw.sugar = True
        sw.canvas = canvas
        parent.show_all()

    sw.canvas.set_flags(gtk.CAN_FOCUS)
    sw.canvas.add_events(gtk.gdk.BUTTON_PRESS_MASK)
    sw.canvas.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
    sw.canvas.add_events(gtk.gdk.POINTER_MOTION_MASK)
    sw.canvas.connect("expose-event", _expose_cb, sw)
    sw.canvas.connect("button-press-event", _button_press_cb, sw)
    sw.canvas.connect("button-release-event", _button_release_cb, sw)
    sw.canvas.connect("motion-notify-event", _mouse_move_cb, sw)
    sw.width = gtk.gdk.screen_width()
    sw.height = gtk.gdk.screen_height()-GRID_CELL_SIZE
    sw.sprites = Sprites(sw.canvas)
    sw.sound = True
    sw.scale = 2
    sw.level = 1
    sw.seq = gen_seq(40)
    sw.counter = 0
    sw.playpushed = False

    # Open the buttons
    d = W/4 # position fudge factor
    sw.buttons_off = [Sprite(sw,"Aoff",sw.width/2-W/2,H/2-d,W/2,H/2),\
                      Sprite(sw,"Boff",sw.width/2-W-d,H,W/2,H/2),\
                      Sprite(sw,"Doff",sw.width/2+d,H,W/2,H/2),\
                      Sprite(sw,"Coff",sw.width/2-W/2,H+H/2+d,W/2,H/2)]
    sw.buttons_on  = [Sprite(sw,"Aon",sw.width/2-W/2,H/2-d,W/2,H/2),\
                      Sprite(sw,"Bon",sw.width/2-W-d,H,W/2,H/2),\
                      Sprite(sw,"Don",sw.width/2+d,H,W/2,H/2),\
                      Sprite(sw,"Con",sw.width/2-W/2,H+H/2+d,W/2,H/2)]
    sw.sounds = ['dog','sheep','cat','bird']
    sw.sound_files = []

    # Save sounds for repeated play
    for i in sw.sounds:
        playWave(i)
        path = sw.activity.get_activity_root() + "/instance/" + i + ".csd"
        sw.sound_files.append(path)
        audioWrite(path)

    _all_off(sw)

    # Start calculating
    sw.press = None
    sw.dragpos = 0
    return sw

#
# Play the sample sequence for the current level
#
def play_the_game(sw):
    sw.playpushed = True
    for i in sw.buttons_on:
        i.spr.hide()
    _stepper(sw,0,False)
    sw.counter = 0

#
# Display next graphic/play next sound in sequence
# Loop through twice: once to display the tile and once to pause between tiles
#
def _stepper(sw,i,j):
     if i > 0:
         sw.buttons_on[sw.seq[i-1]].spr.hide()
     if j is True:
         if i < sw.level*2:
             sw.buttons_on[sw.seq[i]].draw_sprite(1500)
             gobject.idle_add(__play_sound_cb, 
                              sw.sound_files[sw.seq[i]], sw.sound)
             sw.timeout_id = gobject.timeout_add(1000,_stepper,sw,i+1,False)
         else:
             _dance(sw,[0,1,2,3],1,0)
     else:
         sw.timeout_id = gobject.timeout_add(1000,_stepper,sw,i,True)

#
# Button press
#
def _button_press_cb(win, event, sw):
    win.grab_focus()
    x, y = map(int, event.get_coords())
    sw.dragpos = x
    spr = sw.sprites.find_sprite((x,y))
    sw.press = spr
    return True

#
# Mouse move
#
def _mouse_move_cb(win, event, sw):
    if sw.press is None:
        sw.dragpos = 0
        return True

    win.grab_focus()
    x, y = map(int, event.get_coords())

    dx = x-sw.dragpos

    # reset drag position
    sw.dragpos = x

#
# Play the csound associated with the button
#
def __play_sound_cb(sound, flag):
    if flag is True:
        # os.system('csound ' + sound + '/temp.csd >/dev/null 2>/dev/null')
        os.system('csound ' + sound)

#
# Button release -- where the work happens
#
def _button_release_cb(win, event, sw):
    if sw.press == None:
        return True
    for i in range (0,4):
        if sw.press == sw.buttons_off[i].spr:
            sw.buttons_on[i].draw_sprite(1500)
            gobject.idle_add(__play_sound_cb, sw.sound_files[i], sw.sound)
            gobject.timeout_add(500,sw.buttons_on[i].spr.hide)
            if sw.playpushed is False:
                sw.press = None
                return
            if sw.seq[sw.counter] == i: # correct reponse
                sw.counter += 1
                if sw.counter == sw.level*2:
                    gobject.timeout_add(1000, _dance, sw, [i], 10, 0)
                    sw.counter = 0
                    sw.level += 1
                    sw.activity.level_label.set_text(
                        "%s %d" % (_("Level"),sw.level))
                    if sw.level*2 < len(sw.seq):
                        gobject.timeout_add(3000, play_the_game, sw)
                    else: # game over
                        gobject.timeout_add(2000, _flash, sw, 7, True)
                        sw.playpushed = False
                        sw.level = 1
                        sw.seq = gen_seq(30)
                        sw.activity.level_label.set_text(
                            "%s %d" % (_("Level"),sw.level))
            else: # incorrect response
                _all_gone(sw)
                gobject.timeout_add(1000, _all_off, sw)
                sw.counter = 0
    sw.press = None

#
# Turn all the sprites bright
#
def _all_on(sw):
    for i in sw.buttons_off:
        i.draw_sprite(1000)
    for i in sw.buttons_on:
        i.draw_sprite(1500)

#
# Do a little dance
#
def _dance(sw, dancelist, dist, n):
    xo = [0,-dist,dist,0]
    yo = [-dist,0,0,dist]
    if n < 10:
        for i in dancelist:
            sw.buttons_off[i].spr.move_relative((xo[i],yo[i]))
        gobject.timeout_add(30,_dance,sw,dancelist,dist,n+1)
    else:
        for i in dancelist:
            sw.buttons_off[i].spr.move_relative((-xo[i]*10,-yo[i]*10))

#
# Flash
#
def _flash(sw, n, i):
    if n == 0:
        _all_off(sw)
        return
    if i is True:
        _all_on(sw)
        gobject.timeout_add(200,_flash,sw,n-1,False)
    else:
        _all_off(sw)
        gobject.timeout_add(200,_flash,sw,n,True)

#
# Turn all the sprites dim
#
def _all_off(sw):
    for i in sw.buttons_off:
        i.draw_sprite(1000)
    for i in sw.buttons_on:
        i.spr.hide()

#
# Hide all the sprites
#
def _all_gone(sw):
    for i in sw.buttons_off:
        i.spr.hide()
    for i in sw.buttons_on:
        i.spr.hide()

#
# Window expose event
#
def _expose_cb(win, event, sw):
    ''' Callback to handle window expose events '''
    do_expose_event(sw, event)
    return True

def do_expose_event(sw, event):
    ''' Handle the expose-event by drawing '''
    # Restrict Cairo to the exposed area
    cr = sw.canvas.window.cairo_create()
    cr.rectangle(event.area.x, event.area.y,
                 event.area.width, event.area.height)
    cr.clip()
    # Refresh sprite list
    sw.sprites.redraw_sprites(cr=cr)

#
# Shut it down
#
def _destroy_cb(win, event, sw):
    gtk.main_quit()

#
# Generate the sample sequences
#
def gen_seq(n):
    seq = []
    for i in range(1,n+1):
        seq.append(int(random.uniform(0,4)))
    print seq
    return seq
