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
import pango
import subprocess
from pygnotero import gnotero_builder, pdf_meta_info
import sys
import re, htmlentitydefs		
import thread
import time
import shutil
import warnings

class gnoterobrowse(gnotero_builder.gnotero_builder):

	def __init__(self):
	
		"""
		Initialize gnoterobrowse
		"""
	
		# Load the gui file
		if os.name == "nt":
			gnotero_builder.gnotero_builder.__init__(self, "gnoterobrowse-windows.xml")	
		elif os.name == "posix":
			gnotero_builder.gnotero_builder.__init__(self, "gnoterobrowse.xml")	
		else:
			print "gnoterobrowse.__init__(): You appear to be running an unsupported OS"
		
		# Determine the default path
		# Fall back to the homefolder if the sync_path does not exisrb
		if os.path.exists(self.sync_path):
			self.current_path = self.sync_path
		else:
			self.current_path = self.home_folder
			
		# Main HBox
		
		self.hbox_main = self.builder.get_object("hbox_main")						
		
		# Top panel
		
		self.hbox_label = self.builder.get_object("hbox_label")
		self.ebox_label = self.builder.get_object("ebox_label")
		self.label_header = self.builder.get_object("label_header")
		self.label_header.set_markup("<big><b>Gnoterobrowse</b></big>\n<small>Version %.2f</small>" % self.version)			

		self.button_zotero = self.builder.get_object("button_zotero")
		self.button_zotero.connect("clicked", self.start_zotero)				
		
		self.button_gnoteroconf = self.builder.get_object("button_gnoteroconf")
		self.button_gnoteroconf.connect("clicked", self.start_gnoteroconf)		

		self.button_about = self.builder.get_object("button_about")
		self.button_about.connect("clicked", self.about)				
				
		# Progressbar
				
		self.progressbar = self.builder.get_object("progressbar")												
		
		# Left panel (collections)
		
		self.collection_vbox = self.builder.get_object("collection_vbox")			
		self.button_all_items = self.builder.get_object("button_all_items")
		self.button_all_items.connect("clicked", self.show_all)		
		self.button_to_read = self.builder.get_object("button_to_read")
		self.button_to_read.connect("clicked", self.browse_collection, "To read")
			
		# Middle panel (Zotero library)

		self.search_entry = self.builder.get_object("search_entry")
		self.search_entry.connect("activate", self.search)		
		self.button_search = self.builder.get_object("button_search")
		self.button_search.connect("clicked", self.search)				
				
		self.button_copy_all = self.builder.get_object("button_copy_all")
		self.button_copy_all.connect("clicked", self.copy_all)		
		
		self.results_scrolledwindow = self.builder.get_object("results_scrolledwindow")		
		self.results_vbox = gtk.VBox()
		self.results_vbox.set_spacing(4)
		self.results_vbox.set_border_width(4)
		self.results_vbox.set_homogeneous(False)
		self.results_scrolledwindow.add_with_viewport(self.results_vbox)							
		
		# Right panel (Browser)
		
		self.button_browse = self.builder.get_object("button_browse")
		self.button_browse.connect("clicked", self.browse_filesystem)				
		
		self.entry_sync_path = self.builder.get_object("entry_sync_path")
		self.entry_sync_path.set_text(self.current_path)
		self.entry_sync_path.connect("activate", self.set_current_path)					
		
		self.device_scrolledwindow = self.builder.get_object("device_scrolledwindow")		
		self.device_vbox = gtk.VBox()
		self.device_vbox.set_spacing(4)
		self.device_vbox.set_border_width(4)
		self.device_vbox.set_homogeneous(False)
		self.device_scrolledwindow.add_with_viewport(self.device_vbox)					
		
		self.button_refresh = self.builder.get_object("button_refresh")
		self.button_refresh.connect("clicked", self.build_filesystem_list)							
		
		# Set the search term from the command line
		
		search_term = self.cmdline_arg("-s")
		if search_term != None:
			self.search_entry.set_text(search_term)			
			
		# Set the current path from the command line
			
		path = self.cmdline_arg("-p")
		if path != None and os.path.isdir(path):
			
			self.current_path = path
			self.entry_sync_path.set_text(self.current_path)
			
		# Start copying in mini-mode if this is requested
			
		if "-n" in sys.argv:			
			self.window.show_all()			
			self.hbox_main.hide()
			self.window.resize(400, 40)
			self.copy_all()
			
			# Quit after copying if this is requested
			
			if "-q" in sys.argv:
				quit()				
				
		# Realize the main window
				
		self.build_collection_list()
		self.build_filesystem_list()
		self.window.realize()		
		self.style = self.window.get_style()
		self.window.show_all()
		self.window.resize(800, 600)
		self.progressbar.hide()	
		
		# Set pane
		
		self.hpane = self.builder.get_object("hpane")
		self.hpane.set_position(350)
		
		if "To Read" in self.zotero.collection_index:
			self.browse_collection(None, "To read")
			
		if self.enable_live_search == "yes":
			print "gnoterobrowse.__init__(): enabling live search"
			self.search_entry.connect("changed", self.live_search)									
				
	def show_all(self, widget):
	
		"""
		Show all items
		"""
		
		self.search_entry.set_text("")
		self.search()
		
	def unescape(self, text):
		
		"""
		This function unescapes HTML entities, which are
		returned by PDFtk
	
		Taken from
		http://effbot.org/zone/re-sub.htm#unescape-html
		
		Copyright (C) 1995-2010 by Fredrik Lundh

		By obtaining, using, and/or copying this software and/or its associated documentation,
		you agree that you have read, understood, and will comply with the following terms and conditions:

		Permission to use, copy, modify, and distribute this software and its associated documentation
		for any purpose and without fee is hereby granted, provided that the above copyright notice appears
		in all copies, and that both that copyright notice and this permission notice appear in supporting
		documentation, and that the name of Secret Labs AB or the author not be used in advertising or
		publicity pertaining to distribution of the software without specific, written prior permission.
		"""
				
		def fixup(m):
		    text = m.group(0)
		    if text[:2] == "&#":
		        # character reference
		        try:
		            if text[:3] == "&#x":
		                return unichr(int(text[3:-1], 16))
		            else:
		                return unichr(int(text[2:-1]))
		        except ValueError:
		            pass
		    else:
		        # named entity
		        try:
		            text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
		        except KeyError:
		            pass
		    return text # leave as is
		return re.sub("&#?\w+;", fixup, text)		
		
	def metadata_thread(self, args):
		
		"""
		This function is called as a thread
		and retrieves the metadata of all PDFs currently
		in the file browser
		"""
		
		todo = args
		while len(todo) > 0:
			try:									
				box = todo.pop(0)
				box.label.set_markup("<b>%s</b>\n<small><i>Working</i></small>" % os.path.basename(box.delete_button.path).replace("&", "&amp;"))			
				title, author = pdf_meta_info.pdf_get_meta_info(box.delete_button.path)
				
				if title != None and author != None:
					markup = "<span size ='small' color='#cc0000' weight='bold'>[PDF]</span> <b>%s</b>\n<small>%s</small>" % (author, title)				
				elif title == None and author != None:
					markup = "<span size ='small' color='#cc0000' weight='bold'>[PDF]</span> <b>%s</b>\n<small>No title</small>" % author
				elif title != None and author == None:
					markup = "<span size ='small' color='#cc0000' weight='bold'>[PDF]</span> <b>%s</b>\n<small>No author</small>" % title
				else:
					markup = "<span size ='small' color='#cc0000' weight='bold'>[PDF]</span> <b>%s</b>\n<small>No metadata</small>" % os.path.basename(box.delete_button.path).replace("&", "&amp;")				
					
				try:
					box.label.set_markup(markup)
				except:
					box.label.set_markup("<span size ='small' color='#cc0000' weight='bold'>[PDF]</span> <b>%s</b>\n<small>No metadata</small>" % os.path.basename(box.delete_button.path).replace("&", "&amp;"))
			except:
				box.label.set_markup("<span size ='small' color='#cc0000' weight='bold'>[PDF]</span> <b>%s</b>\n<small>No metadata</small>" % os.path.basename(box.delete_button.path).replace("&", "&amp;"))
				break	
			time.sleep(0.05)
			
	def pdf_box(self, author, title, pdf):
	
		"""
		Creates a pretty box to contain a pdf file
		"""

		title = "<b>%s</b>\n<small>%s</small>" % (author, title)	
		title = title.replace("&", "&amp;")
	
		pdf_box = self.pretty_box(title, self.open_pdf, self.highlight_pdf, self.unhighlight_pdf, True)
		
		# Sometimes the markup doesn't take, then replace it with it something similar
		if pdf_box.label.get_text() == "":
			title = "<b>%s</b>\n<small>%s</small>" % (pdf, "Unknown title")	
			title = title.replace("&", "&amp;")
			pdf_box.label.set_markup("<span size ='small' color='%s' weight='bold'>[PDF]</span> %s" % ("#cc0000", title))
		
		pdf_box.delete_button = self.image_button(gtk.STOCK_DELETE, gtk.RELIEF_NONE)
		pdf_box.delete_button.connect("clicked", self.delete_pdf)
		pdf_box.delete_button.path = pdf_box.ebox.pdf = os.path.join(self.current_path, pdf)					
		
		return pdf_box 	
		
	def highlight_pdf(self, widget = None, event = None):
				
		"""
		Highlight a result, but only if a pdf is attached
		"""	
		
		widget.ebox.modify_bg(gtk.STATE_NORMAL, self.style.bg[gtk.STATE_SELECTED])				
		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			widget.box.pack_end(widget.delete_button, False, False)	
		widget.delete_button.show_all()
		
	
	def unhighlight_pdf(self, widget = None, event = None):
		
		"""
		Unhighlight a result
		"""
				
		widget.ebox.modify_bg(gtk.STATE_NORMAL, self.style.bg[gtk.STATE_NORMAL])						
		widget.box.remove(widget.delete_button)		
		
	def highlight_folder(self, widget = None, event = None):
				
		"""
		Highlight a result, but only if a pdf is attached
		"""	
		
		widget.ebox.modify_bg(gtk.STATE_NORMAL, self.style.bg[gtk.STATE_SELECTED])
	
	def unhighlight_folder(self, widget = None, event = None):
		
		"""
		Unhighlight a result
		"""
				
		widget.ebox.modify_bg(gtk.STATE_NORMAL, self.style.bg[gtk.STATE_NORMAL])		
			
	def open_folder(self, widget = None, event = None):
		
		"""
		Open a pdf using xdg-open
		"""		
		
		if event.button != 3:
		
			self.entry_sync_path.set_text(widget.folder)
			self.set_current_path()
		
	def folder_box(self, name):
	
		"""
		Creates a pretty box to contain folders
		"""
		
		folder_box = self.pretty_box("<b>%s</b>" % (name), self.open_folder, self.highlight_folder, self.unhighlight_folder, True)
		folder_box.delete_button = None
		
		if name == "Go up ..":
			# Translate the name "Go up .. " into the parent folder
			folder_box.ebox.folder = os.path.dirname(self.current_path)
		else:
			folder_box.ebox.folder = os.path.join(self.current_path, name)																			
								
		return folder_box		
															
	def set_current_path(self, widget = None):
	
		"""
		Changes the current path based on what's in the entry sync path
		"""
	
		path = self.entry_sync_path.get_text()
		if os.path.isdir(path):
			self.current_path = path
			self.build_filesystem_list()
		self.entry_sync_path.set_text(self.current_path)			
		
	def browse_filesystem(self, widget):
	
		"""
		Open a new folder in the device list
		"""
		
		fd = gtk.FileChooserDialog("Open folder", None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		if fd.run() == gtk.RESPONSE_OK:
			self.current_path = fd.get_filename()
			self.entry_sync_path.set_text(self.current_path)
			self.build_filesystem_list()
		fd.destroy()		
		
	def build_filesystem_list(self, widget = None, get_metadata = True):
	
		"""
		Read the files from the sync_path and create a listing.
		If possible extract PDF information from the files
		"""
	
		# Remove all entries
		self.device_vbox.foreach(lambda widget:self.device_vbox.remove(widget))
		
		if os.path.exists(self.current_path):
		
			if self.current_path != "/":
				self.device_vbox.pack_start(self.folder_box("Go up .."), False, False)	

			try:		
				contents = os.listdir(self.current_path)						
			except:
				self.device_vbox.show_all()
				return
			
			# First list the sub directories
			for item in contents:				
				if os.path.isdir(os.path.join(self.current_path, item)) and item[0] != ".":					
					self.device_vbox.pack_start(self.folder_box(item), False, False)	
			
			todo = []
			# Then list the PDF files
			for item in contents:			
				s = os.path.splitext(item) 
				if len(s) > 1 and s[1].lower() == ".pdf":						
					box = self.pdf_box(os.path.basename(item), "Waiting to retrieve metadata", item)
					todo.append(box)
					self.device_vbox.pack_start(box, False, False)		
					
		self.device_vbox.show_all()
		if get_metadata and self.pdf_use_metadata == "yes":
			thread.start_new_thread(self.metadata_thread, (todo, ))
		
	def delete_pdf(self, widget):
	
		"""
		Delete a file from the device
		"""
		
		if os.path.exists(widget.path):
			os.remove(widget.path)
			print "gnoterobrowse.delete_pdf(): deleted %s\n" % os.path.basename(widget.path)
		self.build_filesystem_list()

	def build_collection_list(self):
	
		"""
		Create buttons to match the collections in the
		Zotero database
		"""
		
		for collection in self.zotero.collection_index:
			if collection.lower() != "to read":
				
				label = gtk.Label(collection)
				label.set_justify(gtk.JUSTIFY_LEFT)
				image = gtk.Image()
				image.set_from_icon_name("emblem-documents", gtk.ICON_SIZE_MENU)
				hbox = gtk.HBox()
				hbox.set_spacing(4)
				hbox.pack_start(image, False, False)				
				hbox.pack_start(label, False, False)
				button = gtk.Button()
				button.add(hbox)				
				button.set_relief(gtk.RELIEF_NONE)
				button.connect("clicked", self.browse_collection, collection)
				self.collection_vbox.pack_start(button, False, False)	
					
		self.button_all_items = self.builder.get_object("button_all_items")
		self.button_all_items.connect("clicked", self.show_all)

	def browse_collection(self, widget, collection):
	
		"""
		Set the search term to search for a collection
		and start the search
		"""
	
		self.search_entry.set_text("collection: \"%s\"" % collection)
		self.search()			
		
	def search(self, widget = None):
	
		"""
		Search the zotero database
		"""
		
		gnotero_builder.gnotero_builder.search(self)		
			
		self.results_vbox.foreach(lambda widget:self.results_vbox.remove(widget))
		search_term = self.search_entry.get_text()
		
		items = self.zotero.search(search_term)
		for item in items:
			
			event_box = self.item_box(item, True)
			event_box.copy_button = None
			self.results_vbox.pack_start(event_box, False, False)				
						
		self.results_scrolledwindow.show_all()
		
	def copy_item(self, item):
	
		"""
		Copies one item to the sync_path
		"""
				
		# Only process articles with an attached pdf
		if item.fulltext != None:					

			# Determine the filename on the target device and the local filename
			target_file = item.filename_format()
		
			# For some reason os.path.join() doesn't work, so just concatting
			source_file = item.fulltext.encode("latin-1")
		
			# If there are multiple articles with the same name, append suffixes
			i = 0
			while os.path.exists(os.path.join(self.current_path, unicode("%s-%d.pdf" % (target_file, i)))):
				i += 1
			target_file = unicode("%s-%d.pdf" % (target_file, i))
			
			# Create a metadata file
			author = item.simple_format()
			title = item.format_title()
			metadata = "InfoKey: Author\nInfoValue: %s\nInfoKey: Title\nInfoValue: %s\n" % (author, title)
			f = open("/tmp/ersyncdata.txt", "w")
			f.write(metadata)
			f.close()
			
			# Do not copy directly, but use pdftk to change the metadata	
			retcode = subprocess.call(["pdftk", source_file, "update_info", "/tmp/ersyncdata.txt", "output", "%s" % os.path.join(self.current_path, target_file)])
			if retcode != 0:
				print "gnoterobrowse.copy_item(): failed to insert metadata %s, doing plain copy" % source_file	
				shutil.copyfile(source_file, os.path.join(self.current_path, target_file))
								
			while gtk.events_pending(): gtk.main_iteration()
			self.build_filesystem_list(None, False)			
			
	def copy_one(self, widget):
		
		"""
		Copies a single file to the current path
		"""
				
		# Prepare the progressbar
		self.progressbar.show()
		self.progressbar.set_fraction(0.5)			
		self.progressbar.set_text("Copying '%s' to %s" % (widget.item.simple_format(), self.current_path))
		while gtk.events_pending(): gtk.main_iteration()

		# Copy the item
		self.copy_item(widget.item)

		# Hide the progressbar
		self.progressbar.hide()		
		self.build_filesystem_list(None, True)					
			
	def copy_all(self, widget = None):
	
		"""
		Synchronize the results to the e-reader
		"""
		
		# Check if the path exists
		if not os.path.exists(self.current_path):
			return
		
		# Get a list of files on the device
		target_files = []
		for fname in os.listdir(self.current_path):
			target_files.append(fname)
			

		# Walk through all articles in the database
		synced_files = []
		results = self.zotero.search(self.search_entry.get_text())

		# Prepare the progressbar
		self.progressbar.show()

		i = 0
		for item in results:	
		
			# Update the progressbar and show results
			self.progressbar.set_text("Copying '%s' to %s" % (item.simple_format(), self.current_path))		
			self.progressbar.set_fraction(1.0 * i / len(results))			
			while gtk.events_pending(): gtk.main_iteration()				
			
			self.copy_item(item)
			i += 1
			
		# Hide the progressbar
		self.progressbar.hide()
		self.build_filesystem_list(None, True)					
				
	def highlight(self, widget = None, event = None):
				
		"""
		Adds a copy button to the highlight
		"""	
		
		if widget.pdf != None:
			im = gtk.Image()
			im.set_from_stock(gtk.STOCK_GO_FORWARD, gtk.ICON_SIZE_BUTTON)
			widget.copy_button = gtk.Button()		
			widget.copy_button.set_image(im)
			widget.copy_button.set_relief(gtk.RELIEF_NONE)
			widget.copy_button.item = widget.item
			widget.copy_button.connect("clicked", self.copy_one)
			widget.copy_button.set_tooltip_text("Copy item")
			widget.box.pack_end(widget.copy_button, False, False)	
			widget.copy_button.show_all()
		gnotero_builder.gnotero_builder.highlight(self, widget, event)		
	
	def unhighlight(self, widget = None, event = None):
		
		"""
		Removes copy button from the highlight
		"""
				
		if widget.copy_button != None:
			widget.box.remove(widget.copy_button)				
		gnotero_builder.gnotero_builder.unhighlight(self, widget, event)								

