from __future__ import division
import numexpr as ne


class TemperatureModel(object):
    """
    TemperatureModel base class
    ...
    Properties
    ----------
    initial_temps : array
        Values for T_AT, T_OCEAN at t=0
    ...
    Methods
    -------
    get_model_values()
        Return values for T_AT, T_OCEAN
    temp_atmosphere()
        Calculate T_AT at t
    temp_lower()
        Calculate T_OCEAN at t
    """
    def __init__(self, params):
        self.params = params
        self._temp_atmosphere_2005 = params.temp_atmosphere_2000
        self._temp_lower_2005 = params.temp_lower_2000
        self._forcing_co2_doubling = params.forcing_co2_doubling

    @property
    def initial_temps(self):
        return [self._temp_atmosphere_2005, self._temp_lower_2005]

    @initial_temps.setter
    def initial_temps(self, value):
        self._temp_atmosphere_2005 = value[0]
        self._temp_lower_2005 = value[1]

    def get_model_values(self, i, df):
        if i == 0:
            return self.initial_temps
        i -= 1
        return (
            self.temp_atmosphere(i, df),
            self.temp_lower(i, df),
        )

    def temp_atmosphere(self, i, df):
        """
        T_AT, Temperature of atmosphere, degrees C
        ...
        Returns
        -------
        float
        """
        ff = (self.params.forcing_co2_doubling / self.params.temp_co2_doubling)
        c1 = self.params.thermal_transfer[0]
        c3 = self.params.thermal_transfer[2]
        ta = df.temp_atmosphere[i]
        tl = df.temp_lower[i]
        f = df.forcing[i + 1]
        return ne.evaluate('ta + c1 * (f - ff * ta - c3 * (ta - tl))')

    def temp_lower(self, i, df):
        """
        T_LO, Temperature of lower oceans, degrees C
        ...
        Returns
        -------
        float
        """
        c4 = self.params.thermal_transfer[3]
        ta = df.temp_atmosphere[i]
        tl = df.temp_lower[i]
        return ne.evaluate('tl + c4 * (ta - tl)')


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
        ma0 = self.params.mass_atmosphere_2005
        mu0 = self.params.mass_upper_2005
        phi1 = self.params.carbon_matrix[0][0]
        phi2 = self.params.carbon_matrix[1][0]
        return (
            ne.evaluate('t0 + e0 * (t2c / ((2 * mpi - ma0 * phi1 - mu0 * phi2) * 1e-3 )) * 1e-3'),
            None
        )


class Dice2010(TemperatureModel):
    def __init__(self, params):
        super(Dice2010, self).__init__(params)

    def temp_atmosphere(self, temp_atmosphere, temp_lower, forcing):
        """
        T_AT, Temperature of atmosphere, degrees C
        ...
        Returns
        -------
        float
        """
        f = (self.params.forcing_co2_doubling / self.params.temp_co2_doubling)
        c1 = self.params.thermal_transfer[0]
        c3 = self.params.thermal_transfer[2]
        return (
            temp_atmosphere +
            c1 * (
                forcing - f *
                temp_atmosphere -
                c3 *
                (temp_atmosphere - temp_lower)
            )
        )
