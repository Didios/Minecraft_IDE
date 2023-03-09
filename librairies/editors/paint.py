# BASE PROGRAM = https://gist.github.com/nikhilkumarsingh/85501ee2c3d8c0cfa9d1a27be5781f06

from tkinter import Frame, Button, Canvas, Scale
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk, ImageDraw
import binascii


class paint(Frame):

    DEFAULT_PEN_SIZE = 1.0
    DEFAULT_COLOR = '#000000'
    DEFAULT_BG = 'grey'
    DEFAULT_MIN = 50

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        # space repartion configuration
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        #self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=1)
        #self.rowconfigure(2, weight=2)
        #self.rowconfigure(3, weight=0)

        self.pen_button = Button(self, text='pen', command=self.use_pen)
        self.pen_button.grid(row=0, column=0, sticky='nsew')

        self.eraser_button = Button(self, text='eraser', command=self.use_eraser)
        self.eraser_button.grid(row=0, column=1, sticky='nsew')

        self.color_button = Button(self, text='color', command=self.choose_color, bg=self.DEFAULT_COLOR)
        self.color_button.grid(row=0, column=2, sticky='nsew')

        self.choose_size_button = Scale(self, from_=1, to=30, resolution=3, orient='horizontal', command=self._set_size)
        self.choose_size_button.grid(row=0, column=3, sticky='nsew')

        self.c = Canvas(self, bg=self.DEFAULT_BG, width=600, height=600)
        self.bind('<Configure>', self._resize_canvas)
        self.c.grid(row=1, columnspan=4, sticky='nw')

        self.modif_bind = None
        self._setup()

