#-------------------------------------------------------------------------------
# Name:        editor
# Purpose:      manage all the text editor functionnality
#
# Author:      Didier Mathias
#
# Created:     24/12/2022
# Copyright:   (c) Elève 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from tkinter import Tk, Text, Scrollbar, Frame, Listbox, Variable, messagebox
from tkinter import VERTICAL, HORIZONTAL, INSERT, EXTENDED, DISABLED, NORMAL, SEL_FIRST, SEL_LAST
import tkinter.font as tkfont

import json

import sys
import os.path as path
sys.path.append(path.join(path.dirname(__file__), '..'))
import debugger as debug
import result as r

class editor(Frame):
    def __init__(self, *args, **kwargs):

        Frame.__init__(self, *args, **kwargs)

        # space repartion configuration
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

        self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=2)
        self.rowconfigure(3, weight=0)

        # text widget
        self.text = Text(self, wrap='none')

        # widget who display line
        self.lineDisplay = Text(self, width=3, state=NORMAL, foreground='gray40', background='gray60')
        self.lineDisplay.insert(0.0, '1')
        self.lineDisplay.tag_configure('right', justify='right')
        self.lineDisplay.tag_add("right", "0.0", "end")
        self.lineDisplay.config(state=DISABLED)

        # widget for diplay error
        self.errorDisplay = Text(self, height=10, wrap='none', state=DISABLED)

        # scrollbar
        self.yscroll = Scrollbar(self, orient=VERTICAL)
        yscrollerror = Scrollbar(self, orient=VERTICAL)
        xscroll1 = Scrollbar(self, orient=HORIZONTAL)
        xscroll2 = Scrollbar(self, orient=HORIZONTAL)

        # special config
        self.errorDisplay.config(yscrollcommand=yscrollerror.set, xscrollcommand=xscroll2.set)
        self.text.config(yscrollcommand=self.__updateScroll, xscrollcommand=xscroll1.set)
        self.lineDisplay.config(yscrollcommand=self.__updateScroll)
        self.yscroll.config(command=self.__scrollBoth)
        yscrollerror.config(command=self.errorDisplay.yview)
        xscroll1.config(command=self.text.xview)
        xscroll2.config(command=self.errorDisplay.xview)

        # placement on the grid
        self.lineDisplay.grid(row=0, column=0, sticky='ns')
        self.text.grid(row=0, column=1, sticky='nsew')
        self.errorDisplay.grid(row=2, column=0, columnspan=2, sticky='nsew')

        self.yscroll.grid(row=0, column=2, sticky='ns')
        yscrollerror.grid(row=2, column=2, sticky='ns')
        xscroll1.grid(row=1, column=0, columnspan=3, sticky='ew')
        xscroll2.grid(row=3, column=0, columnspan=3, sticky='ew')

        # detect all interaction with text
        self.text.bindtags(('.text','Text','post-bind', '.', 'all'))
        self.text.bind_class("post-bind", "<Key>", self.__modification)
        self.text.bind_class("post-bind", "<<Selection>>", self.__sel_manager)
        #self.errorDisplay.bind("<Double-Button-1>", self.goto_error)

        # get editor custom data
        file = open(path.join(path.dirname(__file__), 'style', 'data.json'))
        editorData = json.load(file)
        file.close()

        # set text font
        index = editorData["a_index"].index("font")
        data = editorData["a_data"][index]
        fontUse = (data["name"], data["size"], data["type"])
        self.text.config(font=fontUse)
        self.lineDisplay.config(font=fontUse)
        self.errorDisplay.config(font=fontUse)

        # other variable
        self.debug = debug.debug('1.19.2')
        self.debugList = [r.result()]

        self.isModify = False
        self.colorIndex = []
        self.__set_color_tags()

        self.modif_bind = None
        self.autoDebug = False

