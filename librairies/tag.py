# -------------------------------------------------------------------------------
# Name:        tag
# Purpose:     check if a tag is good
#
# Author:      Didier Mathias
# Created:     24/12/2022
# -------------------------------------------------------------------------------

import os.path as path
import sys
sys.path.append(path.join(path.dirname(__file__)))

from result import Result
from dataLoader import data

from strenum import StrEnum


class e_tag(StrEnum):
    NULL = '@null'
    PLAYER = '@player'
    ADVANCEMENT = '@advancement'
    CRITERION = '@criterion'
    ENTITY = '@entity'
    ATTRIBUTE = '@attribute'
    INT = '@int'
    FLOAT = '@float'
    UUID = '@uuid'
    STRING = '@string'
    IP = '@ip'
    NAMESPACE = '@namespace'
    TEXT = '@text'
    ITEM = '@item'
    ZONE = '@zone'
    COORDINATE = '@coordinate'
    NBTPATH = '@nbtpath'
    FLOATNBT = '@floatnbt'
    NBT = '@nbt'
    VALUENBT = '@valuenbt'
    DATAPACK = '@datapack'
    FUNCTION = '@function'
    GAMEMODE = '@gamemode'
    DIFFICULTY = '@difficulty'
    EFFECT = '@effect'
    ENCHANT = '@enchant'
    AXIS = '@axis'
    BLOCK = '@block'
    PREDICATE = '@predicate'
    SCORE = '@score'
    BETWEEN = '@between'
    DIM = '@dim'
    ROTATION = '@rotation'
    GAMERULE = '@gamerule'
    BOOL = '@bool'
    COMMAND = '@command'
    MODIFICATOR = '@modificator'
    SLOT = '@slot'
    BIOME = '@biome'
    POI = '@poi'
    STRUCTURE = '@structure'
    LOOT = '@loot'
    TOOL = '@tool'
    END = '@end'
    PARTICLE = '@particle'
    RGB = '@rgb'
    FEATURE = '@feature'
    SOUND = '@sound'
    SOURCE = '@source'
    RECIPE = '@recipe'
    TIME = '@time'
    OBJECTIVE = '@objective'
    CRITERIA = '@criteria'
    POSITION = '@position'
    MOB = '@mob'
    TEAM = '@team'
    COLOR = '@color'
    LIST = '@list'


def tag_result(desc, pos=(0, 0)):
    return Result(error=True, type="ValueError", desc=desc, position=pos)


