"""Nengo gui entry point"""
from code.models.naive_model import setup_naive_model
from code.color_world.color_world import ColorWorld
import nengo


MY_MAP = """
#######
#  M  #
# # # #
# #B# #
#G Y R#
#######
"""

ANOTHER_MAP="""
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


color_world = ColorWorld(MY_MAP)
# Your model might not be a nengo.Netowrk() - SPA is permitted
model = nengo.Network()
setup_implausible_model(model, color_world=color_world)
