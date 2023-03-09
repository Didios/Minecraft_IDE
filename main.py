#-------------------------------------------------------------------------------
# Name:        main
# Purpose:     datapack editor
#
# Author:      Didier Mathias
#
# Created:     24/12/2022
# Copyright:   (c) Elève 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# tkinter
from tkinter import Tk, Menu, PhotoImage, BooleanVar
from tkinter.messagebox import askyesnocancel, showerror
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.ttk import Notebook

from os import path
import keyboard

# personnal
import librairies.editors.editor as command
import librairies.editors.paint as texture
import librairies.editors.notebookclose as notebook
import librairies.editors.treeview as fileview

class window:

    BASE_PATH = path.join(path.dirname(__file__), 'temp')

    def __init__(self):
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # grid configure expansion
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        # tree viewer
        self.treeview = fileview.tree(self.root, title="Project Viewer", command_file=self.select_file, path=self.BASE_PATH)
        self.treeview.grid(row=0, column=0, sticky='nsew')

        # tabs widget
        self.tabManager = notebook.NotebookClose(self.root)
        self.tabManager.bind("<<NotebookTabChanged>>", self.change_tab)
        self.tabManager.set_bind_close(self.closeTab)
        self.tabManager.grid(row=0, column=1, sticky='nsew')#expand=True, fill='both')

        self.files = []

        self.noClose = False
        self.auto = BooleanVar()
        self.auto.set(False)

        # advanced settings
        self.set_window()
        self.set_menu()
        self.set_shortcut()
        self.new_file('function')

    def set_window(self):
        self.root.iconbitmap('./assets/icon_v2.ico')

        window_width = 1000
        window_height = 500

        # get the screen dimension
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # find the center point
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        # set the position of the window to the center of the screen
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def set_menu(self):
        menubar = Menu(self.root, background='#ff8000', foreground='black', activebackground='white', activeforeground='black')
        run = Menu(menubar, tearoff=0)
        file = Menu(menubar, tearoff=0)#, background='#ffcc99', foreground='black')
        new = Menu(file, tearoff=0)
        _open = Menu(file, tearoff=0)

        new.add_command(label="Function", command=lambda: self.new_file('function'))
        new.add_command(label="Texture", command=lambda: self.new_file('texture'))

        _open.add_command(label="Function", command=lambda: self.open_file('function'))
        _open.add_command(label="Texture", command=lambda: self.open_file('texture'))

        file.add_cascade(label="New", menu=new)
        file.add_cascade(label="Open", menu=_open)
        file.add_command(label="Save", command=self.save)
        file.add_command(label="Save as", command=self.saveas)

        run.add_command(label="Debug", command=self.debug_current)
        run.add_checkbutton(label="Auto Check", onvalue=1, offvalue=0, variable=self.auto, command=self.set_auto)

        menubar.add_cascade(label="File", menu=file)
        menubar.add_cascade(label="Debug", menu=run)

        self.root.config(menu=menubar)

    def set_auto(self):
        for tab in self.tabManager.tabs():
            item = self.tabManager.nametowidget(tab)
            if type(item) is command.editor:
                item.set_auto_check(self.auto.get())

    def set_shortcut(self):
        keyboard.add_hotkey("F5", self.launch_debug)
        #keyboard.add_hotkey("ctrl+s", self.save)
        #keyboard.add_hotkey("ctrl+alt+s", self.save)
        #keyboard.add_hotkey("ctrl+o", self.open_file)
        #keyboard.add_hotkey("ctrl+n", self.new_file)
        keyboard.add_hotkey("ctrl+w", self.closeTab)

        #self.root.bind("<F5>", self.launch_debug)
        #self.root.bind("<Control-KeyPress-S>", self.save)

    def close(self):
        tabsSize = len(self.files)

        self.noClose = False

        while tabsSize > 1 and not self.noClose:
            self.closeTab(tabsSize -1)
            if self.noClose:
                self.select_tab(tabsSize -1)
                return
            tabsSize = len(self.files)

        if self.get_tab(0).isModify:
            self.closeTab(0)

        if self.noClose:
            self.noClose = False
        else:
            keyboard.remove_all_hotkeys()
            self.root.destroy()

    def closeTab(self, index=-1):
        if index == -1:
            index = self.get_index()

        if self.get_tab(index).isModify:
            save = None
            save = askyesnocancel(self.files[index], "%s \nDo you want to save the current modification before ?" % (self.files[index]))

            if save == None:
                self.noClose = True
                return False
            elif save:
                self.save(index)

        self.files.pop(index)
        self.tabManager.forget(self.tabManager.tabs()[index])

        tabsSize = len(self.files)
        tab = self.get_index()

        if tab > index:
            tab -= 1
        elif tab == index and tabsSize > 0:
            if index == 0:
                tab += 1
            else:
                tab -= 1
            self.select_tab(tab)
        elif tabsSize == 0:
            self.new_file('function')

        return False

    def get_tab(self, index=-1):
        if index == -1:
            index = self.get_index()
        return self.tabManager.nametowidget(self.tabManager.tabs()[index])

    def get_index(self):
        if len(self.tabManager.tabs()) <= 0:
            return -1
        return self.tabManager.index(self.tabManager.select())

    def select_tab(self, index):
        if index < 0:
            index = 0
        elif index >= len(self.tabManager.tabs()):
            index = len(self.tabManager.tabs()) -1

        self.tabManager.select(self.tabManager.tabs()[index])
        self.change_tab()

    def debug_current(self):
        tab = self.get_tab()
        if type(tab) is command.editor:
            tab.debug_text()

    def launch_debug(self):
        #self.save()
        tab = self.get_tab()
        if type(tab) is command.editor:
            tab.debug_text()

