#region check json
import os.path


def get_json_symbols(content):
    """
    transform a json file into a list with only all special caracteres present
    """
    special = ['"', "'", '{', '}', '[', ']', ':', ',']
    ignore = ['\n', '\t', '\r', ' ']

    symbols = []

    # get all special symbols
    for c in content:
        if c in special:
            symbols += [c]
        elif c not in ignore and symbols[-1] != '@':
            symbols += ['@']

    # remove ones in string
    i = 0
    while i < len(symbols):
        if symbols[i] in ["'", '"']:
            s = symbols[i]
            i += 1
            while symbols[i] != s:
                symbols.pop(i)
                if i == len(symbols):
                    break;
            symbols.insert(i, '@')
            i += 1
        i += 1

    return symbols


def check_json(content, strict=False):
    """
    check if a json is correct
    /!\ check only the structure /!\

    strict check if all element in lists seems of the same type
    """
    symbols = get_json_symbols(content)

    if len(symbols) == 0:
        return False

    if strict or symbols[0] == "{":
        return check_struct(symbols, strict)
    else:
        return check_list(symbols, strict)


def check_struct(symbols, strict=False):
    """
    check if a struct is correct
    /!\ check only the structure /!\

    strict check if all element in lists seems of the same type
    """
    # print("STRUCT: " + str(symbols))
    keys = ['"', "'"]
    values = ['{', '[']

    value_begin = ['"', "'", '{', '[']
    value_end = ['"', "'", '}', ']']

    if symbols[0] != "{" or symbols[-1] != "}":
        return False

    symbols.pop(-1)
    symbols.pop(0)

    i = 0
    while i < len(symbols):
        if i + 3 >= len(symbols):
            return False
        if symbols[i] not in keys or symbols[i + 1] != '@' or symbols[i + 2] != symbols[i] or symbols[i + 3] != ':':
            return False
        i += 4

        if symbols[i] not in value_begin:
            return False

        _type = symbols[i]
        if _type in keys:
            if i + 2 >= len(symbols):
                return False
            if symbols[i + 1] != '@' or symbols[i + 2] != symbols[i]:
                return False
            i += 3
        elif _type in values:
            end = get_index_end(symbols, i)
            if end == -1:
                return False
            end += 1
            if end > len(symbols):
                return False

            if _type == '{':
                check = check_struct(symbols[i:end], strict)
            else:
                check = check_list(symbols[i:end], strict)

            if not check:
                return False
            i = end

        if i >= len(symbols):
            return True
        if symbols[i] != ",":
            return False
        i += 1
        if i >= len(symbols):
            return False

    return None


def get_index_end(symbols, index):
    """
    give the index for the closing element of the symbol at current index
    return -1 if not found

    /!\ work only with {} and [] /!\
    """
    s_begin = symbols[index]
    if symbols[index] == '{':
        s_end = '}'
    elif symbols[index] == '[':
        s_end = ']'

    count = 0
    end = index + 1

    while symbols[end] != s_end or count > -1:
        if symbols[end] == s_begin:
            count += 1
        elif symbols[end] == s_end:
            count -= 1

        if count < 0 and symbols[end] == s_end:
            break;

        end += 1
        if end >= len(symbols):
            return -1

    return end


def check_list(symbols, strict=False):
    """
    check if a list is correct
    /!\ check only the structure /!\

    strict check if all element in list seems of the same type
    """
    # print("LIST: " + str(symbols))
    keys = ['"', "'"]
    values = ['{', '[']

    if symbols[0] != "[" or symbols[-1] != "]":
        return False

    symbols.pop(-1)
    symbols.pop(0)

    tobe = None

    i = 0
    while i < len(symbols):
        _type = symbols[i]

        if strict and tobe is not None and _type != tobe:
            return False

        if _type in keys:
            if i + 2 >= len(symbols):
                return False
            if symbols[i + 1] != '@' or symbols[i + 2] != symbols[i]:
                return False
            i += 3
        elif _type in values:
            end = get_index_end(symbols, i)
            if end == -1:
                return False
            end += 1
            if end > len(symbols):
                return False

            if _type == '{':
                check = check_struct(symbols[i:end], strict)
            else:
                check = check_list(symbols[i:end], strict)

            if not check:
                return False
            i = end
        elif _type != '@':
            return False
        else:
            i += 1

        if tobe is None:
            tobe = _type

        if i >= len(symbols):
            return True
        if symbols[i] != ",":
            return False
        i += 1
        if i >= len(symbols):
            return False

    return True

