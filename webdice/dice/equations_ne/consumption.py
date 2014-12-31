from __future__ import division
import numpy as np
import numexpr as ne


class ConsumptionModel(object):
    def __init__(self, params):
        self.params = params

    @property
    def initial_values(self):
        return (
            1,
            self.params.output_init * self.params.savings,
        )

    def consumption(self, output, savings):
        return ne.evaluate('output * (1.0 - savings)')

    def consumption_pc(self, consumption, population):
        return ne.evaluate('1000 * consumption / population')

    def consumption_discount(self, c0, c1, i, discount_type=['ramsey', 'constant'][0]):
        if discount_type == 'ramsey':
            eta = self.params.elasmu
            rho = self.params.prstp
            ts = self.params.ts
            return ne.evaluate('exp(-(eta * log(c1 / c0) / (i * ts + .000001) + rho) * i * ts)')
        if discount_type == 'constant':
            RATE = .03
            return 1 / (1 + RATE) ** (i * self.params.ts)

    def investment(self, savings, output):
        return ne.evaluate('savings * output')

    def get_model_values(self, i, df):
        consumption = self.consumption(df.output[i], self.params.savings)
        consumption_pc = self.consumption_pc(
            consumption, df.population[i]
        )
        if i == 0:
            return (consumption, consumption_pc,) + self.initial_values
        return (
            consumption,
            consumption_pc,
            self.consumption_discount(
                df.consumption_pc[0], consumption_pc, i
            ),
            self.investment(self.params.savings, df.output[i]),
        )


class Dice2007(ConsumptionModel):
    pass


class Dice2010(ConsumptionModel):
    pass


class Dice2013(Dice2010):
    pass