#region private methods
    def _setup(self):
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button
        self.ishover = False

        self.sizedif = 0
        self.isModify = False

        self.realsize = (600, 600)
        self.size = (50, 50)
        self.scale = 600 // 50

        self.hover = self.c.create_rectangle(-self.scale*2, -self.scale*2, -self.scale, -self.scale, outline='black', width=1)

        #self._resize_canvas()
        self.use_pen()
        self.reset_binding()

    def _from_rgba(self, rgba):
        """
        translates an rgb tuple of int to a tkinter friendly color code
        """
        return "#%02x%02x%02x" % rgba[0:3]

    def _to_rgba(self, hexa):
        """
        translates a color code to an rgb tuple of int
        """
        return tuple(list(binascii.unhexlify(hexa[1::])) + [255])

    def _set_size(self, event):
        self.sizedif = max((int(event) -1) // 2 * self.scale, 0)
        self._reset_hover()

    def _get_size(self):
        return (self.size[0] * self.scale, self.size[1] * self.scale)

    def _reset_hover(self):
        self.c.delete(self.hover)

        color = 'white' if self.eraser_on else 'black'
        pos1 = -self.scale - self.sizedif * 2

        self.hover = self.c.create_rectangle(
            pos1, pos1,
            0, 0,
            outline=color, width=1)

    def _on_hover(self, event):
        pos = self.c.coords(self.hover)

        if pos == []:
            self._reset_hover()
            pos = self.c.coords(self.hover)

        coord = ((pos[0] + pos[2]) / 2, (pos[1] + pos[3]) / 2)

        togo = ((event.x // self.scale) * self.scale + self.scale * 0.5,
            (event.y // self.scale) * self.scale + self.scale * 0.5)

        self.c.move(self.hover, togo[0] - coord[0], togo[1] - coord[1])

    def _on_end_hover(self, event):
        self.isHover = False
        self._reset_hover()

    def _resize_canvas(self, event=None):
        if event is None:
            width = self.winfo_width() - (self.c.winfo_rootx() - self.winfo_rootx())
            height = self.winfo_height() - (self.c.winfo_rooty() - self.winfo_rooty())
        else:
            width = event.width - (self.c.winfo_rootx() - self.winfo_rootx())
            height = event.height - (self.c.winfo_rooty() - self.winfo_rooty())

        if (width == self.realsize[0] and height == self.realsize[1]) or width <= self.DEFAULT_MIN or height <= self.DEFAULT_MIN:
            return

        #if self.scale == 0:
        #    self._setup()

        self.realsize = (width, height)

        scale = self.scale
        self.scale = min(self.realsize[0] // self.size[0], self.realsize[1] // self.size[1])

        size = self._get_size()
        self.c.config(width=size[0], height=size[1])

        # rescale all the objects
        ratio = self.scale / scale
        if ratio == 0: ratio = 1
        self.c.scale('all', 0, 0, ratio, ratio)

        self._set_size(self.choose_size_button.get())
#endregion private methods

    def set_bind(self, function):
        self.modif_bind = function

    def reset_binding(self):
        self.c.bind('<Button-1>', self.paint)
        self.c.bind('<B1-Motion>', self.paint)

        self.c.bind('<Leave>', self._on_end_hover)
        self.c.bind("<Motion>", self._on_hover)

#region file management
    def open(self, filepath):
        if filepath is None:
            return

        self.isModify = False

        pilImage = Image.open(filepath)
        w, h = pilImage.size

        self.size = (w, h)

        self.scale = min(self.realsize[0] // w, self.realsize[1] // h)
        self._resize_canvas()

        self.c.delete('all')
        for i in range(w):
            for j in range(h):
                color = pilImage.getpixel((i, j))

                if color[3] != 0: # if not transparent pixel
                    realposx = i * self.scale
                    realposy = j * self.scale
                    self.c.create_rectangle(realposx, realposy, realposx + self.scale, realposy + self.scale, fill=self._from_rgba(color), width=0)

        self._set_size(self.choose_size_button.get())

    def save(self, filepath):
        if filepath is None:
            return

        self.isModify = False

        img = Image.new("RGBA", self.size, (0, 0, 0, 0))
        draw = img.load()

        w = self.size[0] * self.scale
        h = self.size[1] * self.scale

        posX = (w // self.scale) * self.scale
        posY = (h // self.scale) * self.scale

        i = 0
        while i < posX:
            j = 0
            while j < posY:
                items = self.c.find_enclosed(i, j, i + self.scale, j + self.scale)
                if len(items) > 0:
                    color = self.c.itemcget(items[0], 'fill')
                    draw[i//self.scale, j//self.scale] = self._to_rgba(color)

                j += self.scale
            i += self.scale

        img.save(filepath)

    def new(self):
        self.c.delete('all')
        self._setup()
#endregion file management

    def use_pen(self):
        self.activate_button(self.pen_button)
        self._reset_hover()

    def choose_color(self):
        self.use_pen()
        self.color = askcolor(color=self.color)[1]
        self.color_button.config(bg=self.color)
        self._reset_hover()

    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)
        self._reset_hover()

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief='raised')
        some_button.config(relief='sunken')
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event):
        if not self.isModify:
            self.isModify = True
            if self.modif_bind != None:
                self.modif_bind()

        posX = (event.x // self.scale) * self.scale
        posY = (event.y // self.scale) * self.scale

        pos1 = (posX - self.sizedif, posY - self.sizedif)
        pos2 = (posX + self.scale + self.sizedif, posY + self.scale + self.sizedif)

        for item in self.c.find_enclosed(pos1[0], pos1[1], pos2[0], pos2[1]):
            self.c.delete(item)

        if not self.eraser_on:
            i = pos1[0]
            while i < pos2[0]:
                j = pos1[1]
                while j < pos2[1]:
                    self.c.create_rectangle(i, j, i + self.scale, j + self.scale, fill=self.color, width=0)
                    j += self.scale
                i += self.scale

        self._on_hover(event)


if __name__ == '__main__':

    from tkinter import Tk
    from tkinter.filedialog import askopenfilename, asksaveasfilename

    root = Tk()
    root.title("text class")
    root.geometry("600x600")

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    fpaint = paint(root, bg='blue')
    fpaint.grid(row=0, column=0, columnspan=3, sticky='nsew')

    def file_open():
        fpaint.open(askopenfilename(title='Open File', filetypes=[("PNG", ".png")]))

    def file_save():
        fpaint.save(asksaveasfilename(defaultextension='.png', filetypes=[("PNG", '*.png')], title="Save"))

    Button(root, text='open', command=file_open).grid(row=1, column=0, sticky='nsew')
    Button(root, text='save', command=file_save).grid(row=1, column=1, sticky='nsew')
    Button(root, text='new', command=fpaint.new).grid(row=1, column=2, sticky='nsew')

    root.mainloop()
