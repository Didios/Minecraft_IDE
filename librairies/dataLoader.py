#-------------------------------------------------------------------------------
# Name:        dataLoader
# Purpose:     contain all minecraft data for a version give
#
# Author:      Elève
#
# Created:     24/12/2022
# Copyright:   (c) Elève 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import json
import os.path as path

class data:
    def __init__(self, version):
        self.data = {}
        self.version = version
        #self.load_all()

    def load(self, filename):
        file = open(path.join(path.dirname(__file__), 'data', self.version, '%s.json' %(filename)))
        self.data[filename] = json.load(file)
        file.close()

    def load_all(self):
        files = [
            "advancement",
            "attribute",
            "biome",
            "block",
            "color",
            "commands",
            "criteria",
            "difficulty",
            "dimension",
            "effect",
            "enchantment",
            "feature",
            "gamemode",
            "gamerule",
            "item",
            "loot",
            "mob",
            "particle",
            "poi",
            "position",
            "recipe",
            "selector",
            "slot",
            "sound",
            "source",
            "structure",
            "tool",
            "nbt"
        ]

        for file in files:
            self.load(file)

    def get_data(self, dataname):
        if dataname not in self.data.keys():
            self.load(dataname)

        return self.data[dataname]

    def set_version(self, newVersion):
        self.version = newVersion
        self.load_all()