def compact_json(content):
    """
    compact a json into a one line string
    """
    con = ""
    previous = ""
    for c in content:
        if c not in ['\n', '\t', '\r'] and (previous != ':' or (previous == ':' and c != ' ')):
            con += c

        previous = c

    return con

if False:
    with open("../librairies/data/1.19.2/commands.json") as file:
        lines = file.readlines()

    content = ""
    for s in lines:
        content += s

    content = compact_json(content)

    print("JSON: ", content)

    print("NOT STRICT: ", check_json(content, False))
    print("STRICT: ", check_json(content, True), "\n\n")

#endregion check json

#region draw textured model

import os.path as pt
import json

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def get_relative_to(self, origin):
        relative = Vector3(self.x + origin.x, self.y + origin.y, self.z + origin.z)
        return relative

    def to_tuple(self):
        return (self.x, self.y, self.z)

class RGB:
    def __init__(self, r=1, g=1, b=1, type=1):
        """
        type: from 0-1 or 0-255
        """
        self.red = r
        self.green = g
        self.blue = b
        self.type = type

    def get_color(self, type=1):
        if self.type == 1 and type == 255:
            return (self.red * 255, self.green * 255, self.blue * 255)
        elif self.type == 255 and type == 1:
            return (self.red / 255, self.green / 255, self.blue / 255)
        return tuple(self.red * 255, self.green * 255, self.blue * 255)

    def to_tuple(self):
        return (self.red, self.green, self.blue)

class Texture:
    def __init__(self, filepath):
        self.filepath = filepath

        image = pygame.image.load(filepath)
        datas = pygame.image.tostring(image, 'RGBA')

        # create new texture id
        self.id = glGenTextures(1)

        # setup texture
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.get_width(), image.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE,
                     datas)

        # texture scale method
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        # save texture
        glGenerateMipmap(GL_TEXTURE_2D)

class Model:
    def __init__(self, coordinate, verticies=[], faces=[], normals=[], wire=RGB(), textures=None, uvmapping=None):
        """
        coordinate: Vector3, origin position of the model
        verticies: Vector3[], position of each vertice of the model, relative to the origin, by default empty
        faces: Int[][4], list of vertice index to compose each face, by default empty
        normals: Int[][3], list of normals for each face, must be 1 by face, by default empty
        wire: RGB, color of wire draw, by default white
        textures: Texture[], texture used by the model, must be 1 by face, draw wire if None, by default None
        uvmapping: Int[][4][2], uvmapping of the texture used by the model, must be 1 by texture, by default None
        """

        self.coordinate = coordinate
        self.verticies = tuple(v.get_relative_to(coordinate).to_tuple() for v in verticies)
        #self.verticies = tuple(tuple([coordinate[i] + v[i] for i in v]) for v in verticies)

        self.edges = []
        for f in faces:
            self.edges.append((f[0], f[1]))
            self.edges.append((f[1], f[2]))
            self.edges.append((f[2], f[3]))
            self.edges.append((f[3], f[0]))

        self.faces = faces
        self.normals = normals

        self.wire = wire.to_tuple()
        self.textures = textures
        self.uvmapping = uvmapping

    def draw_wire(self):
        """
        draw the model with only wire
        """
        glColor3fv(self.wire)
        glBegin(GL_LINES)

        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])

        glEnd()

    def draw(self):
        """
        draw the model with all texture on faces, if no texture, draw edges only
        """
        if self.textures is None:
            self.draw_wire()
            return None

        # draw faces with texture
        glColor4f(1, 1, 1, 1)  # set white to not affect texture display

        for i_surface, surface in enumerate(self.faces):
            glBindTexture(GL_TEXTURE_2D, self.textures[i_surface].id)
            glBegin(GL_QUADS)

            glNormal3fv(self.normals[i_surface])
            for i_vertex, vertex in enumerate(surface):
                glTexCoord2fv(self.uvmapping[i_surface][i_vertex])
                glVertex3fv(self.verticies[vertex])

            glEnd()
            glBindTexture(GL_TEXTURE_2D, 0)

