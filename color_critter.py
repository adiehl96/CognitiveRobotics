"""Nengo gui entry point"""
from code.models.implausible_model import setup_implausible_model
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


color_world = ColorWorld(ANOTHER_MAP)
# Your model might not be a nengo.Netowrk() - SPA is permitted
model = nengo.Network()
setup_implausible_model(model, color_world=color_world)
