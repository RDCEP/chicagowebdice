# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np


class UtilityModel(object):
    """UtilityModel base class

    """
    def __init__(self, params):
        self.params = params

    @property
    def utility_discount(self):
        """R, Average utility discount rate

        Eq: 1 / (1 + ρ) ^ t

        Returns:
            :returns: Array of discount rates for utility
            :rtype: np.ndarray
        """
        return 1 / ((1 + self.params.prstp) ** (self.params.ts * self.params.t0))

    def utility(self, consumption_pc):
        """U, Period per capita utility function

        Eq: c ^ (1 - η) / (1 - η) + 1

        Args:
            :param consumption_pc: per capita consumption
             :type consumption_pc: float

        Returns:
            :returns: Per capita utility at t
            :rtype: float
        """
        if self.params.elasmu == 1:
            return np.log(consumption_pc)
        denom = 1.0 - self.params.elasmu
        return (consumption_pc ** denom / denom) + 1

    def utility_discounted(self, utility, utility_discount, l):
        """Total period utility

        Eq: R * L * U

        Args:
            :param utility: U(t)
             :type utility: float
            :param utility_discount: R(t)
             :type utility_discount: float
            :param l: L(t), population
             :type l: float

        Returns:
            :returns: Total period utility at t
            :rtype: float
        """
        return utility_discount * l * utility

    def get_model_values(self, index, data):
        """Get values for model variables.

        Args:
            :param i: current time step
            :type i: int
            :param df: Matrix of variables
            :type df: DiceDataMatrix

        Returns:
            :return: Model variables: U(t), RR(t)
            :rtype: tuple
        """
        utility = self.utility(data.consumption_pc[index])
        return (
            utility,
            self.utility_discounted(
                utility, self.utility_discount[index], data.population[index]
            )
        )


class Dice2007(UtilityModel):
    pass


class Dice2010(UtilityModel):
    pass


class Dice2013(Dice2010):
    def utility(self, consumption_pc):
        """U, Period utility function

        Eq: [c ^ (1 - η) - 1] / (1 - η) - 1

        Args:
            :param consumption_pc: per capita consumption
             :type consumption_pc: float

        Returns:
            :returns: Per capita utility at t
            :rtype: float
        """
        if self.params.elasmu == 1:
            return np.log(consumption_pc)
        denom = 1.0 - self.params.elasmu
        return (consumption_pc ** denom - 1) / denom - 1