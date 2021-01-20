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


def move(t, x):
    speed, rotation, dont = x
    # Cheap and implausible check if accumulated input exceeds number
    # of different colors specified
    if dont > 4.5:
        return
    dt = 0.001
    # Limit max speed and increase max rotation to give agent more chance to
    # move into different directions
    max_speed = 10.0  # previously 20
    max_rotate = 25.0  # previously 10
    body.turn(rotation * dt * max_rotate)
    body.go_forward(speed * dt * max_speed)


# A basic movement function that just avoids walls based
def movement_func(x):
    turn = x[2] - x[0]
    spd = x[1] - 0.5
    return spd, turn


# Three sensors for distance to the walls
def detect(t):
    angles = (np.linspace(-0.5, 0.5, 3) + body.dir) % world.directions
    return [body.detect(d, max_distance=4)[0] for d in angles]


# Get a list where the index corresponding to a certain color is 1 if the
# agent is currently standing on that color
def color_detect(t):
    out = [0] * 6
    out[body.cell.cellcolor] = 1
    return out


with model:
    env = grid.GridNode(world, dt=0.005)

    stim_radar = nengo.Node(detect)

    radar = nengo.Ensemble(n_neurons=500, dimensions=3, radius=4)
    nengo.Connection(stim_radar, radar)

    # The movement function is driven by information from the radar,
    # but also gets a signal from the accumulator later on in order to
    # stop moving when all colors are seen
    movement = nengo.Node(move, size_in=3)
    nengo.Connection(radar, movement[0:2], function=movement_func)

    # Create a node that detects which of the 5 different colors is present
    current_color = nengo.Node(color_detect)

    # For the individual colors, create an integrator that gets input
    # from the current_color node and stays at the activated value once
    # a color is received
    green_integrator = nengo.Ensemble(n_neurons=200, dimensions=1)
    blue_integrator = nengo.Ensemble(n_neurons=200, dimensions=1)
    red_integrator = nengo.Ensemble(n_neurons=200, dimensions=1)
    yellow_integrator = nengo.Ensemble(n_neurons=200, dimensions=1)
    magenta_integrator = nengo.Ensemble(n_neurons=200, dimensions=1)

    # Recurrent connections
    tau = 0.1
    nengo.Connection(green_integrator, green_integrator, synapse=tau)
    nengo.Connection(blue_integrator, blue_integrator, synapse=tau)
    nengo.Connection(red_integrator, red_integrator, synapse=tau)
    nengo.Connection(yellow_integrator, yellow_integrator, synapse=tau)
    nengo.Connection(magenta_integrator, magenta_integrator, synapse=tau)

    # Connect colors to the integrators
    mau = 10  # high transform to respond also to quick passes over a color tile
    nengo.Connection(current_color[1], green_integrator, transform=mau, synapse=tau)
    nengo.Connection(current_color[2], red_integrator, transform=mau, synapse=tau)
    nengo.Connection(current_color[3], blue_integrator, transform=mau, synapse=tau)
    nengo.Connection(current_color[4], magenta_integrator, transform=mau, synapse=tau)
    nengo.Connection(current_color[5], yellow_integrator, transform=mau, synapse=tau)

    # Ensemble that accumulates the inputs from the color integrator
    accumulator = nengo.Ensemble(200, 1, radius=6)

    pau = 1
    nengo.Connection(green_integrator, accumulator, transform=pau, synapse=tau)
    nengo.Connection(red_integrator, accumulator, transform=pau, synapse=tau)
    nengo.Connection(blue_integrator, accumulator, transform=pau, synapse=tau)
    nengo.Connection(magenta_integrator, accumulator, transform=pau, synapse=tau)
    nengo.Connection(yellow_integrator, accumulator, transform=pau, synapse=tau)

    # Connect the accumulated signal to the movement node for inhibition
    nengo.Connection(accumulator, movement[2])
