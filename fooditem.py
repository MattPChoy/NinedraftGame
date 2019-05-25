from item import Item

class FoodItem(Item):
    def __init__(self, itemid:str, strength:float):
        print("FoodItem Init")
        self._strength = strength
        self._id = itemid
        super().__init__(id_="apple")

    def get_strength(self) -> float:
        return self._strength

    def place(self):
        print("FoodItem place")
        print("placing food item")
        return [('effect', ('food', self.get_strength()))]

    def can_attack(self):
        return False

        # if self._player.get_food() < self._max_food:
        #     self._player.change_food(strength)

        #     if self._player.get_food < self._max_food:
        #         self._player.change_food(self._max_food)
        
        # elif self._player.get_health() < self._max_health:
        #     self._player.change_health(strength)

        #     if self._player.get_health < self._max_health:
        #         self._player.change_health(self._max_health)

        # return None
            