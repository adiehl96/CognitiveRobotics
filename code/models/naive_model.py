from code.color_world.grid_world.grid_node import GridNode
import nengo
import numpy as np


def setup_naive_model(model, color_world):
    body = color_world.agent
    color_world = color_world.world

    def move(_time, current_movement):
        speed, rotation = current_movement
        delta_t = 0.001
        max_speed = 20.0
        max_rotate = 10.0
        body.turn(rotation * delta_t * max_rotate)
        body.go_forward(speed * delta_t * max_speed)

    # Three sensors for distance to the walls
    def detect(_t):
        angles = (
            np.array([-0.5, 0.0, 0.5]) + body.dir
        ) % color_world.directions
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
            body.x / color_world.width * 2 - 1,
            1 - body.y / color_world.height * 2,
            body.dir / color_world.directions,
        )

    with model:
        env = GridNode(color_world, delta_t=0.005, label="environment")

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
        current_color = nengo.Node(
            lambda t: body.cell.cellcolor, label="current_color"
        )

    return env, movement, stim_radar, radar, position, current_color