#region file management
    # item can be:
    #   function >> command.editor
    #   texture >> texture.paint

    def new_file(self, item):
        if item == "function":
            tab = command.editor(self.tabManager)
        elif item == "texture":
            tab = texture.paint(self.tabManager)

        tab.set_bind(self.modify)
        tab.pack(expand=True)

        self.files.append("")
        self.tabManager.add(tab, text="Untitled")

        self.select_tab(len(self.tabManager.tabs()) -1)

    def open_file(self, item, filepath=""):
        if item == "function":
            files = [("minecraft MCFUNCTION", ".mcfunction")]
        elif item == "texture":
            files = [("PNG", ".png")]

        if filepath == "":
            filepath = askopenfilename(title='Open File', filetypes=files)

        if filepath != '':
            if item == "function":
                tab = command.editor(self.tabManager)
            elif item == "texture":
                tab = texture.paint(self.tabManager)

            # get only filename
            filename = path.splitext(path.basename(filepath))[0]

            tab.set_bind(self.modify)
            tab.pack(expand=True)

            tab.open(filepath)

            self.files.append(filepath)
            self.tabManager.add(tab, text=filename)

            self.select_tab(len(self.tabManager.tabs()) -1)

    def select_file(self, event):
        extension = path.splitext(event)[1]

        if extension in ['.mcfunction']:
            self.open_file('function', event)
        elif extension in ['.png', '.jpg']:
            self.open_file('texture', event)
        else:
            showerror("Can't open file", "file extension is not recognisable")


    def save(self, index=-1):
        if index == -1:
            index = self.get_index()
        filepath = self.files[index]

        if filepath != '':
            self.change_tab()
            self.get_tab(index).save(filepath)
        else:
            self.saveas(index)

    def saveas(self, index=-1):
        if index == -1:
            index = self.get_index()

        item = self.get_tab()
        if type(item) is command.editor:
            extension = '.mcfunction'
            files = [("minecraft MCFUNCTION", ".mcfunction")]
        elif type(item) is texture.paint:
            extension = '.png'
            files = [("PNG", ".png")]

        filepath = asksaveasfilename(
            defaultextension=extension,
            filetypes=files,
            title="Save As")

        if filepath != '':
            self.files[index] = filepath

            # get only filename
            filename = path.splitext(path.basename(filepath))[0]
            self.tabManager.tab(self.get_tab(index), text=filename)

            self.save(index)
        else:
            self.noClose = True
#endregion file management

    def launch(self):
        self.root.mainloop()

    def modify(self):
        newTitle = "* " + self.tabManager.tab('current')['text']

        self.tabManager.tab('current', text=newTitle)
        self.root.title(newTitle)

    def change_tab(self, event=None):
        if len(self.tabManager.tabs()) > 0:
            self.get_tab().reset_binding()
            newTitle = self.tabManager.tab('current')['text']
            self.root.title(newTitle)
        else:
            self.new_file()

if __name__ == '__main__':
    editor = window()
    editor.launch()
