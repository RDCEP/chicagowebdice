# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np


class ConsumptionModel(object):
    """ConsumptionModel base class

    Properties:
        initial_values

    Methods:
        get_model_values()
        consumption()
        consumption_pc()
        consumption_discount()
        investment()

    """
    def __init__(self, params):
        self.params = params

    @property
    def initial_values(self):
        """Consumption discount and investment at t=0

        Returns:
        :return: [ consumption discount(0), I(0) ]
         :rtype: list
        """
        return (
            1,
            self.params.output_init * self.params.savings,
        )

    def consumption(self, output, savings):
        """C, Total global consumption, trillions $USD

        Eq: Y(t) * (1 - s)

        Args:
            :param output: Net output
             :type output: float
            :param savings: Percentage of output invested
             :type savings: float

        Returns:
            :return: Global consumption at t
             :rtype: float
        """
        return output * (1.0 - savings)

    def consumption_pc(self, consumption, population):
        """c, Per capita consumption, thousands $USD

        Eq: 1000 * C(t) / L(t)

        Args:
            :param consumption: Global consumption
             :type consumption: float
            :param population: Global population
             :type population: float

        Returns:
            :return: Per capita consumption at t
             :rtype: float
        """
        return 1000 * consumption / population

    def consumption_discount(self, c0, c1, i, discount_type=['ramsey', 'constant'][0]):
        """Equation for consumption discount rate

        Eq:

        Args:
            :param c0: Consumption at (t - 1)
             :type c0: float
            :param c1: Consumption at (t)
             :type c1: float
            :param i: time step
             :type c0: int

        Kwargs:
            :param discount_type: Specify Ramsey style discounting or constant
                                  rate. Defaults to Ramsey.
             :type discount_type: str

        Returns:
            :return: Discount rate for consumption at t
             :rtype: float
        """
        if discount_type == 'ramsey':
            if c1 <= 0:
                return 1
            return np.exp(-(
                self.params.elasmu * np.log(c1 / c0) / (i * self.params.ts + .000001) +
                self.params.prstp
            ) * i * self.params.ts)
        if discount_type == 'constant':
            RATE = .03
            return 1 / (1 + RATE) ** (i * self.params.ts)

    def investment(self, savings, output):
        """I, Investment, trillions $USD

        Eq: s * Q(t)

        Args:
            :param savings: Percentage of output invested
             :type savings: float
            :param output: Net output
             :type output: float

        Returns:
            :return: Investment at t
             :rtype: float
        """
        return savings * output

    def get_model_values(self, i, df):
        """Get values for model variables.

        Args:
            :param i: current time step
             :type i: int
            :param df: Matrix of variables
             :type df: DiceDataMatrix

        Returns:
            :return: Model variables: C, c, consumption discount rate, I
             :rtype: tuple
        """
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