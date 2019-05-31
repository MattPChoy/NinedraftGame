from block import ResourceBlock


class CraftingTableBlock(ResourceBlock):
    def __init__(self):

        break_table = {
            "hand": (.35, False),
        }
        self._block_id = "crafting_table"

        super().__init__(self._block_id, break_table)
    
    def use(self):
        return('crafting', 'crafting_table')
    
    def get_drops(self):
        return [('item', ('crafting_table',))]

    def get_max_stack_size(self):
        return 64

    def is_stackable(self):
        return True
    
    def can_attack(self):
        return True