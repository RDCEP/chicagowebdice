# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np


class EmissionsModel(object):
    """
    EmissionsModel base class

    Properties:
        emissions_deforest: Emission from deforestation
        emissions_cap: Emissions caps for treaty
        user_tax_rate: Array of user-determined annual tax rates

    Methods:
        get_model_values()
        emissions_ind()
        emissions_total()
        carbon_emitted()
        get_miu()
        miu()
        tax_rate()
    """
    def __init__(self, params):
        self.params = params

    @property
    def emissions_deforest(self):
        """E_land, Emissions from deforestation

        Returns
            :returns: E_land(0) * (1 - .1) ^ (t - 1)
            :rtype: np.ndarray
        """
        return (
            self.params.emissions_deforest_2005 *
            (1 - .1) ** self.params.t0
        )

    @property
    def emissions_cap(self):
        """E_cap, Emissions caps from treaty inputs

        Returns
            :returns: Array of emissions caps
            :rtype: np.ndarray
        """
        return np.concatenate((
            np.ones(5),
            (np.ones(5) * (1 - self.params.e2050)),
            (np.ones(5) * (1 - self.params.e2100)),
            (np.ones(45) * (1 - self.params.e2150)),
        ))

    @property
    def user_tax_rate(self):
        """Optional user-defined carbon tax

        Returns
            :returns: Array of tax rates
            :rtype: np.ndarray
        """
        c = [0, self.params.c2050, self.params.c2100,
             self.params.c2150, self.params.cmax]
        return np.concatenate((
            c[0] + ((c[1] - c[0]) / 5 * np.arange(5)),
            c[1] + ((c[2] - c[1]) / 5 * np.arange(5)),
            c[2] + ((c[3] - c[2]) / 5 * np.arange(5)),
            c[3] + ((c[3] - c[2]) / 5 * np.arange(45)),
        ))

    def get_model_values(self, i, df, deriv=False, opt=False,
                         miu=None, emissions_shock=0):
        """Get values for model variables.

        Args:
            :param i: current time step
            :type i: int
            :param df: Matrix of variables
            :type df: DiceDataMatrix

        Kwargs:
            :param deriv: Calculating derivative or not
            :type deriv: bool
            :param opt: Running optimized loop or not
            :type opt: bool
            :param miu: Emissions control array
            :type miu: np.ndarray
            :param emissions_shock: Amount to increase emissions for SCC
            :type emissions_shock: float

        Returns:
            :return: Model variables: μ, E_ind, E, CCum, τ
            :rtype: tuple
        """
        miu = self.get_miu(i, df, deriv=deriv, opt=opt, miu=miu)
        emissions_ind = self.emissions_ind(
            df.carbon_intensity[i], miu, df.gross_output[i]
        )
        emissions_total = self.emissions_total(
            emissions_ind, self.emissions_deforest[i]
        ) + emissions_shock
        carbon_emitted = emissions_total * 10 \
            if i == 0 \
            else self.carbon_emitted(emissions_total, df.carbon_emitted[i - 1])
        if np.max(carbon_emitted) > self.params.fosslim:
            emissions_total = 0.0
            carbon_emitted = self.params.fosslim
        tax_rate = self.tax_rate(miu, df.backstop[i])
        return (
            miu,
            emissions_ind,
            emissions_total,
            carbon_emitted,
            tax_rate,
        )

    def emissions_ind(self, intensity, miu, gross_output):
        """E_ind, Industrial emissions, GtC

        Args:
            :param intensity:
             :type intensity: float
            :param miu:
             :type intensity: float
            :param gross_output:
             :type intensity: float

        Returns:
            :return: σ(t) * (1 - μ) * Q
             :rtype: float
        """

        return intensity * (1 - miu) * gross_output

    def emissions_total(self, emissions_ind, etree):
        """E, Total emissions, GtC

        Args:
            :param emissions_ind: Industrial emissions
             :type emissions_ind: float
            :param etree: Emissions from deforestation
             :type etree: float

        Returns:
            :return: E_ind + E_tree
             :rtype: float
        """
        return emissions_ind + etree

    def carbon_emitted(self, emissions_total, carbon_emitted):
        """CCum, Total carbon emitted, GtC

        Args:
            :param emissions_total: E(t)
             :type emissions_total: float
            :param carbon_emitted: CCum(t-1)
             :type carbon_emitted: float

        Returns:
            :return: CCum + E(t)
             :rtype: float
        """
        return carbon_emitted + emissions_total * 10

    def get_miu(self, i, df, deriv=False, opt=False, miu=None):
        """μ, get miu for optimized, treaty, tax scenarios

        Args:
            :param i:
            :param df:
            :param deriv:
            :param opt:
            :param miu:

        Returns:
            :return:
        """
        if opt:
            if miu is not None:
                if deriv:
                    return miu
                return miu[i]
        elif miu is None:
            if i > 0:
                if df.carbon_emitted[i - 1] > self.params.fosslim:
                    return 1.0
                if self.params.treaty:
                    return min(self.miu(
                        df.emissions_ind[i - 1],
                        self.emissions_cap[i - 1],
                        df.emissions_ind[0],
                        df.carbon_intensity[i], df.gross_output[i]
                    ), 1.0)
                elif self.params.carbon_tax:
                    return min(
                        (self.user_tax_rate[i] / (
                            df.backstop[i] * 1000)) ** (
                            1 / (self.params.abatement_exponent - 1)),
                        1.0
                    )
                else:
                    return 0
            else:
                return self.params.miu_2005
        else:
            return min(miu[i], 1.0)
        return min(df.miu[i], 1.0)

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
            return 1
        # elif round(emissions_ind, 2) < round((_e2005 * emissions_cap), 2):
        #     return 0
        return 1 - ((_e2005 * emissions_cap) / (intensity * gross_output))

    def tax_rate(self, miu, backstop):
        """
        Implied tax rate, thousands $USD per ton CO_2
        ...
        Returns
        -------
        float
        """
        return (
            backstop * miu ** (self.params.abatement_exponent - 1) * 1000
        ) * (12 / 44)


class Dice2007(EmissionsModel):
    pass


class Dice2010(EmissionsModel):
    @property
    def emissions_deforest(self):
        """
        E_land, Emissions from deforestation
        ...
        Returns
        -------
        array
        """
        return (
            self.params.emissions_deforest_2005 *
            .8 ** self.params.t0
        )