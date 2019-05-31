from item import Item, TOOL_DURABILITIES

class ToolItem(Item):
    def __init__(self, item_id: str, tool_type: str, durability: float):
        super().__init__(id_ = item_id, max_stack=1)
        self._tool_type = tool_type
        self._durability = durability
        
        self._tool_materials = TOOL_DURABILITIES.keys()

        for material in self._tool_materials:
            if material in self._tool_type:
                # Check if valid tool material, could subtract the tool_type string from item_id
                # But that does not check if it is a valid tool.
                self._tool_material = material
        
        self._max_durability = TOOL_DURABILITIES[self._tool_material]

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
    
    def get_max_durability(self):
        return self._max_durability