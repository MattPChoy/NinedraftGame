"""
Simple 2d world where the player can interact with the items in the world.
"""

__author__ = ""
__date__ = ""
__version__ = "1.1.0"
__copyright__ = "The University of Queensland, 2019"

import tkinter as tk
from tkinter import *
from tkinter import messagebox
import random
from collections import namedtuple
import os, sys
import pymunk

from block import Block, ResourceBlock, BREAK_TABLES, LeafBlock, TrickCandleFlameBlock
from grid import Stack, Grid, SelectableGrid, ItemGridView
from item import Item, SimpleItem, HandItem, BlockItem, MATERIAL_TOOL_TYPES, TOOL_DURABILITIES
from player import Player
from dropped_item import DroppedItem
from crafting import GridCrafter, CraftingWindow, GridCrafterView
from world import World
from core import positions_in_range
from game import GameView, WorldViewRouter
from mob import Bird
from hotbaritem import HotbarItem
from toolitem import ToolItem
from craftingtable import CraftingTableBlock
from fooditem import FoodItem

BLOCK_SIZE = 2 ** 5
GRID_WIDTH = 2 ** 5
GRID_HEIGHT = 2 ** 4

gameTitle = 'NineDraft V0.1 Matthew Choy'

# Task 3/Post-grad only:
# Class to hold game data that is passed to each thing's step function
# Normally, this class would be defined in a separate file
# so that type hinting could be used on PhysicalThing & its
# subclasses, but since it will likely need to be extended
# for these tasks, we have defined it here
GameData = namedtuple('GameData', ['world', 'player'])

class Utils():
    @staticmethod
    def roundhalf(number):
        return round(number*2)/2
        

def create_block(*block_id):
    """(Block) Creates a block (this function can be thought of as a block factory)

    Parameters:
        block_id (*tuple): N-length tuple to uniquely identify the block,
        often comprised of strings, but not necessarily (arguments are grouped
        into a single tuple)

    Examples:
        >>> create_block("leaf")
        LeafBlock()
        >>> create_block("stone")
        ResourceBlock('stone')
        >>> create_block("mayhem", 1)
        TrickCandleFlameBlock(1)
    """
    if len(block_id) == 1:
        block_id = block_id[0]
        if block_id == "leaf":
            return LeafBlock()
        elif block_id == "crafting_table":
            return CraftingTableBlock()
        elif block_id in BREAK_TABLES:
            return ResourceBlock(block_id, BREAK_TABLES[block_id])

    elif block_id[0] == 'mayhem':
        return TrickCandleFlameBlock(block_id[1])
        

    raise KeyError(f"No block defined for {block_id}")


def create_item(*item_id):
    """(Item) Creates an item (this function can be thought of as a item factory)

    Parameters:
        item_id (*tuple): N-length tuple to uniquely identify the item,
        often comprised of strings, but not necessarily (arguments are grouped
        into a single tuple)

    Examples:
        >>> create_item("dirt")
        BlockItem('dirt')
        >>> create_item("hands")
        HandItem('hands')
        >>> create_item("pickaxe", "stone")  # *without* Task 2.1.2 implemented
        Traceback (most recent call last):
        ...
        NotImplementedError: "Tool creation is not yet handled"
        >>> create_item("pickaxe", "stone")  # *with* Task 2.1.2 implemented
        ToolItem('stone_pickaxe')
    """
    if item_id == "apple":
        return FoodItem("apple", 2)

    if len(item_id) == 2:

        if item_id[0] in MATERIAL_TOOL_TYPES and item_id[1] in TOOL_DURABILITIES:
            print(f"Item id[0]: {item_id[0]}, {MATERIAL_TOOL_TYPES}, {item_id[1]}, {TOOL_DURABILITIES}")
            
            raise NotImplementedError("Tool creation is not yet handled")

    elif len(item_id) == 1:

        item_type = item_id[0]
        print(f"Item id: {item_id} Item type: {item_type}")

        if item_type == "hands":
            print(f"creating a hands object with {item_type}")
            return HandItem("hands")

        elif item_type == "dirt":
            print(f"creating a dirt object with {item_type}")
            return BlockItem(item_type)

        # Task 1.4 Basic Items: Create wood & stone here
        # ...

        elif item_type in ["stone", "wood"]:
            print(f"creating a stone or wood object with {item_type}")
            return BlockItem(item_type)
        
        elif item_type == "apple":
            print(f"creating an apple object with {item_type}")
            return FoodItem("apple", 2)

        elif item_type == "stick":
            return Item(item_type)
        
        elif item_type == "coal" or item_type == "torch":
            return Item(item_type)   

        elif item_type == "crafting_table":
            print("creating crafting table")
            return BlockItem(item_type)    


    raise KeyError(f"No item defined for {item_id}")


