import nengo

# GridNode sets up the pacman world for visualization
class GridNode(nengo.Node):
    def __init__(self, world, label, delta_t=0.001):

        # The initalizer sets up the html layout for display
        def svg(t):
            last_t = getattr(svg, "_nengo_html_t_", None)
            if last_t is None or t >= last_t + delta_t or t <= last_t:
                svg._nengo_html_ = self.generate_svg(world)
                svg._nengo_html_t_ = t

        super().__init__(svg, label=label)

    # This function sets up an SVG (used to embed html code in the environment)
    def generate_svg(self, world):
        cells = []
        # Runs through every cell in the world (walls & food)
        for i in range(world.width):
            for j in range(world.height):
                cell = world.get_cell(i, j)
                color = cell.color
                if callable(color):
                    color = color()

                if color is not None:
                    cells.append(
                        '<rect x=%d y=%d width=1 height=1 style="fill:%s"/>'
                        % (i, j, color)
                    )

        # Runs through every agent in the world
        agents = []
        for agent in world.agents:

            # sets variables like agent direction, color and size
            direction = agent.dir * 360.0 / world.directions
            color = getattr(agent, "color", "blue")
            if callable(color):
                color = color()

            shape = getattr(agent, "shape", "triangle")

            if shape == "triangle":

                agent_poly = (
                    '<polygon points="0.25,0.25 -0.25,0.25 0,-0.5"'
                    ' style="fill:%s" transform="translate(%f,%f) rotate(%f)"/>'
                    % (color, agent.x + 0.5, agent.y + 0.5, direction)
                )

            elif shape == "circle":
                agent_poly = (
                    "<circle "
                    ' style="fill:%s" cx="%f" cy="%f" r="0.4"/>'
                    % (color, agent.x + 0.5, agent.y + 0.5,)
                )

            agents.append(agent_poly)

        # Sets up the environment as a HTML SVG
        svg = """<svg style="background: white" width="100%%" height="100%%" viewbox="0 0 %d %d">
            %s
            %s
            </svg>""" % (
            world.width,
            world.height,
            "".join(cells),
            "".join(agents),
        )
        return svg
