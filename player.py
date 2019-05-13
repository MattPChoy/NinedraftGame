from physical_thing import PhysicalThing, DynamicThing

class Player(DynamicThing):
    def __init__(self, name="Allan", max_food=20, max_health=20):
        super().__init__()

        self._name = name

        self._food = self._max_food = max_food
        self._health = self._max_health = max_health

    def get_food(self):
        return self._food

    def get_health(self):
        return self._health

    def change_food(self, change):
        self._food += change

        if self._food < 0:
            self._food = 0
        elif self._food > self._max_food:
            self._food = self._max_food

            # TODO: increase health here?

    def change_health(self, change):
        self._health += change

        if self._health < 0:
            self._health = 0
        elif self._health > self._max_health:
            self._health = self._max_health

    def __repr__(self):
        return f"Player({self._name!r})"