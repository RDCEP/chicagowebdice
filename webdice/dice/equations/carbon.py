# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import numexpr as ne


class CarbonModel(object):
    def __init__(self, params):
        self.params = params
        self._carbon_matrix = params.carbon_matrix
        self._mass_atmosphere_init = params.mass_atmosphere_init
        self._mass_upper_init = params.mass_upper_init
        self._mass_lower_init = params.mass_lower_init
        self._mass_preindustrial = params.mass_preindustrial
        self._temp_atmosphere_init = params.temp_atmosphere_init
        self._temp_lower_init = params.temp_lower_init
        self._forcing_co2_doubling = params.forcing_co2_doubling

    @property
    def initial_carbon(self):
        """Carbon mass at t=0

        Returns:
            :return: [ M_{AT}(0), M_{UP}(0), M_{LO}(0) ]
             :rtype: tuple
        """
        return (
            self._mass_atmosphere_init,
            self._mass_upper_init,
            self._mass_lower_init,
        )

    @initial_carbon.setter
    def initial_carbon(self, value):
        self._mass_atmosphere_init = value[0]
        self._mass_upper_init = value[1]
        self._mass_lower_init = value[2]

    @property
    def carbon_matrix(self):
        """Carbon transfer matrix

        Returns:
            :return: 3 x 3 matrix for φ_{i,j}
             :rtype: np.ndarray
        """
        return self._carbon_matrix

    @carbon_matrix.setter
    def carbon_matrix(self, value):
        self._carbon_matrix = value

    @property
    def initial_temps(self):
        """Temperature at t=0

        Returns:
            :return: [ T_{AT}(0), T_{LO}(0) ]
             :rtype: tuple
        """
        return (self._temp_atmosphere_init, self._temp_lower_init)

    @initial_temps.setter
    def initial_temps(self, value):
        self._temp_atmosphere_init = value[0]
        self._temp_lower_init = value[1]

    @property
    def forcing_ghg(self):
        """F_EX, Exogenous forcing for other greenhouse gases

        Eq:

        Returns:
            :return: Array of non-CO2 GHG forcing values
             :rtype: np.ndarray
        """
        return np.concatenate((
            self.params.forcing_ghg_init + .1 * (
                self.params.forcing_ghg_future - self.params.forcing_ghg_init
            ) * np.arange(11),
            self.params.forcing_ghg_future * np.ones(self.params.tmax-11),
        ))

    def mass_atmosphere(self, emissions_total, mass_atmosphere, mass_upper):
        """M_{AT}, Carbon concentration in atmosphere, GtC

        Eq:

        Args:
            :param emissions_total: Total emissions
             :type emissions_total: float
            :param mass_atmosphere: Atmospheric carbon mass at (t - 1)
             :type mass_atmosphere: float
            :param mass_upper: Upper ocean carbon mass at (t - 1)
             :type mass_upper: float

        Returns:
            :return: M_{AT}(t)
             :rtype: float
        """
        return (
            self.carbon_matrix[0][0] * mass_atmosphere +
            self.carbon_matrix[1][0] * mass_upper +
            self.params.ts * emissions_total
        )

    def mass_upper(self, mass_atmosphere, mass_upper, mass_lower):
        """M_{UP}, Carbon concentration in upper ocean, GtC

        Eq:

        Args:
            :param mass_atmosphere: Atmospheric carbon mass at (t - 1)
             :type mass_atmosphere: float
            :param mass_upper: Upper ocean carbon mass at (t - 1)
             :type mass_upper: float
            :param mass_lower: Lower ocean carbon mass at (t - 1)
             :type mass_lower: float

        Returns:
            :return: M_{UP}(t)
             :rtype: float
        """
        return (
            self.carbon_matrix[0][1] * mass_atmosphere +
            self.carbon_matrix[1][1] * mass_upper +
            self.carbon_matrix[2][1] * mass_lower
        )

    def mass_lower(self, mass_upper, mass_lower):
        """M_{LO}, Carbon concentration in lower ocean, GtC

        Eq:

        Args:
            :param mass_upper: Upper ocean carbon mass at (t - 1)
             :type mass_upper: float
            :param mass_lower: Lower ocean carbon mass at (t - 1)
             :type mass_lower: float

        Returns:
            :return: M_{LO}(t)
             :rtype: float
        """
        return (
            self.carbon_matrix[1][2] * mass_upper +
            self.carbon_matrix[2][2] * mass_lower
        )

    def forcing(self, i, df):
        """Forcing equation

        F, Forcing, W/m^2

        Returns:
            float: Forcing

        """
        return (
            self.params.forcing_co2_doubling *
            (np.log(
                df.mass_atmosphere[i] / self.params.mass_preindustrial
            ) / np.log(2)) + self.forcing_ghg[i]
        )

    def get_model_values(self, i, df):
        """Get values for model variables.

        Args:
            :param i: current time step
             :type i: int
            :param df: Matrix of variables
             :type df: DiceDataMatrix

        Returns:
            :return: Model variables: M_{AT}, M_{UP}, M_{LO}
             :rtype: tuple
        """
        if i == 0:
            return self.initial_carbon
        i -= 1
        ma = df.mass_atmosphere[i]
        mu = df.mass_upper[i]
        ml = df.mass_lower[i]
        return (
            self.mass_atmosphere(df.emissions_total[i], ma, mu),
            self.mass_upper(ma, mu, ml),
            self.mass_lower(mu, ml),
        )


