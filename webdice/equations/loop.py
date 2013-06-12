import numpy as np
from damages import *
from carbon import *

class Loop(object):
    """Default equation set."""
    def __init__(self, damages_model=DiceDamages, carbon_model=DiceCarbon):
        self._damages_model = damages_model
        self._carbon_model = carbon_model

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

    def capital(self, capital, depreciation, investment):
        """
        K(t), Capital, trillions $USD
        ...
        Returns
        -------
        Float
        """
        return capital * (1 - depreciation) ** 10 + 10 * investment

    def gross_output(self, productivity, capital, output_elasticty, population):
        """
        Gross output
        ...
        Returns
        -------
        float
        """
        return (
            productivity * capital ** output_elasticty *
            population ** (1 - output_elasticty)
        )

    def emissions_ind(self, intensity, miu, gross_output):
        """
        E_ind, Industrial emissions, GtC
        ...
        Returns
        -------
        float
        """
        return intensity * (1. - miu) * gross_output

    def emissions_total(self, emissions_ind, etree):
        """
        E, Total emissions, GtC
        ...
        Returns
        -------
        float
        """
        return emissions_ind + etree

    def forcing(self, _forcing_co2_doubling, mass_atmosphere,
                _mass_preindustrial, forcing_ghg):
        """
        F, Forcing, W/m^2
        ...
        Returns
        -------
        float
        """
        return (
            _forcing_co2_doubling *
            np.log(mass_atmosphere / _mass_preindustrial) + forcing_ghg
        )
        # return _forcing_co2_doubling * (np.log((
        #     ((mass_atmosphere + ma_next) / 2) + .000001
        # ) / _mass_preindustrial) / np.log(2)) + forcing_ghg

    def temp_atmosphere(self, temp_atmosphere, temp_lower, forcing,
                        _forcing_co2_doubling, temp_co2_doubling,
                        thermal_transfer):
        """
        T_AT, Temperature of atmosphere, degrees C
        ...
        Returns
        -------
        float
        """
        return (
            temp_atmosphere + thermal_transfer[0] * (
                forcing - (_forcing_co2_doubling / temp_co2_doubling) *
                temp_atmosphere - thermal_transfer[2] *
                (temp_atmosphere - temp_lower)
            )
        )

    def temp_lower(self, temp_atmosphere, temp_lower, thermal_transfer):
        """
        T_LO, Temperature of lower oceans, degrees C
        ...
        Returns
        -------
        float
        """
        return (
            temp_lower + thermal_transfer[3] * (temp_atmosphere - temp_lower)
        )

    def abatement(self, gross_output, miu, backstop_growth, abatement_exponent,
                  participation):
        """
        Lambda, Abatement costs, trillions $USD
        ...
        Returns
        -------
        float
        """
        return (
            gross_output * participation ** (1 - abatement_exponent) *
            backstop_growth * miu ** abatement_exponent
        )

    def investment(self, savings, output):
        """
        I, Investment, trillions $USD
        ...
        Returns
        -------
        float
        """
        return savings * output

    def consumption_pc(self, consumption, population):
        """
        c, Per capita consumption, thousands $USD
        ...
        Returns
        -------
        float
        """
        return 1000 * consumption / population

    def consumption_discount(self, prstp, population, elasmu, c0, c1, i):
        """Discount rate for consumption"""
        return 1 / (
            1 + (prstp * 100 + elasmu * (
                (c1 - c0) / 10 / c0
            )) / 100
        ) ** (10 * i)

        # Ramsey discount from SCC paper
        # return np.exp(-(elasmu / (i + .000001) * np.log(
        #     c1 / c0) / 10 + prstp) * i * 10)

        # Constant rate from SCC paper
        # return 1 / ((1 + .03) ** (i * 10))

    def utility(self, consumption_pc, elasmu, population):
        """
        U, Period utility function
        ...
        Returns
        -------
        float
        """
        return (
            (1 / (1 - elasmu + .000001)) * consumption_pc ** (1 - elasmu) + 1
        )

    def utility_discounted(self, utility, utility_discount, l):
        """
        Utility discounted
        ...
        Returns
        -------
        float
        """
        return utility_discount * l * utility

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