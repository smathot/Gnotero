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
from pygnotero import gnotero_base

class gnotero_builder(gnotero_base.gnotero_base):

	def __init__(self, xml_file):
	
		gnotero_base.gnotero_base.__init__(self)
		
		self.builder = gtk.Builder()
		
		self.xml_file = xml_file
		
		if os.path.exists("resources/%s" % xml_file):
			self.builder.add_from_file("resources/%s" % xml_file)
		elif os.path.exists("/usr/local/share/gnotero/%s" % self.xml_file):
			self.builder.add_from_file("/usr/local/share/gnotero/%s" % self.xml_file)
		else:
			self.builder.add_from_file("/usr/share/gnotero/%s" % self.xml_file)
			
		self.builder.connect_signals({ "on_window_destroy" : gtk.main_quit })
		self.window = self.builder.get_object("MainWindow")
		self.window.connect("destroy", self.destroy)			
		
	def destroy(self, widget = None, data = None):

		gtk.main_quit()
				
	def main(self):
		
		gtk.main()		
		
