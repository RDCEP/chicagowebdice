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
        return (
            # self.temp_atmosphere(df, i),
            self.temp_atmosphere(df.temp_atmosphere[i - 1],
                                 df.temp_lower[i - 1],
                                 df.forcing[i],
                                 ),
            self.temp_lower(
                df.temp_atmosphere[i - 1], df.temp_lower[i - 1],
                self.params.thermal_transfer
            ),
        )

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
        return ne.evaluate('temp_atmosphere + c1 * (forcing - f * temp_atmosphere - c3 * (temp_atmosphere - temp_lower))')

    def temp_lower(self, temp_atmosphere, temp_lower, thermal_transfer):
        """
        T_LO, Temperature of lower oceans, degrees C
        ...
        Returns
        -------
        float
        """
        c4 = thermal_transfer[3]
        return ne.evaluate('temp_lower + c4 * (temp_atmosphere - temp_lower)')


class Dice2007(TemperatureModel):
    pass


class LinearTemperature(TemperatureModel):
    def get_model_values(self, i, df):
        if i == 0:
            return self.initial_temps[0], None
        temp_atmosphere = (
            self.initial_temps[0] +
            df.carbon_emitted[i - 1] * .002
        )
        return (
            temp_atmosphere,
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
