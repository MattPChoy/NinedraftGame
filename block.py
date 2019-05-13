from physical_thing import PhysicalThing

BREAK_TABLES = {
    "dirt": {
        "hand": (.75, True),
        "wood_shovel": (.4, True),
        "stone_shovel": (.2, True),
        "iron_shovel": (.15, True),
        "diamond_shovel": (.1, True),
        "golden_shovel": (.1, True)
    },

    "wood": {
        "hand": (3, True),
        "wood_axe": (1.5, True),
        "stone_axe": (.75, True),
        "iron_axe": (.5, True),
        "diamond_axe": (.4, True),
        "golden_axe": (.25, True)
    },

    "stone": {
        "hand": (7.5, False),
        "wood_pickaxe": (1.15, True),
        "stone_pickaxe": (0.6, True),
        "iron_pickaxe": (0.4, True),
        "diamond_pickaxe": (0.3, True),
        "golden_pickaxe": (0.2, True)
    }
}


class Block(PhysicalThing):
    _id = None

    _break_table = {
    }

    def __init__(self, hitpoints=20):
        super().__init__()

        self._hitpoints = self._max_hitpoints = hitpoints

        if self._id is None:
            raise NotImplementedError("A Block subclass must define an _id attribute")

    def get_id(self):
        return self._id

    def get_hitpoints(self):
        return self._hitpoints

    def get_position(self):
        x, y = self.get_shape().bb.center()
        return x, y

    def is_mineable(self):
        return True

    def get_drops(self, luck, break_result):
        return [('item', (self._id,))]

    def get_damage_by_tool(self, item):
        id_ = item.get_id() if item.get_id() in self._break_table else "hand"

        return self._break_table[id_]

    def mine(self, effective_item, actual_item, luck):
        time, correct_item = self.get_damage_by_tool(effective_item)

        # TODO: unhardcode magic number
        damage = 10 / time
        self._hitpoints -= damage

        print(f"Did {damage} damage with {effective_item} (correct? {correct_item})")

        return correct_item, self.is_mined()

    def is_mined(self):
        return self._hitpoints <= 0

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class LeafBlock(Block):
    _id = 'leaves'

    _break_table = {
        "hand": (.35, False),
        "shears": (.4, True),
        "sword": (.2, False)
    }

    def can_use(self):
        return False

    def use(self):
        print("Kayn't nobudy use a leaf blahk foo")

    def get_drops(self, luck, successful_break):
        if not successful_break:
            if luck < 0.3:
                return [('item', ('apple',))]

    def __repr__(self):
        return f"LeafBlock()"


class ResourceBlock(Block):
    # TODO: require_break_table

    def __init__(self, block_id, break_table):
        self._id = block_id
        self._break_table = break_table

        super().__init__()

    def can_use(self):
        return False

    def use(self):
        pass

    def get_drops(self, luck, correct_tool):
        if correct_tool:
            return [('item', (self._id,))] * 20

    def __repr__(self):
        return f"ResourceBlock({self._id!r})"




class TrickCandleFlameBlock(Block):
    """Just when you thought you've blown it out, it comes back again"""

    _id = "mayhem"

    _break_table = {
        "hand": (5, True),
    }

    colours = ['#F47C7C', '#F7F48B', '#70A1D7']

    def __init__(self, i):
        super().__init__()
        self._i = i

    def get_drops(self, luck, break_result):
        return [('block', ('mayhem', (self._i + 1) % len(self.colours)))]

    def use(self):
        pass

    def __repr__(self):
        return f"TrickCandleFlameBlock({self._i!r})"
