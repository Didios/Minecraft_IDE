#
# Made by : Bryan Oakley
# on the site : https://stackoverflow.com/questions/39458337/is-there-a-way-to-add-close-buttons-to-tabs-in-tkinter-ttk-notebook
#


try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk

class NotebookClose(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab"""

    __initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        kwargs["style"] = "NotebookClose"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

        self.bind_close = None

    def set_bind_close(self, function):
        self.bind_close = function

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index
            return "break"

    def on_close_release(self, event):
        """Called when the button is released"""
        if not self.instate(['pressed']):
            return

        element =  self.identify(event.x, event.y)
        if "close" not in element:
            # user moved the mouse off of the close button
            return

        index = self.index("@%d,%d" % (event.x, event.y))

        if self._active == index:
            if self.bind_close != None:
                if self.bind_close(index):
                    self.forget(index)
                    self.event_generate("<<NotebookTabClosed>>")
            else:
                self.forget(index)
                self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            tk.PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
            tk.PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        )

        style.element_create("close", "image", "img_close",
                            ("active", "pressed", "!disabled", "img_closepressed"),
                            ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("NotebookClose", [("NotebookClose.client", {"sticky": "nswe"})])
        style.layout("NotebookClose.Tab", [
            ("NotebookClose.tab", {
                "sticky": "nswe",
                "children": [
                    ("NotebookClose.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("NotebookClose.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("NotebookClose.label", {"side": "left", "sticky": ''}),
                                    ("NotebookClose.close", {"side": "right", "sticky": ''}),
                                ]
                        })
                    ]
                })
            ]
        })
    ])

if __name__ == "__main__":
    root = tk.Tk()

    notebook = NotebookClose(width=200, height=200)
    notebook.pack(side="top", fill="both", expand=True)

    colors = ("red", "orange", "green", "blue", "violet",
        "red", "orange", "green", "blue", "violet",
        "red", "orange", "green", "blue", "violet"
    )

    for color in colors:
        frame = tk.Frame(notebook, background=color)
        notebook.add(frame, text=color)

    root.mainloop()