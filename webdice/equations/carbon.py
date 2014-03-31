from __future__ import division
import numpy as np


class CarbonModel(object):
    """
    CarbonModel base class
    ...
    Properties
    ----------
    initial_carbon : tuple
        Values for M_AT, M_UP, and M_LO at t=0
    carbon_matrix : array
        Carbon transfer coefficients
    forcing_ghg : array
        Forcing for GHGs
    ...
    Methods
    -------
    get_model_values()
        Return values for M_AT, M_UP, M_LO
    mass_atmosphere()
        Calculate M_AT at t
    mass_upper()
        Calculate M_UP at t
    mass_lower()
        Calculate M_LO at t
    forcing()
        Calculate forcing at t
    """
    def __init__(self, params):
        self._params = params
        self._carbon_matrix = params._carbon_matrix
        self._mass_atmosphere_2005 = params._mass_atmosphere_2005
        self._mass_upper_2005 = params._mass_upper_2005
        self._mass_lower_2005 = params._mass_lower_2005
        self._mass_preindustrial = params._mass_preindustrial
        self._temp_atmosphere_2005 = params._temp_atmosphere_2000
        self._temp_lower_2005 = params._temp_lower_2000
        self._forcing_co2_doubling = params._forcing_co2_doubling

    @property
    def initial_carbon(self):
        return (
            self._mass_atmosphere_2005,
            self._mass_upper_2005,
            self._mass_lower_2005,
        )

    @initial_carbon.setter
    def initial_carbon(self, value):
        self._mass_atmosphere_2005 = value[0]
        self._mass_upper_2005 = value[1]
        self._mass_lower_2005 = value[2]

    @property
    def carbon_matrix(self):
        return self._carbon_matrix

    @carbon_matrix.setter
    def carbon_matrix(self, value):
        self._carbon_matrix = value

    @property
    def initial_temps(self):
        return [self._temp_atmosphere_2005, self._temp_lower_2005]

    @initial_temps.setter
    def initial_temps(self, value):
        self._temp_atmosphere_2005 = value[0]
        self._temp_lower_2005 = value[1]

    @property
    def forcing_ghg(self):
        """
        F_EX, Exogenous forcing for other greenhouse gases
        ...
        Returns
        -------
        array
        """
        return np.concatenate((
            self._params._forcing_ghg_2000 + .1 * (
                self._params._forcing_ghg_2100 - self._params._forcing_ghg_2000
            ) * np.arange(11),
            self._params._forcing_ghg_2100 * np.ones(49),
        ))

    def mass_atmosphere(self, emissions_total, mass_atmosphere, mass_upper):
        """
        M_AT, Carbon concentration in atmosphere, GtC
        ...
        Returns
        -------
        float
        """
        return (
            self.carbon_matrix[0][0] * mass_atmosphere +
            self.carbon_matrix[1][0] * mass_upper +
            10 * emissions_total
        )

    def mass_upper(self, mass_atmosphere, mass_upper, mass_lower):
        """
        M_UP, Carbon concentration in shallow oceans, GtC
        ...
        Returns
        -------
        float
        """
        return (
            self.carbon_matrix[0][1] * mass_atmosphere +
            self.carbon_matrix[1][1] * mass_upper +
            self.carbon_matrix[2][1] * mass_lower
        )

    def mass_lower(self, mass_upper, mass_lower):
        """
        M_LO, Carbon concentration in lower oceans, GtC
        ...
        Returns
        -------
        float
        """
        return (
            self.carbon_matrix[1][2] * mass_upper +
            self.carbon_matrix[2][2] * mass_lower
        )

    def forcing(self, index, data):
        """
        F, Forcing, W/m^2
        ...
        Returns
        -------
        float
        """
        return (
            self._forcing_co2_doubling *
            (np.log(
                data.mass_atmosphere[index] / self._mass_preindustrial
            ) / np.log(2)) + self.forcing_ghg[index]
        )

    def get_model_values(self, index, data):
        """
        Return values for M_AT, M_UP, M_LO
        ...
        Args
        ----
        index : int
        data : pd.DataFrame
        ...
        Returns
        -------
        tuple
            M_AT, M_UP, M_LO at t
        """
        if index == 0:
            return (data.mass_atmosphere.ix[:][index] / data.mass_atmosphere.ix[:][index] * self.initial_carbon[0],
                data.mass_upper.ix[:][index] / data.mass_upper.ix[:][index] * self.initial_carbon[1],
                data.mass_lower.ix[:][index] / data.mass_lower.ix[:][index] * self.initial_carbon[2])
            # return self.initial_carbon
        i = index - 1
        return (
            self.mass_atmosphere(data.emissions_total[i],
                                 data.mass_atmosphere[i], data.mass_upper[i]),
            self.mass_upper(data.mass_atmosphere[i], data.mass_upper[i],
                            data.mass_lower[i]),
            self.mass_lower(data.mass_upper[i], data.mass_lower[i]),
        )


