"""
This file is part of Gnotero.

Gnotero is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Gnotero is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Gnotero.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import os.path
import gtk
import gtk.glade
import subprocess
from pygnotero import gnotero_builder
from pygnotero import libzotero
import sys

class gnoteroconf(gnotero_builder.gnotero_builder):

	def __init__(self):
	
		gnotero_builder.gnotero_builder.__init__(self, "gnoteroconf.xml")		
		
		self.label_header = self.builder.get_object("label_header")
		self.label_header.set_markup("<big><b>Gnoteroconf</b></big>\n<small>Version %.2f</small>" % self.version)			
		
		self.ok_button = self.builder.get_object("ok_button")		
		self.cancel_button = self.builder.get_object("cancel_button")		
		self.zotero_folder_input = self.builder.get_object("zotero_folder")			
		self.sync_path_input = self.builder.get_object("sync_path")	
		self.sync_name_input = self.builder.get_object("sync_name")	
		self.button_about = self.builder.get_object("button_about")
		self.checkbutton_gnote = self.builder.get_object("checkbutton_gnote")	
		self.checkbutton_clipboard = self.builder.get_object("checkbutton_clipboard")	
		self.checkbutton_live_search = self.builder.get_object("checkbutton_live_search")
		self.checkbutton_icon_tango = self.builder.get_object("checkbutton_icon_tango")
		self.checkbutton_icon_light = self.builder.get_object("checkbutton_icon_light")
		self.checkbutton_icon_dark = self.builder.get_object("checkbutton_icon_dark")
		self.checkbutton_attach = self.builder.get_object("checkbutton_attach")
		self.spinbutton_hpos = self.builder.get_object("spinbutton_hpos")
		self.spinbutton_vpos = self.builder.get_object("spinbutton_vpos")
		
		self.checkbutton_icon_tango.icon = "gnotero"
		self.checkbutton_icon_light.icon = "gnotero-mono-light"
		self.checkbutton_icon_dark.icon = "gnotero-mono-dark"
		
		self.cancel_button.connect("clicked", self.destroy)
		self.ok_button.connect("clicked", self.save_and_destroy)		
		self.button_about.connect("clicked", self.about)	
		self.checkbutton_icon_tango.connect("toggled", self.toggle_icon_style)			
		self.checkbutton_icon_dark.connect("toggled", self.toggle_icon_style)
		self.checkbutton_icon_light.connect("toggled", self.toggle_icon_style)			
		
		self.zotero_folder_input.set_current_folder(self.zotero_folder)	
		self.sync_path_input.set_current_folder(self.sync_path)		
		self.sync_name_input.set_text(self.sync_name)
		self.checkbutton_gnote.set_active(self.notes == "gnote")
		self.checkbutton_live_search.set_active(self.enable_live_search == "yes")
		self.checkbutton_clipboard.set_active(self.use_clipboard == "yes")
		self.checkbutton_attach.set_active(self.attach_menu_to_icon == "yes")
		self.spinbutton_hpos.set_range(0, 100)
		self.spinbutton_vpos.set_range(0, 100)
		self.spinbutton_hpos.set_value(100 * self.window_pos_x)
		self.spinbutton_vpos.set_value(100 * self.window_pos_y)
		
		self.hold_toggle = False
		self.checkbutton_icon_tango.set_active(self.systray_icon == "gnotero")
		self.checkbutton_icon_light.set_active(self.systray_icon == "gnotero-mono-light")
		self.checkbutton_icon_dark.set_active(self.systray_icon == "gnotero-mono-dark")	
		
		self.window.show_all()		
		
	def toggle_icon_style(self, widget):
	
		if self.hold_toggle:
			return
			
		self.hold_toggle = True	
		self.systray_icon = widget.icon
		self.checkbutton_icon_tango.set_active(self.systray_icon == "gnotero")
		self.checkbutton_icon_light.set_active(self.systray_icon == "gnotero-mono-light")
		self.checkbutton_icon_dark.set_active(self.systray_icon == "gnotero-mono-dark")		
		self.hold_toggle = False			
		
	def save_and_destroy(self, widget):
	
		if not libzotero.valid_location(self.zotero_folder_input.get_filename()):
			mb = gtk.MessageDialog(buttons=gtk.BUTTONS_OK)
			mb.set_title("Incorrect folder")
			mb.set_markup("<b>Incorrect folder. Please select the Zotero Data folder</b>\n\nYou can find this folder in the Advanced section of your Zotero preferences.")
			mb.run()
			mb.destroy()
			return				
		
		if self.checkbutton_gnote.get_active():
			self.notes = "gnote"
		else:
			self.notes = "disabled"			
			
		if self.checkbutton_live_search.get_active():
			self.enable_live_search = "yes"
		else:
			self.enable_live_search = "no"		
			
		if self.checkbutton_clipboard.get_active():
			self.use_clipboard = "yes"
		else:
			self.use_clipboard = "no"	
			
		if self.checkbutton_attach.get_active():
			self.attach_menu_to_icon = "yes"
		else:
			self.attach_menu_to_icon = "no"
			
		self.window_pos_x = 0.01 * self.spinbutton_hpos.get_value_as_int()
		self.window_pos_y = 0.01 * self.spinbutton_vpos.get_value_as_int()
			
		self.zotero_folder = self.zotero_folder_input.get_current_folder()
		self.sync_path = self.sync_path_input.get_current_folder()
		self.sync_name = self.sync_name_input.get_text()	
		
		if self.checkbutton_icon_tango.get_active():
			self.systray_icon = self.checkbutton_icon_tango.icon
		if self.checkbutton_icon_light.get_active():
			self.systray_icon = self.checkbutton_icon_light.icon
		if self.checkbutton_icon_dark.get_active():
			self.systray_icon = self.checkbutton_icon_dark.icon

	
		self.save_config()
		
		mb = gtk.MessageDialog(buttons=gtk.BUTTONS_OK)
		mb.set_title("Please restart gnotero")
		mb.set_markup("<b>Your configuration has been saved</b>\n\nPlease restart any open instances of gnotero, gnoterobrowse and gnoteroconf.")
		mb.run()
		mb.destroy()		
		
		self.destroy(widget)