def draw_models(models, display, size, draw_wire=False):
    # create pygame window
    clock = pygame.time.Clock()

    x = (max(size[0], size[2]) / 2) - 0.5
    y = (size[1] / 2) - 0.5
    z = size[1] * 2

    print(size, x, y, z)

    # setup opengl
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glTranslatef(-x, -y, -z)
    glRotatef(-90, 1, 0, 0)

    # set light
    glLight(GL_LIGHT0, GL_POSITION,  (size[0]*2, size[1]*2, size[2]*2, 1)) # point light from the left, top, front
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

    # enable depth
    glEnable(GL_DEPTH_TEST)

    # enable texture and alpha transparency
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE)

    # set background color
    glClearColor(0.5, 0.5, 0.5, 1)

    pygame.event.clear()

    drag = False
    con = True
    while con:
        # quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                con = False
                #quit()
            elif event.type == pygame.MOUSEWHEEL:
                glTranslatef(x, y, z)
                z += event.precise_y
                glTranslatef(-x, -y, -z)
            elif event.type == pygame.KEYDOWN:
                glTranslatef(x, y, z)
                if event.unicode == 'z':
                    y += 1
                elif event.unicode == 's':
                    y -= 1
                elif event.unicode == 'd':
                    x += 1
                elif event.unicode == 'q':
                    x -= 1
                glTranslatef(-x, -y, -z)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    drag = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drag = False
            elif event.type == pygame.MOUSEMOTION and drag:
                right = event.rel[0] * 10
                up = event.rel[1]
                glRotatef(1, up, 0, right*2)
                #glRotatef(1, up, 0, 0)
            # wheel for zoom
            # move around with drag

        if not con:
            break;

        # clear opengl buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # set light
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # rotate things
        glRotatef(1, 0, 0, 1)

        # draw objects
        for m in models:
            if draw_wire:
                m.draw_wire()
            m.draw()

        # remove light
        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)

        # update screen
        pygame.display.flip()
        clock.tick(60)

def display_block(blockname):
    path_model = '../librairies/data/3D/models'
    path_block = '../librairies/data/3D/blocks'
    path_textures = '../librairies/data/3D/textures'

    with open(pt.join(path_block, blockname + '.json')) as file:
        data = json.load(file)

    with open(pt.join(path_model, data['model'])) as file:
        model_data = json.load(file)

    pygame.init()
    display = (400, 300)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    palette = []
    for tex in data['palette']:
        palette.append(Texture(pt.join(path_textures, tex)))

    textures = []
    for tex in model_data['textures']:
        textures.append(palette[tex])

    verticies = []
    for v in model_data['verticies']:
        verticies.append(Vector3(v[0], v[1], v[2]))

    model_0 = Model(Vector3(0, 0, 0), verticies=verticies, faces=model_data['faces'], normals=model_data['normals'], textures=textures, uvmapping=model_data['uvmapping'])

    draw_models([model_0], display, (1, 1, 1))

if False:
    blocks = [
        "acacia_planks",
        "crafting_table",
        "redstone_torch"
    ]

    for i in blocks:
        display_block(i)

#endregion

#region read .nbt file

import python_nbt.nbt as nbt

def get_nbt_data(file):
    data_brut = nbt.read_from_nbt_file(file)
    data = data_brut.json_obj(full_json=False)

    size = tuple(data['size'])
    blocks = data['blocks']
    palette = data['palette']

    print("SIZE: ", size)
    print("BLOCKS: ", blocks)
    print("PALETTE: ", palette)

    return size, blocks, palette

if False:
    get_nbt_data("../temp/debug.nbt")

#endregion

#region see .nbt file with voxel

from random import choice
import voxelmap as vxm
import numpy as np

def get_air_state(palette):
    air_state = -1
    for i in range(len(palette)):
        if palette[i]['Name'] == 'minecraft:air':
            air_state = i
            break;

    return air_state

def get_random_color():
    c = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    s = '#'
    for i in range(6):
        s += choice(c)
    return s

def get_palette_color(palette, reference=None):
    """
    reference = { "block": 'color' }
    """
    if reference is None:
        names = []
        colors = []
        for i in palette:
            n = i['Name']
            if n in names:
                colors.append(colors[names.index(n)])
            else:
                names.append(n)
                colors.append(get_random_color())

        return colors  # [get_random_color() for i in palette]

    return [reference[i['Name']] for i in palette]

def get_names(palette):
    return [i['Name'] for i in palette]

