# -------------------------------------------------------------------------------
# Name:        widget_notepad
# Purpose:     widget for txt file
#
# Author:      Didier Mathias
# Created:     02/05/2023
# -------------------------------------------------------------------------------

import os.path as path
import sys
sys.path.append(path.join(path.dirname(__file__)))

from editors.editor_widget import Editor_widget as Widget
from editors.texteditor import Texteditor


class Widget_notepad(Widget):
    def __init__(self, *args, **kwargs):
        filepath = kwargs.pop('filepath', None)

        Widget.__init__(self, *args, **kwargs)

        # space repartion configuration
        self.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=1)

        # text editor widget
        self.text = Texteditor(self, filepath=filepath, extension='.txt',
                               filetypes=[("TEXT (*.txt)", '.txt')])

        # placement on the grid
        self.text.grid(row=0, column=0, columnspan=2, sticky='nsew')

        self.binding()

        if filepath is not None:
            self.open_file(filepath)

    # region heritage

    def set_data_path(self, dirpath):
        Widget.set_data_path(self, dirpath)
        Texteditor.set_data_path(Texteditor, dirpath)

    def _modification(self, *event):
        """ set text to modify status """
        Widget._modification(self)

    def binding(self):
        self.text.set_binding()
        self.text.bind('<<Text-Modification>>', self._modification)

    def new_file(self):
        self.text.new()

        self.isModify = False

    def open_file(self, filepath=None):
        self.text.open(filepath)

        self.isModify = False

    def save_file(self, filepath=None):
        filepath = Widget.save_file(self, filepath)

        self.text.save(filepath)
        self.isModify = False

    def save_as_file(self, filepath=None):
        filepath = Widget.save_as_file(self, filepath)
        self.text.save_as(filepath)
        self.isModify = False

    # endregion heritage

    # region text changes

    def clean(self):
        self.text.clean()

        self.isModify = False

    # endregion text changes


if __name__ == "__main__":
    from tkinter import Tk

    root = Tk()
    root.title("text class")
    root.geometry("300x300")

    txt = Widget_notepad(root)
    txt.pack(expand=True, fill='both')

    root.mainloop()
