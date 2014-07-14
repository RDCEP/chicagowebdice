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
        Values for consumption_discount and investment at t=0
    ...
    Methods
    -------
    get_model_values()
    consumption_pc()
    consumption_discount()
    investment()
    """
    def __init__(self, params):
        self.params = params

    @property
    def initial_values(self):
        return (
            1,
            self.params.output_2005 * self.params.savings,
        )

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
        return ne.evaluate('1000 * consumption / population')

    def consumption_discount(self, c0, c1, i, discount_type='ramsey'):
    # def consumption_discount(self, c0, c1, i, discount_type='constant'):
        """Discount rate for consumption"""
        if discount_type == 'ramsey':
            eta = self.params.elasmu
            rho = self.params.prstp
            return ne.evaluate('exp(-(eta * log(c1 / c0) / (i * 10 + .000001) + rho) * i * 10)')
        if discount_type == 'constant':
            RATE = .03
            return 1 / (1 + RATE) ** (i * 10)

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