def display_nbt(file):
    data_brut = nbt.read_from_nbt_file(file)
    data = data_brut.json_obj(full_json=False)

    size = data['size']
    blocks = data['blocks']
    palette = data['palette']

    scale = 1
    size = tuple(j * scale for j in size)

    array = np.ndarray(size, int)
    air_state = get_air_state(palette)
    colors = get_palette_color(palette)

    # 0 is the index for transparent block (air)
    for i in blocks:
        pos = [j * scale for j in i['pos']]
        state = i['state']

        if state != air_state:
            array[pos[0]][pos[1]][pos[2]] = state +1
        else:
            array[pos[0]][pos[1]][pos[2]] = 0

    #incorporate array to Model structure
    model = vxm.Model(array)

    #add voxel colors by index (needed for `custom` coloring)
    for i in range(len(colors)):
       model.hashblocks_add(i+1, colors[i]) # next parameter is alpha

    # display the voxel map
    model.draw('custom', background_color='#ffffff')

if False:
    n = [
        #"../temp/side.nbt",
        "../temp/mouv.nbt",
        "../temp/debug.nbt",
        #"../temp/imprimante v1.nbt",
        #"../temp/printer_v4.nbt"
    ]

    for i in n:
        display_nbt(i)

#endregion

#region see .nbt file textured

def clean_base(value):
    index = value.find('minecraft:')

    if index == 0:
        return value[10::]

    if value[0] == '#' and index == 1:
        return '#' + value[11::]

    return value

def render_nbt(filepath):
    path_model = '../librairies/data/3D/models'
    path_block = '../librairies/data/3D/blocks'
    path_textures = '../librairies/data/3D/textures'

    size, blocks, palette = get_nbt_data(filepath)

    #size = (size[0], size[2], size[1])

    pygame.init()
    display = (400, 300)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    data_models = []
    inexistent = []
    for i in palette:
        blockname = clean_base(i['Name'])

        # check if block data exists, else put debug block
        if not pt.exists(pt.join(path_block, blockname + '.json')):
            inexistent.append(blockname)
            blockname = 'debug'

        # open files
        with open(pt.join(path_block, blockname + '.json')) as file:
            data = json.load(file)
        with open(pt.join(path_model, data['model'])) as file:
            model_data = json.load(file)

        # create model
        palette = []
        for tex in data['palette']:
            palette.append(Texture(pt.join(path_textures, tex)))

        textures = []
        for tex in model_data['textures']:
            textures.append(palette[tex])

        verticies = []
        for v in model_data['verticies']:
            verticies.append(Vector3(v[0], v[1], v[2]))

        data_models.append(
            {
                "verticies": verticies,
                "faces": model_data['faces'],
                "normals": model_data['normals'],
                "textures": textures,
                "uvmapping": model_data['uvmapping']
            }
        )

    models = []
    for i in blocks:
        p = i['pos']
        position = Vector3(p[0], p[2], p[1])
        state = i['state']

        v = data_models[state]['verticies']
        f = data_models[state]['faces']
        n = data_models[state]['normals']
        t = data_models[state]['textures']
        m = data_models[state]['uvmapping']

        model = Model(position, verticies=v, faces=f, normals=n, textures=t, uvmapping=m)
        models.append(model)

    print("OBJECT DON'T EXIST: ", inexistent)
    draw_models(models, display, size)

if False:
    n = [
        #"../temp/side.nbt",
        "../temp/mouv.nbt",
        "../temp/debug.nbt",
        #"../temp/imprimante v1.nbt",
        #"../temp/printer_v4.nbt"
    ]

    for i in n:
        render_nbt(i)

#endregion

#region video player
# import external libraries
import vlc
# import standard libraries
import sys
import tkinter as Tk
from tkinter import ttk
from tkinter.messagebox import showerror
from os import path
from os.path import expanduser
import time
from PIL import ImageTk, Image


#_isWindows = sys.platform.startswith('win')


