# -------------------------------------------------------------------------------
# Name:        main
# Purpose:     datapack editor
#
# Author:      Didier Mathias
# Created:     24/12/2022
# -------------------------------------------------------------------------------

# tkinter
from tkinter import Tk, Menu, Toplevel, BooleanVar, Label, Entry, Checkbutton, Button, IntVar
from tkinter.messagebox import askyesnocancel, showerror
from tkinter.filedialog import asksaveasfilename, askopenfilename, askdirectory
from tkinter.colorchooser import askcolor

# tab manager
import librairies.editors.notebookclose as notebook
# editors
from librairies.widget_mcfunction import Widget_mcfunction as command
from librairies.widget_paint import Widget_paint as paint
from librairies.widget_audio_player import Widget_audioplayer as audioplayer
from librairies.widget_audio_player import Waveform
from librairies.widget_notepad import Widget_notepad as notepad
import librairies.editors.nbtviewer as renderer
import librairies.editors.treeview as explorer

# other
from os import path
from distutils.dir_util import copy_tree
import keyboard
import json
from enum import Enum
from multiprocessing import Process


class e_file(Enum):
    FUNCTION = 0  # widget_mcfunction.py      >> command
    TEXTURE = 1  # widget_paint.py           >> paint
    NBT = 2  # nbtviewer.py              >> renderer
    SOUND = 3  # widget_audio_player.py    >> audioplayer
    JSON = 4  #
    TXT = 5  # widget_notepad.py         >> notepad


