#-------------------------------------------------------------------------------
# Name:        dataLoader
# Purpose:     contain all minecraft data for a version give
#
# Author:      Didier Mathis
#
# Created:     24/12/2022
#-------------------------------------------------------------------------------

import json
import os.path as path

class data:
    DATA_PATH = path.join(path.dirname(__file__), 'data')

    def __init__(self, version):
        self.data = {}
        self.version = version
        #self.load_all()

    def set_data_path(self, dirpath):
        self.DATA_PATH = dirpath
        self.data = {}

    def load(self, filename):
        file = open(path.join(self.DATA_PATH, 'command', self.version, '%s.json' %(filename)))
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
