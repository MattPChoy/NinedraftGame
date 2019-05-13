import tkinter as tk
from typing import Tuple

from item import Item

__author__ = "Benjamin Martin and Paul Haley"


class Stack(object):
    """Stacks are used to store Items with a stack quantity. Stacks appear in the inventory (and
    similar) as to combine items of the same size up to a maximum limit defined by the Item"""

    def __init__(self, item: Item, quantity: int):
        """Constructor of Stack

        Parameters:
            item (Item): Item this Stack will contain
            quantity (int): Stack size

        Pre-condition:
            0 < quantity <= item.get_max_stack_size()"""

        assert (0 < quantity <= item.get_max_stack_size(),
                f"Stack creation attempted with quantity of {quantity} for Item {item.get_id()!r} "
                f"that has a maximum stack size of {item.get_max_stack_size()}")

        self._item = item
        self._quantity = quantity

    def combine(self, other):
        """Add to this stack the amount in other until other depleted or self is full. No action if
        Stacks are of different types (or other is None).

        Parameters:
            other (Stack): stack to subtract quantity from

        Return (Stack): the state of the other stack, None if depleted"""

        if isinstance(other, Stack) and other.get_item().get_id() == self.get_item().get_id():
            other.subtract(self.add(other.get_quantity()))
            if other._quantity <= 0:
                other = None
        return other

    def split(self):
        """Split this stack quantity in two and return the new Stack. The quantity of the new Stack
        and updated self is equal to the original Stack size.

        return (Stack): new Stack with half the size of the original"""
        new = copy.deepcopy(self)
        new._quantity = self._quantity // 2
        self.subtract(self._quantity // 2)
        return new

    def add(self, quantity: int) -> int:
        """Add to this stack without needing to worry about overflow.

        Parameter:
            quantity (int): Quantity of item to be added to this stack
        return (int): amount added to this stack"""

        to_add = min(self._quantity + quantity, self._item.get_max_stack_size()) - self._quantity
        self._quantity += to_add
        return to_add

    def subtract(self, quantity: int) -> int:
        """Remove quantity from stack. If stack size is smaller than quantity being subtracted,
        quantity will be set to 0.

        Parameters:
            quantity (int): quantity to remove if possible

        Return (int): positive amount remaining after subtracting to maintain a non-negative Stack
        size"""

        remainder = self._quantity - quantity
        self._quantity = max(0, remainder)
        return abs(remainder) if remainder > 0 else 0

    def decrement(self):
        """Decrement Stack by one

        Return (bool): True iff stack depleted (self._quantity == 0)"""

        self.subtract(1)
        return bool(self._quantity)

    def get_item(self) -> Item:
        """Return (Item): The Item in this Stack"""
        return self._item

    def get_quantity(self) -> int:
        """Return (int): The Stack size (quantity)"""
        return self._quantity

    def __repr__(self):
        return "Stack(" + self._item.get_id() + ", " + str(self._quantity) + ")"


class ItemGridView(tk.Canvas):
    """Class defining constants and draw methods for rendering item orientated views. The methods
    in in this class allow for a grid view of items to be easily drawn and be added to the master
    view given.

    This class is intended to be extended upon when defining specific item view contexts."""

    BORDER = 100  # BORDER//2 + |item grid| + BORDER//2
    CELL_LENGTH = 64  # pixel width of grid cell
    CELL_SPACING = 5  # pixel spacing between grid cells

    CONTENT_GAP = CELL_LENGTH // 20  # gap between cell outside border and where to render contents

    def __init__(self, master, size,
                 deselected_colour='#e6e8ed',
                 selected_colour='#6CB2D1',
                 commands=None,
                 **kwargs):
        """Constructor for item based views.

        Parameters:
            master: Container to add this view to
            size (tuple<int, int>): Number of (rows, columns) for the grid
            kwargs: kwargs (key word arguments) to be given to the tk.Canvas on creation
        """

        self._commands = commands or {
            "<Button-1>": lambda e: None,
            "<Button-2>": lambda e: None,
            "<Button-3>": lambda e: None,
        }

        rows, columns = size

        height = rows * (self.CELL_LENGTH + self.CELL_SPACING) + self.BORDER
        width = columns * (self.CELL_LENGTH + self.CELL_SPACING) + self.BORDER

        super().__init__(master, width=width, height=height, **kwargs)

        self._selected_colour = selected_colour
        self._deselected_colour = deselected_colour

        self._slots = Grid(rows=rows, columns=columns)

        for key in self._slots:
            self._slots[key] = self.create_oval(self.grid_to_xy_centre(key), self.grid_to_xy_centre(key))

        for event_type, command in self._commands.items():
            self.bind(event_type, lambda event, event_type=event_type: self._handle_event(event_type, event))

    def _handle_event(self, event_type, event):
        position = self.xy_to_grid((event.x, event.y))
        self._commands[event_type](position)

    def grid_to_xy_box(self, grid_position):
        row, column = grid_position

        x0 = self.BORDER // 2 + (self.CELL_LENGTH + self.CELL_SPACING) * column
        y0 = self.BORDER // 2 + (self.CELL_LENGTH + self.CELL_SPACING) * row

        x1 = x0 + self.CELL_LENGTH
        y1 = y0 + self.CELL_LENGTH

        return x0, y0, x1, y1

    def grid_to_xy_centre(self, grid_position):
        x0, y0, x1, y1 = self.grid_to_xy_box(grid_position)

        return (x0 + x1) // 2, (y0 + y1) // 2

    def xy_to_grid(self, xy_position):
        x, y = xy_position

        column = (x - self.BORDER // 2) // (self.CELL_LENGTH + self.CELL_SPACING)
        row = (y - self.BORDER // 2) // (self.CELL_LENGTH + self.CELL_SPACING)

        return row, column

    def draw_cell(self, position, stack, active=False):
        box = self.grid_to_xy_box(position)

        text = stack.get_item().get_id().replace('_', '\n') if stack else ""

        colour = self._selected_colour if active else self._deselected_colour

        tags = [
            self.create_rectangle(box, fill=colour),
            self.create_text(self.grid_to_xy_centre(position), text=text)
        ]

        self._slots[position] = tags

    def render(self, items, active_position):
        """Re-render the Hot Bar

        Parameters:
            items list<Stack>: items to be displayed in Hot Bar
            active_position (int): id of currently active cell
        """
        self.delete(tk.ALL)
        for position, stack in items:
            self.draw_cell(position, stack, position == active_position)


class Crafter(object):
    """Square crafter model. The crafter can be used for combining multiple items into a single
    item based off crafting recipes. """

    def __init__(self, size: int, recipes, item_categories):
        """Constructor for Crafter model

        Parameters:
            size (int): side length of item grid

        Pre-condition:
            size > 0"""

        self._recipes = recipes
        self._item_categories = item_categories

        assert (size > 0)
        size = 3
        self._space = [None] * size
        for i in range(len(self._space)):
            self._space[i] = [None] * size

        self._space[0][1] = Stack(Item('stick'), 1)
        self._space[1][1] = Stack(Item('stick'), 1)

    def _state_to_key(self) -> Tuple[Tuple[Stack]]:
        """Converts the crafter list matrix (grid) to a reduced tuple matrix based off the extremes
        of where items are placed in the grid.

        Example (where 1 is an occupied cell and 0 is empty):
            [0, 0, 1]
            [0, 0, 1]  => (1)
            [0, 0, 0]     (1)

        Return tuple(tuple(Stack)): Reduced form of Stacks in grid"""

        # Initialise extremities of utilised area (values beyond grid)
        top = len(self._space)
        bottom = -1
        left = len(self._space[0])
        right = -1

        for row in range(len(self._space)):  # Searching for corners of items
            for col in range(len(self._space[row])):
                if self._space[row][col]:
                    if row < top:
                        top = row
                    if col < left:
                        left = col
                    if row > bottom:
                        bottom = row
                    if col > right:
                        right = col

        # Converting list matrix to tuple matrix
        pattern = [None] * (1 + bottom - top)
        for i in range(len(pattern)):
            pattern[i] = tuple(self._space[i][left:right + 1])
        return tuple(pattern)

    def find_match(self):
        """Checks the crafting grid to see if there is a matching crafting recipe and returns it.

        Return tuple(tuple(str)): crafting recipe match or None"""
        state = self._state_to_key()
        for r in self._recipes:
            if len(r) == len(state) and len(r[0]) == len(state[0]):  # same reduced dimensions
                for i in range(len(r)):
                    for j in range(len(r[i])):
                        # check each cell is same Item id or appropriate category
                        item = state[i][j].get_item().get_id() if state[i][j] else None
                        if item != r[i][j] or \
                                (item and item not in self._item_categories.get(r[i][j], r[i][j])):
                            break
                    else:
                        continue  # this row matched recipe, keep checking
                    break
                else:  # all rows matched (did not break), match found
                    return r
        return None

    def craft(self):
        """
        return (Stack): Matching result of crafting recipe or None if no match.
        """

        match = self.find_match()
        if not match:
            return None
        for i in range(len(self._space)):
            for j in range(len(self._space[i])):
                if self._space[i][j]:
                    self._space[i][j].decrement()
        self._update()
        return copy.deepcopy(crafting_recipes[match])

    def _update(self):
        """Set all Stacks of size 0 to None in space"""
        for i in range(len(self._space)):
            for j in range(len(self._space[i])):
                if self._space[i][j] and not self._space[i][j].get_quantity():
                    self._space[i][j] = None

    def add_to_slot(self, stack: Stack, row: int, column: int):
        """Add the stack the row and column specified

        Parameters:
            stack (Stack): stack to add
            row (int): row to add to
            column (int): column to add to

        return (bool): True iff coordinates are in the crafting grid"""
        in_grid = row < self.get_size() and column < self.get_size()
        if in_grid:
            self._space[row][column] = stack
        return in_grid

    def get_item(self, row: int, column: int) -> Stack:
        """Retrieve item from coordinates

        Parameters:
            row (int): row to add to
            column (int): column to add to

        return (Stack): stack at coordinates (potentially None)"""
        return self._space[row][column]

    def get_items(self):
        """return list(list(Stack)): crafter grid"""
        return self._space

    def remove_item(self, row: int, column: int) -> Stack:
        """Remove and return Stack at coordinates

        Parameters:
            row (int): row to add to
            column (int): column to add to

        return (Stack): stack at coordinates (potentially None)"""
        item = self._space[row][column]
        self._space[row][column] = None
        return item

    def get_size(self) -> int:
        """return (int): the side dimension of crafter"""
        return len(self._space)


class CrafterView(ItemGridView):
    """View class for crafting based views. This view gives a square crafting grid and a result
    cell"""

    def __init__(self, master, size):
        """Constructor for CrafterView

        Parameters:
            master: container to add this view to
            size (int): side dimension for crafting grid"""
        super().__init__(master, size, size)

        self._SIZE = size

        # Create arrow between grid and result cell
        arrow_start = self._get_cell_top_left(self._COLUMNS // 2, self._ROWS)
        arrow_start = arrow_start[0], arrow_start[1] + self.CELL_LENGTH // 2
        self.create_line(*arrow_start, arrow_start[0] + self.CELL_LENGTH, arrow_start[1], width=4,
                         arrow=tk.LAST, arrowshape=(10, 15, 10))

        # Result cell
        self._result_location = (self._SIZE // 2, self._SIZE + 1)
        result_top_left = self._get_cell_top_left(*self._result_location)
        self._result = self.draw_cell(result_top_left)
        self._result_render = self.create_text(self._result_location[0] + self.CONTENT_GAP,
                                               self._result_location[1] + self.CONTENT_GAP,
                                               anchor=tk.W, text="")

    def selected_cell(self, x, y):
        """Find and return the cell that has been clicked on (including result) if any.

        parameters:
            x (int): pixels x
            y (int): pixels y

        return (int, int): (row,col) if coordinates are within a cell, else (-1,-1)"""
        table_location = super().selected_cell(x, y)
        if table_location != (-1, -1):
            return table_location
        if self._is_in_cell(x, y, self._get_cell_top_left(*self._result_location)):
            return self._result_location
        return -1, -1

    def is_result_location(self, location):
        """Check if location is the result cell coordinates

        Parameters:
            location (int, int): (row, column) to check

        return (bool): True iff result cell specified"""
        return location == self._result_location

    def select_cell(self, row, column):
        """Mark a cell as selected, this will deselect the previous cell if one is selected.
        Asking to select (-1, -1) will deselect everything. Override includes support for the
        result cell.

        Parameters:
            row (int): row number of cell to select
            column (int): column number of cell to select"""
        if self._selected:
            self.itemconfig(self._selected, fill=self._deselected_colour)
        if row == -1 or column == -1:
            self._selected = None
        else:
            if (row, column) == self._result_location:
                self.itemconfig(self._result, fill=self._selected_colour)
                self._selected = self._result
            else:
                self.itemconfig(self._slots[row][column], fill=self._selected_colour)
                self._selected = self._slots[row][column]


class Grid:
    def __init__(self, rows=4, columns=5):
        self._items = [
            [
                None for j in range(columns)
            ] for i in range(rows)
        ]

    def get_size(self):
        """(int, int) Returns the (row, column) size of this inventory"""

        rows = len(self._items)
        columns = len(self._items[0])

        return rows, columns

    def __getitem__(self, position) -> [Stack, None]:
        row, column = position
        return self._items[row][column]

    def __setitem__(self, position, item: [Stack, None]):
        row, column = position
        self._items[row][column] = item

    def __len__(self):
        rows, columns = self.get_size()
        return rows * columns

    def items(self):
        for i, row in enumerate(self._items):
            for j, cell in enumerate(row):
                yield (i, j), cell

    def keys(self):
        yield from self

    def values(self):
        for i, row in enumerate(self._items):
            for j, cell in enumerate(row):
                yield cell

    def __iter__(self):
        for i, row in enumerate(self._items):
            for j, cell in enumerate(row):
                yield (i, j)

    def pop(self, position):
        value = self[position]
        self[position] = None
        return value

    def __contains__(self, position):
        row, column = position
        rows, columns = self.get_size()

        return 0 <= row < rows and 0 <= column < columns

    #### end standardised collection methods

    def add_item(self, item: Item):
        self.add_items(Stack(item, 1))

    def add_items(self, stack: Stack):
        """Add a stack to the inventory. The insertion method will first try combining existing
        stacks before placing the remaining new stack into the first empty cell (if any). The
        return of this method must be checked to verify the given stack does not have remaining
        quantity.

        Parameters:
            stack (Stack): stack to add to the inventory

        return (bool): True iff the entire stack was added."""
        first_empty = None
        for row in range(len(self._items)):
            for column in range(len(self._items[row])):
                if self._items[row][column]:  # check that cell is not empty (None)
                    self._items[row][column].combine(stack)
                elif not first_empty:  # find first cell that is empty (if any)
                    first_empty = (row, column)
                if not stack.get_quantity():
                    return True

        # Did not deplete stack on pre-existing stack, add to first empty cell if found
        if first_empty:
            self._items[first_empty[0]][first_empty[1]] = stack
            return True
        return False

    def add_to_slot(self, stack: Stack, row: int, column: int):
        """Add the stack the row and column specified

        Parameters:
            stack (Stack): stack to add
            row (int): row to add to
            column (int): column to add to

        return (bool): True iff coordinates are in the crafting grid"""
        self[row, column] = stack

    def get_items(self):
        return list(self.values())

    def get_item(self, row, column):
        return self[row, column]

    def remove_item(self, row, column):
        return self.pop((row, column))


class SelectableGrid(Grid):
    def __init__(self, rows=4, columns=5):
        super().__init__(rows=rows, columns=columns)

        self._selected = None

    def get_selected(self):
        return self._selected

    def get_selected_value(self):
        if self._selected:
            return self[self._selected]
        else:
            return None

    def select(self, position):
        if position not in self:
            raise KeyError(f"Invalid position {position} on {self.get_size()} grid")

        self._selected = position

    def deselect(self):
        self._selected = None

    def toggle_selection(self, position):
        if position not in self:
            raise KeyError(f"Invalid position {position} on {self.get_size()} grid")

        if self._selected == position:
            self._selected = None
        else:
            self._selected = position


class HotBar(SelectableGrid):
    """Hot Bar model for storing of the player's on-hand items (Stacks). The Hot Bar is comparable
    to a single row inventory but has the concept of an active item that the player is currently
    holding/using. """

    def __init__(self, columns=10):
        super().__init__(rows=1, columns=columns)
        self._active = 0

    def set_item(self, index: int, stack: Stack):
        """Store the given stack in the cell corresponding to the id given.

        Parameters:
            index (int): cell id to add Stack to
            stack (Stack): stack to place into cell"""
        if not (0 <= index < len(self._items[0])):
            raise IndexError(f"ID must be in range 0 <= id < {len(self._items)}; instead got {index}")
        self[0, index] = stack

    def add_item(self, stack: Stack) -> bool:
        """Find the first empty cell and place the Stack into it.

        Parameters:
            stack (Stack): stack to add to Hot Bar

        Return (bool): True iff Stack was added; False if HotBar was full."""
        for position, stack in self._items.items():
            print(position, stack)


        if None in self._items:
            self._items[0][self._items[0].index(None)] = stack
            return True
        return False

    def remove_item(self, id: int) -> Stack:
        """Remove and return Stack at id

        Parameters:
            id (int): cell to remove from

        return (Stack): Stack at cell requested (could be None)"""
        return self.pop((0, id))

    def get_item(self, id) -> Stack:
        """Get and return Stack at id

        Parameters:
            id (int): cell to get from

        return (Stack): Stack at cell requested (could be None)"""
        return self[(0, id)]

    def get_items(self):
        """return list(list(Stack)): inventory grid"""
        return self._items

    def get_first_empty_id(self) -> int:
        """return (int): get the first empty cell in the Hot Bar"""
        return self._items[0].index(None)
