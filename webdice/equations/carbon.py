import numpy as np

class CarbonModel(object):
    def __init__(self):
        _b11, _b12, _b13 = .810712, .189288, 0
        _b21, _b22, _b23 = .097213, .852787, .05
        _b31, _b32, _b33 = 0, .003119, .996881
        self._carbon_matrix = np.array([
            _b11, _b12, _b13,
            _b21, _b22, _b23,
            _b31, _b32, _b33,
        ]).reshape(3, 3)
        self._mass_atmosphere_2005 = 808.9
        self._mass_upper_2005 = 1255.
        self._mass_lower_2005 = 18365.

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
        return [
            self.mass_atmosphere(emissions_total, mass_atmosphere, mass_upper),
            self.mass_upper(mass_atmosphere, mass_upper, mass_lower),
            self.mass_lower(mass_upper, mass_lower),
        ]


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


class DiceCarbon(CarbonModel):
    pass


class BeamCarbon(CarbonModel):
    def __init__(self):
        CarbonModel.__init__(self)
        self.N = 20
        self.initial_carbon = [808.9, 772.4, 38620.5]

    def get_h(self, mass_upper):
        #sympy
        return 8.11054e-10 * mass_upper + 3.24421e-15 * np.sqrt(
            6.25e+10 * mass_upper ** 2 - 7.68281e+13 * mass_upper + 2.36815e+16
        ) - 5.0e-7

        #wolfram alpha
        # return 8.11054e-10 * mass_upper + 5.07187e-24 * np.sqrt(
        #     2.55719e+28 * mass_upper**2-3.14342e+31 * mass_upper + 9.68932e+33
        # ) - 5.e-7

        #mathematica
        #return -5e-7 + 8.24427e-10 * mass_upper + 1.40633e-25 * np.sqrt(
        #    1.26024e+37 - 4.15591e+34 * mass_upper + 3.43659e+31 * mass_upper ** 2
        #)

    def get_model_values(self, emissions_total, mass_atmosphere,
                          mass_upper, mass_lower):
        _ma, _mu, _ml = mass_atmosphere, mass_upper, mass_lower
        for i in range(self.N):
            _h = self.get_h(_mu)
            _b = (28.944 * _h ** 2) / (_h ** 2 + _h * 10e-6 + 7.53e-16)
            self.carbon_matrix = np.array([
                -.2, .2, 0,
                _b, -_b - .05, .05,
                0, .001, -.001,
            ]).reshape(3, 3)
            _maa = self.mass_atmosphere(emissions_total, _ma, _mu) / self.N
            _muu = self.mass_upper(_ma, _mu, _ml) / self.N
            _mll = self.mass_lower(_mu, _ml) / self.N
            _ma += _maa
            _mu += _muu
            _ml += _mll
        return [_ma, _mu, _ml]
