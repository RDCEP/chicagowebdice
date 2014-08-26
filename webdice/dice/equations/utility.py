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
        """
        R, Average utility discount rate
        ...
        Returns
        -------
        array
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
        """
        U, Period utility function
        ...
        Returns
        -------
        float
        """
        if self.params.elasmu == 1:
            return np.log(consumption_pc)
        if consumption_pc == 0:
            # If consumption[t] = 0 (eg, if abatement = output), utility = 0
            return 0
        denom = 1.0 - self.params.elasmu
        return (1 / denom) * (consumption_pc ** denom - 1)

    def utility_discounted(self, utility, utility_discount, l):
        """
        Utility discounted
        ...
        Returns
        -------
        float
        """
        return utility_discount * l * utility


class Dice2007(UtilityModel):
    pass


class Dice2010(UtilityModel):
    pass