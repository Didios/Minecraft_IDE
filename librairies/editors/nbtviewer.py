# -------------------------------------------------------------------------------
# Name:        nbtviewer
# Purpose:     to visualize minecraft .nbt file in 3D window
#
# Author:      Didier Mathias
#
# Created:     27/04/2023
# -------------------------------------------------------------------------------

# be in 'librairies' file
from __future__ import annotations
import sys
import os.path as path

sys.path.append(path.join(path.dirname(__file__), '..'))

# import
import json
import python_nbt.nbt as nbt

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from random import choice
import voxelmap as vxm
import numpy as np

#region 3D tools


class Vector3:
    """
    Vector in a 3D space
    """

    def __init__(self, x: int | float = 0, y: int | float = 0, z: int | float = 0) -> None:
        """
        Initialize a Vector3
        Args:
            x (int | float): x coordinate, by default 0
            y (int | float): y coordinate, by default 0
            z (int | float): z coordinate, by default 0
        """
        self.x = x
        self.y = y
        self.z = z

    def get_relative_to(self, origin: Vector3) -> Vector3:
        """
        Get this vector in relative to another one
        Args:
            origin (Vector3): origin to set this Vector3 relative to

        Returns:
            Vector3
        """
        relative = Vector3(self.x + origin.x, self.y + origin.y, self.z + origin.z)
        return relative

    def to_tuple(self) -> tuple[int | float, int | float, int | float]:
        """
        Get a tuple representation
        Returns:
            tuple(x, y, z)
        """
        return (self.x, self.y, self.z)


class RGB:
    def __init__(self, r: int | float = 1, g: int | float = 1, b: int | float = 1, t: int = 1) -> None:
        """
        Initialize a RGB color
        Args:
            r (int | float): red value, by default 1
            g (int | float): green value, by default 1
            b (int | float): blue value, by default 1
            t (int): 1 or 255, on which field is the value defined, by default 1
        """
        self.red = r
        self.green = g
        self.blue = b
        self.type = t

    def get_color(self, t: int = 1) -> tuple[int | float, int | float, int | float]:
        """
        Get color in a tuple form, can specify the type
        Args:
            t (int): 1 or 255, on which field is the value defined, by default 1

        Returns:
            tuple with rgb values
        """
        if self.type == 1 and t == 255:
            return (self.red * 255, self.green * 255, self.blue * 255)
        elif self.type == 255 and t == 1:
            return (self.red / 255, self.green / 255, self.blue / 255)

        return (self.red, self.green, self.blue)

    def to_tuple(self) -> tuple[int | float, int | float, int | float]:
        """
        get color in a tuple form
        Returns:
            tuple with rgb value
        """
        return (self.red, self.green, self.blue)


