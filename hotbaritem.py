from item import Item

class HotbarItem(Item):
    def __init__(self, item_id:str):
        self._id = item_id
        super().__init__(id_=item_id, attack_range=0)
    
    def can_attack(self):
        pass
    
    def attack(self):
        pass

    def place(self):
        # A stick is an item which cannot be placed.
        pass
    
    def get_attack_range(self):
        return 0
