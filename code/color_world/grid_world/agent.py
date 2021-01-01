from code.color_world.grid_world.cell import Cell


class CellularException(Exception):
    pass


class Agent:
    def __init__(self):
        self.world = None
        self.cell = None

    def __setattr__(self, key, val):
        if key == "cell":
            old = self.__dict__.get(key, None)
            if old is not None:
                old.agents.remove(self)
            if val is not None:
                val.agents.append(self)
        self.__dict__[key] = val

    def __getattr__(self, key):
        if key == "left_cell":
            return self.get_cell_on_left()
        elif key == "right_cell":
            return self.get_cell_on_right()
        elif key == "ahead_cell":
            return self.get_cell_ahead()
        raise AttributeError(key)

    def turn(self, amount):
        self.dir = (self.dir + amount) % self.world.directions

    def turn_left(self):
        self.turn(-1)

    def turn_right(self):
        self.turn(1)

    def turn_around(self):
        self.turn(self.world.directions / 2)

    def go_in_direction(self, dir):
        target = self.world.get_cell_neighbours(self.cell)[dir]
        if getattr(target, "wall", False):
            return False
        self.cell = target
        return True

    def go_forward(self):
        if self.world is None:
            raise CellularException("Agent has not been put in a World")
        return self.go_in_direction(self.dir)

    def go_backward(self):
        self.turn_around()
        r = self.go_forward()
        self.turn_around()
        return r

    def get_cell_ahead(self):
        return self.world.get_cell_neighbours(self.cell)[self.dir]

    def get_cell_on_left(self):
        return self.world.get_cell_neighbours(self.cell)[
            (self.dir - 1) % self.world.directions
        ]

    def get_cell_on_right(self):
        return self.world.get_cell_neighbours(self.cell)[
            (self.dir + 1) % self.world.directions
        ]

    def go_towards(self, target, y=None):
        if not isinstance(target, Cell):
            target = self.world.grid[int(y)][int(target)]
        if self.world is None:
            raise CellularException("Agent has not been put in a World")
        if self.cell == target:
            return
        best = None
        for i, n in enumerate(self.world.get_cell_neighbours(self.cell)):
            if n == target:
                best = target
                bestDir = i
                break
            if getattr(n, "wall", False):
                continue
            dist = (n.x - target.x) ** 2 + (n.y - target.y) ** 2
            if best is None or bestDist > dist:
                best = n
                bestDist = dist
                bestDir = i
        if best is not None:
            if getattr(best, "wall", False):
                return False
            self.cell = best
            self.dir = bestDir
            return True

    def update(self):
        pass