class Player(Tk.Frame):
    """The main window has to deal with events.
    """
    _geometry = ''
    _stopped  = None

    def __init__(self, parent, title=None, video=''):
        Tk.Frame.__init__(self, parent)

        self.parent = parent  # == root
        #self.parent.iconbitmap("media/audio_icone.ico")
        self.parent.title("Audio-Guide on Shepard Fairey")
        self.video = expanduser(video)
        self.Menu()

    def Room_1(self):
        self.suppr()
        self.video += "Room_1.mp3"
        self.AudioDisplay()

    def Room_2(self):
        self.suppr()
        self.video += "Room_2.mp3"
        self.AudioDisplay()

    def Room_3(self):
        self.suppr()
        self.video += "Room_3.mp3"
        self.AudioDisplay()

    def Room_4(self):
        self.suppr()
        self.video += "Room_4.mp3"
        self.AudioDisplay()

    def Room_5(self):
        self.suppr()
        self.video += "Room_5.mp3"
        self.AudioDisplay()

    def Credits(self):
        self.suppr()
        img = ImageTk.PhotoImage(Image.open("media/credits.png"))
        credit = Tk.Label(self.parent, image = img)
        credit.image = img
        credit.pack()

        Tk.Button(self.parent, width=10, text="Back to Menu", command=self.Menu).pack(side=Tk.LEFT)
        Tk.Button(self.parent, width=10, text="Quit", command=self.parent.destroy).pack(side=Tk.RIGHT)

        self.parent.minsize(width=250, height=327)
        self.parent.maxsize(width=250, height=327)

    def suppr(self):
        for element in self.parent.winfo_children():
            element.destroy()

    def Menu(self):
        self.suppr()

        self.video = "media/"

        Tk.Button(self.parent, width=24, height=4, text="Shepard Fairey? Who is he?", command = self.Room_1).grid(row=0, column=0)
        Tk.Button(self.parent, width=24, height=4, text="From shadow to light : \n politics as a launch way", command = self.Room_2).grid(row=0, column=1)
        Tk.Button(self.parent, width=24, height=4, text="Communication by emotion : \n the power of art", command = self.Room_3).grid(row=1, column=0)
        Tk.Button(self.parent, width=24, height=4, text="The business man behind \n the scene: OBEY", command = self.Room_4).grid(row=1, column=1)
        Tk.Button(self.parent, width=24, height=4, text="New messages : news revisited", command = self.Room_5).grid(row=2, column=0)
        Tk.Button(self.parent, width=24, height=4, text="Credits", command = self.Credits).grid(row=2, column=1)

        self.parent.geometry("356x213")
        self.parent.maxsize(width=356, height=213)
        self.parent.minsize(width=356, height=213)

    def AudioDisplay(self):
        # video button

        buttons = ttk.Frame(self.parent)
        self.playButton = ttk.Button(buttons, text="Play", command=self.OnPlay)
        stop            = ttk.Button(buttons, text="Stop", command=self.OnStop)
        self.playButton.pack(side=Tk.LEFT)
        stop.pack(side=Tk.LEFT)

        # video volume slider
        self.volVar = Tk.IntVar()
        self.volSlider = Tk.Scale(buttons, variable=self.volVar, command=self.OnVolume,
                                  from_=0, to=100, orient=Tk.HORIZONTAL, length=200,
                                  showvalue=0, label='Volume')
        self.volSlider.pack(side=Tk.RIGHT)
        buttons.pack(side=Tk.BOTTOM, fill=Tk.X)


        # panel to hold player time slider
        timers = ttk.Frame(self.parent)
        self.timeVar = Tk.DoubleVar()
        self.timeSliderLast = 0
        self.timeSlider = Tk.Scale(timers, variable=self.timeVar, command=self.OnTime,
                                   from_=0, to=1000, orient=Tk.HORIZONTAL, length=500,
                                   showvalue=0)  # label='Time',
        self.timeSlider.pack(side=Tk.TOP, fill=Tk.X, expand=1)
        self.timeSliderUpdate = time.time()
        timers.pack(side=Tk.TOP, fill=Tk.X)


        # VLC player
        args = []
        self.Instance = vlc.Instance(args)
        self.player = self.Instance.media_player_new()

        #self.parent.bind("<Configure>", self.OnConfigure)  # catch window resize, etc.
        self.parent.update()

        # Estetic, to keep our video panel at least as wide as our buttons panel.
        self.parent.geometry("502x70")
        self.parent.minsize(width=502, height=70)
        self.parent.maxsize(width=502, height=70)

        self.OnPlay()
        self.OnTick()  # set the timer up

    def _Pause_Play(self, playing):
        p = 'Pause' if playing else 'Play'
        c = self.OnPlay if playing is None else self.OnPause
        self.playButton.config(text=p, command=c)
        self._stopped = False

    def _Play(self, video):
        m = self.Instance.media_new(str(video))  # Path, unicode
        self.player.set_media(m)

        self.OnPlay()

    def OnPause(self, *unused):
        """Toggle between Pause and Play.
        """
        if self.player.get_media():
            self._Pause_Play(not self.player.is_playing())
            self.player.pause()  # toggles

    def OnPlay(self, *unused):
        """Play audio
        """
        if not self.player.get_media():
            self._Play(self.video)
            self.video = ''
        elif self.player.play():  # == -1
            self.showError("Unable to play the video.")
        else:
            self._Pause_Play(True)
            vol = self.player.audio_get_volume()
            if vol > 0:
                self.volVar.set(vol)
                self.volSlider.set(vol)

    def OnStop(self, *unused):
        """Stop the player, resets media.
        """
        self.player.stop()
        self._Pause_Play(None)
        self.timeSlider.set(0)
        self._stopped = True
        self.suppr()
        self.Menu()

    def OnTick(self):
        """Timer tick, update the time slider to the video time.
        """
        if self.player:
            t = self.player.get_length() * 1e-3  # to seconds
            if t > 0:
                self.timeSlider.config(to=t)

                t = self.player.get_time() * 1e-3  # to seconds
                if t > 0 and time.time() > (self.timeSliderUpdate + 2):
                    self.timeSlider.set(t)
                    self.timeSliderLast = int(self.timeVar.get())
        self.parent.after(1000, self.OnTick)

    def OnTime(self, *unused):
        if self.player:
            t = self.timeVar.get()
            if self.timeSliderLast != int(t):
                self.player.set_time(int(t * 1e3))  # milliseconds
                self.timeSliderUpdate = time.time()

    def OnVolume(self, *unused):
        """Volume slider changed, adjust the audio volume.
        """
        vol = min(self.volVar.get(), 100)
        self.volSlider.config(label="Volume " + str(vol))
        if self.player and not self._stopped:
                self.showError("Failed to set the volume: %s." % (v_M,))

    def showError(self, message):
        """Display a simple error dialog.
        """
        self.OnStop()
        showerror(self.parent.title(), message)


