import os
from tkinter import Frame, Scrollbar
from tkinter.ttk import Treeview#, Scrollbar


class tree(Frame):
    def __init__(self, *args, **kwargs):
        path = os.getcwd()
        if 'path' in kwargs.keys():
            path = kwargs['path']
            kwargs.pop('path')

        title = "Tree"
        if 'title' in kwargs.keys():
            title = kwargs['title']
            kwargs.pop('title')

        self.bind_file = None
        self.bind_dir = None
        if 'command_file' in kwargs.keys():
            self.bind_file = kwargs['command_file']
            kwargs.pop('command_file')
        if 'command_dir' in kwargs.keys():
            self.bind_dir = kwargs['command_dir']
            kwargs.pop('command_dir')

        Frame.__init__(self, *args, **kwargs)

        # space repartion configuration
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)


        self.nodes = dict()
        self.tree = Treeview(self)

        ysb = Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = Scrollbar(self, orient='horizontal', command=self.tree.xview)

        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0', text=title, anchor='w')

        self.tree.grid(row=0, column=0, sticky='nsew')
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')

        abspath = os.path.abspath(path)
        text = abspath
        if len(abspath) > 30:
            text = '... ' + text[-26::]

        self.insert_node('', text, abspath)
        self.tree.bind('<<TreeviewOpen>>', self.open_node)

    def insert_node(self, parent, text, abspath):
        node = self.tree.insert(parent, 'end', text=text, open=False)
        if os.path.isdir(abspath):
            self.nodes[node] = abspath
            self.tree.insert(node, 'end')
        else:
            self.nodes[node] = '#' + abspath

    def open_node(self, event):
        node = self.tree.focus()
        abspath = self.nodes.get(node, None)

        if abspath:
            if abspath[0] == '#':
                if self.bind_file: self.bind_file(abspath[1::])
            else:
                self.tree.delete(self.tree.get_children(node))
                for p in os.listdir(abspath):
                    self.insert_node(node, p, os.path.join(abspath, p))

                if self.bind_dir: self.bind_dir(abspath)



if __name__ == '__main__':
    def print_file(file):
        print("FILE", file)
    def print_dir(dir):
        print("DIR", dir)

    from tkinter import Tk
    root = Tk()

    treeview = tree(root, title="Test Tree", command_file=print_file, command_dir=print_dir) #path=r'C:\Users\Elève\Desktop\Minecraft IDE')
    treeview.pack(expand=True, fill='both')

    root.mainloop()