def check_tag(tag: str, values: list[str], loader: data) -> Result:
    """
    Check if a tag is correct in a minecraft command
    Args:
        tag (): tag to check, include options
        values (): next arguments in the command
        loader (): data to open file in correct version

    Returns:
        result of the operation
    """
    # get options and separate it from tag
    options = []
    while tag[-2] == "-":
        options += [tag[-2::] + '']
        tag = tag[0:-2]

    # default result
    r = tag_result(f"Type of {tag} is not defined")

    # get tag enum
    t = tag # e_tag[tag]

    if t == e_tag.ADVANCEMENT:
        return is_in_data(values[0], loader, 'advancement')
    elif t == e_tag.ATTRIBUTE:
        return is_in_data(values[0], loader, 'attribute')
    elif t == e_tag.GAMEMODE:
        return is_in_data(values[0], loader, 'gamemode')
    elif t == e_tag.DIFFICULTY:
        return is_in_data(values[0], loader, 'difficulty')
    elif t == e_tag.EFFECT:
        return is_in_data(values[0], loader, 'effect')
    elif t == e_tag.DIM:
        return is_in_data(values[0], loader, 'dimension')
    elif t == e_tag.BIOME:
        return is_in_data(values[0], loader, 'biome')
    elif t == e_tag.POI:
        return is_in_data(values[0], loader, 'poi')
    elif t == e_tag.STRUCTURE:
        return is_in_data(values[0], loader, 'structure')
    elif t == e_tag.PARTICLE:
        return is_in_data(values[0], loader, 'particle')
    elif t == e_tag.FEATURE:
        return is_in_data(values[0], loader, 'feature')
    elif t == e_tag.SOURCE:
        return is_in_data(values[0], loader, 'source')
    elif t == e_tag.POSITION:
        return is_in_data(values[0], loader, 'position')
    elif t == e_tag.MOB:
        return is_in_data(values[0], loader, 'mob')
    elif t == e_tag.SLOT:
        return is_in_data(values[0], loader, 'slot')
    elif t == e_tag.SOUND:
        return is_in_data(values[0], loader, 'sound')
    elif t == e_tag.RECIPE:
        return is_in_data(values[0], loader, 'recipe')
    elif t == e_tag.LOOT:
        return is_in_data(values[0], loader, 'loot')
    elif t == e_tag.TOOL:
        return is_in_data(values[0], loader, 'tool')
    elif t == e_tag.INT:
        return is_integer(options, values)
    elif t == e_tag.STRING:
        return is_string(options, values)
    elif t == e_tag.FLOAT:
        return is_float(options, values)
    elif t == e_tag.UUID:
        return is_uuid(values)
    elif t == e_tag.IP:
        return is_ip(values)
    elif t == e_tag.AXIS:
        return is_axis(values)
    elif t == e_tag.BETWEEN:
        return is_between(values)
    elif t == e_tag.ROTATION:
        return is_rotation(values)
    elif t == e_tag.BOOL:
        return is_bool(values)
    elif t == e_tag.END:
        return is_end(values)
    elif t == e_tag.RGB:
        return is_rgb(values)
    elif t == e_tag.TEAM:
        return is_team(values)
    elif t == e_tag.COORDINATE:
        return is_coordinate(options, values)
    elif t == e_tag.COLOR:
        return is_color(options, values, loader)
    elif t == e_tag.GAMERULE:
        return is_gamerule(options, values, loader)
    elif t == e_tag.TIME:
        return is_time(values)
    elif t == e_tag.ENCHANT:
        return is_enchant(options, values, loader)
    elif t == e_tag.BLOCK:
        return is_block(options, values, loader)
    elif t == e_tag.ITEM:
        return is_item(options, values, loader)
    elif t == e_tag.OBJECTIVE:
        return is_objective(values)
    elif t == e_tag.CRITERIA:
        return is_criteria(values, loader)
    elif t == e_tag.ZONE:
        return is_zone(values)

    return r

#region tools


def clean_base(value):
    index = value.find('minecraft:')

    if index == 0:
        return value[10::]

    if value[0] == '#' and index == 1:
        return '#' + value[11::]

    return value


def is_in_data(value, loader, dataname):
    """
    data of type dataname
    exists in dataname.json
    """
    value = clean_base(value)

    data = loader.get_data(dataname)["a_data"]
    if value not in data:
        return tag_result(f"{dataname.capitalize()} {value} doesn't exists")

    return Result()


def get_number(chain):
    if len(chain) < 1:
        return None

    is_negative = False
    if chain[0] == '-':
        chain = chain[1::]
        is_negative = True

    if len(chain) < 1:
        return None
    if chain[0] == '.' or chain[-1] == '.':
        return None

    is_float = False
    nbr = 0
    multiplier = 1
    i = len(chain) - 1
    while i >= 0:
        char = chain[i]
        if char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            if not is_float and char == '.':
                is_float = True
                nbr = nbr / multiplier
                multiplier = multiplier // multiplier
            else:
                return None
        else:
            nbr += int(char) * multiplier
            multiplier *= 10

        i -= 1

    if is_negative:
        nbr = -nbr

    return nbr

#endregion tools

# PARAMETER:
#   options = ['--', '-p', '-1'] >> see tag modificator
#   values = [] >> next arguments of the command
# RETURN:
#   (tagIsGood, reasonOnFalse, numberOfValuesToSkip)

#region check function


