#-------------------------------------------------------------------------------
# Name:        debugger
# Purpose:      can debug a .mcfunction file
#
# Author:      Didier Mathias
#
# Created:     24/12/2022
# Copyright:   (c) Elève 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__)))

import tag as tagCheck
import dataLoader as dl
import result as r

class debug:
    def __init__(self, version):
        self.loader = dl.data(version)
        self.data = self.loader.get_data("commands")
        self.argsCheck = 0

    def text_to_list(self, text):
        """
        transform : '/execute as player run say "comment ça va ?"'
        into : ['execute', 'as', 'player', 'run', 'say', '"comment ça va ?"']
        """
        args = []

        if text[0] == '/':
            text = text[1::]

        newarg = True
        i = 0
        textlen = len(text)
        while i < textlen:
            if newarg:
                args += [""]

            newarg= True

            if text[i] in ['"', '(', '[', '{']:
                to_pass = 1

                args[-1] += text[i]
                i+=1
                while i < textlen and to_pass > 0:
                    args[-1] += text[i]

                    if text[i] in ['"', '(', '[', '{']:
                        to_pass += 1
                    elif text[i] in ['"', ')', ']', '}']:
                        to_pass -= 1

                    i+=1
            elif text[i] != " ":
                args[-1] += text[i]
                newarg = False

            i+=1

        return args

    def check_tag(self, tag, values):
        #determine options
        options = []
        while tag[-2] == "-":
            options += [tag[-2::] + '']
            tag = tag[0:-2]

        # check value
        if tag == "@advancement":
            return tagCheck.is_advancement(options, values, self.loader)
        elif tag == "@attribute":
            return tagCheck.is_attribute(options, values, self.loader)
        elif tag == "@difficulty":
            return tagCheck.is_difficulty(options, values, self.loader)
        elif tag == "@effect":
            return tagCheck.is_effect(options, values, self.loader)
        elif tag == "@enchant":
            return tagCheck.is_enchant(options, values, self.loader)
        elif tag == "@coordinate":
            return tagCheck.is_coordinate(options, values)
        elif tag == "@float":
            return tagCheck.is_float(options, values)
        elif tag == "@gamemode":
            return tagCheck.is_gamemode(options, values, self.loader)
        elif tag == "@int":
            return tagCheck.is_integer(options, values)
        elif tag == "@ip":
            return tagCheck.is_ip(options, values)
        elif tag == "@item":
            return tagCheck.is_item(options, values, self.loader)
        elif tag == "@string":
            return tagCheck.is_string(options, values)
        elif tag == "@uuid":
            return tagCheck.is_uuid(options, values)
        elif tag == "@axis":
            return tagCheck.is_axis(options, values)
        elif tag == "@between":
            return tagCheck.is_between(options, values)
        elif tag == "@dim":
            return tagCheck.is_dimension(options, values, self.loader)
        elif tag == "@rotation":
            return tagCheck.is_rotation(options, values)
        elif tag == "@bool":
            return tagCheck.is_bool(options, values)
        elif tag == "@biome":
            return tagCheck.is_biome(options, values, self.loader)
        elif tag == "@poi":
            return tagCheck.is_poi(options, values, self.loader)
        elif tag == "@structure":
            return tagCheck.is_structure(options, values, self.loader)
        elif tag == "@end":
            return tagCheck.is_end(options, values)
        elif tag == "@particle":
            return tagCheck.is_particle(options, values, self.loader)
        elif tag == "@rgb":
            return tagCheck.is_rgb(options, values)
        elif tag == "@feature":
            return tagCheck.is_feature(options, values, self.loader)
        elif tag == "@source":
            return tagCheck.is_source(options, values, self.loader)
        elif tag == "@position":
            return tagCheck.is_position(options, values, self.loader)
        elif tag == "@mob":
            return tagCheck.is_mob(options, values, self.loader)
        elif tag == "@team":
            return tagCheck.is_team(options, values)
        elif tag == "@slot":
            return tagCheck.is_slot(options, values, self.loader)
        elif tag == "@sound":
            return tagCheck.is_sound(options, values, self.loader)
        elif tag == "@recipe":
            return tagCheck.is_recipe(options, values, self.loader)
        elif tag == "@color":
            return tagCheck.is_color(options, values, self.loader)
        elif tag == "@gamerule":
            return tagCheck.is_gamerule(options, values, self.loader)
        elif tag == "@loot":
            return tagCheck.is_loot(options, values, self.loader)
        elif tag == "@tool":
            return tagCheck.is_tool(options, values, self.loader)
        elif tag == "@time":
            return tagCheck.is_time(options, values)
        elif tag == "@criteria":
            return tagCheck.is_criteria(options, values, self.loader)
        elif tag == "@objective":
            return tagCheck.is_objective(options, values)
        elif tag == "@enchant":
            return tagCheck.is_enchant(options, values, self.loader)
        elif tag == "@block":
            return tagCheck.is_block(options, values, self.loader)
        elif tag == "@zone":
            return tagCheck.is_zone(options, values)

        return tagCheck.tagResult(False, "Type of %s is not defined" %(tag), 0)

    def debug_command(self, command):
        self.argsCheck = 0

        commandList = self.text_to_list(command)
        result = self._debug_v2(commandList) #self._debug(commandList)
        print(result)
        if not result.is_error():
            if command[-1] == ' ':
                result = r.result(True, (len(command)-1, 0), "Syntax Error", "Command can't finish by a space")
            elif len(commandList) > self.argsCheck:
                pos = 0
                for i in range(self.argsCheck):
                    pos += len(commandList[i]) +1
                print(commandList, self.argsCheck)
                result = r.result(True, (pos -1, 0), "Command Error", "Command have too much argument")

        return result

    def get_position(self, pos):
        return (pos, 0)

    def _debug(self, args, index = "null", position = 0):
        subdata = self.data[index]
        name = subdata["name"]

        # check name
        if name != "@null" and name != args[0]:
            return r.result(True, self.get_position(position), "SyntaxError", 'Command "%s" is incorrect' % (args[0]))

        tocheck = 1
        if name == "@null":
            tocheck = 0

        followdata = subdata["next"]
        for subfollow in followdata:
            # check data integrity
            if type(subfollow) != list:
                return r.result(True, self.get_position(-1), "DataError", "File syntax error")

            if tocheck >= len(args):
                newPosition = position
                for i in args:
                    newPosition += len(i) + 1
                return r.result(True, self.get_position(newPosition -1), "CommandError", "Command is incomplete")

            isOptionnal = False

            result = r.result(True, self.get_position(position), "CommandError", "Command don't exist")
            for follow in subfollow:
                # check integrity
                if type(follow) != str:
                    return r.result(True, self.get_position(-1), "DataError", "File data are incompatible")

                # check if optionnal
                if follow[-2::] == "--":
                    follow = follow[0:-2]
                    isOptionnal = True

                if "@" in follow:
                    tagResult = self.check_tag(follow, args[tocheck::])

                    pos = position
                    for i in range(tagResult.get_skip_number() + tocheck):
                        pos += len(args[i]) + 1
                    result.from_tag(tagResult, pos)

                    self.argsCheck += tagResult.get_skip_number() + 1
                    if tagResult.get_result():
                        tocheck += tagResult.get_skip_number()
                        break;
                else:
                    namecheck = self.data[follow]["name"]

                    if args[tocheck] == namecheck or namecheck == "@null":
                        newPosition = position
                        for i in range(tocheck):
                            newPosition += len(args[i]) + 1

                        result = self._debug(args[tocheck::], follow, newPosition)
                        if not result.is_error():
                            self.argsCheck += 1
                            break;

            if result.is_error() and not isOptionnal:
                return result

        return r.result()

    def _debug_v2(self, commandLine, indexData='null', indexCheck=0):
        j_command = self.data[indexData]

        if commandLine[indexCheck] != j_command['name'] and j_command['name'] != '@null':
            return r.result(True, self.get_position(0), "SyntaxError", 'Command "%s" is incorrect' % (commandLine[0]))
        elif commandLine[indexCheck] == j_command['name']:
            indexCheck += 1

        commandNext = j_command['next']

        for i, argument in enumerate(commandNext):
            if type(argument) is not list:
                return r.result(True, self.get_position(-1), "DataError", "File syntax error")

            if indexCheck >= len(commandLine):
                position = 0
                for j in commandLine:
                    position += len(j) + 1

                for arg in commandNext[i::]:
                    for pos in arg:
                        if '--' not in pos:
                            return r.result(True, self.get_position(position -1), "CommandError", "Command is incomplete")
                return r.result()

            argumentOptionnel = False

            pos = 0
            for j in commandLine[:indexCheck]:
                pos += len(j) + 1
            resultat = r.result(True, self.get_position(pos -1), "CommandError", "Command %s don't exist" % ('"%s"' % (commandLine[indexCheck])))

            for possible in argument:
                if type(possible) != str:
                    return r.result(True, self.get_position(-1), "DataError", "File data are incompatible")

                if '--' in possible:
                    possible = possible[0:-2]
                    argumentOptionnel = True

                if possible[0] == '@':
                    tagResultat = self.check_tag(possible, commandLine[indexCheck::])

                    pos = 0
                    for j in commandLine[:indexCheck+1]:
                        pos += len(j) + 1

                    resultat.from_tag(tagResultat, pos -1)

                    if not resultat.is_error():
                        indexCheck += tagResultat.get_skip_number() +1
                        self.argsCheck += tagResultat.get_skip_number() + 1
                else:
                    nomCommande = self.data[possible]['name']

                    if nomCommande == commandLine[indexCheck] or nomCommande == '@null':
                        resultat = self._debug_v2(commandLine, possible, indexCheck)

                        if not resultat.is_error():
                            indexCheck += 1
                            self.argsCheck += 1

                if not resultat.is_error():
                    break

            if not argumentOptionnel and resultat.is_error():
                return resultat

        return resultat


if __name__ == "__main__":
    debugger = debug('1.19.2')
    commands = [
        "/execute run say hello world !",
        "execute as",
        "i am a test",
        "execute as zouge run say hello",
        "locate biome jun",
        "gamerule sendCommandFeedback f",
        "gamerule sendCommandFeedback true ",
        "gamerule sendCommandFeedback true this is an error",
        "fill ~ ~ ~ ~ ~ ~ dirt replace grass",
        "fill ~ ~ ~ ~ ~ ~ dirt",
        "summon chicken ~ ~ ~ {}"
    ]

    print("TEST BEGIN")
    for c in commands:
        print("COMMAND :", c)
        result = debugger.debug_command(c)
        print("-----------------------------------------------")
    print("TEST END")
