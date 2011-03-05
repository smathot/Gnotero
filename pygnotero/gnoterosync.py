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
from pygnotero import zoterotools
from pygnotero import gnotero_builder
import pytools
import sys

class gnoterosync(gnotero_builder.gnotero_builder):

	def __init__(self):
	
		gnotero_builder.gnotero_builder.__init__(self, "gnoterosync.xml")				

		self.sync_term = self.builder.get_object("sync_term")
		self.sync_button = self.builder.get_object("sync_button")
		self.output = self.builder.get_object("output")
		self.output_buffer = self.builder.get_object("output_buffer")
		self.close_button = self.builder.get_object("close_button")
		self.settings_button = self.builder.get_object("settings_button")		
		self.settings_entry = self.builder.get_object("settings_entry")			    			    
		
		self.settings_entry.set_markup("<b>%s</b>\n<span size='small'>%s</span>" % (self.sync_name, self.sync_path))		
	    						
		if pytools.cmdline_arg("-s") != None:			
			self.sync_term.set_text(pytools.cmdline_arg("-s"))
		self.sync_term.connect("activate", self.sync)
		
		self.sync_button.connect("clicked", self.sync)
		self.settings_button.connect("clicked", self.start_gnoteroconf)		
		self.close_button.connect("clicked", self.destroy)
		self.window.resize(300, 400)
		
		self.window.show_all()
		
		if "-n" in sys.argv and pytools.cmdline_arg("-s") != None:
			self.sync()
		
	def sync(self, argv = None):
	
		"""
		Synchronize the results to the e-reader
		"""
		
		if not os.path.exists(self.sync_path):
			self.output_buffer.insert_at_cursor("Target path not found: %s\nDo you have a device configured and attached to your computer?\n" % self.sync_path)
			return
		
		# Get a list of files on the device
		target_files = []
		for fname in os.listdir(self.sync_path):
			target_files.append(fname)
			
		self.output_buffer.insert_at_cursor("Copying .pdf files matching '%s' ...\n" % self.sync_term.get_text())
	
		# Walk through all articles in the database
		print
		print "Copying new files"
		synced_files = []
		for item in zoterotools.search_zotero(self.sync_term.get_text(), "notags"):
	
			# Only process articles with an attached pdf
			if len(item) > 2:
	
				# Determine the filename on the target device and the local filename
				target_file = unicode("%s.pdf" % item[0]).encode("ascii", "ignore").replace("\\", "")
				
				# For some reason os.path.join() doesn't work, so just concatting
				source_file = unicode(item[1]).encode("latin-1")
				
				# If there are multiple articles with the same name, append suffixes
				i = 0
				for fname in synced_files:
					if fname == target_file:
						i += 1
						target_file = unicode("%s-%d.pdf" % (item[0], i)).encode("ascii", "ignore").replace("\\", "")
						
				# Create a metadata file
				author = unicode(item[0]).encode("ascii", "ignore")
				title = unicode(item[2]["title"]).encode("ascii", "ignore")
				metadata = "InfoKey: Author\nInfoValue: %s\nInfoKey: Title\nInfoValue: %s\n" % (author, title)
				f = open("/tmp/ersyncdata.txt", "w")
				f.write(metadata)
				f.close()
		
				# Do not copy directly, but use pdftk to change the metadata
				cmd = "pdftk \"%s\" update_info /tmp/ersyncdata.txt output \"%s\"" % (source_file, os.path.join(self.sync_path, target_file))	
			
				synced_files.append(target_file)
	
				# If the target file is not present on the target device, copy it
				if target_file not in target_files:
					print "=>", target_file
					#shutil.copy(source_file, "%s/%s" % (target_dir, target_file))
					retcode = subprocess.call(["pdftk", source_file, "update_info", "/tmp/ersyncdata.txt", "output", "%s" % os.path.join(self.sync_path, target_file)])
					if retcode != 0:
						print "Failed to copy %s" % source_file		
					
					self.output_buffer.insert_at_cursor("Copying %s ...\n" % (target_file))
							
				else:
					target_files.remove(target_file)
					
					self.output_buffer.insert_at_cursor("Skipping %s ...\n" % (target_file))
					
				while gtk.events_pending(): gtk.main_iteration()
				
		self.output_buffer.insert_at_cursor("Finished!\n")
		