# Task 1.3: Implement StatusView class here
# ...
class StatusView(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self._master = root

        self._heart = tk.PhotoImage(file="images/health.png")
        tk.Label(self, image=self._heart).pack(side=tk.LEFT)
        self._hearttxt = tk.Label(self, text= "health")
        self._hearttxt.pack(side = tk.LEFT)

        self._food = tk.PhotoImage(file="images/food.png")
        tk.Label(self, image=self._food).pack(side=tk.LEFT)
        self._foodtxt = tk.Label(self, text= "food")
        self._foodtxt.pack(side = tk.LEFT)
    
    def update_health(self, newhealth):
        self._hearttxt['text'] = f"Health {newhealth}"
    
    def update_food(self, newfood):
        self._foodtxt['text'] = f"Food {newfood}"



BLOCK_COLOURS = {
    'diamond': 'blue',
    'dirt': '#552015',
    'stone': 'grey',
    'wood': '#723f1c',
    'leaves': 'green',
    'crafting_table': 'pink',
    'furnace': 'black',
}

ITEM_COLOURS = {
    'diamond': 'blue',
    'dirt': '#552015',
    'stone': 'grey',
    'wood': '#723f1c',
    'apple': '#ff0000',
    'leaves': 'green',
    'crafting_table': 'pink',
    'furnace': 'black',
    'cooked_apple': 'red4'
}

CRAFTING_RECIPES_2x2 = [
    (
        (
            (None, 'wood'),
            (None, 'wood')
        ),
        Stack(create_item('stick'), 4)
    ),

    (
        (
            ('stick', 'stick'),
            ('stick', 'stick')
        ),
        Stack(create_item('wood'), 2)
    ),

    (
        (
            ('coal', None),
            ('stick', None),
        ),
        Stack(create_item('torch'), 4)
    )

    # TODO: Add crafting table
    # TODO: Add another recipe
]
"""
CRAFTING_RECIPES_3x3 = {
    (
        (
            (None, None, None),
            (None, 'wood', None),
            (None, 'wood', None)
        ),
        Stack(create_item('stick'), 16)
    ),
    (
        (
            ('wood', 'wood', 'wood'),
            (None, 'stick', None),
            (None, 'stick', None)
        ),
        Stack(create_item('pickaxe', 'wood'), 1)
    ),
    (
        (
            ('wood', 'wood', None),
            ('wood', 'stick', None),
            (None, 'stick', None)
        ),
        Stack(create_item('axe', 'wood'), 1)
    ),
    (
        (
            (None, 'wood', None),
            (None, 'stick', None),
            (None, 'stick', None)
        ),
        Stack(create_item('shovel', 'wood'), 1)
    ),
    (
        (
            (None, 'stone', None),
            (None, 'stone', None),
            (None, 'stick', None)
        ),
        Stack(create_item('sword', 'wood'), 1)
    )
}
"""
def load_simple_world(world):
    """Loads blocks into a world

    Parameters:
        world (World): The game world to load with blocks
    """
    block_weights = [
        (100, 'dirt'),
        (30, 'stone'),
    ]

    cells = {}

    ground = []

    width, height = world.get_grid_size()

    for x in range(width):
        for y in range(height):
            if x < 22:
                if y <= 8:
                    continue
            else:
                if x + y < 30:
                    continue

            ground.append((x, y))

    weights, blocks = zip(*block_weights)
    kinds = random.choices(blocks, weights=weights, k=len(ground))

    for cell, block_id in zip(ground, kinds):
        cells[cell] = create_block(block_id)

    trunks = [(3, 8), (3, 7), (3, 6), (3, 5)]

    for trunk in trunks:
        cells[trunk] = create_block('wood')

    leaves = [(4, 3), (3, 3), (2, 3), (4, 2), (3, 2), (2, 2), (4, 4), (3, 4), (2, 4)]

    for leaf in leaves:
        cells[leaf] = create_block('leaf')

    for cell, block in cells.items():
        # cell -> box
        i, j = cell

        world.add_block_to_grid(block, i, j)

    world.add_block_to_grid(create_block("mayhem", 0), 14, 8)

    world.add_mob(Bird("friendly_bird", (12, 12)), 400, 100)


class Ninedraft:
    """High-level app class for Ninedraft, a 2d sandbox game"""

    def __init__(self, master):
        """Constructor

        Parameters:
            master (tk.Tk): tkinter root widget
        """

        self._master = master
        self._master.title(gameTitle)
        self._world = World((GRID_WIDTH, GRID_HEIGHT), BLOCK_SIZE)

        load_simple_world(self._world)

        self._player = Player()
        self._world.add_player(self._player, 250, 150)

        self._world.add_collision_handler("player", "item", on_begin=self._handle_player_collide_item)

        self._hot_bar = SelectableGrid(rows=1, columns=10)
        self._hot_bar.select((0, 0))

        starting_hotbar = [
            Stack(create_item("dirt"), 20),
            Stack(create_item("apple"), 4),
            Stack(create_item("crafting_table"), 1)
        ]

        for i, item in enumerate(starting_hotbar):
            self._hot_bar[0, i] = item

        self._hands = create_item('hands')

        self.starting_inventory = [
            ((1, 5), Stack(Item('dirt'), 10)),
            ((0, 2), Stack(Item('wood'), 10)),
            ((0, 0), Stack(SimpleItem('coal'), 4)),
        ]
        self._inventory = Grid(rows=3, columns=10)
        for position, stack in self.starting_inventory:
            self._inventory[position] = stack

        self._crafting_window_size = (3,3)
        self._master.bind("e",
                          lambda e: self.run_effect(('crafting', 'basic')))

        self._view = GameView(master, self._world.get_pixel_size(), WorldViewRouter(BLOCK_COLOURS, ITEM_COLOURS))
        self._view.pack()

        # Task 1.2 Mouse Controls: Bind mouse events here
        # ...
        self._view.bind("<Button-1>", self._left_click)
          # Note that <Button-2> symbolises middle click.
        self._view.bind("<Button-3>", self._right_click)
        self._view.bind("<Motion>", self._mouse_move)
        self._view.bind("<Leave>", lambda e:self._mouse_leave)

        # Task 1.3: Create instance of StatusView here
        # ...
        self._StatusView = StatusView(self._master)
        self._StatusView.pack()

        self._hot_bar_view = ItemGridView(master, self._hot_bar.get_size())
        self._hot_bar_view.pack(side=tk.TOP, fill=tk.X)

        # Task 1.5 Keyboard Controls: Bind to space bar for jumping here
        # ...

        self._master.bind("<space>", self._jump)

        self._master.bind("a", lambda e: self._move(-1, 0))
        self._master.bind("<Left>", lambda e: self._move(-1, 0))
        self._master.bind("d", lambda e: self._move(1, 0))
        self._master.bind("<Right>", lambda e: self._move(1, 0))
        self._master.bind("s", lambda e: self._move(0, 1))
        self._master.bind("<Down>", lambda e: self._move(0, 1))

        # Task 1.5 Keyboard Controls: Bind numbers to hotbar activation here
        # ...

        for k in range(10):
            key=k
            self._master.bind(str(key), lambda e, key=key: self.hotbar_select(key))

        # Task 1.6 File Menu & Dialogs: Add file menu here
        # ...

        self._master.bind("<Escape>", self.exitapp)
        self._master.bind("<r>", self.restart)

        self._target_in_range = False
        self._target_position = 0, 0

        self._currently_crafting = False

        self.redraw()

        self.step()

    def exitapp(self, event=None):
        if messagebox.askokcancel("Quit", "Do you want to quit"):
            self._master.destroy()

    def restart(self, event=None):
        # self.exitapp()
        # main()

        if messagebox.askokcancel("Restart Game", "Do you want to restart the game?"):
            python = sys.executable
            os.execl(python, python, *sys.argv)
            #reset the items in the inventory
            for position, stack in self.starting_inventory:
                self._inventory[position] = stack
    
    def hotbar_select(self, key):
        hb_slot = None

        # Since key will be 1 to 9,
        if key == 0:
            hb_slot = 9
        else:
            hb_slot = key-1

        self._hot_bar.select((0, hb_slot))
        print(f"Selected hotbar slot {hb_slot} with {key}, containing {self.get_holding()} ") 
    
    def redraw(self):
        self._view.delete(tk.ALL)

        # physical things
        self._view.draw_physical(self._world.get_all_things())

        # target
        target_x, target_y = self._target_position
        target = self._world.get_block(target_x, target_y)
        cursor_position = self._world.grid_to_xy_centre(*self._world.xy_to_grid(target_x, target_y))

        # Task 1.2 Mouse Controls: Show/hide target here
        # ...

        if self._target_in_range:
            player_position = self._player.get_position()
            self._view.show_target(player_position, cursor_position)
        elif self._target_in_range:
            self._view.hide_target()
        

        # Task 1.3 StatusView: Update StatusView values here
        # ...
        self._StatusView.update_food(self._player.get_food())
        self._StatusView.update_health(self._player.get_health())

        # hot bar
        self._hot_bar_view.render(self._hot_bar.items(), self._hot_bar.get_selected())

    def step(self):
        data = GameData(self._world, self._player)
        self._world.step(data)
        self.redraw()
        try:
            self._craftingui.redraw()
        except:
            pass
        # Task 1.6 File Menu & Dialogs: Handle the player's death if necessary
        # ...

        if self._player.is_dead():
            self.restart()

        self._master.after(15, self.step)

    def _move(self, dx, dy):
        self.check_target()
        velocity = self._player.get_velocity()
        self._player.set_velocity((velocity.x + dx * 80, velocity.y + dy * 80))

    def _jump(self, event):
        
        velocity = self._player.get_velocity()
        # Task 1.2: Update the player's velocity here
        # ...

        xvel = velocity[0]*0.5
        yvel = velocity[1]-150

        self._player.set_velocity((xvel, yvel))

    def mine_block(self, block, x, y):

        luck = random.random()
        active_item, effective_item = self.get_holding()

        was_item_suitable, was_attack_successful = block.mine(effective_item, active_item, luck)

        effective_item.attack(was_attack_successful)

        # food_decrease_factor = -0.2
        # health_decrease_factor = -0.1

        food_decrease_factor = -1
        health_decrease_factor = -1

        if block.is_mined():
            # Task 1.2 Mouse Controls: Reduce the player's food/health appropriately

            if self._player.get_food() > 0:
                # If the player still has food, decrease the food
                self._player.change_food(food_decrease_factor)
            else:
                # If the player does not have food left, then decrease their health
                self._player.change_health(health_decrease_factor)
            # Update the status view bar
            # self._StatusView.updateSV()

            # Task 1.2 Mouse Controls: Remove the block from the world & get its drops
            # ...   
               

            drops = block.get_drops(luck, was_item_suitable)
            self._world.remove_block(block)

            if not drops:
                return

            x0, y0 = block.get_position()

            for i, (drop_category, drop_types) in enumerate(drops):
                print(f'Dropped {drop_category}, {drop_types}')

                if drop_category == "item":
                    physical = DroppedItem(create_item(*drop_types))

                    # this is so bleh
                    x = x0 - BLOCK_SIZE // 2 + 5 + (i % 3) * 11 + random.randint(0, 2)
                    y = y0 - BLOCK_SIZE // 2 + 5 + ((i // 3) % 3) * 11 + random.randint(0, 2)

                    self._world.add_item(physical, x, y)
                elif drop_category == "block":
                    self._world.add_block(create_block(*drop_types), x, y)
                else:
                    raise KeyError(f"Unknown drop category {drop_category}")

    def get_holding(self):
        active_stack = self._hot_bar.get_selected_value()
        active_item = active_stack.get_item() if active_stack else self._hands

        effective_item = active_item if active_item.can_attack() else self._hands

        return active_item, effective_item

    def check_target(self):
        # select target block, if possible
        active_item, effective_item = self.get_holding()

        pixel_range = active_item.get_attack_range() * self._world.get_cell_expanse()

        self._target_in_range = positions_in_range(self._player.get_position(),
                                                   self._target_position,
                                                   pixel_range)

    def _mouse_move(self, event):
        self._target_position = event.x, event.y
        self.check_target()

    def _mouse_leave(self):
        self._target_in_range = False
        self._view.hide_target()

    def _left_click(self, event):
        # Invariant: (event.x, event.y) == self._target_position
        #  => Due to mouse move setting target position to cursor
        x, y = self._target_position

        if self._target_in_range:
            block = self._world.get_block(x, y)
            if block:
                self.mine_block(block, x, y)

    def _trigger_crafting(self, craft_type):
        print(f"Crafting with {craft_type}")

        if craft_type == "basic":
            crafter = GridCrafter(CRAFTING_RECIPES_2x2)
        else:
             crafter = GridCrafter(CRAFTING_RECIPES_3x3, rows=3, columns=3)
        # (self, master, title, hot_bar: Grid, inventory: Grid, crafter: GridCrafter)


        # Crafting menu is not currently open
        self._craftingui = CraftingWindow(self._master, "Ninedraft Crafting Menu", self._hot_bar, self._inventory, crafter)
        self._craftingui.bind("e", lambda e: self._craftingui.destroy())
        self._currently_crafting = True

    def run_effect(self, effect):
        if len(effect) == 2:
            if effect[0] == "crafting":
                craft_type = effect[1]

                if craft_type == "basic":
                    print("Can't craft much on a 2x2 grid :/")

                elif craft_type == "crafting_table":
                    print("Let's get our kraft® on! King of the brands")

                self._trigger_crafting(craft_type)
                return
            elif effect[0] in ("food", "health"):
                print(f"Effect: {effect}, Effect[0]: {effect[0]}")
                stat, strength = effect
                

                if (self._player.get_food() < self._player.get_max_food()):
                    effect_to_change = "food"
                else:
                    effect_to_change = "health"
                getattr(self._player, f"change_{effect_to_change}")(strength)
                
                print(f"Gaining {strength} {effect_to_change}!")

                self._StatusView.update_food(self._player.get_food())
                self._StatusView.update_health(self._player.get_health())
                return

        raise KeyError(f"No effect defined for {effect}")

    def _right_click(self, event):

        x, y = self._target_position
        target = self._world.get_thing(x, y)

        if target:
            # use this thing
            print(f'using {target}')
            effect = target.use()
            print(f'used {target} and got {effect}')

            if effect:
                self.run_effect(effect)

        else:
            # place active item
            # selected = self.get_holding()
            selected = self._hot_bar.get_selected()

            if not selected:
                return

            stack = self._hot_bar[selected]
            drops = stack.get_item().place()
            print(f"Stack: {stack}, Drops: {drops}, GetItem: {stack.get_item()}")

            stack.subtract(1)
            if stack.get_quantity() == 0:
                # remove from hotbar
                self._hot_bar[selected] = None

            if not drops:
                return

            # handling multiple drops would be somewhat finicky, so prevent it
            if len(drops) > 1:
                raise NotImplementedError("Cannot handle dropping more than 1 thing")

            drop_category, drop_types = drops[0]

            x, y = event.x, event.y

            if drop_category == "block":
                if not self._target_in_range:
                    # If trying to place outside range
                    return None
                existing_block = self._world.get_block(x, y)

                if not existing_block:
                    self._world.add_block(create_block(drop_types[0]), x, y)
                else:
                    raise NotImplementedError(
                        "Automatically placing a block nearby if the target cell is full is not yet implemented")

            elif drop_category == "effect":
                self.run_effect(drop_types)

            else:
                raise KeyError(f"Unknown drop category {drop_category}")

    def _activate_item(self, index):
        print(f"Activating {index}")

        self._hot_bar.toggle_selection((0, index))

    def _handle_player_collide_item(self, player: Player, dropped_item: DroppedItem, data,
                                    arbiter: pymunk.Arbiter):
        """Callback to handle collision between the player and a (dropped) item. If the player has sufficient space in
        their to pick up the item, the item will be removed from the game world.

        Parameters:
            player (Player): The player that was involved in the collision
            dropped_item (DroppedItem): The (dropped) item that the player collided with
            data (dict): data that was added with this collision handler (see data parameter in
                         World.add_collision_handler)
            arbiter (pymunk.Arbiter): Data about a collision
                                      (see http://www.pymunk.org/en/latest/pymunk.html#pymunk.Arbiter)
                                      NOTE: you probably won't need this
        Return:
             bool: False (always ignore this type of collision)
                   (more generally, collision callbacks return True iff the collision should be considered valid; i.e.
                   returning False makes the world ignore the collision)
        """

        item = dropped_item.get_item()

        if self._hot_bar.add_item(item):
            print(f"Added 1 {item!r} to the hotbar")
        elif self._inventory.add_item(item):
            print(f"Added 1 {item!r} to the inventory")
        else:
            print(f"Found 1 {item!r}, but both hotbar & inventory are full")
            return True

        self._world.remove_item(dropped_item)
        return False

# Task 1.1 App class: Add a main function to instantiate the GUI here
# ...

def main():
    root = tk.Tk()
    Ninedraft(root)
    root.mainloop()

if __name__ == "__main__":
    main()
