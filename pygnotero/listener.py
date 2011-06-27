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

import threading
import gobject
import socket
import time

gobject.threads_init()

class Listener(threading.Thread):

	"""
	Listens for commands.
	"""

	def __init__(self, gnotero, port = 43250):
	
		"""
		Constructor
		"""
	
		self.port = port
		self.gnotero = gnotero
		self.alive = True
		threading.Thread.__init__(self)

	def run(self):

		"""
		This function is spawned as a thread and handles communications.
		Communication is through UDP.
		"""

		# Create a socket and bind it to the first available port (starting from the preferred port)
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			sock.bind(("", self.port))
			print "listener.run(): listening on port %d" % self.port		
		except:
			print "listener.run(): failed to open port %d" % self.port		
			return
			
		sock.settimeout(0.5)
		
		# Loop infinitely until the application is quit somewhere else
		while self.alive:
				
			# Wait for an incoming request
			
			try:
				s, comm_addr = sock.recvfrom(128)
			except:
				s = None
				
			if s != None:
				print "listener.run(): received '%s'" % s

				if s[:6] == "search":
				
					# Set the search entry, disable clipboard use (if enabled)
					# and emit the activate signal
				
					print "listener.run(): searching for '%s'" % s[7:]
					self.gnotero.search_edit.set_text(s[7:])
					tmp = self.gnotero.use_clipboard
					self.gnotero.use_clipboard = "no"
					gobject.idle_add(self.gnotero.emit, "activate")	
					time.sleep(0.2)
					self.gnotero.use_clipboard = tmp									

				elif "activate" == s[:8]:
				
					# Show the window
				
					print "listener.run(): activating"
					gobject.idle_add(self.gnotero.emit, "activate")	
							
