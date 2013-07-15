from dice import Dice
from params_2010 import Dice2010Params

class Dice2010(Dice):
    def __init__(self):
        super(Dice2010, self).__init__()
        self.params = Dice2010Params()
        self.data = self.params._data


if __name__ == '__main__':
    d = Dice2010()
    d.loop()
    print d.data.vars.population[:5]