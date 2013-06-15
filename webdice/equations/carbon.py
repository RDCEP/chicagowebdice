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
        self._temp_atmosphere_2005 = params._temp_atmosphere_2000
        self._temp_lower_2005 = params._temp_lower_2000

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
            self._params._forcing_ghg_2000 + (np.ones(49) * .36),
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
            self.carbon_matrix[0][0] * mass_atmosphere + self.carbon_matrix[1][0] *
            mass_upper + (10 * emissions_total)
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
            self.carbon_matrix[0][1] * mass_atmosphere + self.carbon_matrix[1][1] *
            mass_upper + (self.carbon_matrix[2][1] * mass_lower)
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
            self.carbon_matrix[1][2] * mass_upper + self.carbon_matrix[2][2] * mass_lower
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
            np.log(
                data.mass_atmosphere[index] / self._mass_preindustrial
            ) + self.forcing_ghg[index]
        )

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

    def get_carbon_values(self, index, data):
        """
        Return values for M_AT, M_UP, M_LO
        ...
        Args
        ----
        emissions_total : float, E_total at t-1
        mass_atmosphere : float, M_AT at t-1
        mass_upper : float, M_UP at t-1
        mass_lower : float, M_LO at t-1
        ...
        Returns
        -------
        tuple
            M_AT, M_UP, M_LO at t
        """
        if index == 0:
            return self.initial_carbon
        i = index - 1
        return (
            self.mass_atmosphere(data.emissions_total[i],
                                 data.mass_atmosphere[i], data.mass_upper[i]),
            self.mass_upper(data.mass_atmosphere[i], data.mass_upper[i],
                            data.mass_lower[i]),
            self.mass_lower(data.mass_upper[i], data.mass_lower[i]),
        )

    def get_temperature_values(self, index, data):
        if index == 0:
            return self.initial_temps
        i = index - 1
        return (
            self.temp_atmosphere(
                data.temp_atmosphere[i], data.temp_lower[i], data.forcing[index],
                self._params._forcing_co2_doubling,
                self._params.temp_co2_doubling, self._params.thermal_transfer
            ),
            self.temp_lower(
                data.temp_atmosphere[i], data.temp_lower[i],
                self._params.thermal_transfer
            ),
        )


class DiceCarbon(CarbonModel):
    pass


class BeamCarbon(CarbonModel):
    """
    CarbonModel for simplified BEAM
    ...
    Methods
    -------
    get_h()
        Calculate H based on M_UP
    get_model_values()
        Set BEAM transfer matrix, and return values for M_AT, M_UP, M_LO
    """
    def __init__(self, params):
        CarbonModel.__init__(self, params)
        self.N = 20
        # self.initial_carbon = [808.9, 772.4, 38620.5]  # from BEAM paper
        # self.initial_carbon = [808.9, 571.5, 38620.5]  # M_UP at H = 10**-8.1
        self.initial_carbon = [808.9, 585, 38620.5]  # Nate's guess

    def get_h(self, mass_upper):
        """
        Calculate H based on M_UP
        ...
        Args
        ----
        mass_upper : float, M_UP at t-1
        ...
        Returns
        -------
        float
        """
        return 8.11054e-10 * mass_upper + 3.24421e-15 * np.sqrt(
            6.25e+10 * mass_upper ** 2 - 7.68281e+13 * mass_upper + 2.36815e+16
        ) - 5.0e-7

    def get_carbon_values(self, index, data):
        """
        Set BEAM transfer matrix, and return values for M_AT, M_UP, M_LO
        ...
        Args
        ----
        emissions_total : float, E_total at t-1
        mass_atmosphere : float, M_AT at t-1
        mass_upper : float, M_UP at t-1
        mass_lower : float, M_LO at t-1
        ...
        Returns
        -------
        tuple
            M_AT, M_UP, M_LO at t
        """
        if index == 0:
            return self.initial_carbon
        i = index - 1
        _ma, _mu, _ml = (
            data.mass_atmosphere[i], data.mass_upper[i], data.mass_lower[i]
        )
        for x in range(self.N):
            _h = self.get_h(_mu)
            _b = (28.944 * _h ** 2) / (_h ** 2 + _h * 1e-6 + 7.53e-16)
            self.carbon_matrix = np.array([
                -.2, .2, 0,
                _b, -_b - .05, .05,
                0, .001, -.001,
            ]).reshape(3, 3)
            _ma_incr = self.mass_atmosphere(
                data.emissions_total[i], _ma, _mu) / self.N
            _mu_incr = self.mass_upper(_ma, _mu, _ml) / self.N
            _ml_incr = self.mass_lower(_mu, _ml) / self.N
            _ma += _ma_incr
            _mu += _mu_incr
            _ml += _ml_incr
        return _ma, _mu, _ml