def is_integer(options, values):
    """
    data on integer type
    -+ >> is positiv or null
    -1 >> is greater than 0
    -p >> is a port, must be in range 0-65535
    """
    if len(values[0]) == 0:
        return tag_result("There is no value")

    nbr = get_number(values[0])
    if type(nbr) is not int:
        return tag_result("Impossible Int")

    if '-+' in options and nbr < 0:
        return tag_result("Int must be greater or equal to 0")
    if '-1' in options and nbr < 1:
        return tag_result("Int must be greater or equal to 1")
    if '-p' in options and (nbr < 0 or nbr > 65535):
        return tag_result("Int must be between 0 and 65535")

    return Result()


def is_string(options, values):
    """
    data of string type
    -l >> englobe all the other values
    """
    if '-l' in options:
        return Result(position=(len(values), 0))

    return Result()


def is_float(options, values):
    """
    data of float type
    """
    if len(values[0]) == 0:
        return tag_result("There is no value")

    if values[-1] == 'F':
        nbr = get_number(values[0][::-1])
    else:
        nbr = get_number(values[0])

    if nbr is None:
        return tag_result("Impossible float")

    if '-f' in options and values[-1] == 'F':
        return tag_result("This float doesn't need and 'F'")

    return Result()


def is_uuid(values):
    """
    data of uuid type, must be in the following form:
        00000000-0000-0000-0000-000000000000
    """
    base = "00000000-0000-0000-0000-000000000000"
    error = tag_result(f"UUID must be in this form : {base}")

    if len(values[0]) != len(base):
        return error

    baseList = base.split('-')
    numberList = values[0].split('-')

    if len(numberList) != len(baseList):
        return error

    for i in range(len(numberList)):
        if len(numberList[i]) != len(baseList[i]):
            return error
        if not type(get_number(numberList[i])) is not int:
            return error

    return Result()


def is_ip(values):
    """
    data of type ip adress, like:
        255.255.255.255
    4 number in range 0-255 separate by '.'
    """
    error = tag_result("IP adress must be composed of 4 integer separate by '.'")

    numberList = values[0].split('.')

    if len(numberList) != 4:
        return error

    for n in numberList:
        nbr = get_number(n)
        if type(nbr) is not int:
            return error

        if nbr < 0 or nbr > 255:
            return tag_result("IP adress must be composed by numbers between 0 and 255")

    return Result(True)


def is_axis(values):
    """
    data of type axis, must have at least one the three letters x, y, z
    and can only have one iteration of each
    the order has no importance
    """
    if len(values[0]) > 3:
        return tag_result("There is only 3 Axis : xyz")

    for l in values[0]:
        if l not in ['x', 'y', 'z']:
            return tag_result(f"Axis of type {l} doesn't exists")

    if values[0].count('x') > 1 or values[0].count('y') > 1 or values[0].count('z') > 1:
        return tag_result("Each Axis can only be present once")

    return Result()


def is_between(values):
    """
    data of type between, can be a float, an integer or with the form min..max where
    min and max are two numbers
    """
    numberList = values[0].split('..')

    if len(numberList) > 2:
        return tag_result("Interval can only have two extrema")

    for n in numberList:
        if not get_number(n) is not None:
            return tag_result("Interval need to be composed of numbers")

    return Result()


def is_rotation(values):
    """
    data of type rotation
    two consecutives int
    """
    if len(values) < 2:
        return tag_result("Rotation is incomplete")

    if type(get_number(values[0])) is not int or type(get_number(values[1])) is not int:
        return tag_result("Rotation need to be two consecutives Integer")

    return Result(position=(1, 0))


def is_bool(values):
    """
    data of type boolean,
    is 'true' or 'false'
    true can be 1b and false can be 0b too
    """
    if values[0] not in ['true', 'false', '1b', '0b']:
        return tag_result("Boolean need to be true, false, 1b or 0b")

    return Result()


def is_end(values):
    """
    data on type end
    all next argument are gonna be valid
    """
    return Result(position=(len(values), 0))


