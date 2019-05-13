import tkinter as tk
from instance_router import InstanceRouter

class GameView(tk.Canvas):
    def __init__(self, master, size, physical_view_router: InstanceRouter):
        width, height = size
        super().__init__(master, width=width, height=height)

        self._world_view_router = physical_view_router

    def show_target(self, player_position, target_position):
        # TODO: abstract
        half_size = 12
        thickness = 4

        x, y = target_position

        coords = x - half_size, y - half_size, x + half_size, y + half_size
        self.create_rectangle(coords, fill='', width=thickness * 2, outline='purple', tag=('block', 'target'))

        self.create_line(player_position, (x, y), fill='white', tag='cursor')

    def hide_target(self):
        self.delete('cursor', 'target')

    def draw_physical(self, things):
        for thing in things:
            shape = thing.get_shape()

            # QUERY: cache these?
            items = self._world_view_router.route_and_call(thing, shape, self)