class Dice2007(CarbonModel):
    pass


class BeamCarbon(CarbonModel):
    """CarbonModel for simplified BEAM

    Methods:
        get_model_values()
            Set BEAM transfer matrix, and return values for M_AT, M_UP, M_LO

    """
    def __init__(self, params):
        CarbonModel.__init__(self, params)
        self.N = self.params.ts * 2
        self.initial_carbon = [808.9, 725, 35641]
        self.carbon_matrix_skel = np.array([
            -.2, .2, 0,
            .2, -.2, .05,
            0, .001, -.001,
        ]).reshape((3, 3, 1))

    def get_model_values(self, i, df):
        """
        -----------------------------------
        Background regarding BEAM equations
        -----------------------------------
        k_a = .2       /yr
        k_d = .05      /yr
        delta = 50
        k_h = 1.91e3
        k_1 = 8e-7
        k_2 = 4.53e-10
        AM = 1.77e20   mol
        OM = 7.8e22    mol
        Alk = 767.0
        _a = k_h * (AM / (OM * (delta + 1)))
        """
        _dims = self.params.tmax + 1 if df.ndim > 2 else 1
        if i == 0:
            return (
                self.initial_carbon[0] * np.ones(_dims),
                self.initial_carbon[1] * np.ones(_dims),
                self.initial_carbon[2] * np.ones(_dims),
            )
        i -= 1
        self.carbon_matrix = np.tile(self.carbon_matrix_skel, _dims)
        ma, mu, ml = (df.mass_atmosphere[i], df.mass_upper[i],
                         df.mass_lower[i])
        for x in xrange(int(self.N)):
            h = ne.evaluate('5.21512e-10 * mu + 7.32749e-18 * sqrt(5.06546e15 * mu ** 2 - 7.75282e18 * mu + 2.97321e21) - 4e-7')
            b = ne.evaluate('142.349 / (1 + 8e-7 / h + 8e-7 * 4.53e-10 / h)')

            self.carbon_matrix[1][0] = b * .2
            self.carbon_matrix[1][1] = b * -.2 - .05
            ma += self.mass_atmosphere(
                df.emissions_total[i], ma, mu) / self.N
            mu += self.mass_upper(ma, mu, ml) / self.N
            ml += self.mass_lower(mu, ml) / self.N
        return ma, mu, ml


class LinearCarbon(CarbonModel):
    """CarbonModel for Linear Carbon / Temp
    """

    def get_model_values(self, i, df):
        return (
            None, None, None
        )

    def forcing(self, i, df):
        return None


class Dice2010(CarbonModel):
    pass


class Dice2013(CarbonModel):
    pass