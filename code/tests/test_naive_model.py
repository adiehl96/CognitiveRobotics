from code.models.naive_model import setup_naive_model
from code.color_world.color_world import ColorWorld
import nengo


def test_naive_model():
    my_map = """
    #######
    #  M  #
    # # # #
    # #B# #
    #G Y R#
    #######
    """

    color_world = ColorWorld(my_map)
    print(color_world.agent)
    # Your model might not be a nengo.Netowrk() - SPA is permitted
    model = nengo.Network()
    setup_naive_model(model, color_world=color_world)
    model_objects = setup_naive_model(model, color_world=color_world)

    with model:
        _radar_p = nengo.Probe(model_objects[3], synapse=0.01)

    with nengo.Simulator(model) as sim:
        sim.run(1)
