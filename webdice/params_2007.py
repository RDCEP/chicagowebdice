from params import DiceParams
import numpy as np

class Dice2007Params(DiceParams):
    def __init__(self):
        super(Dice2007Params, self).__init__()
        dice_version = '2007'
        self.carbon_model = 'dice_%s' % dice_version
        self.consumption_model = 'dice_%s' % dice_version
        self.damages_model = 'dice_%s' % dice_version
        self.emissions_model = 'dice_%s' % dice_version
        self.productivity_model = 'dice_%s' % dice_version
        self.temperature_model = 'dice_%s' % dice_version
        self.utility_model = 'dice_%s' % dice_version