class Dice2007(CarbonModel):
    pass


class BeamCarbon(CarbonModel):
    """
    CarbonModel for simplified BEAM
    ...
    Methods
    -------
    get_model_values()
        Set BEAM transfer matrix, and return values for M_AT, M_UP, M_LO
    """
    def __init__(self, params):
        CarbonModel.__init__(self, params)
        self.N = 20
        self.initial_carbon = [808.9, 725, 35641]
        self._carbon_matrix_skel = np.array([
            -.2, .2, 0,
            .2, -.2, .05,
            0, .001, -.001,
        ]).reshape((3, 3, 1))

    def get_model_values(self, index, data):
        """
        Set BEAM transfer matrix, and return values for M_AT, M_UP, M_LO
        ...
        Args
        ----
        index : int
        data : pd.DataFrame
        ...
        Returns
        -------
        tuple
            M_AT, M_UP, M_LO at t
        ...
        -----------------------------------
        Background regarding BEAM equations
        -----------------------------------
        k_a = .2       /yr
        k_d = .05      /yr
        delta = 50
        k_h = 1.91e3
        k_1 = 1e-6     mol/kg
        k_2 = 7.53e-10 mol/kg
        AM = 1.77e20   mol
        OM = 7.8e22    mol
        Alk = 662.7    GtC
        _a = k_h * (AM / (OM * (delta + 1)))
        """
        # if opt: self.N = 2
        _dims = 61 if data.ndim > 2 else 1
        if index == 0:
            return (
                self.initial_carbon[0] * np.ones(_dims),
                self.initial_carbon[1] * np.ones(_dims),
                self.initial_carbon[2] * np.ones(_dims),
            )
        self.carbon_matrix = np.tile(self._carbon_matrix_skel, _dims)
        i = index - 1
        _ma, _mu, _ml = (
            data.mass_atmosphere[i], data.mass_upper[i], data.mass_lower[i]
        )
        for x in xrange(self.N):
            _h = 5.21512e-10 * _mu + 7.32749e-18 * np.sqrt(
                5.06546e15 * _mu ** 2 - 7.75282e18 * _mu + 2.97321e21
            ) - 4e-7
            _b = 142.349 / (1 + 8e-7 / _h + 8e-7 * 4.53e-10 / _h)
            self.carbon_matrix[1][0] = _b * .2
            self.carbon_matrix[1][1] = _b * -.2 - .05
            _ma += self.mass_atmosphere(
                data.emissions_total[i], _ma, _mu) / self.N
            _mu += self.mass_upper(_ma, _mu, _ml) / self.N
            _ml += self.mass_lower(_mu, _ml) / self.N
        return _ma, _mu, _ml


class LinearCarbon(CarbonModel):
    def get_model_values(self, index, data):
        return (
            None, None, None
        )

    def forcing(self, index, data):
        return None


class Dice2010(CarbonModel):
    @property
    def forcing_ghg(self):
        """
        F_EX, Exogenous forcing for other greenhouse gases
        ...
        Returns
        -------
        array
        """
        return np.concatenate((
            self._params._forcing_ghg_2000 + .1 * (
                self._params._forcing_ghg_2100 - self._params._forcing_ghg_2000
            ) * np.arange(11),
            self._params._forcing_ghg_2000 * (np.ones(49) * .36),
        ))