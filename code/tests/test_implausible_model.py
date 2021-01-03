"""Module containing tests for the implausible model"""
from code.models.implausible_model import setup_implausible_model
from code.color_world.color_world import ColorWorld
import nengo


def test_implausible_model():
    """Test whether the implausible model actually compiles"""
    my_map = """
    #######
    #  M  #
    # # # #
    # #B# #
    #G Y R#
    #######
    """

    color_world = ColorWorld(my_map)
    model = nengo.Network()
    model_objects = setup_implausible_model(model, color_world=color_world)

    with model:
        _blue_integrator_p = nengo.Probe(model_objects[0], synapse=0.01)

    with nengo.Simulator(model) as sim:
        sim.run(1)
