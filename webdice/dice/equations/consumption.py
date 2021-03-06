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
        discount_factor()
        investment()

    """
    def __init__(self, params):
        self.params = params

    @property
    def initial_values(self):
        """Consumption discount and investment at t=0

        Returns:
            tuple: discount rate for consumption, and investment in $1000USD

        """
        return (
            1, 0, 0,
            self.params.output_2005 * self.params.savings,
        )

    def get_model_values(self, i, df):
        """Get results for t

        Return values for Consumption (C), Consumption per capita (c),
        Discount rate for consumption, and Investment (I)

        Args:
            i (int): time step
            df (DiceDataMatrix): model variables

        Returns:
            tuple: C, c, discount rate, I

        """
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
            discount_rate * 100,
            self.discount_forward(df.discount_rate[i-1] / 100., discount_rate, i) * 100,
            self.investment(self.params.savings, df.output[i]),
        )

    def consumption(self, output, savings):
        """Equation for consumption

        C, Consumption, trillions $USD

        Args:
            output (float or array of float): Economic output at t
            savings (float or array of float): Savings rate at t

        Returns:
            float or array of float

        """
        return output * (1.0 - savings)

    def consumption_pc(self, consumption, population):
        """Equation for consumption per capita
        c, Per capita consumption, thousands $USD
        ...
        Returns
        -------
        float
        """
        return consumption / population

    def discount_factor(self, c0, c1, i, discount_type='ramsey'):
    # def discount_factor(self, c0, c1, i, discount_type='constant'):
        """Equation for consumption discount factor

        Discount factor for consumption
        """
        if discount_type == 'ramsey':
            if c1 <= 0:
                return 1
            return np.exp(-(
                self.params.elasmu * np.log(c1 / c0) / (i * 10 + .000001) +
                self.params.prstp
            ) * i * 10)
        if discount_type == 'constant':
            RATE = .03
            return 1 / (1 + RATE) ** (i * 10)

    def discount_rate(self, factor, i):
        return 1 / factor ** (1 / (i * 10)) - 1

    def discount_forward(self, r0, r1, i):
        return ((1 + r1) ** i / (1 + r0) ** (i - 1)) - 1

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