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

from pygnotero import autoconfig
from pygnotero import libzotero
try:
	from pygnotero import libgnote
except:
	print "gnotero_base: failed to initialize libgnote (you are probably running Windows or are missing some dependencies)"
import os
import sys
import pango
import os.path
import gtk
import gobject
import subprocess
import warnings
import urllib

class gnotero_base(autoconfig.autoconfig):	

	version = 0.42

	def __init__(self):			
	
		autoconfig.autoconfig.__init__(self, ".gnotero")
		self.update_check()		

		print
		print "Welcome to Gnotero %.2f!" % self.version
		print "Homepage: http://www.cogsci.nl/gnotero"
		print
		print "Gnotero is free software, released under the GNU General Public License v3"
		print "http://www.gnu.org/licenses/gpl.html"
		print
		print "Settings are stored in %s" % os.path.join(self.home_folder, ".gnotero")
		print		
		
		self.zotero = libzotero.libzotero(self.zotero_folder)
		if self.notes == "gnote" and self.os == "*nix":		
			self.gnote = libgnote.libgnote(self.home_folder)
		self.timer_id = None
		
		if self.zotero.error:
			print "gnotero_base.__init__(): an error occured in libzotero"
			mb = gtk.MessageDialog(buttons=gtk.BUTTONS_OK)
			mb.set_title("Something went wrong!")
			mb.set_markup("<b>Failed to connect to Zotero</b>\n\nAre you running an outdated version of Zotero?")
			mb.run()
			mb.destroy()
			quit()		
				
	def default_settings(self):
	
		"""
		The default gnotero settings
		"""
	
		d = {}		
		d["zotero_folder"] = ""
		d["notes"] = "disabled"		
		d["max_results"] = 10
		d["lower_border_width"] = 4
		d["sync_path"] = "None"
		d["sync_name"] = "E-Reader"
		d["pdf_color"] = "#cc0000"
		d["enable_live_search"] = "yes"
		d["live_search_min_char"] = 3
		d["live_search_time"] = 300
		d["systray_icon"] = "gnotero"
		d["firefox_path"] = "firefox"
		d["pdf_reader_path"] = "xdg-open"
		d["popup_width"] = 340
		d["attach_menu_to_icon"] = "yes"
		d["window_pos_x"] = 0.5
		d["window_pos_y"] = 0.25
		d["check_updates"] = "yes"
		d["ignore_updates_up_to_version"] = 0.0
		d["ellipsize"] = "yes"
		d["pdf_use_metadata"] = "yes"
		
		return d
	
	def settings_comments(self):
		
		"""
		Offers a description of the settings in the config file
		"""
		
		d = {}
		d["zotero_folder"] = "[path] Path to Zotero (the folder which contains zotero.sqlite)"
		d["notes"] = "[disabled | gnote] Indicates if Gnote should be searched for notes (disabled on Windows)"		
		d["max_results"] = "[nr] maximum number of results per search"
		d["lower_border_width"] = "[pixels] size of the border on the bottom of the Gnotero window"
		d["sync_path"] = "[path] default path for PDF copying"
		d["sync_name"] = "[description] Description of the path for PDF copying"
		d["pdf_color"] = "[#RRGGBB] The color of the [PDF] message"
		d["enable_live_search"] = "[yes | no] enables/ disables live search"
		d["live_search_min_char"] = "[nr] The minimum number of characters for live search"
		d["systray_icon"] = "[icon name] Name of the systray icon"
		d["firefox_path"] = "[path] Path to Firefox"
		d["pdf_reader_path"] = "[path] path to the program used for opening PDFs"
		d["popup_width"] = "[pixels] Width op the window"
		d["attach_menu_to_icon"] = "[yes | no] Indicates if the window is attached to the panel icon. Is ignored under Windows."
		d["window_pos_x"] = "[0 .. 1] The hoziontal position of the window relative to the display size"
		d["window_pos_y"] = "[0 .. 1] The vertical position of the window relative to the display size"
		d["check_updates"] = "[yes | no] Automatically checks for updates"
		d["ignore_updates_up_to_version"] = "[version] Supresses the update notification if the update version number is less or equal to a specified version"
		d["ellipsize"] = "[yes | no] Use '...' to shorten titles and authors"
		d["pdf_use_metadata"] = "[yes | no] Use metadata for display in Zotero and automatically edit metadata when copying"
		
		return d
		
	def first_run(self):
	
		"""
		This is called the first time that Gnotero is called, to
		set the Zotero location.
		"""
		
		print "gnotero_base.first_run(): this appears to be the first run"
	
		# Ask if the user wants to locate Zotero automatically or manually
		mb = gtk.MessageDialog()				
		mb.add_button("Yes, go ahead!", 0)
		mb.add_button("No, I want to locate Zotero manually", 1)
		mb.set_title("Welcome to Gnotero!")
		
		s = "<b>This appears to be the first time that you run Gnotero.</b>\n\nGnotero needs to know where your Zotero folder is located. Do you want Gnotero to try to locate your Zotero folder automatically (this may take some time)?"
		
		if self.os == "windows":
			s += "\n\n<b>Note to Windows users</b>\n\nCurrently Gnotero does not offer a graphical configuration tool for Windows. " \
				+ "If you run into any programs you can 'reset' Gnotero by removing the configuration file, which is located here: " \
				+ "<b>%s</b>" % os.path.join(self.home_folder, self.config_file)
						
		mb.set_markup(s)
					
		if mb.run()	== 0:
		
			# Locate zotero automatically
			mb.destroy()
			print "gnotero_base.first_run(): locating zotero.sqlite"
			location = self.locate(self.home_folder, "zotero.sqlite")
			print "gnotero_base.first_run(): zotero appears to be in '%s'" % location
			if location != None:
				mb = gtk.MessageDialog()		
				mb.set_title("Zotero found!")						
				mb.add_button("Yes, that's were it is!", 0)
				mb.add_button("No, it's not", 1)
				mb.set_markup("Gnotero thinks Zotero is located here:\n\n<b>%s</b>\n\nIs that correct?" % location)
				if mb.run() == 0:
					mb.destroy()
					self.zotero_folder = location
				else:
					mb.destroy()
					self.locate_zotero()
				
		else:
		
			# Locate zotero manually
			mb.destroy()
			self.locate_zotero()
			
		# Under windows we need the actual path of firefox and the acrobat reader
		if self.os == "windows":

			self.messagebox("Locate Firefox", "Please indicate the location of <b>Firefox</b>.\n\nIf you don't know where Firefox is located, you may find it here:\n<b>[DRIVE LETTER]:\\\\Program Files\\Mozilla Firefox\\firefox.exe</b>")

			fd = gtk.FileChooserDialog("Locate Firefox (firefox.exe)", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
			if fd.run() == gtk.RESPONSE_OK:
				self.firefox_path = fd.get_filename()
			else:
				self.messagebox("Cancelled", "You have pressed cancel, exiting Gnotero...")
				gtk.main_quit()
			fd.destroy()

			self.messagebox("Locate Acrobat Reader (or another PDF reader)", "Please indicate the location of <b>Acrobat Reader</b> (or another executable you wish to use for reading PDF files).\n\nIf you don't know where Acrobat Reader is located, you may find it here:\n<b>[DRIVE LETTER]:\\\\Program Files\\Adobe\\Reader 9.0\\Reader\\AcroRd32.exe</b>")

			fd = gtk.FileChooserDialog("Locate Acrobat Reader (acroread.exe)", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
			if fd.run() == gtk.RESPONSE_OK:
				self.pdf_reader_path = fd.get_filename()
			else:
				self.messagebox("Cancelled", "You have pressed cancel, exiting Gnotero...")
				gtk.main_quit()				
			fd.destroy()			

		self.save_config()	

	def messagebox(self, title, msg):

		"""
		Presents a simple messagebox
		"""	

		mb = gtk.MessageDialog(buttons=gtk.BUTTONS_OK)		
		mb.set_title(title)						
		mb.set_markup(msg)
		mb.run()
		mb.destroy()			
					
	def quit(self, event):
		
		"""
		Quits the program
		"""
		
		print "gnotero_base.quit(): bye!"

		gtk.main_quit()
				
	def locate_zotero(self, event = None):
		
		"""
		Presents a simple preference dialog.
		Currently, this is simply a locate dialog for the Zotero folfer.
		"""
		
		fd = gtk.FileChooserDialog("Locate Zotero Folder", None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		if fd.run() == gtk.RESPONSE_OK:
			self.zotero_folder = fd.get_filename()
			
			print "gnoter_base.locate_zotero(): selected %s" % self.zotero_folder
			
			if libzotero.valid_location(self.zotero_folder):
				print "gnoter_base.locate_zotero(): path ok"
				self.zotero = libzotero.libzotero(self.zotero_folder)
			else:
				print "gnoter_base.locate_zotero(): path not ok"
				fd.destroy()
				mb = gtk.MessageDialog(buttons=gtk.BUTTONS_OK)
				mb.set_title("Oops!")
				mb.set_markup("<b>I could not find zotero.sqlite in this folder</b>\n\nYou can find the Zotero folder in the Advanced section of your Zotero preferences.\n\nPlease try again.")
				mb.run()
				mb.destroy()
				self.locate_zotero()
				return
		else:
			self.messagebox("Cancelled", "You have pressed cancel, exiting Gnotero...")
			quit()				
		
		fd.destroy()
	
	def about(self, event):
		
		"""
		Displays a simple About dialog
		"""
		
		mb = gtk.MessageDialog(buttons=gtk.BUTTONS_OK)
		mb.set_title("About Gnotero")
		mb.set_markup("<b>Gnotero %.2f</b>\n\nQuick access to your Zotero references\n\nSebastiaan Mathot (2009-2010)\n<span size='small'>http://www.cogsci.nl/gnotero</span>" % self.version)
		mb.run()
		mb.destroy()			
		
	def start_gnoterobrowse(self, event):
		
		"""
		Start gnoterosync and begin syncing immediately
		"""

		if self.os == "windows":
			self.messagebox("I'm really sorry, but ...", "currently Gnoterobrowse only works under Linux.")
			return
	
		pid = subprocess.Popen(["gnoterobrowse"]).pid
		print "gnoterosync started as process %d" % pid
		
	def start_gnoteroconf(self, event):
		
		"""
		Start gnoterosync and begin syncing immediately
		"""

		if self.os == "windows":
			self.messagebox("I'm really sorry, but ...", "... currently Gnoteroconf only works under Linux.\nYou can manually change your configuration by editing\n<b>%s</b>" % os.path.join(self.home_folder, self.config_file))
			return
			
		pid = subprocess.Popen(["gnoteroconf"]).pid
		print "gnoteroconf started as process %d" % pid	
		
	def start_zotero(self, event):
		
		pid = subprocess.Popen([self.firefox_path, "-new-window", "zotero://fullscreen"]).pid
		print "Firefox started with fullscreen Zotero as process %d" % pid			
		
	def pretty_box(self, text, press_func, enter_func, leave_func, ellipsize = False):
	
		"""
		Creates a pretty box, which can be used to store Zotero items
		and files in gnoterobrowse
		
		Structure:
		meta_box (eventbox)
		+ meta_hbox (hbox)
		  + event_box (eventbox)
		    + result_box (hbox)
		      + result (label)
		
		"""
	
		result = gtk.Label()		
		if ellipsize:
			result.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
			result.set_max_width_chars(20)		
		result.set_alignment(0, 0.5)
		result.set_markup(text)
		result.set_line_wrap(True)
					
		result_box = gtk.HBox()				
		result_box.pack_start(result, True, True)
		result_box.set_border_width(4)
	
		event_box = gtk.EventBox()								
		event_box.add(result_box)										
		event_box.connect("button-press-event", press_func)
		
		meta_hbox = gtk.HBox()
		meta_hbox.pack_start(event_box)
		
		meta_box = gtk.EventBox()
		meta_box.label = result
		meta_box.ebox = event_box
		meta_box.box = meta_hbox

		meta_box.connect("enter-notify-event", enter_func)
		meta_box.connect("leave-notify-event", leave_func)
		
		meta_box.add(meta_hbox)		
			
		return meta_box						
				
	def item_box(self, item, ellipsize = False):
	
		"""
		Creates a pretty gtk.Label from a zotero item
		"""
				
		title = item.gnotero_format()
		
		item_box = self.pretty_box(title, self.open_pdf, self.highlight, self.unhighlight, ellipsize)
		
		if item.fulltext != None:
			item_box.label.set_markup("<span size ='small' color='%s' weight='bold'>[PDF]</span> %s" % (self.pdf_color, title))
		
		item_box.pdf = item.fulltext
		item_box.ebox.pdf = item.fulltext
		item_box.item = item
		item_box.note_retrieved = False
		item_box.note_button = None		
		item_box.firefox_button = None
		
		return item_box	
		
	def highlight(self, widget = None, event = None):
				
		"""
		Highlight a result, but only if a pdf is attached
		"""	
		
		self.retrieve_note(widget)
		
		if widget.note_button != None:
			widget.box.pack_end(widget.note_button, False, False)	
			widget.note_button.show_all()
			
		if widget.firefox_button == None:
			widget.firefox_button = self.firefox_button(widget.item)

		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			widget.box.pack_end(widget.firefox_button, False, False)	
		widget.firefox_button.show_all()			
		
		if widget.pdf != None:
			widget.ebox.modify_bg(gtk.STATE_NORMAL, self.style.bg[gtk.STATE_SELECTED])
	
	def unhighlight(self, widget = None, event = None):
		
		"""
		Unhighlight a result
		"""
				
		if widget.pdf != None:
			widget.ebox.modify_bg(gtk.STATE_NORMAL, self.style.bg[gtk.STATE_NORMAL])

		if widget.firefox_button != None:
			with warnings.catch_warnings():
				warnings.simplefilter("ignore")
	   			widget.box.remove(widget.firefox_button)

		if widget.note_button != None:
			widget.box.remove(widget.note_button)
			
	def open_pdf(self, widget = None, event = None):
		
		"""
		Open a pdf using xdg-open
		"""		
		
		if widget.pdf != None:
		
			fse = sys.getfilesystemencoding()
			
			if os.name == "nt":			
				os.startfile(widget.pdf.encode("latin-1"))
			else:
				pid = subprocess.call([self.pdf_reader_path, widget.pdf])
				print "PDF opened using %s, pid = %d" % (self.pdf_reader_path, pid)
				
	def open_note(self, widget, event = None):
		
		"""
		Opens a note in Gnote
		"""
		
		subprocess.call(widget.note.cmd.split())
		
	def open_firefox(self, widget, event = None):
		
		"""
		Opens an item in a new firefox window
		"""

		print "Opening item in firefox (key = %s)" % widget.item.key
		subprocess.Popen([self.firefox_path, "zotero://select/items/0_%s" % widget.item.key])		
		subprocess.Popen([self.firefox_path, "zotero://report/items/0_%s/html/report.html" % widget.item.key])		
		
	def firefox_button(self, item):
		
		"""
		Returns a button which selects the item in a new firefox
		window
		"""		

		im = gtk.Image()
		if self.os == "windows":
			#im.set_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_BUTTON)
			im.set_from_file("data\\icons\\firefox.png")
		else:
			im.set_from_icon_name("firefox", gtk.ICON_SIZE_BUTTON)
		im.set_tooltip_text("Show in Firefox")					
			
		button = gtk.Button()
		button.set_image(im)
		button.set_relief(gtk.RELIEF_NONE)
		button.item = item
		button.connect("clicked", self.open_firefox)
		
		return button					
		
	def retrieve_note(self, widget):
		
		"""
		Retrieves note information for a widget
		"""
		
		if widget.note_retrieved or self.notes != "gnote" or widget.item == None:
			return
		
		note = self.gnote.search(widget.item)
		
		if note != None:
			
			im = gtk.Image()
			im.set_from_icon_name("gnote", gtk.ICON_SIZE_BUTTON)
			try:
				im.set_tooltip_markup(note.preview)
			except:
				im.set_tooltip_text(note.preview)
				
			button = gtk.Button()
			button.set_image(im)
			button.set_relief(gtk.RELIEF_NONE)
			
			button.note = note
			button.connect("clicked", self.open_note)							
			widget.note_button = button	
			widget.note_retrieved = True								
							
		else:
			widget.set_tooltip_text("No note attached")						
				
	def image_button(self, stock, relief = None):
	
		"""
		Create a button containing a single stock image
		"""
	
		button = gtk.Button()
		img = gtk.Image()
		img.set_from_stock(stock, gtk.ICON_SIZE_BUTTON)
		button.set_image(img)
		if relief != None:
			button.set_relief(relief)
		return button
								
	def cmdline_arg(self, arg):
		
		"""
		Returns a command line argument
		"""
		
		try:
			return sys.argv[sys.argv.index(arg) + 1]
		except:
			return None
			
	def search(self):
	
		"""
		A basic search function, to be overridden
		"""
	
		# Disable the timer if necessary
		if self.timer_id != None:
			gobject.source_remove(self.timer_id)
			
	def live_search(self, widget):
	
		"""
		Updates the search results as you type
		"""
	
		search_term = widget.get_text()
		if len(search_term) >= self.live_search_min_char:
			if self.timer_id != None:
				gobject.source_remove(self.timer_id)
			self.timer_id = gobject.timeout_add(self.live_search_time, self.search)								

	def locate(self, path, target):

		"""
		Tries to find the location of a target file
		"""
		
		if "--verbose" in sys.argv:
			print path[len(self.home_folder):]
		
		# Don't scan filesystems that may contain recursions
		if ".gvfs" in path or ".wine" in path:
			return None
	
		for (dirpath, dirnames, filenames) in os.walk(path):
	
			for filename in filenames:
				if filename == target:
					return dirpath
		
			for dirname in dirnames:			
				location = self.locate(os.path.join(dirpath, dirname), target)
				if location != None:
					return location

		return None		
	
	def update_check(self):
		
		"""
		Depending on settings, this function checks from an update
		and displays a notification if an update is available
		"""
		
		if self.check_updates != "yes":
			return True
		
		print "gnotero_base.update_check(): opening http://www.cogsci.nl/software/gnotero/MOST_RECENT_VERSION.TXT"		
		try:
			fd = urllib.urlopen("http://files.cogsci.nl/software/gnotero/MOST_RECENT_VERSION.TXT")
			mrv = float(fd.read().strip())
		except:
			print "gnotero_base.update_check(): failed to check for update"
			return
		
		print "gnotero_base.update_check(): most recent version is %.2f" % mrv
		
		if mrv > self.version and mrv > self.ignore_updates_up_to_version:
			
			print "gnotero_base.update_check(): update found"
			
			mb = gtk.MessageDialog()		
			mb.set_title("Update available")
			mb.add_button("Please remind me later", 0)
			mb.add_button("Don't bother me again with this update", 1)
			mb.set_markup("<b>Gnotero %.2f is available</b>\n\nYou can download the latest version from\n<span size='small'>http://www.cogsci.nl/gnotero</span>" % mrv)
			if mb.run() == 1:
				print "gnotero_base.update_check(): ignoring this update"				
				self.ignore_updates_up_to_version = 0.42
				self.save_config()
				
			mb.destroy()				

