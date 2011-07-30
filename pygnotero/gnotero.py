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
import gobject
import time
import subprocess
import socket
import threading
from pygnotero import gnotero_base, listener

have_AppIndicator = True
try:
	import appindicator
except:
	have_AppIndicator = False


class Gnotero(gtk.StatusIcon, gnotero_base.gnotero_base):
	
	def __init__(self):
		
		"""
		The constructor
		"""
		
		gnotero_base.gnotero_base.__init__(self)		
	
		if have_AppIndicator:
			self.AppInd = appindicator.Indicator("gnotero-menu",self.systray_icon,appindicator.CATEGORY_OTHER)
			self.AppInd.set_status(appindicator.STATUS_ACTIVE)
			self.attach_menu_to_icon == "no"
		else:
			gtk.StatusIcon.__init__(self)				
		
		# give gnotero items a copy of have_AppIndicator, so
		# the listener can acess it without needing to load
		# appindicator.
		self.use_AppInd = have_AppIndicator
			
		
		if self.os != "windows":
			if have_AppIndicator:
				actions = [
					('Menu',  None, 'Menu'),
					('Search',None,None,None,'Search Zotero',self.on_activate),
					('Quit', gtk.STOCK_QUIT, None, None, 'Quit', self.quit),
					('Settings', gtk.STOCK_PREFERENCES, None, None, 'Gnoteroconf', self.start_gnoteroconf),
					('Copy', None, None, None, 'Gnoterobrowse', self.start_gnoterobrowse),
					('Zotero', None, None, None, 'Zotero', self.start_zotero),
					('About', gtk.STOCK_ABOUT, None, None, 'About', self.about)
					]

				menu = """
				<ui>
				 <menubar name="Menubar">
				  <menu action="Menu">
                                   <menuitem action="Search"/>
				   <menuitem action="Settings"/>
				   <menuitem action="Copy"/>
				   <menuitem action="Zotero"/>
				   <menuitem action="About"/>
				   <menuitem action="Quit"/>			   
				  </menu>
				 </menubar>
				</ui>
			"""
			else:
				actions = [
					('Menu',  None, 'Menu'),
					('Quit', gtk.STOCK_QUIT, None, None, 'Quit', self.quit),
					('Settings', gtk.STOCK_PREFERENCES, None, None, 'Gnoteroconf', self.start_gnoteroconf),
					('Copy', None, None, None, 'Gnoterobrowse', self.start_gnoterobrowse),
					('Zotero', None, None, None, 'Zotero', self.start_zotero),
					('About', gtk.STOCK_ABOUT, None, None, 'About', self.about)
					]

				menu = """
				<ui>
				 <menubar name="Menubar">
				  <menu action="Menu">
				   <menuitem action="Settings"/>
				   <menuitem action="Copy"/>
				   <menuitem action="Zotero"/>
				   <menuitem action="About"/>
				   <menuitem action="Quit"/>			   
				  </menu>
				 </menubar>
				</ui>
			"""
		else:
			actions = [
				('Menu',  None, 'Menu'),
				('Quit', gtk.STOCK_QUIT, None, None, 'Quit', self.quit),
				('Zotero', None, None, None, 'Zotero', self.start_zotero),
				('About', gtk.STOCK_ABOUT, None, None, 'About', self.about)
				]

			menu = """
				<ui>
				 <menubar name="Menubar">
				  <menu action="Menu">
				   <menuitem action="Zotero"/>
				   <menuitem action="About"/>
				   <menuitem action="Quit"/>			   
				  </menu>
				 </menubar>
				</ui>
			"""
			
		self.first_result = None
		self.clipboard = gtk.Clipboard()

		ag = gtk.ActionGroup('Actions')
		ag.add_actions(actions)
		self.manager = gtk.UIManager()
		self.manager.insert_action_group(ag, 0)
		self.manager.add_ui_from_string(menu)
		self.menu = self.manager.get_widget('/Menubar/Menu/Quit').props.parent

		if have_AppIndicator:
			self.menu.show()
			self.AppInd.set_menu(self.menu)

		quit = self.manager.get_widget('/Menubar/Menu/Quit')
		quit.get_children()[0].set_markup('Quit')		

		if self.os != "windows":
			preferences = self.manager.get_widget('/Menubar/Menu/Settings')		
			preferences.get_children()[0].set_markup('Gnoteroconf')
		
			copy = self.manager.get_widget('/Menubar/Menu/Copy')
			copy.get_children()[0].set_markup('Gnoterobrowse ')
		
			if have_AppIndicator:
				search = self.manager.get_widget('/Menubar/Menu/Search')
				search.get_children()[0].set_markup('Search Gnotero')
			

		zotero = self.manager.get_widget('/Menubar/Menu/Zotero')
		zotero.get_children()[0].set_markup('Fullscreen Zotero ')		
		
		self.icon_theme = gtk.icon_theme_get_default()							
		if self.os == "windows":
			self.set_from_file("data\\icons\\gnotero.png")
		else:
			if not have_AppIndicator:
				pixbuf = self.icon_theme.load_icon(self.systray_icon, 22, 0)
				self.set_from_pixbuf(pixbuf)

		if not have_AppIndicator:
			self.set_tooltip('Quick access to your Zotero references')
			self.set_visible(True)							
							
			self.connect('popup-menu', self.on_popup_menu)
			self.connect('activate', self.on_activate)		


		self.shown = False		
		self.create_window()	
			
		# Start the listener	
		self.listener = listener.Listener(self)
		self.listener.start()
		
	def quit(self, event = None):
	
		"""
		Stop Gnotero
		"""
		
		self.listener.alive = False	
		gnotero_base.gnotero_base.quit(self, event)
						
	def create_window(self):
		
		"""
		Creates an empty results window
		"""
	
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.realize()				

		# Windows appears to ignore the skip taskbar hint, so we initialize
		# an icon and a name to display in the taskbar
		if self.os == "windows":
			self.window.set_icon_from_file("data\\icons\\gnotero.png")
		
		self.window.set_title("Gnotero")
		self.window.set_decorated(False)
		self.window.set_keep_above(True)
		self.window.set_skip_taskbar_hint(True)
								
		self.style = self.window.get_style()
							
		self.search_edit = gtk.Entry()
		self.search_edit.set_has_frame(False)
		self.search_edit.connect("activate", self.search)
		
		if self.enable_live_search == "yes":
			print "gnotero.create_window(): enabling live search"
			self.search_edit.connect("changed", self.live_search)
				
		self.search_box = gtk.HBox()
		self.search_box.pack_start(self.search_edit, True, True)		
		self.search_box.set_border_width(16)
		
		self.search_event_box = gtk.EventBox()
		self.search_event_box.add(self.search_box)	
		self.search_event_box.modify_bg(gtk.STATE_NORMAL, self.style.bg[gtk.STATE_SELECTED])
								
		self.results_box = gtk.VBox()
		self.results_box.set_homogeneous(False)
		self.results_box.set_border_width(4)
		self.results_box.set_spacing(4)				
				
		self.border_box = gtk.HBox()
		self.border_box.set_border_width(self.lower_border_width)
		
		self.border_event_box = gtk.EventBox()
		self.border_event_box.add(self.border_box)	
		self.border_event_box.modify_bg(gtk.STATE_NORMAL, self.style.bg[gtk.STATE_SELECTED])		
		
		self.main_box = gtk.VBox()
		self.main_box.pack_start(self.search_event_box)			
		self.main_box.pack_start(self.results_box)
		self.main_box.pack_start(self.border_event_box)		
		
		self.window.add(self.main_box)				
		
		self.window.connect("focus-out-event", self.on_focus_out)
		self.window.set_size_request(self.popup_width, -1)		
		
		self.search()
		
	def sync(self, event):
		
		"""
		Start gnoterosync and begin syncing immediately
		"""
	
		pid = subprocess.Popen(["gnoterobrowse", "-n", "-q", "-s", self.search_edit.get_text()]).pid
		print "gnoterobrowse started as process %d" % pid			
									
	def nice_box(self, icon, msg):
		
		"""
		Creates a nice box for a result
		"""
	
		result = gtk.Label()
		result.set_markup(msg)
		result.set_line_wrap(True)
			
		result_box = gtk.HBox()
		result_box.pack_start(result, False, False)
		result_box.set_border_width(4)
		result_box.set_homogeneous(False)
		
		event_box = gtk.EventBox()
		event_box.add(result_box)
						
		return event_box
		
	def no_results(self):
		
		"""
		Notify if no results have been presented
		"""
		
		self.results_box.pack_start(self.nice_box("gnome-info", "<b>No results</b>"))
				
			
	def next_results(self, widget = None, event = None):
		
		"""
		Skip to the next page of the search results
		"""
		
		self.first_result += self.max_results
		self.search()
		
	def previous_results(self, widget = None, event = None):
		
		"""
		Skip to the previous page of the search results
		"""
		
		self.first_result -= self.max_results
		self.search()												
							
	def search(self, widget = None, event = None):
		
		"""
		Search Zotero and display the results
		"""		

		gnotero_base.gnotero_base.search(self)
		
		self.results_box.foreach(lambda widget:self.results_box.remove(widget))
		self.window.resize(300, 50)

		search_term = self.search_edit.get_text()				
						
		if search_term.strip() == "":
			self.results_box.pack_start(self.nice_box("gnome-info", "<b>No search term specificed</b>"))
		else:
			items = self.zotero.search(search_term)						
			
			if len(items) == 0:
				self.first_result = None
				self.results_box.pack_start(self.nice_box("gnome-info", "<b>No results for</b> <i>%s</i>" % search_term))						
			elif len(items) > self.max_results:
			
				if self.first_result == None:
					self.first_result = 0
					
				self.button_box = gtk.HBox()
						
				self.button_box.pack_start(self.nice_box("gnome-info", "<b>Too many results for</b> <i>%s</i>\nDisplaying %d to %d of %d" % (search_term, self.first_result + 1, min(len(items), self.first_result + self.max_results), len(items))))
				
				if self.first_result + self.max_results < len(items):
					image = gtk.Image()
					
					if self.os == "windows":
						image.set_from_file("data\\icons\\go-next.png")
					else:
						image.set_from_icon_name("next", gtk.ICON_SIZE_BUTTON)
										
					button = gtk.Button()										
					button.add(image)
					button.connect("clicked", self.next_results)					
					self.button_box.pack_end(button, False, False, 4)	
									
				if self.first_result > 0:
					image = gtk.Image()
					if self.os == "windows":
						image.set_from_file("data\\icons\\go-previous.png")
					else:
						image.set_from_icon_name("previous", gtk.ICON_SIZE_BUTTON)
					
					button = gtk.Button()
					button.add(image)
					button.connect("clicked", self.previous_results)					
					self.button_box.pack_end(button, False, False)
					
				self.results_box.pack_start(self.button_box)
				
				items = items[self.first_result:self.first_result + self.max_results]				
				
			else:
				self.first_result = None
				self.results_box.pack_start(self.nice_box("gnome-info", "<b>%s results for</b> <i>%s</i>" % (len(items), search_term)))								
			
			ellipsize = self.ellipsize == "yes"
			for item in items:																	
				event_box = self.item_box(item, ellipsize)
				self.results_box.pack_start(event_box)
								
		self.results_box.show_all()		
				
				
	def on_popup_menu(self, status, button, time):
		
		"""
		Wrapper function
		"""
					
		self.menu.popup(None, None, None, button, time)

		
	def on_activate(self, status = None):
		
		"""
		Show the window
		"""		
	
		if not self.shown:
		
			# The get_geometry function does not appear to work under windows
			if self.os != "windows" and self.attach_menu_to_icon == "yes":
				screen, area, orientation = self.get_geometry()
				
				# Make sure the window is completely displayed
				# Patch by Thomas Jost
				posx, posy = area[0], area[1]
				ww, wh = self.window.get_size()
				monitor = screen.get_monitor_geometry(screen.get_monitor_at_point(posx, posy))
				if posx < monitor.x:
					posx = monitor.x
				elif posx + ww > monitor.x + monitor.width:
					posx = monitor.x + monitor.width - ww
				if posy < monitor.y:
					posy = monitor.y
				elif posy + wh > monitor.x + monitor.height:
					posy = monitor.y + monitor.height - wh								             
				self.window.move(posx, posy)		
				
			else:				
				self.window.move(int(gtk.gdk.screen_width() * self.window_pos_x - self.popup_width / 2), int(gtk.gdk.screen_height() * self.window_pos_y))
			
			# Optionally, use the clipboard for the search term. Use at the most
			# the first 10 characters of the first line of the clipboard
			if self.use_clipboard == "yes":
				s = self.clipboard.wait_for_text()
				if s != None:
					self.search_edit.set_text(s.split()[0][:10].strip())					
					self.search()
					
			self.search_edit.select_region(0, -1)					
			self.window.show_all()
			self.shown = True
									
		else:
			self.window.hide()
			self.shown = False			
			
	def on_focus_out(self, widget, event):
		
		"""
		Hide the window
		"""
		
		if self.shown:
			self.window.hide()
			self.shown = False
		
