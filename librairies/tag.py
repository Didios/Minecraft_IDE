#-------------------------------------------------------------------------------
# Name:        tag
# Purpose:     check if a tag is good
#
# Author:      Didier Mathias
#
# Created:     24/12/2022
# Copyright:   (c) Elève 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__)))

import dataLoader as dl

class tagResult:
    def __init__(self, isGood, reason="", toSkip=0):
        self.result = isGood
        self.reason = reason
        self.nbrToSkip = toSkip

    def get_result(self):
        return self.result

    def get_reason(self):
        return self.reason

    def get_skip_number(self):
        return self.nbrToSkip

    def __str__(self):
        return "(%s, %s, %i)" % (self.result, self.reason, self.nbrToSkip)

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
        return tagResult(False, "%s %s doesn't exists" % (dataname.capitalize(), '"%s"' % (value)))

    return tagResult(True)

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
    i = len(chain) -1
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

#region is_in_data tag

def is_advancement(options, values, loader):
    """
    data of type advancement
    exists in advancement.json
    """
    return is_in_data(values[0], loader, "advancement")

def is_attribute(options, values, loader):
    """
    data of type attribute
    exists in attribute.json
    """
    return is_in_data(values[0], loader, "attribute")

def is_gamemode(options, values, loader):
    """
    data of type gamemode
    exists in gamemode.json
    """
    return is_in_data(values[0], loader, "gamemode")

def is_difficulty(options, values, loader):
    """
    data of type difficulty
    exists in difficulty.json
    """
    return is_in_data(values[0], loader, "difficulty")

def is_effect(options, values, loader):
    """
    data of type effect
    exists in effect.json
    """
    return is_in_data(values[0], loader, "effect")

def is_dimension(options, values, loader):
    """
    data of type dimension
    exists in dimension.json
    """
    return is_in_data(values[0], loader, "dimension")

def is_biome(options, values, loader):
    """
    data of type biome
    exists in biome.json
    """
    return is_in_data(values[0], loader, "biome")

def is_poi(options, values, loader):
    """
    data of type poi (Point Of Interest)
    exists in poi.json
    """
    return is_in_data(values[0], loader, "poi")

def is_structure(options, values, loader):
    """
    data of type structure
    exists in structure.json
    """
    return is_in_data(values[0], loader, "structure")

def is_particle(options, values, loader):
    """
    data of type particle
    exists in particle.json
    """
    return is_in_data(values[0], loader, "particle")

def is_feature(options, values, loader):
    """
    data of type feature
    exists in feature.json
    """
    return is_in_data(values[0], loader, "feature")

def is_source(options, values, loader):
    """
    data of type source
    exists in source.json
    """
    return is_in_data(values[0], loader, "source")

def is_position(options, values, loader):
    """
    data of type position
    exists in position.json
    """
    return is_in_data(values[0], loader, "position")

def is_mob(options, values, loader):
    """
    data of type mob
    exists in mob.json
    """
    return is_in_data(values[0], loader, "mob")

def is_slot(options, values, loader):
    """
    data of type slot
    exists in slot.json
    """
    return is_in_data(values[0], loader, "slot")

def is_sound(options, values, loader):
    """
    data of type sound
    exists in sound.json
    """
    return is_in_data(values[0], loader, "sound")

def is_recipe(options, values, loader):
    """
    data of type recipe
    exists in recipe.json
    """
    return is_in_data(values[0], loader, "recipe")

def is_loot(options, values, loader):
    """
    data of type loot table
    exists in loot.json
    """
    return is_in_data(values[0], loader, "loot")

def is_tool(options, values, loader):
    """
    data of type tool
    exists in tool.json
    """
    return is_in_data(values[0], loader, "tool")
#endregion is_in_data tag

def is_integer(options, values):
    """
    data on integer type
    -+ >> is positiv or null
    -1 >> is greater than 0
    -p >> is a port, must be in range 0-65535
    """
    if len(values[0]) == 0:
        return tagResult(False, "There is no value")

    nbr = get_number(values[0])
    if type(nbr) is not int:
        return tagResult(False, "Impossible Int")

    if '-+' in options and nbr < 0:
        return tagResult(False, "Int must be greater or equal to 0")
    if '-1' in options and nbr < 1:
        return tagResult(False, "Int must be greater or equal to 1")
    if '-p' in options and (nbr < 0 or nbr > 65535):
        return tagResult(False, "Int must be between 0 and 65535")

    return tagResult(True)

def is_string(options, values):
    """
    data of string type
    -l >> englobe all the other values
    """
    if '-l' in options:
        return tagResult(True, "", len(values))

    return tagResult(True)