class Texture:
    def __init__(self, filepath: str) -> None:
        """
        Initialize and create a new Texture, use for and with PyOpenGl, context must be set before
        Args:
            filepath (str): the relative or absolute path to the file texture
        """
        self.filepath = filepath

        # load texture file
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
    def __init__(self, coordinate: Vector3, verticies: list[Vector3] = [], faces: list[list[int, int, int, int]] = [],
                 normals: list[list[int | float, int | float, int | float]] = [], wire: RGB = RGB(),
                 textures: list[Texture] = None, uvmapping: list[list[list[float, float]]] = None) -> None:
        """
        Initialize a 3D model with PyOpenGl, the model can only use quads
        Args:
            coordinate (): coordinates of the origin of the model
            verticies (): relative coordinates of each vertex, by default []
            faces (): each list contain 4 point to create faces, by default []
            normals (): normals vector for each face, by default []
            wire (): color of the wire if draw edge, by default RGB()
            textures (): textures used by each face, by default None
            uvmapping (): textures mapping for each face, by default None
        """

        self.coordinate = coordinate
        self.verticies = tuple(v.get_relative_to(coordinate).to_tuple() for v in verticies)

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

    def draw_wire(self) -> None:
        """
        Draw model edges with line
        """
        glColor3fv(self.wire)
        glBegin(GL_LINES)

        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])

        glEnd()

    def draw(self) -> None:
        """
        Draw model with all texture on faces, if no texture is defined, draw edges only
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

#endregion

#region render function


def render_pyopengl(models: list[Model], display: tuple[int, int], size: tuple[int, int, int], draw_wire: bool = False) -> None:
    """
    Display models in a window with opengl
    Args:
        models (): list of models to render
        display (): size of the window to diplay
        size (): zone take by all models
        draw_wire (): model should be drawn with their wire, by default False
    """
    # create pygame window
    clock = pygame.time.Clock()

    x = (max(size[0], size[2]) / 2) - 0.5
    y = (size[1] / 2) - 0.5
    z = size[1] * 2

    print(size, x, y, z)

    # setup opengl
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glTranslatef(-x, -y, -z)
    glRotatef(-90, 1, 0, 0)

    # set light
    glLight(GL_LIGHT0, GL_POSITION, (size[0] * 2, size[1] * 2, size[2] * 2, 1))  # point light from the left, top, front
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
                # quit()
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
                glRotatef(1, up, 0, right * 2)
                # glRotatef(1, up, 0, 0)
            # wheel for zoom
            # move around with drag

        if not con:
            break;

        # clear opengl buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # set light
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # rotate things
        #glRotatef(1, 0, 0, 1)

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


def render_block(blockname: str, data_path: str) -> None:
    """
    Display a single block in a little window with PyOpenGl, data of the block must be in data/3D/
    Args:
        blockname (): name of the block to generate
    """
    # file path
    path_model = path.join(data_path, '3D', 'models')
    path_block = path.join(data_path, '3D', 'blocks')
    path_textures = path.join(data_path, '3D', 'textures')

    # get data
    with open(path.join(path_block, blockname + '.json')) as file:
        data = json.load(file)
    with open(path.join(path_model, data['model'])) as file:
        model_data = json.load(file)

    # create opengl context
    pygame.init()
    display = (400, 300)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # get textures data
    palette = []
    textures = []
    for tex in data['palette']:
        palette.append(Texture(path.join(path_textures, tex)))
    for tex in model_data['textures']:
        textures.append(palette[tex])

    # get verticies data
    verticies = []
    for v in model_data['verticies']:
        verticies.append(Vector3(v[0], v[1], v[2]))

    # create model
    model_0 = Model(Vector3(0, 0, 0), verticies=verticies, faces=model_data['faces'], normals=model_data['normals'],
                    textures=textures, uvmapping=model_data['uvmapping'])

    # display model
    render_pyopengl([model_0], display, (1, 1, 1))

#endregion

#region utils


def get_nbt_data(filepath: str) -> tuple[list[int, int, int], list[dict[str: list[int, int, int] | int]], list[dict[str: dict | str]]]:
    """
    Retrieve nbt data from a nbt file
    Args:
        filepath (): relative or absolut path to the .nbt file

    Returns:
        size of the structure
        blocks data
        palette data
    """
    data_brut = nbt.read_from_nbt_file(filepath)
    data = data_brut.json_obj(full_json=False)

    size = tuple(data['size'])
    blocks = data['blocks']
    palette = data['palette']

    return size, blocks, palette


def clean_base(value: str) -> str:
    """
    Clean a minecraft index name from the '#minecraft:' if present
    Args:
        value (): the string to evaluate

    Returns:
        clean string
    """
    index = value.find('minecraft:')

    if index == 0:
        return value[10::]
    elif index == 1 and value[0] == '#':
        return '#' + value[11::]

    return value

def get_air_state(palette: list[dict[str: dict | str]]) -> int:
    """
    Get state index of air block for a palette
    Args:
        palette (): palette to analyse

    Returns:
        int index
    """
    air_state = -1
    for i in range(len(palette)):
        if palette[i]['Name'] == 'minecraft:air':
            air_state = i
            break;

    return air_state


def get_random_color() -> str:
    """
    Create a hex random color code
    Returns:
        hex color code
    """
    c = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    s = '#'
    for i in range(6):
        s += choice(c)
    return s


def get_palette_color(palette: list[dict[str: dict | str]], reference: dict[str: str] = None):
    """
    Get all color of a palette, if no reference is provided, random colors are set
    Args:
        palette (): palette to analyze
        reference (): colors reference for each block

    Returns:
        list of all color, index are the same as in palette
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

