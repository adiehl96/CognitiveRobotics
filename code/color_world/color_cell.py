"""
This module defines the content of the cells of a world
and the agent that acts in it.
"""
from code.color_world.grid_world.cell import Cell


class ColorCell(Cell):
    """Define the information contained in the cells a world is made of."""

    def __init__(self):
        super().__init__()
        self.cellcolor = 0
        self.colordict = {
            0: "black",
            1: "green",
            2: "red",
            3: "blue",
            4: "magenta",
            5: "yellow",
        }

    def color(self):
        """Returns a color corresponding to the state of the cell"""
        if self.wall:
            return self.colordict[self.cellcolor]
        elif self.cellcolor:
            return self.colordict[self.cellcolor]
        else:
            return None

    def load(self, char):
        """Set the color of this particular cell"""
        if char == "#":
            self.wall = True
            self.cellcolor = 0
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
