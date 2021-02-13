import grid
import nengo
import numpy as np

mymap = """
#######
#  M  #
# # # #
# #B# #
#G Y R#
#######
"""

theMap = """
##########
#G#     B#
# # #### #
#M  #    #
### #B## #
#Y     #R#
## #######
#  #    M#
# ## ## ##
#G   #R Y#
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


world = grid.World(Cell, map=theMap, directions=4)

body = grid.ContinuousAgent()
world.add(body, x=1, y=2, dir=2)


def move(t, x):
    speed, rotation = x
    dt = 0.001
    # Limit max speed and increase max rotation to give agent more chance to
    # move into different directions
    max_speed = 5.0  # previously 20
    min_speed = 0.01  # minimum speed
    max_rotate = 25.0  # previously 10
    body.turn(rotation * dt * max_rotate)
    body.go_forward(speed * dt * max_speed if abs(speed) > min_speed else 0)


# Three sensors for distance to the walls
def detect(t):
    directions = (np.linspace(-0.5, 0.5, 3) + body.dir) % world.directions
    return [body.detect(d, max_distance=4)[0] for d in directions]


# Get a list where the index corresponding to a certain color is 1 if the
# agent is currently standing on that color
def color_detect(t):
    out = [0] * 6
    out[body.cell.cellcolor] = 1
    return out


model = nengo.Network()
with model:
    env = grid.GridNode(world, dt=0.005)

    stim_radar = nengo.Node(detect)
    rotation = nengo.Ensemble(n_neurons=500, dimensions=2, radius=4)
    speed = nengo.Ensemble(n_neurons=500, dimensions=1, radius=4)
    nengo.Connection(stim_radar[1], speed)
    nengo.Connection(stim_radar[0], rotation[0])
    nengo.Connection(stim_radar[2], rotation[1])

    # Implement a stopper in between that routes the signal from radar to
    # movement, but stops on a given signal from stop_ens
    interrupt = nengo.Ensemble(500, 2, radius=4)
    nengo.Connection(speed, interrupt[0], function=lambda x: x - 0.5)
    nengo.Connection(rotation, interrupt[1], function=lambda x: x[1] - x[0])

    # the movement function is only driven by information from the radar
    movement = nengo.Node(move, size_in=2)
    nengo.Connection(interrupt, movement)

    current_color = nengo.Node(color_detect)

    # Integrators for the individual colors
    green_integrator = nengo.Ensemble(n_neurons=200, dimensions=1, radius=0.8)
    blue_integrator = nengo.Ensemble(n_neurons=200, dimensions=1, radius=0.8)
    red_integrator = nengo.Ensemble(n_neurons=200, dimensions=1, radius=0.8)
    yellow_integrator = nengo.Ensemble(n_neurons=200, dimensions=1, radius=0.8)
    magenta_integrator = nengo.Ensemble(n_neurons=200, dimensions=1, radius=0.8)

    # Recurrent connections
    tau = 0.1
    nengo.Connection(green_integrator, green_integrator, synapse=tau)
    nengo.Connection(blue_integrator, blue_integrator, synapse=tau)
    nengo.Connection(red_integrator, red_integrator, synapse=tau)
    nengo.Connection(yellow_integrator, yellow_integrator, synapse=tau)
    nengo.Connection(magenta_integrator, magenta_integrator, synapse=tau)

    # Connect colors to the integrators
    mau = 10
    nengo.Connection(current_color[1], green_integrator, transform=mau, synapse=tau)
    nengo.Connection(current_color[2], red_integrator, transform=mau, synapse=tau)
    nengo.Connection(current_color[3], blue_integrator, transform=mau, synapse=tau)
    nengo.Connection(current_color[4], magenta_integrator, transform=mau, synapse=tau)
    nengo.Connection(current_color[5], yellow_integrator, transform=mau, synapse=tau)

    stop_ens = nengo.Ensemble(1000, 1, radius=5)

    nengo.Connection(
        green_integrator,
        stop_ens,
        synapse=tau,
        function=lambda x: 0.9 if x > 0.7 else 0,
    )
    nengo.Connection(
        red_integrator, stop_ens, synapse=tau, function=lambda x: 0.9 if x > 0.7 else 0
    )
    nengo.Connection(
        blue_integrator, stop_ens, synapse=tau, function=lambda x: 0.9 if x > 0.7 else 0
    )
    nengo.Connection(
        magenta_integrator,
        stop_ens,
        synapse=tau,
        function=lambda x: 0.9 if x > 0.7 else 0,
    )
    nengo.Connection(
        yellow_integrator,
        stop_ens,
        synapse=tau,
        function=lambda x: 0.9 if x > 0.7 else 0,
    )

    nengo.Connection(
        stop_ens,
        interrupt.neurons,
        function=lambda x: 1 if x > 0.7 else 0,
        transform=[[-3.5]] * 500,
    )

    # Input the number of colors
    input_node = nengo.Node([5])
    nengo.Connection(input_node, stop_ens, transform=-1)

    continuous_one = nengo.Node([1])
    nengo.Connection(continuous_one, stop_ens)
