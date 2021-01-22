import grid
import nengo
import numpy as np 

mymap="""
#######
#  M  #
# # # #
# #B# #
#G Y R#
#######
"""

theMap="""
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

class Cell(grid.Cell):

    def color(self):
        if self.wall:
            return 'black'
        elif self.cellcolor == 1:
            return 'green'
        elif self.cellcolor == 2:
            return 'red'
        elif self.cellcolor == 3:
            return 'blue'
        elif self.cellcolor == 4:
            return 'magenta'
        elif self.cellcolor == 5:
            return 'yellow'
             
        return None

    def load(self, char):
        self.cellcolor = 0
        if char == '#':
            self.wall = True
            
        if char == 'G':
            self.cellcolor = 1
        elif char == 'R':
            self.cellcolor = 2
        elif char == 'B':
            self.cellcolor = 3
        elif char == 'M':
            self.cellcolor = 4
        elif char == 'Y':
            self.cellcolor = 5
    
            
world = grid.World(Cell, map=mymap, directions=4)

body = grid.ContinuousAgent()
world.add(body, x=1, y=2, dir=2)


def move(t, x):
    speed, rotation = x
    dt = 0.001
    # Limit max speed and increase max rotation to give agent more chance to 
    # move into different directions
    max_speed = 5.0 # previously 20
    max_rotate = 25.0 # previously 10
    body.turn(rotation * dt * max_rotate)
    body.go_forward(speed * dt * max_speed)

# Three sensors for distance to the walls
def detect(t):
    angles = (np.linspace(-0.5, 0.5, 3) + body.dir) % world.directions
    return [body.detect(d, max_distance=4)[0] for d in angles]

# A basic movement function that just avoids walls based on distance
def movement_func(x):
    turn = x[2] - x[0]
    spd = x[1] - 0.5
    return spd, turn

def move_with_interrupt(x):
    spd, turn, dont = x
    if dont > 0.8:
        return 0, 0
    else:
        return spd, turn

#if you wanted to know the position in the world, this is how to do it
#The first two dimensions are X,Y coordinates, the third is the orientation
#(plotting XY value shows the first two dimensions)
def position_func(t):
    return body.x / world.width * 2 - 1, 1 - body.y/world.height * 2, body.dir / world.directions

# Get a list where the index corresponding to a certain color is 1 if the
# agent is currently standing on that color
def color_detect(t):
    out = [0]*6
    out[body.cell.cellcolor] = 1
    return out

model = nengo.Network()
with model:
    env = grid.GridNode(world, dt=0.005)

    stim_radar = nengo.Node(detect)
    
    radar = nengo.Ensemble(n_neurons=500, dimensions=3, radius=4)
    nengo.Connection(stim_radar, radar)

    # Implement a stopper in between that routes the signal from radar to 
    # movement, but stops on a given signal from stop_ens
    interrupt = nengo.Ensemble(500, 3, radius=4)
    nengo.Connection(radar, interrupt[0:2], function=movement_func)
        
    #the movement function is only driven by information from the radar
    movement = nengo.Node(move, size_in=2)
    nengo.Connection(interrupt, movement, function=move_with_interrupt)  

    position = nengo.Node(position_func)

    current_color = nengo.Node(color_detect)
    
    # Integrators for the individual colors
    green_integrator = nengo.Ensemble(n_neurons=200, dimensions=1)
    blue_integrator = nengo.Ensemble(n_neurons=200, dimensions=1)
    red_integrator = nengo.Ensemble(n_neurons=200, dimensions=1)
    yellow_integrator = nengo.Ensemble(n_neurons=200, dimensions=1)
    magenta_integrator = nengo.Ensemble(n_neurons=200, dimensions=1)

    # Recurrent connections
    tau = 0.1
    nengo.Connection(green_integrator, green_integrator, synapse=tau)
    nengo.Connection(blue_integrator, blue_integrator, synapse=tau)
    nengo.Connection(red_integrator, red_integrator, synapse=tau)
    nengo.Connection(yellow_integrator, yellow_integrator, synapse=tau)
    nengo.Connection(magenta_integrator, magenta_integrator, synapse=tau)

    # Connect colors to the integrators
    mau = 10
    nengo.Connection(current_color[1], green_integrator, 
        transform=mau, synapse=tau)
    nengo.Connection(current_color[2], red_integrator, 
        transform=mau, synapse=tau)
    nengo.Connection(current_color[3], blue_integrator, 
        transform=mau, synapse=tau)
    nengo.Connection(current_color[4], magenta_integrator, 
        transform=mau, synapse=tau)
    nengo.Connection(current_color[5], yellow_integrator, 
        transform=mau, synapse=tau)

    stop_ens = nengo.Ensemble(200, 1, radius=1)

    pau = 1
    nengo.Connection(green_integrator, stop_ens,
        transform=pau, synapse=tau)
    nengo.Connection(red_integrator, stop_ens,
        transform=pau, synapse=tau)
    nengo.Connection(blue_integrator, stop_ens,
        transform=pau, synapse=tau)
    nengo.Connection(magenta_integrator, stop_ens,
        transform=pau, synapse=tau)
    nengo.Connection(yellow_integrator, stop_ens,
        transform=pau, synapse=tau)

    stop_integrator = nengo.Ensemble(200,1)
    nengo.Connection(stop_integrator, stop_integrator, synapse=0.01, transform=0.1)
    nengo.Connection(stop_ens, stop_integrator)

    # Connect the accumulated signal to the interrupt to inhibit the signal
    nengo.Connection(stop_integrator, interrupt[2])

    # Input the number of colors
    input_node = nengo.Node([4])
    nengo.Connection(input_node, stop_ens, transform=-1)
    
    continuous_one = nengo.Node([1])
    nengo.Connection(continuous_one, stop_ens)
