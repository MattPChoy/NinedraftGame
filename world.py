import pymunk
import time

# TODO: move instantiation logic to app/game
from physical_thing import BoundaryWall

COLLISION_TYPES = {
    "wall": 1,
    "block": 2,
    "player": 3,
    "item": 4,
    "creature": 5
}

# must be a unique power of 2, less than 2 ^ 32
PHYSICAL_THING_CATEGORIES = {
    "wall": 2 ** 1,
    "block": 2 ** 2,
    "player": 2 ** 3,
    "item": 2 ** 4,
    "creature": 2 ** 5
}

COLLISION_HANDLER_CALLBACKS = {'begin', 'separate', 'pre_solve', 'post_solve'}


class World:
    def __init__(self, grid_size, cell_expanse):
        self._space = space = pymunk.Space()

        space.gravity = 0, 300

        self._grid_size = grid_size
        self._cell_expanse = cell_expanse

        self._pixel_size = width, height = tuple(grid * cell_expanse for grid in grid_size)

        thickness = 50

        walls = [
            ('top', (0 - thickness, 0 - thickness), (width + thickness, 0 - thickness)),
            ('bottom', (0 - thickness, height + thickness), (width + thickness, height + thickness)),
            ('left', (0 - thickness, 0 - thickness), (0 - thickness, height + thickness)),
            ('right', (width + thickness, 0 - thickness), (width + thickness, height + thickness)),
        ]

        for wall_id, top_left, bottom_right in walls:
            wall = BoundaryWall(wall_id)
            shape = pymunk.Segment(space.static_body, top_left, bottom_right, thickness)
            wall.set_shape(shape)

            shape.friction = 1.
            shape.collision_type = COLLISION_TYPES['wall']
            shape.filter = pymunk.ShapeFilter(categories=PHYSICAL_THING_CATEGORIES["wall"])
            shape.object = wall

            space.add(shape)

        self._last_time = time.time()

    def add_player(self, player, x, y):
        dx = dy = int(self._cell_expanse * .4 - 2)

        body = pymunk.Body(50, pymunk.inf)
        body.position = x, y

        shape = pymunk.Poly(body, [(-dx, -dy), (dx, -dy), (dx, dy), (-dx, dy)], radius=3)
        shape.friction = .5
        shape.collision_type = COLLISION_TYPES['player']
        shape.object = player
        shape.filter = pymunk.ShapeFilter(categories=PHYSICAL_THING_CATEGORIES["player"])

        player.set_shape(shape)

        self._space.add(body, shape)

    def remove_player(self, player):
        self._space.remove(player.get_shape())

    def _wrap_callback(self, callback):
        def wrapped_callback(arbiter, space, data):
            thing_a, thing_b = [s.object for s in arbiter.shapes]
            return callback(thing_a, thing_b, data['data'], arbiter)

        return wrapped_callback

    def add_collision_handler(self, collision_type_a, collision_type_b, data=None,
                              on_begin=None, on_separate=None, on_pre_solve=None, on_post_solve=None):
        handler = self._space.add_collision_handler(COLLISION_TYPES[collision_type_a],
                                                    COLLISION_TYPES[collision_type_b])

        handler.data['data'] = data

        local_variables = locals()

        for key in COLLISION_HANDLER_CALLBACKS:
            callback = local_variables[f"on_{key}"]
            if callback:
                setattr(handler, key, self._wrap_callback(callback))

    def get_pixel_size(self):
        return self._pixel_size

    def get_grid_size(self):
        return self._grid_size

    def get_cell_expanse(self):
        return self._cell_expanse

    def get_all_things(self):
        for shape in self._space.shapes:
            object = shape.object

            if object:
                yield object

    def set_gravity(self, gravity_x, gravity_y):
        self._space.gravity = (gravity_x, gravity_y)

    def step(self):
        for shape in self._space.shapes:
            object = shape.object

            if object:
                object.step()

        now = time.time()
        self._space.step(now - self._last_time)
        self._last_time = now

    def xy_to_grid(self, x, y):
        return x // self._cell_expanse, y // self._cell_expanse

    def grid_to_xy(self, x, y):
        return x * self._cell_expanse, y * self._cell_expanse

    def grid_to_xy_centre(self, x, y):
        return (x + .5) * self._cell_expanse, (y + .5) * self._cell_expanse

    def add_block_to_grid(self, block, column, row):
        left = column * self._cell_expanse
        right = (column + 1) * self._cell_expanse
        top = row * self._cell_expanse
        bottom = (row + 1) * self._cell_expanse

        shape = pymunk.Poly(self._space.static_body, [(left, top), (left, bottom), (right, bottom), (right, top)])
        shape.object = block
        shape.group = 2

        shape.friction = 1.
        shape.collision_type = COLLISION_TYPES['block']
        shape.filter = pymunk.ShapeFilter(categories=PHYSICAL_THING_CATEGORIES["block"])

        block.set_shape(shape)
        self._space.add(shape)

    # TODO: is this even necessary? is add_block_to_grid?
    def get_block_from_grid(self, block, column, row):
        # TODO: implement
        return NotImplementedError()

    def add_block(self, block, x, y):
        return self.add_block_to_grid(block, *self.xy_to_grid(x, y))

    def get_block(self, x, y):
        blocks = self._space.point_query((x, y), 0, pymunk.ShapeFilter(mask=PHYSICAL_THING_CATEGORIES["block"]))

        if blocks:
            return blocks[0].shape.object

    def remove_block(self, block):
        self._space.remove(block.get_shape())

    def add_item(self, item, x, y):
        # TODO: abstract this
        width, height = (8, 8)

        left = -width // 2
        right = width // 2
        top = - height // 2
        bottom = height // 2

        body = pymunk.Body(2, pymunk.inf)
        body.position = x, y
        shape = pymunk.Poly(body, [(left, top), (left, bottom), (right, bottom), (right, top)])

        shape.object = item
        shape.collision_type = COLLISION_TYPES['item']
        shape.filter = pymunk.ShapeFilter(categories=PHYSICAL_THING_CATEGORIES["item"])
        shape.friction = 1.

        item.set_shape(shape)
        self._space.add(body, shape)

    def remove_item(self, item):
        self._space.remove(item.get_shape())

    def remove_creature(self, item):
        self._space.remove(item.get_shape())

    def add_creature(self, item, x, y):
        # TODO: abstract this
        width, height = (32, 16)

        left = -width // 2
        right = left + width
        top = -height // 2
        bottom = top + height

        body = pymunk.Body(20, pymunk.inf)
        body.position = x, y
        shape = pymunk.Poly(body, [(left, top), (left, bottom), (right, bottom), (right, top)])

        shape.object = item
        shape.collision_type = COLLISION_TYPES['creature']
        shape.filter = pymunk.ShapeFilter(categories=PHYSICAL_THING_CATEGORIES["creature"])
        shape.friction = 1.

        item.set_shape(shape)
        self._space.add(body, shape)

    def get_thing(self, x, y):
        queries = self._space.point_query((x, y), 0, pymunk.ShapeFilter(
            mask=pymunk.ShapeFilter.ALL_MASKS ^ PHYSICAL_THING_CATEGORIES["wall"]))

        return queries[0].shape.object if queries else None

    def get_items(self, x, y, max_distance):
        queries = self._space.point_query((x, y), max_distance,
                                          pymunk.ShapeFilter(mask=PHYSICAL_THING_CATEGORIES["item"]))

        return [q.shape.object for q in queries]

    def get_creatures(self, x, y, max_distance):
        queries = self._space.point_query((x, y), max_distance,
                                          pymunk.ShapeFilter(mask=PHYSICAL_THING_CATEGORIES["creature"]))

        return [q.shape.object for q in queries]
