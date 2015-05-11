from __future__ import division
import numpy as np
import numexpr as ne


class ConsumptionModel(object):
    """
    ConsumptionModel base class
    ...
    Properties
    ----------
    initial_values : array
        Values for discount_factor and investment at t=0
    ...
    Methods
    -------
    get_model_values()
    consumption_pc()
    discount_factor()
    investment()
    """
    def __init__(self, params):
        self.params = params

    @property
    def initial_values(self):
        return (
            1, None, None,
            self.params.output_2005 * self.params.savings,
        )

    def get_model_values(self, i, df):
        consumption = self.consumption(df.output[i], self.params.savings)
        consumption_pc = self.consumption_pc(
            consumption, df.population[i]
        )
        if i == 0:
            return (consumption, consumption_pc,) + self.initial_values
        discount_factor = self.discount_factor(
            df.consumption_pc[0], consumption_pc, i
        )
        discount_rate = self.discount_rate(discount_factor, i)
        return (
            consumption,
            consumption_pc,
            discount_factor,
            discount_rate,
            self.discount_forward(df.discount_rate[i-1], discount_rate, i),
            self.investment(self.params.savings, df.output[i]),
        )

    def consumption(self, output, savings):
        """
        C, Consumption, trillions $USD
        ...
        Returns
        -------
        float
        """
        return ne.evaluate('output * (1.0 - savings)')

    def consumption_pc(self, consumption, population):
        """
        c, Per capita consumption, thousands $USD
        ...
        Returns
        -------
        float
        """
        return ne.evaluate('consumption / population')

    def discount_factor(self, c0, c1, i, discount_type='ramsey'):
    # def discount_factor(self, c0, c1, i, discount_type='constant'):
        """Discount rate for consumption"""
        if discount_type == 'ramsey':
            eta = self.params.elasmu
            rho = self.params.prstp
            return ne.evaluate('exp(-(eta * log(c1 / c0) / (i * 10 + .000001) + rho) * i * 10)')
        if discount_type == 'constant':
            RATE = .03
            return 1 / (1 + RATE) ** (i * 10)

    def discount_rate(self, factor, i):
        return ne.evaluate('1 / factor ** (1 / (i * 10)) - 1')

    def discount_forward(self, r0, r1, i):
        return ne.evaluate('((1 + r1) ** (i * 10) / (1 + r0) ** ((i - 1) * 10)) ** .1 - 1')



    def investment(self, savings, output):
        """
        I, Investment, trillions $USD
        ...
        Returns
        -------
        float
        """
        return ne.evaluate('savings * output')


class Dice2007(ConsumptionModel):
    pass


class Dice2010(ConsumptionModel):
    pass