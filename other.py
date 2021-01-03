"""Nengo gui entry point"""
import nengo


model = nengo.Network()

with model:
    stim = nengo.Node([0, 0])
    light = nengo.Node([0])

    agent = nengo.Ensemble(n_neurons=500, dimensions=3)
    foodloc = nengo.Ensemble(n_neurons=500, dimensions=2)
    lightloc = nengo.Ensemble(n_neurons=500, dimensions=1)

    nengo.Connection(stim, foodloc)
    nengo.Connection(foodloc, agent, synapse=5)
    nengo.Connection(light, lightloc)
