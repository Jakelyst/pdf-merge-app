import subprocess
import tkinter
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from pathlib import Path
from PyPDF2 import PdfFileMerger


list_of_paths = []


def add_to_list() -> None:
	"""Add user selected files to the list of files to be combined."""
	
	def get_file_paths() -> list[Path]:
		"""Open a system dialog window for the user to select files, and 
		return the paths to those files.
		"""
		file_paths = askopenfilenames(filetypes=[("PDF Files", "*.pdf")])

		# Convert strings of paths into pathlib Path objects.
		file_paths = [Path(file_path) for file_path in file_paths]
		return file_paths
	
	# Clear any existing selected files before getting new selection.
	listbox.delete(0, tkinter.END)
	list_of_paths.clear()
	file_paths = get_file_paths()

	# Add the names of the selected files to the listbox.
	for path in file_paths:
		listbox.insert(tkinter.END, path.name)
		list_of_paths.append(path)  # Add full paths to global list_of_paths


def save_PDF() -> None:
	"""Open a system dialog window for the user to select a location to save 
	the combined file. Then combine the pdfs and save the combined pdf to
	the file location selected by the user.
	"""
	# Get list of the files in the order they appear in the interface.
	list_as_shown = list(listbox.get(0, tkinter.END))
	
	def sort_by_index(list_item: Path) -> int:
		"""Reorder the list of the full path names to be in the same order as
		the list of file names arranged by the user.
		"""
		nonlocal list_as_shown
		name = list_item.name
		return list_as_shown.index(name)
	
	def merge_PDFs(paths : list[Path]) -> PdfFileMerger:
		"""Create a PdfFileMerger object with the combined files."""
		pdf_merger = PdfFileMerger()
		for path in paths:
			pdf_merger.append(str(path))
		return pdf_merger

	# Merge the pdfs.
	#pdfPaths = list_of_paths.sort(key=sort_by_index)
	pdf_paths = sorted(list_of_paths, key=sort_by_index)
	pdf_merger = merge_PDFs(pdf_paths)

	# Save the combined pdf.
	file_path = asksaveasfilename(filetypes=[("PDF Files", "*.pdf")])
	with Path(file_path).open(mode='wb') as output_file:
		pdf_merger.write(output_file)

	# Try to open the comnined pdf file to view it if on Windows.
	try:
		subprocess.run(["start", '', str(file_path)], shell=True)
	except Exception:
		# Failing that, try MacOS.
		try:
			subprocess.run(["open", str(file_path)])
		except Exception:
			# Failing that, try linux.
			try:
				subprocess.run(["xdg-open", str(file_path)])
			except Exception:
				# Failing that, leave file unopened.
				pass


class DragDropListBox(tkinter.Listbox):
	"""A tkinter listbox with drag and drop reordering of entries."""
	def	__init__(self, master, **kw):
		#kw['selectmode'] = tkinter.SINGLE
		kw['selectmode'] = tkinter.BROWSE
		tkinter.Listbox.__init__(self, master, kw)
		self.bind('<Button-1>', self.setCurrent)
		self.bind('<B1-Motion>', self.shiftSelection)
		self.curIndex = None

	def	setCurrent(self, event):
		self.curIndex = self.nearest(event.y)

	def shiftSelection(self, event):
		i = self.nearest(event.y)
		if i < self.curIndex:
			x = self.get(i)
			self.delete(i)
			self.insert(i+1, x)
			self.curIndex = i
		elif i > self.curIndex:
			x = self.get(i)
			self.delete(i)
			self.insert(i-1, x)
			self.curIndex = i


if __name__ == "__main__":
	root = tkinter.Tk()
	root.geometry('400x400')
	root.title("PDF Merge")
	listbox = DragDropListBox(root)
	listbox.pack(fill=tkinter.BOTH, expand=True)
	button = tkinter.Button(root, command=add_to_list, text='Select PDFs')
	button2 = tkinter.Button(root, command=save_PDF, text='Combine & save')
	button.pack()
	button2.pack()
	root.mainloop()