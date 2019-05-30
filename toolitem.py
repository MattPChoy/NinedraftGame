from item import Item

class ToolItem(Item):
    def __init__(self, item_id: str, tool_type: str, durability: float):
        super().__init__(id_ = item_id, max_stack=1)
        self._tool_type = tool_type
        self._durability = durability

    def get_type(self):
        return self._tool_type
    
    def get_durability(self):
        return self._durability
    
    def can_attack(self):
        if self.get_durability() != 0:
            return True
        else:
            return False
    
    def attack(self, successful: bool):
        if successful:
            self._durability -= 1