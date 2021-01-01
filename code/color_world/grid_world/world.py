# grid.py courtesy of Terry Stewart, UWaterloo
# see https://github.com/tcstewar/syde556-1/

from code.color_world.grid_world.cell import Cell
import random
from multimethod import multimeta


class World(metaclass=multimeta):
    def __init__(
        self,
        cell=None,
        width=None,
        height=None,
        directions=8,
        filename=None,
        map=None,
    ):
        if cell is None:
            cell = Cell
        self.Cell = cell
        self.directions = directions
        if filename or map:
            if filename:
                map_file = open(filename, "r+")
                data = map_file.readlines()
            else:
                data = map.splitlines()
                if len(data[0]) == 0:
                    del data[0]
            if height is None:
                height = len(data)
            if width is None:
                width = max([len(x.rstrip()) for x in data])
        if width is None:
            width = 20
        if height is None:
            height = 20
        self.width = width
        self.height = height
        self.image = None
        self.reset()
        if filename or map:
            self.load(filename=filename, map=map)

    def get_cell(self, x, y):
        return self.grid[y][x]

    def get_cell_neighbours(self, x, y):
        pts = [
            self.get_point_in_direction(x, y, direction)
            for direction in range(self.directions)
        ]
        return tuple([self.grid[y][x] for (x, y) in pts])

    def get_cell_neighbours(self, cell):
        x = cell.x
        y = cell.y
        pts = [
            self.get_point_in_direction(x, y, direction)
            for direction in range(self.directions)
        ]
        return tuple([self.grid[y][x] for (x, y) in pts])

    def find_cells(self, filter):
        for row in self.grid:
            for cell in row:
                if filter(cell):
                    yield cell

    def reset(self):
        self.grid = [
            [self._make_cell(i, j) for i in range(self.width)]
            for j in range(self.height)
        ]
        self.dictBackup = [
            [{} for i in range(self.width)] for j in range(self.height)
        ]
        self.agents = []
        self.age = 0

    def _make_cell(self, x, y):
        c = self.Cell()
        c.x = x
        c.y = y
        c.world = self
        c.agents = []
        return c

    def randomize(self):
        if not hasattr(self.Cell, "randomize"):
            return
        for row in self.grid:
            for cell in row:
                cell.randomize()

    def save(self, file_name=None):
        if not hasattr(self.Cell, "save"):
            return
        if isinstance(f, type("")):
            f = open(file_name, "rw+")

        total = ""
        for j in range(self.height):
            line = ""
            for i in range(self.width):
                line += self.grid[j][i].save()
            total += "%s\n" % line
        if f is not None:
            f.write(total)
            f.close()
        else:
            return total

    def load(self, filename=None, map=None):
        if not hasattr(self.Cell, "load"):
            return
        if filename:
            if isinstance(filename, type("")):
                filename = open(filename, "rw+")
            lines = filename.readlines()
        else:
            lines = map.splitlines()
            if len(lines[0]) == 0:
                del lines[0]
        lines = [x.rstrip() for x in lines]
        fh = len(lines)
        fw = max([len(x) for x in lines])
        if fh > self.height:
            fh = self.height
            starty = 0
        else:
            starty = int((self.height - fh) / 2)
        if fw > self.width:
            fw = self.width
            startx = 0
        else:
            startx = int((self.width - fw) / 2)

        self.reset()
        for j in range(fh):
            line = lines[j]
            for i in range(min(fw, len(line))):
                self.grid[starty + j][startx + i].load(line[i])

    def update(self):
        if hasattr(self.Cell, "update"):
            for j, row in enumerate(self.grid):
                for i, c in enumerate(row):
                    self.dictBackup[j][i].update(c.__dict__)
                    c.update()
                    c.__dict__, self.dictBackup[j][i] = (
                        self.dictBackup[j][i],
                        c.__dict__,
                    )
            for j, row in enumerate(self.grid):
                for i, c in enumerate(row):
                    c.__dict__, self.dictBackup[j][i] = (
                        self.dictBackup[j][i],
                        c.__dict__,
                    )
            for a in self.agents:
                a.update()
        else:
            for a in self.agents:
                oldCell = a.cell
                a.update()
        self.age += 1

    def get_offset_in_direction(self, x, y, dir):
        if self.directions == 8:
            dx, dy = [
                (0, -1),
                (1, -1),
                (1, 0),
                (1, 1),
                (0, 1),
                (-1, 1),
                (-1, 0),
                (-1, -1),
            ][dir]
        elif self.directions == 4:
            dx, dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][dir]
        elif self.directions == 6:
            if y % 2 == 0:
                dx, dy = [(1, 0), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1)][
                    dir
                ]
            else:
                dx, dy = [(1, 0), (1, 1), (0, 1), (-1, 0), (0, -1), (1, -1)][
                    dir
                ]
        return dx, dy

    def get_point_in_direction(self, x, y, dir):
        dx, dy = self.get_offset_in_direction(x, y, dir)

        x2 = x + dx
        y2 = y + dy

        if x2 < 0:
            x2 += self.width
        if y2 < 0:
            y2 += self.height
        if x2 >= self.width:
            x2 -= self.width
        if y2 >= self.height:
            y2 -= self.height

        return (x2, y2)

    def remove(self, agent):
        self.agents.remove(agent)
        agent.world = None
        agent.cell = None

    def add(self, agent, x=None, y=None, cell=None, dir=None):
        self.agents.append(agent)
        if x is not None and y is not None:
            cell = self.grid[y][x]
        if cell is None:
            while True:
                xx = x
                yy = y
                if xx is None:
                    xx = random.randrange(self.width)
                if yy is None:
                    yy = random.randrange(self.height)
                if not getattr(self.grid[yy][xx], "wall", False):
                    y = yy
                    x = xx
                    break
        else:
            x = cell.x
            y = cell.y

        if dir is None:
            dir = random.randrange(self.directions)

        agent.cell = self.grid[y][x]
        agent.dir = dir
        agent.world = self
        agent.x = x
        agent.y = y
