import tkinter as tk
from tkinter import *
my_w = tk.Tk()
my_w.geometry("410x200")  # Size of the window

#config
my_w.columnconfigure(0, weight=0)
my_w.columnconfigure(1, weight=3)
my_w.columnconfigure(2, weight=0)

my_w.rowconfigure(0, weight=4)
my_w.rowconfigure(1, weight=0)
my_w.rowconfigure(2, weight=2)
my_w.rowconfigure(3, weight=0)

# frame
frame_left_top = tk.Frame(my_w,bg='red', width=30)
frame_middle_top = tk.Frame(my_w,bg='yellow')
frame_left_center = tk.Frame(my_w,bg='lightgreen')

frame_scrolly_top = tk.Frame(my_w,bg='blue', width=10)
frame_scrolly_center = tk.Frame(my_w,bg='lightblue', width=10)
frame_scrollx_top = tk.Frame(my_w,bg='green', height=10)
frame_scrollx_center = tk.Frame(my_w,bg='pink', height=10)


# grid
frame_left_top.grid(row=0,column=0,sticky='ns')
frame_middle_top.grid(row=0,column=1,sticky='nsew')

frame_left_center.grid(row=2,column=0,columnspan=2,sticky='nsew')

frame_scrolly_top.grid(row=0,column=2,sticky='ns')
frame_scrolly_center.grid(row=2,column=2,sticky='ns')

frame_scrollx_top.grid(row=1,column=0,columnspan=3,sticky='ew')
frame_scrollx_center.grid(row=3,column=0,columnspan=3,sticky='ew')

# create
my_w.mainloop()  # Keep the window open