#region private methods
    def __scrollBoth(self, action, position, type=None):
        """
        Scroll both text and line display
        """
        self.text.yview_moveto(position)
        self.lineDisplay.yview_moveto(position)

    def __updateScroll(self, first, last, type=None):
        """
        update scrollbar, text and line display when scrollbar move
        """
        self.text.yview_moveto(first)
        self.lineDisplay.yview_moveto(first)
        self.yscroll.set(first, last)

    def __sel_manager(self, event):
        self.text.tag_remove("sel_intersection", 0.0, 'end')

        if len(self.text.tag_ranges("sel")) > 0:
            self.text.tag_add("sel_intersection", SEL_FIRST, SEL_LAST)

    def __set_color_tags(self):
        """
        create all tag for different color of text use
        see editor/text.json for tag specificity
        """
        file = open(path.join(path.dirname(__file__), 'style', 'text.json'))
        colorData = json.load(file)
        file.close()

        self.colorIndex = colorData["a_index"]
        data = colorData["a_data"]
        i = 0
        while i < len(self.colorIndex):
            section = self.colorIndex[i]
            sectionData = data[i]
            self.text.tag_config(section,
                background=sectionData["background"],
                foreground=sectionData["foreground"],
                overstrike=sectionData["overstrike"],
                underline=sectionData["underline"])

            i += 1

        self.errorDisplay.tag_config("goto_error",
            background="white",
            foreground="red",
            underline=1)
        self.errorDisplay.tag_bind("goto_error", "<Double-Button-1>", self.__goto_error)

    def __modification(self, *event):
        """
        set text to modify status
        debug current line
        update errorDisplay
        """
        if not self.isModify:
            self.isModify = True
            if self.modif_bind != None:
                self.modif_bind()

        positionCursor = self.get_list_coord(self.text.index(INSERT))

        lentext = self.get_length()
        lenline = self.get_list_coord(self.lineDisplay.index('end'))[1] -1
        if lenline != lentext:
            self.update_line_display()

            if lentext < lenline:
                self.debugList = self.debugList[0:lentext]
            else:
                self.debugList += [r.result() for i in range(lentext - lenline)]

        if self.autoDebug:
            self.debug_line(positionCursor[1])

    def __goto_error(self, *event):
        """
        move text to error currently selected
        """
        indexLine = self.get_list_coord(self.errorDisplay.index(INSERT))[1]

        indexError = 0
        indexText = 0
        while indexError != indexLine:
            if self.debugList[indexText].is_error():
                indexError += 1
            indexText += 1

        position = self.get_text_coord(*self.debugList[indexText].get_position())
        self.text.see(position)

    def __set_color_line(self, index):
        """
        set color for the current line

        # apply tag to text to set correct color, see "editor/text_color.json" to see different type config
        """

        # get line modify data
        line = self.get_lines()[index]
        lastDebug = self.debugList[index]

        # check if line not empty
        if not self.is_command(line) and not self.is_comment(line):
            return

        # get begin and end line position
        beginLine = self.get_text_coord(0, index)
        endLine = self.get_text_coord(len(line), index)

        # reset all text tag to default for this line
        self.set_default(beginLine, endLine)

        #apply correct tag
        if self.is_comment(line):
            self.text.tag_add("comment", beginLine, endLine)
        elif lastDebug.is_error():
            beginError = max(lastDebug.get_position()[0] -1, 0)
            while beginError > 0 and line[beginError] != " ":
                beginError -= 1
            if line[beginError] == " " and beginError > 0:
                beginError += 1

            beginErrorPos = self.get_text_coord(beginError, index)

            self.text.tag_add("error", beginErrorPos, endLine)

#endregion private methods

#region getters
    def get_widget(self):
        return self

    def get_text(self):
        return self.text.get(0.0, 'end')

    def get_lines(self):
        return self.text.get(0.0, 'end').splitlines()

    def get_length(self):
        return self.get_list_coord(self.text.index('end'))[1]

    def get_text_coord(self, x, y):
        return str(y+1) + '.' + str(x)

    def get_list_coord(self, index):
        ilist = index.split('.')

        line = int(ilist[0]) -1
        column = int(ilist[1])
        return [column, line]
#endregion getters

#region setters
    def set_bind(self, function):
        self.modif_bind = function

    def set_auto_check(self, check):
        self.autoDebug = check

    def set_default(self, posA, posB):
        """
        set the default color between position posA and posB
        """
        for i in self.colorIndex:
            self.text.tag_remove(i, posA, posB)

        self.text.tag_add("default", posA, posB)

