# -------------------------------------------------------------------------------
# Name:        editor_widget
# Purpose:     base class for app tab
#
# Author:      Didier Mathias
# Created:     02/05/2023
# -------------------------------------------------------------------------------

from tkinter import Frame
from tkinter.filedialog import askopenfilename
import os.path as path


class Editor_widget(Frame):
    """
    event:
        Modification    >> all modification on widget
    """

    PATH_DATA = path.join(path.dirname(__file__), 'data')

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        self.filetypes = []
        self.isModify = False

    def set_data_path(self, path):
        self.PATH_DATA = path

    def _modification(self, *args):
        """ set text to modify status """
        self.event_generate('<<Modification>>')
        self.isModify = True

    def binding(self):
        pass

    def new_file(self):
        pass

    def open_file(self, filepath=None):
        if filepath is None:
            return askopenfilename(title='Open File', filetypes=self.filetypes)
        return filepath

    def save_file(self, filepath=None):
        if filepath is None:
            return askopenfilename(title='Open File', filetypes=self.filetypes)
        return filepath

    def save_as_file(self):
        pass
