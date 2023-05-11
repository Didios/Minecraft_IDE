# -------------------------------------------------------------------------------
# Name:        widget_mcfunction
# Purpose:     widget for mcfunction file
#
# Author:      Didier Mathias
# Created:     24/12/2022
# Refactor:    02/05/2023
# -------------------------------------------------------------------------------

from tkinter import Text, Scrollbar

import json
import os.path as path
import sys
sys.path.append(path.join(path.dirname(__file__)))

from debugger import debug as debugger
from result import Result

from editors.editor_widget import Editor_widget as Widget
from editors.texteditor import Texteditor, to_text_coord, to_list_coord


def is_command(line):
    """ check if a line is a command """
    if len(line) == 0:
        return False

    if line[0] == "#":
        return False

    for char in line:
        if char not in [' ', '\n', '\r']:
            return True

    return False


def is_comment(line):
    """ check if line is a comment """
    if len(line) == 0:
        return False

    if line[0] == '#':
        return True

    return False


class Widget_mcfunction(Widget):
    AUTO_CHECK = True
    VERSION = '1.19.2'

    STYLESHEET = path.join(path.dirname(__file__), 'data', 'style', 'text.json')
    DATASHEET = path.join(path.dirname(__file__), 'data', 'style', 'data.json')

    def __init__(self, *args, **kwargs):
        filepath = kwargs.pop('filepath', None)
        self.debug = debugger(kwargs.pop('version', self.VERSION))

        Widget.__init__(self, *args, **kwargs)

        # space repartion configuration
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=0)

        # text editor widget
        self.text = Texteditor(self, filepath=filepath, extension='.mcfunction',
                               filetypes=[("minecraft MCFUNCTION (*.mcfunction)", '.mcfunction')])

        # widget for display error
        self.display_error = Text(self, height=10, wrap='none', state='disabled')

        # scrollbar
        self.y_scroll_error = Scrollbar(self, orient='vertical')
        self.x_scroll_error = Scrollbar(self, orient='horizontal')

        # special config
        self.display_error.config(yscrollcommand=self.y_scroll_error.set, xscrollcommand=self.x_scroll_error.set)
        self.y_scroll_error.config(command=self.display_error.yview)
        self.x_scroll_error.config(command=self.display_error.xview)

        # placement on the grid
        self.text.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.display_error.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.y_scroll_error.grid(row=1, column=1, sticky='ns')
        self.x_scroll_error.grid(row=2, column=0, sticky='ew')

        # get editor custom data
        file = open(self.DATASHEET)
        editorData = json.load(file)
        file.close()

        # set text font
        fontData = editorData["a_data"][editorData["a_index"].index("font")]
        fontUse = (fontData["name"], fontData["size"], fontData["type"])
        self.display_error.config(font=fontUse)

        # debug variable
        self.debugList = [Result()]

        # colors
        self.colorIndex = []
        self.__set_color_tags()

        self.binding()

        if filepath is not None:
            self.open_file(filepath)

    # region heritage

    def set_data_path(self, dirpath):
        Widget.set_data_path(self, dirpath)

        self.STYLESHEET = path.join(dirpath, 'style', 'text.json')
        self.DATASHEET = path.join(dirpath, 'style', 'data.json')

        debugger.set_data_path(debugger, dirpath)
        Texteditor.set_data_path(Texteditor, dirpath)

    def _modification(self, *event):
        """
        set text to modify status
        debug current line
        update errorDisplay
        """
        Widget._modification(self)

        len_text = self.text.get_length()
        len_debug = len(self.debugList)
        if len_text < len_debug:
            self.debugList = self.debugList[0:len_text]
        else:
            self.debugList += [Result() for _ in range(len_text - len_debug)]

        if self.AUTO_CHECK:
            positionCursor = to_list_coord(self.text.get_cursor_index())
            self.debug_line(positionCursor[1])

    def binding(self):
        self.text.set_binding()
        self.text.bind('<<Text-Modification>>', self._modification)

    def new_file(self):
        self.text.new()
        self.debugList = [Result() for _ in range(self.text.get_length())]

        self.isModify = False

    def open_file(self, filepath=None):
        self.text.open(filepath)

        self.display_error.replace(0.0, 'end', "")
        self.debugList = [Result() for _ in range(self.text.get_length())]

        self.isModify = False

    def save_file(self, filepath=None):
        filepath = Widget.save_file(self, filepath)

        self.text.save(filepath)
        self.isModify = False

    def save_as_file(self, filepath=None):
        filepath = Widget.save_as_file(self, filepath)
        self.text.save_as()
        self.isModify = False

    # endregion heritage

    # region private methods

    def __set_color_tags(self):
        """
        create all tag for different color of text use
        see editor/text.json for tag specificity
        """
        file = open(self.STYLESHEET)
        colorData = json.load(file)
        file.close()

        self.colorIndex = colorData["a_index"]

        self.display_error.tag_config("goto_error",
                                      background="white",
                                      foreground="red",
                                      underline=True)

        self.display_error.tag_bind("goto_error", "<Double-Button-1>", self.__goto_error)

    def __goto_error(self, *args):
        """ move text to error currently selected """
        indexLine = to_list_coord(self.display_error.index('insert'))[1]

        indexError = 0
        indexText = 0
        while indexError != indexLine:
            if self.debugList[indexText].is_error():
                indexError += 1
            indexText += 1

        position = to_text_coord(*self.debugList[indexText].get_position())
        self.text.see(position)

    def __set_color_line(self, index):
        """ set color for the current line """

        # get line modify data
        line = self.text.get_all_lines()[index]
        lastDebug = self.debugList[index]

        # check if line not empty
        if not is_command(line) and not is_comment(line):
            return

        # get begin and end line position
        beginLine = to_text_coord(0, index)
        endLine = to_text_coord(len(line), index)

        # reset all text tag to default for this line
        self.text.set_default(beginLine, endLine)

        # apply correct tag
        if is_comment(line):
            self.text.set_color_line('comment', index)
        elif lastDebug.is_error():
            beginError = max(lastDebug.get_position()[0] - 1, 0)
            while beginError > 0 and line[beginError] != " ":
                beginError -= 1
            if line[beginError] == " " and beginError > 0:
                beginError += 1

            beginErrorPos = to_text_coord(beginError, index)

            self.text.set_color('error', beginErrorPos, endLine)

    # endregion private methods

    def update_debug_display(self):
        text = ""
        for d in self.debugList:
            if d.is_error():
                text += str(d) + "\n"

        self.display_error.config(state='normal')
        self.display_error.replace(0.0, 'end', text[0:-1])

        lines = self.display_error.get(0.0, 'end').splitlines()
        for i in range(len(lines)):
            pos = 0
            while pos < len(lines[i]) and lines[i][pos] != ">":
                pos += 1
            self.display_error.tag_add("goto_error", to_text_coord(0, i), to_text_coord(pos, i))

        self.display_error.config(state='disabled')

    # region debug

    def debug_line(self, index):
        """ debug the line at index """
        lines = self.text.get_all_lines()

        if is_command(lines[index]):
            self.debugList[index] = self.debug.debug_command(lines[index])
        else:
            self.debugList[index] = Result()

        self.debugList[index].set_position(None, index)
        self.__set_color_line(index)

        self.update_debug_display()

    def debug_text(self):
        """ debug all the text """
        lines = self.text.get_all_text()

        for i in range(len(lines)):
            line = lines[i]
            if is_command(line):
                self.debugList[i] = self.debug.debug_command(line)
                self.debugList[i].set_position(None, i)
            else:
                self.debugList[i] = Result()

            self.__set_color_line(i)

        self.update_debug_display()

    # endregion debug

    # region text changes

    def clean(self):
        self.text.clean()

        self.display_error.replace(0.0, 'end', "")
        self.debugList = [Result()]

        self.isModify = False


# endregion text changes


if __name__ == "__main__":
    from tkinter import Tk

    root = Tk()
    root.title("text class")
    root.geometry("300x300")

    txt = Widget_mcfunction(root)
    txt.pack(expand=True, fill='both')

    root.mainloop()
