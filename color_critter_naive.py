"""Nengo gui entry point"""
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


def move(_time, current_movement):
    speed, rotation = current_movement
    delta_t = 0.001
    max_speed = 20.0
    max_rotate = 10.0
    body.turn(rotation * delta_t * max_rotate)
    body.go_forward(speed * delta_t * max_speed)


# Three sensors for distance to the walls
def detect(_t):
    angles = (np.array([-0.5, 0.0, 0.5]) + body.dir) % world.directions
    return [body.detect(d, max_distance=4)[0] for d in angles]


# a basic movement function that just avoids walls based
def movement_func(x):
    turn = x[2] - x[0]
    speed = x[1] - 0.5
    return speed, turn


# if you wanted to know the position in the world, this is how to do it
# The first two dimensions are X,Y coordinates, the third is the orientation
# (plotting XY value shows the first two dimensions)
def position_func(_t):
    return (
        body.x / world.width * 2 - 1,
        1 - body.y / world.height * 2,
        body.dir / world.directions,
    )


with model:
    env = grid.GridNode(world, dt=0.005)

    movement = nengo.Node(move, size_in=2, label="movement")

    stim_radar = nengo.Node(detect, label="stim_radar")

    radar = nengo.Ensemble(n_neurons=500, dimensions=3, radius=4)
    nengo.Connection(stim_radar, radar)
    # the movement function is only driven by information from the
    # radar
    nengo.Connection(radar, movement, function=movement_func)

    position = nengo.Node(position_func, label="position")

    # This node returns the color of the cell currently occupied.
    # Note that you might want to transform this into
    # something else (see the assignment)
    current_color = nengo.Node(lambda t: body.cell.cellcolor, label="current_color")