def is_rgb(values):
    """
    data of type RGB
    3 consecutives numbers in range 0-255
    """
    if len(values) < 3:
        return tag_result("RGB is incomplete")

    for i in range(3):
        nbr = get_number(values[i])
        if type(nbr) is not int:
            return tag_result("RGB need to be 3 int")

        if nbr < 0 or nbr > 255:
            return tag_result("RGB numbers need to be between 0 and 255")

    return Result(position=(2, 0))


def is_team(values):
    """
    data of type team
    is a string without space
    """
    if ' ' in values[0]:
        return tag_result("Team cannot contain space")

    return Result()


def is_coordinate(options, values):
    """
    data of types coordinates
    3 float or int, can be preceded by '~' or '^' but not the 2 in the same coordinate
    -2 >> only 2 numbers are necessary
    """
    signs = ['~', '^']
    sign = ''

    length = 3
    if '-2' in options:
        length = 2

    if len(values) < length:
        return tag_result(f"Not Enough Values, need {length} values")

    for i in range(length):
        val = values[i]
        if len(val) == 0:
            return tag_result("Value is Null", (i, 0))

        if sign == '':
            if val[0] in signs:
                sign = val[0]
                number = val[1::]
            else:
                number = val
        elif val[0] in signs and val[0] != sign:
            return tag_result("No Symbols Mix Allowed", (i, 0))
        else:
            number = val[1::]

        if number != '' and get_number(number) is None:
            return tag_result("Value is not a number", (i, 0))

    return Result(position=(2, 0))


def is_color(options, values, loader):
    """
    data of type color
    exists in color.json
    -r >> can also be 'reset'
    """
    r = is_in_data(values[0], loader, "color")

    if '-r' in options:
        if values[0] == 'reset':
            r = Result()

    return r


def is_gamerule(options, values, loader):
    """
    data of type gamerule
    exists in gamerule.json
    -v >> check the next value depend on the gamerule
    """
    gamerule = loader.get_data("gamerule")
    data = gamerule["a_data"]

    if values[0] not in data:
        return tag_result(f"Gamerule values[0] doesn't exists")

    r = Result()
    if '-v' in options and len(values[1::]) > 0:
        datavalues = gamerule["a_value"][data.index(values[0])]
        if datavalues == '@bool':
            r = is_bool(values[1::])
        elif datavalues == '@int':
            r = is_integer([], values[1::])

        r.position_add(1)

    return r


def is_time(values):
    """
    data of type time
    a nul or positive float follow by 'd', 's' or 't'
    a nul or positive integer
    """
    need_float = False
    if values[0][-1] in ['d', 's', 't']:
        need_float = True
        values[0] = values[0][::-1]

    nbr = get_number(values[0])

    if nbr is None:
        return tag_result("Time need to be a number")

    if nbr < 0:
        return tag_result("Time numbers needs to be nul or positive number")

    if need_float:
        if type(nbr) is float:
            return Result()
        return tag_result("This time need to be a float")

    if type(nbr) is int:
        return Result()
    return tag_result("This time need to be an int")


def is_enchant(options, values, loader):
    """
    data of type enchant
    exists in enchantment.json
    -v >> check the next value depend on the enchant
    """
    enchant = loader.get_data("enchantment")
    data = enchant["a_data"]

    values[0] = clean_base(values[0])
    if values[0] not in data:
        return tag_result(f"Enchantment {values[0]} doesn't exists")

    r = Result()
    if '-v' in options and len(values[1::]) > 0:
        maxLevel = enchant["a_level"][data.index(values[0])]

        if values[1] < 0 or values[1] > maxLevel:
            r = tag_result(f"This enchant must be between 0 and level {maxLevel}")

        r.position_add(1)

    return r


