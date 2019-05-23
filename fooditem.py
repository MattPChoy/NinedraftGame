from item import Item

class FoodItem(Item):
    def __init__(self, itemid, strength):
        self._strength = strength
        self._id = itemid

    def get_strength(self) -> float:
        return self._strength
    
    def set_player(self, player):
        self._player = player
        self._max_food = self._player.get_max_food()
        self._max_health = self._player.get_max_health()
        return None

    def place(self):
        strength = self.get_strength()

        if self._player.get_food() < self._max_food:
            self._player.change_food(strength)

            if self._player.get_food < self._max_food:
                self._player.change_food(self._max_food)
        
        elif self._player.get_health() < self._max_health:
            self._player.change_health(strength)

            if self._player.get_health < self._max_health:
                self._player.change_health(self._max_health)

        return None
            