import tkinter as tk
from grid import SelectableGrid, ItemGridView


class CraftingWindow(tk.Toplevel):
    def __init__(self, master, hot_bar: SelectableGrid, inventory: SelectableGrid, crafter):
        super().__init__(master)

        self._hot_bar = hot_bar
        self._inventory = inventory
        self._crafter = crafter

        # self._crafting_view = CrafterView()

        self._selection = None

        self._inventory_view = ItemGridView(self, inventory.get_size(), commands={
            "<Button-1>": lambda position: self._handle_click("inventory", position)
        })
        self._inventory_view.pack()

        self._hot_bar_view = ItemGridView(self, hot_bar.get_size(), commands={
            "<Button-1>": lambda position: self._handle_click("hot_bar", position)
        })
        self._hot_bar_view.pack()

        self.redraw()

    def redraw(self):
        widget, position = self._selection if self._selection else (None, None)
        self._inventory_view.render(self._inventory.items(), position if widget == "inventory" else None)
        self._hot_bar_view.render(self._hot_bar.items(), position if widget == "hot_bar" else None)

    def _handle_click(self, widget, position):
        print(f"Clicked on {widget} @ {position}")
        selection = widget, position

        if self._selection == selection:
            # Deselecting current position
            self._selection = None
        else:
            # Selecting new position
            # TODO: implement swap
            self._selection = selection

        self.redraw()