def is_block(options, values, loader):
    """
    data of type block
    exists in block.json
    -d >> can also be a blocktag
    -n >> can be follow by a @nbt
    """
    j_block = loader.get_data("block")
    blocks = j_block["a_data"]
    tags = j_block["a_tag"]
    nbt = ""

    values[0] = clean_base(values[0])

    if '-n' in options and '{' in values[0]:
        index = values[0].find('{')
        nbt = values[0][index::]

    r = Result()

    if values[0] not in blocks:
        if '-d' in options:
            if values[0] not in tags:
                r = tag_result(f"Block (type) {values[0]} doesn't exists")
        else:
            r = tag_result(f"Block {values[0]} doesn't exists")

    if r.is_error():
        return r

    if '-n' in options and len(nbt) > 0:
        r = is_nbt(nbt)

    return r


def is_item(options, values, loader):
    """
    data of type item
    exists in item.json
    -n >> can be follow by a @nbt
    """
    j_item = loader.get_data("block")
    items = j_item["a_data"]

    values[0] = clean_base(values[0])

    nbt = ""
    if '-n' in options and '{' in values[0]:
        index = values[0].find('{')
        nbt = values[0][index::]

    r = Result()
    if values[0] not in items:
        r = tag_result(f"Item {values[0]} doesn't exists")

    if r.is_error():
        return r

    if '-n' in options and len(nbt) > 0:
        r = is_nbt(nbt)

    return r


def is_objective(values):
    """
    data of type objectives
    a string with a max length of 16
    """
    if len(values[0]) > 16:
        return tag_result("Objectives has a max length of 16")
    return Result()


def is_criteria(values, loader):
    """
    data of type criteria
    exists in criteria.json
    """
    j_criteria = loader.get_data("criteria")
    criteria = j_criteria["a_data"]

    # remove unnecessary 'minecraft.'
    if values[0].find('minecraft.') == 0:
        values[0] = values[0][10::]

    index = values[0].find('minecraft.')
    if index > 1:
        if values[0][index - 1] == ':':
            values[0] = values[0][0:index] + values[0][index + 10::]

    for c in criteria:
        if '@' in c:
            cut_c = c.split(':')
            cut_v = values[0].split(':')

            if cut_v[0] == cut_c[0]:
                if ':' in cut_v[1]:
                    break
                elif cut_c[1] == 'item' and is_item([], [cut_v[1]], loader):
                    return Result()
                elif cut_c[1] == 'block' and is_block([], [cut_v[1]], loader):
                    return Result()
                elif cut_c[1] == 'mob' and not check_tag("@mob", [cut_v[1]], loader).is_error():
                    return Result()
                elif cut_c[1] == 'color' and is_color([], [cut_v[1]], loader):
                    return Result()
                break
        elif values[0] == c:
            return Result()

    return tag_result(f"Criteria {values[0]} doesn't exists")


def is_zone(values):
    """
    data of type zone
    two @coordinates consecutives
    the volume between the 2 point can't exceed 32768 block
    """

    if len(values) < 6:
        return tag_result("Zone need two consecutives coordinates", (len(values), 0))

    # check if coordinates are correct
    r = is_coordinate([], values[0:3])
    if r.is_error():
        return tag_result(f"Zone first coordinate is incorrect : {r.desc}", r.get_position())

    r = is_coordinate([], values[3::])
    if r.is_error():
        return tag_result(f"Zone second coordinate is incorrect : {r.desc}",
                          (3 + r.get_position()[0], r.get_position()[1]))

    # check zone size
    pointA = []
    pointB = []
    for i in range(6):
        if values[i][0] in ['~', '^']:
            values[i] = values[i][1::]

        nbr = get_number(values[i])
        if nbr is None:
            nbr = 0

        if i < 3:
            pointA += [nbr]
        else:
            pointB += [nbr]

    x = abs(pointB[0] - pointA[0])
    y = abs(pointB[1] - pointA[1])
    z = abs(pointB[2] - pointA[2])

    if x * y * z > 32768:
        return tag_result("Zone size can't be higher than 32'768 block (suppose local position is 0 0 0)")

    return Result(position=(5, 0))


def is_nbt(value):
    return tag_result("NBT CHECK DONT EXISTS")

#endregion
