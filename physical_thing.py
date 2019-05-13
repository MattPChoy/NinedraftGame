class PhysicalThing:
    def __init__(self):
        self._shape = None

    def is_mineable(self):
        raise NotImplementedError("A PhysicalThing subclass must implement an is_mineable method")

    def is_useable(self):
        raise NotImplementedError("A PhysicalThing subclass must implement an is_useable method")

    def use(self):
        raise NotImplementedError("A PhysicalThing subclass must implement a use method")

    def set_shape(self, shape):
        self._shape = shape

    def get_shape(self):
        return self._shape

    def get_position(self):
        position = self._shape.body.position
        return position.x, position.y

    def step(self):
        pass

    def __repr__(self):
        raise NotImplementedError("A PhysicalThing subclass must implement a __repr__ method")


class DynamicThing(PhysicalThing):
    def is_mineable(self):
        return False

    def get_velocity(self):
        return self.get_shape().body.velocity

    def set_velocity(self, velocity):
        self.get_shape().body.velocity = velocity


class BoundaryWall(PhysicalThing):
    def __init__(self, wall_id):
        super().__init__()

        self._id = wall_id

    def get_id(self):
        return self._id

    def is_mineable(self):
        return False

    def is_useable(self):
        return False

    def use(self):
        pass

    def get_position(self):
        x, y = self.get_shape().bb.center()
        return x, y

    def __repr__(self):
        return f"BoundaryWall({self._id!r})"