#endregion setters

#region file management
    def new(self):
        self.text.replace(0.0, 'end', '')
        self.errorDisplay.replace(0.0, 'end', "")
        self.set_default('0.0', 'end')
        self.isModify = False

        self.debugList = [r.result() for i in range(self.get_length())]
        self.update_line_display()

    def open(self, filepath):
        if filepath is None:
            return

        with open(filepath, 'r') as file:
            self.text.replace(0.0, 'end', file.read())

        self.errorDisplay.replace(0.0, 'end', "")
        self.set_default('0.0', 'end')

        self.debugList = [r.result() for i in range(self.get_length())]
        self.update_line_display()

        self.isModify = False

    def save(self, filepath):
        with open(filepath, 'w') as file:
            file.writelines(self.get_text())
#endregion file management

    def reset_binding(self):
        self.text.bind_class("post-bind", "<Key>", self.__modification)
        self.text.bind_class("post-bind", "<<Selection>>", self.__sel_manager)

    def update_debug_display(self):
        text = ""
        for d in self.debugList:
            if d.is_error():
                text += str(d) + "\n"

        self.errorDisplay.config(state=NORMAL)
        self.errorDisplay.replace(0.0, 'end', text[0:-1])

        lines = self.errorDisplay.get(0.0, 'end').splitlines()
        for i in range(len(lines)):
            pos = 0
            while pos < len(lines[i]) and lines[i][pos] != ">":
                pos += 1
            self.errorDisplay.tag_add("goto_error", self.get_text_coord(0, i), self.get_text_coord(pos, i))

        self.errorDisplay.config(state=DISABLED)

    def update_line_display(self):
        lentext = self.get_length()
        lenline = self.get_list_coord(self.lineDisplay.index('end'))[1] -1

        if lenline != lentext:
            text = ""
            for i in range(lentext):
                text += str(i +1)
                if i != lentext -1:
                    text += "\n"

            self.lineDisplay.config(state=NORMAL)
            self.lineDisplay.replace(0.0, 'end', text)
            self.lineDisplay.tag_add("right", "0.0", "end")
            self.lineDisplay.config(state=DISABLED)

#region debug
    def is_command(self, line):
        """
        check if a line is a command
        """
        if len(line) == 0:
            return False

        if line[0] == "#":
            return False

        for char in line:
            if char not in [' ', '\n', '\r']:
                return True

        return False

    def is_comment(self, line):
        """
        check if line is a comment
        """
        if len(line) == 0:
            return False

        if line[0] == '#':
            return True

        return False

    def debug_line(self, index):
        """
        debug the current line
        """
        lines = self.get_lines()

        if self.is_command(lines[index]):
            self.debugList[index] = self.debug.debug_command(lines[index])
        else:
            self.debugList[index] = r.result()

        self.debugList[index].set_position(None, index)
        self.__set_color_line(index)

        self.update_debug_display()

    def debug_text(self):
        """
        debug all the text
        """
        lines = self.get_lines()

        for i in range(len(lines)):
            line = lines[i]
            if self.is_command(line):
                self.debugList[i] = self.debug.debug_command(line)
                self.debugList[i].set_position(None, i)
            else:
                self.debugList[i] = r.result()

            self.__set_color_line(i)

        self.update_debug_display()
#endregion debug

#region text changes
    def clean(self):
        self.text.replace(0.0, 'end', "")
        self.errorDisplay.replace(0.0, 'end', "")
        self.set_default('0.0', 'end')

        self.update_line_display()
        self.debugList = [r.result() for i in range(self.get_length())]

        self.isModify = False
#endregion text changes


if __name__ == "__main__":
    from tkinter import Tk
    root = Tk()
    root.title("text class")
    root.geometry("300x300")

    txt = editor(root)
    txt.set_auto_check(True)
    #txt.get_widget().grid(row=0, column=0, sticky='nw')
    txt.pack(expand=True, fill='both')

    root.mainloop()