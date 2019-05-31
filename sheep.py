from mob import Mob, Bird
from game import WorldViewRouter, BoundaryWall
import cmath
import random
from block import Block, TrickCandleFlameBlock, ResourceBlock
from dropped_item import DroppedItem
from player import Player


SHEEP_GRAVITY_FACTOR = 0
SHEEP_X_SCALE=1.61803

class Sheep(Mob):
    def step(self, time_delta, game_data):
        """Advance this bird by one time step

        See PhysicalThing.step for parameters & return"""
        # Every 20 steps; could track time_delta instead to be more precise
        if self._steps % 20 == 0:
            # a random point on a movement circle (radius=tempo), scaled by the percentage
            # of health remaining
            health_percentage = self._health / self._max_health
            z = cmath.rect(self._tempo * health_percentage, random.uniform(0, 2 * cmath.pi))

            # stretch that random point onto an ellipse that is wider on the x-axis
            dx, dy = z.real * SHEEP_X_SCALE, z.imag

            x, y = self.get_velocity()
            velocity = x + dx, y + dy - SHEEP_GRAVITY_FACTOR

            self.set_velocity(velocity)

        super().step(time_delta, game_data)

    def get_drops(self):
        return[('item', ("wool",))]

class mobRouter(WorldViewRouter):
    _routing_table = [
        # (class, method name)
        (Block, '_draw_block'),
        (TrickCandleFlameBlock, '_draw_mayhem_block'),
        (DroppedItem, '_draw_physical_item'),
        (Player, '_draw_player'),
        (Bird, '_draw_bird'),
        (BoundaryWall, '_draw_undefined'),
        (None.__class__, '_draw_undefined'),
        (Sheep, '_draw_sheep')
    ]

    def _draw_sheep(self, instance, shape, view):
        return [view.create_oval(shape.bb.left, shape.bb.top, shape.bb.right, shape.bb.bottom,
                                 fill='white', tags=('mob', 'sheep'))]