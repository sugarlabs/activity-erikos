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

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import sugar
from sugar.activity import activity
try: # 0.86+ toolbar widgets
    from sugar.bundle.activitybundle import ActivityBundle
    from sugar.activity.widgets import ActivityToolbarButton
    from sugar.activity.widgets import StopButton
    from sugar.graphics.toolbarbox import ToolbarBox
    from sugar.graphics.toolbarbox import ToolbarButton
except ImportError:
    pass
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.menuitem import MenuItem
from sugar.graphics.icon import Icon
from sugar.datastore import datastore

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

        try:
            # Use 0.86 toolbar design
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

            separator = gtk.SeparatorToolItem()
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            # Label for showing level
            self.level_label = gtk.Label("%s %d" % (_("Level"),1))
            self.level_label.show()
            level_toolitem = gtk.ToolItem()
            level_toolitem.add(self.level_label)
            toolbar_box.toolbar.insert(level_toolitem,-1)

            separator = gtk.SeparatorToolItem()
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

        except NameError:
            # Use pre-0.86 toolbar design
            self.toolbox = activity.ActivityToolbox(self)
            self.set_toolbox(self.toolbox)

            self.projectToolbar = ProjectToolbar(self)
            self.toolbox.add_toolbar( _('Project'), self.projectToolbar )

            self.toolbox.show()

        # Create a canvas
        canvas = gtk.DrawingArea()
        canvas.set_size_request(gtk.gdk.screen_width(), \
                                gtk.gdk.screen_height())
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
            self.sound.set_icon("speaker-muted-000")            
            self.sound.set_tooltip(_('Unmute'))
            self.sw.sound = False
        else:
            self.sound.set_icon("speaker-muted-100")
            self.sound.set_tooltip(_('Mute'))
            self.sw.sound = True
        return True

    """
    Write the slider positions to the Journal
    """
    def write_file(self, file_path):
        _logger.debug("Write level: " + str(self.sw.level))
        self.metadata['level'] = self.sw.level

#
# Project toolbar for pre-0.86 toolbars
#
class ProjectToolbar(gtk.Toolbar):

    def __init__(self, pc):
        gtk.Toolbar.__init__(self)
        self.activity = pc

        # Play button
        self.activity.play = ToolButton( "media-playback-start" )
        self.activity.play.set_tooltip(_('Play'))
        self.activity.play.props.sensitive = True
        self.activity.play.connect('clicked', self.activity._play_cb)
        self.insert(self.activity.play, -1)
        self.activity.play.show()

        # Sound toggle button
        self.activity.sound = ToolButton( "speaker-muted-100" )
        self.activity.sound.set_tooltip(_('Mute'))
        self.activity.sound.props.sensitive = True
        self.activity.sound.connect('clicked', self.activity._sound_cb)
        self.insert(self.activity.sound, -1)
        self.activity.sound.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        # Label for showing play status
        self.activity.level_label = gtk.Label("%s %d" % (_("Level"),1))
        self.activity.level_label.show()
        self.activity.level_toolitem = gtk.ToolItem()
        self.activity.level_toolitem.add(self.activity.level_label)
        self.insert(self.activity.level_toolitem, -1)
        self.activity.level_toolitem.show()
