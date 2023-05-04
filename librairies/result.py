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

class Result:
    def __init__(self, error: bool = False, position: tuple[int, int] = (0, 0), type: str = "", desc: str = "") -> None:
        """
        Create a Result for a debug
        Args:
            error (): is the result an error, by default False
            position (): position in text/file, use if error, by default (0, 0)
            type (): type/title, by default ""
            desc (): description, by default ""
        """
        self.error = error
        self.position = position
        self.type = type
        self.desc = desc

    def get_position(self) -> tuple[int, int]:
        """ Get position of the result """
        return self.position

    def is_error(self) -> bool:
        """ is the result an error """
        return self.error

    def position_add(self, x: int = 0, y: int = 0) -> None:
        """
        Increment position to x and y
        Args:
            x (): x
            y (): y
        """
        self.position = (self.position[0] + x, self.position[1] + y)

    def set_position(self, x=None, y=None):
        if x != None and y != None:
            self.position = (x, y)
        elif x != None:
            self.position = (x, self.position[1])
        elif y != None:
            self.position = (self.position[0], y)

    def set_desc(self, desc):
        self.desc = desc

    def __str__(self):
        text = ""

        if self.error:
            text = "Error on line %i at position %i >> %s : %s" % (self.position[1], self.position[0], self.type, self.desc)
        else:
            text = "No Error"

        return text

    def __repr__(self):
        return f'Error: {self.error}, Position: {self.position}, Type: {self.type}, Description: {self.desc}'

if __name__ == '__main__':
    r = result(True, (0, 1), "SyntaxError", "this is an error test ")
    print(r)
