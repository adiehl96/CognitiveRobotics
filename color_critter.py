"""Nengo gui entry point"""
from code.models.implausible_model import setup_implausible_model
import grid
import nengo
import numpy as np

MY_MAP = """
#######
#  M  #
# # # #
# #B# #
#G Y R#
#######
"""

ANOTHER_MAP = """
##########
#G#     B#
# # #### #
#M  #    #
### #B## #
#Y     #R#
## #######
#  #    M#
# ## ## ##
#    #R Y#
##########
"""


class Cell(grid.Cell):
    def color(self):
        if self.wall:
            return "black"
        elif self.cellcolor == 1:
            return "green"
        elif self.cellcolor == 2:
            return "red"
        elif self.cellcolor == 3:
            return "blue"
        elif self.cellcolor == 4:
            return "magenta"
        elif self.cellcolor == 5:
            return "yellow"

        return None

    def load(self, char):
        self.cellcolor = 0
        if char == "#":
            self.wall = True

        if char == "G":
            self.cellcolor = 1
        elif char == "R":
            self.cellcolor = 2
        elif char == "B":
            self.cellcolor = 3
        elif char == "M":
            self.cellcolor = 4
        elif char == "Y":
            self.cellcolor = 5


world = grid.World(Cell, map=MY_MAP, directions=4)
body = grid.ContinuousAgent()
world.add(body, x=1, y=2, dir=2)

# Your model might not be a nengo.Netowrk() - SPA is permitted
model = nengo.Network()
setup_implausible_model(model, color_world=world, body=body, grid=grid)