if False:
    root = Tk.Tk()
    player = Player(root, video="")
    root.mainloop()

#endregion

# Requires pydub (with ffmpeg) and Pillow
#
# Usage: python waveform.py <audio_file>

import sys

from pydub import AudioSegment
from PIL import Image, ImageDraw


class Waveform(object):

    bar_count = 107
    db_ceiling = 60

    def __init__(self, filename):
        self.filename = filename
        audio_file = AudioSegment.from_file( self.filename , self.filename.split('.')[-1])

        self.peaks = self._calculate_peaks(audio_file)

    def _calculate_peaks(self, audio_file):
        """ Returns a list of audio level peaks """
        chunk_length = len(audio_file) / self.bar_count

        loudness_of_chunks = [
            audio_file[i * chunk_length: (i + 1) * chunk_length].rms
            for i in range(self.bar_count)]

        max_rms = max(loudness_of_chunks) * 1.00

        return [int((loudness / max_rms) * self.db_ceiling)
                for loudness in loudness_of_chunks]

    def _get_bar_image(self, size, fill):
        """ Returns an image of a bar. """
        width, height = size
        bar = Image.new('RGBA', size, fill)

        end = Image.new('RGBA', (width, 2), fill)
        draw = ImageDraw.Draw(end)
        draw.point([(0, 0), (3, 0)], fill='#c1c1c1')
        draw.point([(0, 1), (3, 1), (1, 0), (2, 0)], fill='#555555')

        bar.paste(end, (0, 0))
        bar.paste(end.rotate(180), (0, height - 2))
        return bar

    def _generate_waveform_image(self):
        """ Returns the full waveform image """
        im = Image.new('RGB', (840, 128), '#f5f5f5')
        for index, value in enumerate(self.peaks, start=0):
            column = index * 8 + 2
            upper_endpoint = 64 - value

            im.paste(self._get_bar_image((4, value * 2), '#424242'),
                     (column, upper_endpoint))

        return im

    def save(self):
        """ Save the waveform as an image """
        png_filename = self.filename.replace(
            self.filename.split('.')[-1], 'png')
        with open(png_filename, 'wb') as imfile:
            self._generate_waveform_image().save(imfile, 'PNG')


if True:
    import sys
    import os.path as path
    #AudioSegment.converter = 'C:\\ffmpeg\\bin\\ffmpeg.exe'
    #AudioSegment.ffmpeg ='C:\\ffmpeg\\bin\\ffmpeg.exe'
    #envdir_list.append(r'D:\ffmpeg\bin')
    sys.path.append(path.join(path.dirname(__file__), '..'))

    filename = '../temp/cave1.ogg'

    with open(filename):
        print("test")

    waveform = Waveform(filename)
    waveform.save()