class window:
    PROJECT_PATH = path.join(path.dirname(__file__), 'temp')
    PROJECT_TEMPLATE = path.join(path.dirname(__file__), 'template')
    PROJECT_DATA = path.join(path.dirname(__file__), 'data')

    def __init__(self) -> None:
        """ Initialize the main window of the IDE """
        self.parameters = {}
        self.files = []
        self.can_noone = False

        self.root = None
        self.treeview = None
        self.tabManager = None

        # create window
        self.setup_window()
        self.setup_grid()

        # other tkinter related variable
        self.auto = BooleanVar()
        self.auto.set(True)

        # setup other window things
        self.setup_widget()
        self.setup_menubar()
        self.setup_shortcut()

        command.set_data_path(command, self.PROJECT_DATA)
        paint.set_data_path(paint, self.PROJECT_DATA)
        audioplayer.set_data_path(audioplayer, self.PROJECT_DATA)
        notepad.set_data_path(notepad, self.PROJECT_DATA)
        renderer.DATA_PATH = self.PROJECT_DATA

        self.parameters_file = path.join(self.PROJECT_DATA, 'parameters.json')
        self.parameters = self.init_parameters()
        self.parameters_object = {}
        self.parameters_window = None

        # create new file
        self.new_file(e_file.TXT)

    # region setup

    def setup_widget(self) -> None:
        """ Setup basic widget """
        # tree viewer
        self.treeview = explorer.tree(self.root, title="Project Viewer",
                                      command_file=self.execute_file, path=self.PROJECT_PATH)

        # tabs widget
        self.tabManager = notebook.NotebookClose(self.root)
        self.tabManager.bind("<<NotebookTabChanged>>", self.change_tab)
        self.tabManager.set_bind_close(self.close_tab)

        self.treeview.grid(row=0, column=0, sticky='nsew')
        self.tabManager.grid(row=0, column=1, sticky='nsew')

    def setup_grid(self) -> None:
        """ Setup basic grid """
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

    def setup_window(self) -> None:
        """ setup basic empty window """
        # create window
        self.root = Tk()
        self.root.iconbitmap('assets/icon_v2.ico')

        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        self.setup_window_size()

    def setup_window_size(self) -> None:
        """ Set window basic geometry """
        window_width = 1000
        window_height = 500

        # get the screen dimension
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # set the position of the window to the center of the screen
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def setup_menubar(self) -> None:
        """ Create Menu bar """
        # create bar
        menubar = Menu(self.root, background='#ff8000', foreground='black',
                       activebackground='white', activeforeground='black')

        # create main menu
        project = Menu(menubar, tearoff=0)
        run = Menu(menubar, tearoff=0)
        file = Menu(menubar, tearoff=0)

        # create file sub menu
        new = Menu(file, tearoff=0)
        _open = Menu(file, tearoff=0)

        # add 'new' menu item
        new.add_command(label="Function", command=lambda: self.new_file(e_file.FUNCTION))
        new.add_command(label="Texture", command=lambda: self.new_file(e_file.TEXTURE))
        new.add_command(label="Text", command=lambda: self.new_file(e_file.TXT))

        # add '_open' menu item
        _open.add_command(label="Function", command=lambda: self.open_file(e_file.FUNCTION))
        _open.add_command(label="Texture", command=lambda: self.open_file(e_file.TEXTURE))
        _open.add_command(label="Text", command=lambda: self.open_file(e_file.TXT))
        _open.add_command(label="Sound", command=lambda: self.open_file(e_file.SOUND))
        _open.add_command(label="Nbt", command=lambda: self.open_file(e_file.NBT))

        # add 'file' menu item
        file.add_cascade(label="New", menu=new)
        file.add_cascade(label="Open", menu=_open)
        file.add_command(label="Save", command=self.save)
        file.add_command(label="Save as", command=self.saveas)

        # add 'project' menu item
        project.add_cascade(label="New", command=self.new_project)
        project.add_cascade(label="Open", command=self.open_project)

        # add 'run' menu item
        run.add_command(label="Debug", command=self.launch_debug)
        run.add_checkbutton(label="Auto Check", onvalue=1, offvalue=0, variable=self.auto, command=self.set_auto)

        # add menu bar item
        menubar.add_command(label="Parameters", command=self.create_parameters)
        menubar.add_cascade(label="Project", menu=project)
        menubar.add_cascade(label="File", menu=file)
        menubar.add_cascade(label="Debug", menu=run)

        # config window menu
        self.root.config(menu=menubar)

    def setup_shortcut(self) -> None:
        """ Setup shortcut """
        keyboard.add_hotkey("F5", self.launch_debug)
        # keyboard.add_hotkey("ctrl+s", self.save)
        # keyboard.add_hotkey("ctrl+alt+s", self.save)
        # keyboard.add_hotkey("ctrl+o", self.open_file)
        # keyboard.add_hotkey("ctrl+n", self.new_file)
        keyboard.add_hotkey("ctrl+w", self.close_tab)

    # endregion

    # region setters

    def set_auto(self) -> None:
        """ Set editors auto-debug functionality """
        command.AUTO_CHECK = self.auto.get()

    # endregion

    # region window management

    def close_window(self) -> None:
        """ Close window, ask to save if files not saved """
        try:
            tabsSize = len(self.files)
            canClose = True

            # close all tab
            while tabsSize > 1 and canClose:
                canClose = self.close_tab(tabsSize - 1)
                tabsSize = len(self.files)
            if self.get_tab(0).isModify:
                canClose = self.close_tab(0)

            # if you can close, destroy window, else open last tab
            if not canClose:
                self.open_tab(tabsSize - 1)
            else:
                keyboard.remove_all_hotkeys()
                self.root.destroy()
        except:
            self.root.destroy()

    def open_window(self):
        """ Launch window mainloop """
        self.root.mainloop()

    # endregion

    # region tab management

    def close_tab(self, index: int = -1) -> bool:
        """
        Close a tab of the window at index, if index is -1, close current open
        Args:
            index (): index of the tab, by default -1

        Returns:
            is the tab close
        """
        # check index
        if index == -1:
            index = self.get_current_index()

        # check if tab is modify, if yes, ask to save
        if self.get_tab(index).isModify:
            save = askyesnocancel(self.files[index],
                                  f'{self.files[index]}\nDo you want to save the current modification before ?')

            if save is None:
                return False
            elif save:
                self.save(index)

        # close the tab
        self.files.pop(index)
        self.tabManager.forget(self.tabManager.tabs()[index])

        # open a tab
        tabsSize = len(self.files)
        tab = self.get_current_index()

        if tab > index:
            tab -= 1
        elif tab == index and tabsSize > 0:
            if index == 0:
                tab += 1
            else:
                tab -= 1
            self.open_tab(tab)

        return True

    def open_tab(self, index: int) -> None:
        """
        Open tab at index
        Args:
            index (): index of the tab to open, is restrained to current tab number
        """
        # restrain index
        index = min(max(0, index), len(self.tabManager.tabs()) - 1)

        # select tab
        self.tabManager.select(self.tabManager.tabs()[index])
        self.change_tab()

    def get_tab(self, index: int = -1):
        """
        Get tab class instance at index
        Args:
            index (): index of the tab, by default -1

        Returns:
            class instance
        """
        if index == -1:
            index = self.get_current_index()
        return self.tabManager.nametowidget(self.tabManager.tabs()[index])

    def get_current_index(self) -> int:
        """
        Get index of the current tab open, if there is no tab, return -1
        Returns:
            index of the tab
        """
        if len(self.tabManager.tabs()) <= 0:
            return -1
        return self.tabManager.index(self.tabManager.select())

    def change_tab(self, event=None) -> None:
        """
        Make necessary change when move from one tab to another
        Args:
            event (): event for tkinter callback
        """
        if len(self.tabManager.tabs()) > 0:
            # reset binding
            self.get_tab().binding()
            # modify window title
            self.root.title(self.tabManager.tab('current')['text'])
        elif not self.can_noone:
            self.new_file(e_file.TXT)

    def create_instance(self, item: e_file, filepath=None):
        """
        Create a new instance with file item type
        Args:
            item (): type of the tab

        Returns:
            new instance
        """
        if item == e_file.FUNCTION:
            return command(self.tabManager, filepath=filepath)
        elif item == e_file.TEXTURE:
            return paint(self.tabManager, filepath=filepath)
        elif item == e_file.SOUND:
            return audioplayer(self.tabManager, filepath=filepath)
        # create txt tab by default
        return notepad(self.tabManager, filepath=filepath)

    # endregion

    def launch_debug(self) -> None:
        """ Debug current tab if is an editor """
        tab = self.get_tab()
        if type(tab) is command:
            tab.debug_text()

    # region file management

    def new_file(self, item: e_file) -> None:
        """
        Create a new file of the item
        Args:
            item (): file type to create
        """
        # create tab
        tab = self.create_instance(item)

        # setup tab
        tab.bind('<<Modification>>', self.modify_file)
        tab.pack(expand=True)

        # setup tab manager for add new file
        self.files.append("")
        self.tabManager.add(tab, text="Untitled")

        # open new tab
        self.open_tab(len(self.tabManager.tabs()) - 1)

    def open_file(self, item: e_file, filepath: str = None) -> None:
        """
        Open a new file, if there is no filepath, it is ask
        Args:
            item (): file type to open
            filepath (): path of the file, by default None
        """
        if item == e_file.FUNCTION:
            files = [("minecraft MCFUNCTION (*.mcfunction)", '.mcfunction')]
        elif item == e_file.TEXTURE:
            files = [("PNG (*.png)", '.png')]
        elif item == e_file.NBT:
            files = [("NBT (*.nbt)", '.nbt')]
        elif item == e_file.SOUND:
            files = [("SOUND (*.ogg)", '.ogg')]
        elif item == e_file.TXT:
            files = [("TEXT (*.txt)", '.txt')]
        else:
            return None

        # check if file
        if filepath is None:
            filepath = askopenfilename(title='Open File', filetypes=files)

        if filepath != '':
            if item == e_file.NBT:
                # launch viewer in another process to not block tkinter mainloop
                process = Process(target=renderer.display_nbt_file, args=[filepath])
                process.start()
                return None

            # get only filename without extension
            filename = path.splitext(path.basename(filepath))[0]

            # create new tab
            tab = self.create_instance(item, filepath)
            # setup tab
            tab.bind('<<Modification>>', self.modify_file)
            # tab.open(filepath)
            tab.pack(expand=True)

            # add tab to tab manager
            self.files.append(filepath)
            self.tabManager.add(tab, text=filename)
            # open tab
            self.open_tab(len(self.tabManager.tabs()) - 1)

    def execute_file(self, event) -> None:
        """
        Execute a file, open it for most
        Args:
            event (): tkinter event for callback
        """
        # get file extension
        extension = path.splitext(event)[1]

        # get file type
        filetype = None

        if extension in ['.mcfunction']:
            filetype = e_file.FUNCTION
        elif extension in ['.png', '.jpg']:
            filetype = e_file.TEXTURE
        elif extension in ['.nbt']:
            filetype = e_file.NBT
        elif extension in ['.ogg']:
            filetype = e_file.SOUND
        elif extension in ['.txt']:
            filetype = e_file.TXT

        # execute file
        if filetype is not None:
            self.open_file(filetype, event)
        else:
            showerror("Can't open file", "file extension is not recognisable")

    def save(self, index: int = -1) -> None:
        """
        Save a file by index, if no filepath exists, make 'save as'
        Args:
            index (): file tab index, -1 mean current open, by default -1
        """
        # check index
        if index == -1:
            index = self.get_current_index()
        # get current filepath
        filepath = self.files[index]

        # if no filepath, make 'save as', else save it
        if filepath != '':
            self.change_tab()
            self.get_tab(index).save_file(filepath)
        else:
            self.saveas(index)

    def saveas(self, index: int = -1) -> None:
        """
        Open a file dialog ta savefile at index tab
        Args:
            index (): file tab index, -1 mean current open, by default -1
        """
        # check index
        if index == -1:
            index = self.get_current_index()

        # get tab
        item = self.get_tab()

        # get data from tab
        if type(item) is command:
            extension = '.mcfunction'
            files = [("minecraft MCFUNCTION (*.mcfunction)", ".mcfunction")]
        elif type(item) is paint:
            extension = '.png'
            files = [("PNG (*.png)", ".png")]
        elif type(item) is notepad:
            extension = '.txt'
            files = [("TEXT (*.txt)", ".txt")]
        else:
            return None

        # open filedialog to get filepath
        filepath = asksaveasfilename(
            defaultextension=extension,
            filetypes=files,
            title="Save As")

        # save if file exists
        if filepath != '':
            # set new filepath
            self.files[index] = filepath

            # get only filename and set it
            filename = path.splitext(path.basename(filepath))[0]
            self.tabManager.tab(self.get_tab(index), text=filename)

            # save
            self.save(index)

    def modify_file(self, *args) -> None:
        """ Trigger if current open file is modify, change title """

        if not self.get_tab(self.get_current_index()).isModify:
            fileTitle = "* " + self.tabManager.tab('current')['text']

            self.tabManager.tab('current', text=fileTitle)
            self.root.title(fileTitle)

    # endregion

    # region project management

    def new_project(self) -> None:
        """ close previous project and create a new project """
        dirpath = askdirectory(title='Open Project')
        if dirpath == '':
            self.new_file(e_file.TXT)
            return

        self.can_noone = True
        self.close_project()
        self.can_noone = False

        # create template datapack
        copy_tree(self.PROJECT_TEMPLATE, dirpath)

        # update data
        self.PROJECT_PATH = dirpath

        # update treeview
        self.treeview.clean()
        self.treeview.first_open(dirpath)

        # open pack.mcmeta
        self.open_file(e_file.TXT, path.join(dirpath, 'pack.mcmeta'))

    def open_project(self) -> None:
        """ Save current project, then ask for a new one """
        filepath = askopenfilename(title='Open Project', filetypes=[("PROJECT FILE (pack.mcmeta)", 'pack.mcmeta')])
        if filepath == '':
            return

        self.can_noone = True
        self.close_project()
        self.can_noone = False

        dirpath = path.dirname(filepath)

        # update data
        self.PROJECT_PATH = dirpath

        # update treeview
        self.treeview.clean()
        self.treeview.first_open(dirpath)

        # open pack.mcmeta
        self.open_file(e_file.TXT, filepath)

    def close_project(self):
        index = len(self.tabManager.tabs()) - 1
        # close all tab
        while index >= 0:

            # check if tab is modify, if yes, ask to save
            if self.tabManager.nametowidget(self.tabManager.tabs()[index]).isModify:
                save = askyesnocancel(self.files[index],
                                      f'{self.files[index]}\nDo you want to save the current modification before ?')

                if save is not None:
                    self.get_tab(index).save_file()

            # close the tab
            self.files.pop(index)
            self.tabManager.forget(self.tabManager.tabs()[index])

            index -= 1

    # endregion project management

    # region parameters

    def create_parameters(self):
        self.parameters_window = Toplevel(self.root)
        self.parameters_window.title('Parameters')
        self.parameters_window.iconbitmap('assets/icon_v2.ico')
        self.parameters_window.grab_set()

        for i in range(5):
            self.parameters_window.rowconfigure(i, weight=1)

        self.parameters_window.columnconfigure(0, weight=1)
        self.parameters_window.columnconfigure(1, weight=2)
        self.parameters_window.columnconfigure(2, weight=0)

        Label(self.parameters_window, text='', width=2).grid(row=0, column=2, sticky='nsew')

        # audio player
        row = 0
        data = self.parameters['audioplayer']
        Label(self.parameters_window, text='AUDIO PLAYER').grid(row=row, column=0, columnspan=2, sticky='nsew')
        self.parameters_window.rowconfigure(row, weight=0)

        Label(self.parameters_window, text='Play On Open').grid(row=row + 1, column=0, sticky='nsew')
        self.parameters_object['ap_play'] = BooleanVar()
        self.parameters_object['ap_play'].set(data['play_on_open'])
        Checkbutton(self.parameters_window, anchor='center', variable=self.parameters_object['ap_play'], onvalue=True,
                    offvalue=False).grid(row=row + 1, column=1, sticky='nsew')

        Label(self.parameters_window, text='Line Width').grid(row=row + 2, column=0, sticky='nsew')
        self.parameters_object['ap_width'] = IntVar()
        self.parameters_object['ap_width'].set(data['line_width'])
        Entry(self.parameters_window, textvariable=self.parameters_object['ap_width']).grid(row=2, column=1,
                                                                                            sticky='nsew')

        Label(self.parameters_window, text='Bar Count').grid(row=row + 3, column=0, sticky='nsew')
        self.parameters_object['ap_count'] = IntVar()
        self.parameters_object['ap_count'].set(data['bar_count'])
        Entry(self.parameters_window, textvariable=self.parameters_object['ap_count']).grid(row=row + 3, column=1,
                                                                                            sticky='nsew')

        Label(self.parameters_window, text='Db Ceiling').grid(row=row + 4, column=0, sticky='nsew')
        self.parameters_object['ap_ceiling'] = IntVar()
        self.parameters_object['ap_ceiling'].set(data['db_ceiling'])
        Entry(self.parameters_window, textvariable=self.parameters_object['ap_ceiling']).grid(row=row + 4, column=1,
                                                                                              sticky='nsew')

        # function
        row += 5
        Label(self.parameters_window, text='', width=2, height=1).grid(row=row, column=2, sticky='nsew')
        self.parameters_window.rowconfigure(row, weight=0)
        row += 1
        data = self.parameters['function']
        Label(self.parameters_window, text='FUNCTION').grid(row=row, column=0, columnspan=2, sticky='nsew')
        self.parameters_window.rowconfigure(row, weight=0)

        Label(self.parameters_window, text='Auto Check').grid(row=row + 1, column=0, sticky='nsew')
        self.parameters_object['fn_check'] = BooleanVar()
        self.parameters_object['fn_check'].set(data['auto_check'])
        Checkbutton(self.parameters_window, anchor='center', variable=self.parameters_object['fn_check'],
                    onvalue=True, offvalue=False).grid(row=row + 1, column=1, sticky='nsew')

        # paint
        row += 2
        Label(self.parameters_window, text='', width=2, height=1).grid(row=row, column=2, sticky='nsew')
        self.parameters_window.rowconfigure(row, weight=0)
        row += 1
        data = self.parameters['paint']
        Label(self.parameters_window, text='PAINT').grid(row=row, column=0, columnspan=2, sticky='nsew')
        self.parameters_window.rowconfigure(row, weight=0)

        Label(self.parameters_window, text='Background').grid(row=row+1, column=0, sticky='nsew')
        self.parameters_object['pt_background'] = \
            Button(self.parameters_window, anchor='center', bg=data['default_bg'],
                   command=lambda: (self.parameters_object['pt_background'].config(
                       bg=askcolor(color=self.parameters_object['pt_background']['background'])[1])))
        self.parameters_object['pt_background'].grid(row=row+1, column=1, sticky='nsew')

        # end button
        row += 2
        Label(self.parameters_window, text='', width=2, height=1).grid(row=row, column=2, sticky='nsew')
        self.parameters_window.rowconfigure(row, weight=0)
        Button(self.parameters_window, text='Apply', command=self.save_parameters).grid(row=row+1, column=0,
                                                                                        columnspan=3, sticky='nsew')

        self.parameters_window.geometry(f"250x300+"
                                        f"{self.root.winfo_x() + self.root.winfo_width()//2 - 125}+"
                                        f"{self.root.winfo_y() + self.root.winfo_height()//2 - 150}")
        self.parameters_window.resizable(width=False, height=False)

    def save_parameters(self):
        try:
            self.parameters['audioplayer']['play_on_open'] = self.parameters_object['ap_play'].get()
            self.parameters['audioplayer']['line_width'] = self.parameters_object['ap_width'].get()
            self.parameters['audioplayer']['bar_count'] = self.parameters_object['ap_count'].get()
            self.parameters['audioplayer']['db_ceiling'] = self.parameters_object['ap_ceiling'].get()
            self.parameters['function']['auto_check'] = self.parameters_object['fn_check'].get()
            self.parameters['paint']['default_bg'] = self.parameters_object['pt_background']['background']

            self.parameters_window.destroy()
            self.parameters_window = None
        except:
            showerror('Invalid Entry', 'A parameter is incorrect, please check')

        with open(self.parameters_file, 'w') as file:
            json.dump(self.parameters, file)
        self.init_parameters()


    def init_parameters(self):
        with open(self.parameters_file, 'r') as file:
            param = json.load(file)

        audioplayer.PLAY_ON_OPEN = param['audioplayer']['play_on_open']
        audioplayer.LINE_WIDTH = param['audioplayer']['line_width']
        Waveform.bar_count = param['audioplayer']['bar_count']
        Waveform.db_ceiling = param['audioplayer']['db_ceiling']
        command.AUTO_CHECK = param['function']['auto_check']
        paint.DEFAULT_BG = param['paint']['default_bg']

        return param


# endregion parameters


if __name__ == '__main__':
    app = window()
    app.open_window()
