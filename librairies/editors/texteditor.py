# -------------------------------------------------------------------------------
# Name:        text editor
# Purpose:     create a frame with an integrate text editor
#
# Author:      Didier Mathias
#
# Created:     02/05/2023
# -------------------------------------------------------------------------------

from tkinter import Text, Scrollbar, Frame, SEL_LAST, SEL_FIRST
from tkinter.filedialog import asksaveasfilename, askopenfilename
import json
import os.path as path


def to_text_coord(x, y):
    return str(y + 1) + '.' + str(x)


def to_list_coord(index):
    list_coord = index.split('.')
    return int(list_coord[1]), int(list_coord[0]) - 1


class Texteditor(Frame):
    """
    event:
        Text-Modification    >> all modification on text widget
    """

    STYLESHEET = path.join(path.dirname(__file__), '../data/style', 'text.json')
    DATASHEET = path.join(path.dirname(__file__), '../data/style', 'data.json')

    def __init__(self, *args, **kwargs):

        self.filepath = kwargs.pop('filepath', None)
        self.extension = kwargs.pop('extension', '.txt')
        self.filetypes = kwargs.pop('filetypes', [('TEXT (*.txt)', '.txt')])

        Frame.__init__(self, *args, **kwargs)

        # grid space configuration
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

        self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=0)

        # text widget
        self.text = Text(self, wrap='none')

        # widget who display line number
        self.lineDisplay = Text(self, width=3, state='normal', foreground='gray40', background='gray60')
        self.lineDisplay.insert(0.0, '1')
        self.lineDisplay.tag_configure('right', justify='right')
        self.lineDisplay.tag_add("right", "0.0", "end")
        self.lineDisplay.config(state='disabled')

        # scrollbar
        self.y_scroll = Scrollbar(self, orient='vertical', command=self.__scrollBoth)
        self.x_scroll = Scrollbar(self, orient='horizontal', command=self.text.xview)

        # scrollbar config
        self.text.config(yscrollcommand=self.__updateScroll, xscrollcommand=self.x_scroll.set)
        self.lineDisplay.config(yscrollcommand=self.__updateScroll)

        # placement on the grid
        self.lineDisplay.grid(row=0, column=0, sticky='ns')
        self.text.grid(row=0, column=1, sticky='nsew')

        self.y_scroll.grid(row=0, column=2, sticky='ns')
        self.x_scroll.grid(row=1, column=0, columnspan=3, sticky='ew')

        # detect text interaction
        self.text.bindtags(('.text', 'Text', 'post-bind', '.', 'all'))
        self.set_binding()

        # get editor custom data
        file = open(self.DATASHEET)
        editorData = json.load(file)
        file.close()

        # set text font
        index = editorData["a_index"].index("font")
        data = editorData["a_data"][index]
        fontUse = (data["name"], data["size"], data["type"])
        self.text.config(font=fontUse)
        self.lineDisplay.config(font=fontUse)

        # other variable
        self.__set_color_tags()
        self.isModify = False

        if self.filepath is not None:
            self.open()

    def set_data_path(self, dirpath):
        self.STYLESHEET = path.join(dirpath, 'style', 'text.json')
        self.DATASHEET = path.join(dirpath, 'style', 'data.json')

    # region private methods
    def __scrollBoth(self, position):
        """ Scroll both text and line display """
        self.text.yview_moveto(position)
        self.lineDisplay.yview_moveto(position)

    def __updateScroll(self, first, last):
        """ update scrollbar, text and line display when scrollbar move """
        self.text.yview_moveto(first)
        self.lineDisplay.yview_moveto(first)
        self.y_scroll.set(first, last)

    def __sel_manager(self, *args):
        """ set visual selection """
        self.text.tag_remove("sel_intersection", 0.0, 'end')

        if len(self.text.tag_ranges("sel")) > 0:
            self.text.tag_add("sel_intersection", SEL_FIRST, SEL_LAST)

    def __set_color_tags(self):
        """
        create all tag for different color of text use
        see editor/text.json for tag specificity
        """
        file = open(self.STYLESHEET)
        colorData = json.load(file)
        file.close()

        self.colorIndex = colorData["a_index"]
        data = colorData["a_data"]

        for i, section in enumerate(self.colorIndex):
            section_data = data[i]
            self.text.tag_config(section,
                                 background=section_data["background"],
                                 foreground=section_data["foreground"],
                                 overstrike=section_data["overstrike"],
                                 underline=section_data["underline"])

    def __modification(self, *args):
        """
        set text to modify status
        """
        self.isModify = True
        self.event_generate('<<Text-Modification>>')

        self.update_line_display()

    def set_color_line(self, tag, index):
        """
        set color for the current line

        # apply tag to text to set correct color, see "editor/text_color.json" to see different type config
        """

        # get line modify data
        line = self.get_all_lines()[index]

        # get begin and end line position
        beginLine = to_text_coord(0, index)
        endLine = to_text_coord(len(line), index)

        # reset all text tag to default for this line
        self.set_default(beginLine, endLine)

        # apply correct tag
        self.text.tag_add(tag, beginLine, endLine)

    def set_color(self, tag, posA, posB):
        """ set color tag from posA to posB """

        for i in self.colorIndex:
            self.text.tag_remove(i, posA, posB)

        self.text.tag_add(tag, posA, posB)

    def set_default(self, posA, posB):
        """
        set the default color between position posA and posB
        """
        for i in self.colorIndex:
            self.text.tag_remove(i, posA, posB)

        self.text.tag_add("default", posA, posB)

    # endregion private methods

    # region getters

    def get_all_text(self):
        return self.text.get(0.0, 'end')

    def get_all_lines(self):
        return self.text.get(0.0, 'end').splitlines()

    def get_length(self):
        return to_list_coord(self.text.index('end'))[1]

    def get_cursor_index(self):
        return self.text.index('insert')

    # endregion getters

    # region file management

    def new(self):
        if self.isModify:
            self.save()

        self.text.replace(0.0, 'end', '')
        self.set_default('0.0', 'end')

        self.update_line_display()
        self.__modification()

    def open(self, filepath=None):
        if self.isModify:
            self.save()

        if filepath is None:
            filepath = self.filepath

        if filepath is None:
            self.filepath = askopenfilename(title='Open File', filetypes=self.filetypes)
        else:
            self.filepath = filepath

        if self.filepath == '':
            self.filepath = None
            return

        with open(self.filepath, 'r') as file:
            self.text.replace(0.0, 'end', file.read())

        self.set_default('0.0', 'end')
        self.update_line_display()

        self.isModify = False

    def save(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath

        if self.filepath is None:
            self.save_as()
        else:
            with open(self.filepath, 'w') as file:
                file.writelines(self.get_all_text())

        self.isModify = False

    def save_as(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath
        else:
            # open filedialog to get filepath
            self.filepath = asksaveasfilename(
                defaultextension=self.extension,
                filetypes=self.filetypes,
                title="Save As")

        # save if file exists
        if self.filepath != '':
            self.save()

    # endregion file management

    def set_binding(self):
        self.text.bind_class("post-bind", "<Key>", self.__modification)
        self.text.bind_class("post-bind", "<<Selection>>", self.__sel_manager)
        self.text.bind_class("post-bind", "<Control-v>", self.__paste)
        self.text.bind_class("post-bind", "<Control-x>", self.__cut)

    def update_line_display(self):
        len_text = self.get_length()
        len_line = to_list_coord(self.lineDisplay.index('end'))[1] - 1

        if len_line != len_text:
            # determine text to add
            text = ""
            for i in range(len_text):
                text += str(i + 1)
                if i != len_text - 1:
                    text += '\n'

            # add text to display
            self.lineDisplay.config(state='normal')
            self.lineDisplay.replace(0.0, 'end', text)
            self.lineDisplay.tag_add("right", "0.0", "end")
            self.lineDisplay.config(state='disabled')

    def see(self, index):
        return self.text.see(index)

    # region text changes

    def clean(self):
        self.text.replace(0.0, 'end', "")
        self.set_default('0.0', 'end')

        self.update_line_display()
        self.__modification()

    def __paste(self, *args):
        self.__modification()

    def __cut(self, *args):
        if self.text.tag_ranges('sel'):
            self.text.replace(SEL_FIRST, SEL_LAST, '')

        self.__modification()

    # endregion text changes


if __name__ == "__main__":
    from tkinter import Tk, Menu

    root = Tk()
    root.title("text class")
    root.geometry("300x300")

    txt = Texteditor(root)
    txt.new()
    txt.pack(expand=True, fill='both')

    menubar = Menu(root)
    menubar.add_command(label="New", command=txt.new)
    menubar.add_command(label="Open", command=txt.open)
    menubar.add_command(label="Save", command=txt.save)
    menubar.add_command(label="Save as", command=txt.save_as)

    root.config(menu=menubar)
    root.mainloop()
