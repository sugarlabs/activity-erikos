#Copyright (c) 2009, 2011 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import os.path

import sprites

#
# class for defining individual cards
#
class Sprite:
    def __init__(self, sw, name, x, y, w, h):
        # create sprite from svg file
        self.spr = sprites.Sprite(sw.sprites, x, y,
                          self.load_image(sw.path,name,w*sw.scale,h*sw.scale))

    def draw_sprite(self, layer=1000):
        self.spr.set_layer(layer)
        self.spr.draw()

    def load_image(self, file, name, w, h):
        return gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(file + 
                                                                 name + 
                                                                 '.svg'),
                                                    w, h)

