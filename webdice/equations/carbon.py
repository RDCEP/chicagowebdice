import numpy as np

class CarbonModel(object):
    """
    CarbonModel base class
    ...
    Properties
    ----------
    initial_carbon : tuple
        Values for M_AT, M_UP, and M_LO at t=0
    Methods
    -------
    mass_atmosphere()
        Calculate M_AT at t
    mass_upper()
        Calculate M_UP at t
    mass_lower()
        Calculate M_LO at t
    get_model_values()
        Return values for M_AT, M_UP, M_LO
    forcing()
        Calculate forcing at t
    """
    def __init__(self, _mass_atmosphere, _mass_upper, _mass_lower, _mass_pre):
        _b11, _b12, _b13 = .810712, .189288, 0
        _b21, _b22, _b23 = .097213, .852787, .05
        _b31, _b32, _b33 = 0, .003119, .996881
        self._carbon_matrix = np.array([
            _b11, _b12, _b13,
            _b21, _b22, _b23,
            _b31, _b32, _b33,
        ]).reshape(3, 3)
        self._mass_atmosphere_2005 = _mass_atmosphere
        self._mass_upper_2005 = _mass_upper
        self._mass_lower_2005 = _mass_lower
        self._mass_preindustrial = _mass_pre

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

    def get_model_values(self, emissions_total, mass_atmosphere,
                          mass_upper, mass_lower):
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
        return (
            self.mass_atmosphere(emissions_total, mass_atmosphere, mass_upper),
            self.mass_upper(mass_atmosphere, mass_upper, mass_lower),
            self.mass_lower(mass_upper, mass_lower),
        )

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

    def forcing(self, _forcing_co2_doubling, mass_atmosphere, forcing_ghg):
        """
        F, Forcing, W/m^2
        ...
        Returns
        -------
        float
        """
        return (
            _forcing_co2_doubling *
            np.log(mass_atmosphere / self._mass_preindustrial) + forcing_ghg
        )
        # return _forcing_co2_doubling * (np.log((
        #     ((mass_atmosphere + ma_next) / 2) + .000001
        # ) / _mass_preindustrial) / np.log(2)) + forcing_ghg


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
    def __init__(self, _mass_atmosphere, _mass_upper, _mass_lower, _mass_pre):
        CarbonModel.__init__(
            self, _mass_atmosphere, _mass_upper, _mass_lower, _mass_pre
        )
        self.N = 20

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
        # sympy
        return 8.11054e-10 * mass_upper + 3.24421e-15 * np.sqrt(
            6.25e+10 * mass_upper ** 2 - 7.68281e+13 * mass_upper + 2.36815e+16
        ) - 5.0e-7

        # wolfram alpha
        # return 8.11054e-10 * mass_upper + 5.07187e-24 * np.sqrt(
        #     2.55719e+28 * mass_upper**2-3.14342e+31 * mass_upper + 9.68932e+33
        # ) - 5.e-7

        # mathematica
        # return -5e-7 + 8.24427e-10 * mass_upper + 1.40633e-25 * np.sqrt(
        #     1.26024e+37 - 4.15591e+34 * mass_upper + 3.43659e+31 * \
        #     mass_upper ** 2
        # )

    def get_model_values(self, emissions_total, mass_atmosphere,
                         mass_upper, mass_lower):
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
        _ma, _mu, _ml = mass_atmosphere, mass_upper, mass_lower
        for i in range(self.N):
            _h = self.get_h(_mu)
            _b = (28.944 * _h ** 2) / (_h ** 2 + _h * 1e-6 + 7.53e-16)
            self.carbon_matrix = np.array([
                -.2, .2, 0,
                _b, -_b - .05, .05,
                0, .001, -.001,
            ]).reshape(3, 3)
            _ma_incr = self.mass_atmosphere(emissions_total, _ma, _mu) / self.N
            _mu_incr = self.mass_upper(_ma, _mu, _ml) / self.N
            _ml_incr = self.mass_lower(_mu, _ml) / self.N
            _ma += _ma_incr
            _mu += _mu_incr
            _ml += _ml_incr
        return _ma, _mu, _ml
