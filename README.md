# Minecraft_IDE
This project aims to create an IDE entirely dedicated to the development of Minecraft datapacks from A to Z

A datapack will here be refered has a project.

Final posibility in the IDE:
- create new project
- open and modify an existing project
- debug any .mcfunction, .mcmeta or .json file
- add or modify any .png file in the project


The big part is on the file debugging sides, it will be an editor like notepad++ with some code color to help comprehension.
The editor should be in the capability of read and determine if the file contain an error, if it does, it must display the position of the error and why does it occurs.
A simple paint should do the trick for the .png part

Data used for debugging must be located in "librairies/data/[version]/".
Data present are:
- commands.json contain all possible command composition
- other datas contains different information to help debugging some tag present in commands.json

Tags are represented with an "@" in the beginning. 
Tags can be optionnal (see with "--") and present some options like "-l".
All tags and options are described in the "prototype/Tag.xlsx" file.
  In this file, green part have already been processed, yellow are in progress and white are not started yet