def is_float(options, values):
    """
    data of float type
    """
    if len(values[0]) == 0:
        return tagResult(False, "There is no value")

    if values[-1] == 'F':
        nbr = get_number(values[0][::-1])
    else:
        nbr = get_number(values[0])

    if nbr is None:
        return tagResult(False, "Impossible float")

    if '-f' in options and values[-1] == 'F':
        return tagResult(False, "This float doesn't need and 'F'")

    return tagResult(True)

def is_uuid(options, values):
    """
    data of uuid type, must be in the following form:
        00000000-0000-0000-0000-000000000000
    """
    error = tagResult(False, "UUID must be in this form : %s" % (base))

    base = "00000000-0000-0000-0000-000000000000"
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

    return tagResult(True)

def is_ip(options, values):
    """
    data of type ip adress, like:
        255.255.255.255
    4 number in range 0-255 separate by '.'
    """
    error = tagResult(False, "IP adress must be composed of 4 integer separate by '.'")

    numberList = values[0].split('.')

    if len(numberList) != 4:
        return error

    for n in numberList:
        nbr = get_number(n)
        if type(nbr) is not int:
            return error

        if nbr < 0 or nbr > 255:
            return tagResult(False, "IP adress must be composed by numbers between 0 and 255")

    return tagResult(True)

def is_axis(options, values):
    """
    data of type axis, must have at least one the three letters x, y, z
    and can only have one iteration of each
    the order has no importance
    """
    if len(values[0]) > 3:
        return tagResult(False, "There is only 3 Axis : xyz")

    for l in values[0]:
        if l not in ['x', 'y', 'z']:
            return tagResult(False, "Axis of type %s doesn't exists" % (l))

    if values[0].count('x') > 1 or values[0].count('y') > 1 or values[0].count('z') > 1:
        return tagResult(False, "Each Axis can only be present once")

    return tagResult(True)

def is_between(options, values):
    """
    data of type between, can be a float, an integer or with the form min..max where
    min and max are two numbers
    """
    numberList = values[0].split('..')

    if len(numberList) > 2:
        return tagResult(False, "Interval can only have two extrema")

    for n in numberList:
        if not get_number(n) is not None:
            return tagResult(False, "Interval need to be composed of numbers")

    return tagResult(True)

def is_rotation(options, values):
    """
    data of type rotation
    two consecutives int
    """
    if len(values) < 2:
        return tagResult(False, "Rotation is incomplete")

    if type(get_number(values[0])) is not int or type(get_number(values[1])) is not int:
        return tagResult(False, "Rotation need to be two consecutives Integer")

    return tagResult(True, "", 1)

def is_bool(options, values):
    """
    data of type boolean,
    is 'true' or 'false'
    true can be 1b and false can be 0b too
    """
    if values[0] not in ['true', 'false', '1b', '0b']:
        return tagResult(False, "Boolean need to be true, false, 1b or 0b")

    return tagResult(True)

def is_end(options, values):
    """
    data on type end
    all next argument are gonna be valid
    """
    return tagResult(True, "", len(values))

def is_rgb(options, values):
    """
    data of type RGB
    3 consecutives numbers in range 0-255
    """
    if len(values) < 3:
        return tagResult(False, "RGB is incomplete")

    for i in range(3):
        nbr = get_number(values[i])
        if type(nbr) is not int:
            return tagResult(False, "RGB need to be 3 int")

        if nbr < 0 or nbr > 255:
            return tagResult(False, "RGB numbers need to be between 0 and 255")

    return tagResult(True, "", 2)

def is_team(options, values):
    """
    data of type team
    is a string without space
    """
    if ' ' in values[0]:
        return tagResult(False, "Team cannot contain space")

    return tagResult(True)

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
        return tagResult(False, "Not Enough Values, need %d values" % (length))

    for i in range(length):
        val = values[i]
        if len(val) == 0:
            return tagResult(False, "Value is Null", i)

        number = ''
        if sign == '':
            if val[0] in signs:
                sign = val[0]
                number = val[1::]
            else:
                number = val
        elif val[0] in signs and val[0] != sign:
            return tagResult(False, "No Symbols Mix Allowed", i)
        else:
            number = val[1::]

        if number != '' and get_number(number) is None:
            return tagResult(False, "Value is not a number", i)

    return tagResult(True, "", 2)

def is_color(options, values, loader):
    """
    data of type color
    exists in color.json
    -r >> can also be 'reset'
    """
    result = is_in_data(values[0], loader, "recipe")

    if '-r' in options:
        if values[0] == 'reset':
            result = tagResult(True)

    return result

