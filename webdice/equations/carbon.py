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

    def get_h(self, mass_upper):
        return -5e-7 + 8.24427e-10 * mass_upper + 1.40633e-25 * np.sqrt(
            1.26024e+37 - 4.15591e+34 * mass_upper + 3.43659e+31 * mass_upper ** 2
        )

    def get_model_values(self, emissions_total, mass_atmosphere,
                          mass_upper, mass_lower):
        _ma, _mu, _ml = mass_atmosphere, mass_upper, mass_lower
        for i in range(self.N):
            _h = self.get_h(_mu)
            _b12 = (28.944 * _h ** 2) / (_h ** 2 + _h / 10 ** 6 + 7.53 * 10 ** -16)
            self.carbon_matrix = np.array([
                -.2, _b12, 0,
                .2,  -_b12 - .05, .001,
                0, .05, -.001
            ]).reshape(3, 3)
            _ma += self.mass_atmosphere(emissions_total, _ma, _mu) / self.N
            _mu += self.mass_upper(_ma, _mu, _ml) / self.N
            _ml += self.mass_lower(_mu, _ml) / self.N
        return [_ma, _mu, _ml]