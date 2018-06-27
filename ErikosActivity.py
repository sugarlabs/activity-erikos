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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

from sugar3.activity import activity
from sugar3.bundle.activitybundle import ActivityBundle
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.menuitem import MenuItem
from sugar3.graphics.icon import Icon
from sugar3.datastore import datastore

from gettext import gettext as _
import locale
import os.path

import logging
_logger = logging.getLogger("erikos-activity")

from sprites import *
import window

#
# Sugar activity
#
class ErikosActivity(activity.Activity):

    def __init__(self, handle):
        super(ErikosActivity,self).__init__(handle)
        toolbar_box = ToolbarBox()

        # Buttons added to the Activity toolbar
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        # Play Button
        self.play = ToolButton( "media-playback-start" )
        self.play.set_tooltip(_('Play'))
        self.play.props.sensitive = True
        self.play.connect('clicked', self._play_cb)
        toolbar_box.toolbar.insert(self.play, -1)
        self.play.show()

        # Sound Toggle Button
        self.sound = ToolButton( "speaker-muted-100" )
        self.sound.set_tooltip(_('Mute'))
        self.sound.props.sensitive = True
        self.sound.connect('clicked', self._sound_cb)
        toolbar_box.toolbar.insert(self.sound, -1)
        self.sound.show()

        separator = Gtk.SeparatorToolItem()
        separator.show()
        toolbar_box.toolbar.insert(separator, -1)

        # Label for showing level
        self.level_label = Gtk.Label(label="%s %d" % (_("Level"),1))
        self.level_label.show()
        level_toolitem = Gtk.ToolItem()
        level_toolitem.add(self.level_label)
        toolbar_box.toolbar.insert(level_toolitem,-1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        separator.show()
        toolbar_box.toolbar.insert(separator, -1)

        # The ever-present Stop Button
        stop_button = StopButton(self)
        stop_button.props.accelerator = '<Ctrl>Q'
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        # Create a canvas
        canvas = Gtk.DrawingArea()
        canvas.set_size_request(Gdk.Screen.width(), \
                                Gdk.Screen.height())
        self.set_canvas(canvas)
        canvas.show()
        self.show_all()

        # Initialize the canvas
        self.sw = window.new_window(canvas, \
                                    os.path.join(activity.get_bundle_path(), \
                                                 'images/'), \
                                    self)
        self.sw.activity = self

        # Read the level from the Journal
        try:
            sw.level = int(self.metadata['level'])
        except:
            pass

    def _play_cb(self, button):
        window.play_the_game(self.sw)
        return True

    def _sound_cb(self, button):
        if self.sw.sound is True:
            self.sound.set_icon_name("speaker-muted-000")
            self.sound.set_tooltip(_('Unmute'))
            self.sw.sound = False
        else:
            self.sound.set_icon_name("speaker-muted-100")
            self.sound.set_tooltip(_('Mute'))
            self.sw.sound = True
        return True

    """
    Write the slider positions to the Journal
    """
    def write_file(self, file_path):
        _logger.debug("Write level: " + str(self.sw.level))
        self.metadata['level'] = self.sw.level
