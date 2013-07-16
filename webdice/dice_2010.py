from dice import Dice
from params_2010 import Dice2010Params

class Dice2010(Dice):
    def __init__(self, optimize=False):
        super(Dice2010, self).__init__()
        self.params = Dice2010Params()
        self.data = self.params._data
        self.params._optimize = optimize


if __name__ == '__main__':
    d = Dice2010(optimize=False)
    d.loop()
    print d.data.vars.gross_output[:5]
    print d.data.vars.emissions_ind[:5]
    print d.data.vars.scc[:5]