# This is a sample Python script.
import keyboard # simulate keyboard input
import clipboard # get content form clipboard
from pynput.keyboard import Key, Controller # to press ctrl+shift+left
import pyautogui
from time import sleep # wait between action
import pydirectinput

import pynput as pynput


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def get_data():
    # be ready to automation
    print("WAIT")
    sleep(5)
    print("GO")

    i = 1
    text = "["
    last = ""
    very_last = clipboard.paste()
    print("Last =", very_last)
    while last != very_last:
        print("Item number", i)
        # go to next item
        for j in range(i):
            click("tab")
            sleep(0.1)

        # go to begin of item
        #click("ctrl+left")
        #sleep(0.1)

        # select item
        keyboard.press("ctrl+shift")
        click("left")
        keyboard.release("ctrl+shift")
        sleep(0.1)

        # cut item >> add it to clipboard
        click("ctrl+x")
        last = clipboard.paste()

        # increment data
        text += '"' + last + '",'

        # ready for next loop
        i += 1
        sleep(0.1)

    # end data
    text = text[0:-1]
    text += "]"

    # print data
    print("Data:\n", text)

def test():
    print("test begin")
    sleep(3)

    pydirectinput.keyDown('a')
    sleep(1)
    pydirectinput.keyUp('a')

    keyboard.write("minecraft:truc")
    pyautogui.write("test")

    print("test end")


class scrap:
    def __init__(self):
        self.data = '{\n\t"a_data": [\n'
        self.previous = ""
        self.repetition = 1780#1
        self.continue_loop = True

    def copy_clipboard(self, event=""):
        current = clipboard.paste()
        if current != self.previous:
            print('"%s",' % (current))
            self.data +=  '\t\t"%s",\n' % (current)
            self.previous = current

    def click(self, hotkey):
        keyboard.press(hotkey)
        sleep(0.01)
        keyboard.release(hotkey)

    def save_data(self, event=""):
        self.data = self.data[0:-2] + '\n\t]\n}'

        f = open("data.txt", "w")
        f.write(self.data)
        f.close()
        print("Data has been saved !")

    def action(self, event=""):
        for j in range(self.repetition):
            self.click("tab")
            sleep(0.02)
            if not self.continue_loop:
                break

        self.repetition += 1

    def selection(self, event=""):
        board = Controller()
        board.press(Key.ctrl )
        board.press(Key.shift )
        board.press(Key.left )
        sleep(0.1)
        board.release(Key.ctrl )
        board.release(Key.left )
        board.release(Key.shift )

        # cut item >> add it to clipboard
        self.click("ctrl+x")
        sleep(0.1)

    def stop(self, event=""):
        self.continue_loop = False
        keyboard.remove_all_hotkeys()

    def start(self, event=""):
        while self.continue_loop:
            self.action()
            sleep(0.01)
            self.selection()
            sleep(0.01)
            self.copy_clipboard()
            sleep(0.01)

if __name__ == '__main__':
    print_hi('PyCharm')

    s = scrap()

    from tkinter import *

    root = Tk()

    keyboard.add_hotkey("ctrl+b", s.start)
    Button(root, width=50, text='STOP', command=s.stop).pack()
    Button(root, width=50, text='SAVE', command=s.save_data).pack()

    root.mainloop()

    keyboard.remove_all_hotkeys()