def is_gamerule(options, values, loader):
    """
    data of type gamerule
    exists in gamerule.json
    -v >> check the next value depend on the gamerule
    """
    gamerule = loader.get_data("gamerule")
    data = gamerule["a_data"]

    if values[0] not in data:
        return tagResult(False, "Gamerule %s doesn't exists" % ('"%s"' % (values[0])))

    result = tagResult(True)
    if '-v' in options and len(values[1::]) > 0:
        datavalues = gamerule["a_value"][data.index(values[0])]
        if datavalues == '@bool':
            result = is_bool([], values[1::])
        elif datavalues == '@int':
            result = is_int([], values[1::])

        result.nbrToSkip += 1

    return result

def is_time(options, values):
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
        return tagResult(False, "Time need to be a number")

    if nbr < 0:
        return tagResult(False, "Time numbers needs to be nul or positive number")

    if need_float:
        if type(nbr) is float:
            return tagResult(True)
        return tagResult(False, "This time need to be a float")

    if type(nbr) is int:
        return tagResult(True)
    return tagResult(False, "This time need to be an int")

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
        return tagResult(False, "Enchantment %s doesn't exists" % ('"%s"' % (values[0])))

    result = tagResult(True)
    if '-v' in options and len(values[1::]) > 0:
        maxLevel = enchant["a_level"][data.index(values[0])]

        if values[1] < 0 or values[1] > maxLevel:
            result = tagResult(False, "This enchant must be between 0 and level %d" % (maxLevel))

        result.nbrToSkip += 1

    return result

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

    result = tagResult(True)

    if values[0] not in blocks:
        if '-d' in options:
            if values[0] not in tags:
                result = tagResult(False, "Block (type) %s doesn't exists" % ('"%s"' % (values[0])))
        else:
            result = tagResult(False, "Block %s doesn't exists" % ('"%s"' % (values[0])))

    if not result.get_result():
        return result

    if '-n' in options and len(nbt) > 0:
        result = is_nbt(nbt)

    return result

def is_item(options, values, loader):
    """
    data of type item
    exists in item.json
    -n >> can be follow by a @nbt
    """
    j_item = loader.get_data("block")
    items = j_item["a_data"]

    values[0] = clean_base(values[0])

    if '-n' in options and '{' in values[0]:
        index = values[0].find('{')
        nbt = values[0][index::]

    result = tagResult(True)
    if values[0] not in blocks:
            result = tagResult(False, "Item %s doesn't exists" % ('"%s"' % (values[0])))

    if not result.get_result():
        return result

    if '-n' in options and len(nbt) > 0:
        result = is_nbt(nbt)

    return result

def is_objective(options, values):
    """
    data of type objectives
    a string with a max length of 16
    """
    if len(values[0]) > 16:
        return tagResult(False, "Objectives has a max length of 16")
    return tagResult(True)

def is_criteria(options, values, loader):
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
        if values[0][index -1] == ':':
            values[0] = values[0][0:index] + values[0][index+10::]

    for c in criteria:
        if '@' in c:
            cut_c = c.split(':')
            cut_v = values[0].split(':')

            if cut_v[0] == cut_c[0]:
                if ':' in cut_v[1]:
                    break
                elif cut_c[1] == 'item' and is_item([], [cut_v[1]], loader):
                    return tagResult(True)
                elif cut_c[1] == 'block' and is_block([], [cut_v[1]], loader):
                    return tagResult(True)
                elif cut_c[1] == 'mob' and is_mob([], [cut_v[1]], loader):
                    return tagResult(True)
                elif cut_c[1] == 'color' and is_color([], [cut_v[1]], loader):
                    return tagResult(True)
                break
        elif values[0] == c:
            return tagResult(True)

    return tagResult(False, "Criteria %s doesn't exists" % ('"%s"' % (values[0])))

def is_zone(options, values):
    """
    data of type zone
    two @coordinates consecutives
    the volume between the 2 point can't exceed 32768 block
    """

    if len(values) < 6:
        return tagResult(False, "Zone need two consécutives coordinates", len(values))

    # check if coordinates are correct
    result = is_coordinate([], values[0:3])
    if not result.get_result():
        return tagResult(False, "Zone first coordinate is incorrect : %s" % (result.get_reason()), result.get_skip_number())

    result = is_coordinate([], values[3::])
    if not result.get_result():
        return tagResult(False, "Zone second coordinate is incorrect : %s" % (result.get_reason()), 3 + result.get_skip_number())

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
        return tagResult(False, "Zone size can't be higher than 32'768 block (suppose local position is 0 0 0)")

    return tagResult(True, "", 5)