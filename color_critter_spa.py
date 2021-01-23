import nengo
import nengo.spa as spa
import numpy as np
import grid

D = 32

model = spa.SPA()

vocab = spa.Vocabulary(D)
vocab2 = spa.Vocabulary(D)

mymap = """
#######
#  M  #
# # # #
# #B# #
#G Y R#
#######
"""


class Cell(grid.Cell):
    def color(self):
        if self.wall:
            return "BLACK"
        elif self.cellcolor == 1:
            return "GREEN"
        elif self.cellcolor == 2:
            return "RED"
        elif self.cellcolor == 3:
            return "BLUE"
        elif self.cellcolor == 4:
            return "MAGENTA"
        elif self.cellcolor == 5:
            return "YELLOW"

        return "NONE"

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


world = grid.World(Cell, map=mymap, directions=4)

body = grid.ContinuousAgent()
world.add(body, x=1, y=2, dir=2)


def move(t, x):
    speed, rotation = x
    dt = 0.001
    # Limit max speed and increase max rotation to give agent more chance to
    # move into different directions
    max_speed = 5.0  # previously 20
    max_rotate = 25.0  # previously 10
    min_speed = 0.3

    body.turn(rotation * dt * max_rotate)
    body.go_forward(speed * dt * max_speed if speed > min_speed else 0)


# Three sensors for distance to the walls
def detect(t):
    angles = (np.linspace(-0.5, 0.5, 3) + body.dir) % world.directions
    return [body.detect(d, max_distance=4)[0] for d in angles]


# A basic movement function that just avoids walls based on distance
def movement_func(x):
    turn = x[2] - x[0]
    spd = x[1] - 0.5
    return spd, turn


# Get a list where the index corresponding to a certain color is 1 if the
# agent is currently standing on that color
def color_detect(t):
    return body.cell.color()


with model:
    color_vocab = spa.Vocabulary(D)
    color_vocab.parse("GREEN+RED+BLUE+MAGENTA+YELLOW+NONE")

    binary_vocab = spa.Vocabulary(2)
    binary_vocab.parse("TRUE+FALSE")

    # --- Environment & Radar ---#
    env = grid.GridNode(world, dt=0.005)
    stim_radar = nengo.Node(detect)
    radar = nengo.Ensemble(n_neurons=500, dimensions=3, radius=4)
    nengo.Connection(stim_radar, radar)
    movement = nengo.Node(move, size_in=2)

    # --- Visual Input ---#
    model.color_input = spa.State(D, vocab=color_vocab)
    model.input = spa.Input(color_input=color_detect)

    # --- Color Memory ---#
    model.green_memory = spa.State(
        2, vocab=binary_vocab, feedback=1.0, feedback_synapse=0.001
    )
    model.green_memory_cleanup = spa.AssociativeMemory(
        input_vocab=binary_vocab, wta_output=True, threshold=0.7
    )
    nengo.Connection(
        model.green_memory_cleanup.output, model.green_memory.input, synapse=0.01
    )
    nengo.Connection(
        model.green_memory.output, model.green_memory_cleanup.input, synapse=0.01
    )

    model.red_memory = spa.State(
        2, vocab=binary_vocab, feedback=1.0, feedback_synapse=0.001
    )
    model.red_memory_cleanup = spa.AssociativeMemory(
        input_vocab=binary_vocab, wta_output=True, threshold=0.7
    )
    nengo.Connection(
        model.red_memory_cleanup.output, model.red_memory.input, synapse=0.01
    )
    nengo.Connection(
        model.red_memory.output, model.red_memory_cleanup.input, synapse=0.01
    )

    model.blue_memory = spa.State(
        2, vocab=binary_vocab, feedback=1.0, feedback_synapse=0.001
    )
    model.blue_memory_cleanup = spa.AssociativeMemory(
        input_vocab=binary_vocab, wta_output=True, threshold=0.7
    )
    nengo.Connection(
        model.blue_memory_cleanup.output, model.blue_memory.input, synapse=0.01
    )
    nengo.Connection(
        model.blue_memory.output, model.blue_memory_cleanup.input, synapse=0.01
    )

    model.magenta_memory = spa.State(
        2, vocab=binary_vocab, feedback=1.0, feedback_synapse=0.001
    )
    model.magenta_memory_cleanup = spa.AssociativeMemory(
        input_vocab=binary_vocab, wta_output=True, threshold=0.7
    )
    nengo.Connection(
        model.magenta_memory_cleanup.output, model.magenta_memory.input, synapse=0.01
    )
    nengo.Connection(
        model.magenta_memory.output, model.magenta_memory_cleanup.input, synapse=0.01
    )

    model.yellow_memory = spa.State(
        2, vocab=binary_vocab, feedback=1.0, feedback_synapse=0.001
    )
    model.yellow_memory_cleanup = spa.AssociativeMemory(
        input_vocab=binary_vocab, wta_output=True, threshold=0.7
    )
    nengo.Connection(
        model.yellow_memory_cleanup.output, model.yellow_memory.input, synapse=0.01
    )
    nengo.Connection(
        model.yellow_memory.output, model.yellow_memory_cleanup.input, synapse=0.01
    )

    # --- Stop Mechanism ---#
    user_input = nengo.Node([4])
    stop_ens = nengo.Ensemble(1000, 1, radius=1)
    color_pass_through = nengo.Ensemble(1000, 10, radius=1)
    interrupt = nengo.Ensemble(1500, 3, radius=4)
    nengo.Connection(radar, interrupt[0:2], function=movement_func)
    nengo.Connection(interrupt, movement, function=lambda x: (x[0] * x[2], x[1] * x[2]))
    nengo.Connection(stop_ens, interrupt[2], function=lambda x: 0 if x > 0.8 else 1)
    nengo.Connection(user_input, stop_ens, transform=-1)
    nengo.Connection(model.green_memory.output, color_pass_through[0:2])
    nengo.Connection(model.red_memory.output, color_pass_through[2:4])
    nengo.Connection(model.blue_memory.output, color_pass_through[4:6])
    nengo.Connection(model.magenta_memory.output, color_pass_through[6:8])
    nengo.Connection(model.yellow_memory.output, color_pass_through[8:10])
    nengo.Connection(
        color_pass_through[0:2],
        stop_ens,
        function=lambda x: np.dot(x, binary_vocab["TRUE"].v),
    )
    nengo.Connection(
        color_pass_through[2:4],
        stop_ens,
        function=lambda x: np.dot(x, binary_vocab["TRUE"].v),
    )
    nengo.Connection(
        color_pass_through[4:6],
        stop_ens,
        function=lambda x: np.dot(x, binary_vocab["TRUE"].v),
    )
    nengo.Connection(
        color_pass_through[6:8],
        stop_ens,
        function=lambda x: np.dot(x, binary_vocab["TRUE"].v),
    )
    nengo.Connection(
        color_pass_through[8:10],
        stop_ens,
        function=lambda x: np.dot(x, binary_vocab["TRUE"].v),
    )

    actions = spa.Actions(
        "dot(color_input, GREEN) --> green_memory=TRUE",
        "dot(color_input, RED) --> red_memory=TRUE",
        "dot(color_input, BLUE) --> blue_memory=TRUE",
        "dot(color_input, MAGENTA) --> magenta_memory=TRUE",
        "dot(color_input, YELLOW) --> yellow_memory=TRUE",
        "dot(color_input, NONE) --> yellow_memory=0.25*FALSE, magenta_memory=0.25*FALSE",
        "0.5 --> ",
    )

    model.bg = spa.BasalGanglia(actions)
    model.thalamus = spa.Thalamus(model.bg)
