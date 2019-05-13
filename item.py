class Item:
    def __init__(self, id_, max_stack=64, attack_range=10):
        self._id = id_
        self._max_stack_size = max_stack
        self._range = attack_range

    def get_id(self):
        return self._id

    def __repr__(self):
        return f"{self.__class__.__name__}({self._id!r})"

    def can_attack(self):
        raise NotImplementedError("An Item subclass must implement a can_attack method")

    def attack(self, successful):
        raise NotImplementedError("An Item subclass must implement an attack method")

    def place(self):
        raise NotImplementedError("An Item subclass must implement a place method")

    def get_max_stack_size(self):
        return self._max_stack_size

    def is_stackable(self):
        return self._max_stack_size != 1

    def get_attack_range(self):
        return self._range

class HandItem(Item):
    def __init__(self, id_):
        super().__init__(id_, max_stack=1)

    def get_durability(self):
        return float("inf")

    def can_attack(self):
        return True

    def place(self):
        pass

    def is_depleted(self):
        return False

    def attack(self, successful):
        pass

class BlockItem(Item):
    """An item that drops a Block form of itself when used"""

    def can_attack(self):
        return False

    def place(self):
        return [('block', (self._id, ))]




TOOL_DURABILITIES = {
    "wood": 60,
    "stone": 132,
    "iron": 251,
    "gold": 33,
    "diamond": 1562
}

MATERIAL_TOOL_TYPES = {"axe", "shovel", "hoe", "pickaxe", "sword"}

