#-------------------------------------------------------------------------------
# Name:        result
# Purpose:      result of a line after debug
#
# Author:      Didier Mathias
#
# Created:     01/01/2023
# Copyright:   (c) Elève 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from tag import tagResult

class result:
    def __init__(self, error=False, position=(0, 0), type="", description=""):
        self.error = error # True-False
        self.position = position # (x, y)
        self.type = type # Syntax, Name etc.
        self.desc = description

    def get_position(self):
        return self.position

    def is_error(self):
        return self.error

    def set_position(self, x=None, y=None):
        if x != None and y != None:
            self.position = (x, y)
        elif x != None:
            self.position = (x, self.position[1])
        elif y != None:
            self.position = (self.position[0], y)

    def from_tag(self, result, position):
        self.error = not result.get_result()
        self.type = "ValueError"
        self.desc = result.get_reason()
        self.position = (position, 0)

    def __str__(self):
        text = ""

        if self.error:
            text = "Error on line %i at position %i >> %s : %s" % (self.position[1], self.position[0], self.type, self.desc)
        else:
            text = "No Error"

        return text

if __name__ == '__main__':
    r = result(True, (0, 1), "SyntaxError", "this is an error test ")
    print(r)
