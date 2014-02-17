from __future__ import division
import numpy as np


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
        self._params = params

    @property
    def initial_values(self):
        return (
            1,
            self._params._output_2005 * self._params.savings,
        )

    def get_model_values(self, index, data):
        consumption, population = self.consumption(
            data.output[index], self._params.savings, data.population[index])
        consumption_pc = self.consumption_pc(consumption, population)
        if index == 0:
            return (consumption, consumption_pc,) + self.initial_values + \
                   (population,)
        return (
            consumption,
            consumption_pc,
            self.consumption_discount(data.consumption_pc[0],
                                      consumption_pc, index),
            self.investment(self._params.savings, data.output[index]),
            population
        )

    def consumption(self, output, savings, population):
        """
        C, Consumption, trillions $USD
        ...
        Returns
        -------
        float
        """
        c = output * (1.0 - savings)
        mc = 250e-6 * population
        return c, np.maximum(population * np.minimum(c, mc) / mc, 0)

    def consumption_pc(self, consumption, population):
        """
        c, Per capita consumption, thousands $USD
        ...
        Returns
        -------
        float
        """
        return 1e3 * consumption / population

    def consumption_discount(self, c0, c1, i, discount_type='ramsey'):
    # def consumption_discount(self, c0, c1, i, discount_type='constant'):
        """Discount rate for consumption"""
        if discount_type == 'ramsey':
            return np.exp(-(
                self._params.elasmu * np.log(c1 / c0) / (i * 10 + 1e-6) +
                self._params.prstp
            ) * i * 10)
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
        return savings * output

class Dice2007(ConsumptionModel):
    pass


class Dice2010(ConsumptionModel):
    pass