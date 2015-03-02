# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np


class UtilityModel(object):
    """
    UtilityModel base class
    ...
    Properties
    ----------
    utility_discount : array
        Average utility discount rate
    ...
    Methods
    -------
    get_model_values()
    utility()
    utility_discounted()
    """
    def __init__(self, params):
        self.params = params

    @property
    def utility_discount(self):
        """R, Average utility discount rate

        Returns:
            :returns: 1 / (1 + ρ) ^ (t-1)
            :rtype: np.ndarray
        """
        return 1 / ((1 + self.params.prstp) ** (10 * self.params.t0))

    def get_model_values(self, index, data):
        utility = self.utility(data.consumption_pc[index])
        return (
            utility,
            self.utility_discounted(
                utility, self.utility_discount[index], data.population[index]
            )
        )

    def utility(self, consumption_pc):
        """U, Period utility function

        Args:
            :param consumption_pc: per capita consumption
             :type consumption_pc: float

        Returns:
            :returns: c ^ (1 - η) / (1 - η) + 1
            :rtype: float
        """
        if self.params.elasmu == 1:
            return np.log(consumption_pc)
        denom = 1.0 - self.params.elasmu
        return (consumption_pc ** denom / denom) + 1

    def utility_discounted(self, utility, utility_discount, l):
        """Utility discounted

        Args:
            :param utility: U(t)
             :type utility: float
            :param utility_discount: R(t)
             :type utility_discount: float
            :param l: L(t), population
             :type l: float

        Returns:
            :returns: R * L * U
            :rtype: float
        """
        return utility_discount * l * utility


class Dice2007(UtilityModel):
    pass


class Dice2010(UtilityModel):
    pass