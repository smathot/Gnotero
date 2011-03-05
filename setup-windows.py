from distutils.core import setup
import py2exe

setup(


	windows = ["gnotero"],
	data_files=[
	('data/icons', [
	  'data/icons/firefox.png',
	  'data/icons/gnotero.png',
	  'data/icons/go-next.png',
	  'data/icons/go-previous.png',	  
	  ]
	),
	('lib/gtk-2.0/2.10.0/engines', ['C:\\gtk-2.16\\lib\\gtk-2.0\\2.10.0\\engines\\libclearlooks.dll']),
	('share/themes/Clearlooks/gtk-2.0', ['C:\\gtk-2.16\\share\\themes\\Clearlooks\\gtk-2.0\gtkrc']),
	('etc/gtk-2.0', ['C:\\gtk-2.16\\etc\\gtk-2.0\gtkrc']),
	],
	options = {
	'py2exe' : {
		'bundle_files' : 3,
		'includes': 'cairo, pango, pangocairo, gtk, gio, atk, gobject',
	}
	}


)
