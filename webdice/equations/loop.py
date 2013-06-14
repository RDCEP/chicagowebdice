import numpy as np
from damages import *
from carbon import *
from emissions import *
from consumption import *
from welfare import *
from productivity import *

class Loop(object):
    """Default equation set."""
    def __init__(self, params, damages_model=DiceDamages,
                 carbon_model=DiceCarbon):
        self._damages_model = damages_model
        self._carbon_model = carbon_model
        self._emissions_model = EmissionsModel(params)
        self._consumption_model = ConsumptionModel(params)
        self._welfare_model = UtilityModel(params)
        self._productivity_model = ProductivityModel(params)

    @property
    def damages_model(self):
        return self._damages_model

    @damages_model.setter
    def damages_model(self, value):
        self._damages_model = value

    @property
    def carbon_model(self):
        return self._carbon_model

    @carbon_model.setter
    def carbon_model(self, value):
        self._carbon_model = value

    @property
    def emissions_model(self):
        return self._emissions_model

    @emissions_model.setter
    def emissions_model(self, value):
        self._carbon_model = value

    @property
    def consumption_model(self):
        return self._consumption_model

    @consumption_model.setter
    def consumption_model(self, value):
        self._consumption_model = value

    @property
    def welfare_model(self):
        return self._welfare_model

    @welfare_model.setter
    def welfare_model(self, value):
        self._welfare_model = value

    @property
    def productivity_model(self):
        return self._productivity_model

    @productivity_model.setter
    def productivity_model(self, value):
        self._productivity_model = value

    def welfare(self, utility_discounted, utility_discount):
        """
        Objective function
        ...
        Returns
        -------
        float
        """
        return np.sum(utility_discounted)

    def miu(self, emissions_ind, emissions_cap, _e2005, intensity,
            gross_output):
        """
        mu, Emissions reduction rate
        ...
        Returns
        -------
        float
        """
        if emissions_cap == 0:
            return 1.
        elif round(emissions_ind, 2) < round((_e2005 * emissions_cap), 2):
            return 0.
        else: return 1 - ((_e2005 * emissions_cap) / (intensity * gross_output))

    def tax_rate(self, backstop, miu, abatement_exponent):
        """
        Implied tax rate, thousands $USD per ton CO_2
        ...
        Returns
        -------
        float
        """
        return (
            backstop * miu ** (abatement_exponent - 1) * 1000
        )