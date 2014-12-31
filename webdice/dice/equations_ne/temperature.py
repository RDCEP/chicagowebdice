from __future__ import division
import numexpr as ne


class TemperatureModel(object):
    def __init__(self, params):
        self.params = params
        self._temp_atmosphere_2005 = params.temp_atmosphere_init
        self._temp_lower_2005 = params.temp_lower_init
        self._forcing_co2_doubling = params.forcing_co2_doubling

    @property
    def initial_temps(self):
        return [self._temp_atmosphere_2005, self._temp_lower_2005]

    @initial_temps.setter
    def initial_temps(self, value):
        self._temp_atmosphere_2005 = value[0]
        self._temp_lower_2005 = value[1]

    def temp_atmosphere(self, ta, tl, f):
        ff = (self.params.forcing_co2_doubling / self.params.temp_co2_doubling)
        c1 = self.params.thermal_transfer[0]
        c3 = self.params.thermal_transfer[2]
        return ne.evaluate('ta + c1 * (f - ff * ta - c3 * (ta - tl))')

    def temp_lower(self, ta, tl):
        c4 = self.params.thermal_transfer[3]
        return ne.evaluate('tl + c4 * (ta - tl)')

    def get_model_values(self, i, df):
        if i == 0:
            return self.initial_temps
        i -= 1
        return (
            self.temp_atmosphere(df.temp_atmosphere[i],
                                 df.temp_lower[i],
                                 df.forcing[i + 1],),
            self.temp_lower(df.temp_atmosphere[i],
                            df.temp_lower[i],)
        )


class Dice2007(TemperatureModel):
    pass


class LinearTemperature(TemperatureModel):
    def get_model_values(self, i, df):
        if i == 0:
            return self.initial_temps[0], None
        t0 = self.initial_temps[0]
        e0 = df.carbon_emitted[i - 1]
        t2c = self.params.temp_co2_doubling
        mpi = self.params.mass_preindustrial
        ma0 = self.params.mass_atmosphere_init
        mu0 = self.params.mass_upper_init
        phi1 = self.params.carbon_matrix[0][0]
        phi2 = self.params.carbon_matrix[1][0]
        return (
            ne.evaluate('t0 + e0 * (t2c / ((2 * mpi - ma0 * phi1 - mu0 * phi2) * 1e-3 )) * 1e-3'),
            None
        )


class Dice2010(TemperatureModel):
    pass


class Dice2013(Dice2010):
    pass