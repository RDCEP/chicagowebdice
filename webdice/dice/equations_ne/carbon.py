from __future__ import division
import numpy as np
import numexpr as ne
import __builtin__

try:
    __builtin__.profile
except AttributeError:
    def profile(func): return func
    __builtin__.profile = profile


class CarbonModel(object):
    def __init__(self, params):
        self.params = params
        self._carbon_matrix = params.carbon_matrix
        self._mass_atmosphere_init = params.mass_atmosphere_init
        self._mass_upper_init = params.mass_upper_init
        self._mass_lower_init = params.mass_lower_init
        self._mass_preindustrial = params.mass_preindustrial
        self._temp_atmosphere_2005 = params.temp_atmosphere_init
        self._temp_lower_2005 = params.temp_lower_init
        self._forcing_co2_doubling = params.forcing_co2_doubling

    @property
    def initial_carbon(self):
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
        return np.concatenate((
            self.params.forcing_ghg_init + .1 * (
                self.params.forcing_ghg_future - self.params.forcing_ghg_init
            ) * np.arange(11),
            self.params.forcing_ghg_future * np.ones(self.params.tmax - 11),
        ))

    def mass_atmosphere(self, emissions_total, mass_atmosphere, mass_upper):
        b11 = self.carbon_matrix[0][0]
        b12 = self.carbon_matrix[1][0]
        ts = self.params.ts
        return ne.evaluate('b11 * mass_atmosphere + b12 * mass_upper + ts * emissions_total')

    def mass_upper(self, mass_atmosphere, mass_upper, mass_lower):
        b21 = self.carbon_matrix[0][1]
        b22 = self.carbon_matrix[1][1]
        b23 = self.carbon_matrix[2][1]
        return ne.evaluate('b21 * mass_atmosphere + b22 * mass_upper + b23 * mass_lower')

    def mass_lower(self, mass_upper, mass_lower):
        b32 = self.carbon_matrix[1][2]
        b33 = self.carbon_matrix[2][2]
        return ne.evaluate('b32 * mass_upper + b33 * mass_lower')

    def forcing(self, i, df):
        fco2 = self.params.forcing_co2_doubling
        ma = df.mass_atmosphere[i]
        mpi = self.params.mass_preindustrial
        fg = self.forcing_ghg[i]
        return ne.evaluate('fco2 * (log(ma / mpi) / log(2)) + fg')

    def get_model_values(self, i, df):
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
        _dims = self.params.tmax + 1 if df.ndim > 2 else 1
        if i == 0:
            return (
                self.initial_carbon[0] * np.ones(_dims),
                self.initial_carbon[1] * np.ones(_dims),
                self.initial_carbon[2] * np.ones(_dims),
            )
        i -= 1
        self.carbon_matrix = np.tile(self.carbon_matrix_skel, _dims)
        ma, mu, ml = (df.mass_atmosphere[i], df.mass_upper[i], df.mass_lower[i])
        n = self.N
        for x in xrange(int(n)):
            h = ne.evaluate('5.21512e-10 * mu + 7.32749e-18 * sqrt(5.06546e15 * mu ** 2 - 7.75282e18 * mu + 2.97321e21) - 4e-7')
            b = ne.evaluate('142.349 / (1 + 8e-7 / h + 8e-7 * 4.53e-10 / h)')

            self.carbon_matrix[1][0] = b * .2
            self.carbon_matrix[1][1] = b * -.2 - .05
            _ma = self.mass_atmosphere(
                df.emissions_total[i], ma, mu)
            ma = ne.evaluate('ma + _ma / n')
            _mu = self.mass_upper(ma, mu, ml)
            mu = ne.evaluate('mu + _mu / n')
            _ml = self.mass_lower(mu, ml)
            ml = ne.evaluate('ml + _ml / n')
        return ma, mu, ml


class LinearCarbon(CarbonModel):
    def get_model_values(self, i, df):
        return (
            None, None, None
        )

    def forcing(self, i, df):
        return None


class Dice2010(CarbonModel):
    pass


class Dice2013(Dice2010):
    pass