#endregion

#region display function


def display_pyopengl(filepath: str, data_path: str) -> None:
    """
    Render a .nbt file with PyOpenGl and PyGame, block data must be in 'data/3D',
    inexistent blocks will be replaced with debug block
    Args:
        filepath (): relative or absolute path to the .nbt file
    """
    # path file to data
    path_model = path.join(data_path, '3D', 'models')
    path_block = path.join(data_path, '3D', 'blocks')
    path_textures = path.join(data_path, '3D', 'textures')

    # retrieve data from file
    size, blocks, palette = get_nbt_data(filepath)

    # create PyOpenGl context for textures
    pygame.init()
    display = (400, 300)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # get data models
    data_models = []
    inexistent = []
    for i in palette:
        blockname = clean_base(i['Name'])

        # check if block data exists, else put debug block
        if not path.exists(path.join(path_block, blockname + '.json')):
            inexistent.append(blockname)
            blockname = 'debug'

        # open files
        with open(path.join(path_block, blockname + '.json')) as file:
            data = json.load(file)
        with open(path.join(path_model, data['model'])) as file:
            model_data = json.load(file)

        # transform textures and verticies info
        palette = []
        for tex in data['palette']:
            palette.append(Texture(path.join(path_textures, tex)))

        textures = []
        for tex in model_data['textures']:
            textures.append(palette[tex])

        verticies = []
        for v in model_data['verticies']:
            verticies.append(Vector3(v[0], v[1], v[2]))

        # save model dara infos
        data_models.append(
            {
                "verticies": verticies,
                "faces": model_data['faces'],
                "normals": model_data['normals'],
                "textures": textures,
                "uvmapping": model_data['uvmapping']
            }
        )

    # create data
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

    # display inexistent block
    if len(inexistent) > 0:
        print("OBJECTS DON'T EXIST: ", inexistent)

    # render models
    render_pyopengl(models, display, size)


def display_voxel(filepath: str) -> None:
    """
    Render a .nbt file with VoxelMap,
    each block of the palette get a random color
    Args:
        filepath (): relative or absolute path to the .nbt file
    """
    # get data
    size, blocks, palette = get_nbt_data(filepath)

    air_state = get_air_state(palette)
    colors = get_palette_color(palette)

    # init voxel array
    array = np.ndarray(size, int)

    # get block state
    # 0 is the index for transparent block (air)
    for i in blocks:
        pos = i['pos']
        state = i['state']

        if state != air_state:
            array[pos[0]][pos[1]][pos[2]] = state +1
        else:
            array[pos[0]][pos[1]][pos[2]] = 0

    # put voxel block state data into vxm.Model structure
    model = vxm.Model(array)

    # add voxel colors into model by index (needed for `custom` coloring)
    for i in range(len(colors)):
       model.hashblocks_add(i+1, colors[i]) # next parameter is alpha

    # display the voxel map
    model.draw('custom', background_color='#ffffff')

#endregion


def display_nbt_file(filepath: str, model_type: str = 'voxel', data_path: str = '') -> None:
    """
    Display a view of a .nbt file in a window dedicated, can choose between voxel or textured view
    Args:
        filepath (): filepath to the file to render
        model_type (): 'voxel' or 'opengl', type of render to display, by default 'voxel'
    """

    if model_type == 'voxel':
        display_voxel(filepath)
    elif model_type == 'opengl':
        display_pyopengl(filepath, data_path)


if __name__ == "__main__":
    b = [
        "acacia_planks",
        "crafting_table",
        "redstone_torch"
    ]

    display_nbt_file('../../temp/mouv.nbt')

    for i in b:
        render_block(i, path.join(path.dirname(__file__), 'data'))
