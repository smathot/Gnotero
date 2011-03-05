#!/usr/bin/env python
#-*- coding:utf-8 -*-

from distutils.core import setup
import glob

setup(name='gnotero',
	version='0.43',
	description='Quick access to your Zotero references',
	author='Sebastiaan Mathot',
	author_email='s.mathot@cogsci.nl',
	url='http://www.cogsci.nl/gnotero',
	scripts=['gnotero', 'gnoterobrowse', 'gnoteroconf', 'gnoteroctrl'],
	packages=['pygnotero'],
	package_dir={'pygnotero' : 'pygnotero'},
	data_files=[
		('share/applications', ['data/gnotero.desktop', 'data/gnoterobrowse.desktop']),
		('share/pixmaps', ['data/icons/32x32/apps/gnotero.png']),
		('share/gnotero', ['resources/gnoterobrowse.xml', 'resources/gnoteroconf.xml', ]),		
		('share/icons/hicolor/scalable/apps', glob.glob('data/icons/scalable/apps/*.svg')),
		('share/icons/hicolor/16x16/apps', glob.glob('data/icons/16x16/apps/*.png')),
		('share/icons/hicolor/22x22/apps', glob.glob('data/icons/22x22/apps/*.png')),
		('share/icons/hicolor/24x24/apps', glob.glob('data/icons/24x24/apps/*.png')),
		('share/icons/hicolor/32x32/apps', glob.glob('data/icons/32x32/apps/*.png')),		
		]
	)


