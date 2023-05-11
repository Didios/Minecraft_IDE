# -------------------------------------------------------------------------------
# Name:        debugger
# Purpose:      can debug a .mcfunction file
#
# Author:      Didier Mathias
# Created:     24/12/2022
# -------------------------------------------------------------------------------

import os.path as path
import sys
sys.path.append(path.join(path.dirname(__file__)))

from tag import check_tag
from result import Result
from dataLoader import data as dl


class debug:
    def __init__(self, version):
        self.loader = dl(version)
        self.data = self.loader.get_data("commands")
        self.argsCheck = 0

    def set_data_path(self, dirpath):
        dl.set_data_path(dl, dirpath)

    def text_to_list(self, text):
        """
        transform : '/execute as player run say "comment ça va ?"'
        into : ['execute', 'as', 'player', 'run', 'say', '"comment ça va ?"']
        """
        args = []

        if text[0] == '/':
            text = text[1::]

        newarg = True;
        i = 0
        textlen = len(text)
        while i < textlen:
            if newarg:
                args += [""]

            newarg = True

            if text[i] in ['"', '(', '[', '{']:
                to_pass = 1

                args[-1] += text[i]
                i += 1
                while i < textlen and to_pass > 0:
                    args[-1] += text[i]

                    if text[i] in ['"', '(', '[', '{']:
                        to_pass += 1
                    elif text[i] in ['"', ')', ']', '}']:
                        to_pass -= 1

                    i += 1
            elif text[i] != " ":
                args[-1] += text[i]
                newarg = False

            i += 1

        return args

    def debug_command(self, command):
        self.argsCheck = 0

        commandList = self.text_to_list(command)
        r = self._debug_v2(commandList)
        if not r.is_error():
            if command[-1] == ' ':
                r = Result(error=True, position=(len(command) - 1, 0),
                           type="Syntax Error", desc="Command can't finish by a space")
            elif len(commandList) > self.argsCheck:
                pos = 0
                for i in range(self.argsCheck):
                    pos += len(commandList[i]) + 1
                r = Result(error=True, position=(pos - 1, 0),
                           type="Command Error", desc="Command have too much argument")
        return r

    def _debug_v2(self, commandLine: list[str], indexData: str = 'null', indexCheck: int = 0) -> Result:
        """
        Debug a command minecraft on list form without space
        Args:
            commandLine (): command to debug
            indexData (): index of command to check in files
            indexCheck (): index of progression in commandLine

        Returns:
            result of the operation
        """
        # get command data
        j_command = self.data[indexData]

        # check name of command
        if commandLine[indexCheck] != j_command['name'] and j_command['name'] != '@null':
            return Result(error=True, type="SyntaxError", desc=f'Command "{commandLine[0]}" is incorrect')
        elif commandLine[indexCheck] == j_command['name']:
            indexCheck += 1

        # get follow data
        commandNext = j_command['next']

        # default result
        resultat = Result()
        for i, argument in enumerate(commandNext):
            # check file integrity
            if type(argument) is not list:
                return Result(error=True, position=(-1, 0),
                              type="DataError", desc="File syntax error")

            # check end command
            if indexCheck >= len(commandLine):
                position = 0
                for j in commandLine:
                    position += len(j) + 1

                # check if no required follow data, raise error if yes, end programm if no
                for arg in commandNext[i::]:
                    for pos in arg:
                        if '--' not in pos:
                            return Result(error=True, position=(position - 1, 0),
                                          type="CommandError", desc="Command is incomplete")
                return Result()

            argumentOptionnel = False

            # default error
            pos = 0
            for j in commandLine[:indexCheck]:
                pos += len(j) + 1
            resultat = Result(error=True, position=(pos - 1, 0),
                              type="CommandError", desc=f"Command {commandLine[indexCheck]} don't exist")

            # check following argument
            for possible in argument:
                # check data integrity
                if type(possible) != str:
                    return Result(error=True, position=(-1, 0),
                                  type="DataError", desc="File data are incompatible")

                # check if argument optional
                if '--' in possible:
                    possible = possible[0:-2]
                    argumentOptionnel = True

                # check if argument is tag or command
                if possible[0] == '@':
                    # get tag debug
                    resultat = check_tag(possible, commandLine[indexCheck::], self.loader)

                    i = indexCheck

                    # increment index in commandLine
                    if not resultat.is_error():
                        indexCheck += resultat.get_position()[0] + 1
                        self.argsCheck += resultat.get_position()[0] + 1

                    # set position of resultat
                    pos = 0
                    for j in commandLine[:i + 1]:
                        pos += len(j) + 1
                    resultat.position_add(pos - 1)
                else:
                    # get next command name
                    nomCommande = self.data[possible]['name']

                    # check next comand name
                    if nomCommande == commandLine[indexCheck] or nomCommande == '@null':
                        # get debug
                        resultat = self._debug_v2(commandLine, possible, indexCheck)

                        # if no error continue
                        if not resultat.is_error():
                            indexCheck += 1
                            self.argsCheck += 1

                # if argument is ok, continue debug
                if not resultat.is_error():
                    break

            # if get error and argument not optional, raise the error
            if resultat.is_error() and not argumentOptionnel:
                return resultat

        return resultat


if __name__ == "__main__":
    debugger = debug('1.19.2')
    commands = [
        "/execute run say hello world !",
        "execute as",
        "i am an error test",
        "execute as zouge run say hello",
        "locate biome jun",
        "gamerule sendCommandFeedback f",
        "gamerule sendCommandFeedback true ",
        "gamerule sendCommandFeedback true this is an error",
        "fill ~ ~ ~ ~ ~ ~ dirt replace grass",
        "fill ~ ~ ~ ~ ~ ~ dirt",
        "summon chicken ~ ~ ~ {}",
        "tag @p add player",
        'summon chicken ~ ~ ~ {NoGravity: 1b, Invulnerable:1b, PersistenceRequired: 1b, NoAI: 1b, CanPickUpLoot: 0b, Tags: ["player"]}',
        "team add 100",
        "team modify 100 collisionRule never",
    ]

    print("TEST BEGIN")
    for c in commands:
        print("COMMAND :", c)
        print("RESULT: ", debugger.debug_command(c))
        print("-----------------------------------------------")
    print("TEST END")
