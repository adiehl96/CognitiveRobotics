from code.color_world.grid_world.continuous_agent import ContinuousAgent
from code.color_world.color_cell import ColorCell
from code.color_world.grid_world.world import World


class ColorWorld:
    def __init__(self, map):
        self.world = World(cell=ColorCell, map=map, directions=4)
        self.agent = ContinuousAgent()
        self.world.add(self.agent, x=1, y=2, dir=2)
