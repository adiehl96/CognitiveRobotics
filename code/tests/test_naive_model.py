"""Module containing tests for the naive model"""
from code.models.naive_model import setup_naive_model
from code.color_world.color_world import ColorWorld
import nengo


def test_naive_model():
    """Test whether the naive model actually compiles"""

    another_map = """
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

    color_world = ColorWorld(another_map)
    model = nengo.Network()
    model_objects = setup_naive_model(model, color_world=color_world)

    with model:
        _radar_p = nengo.Probe(model_objects[3], synapse=0.01)

    with nengo.Simulator(model) as sim:
        sim.run(1)
