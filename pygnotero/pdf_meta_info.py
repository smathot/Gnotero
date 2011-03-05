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

import warnings
from pyPdf import PdfFileWriter, PdfFileReader

def pdf_get_meta_info(path):

	"""
	A very simple function to retrieve the author and
	title from a PDF file
	"""

	with warnings.catch_warnings():
		warnings.filterwarnings("ignore",category=DeprecationWarning)
		input1 = PdfFileReader(file(path, "rb"))
		
	info = input1.getDocumentInfo()
	
	title = info.title
	if title == "":
		title = None
	author = info.author
	if author == "":
		author = None	

	return title, author

def pdf_set_meta_info(path, title, author):

	None
	

