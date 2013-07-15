from dice import Dice


class Dice2007(Dice):
    def __init__(self):
        super(Dice2007, self).__init__()


if __name__ == '__main__':
    d = Dice2007()
    d.loop()
    print d.data.vars.population[:5]
    print d.eq.productivity_model.population_growth