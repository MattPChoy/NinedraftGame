from physical_thing import DynamicThing


class DroppedItem(DynamicThing):
    def __init__(self, item):
        super().__init__()

        self._item = item

    def get_item(self):
        return self._item

    def __repr__(self):
        return f"{self.__class__.__name__}({self._item!r})"
