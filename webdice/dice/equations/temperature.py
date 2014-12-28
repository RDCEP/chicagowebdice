# -*- coding: utf-8 -*-
from __future__ import division


class TemperatureModel(object):
    """TemperatureModel base class

    Properties:
        initial_temps: Values for T_AT, T_OCEAN at t=0

    Methods:
        get_model_values(): Return values for T_AT, T_OCEAN
        temp_atmosphere(): Calculate T_AT at t
        temp_lower(): Calculate T_OCEAN at t
    """
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

    def get_model_values(self, i, df):
        if i == 0:
            return self.initial_temps
        i -= 1
        return (
            self.temp_atmosphere(df.temp_atmosphere[i],
                                 df.temp_lower[i],
                                 df.forcing[i + 1],),
            self.temp_lower(df.temp_atmosphere[i],
                            df.temp_lower[i],),
        )

    def temp_atmosphere(self, temp_atmosphere, temp_lower, forcing):
        """T_AT, increase in atmospheric temperature since 1750, degrees C

         Args:
            :param temp_atmosphere: Atmospheric temperature at t-1
             :type temp_atmosphere: float
            :param temp_lower: Lower ocean temperature at t-1
             :type temp_lower: float
            :param forcing: Forcings at t
             :type forcing: float

        Returns:
            :returns: T_AT(t-1) + ξ_1 * (F(t) - F2xCO2 / T2xCO2 * T_AT(t-1) - ξ_3 * (T_AT(t-1) - T_Ocean(t-1)))
              :rtype: float
        """
        return (
            temp_atmosphere +
            self.params.thermal_transfer[0] * (
                forcing - (self.params.forcing_co2_doubling /
                           self.params.temp_co2_doubling) *
                temp_atmosphere - self.params.thermal_transfer[2] *
                (temp_atmosphere - temp_lower)
            )
        )

    def temp_lower(self, temp_atmosphere, temp_lower):
        """T_AT, increase in atmospheric temperature since 1750, degrees C

         Args:
            :param i: current time step
             :type i: int
            :param df: Matrix of variable values
             :type df: DiceDataMatrix

        Returns:
            :returns: T_Ocean(t-1) + ξ_4 * (T_AT(t-1) - T_Ocean(t-1))
            :rtype: float
        """
        return (
            temp_lower + self.params.thermal_transfer[3] *
            (temp_atmosphere - temp_lower)
        )


class Dice2007(TemperatureModel):
    pass


class LinearTemperature(TemperatureModel):
    def get_model_values(self, i, df):
        if i == 0:
            return self.initial_temps[0], None
        temp_atmosphere = (
            self.initial_temps[0] +
            df.carbon_emitted[i - 1] * (
                self.params.temp_co2_doubling / ((
                    2 * self.params.mass_preindustrial + (
                        2 * self.params.mass_preindustrial -
                        (self.params.mass_atmosphere_init * self.params.carbon_matrix[0][0]) -
                        (self.params.mass_upper_init * self.params.carbon_matrix[1][0])
                    )) * 1e-3)
            ) * 1e-3
        )
        return (
            temp_atmosphere,
            None
        )


class Dice2010(TemperatureModel):
    def __init__(self, params):
        super(Dice2010, self).__init__(params)

    def temp_atmosphere(self, temp_atmosphere, temp_lower, forcing):
        """T_AT, increase in atmospheric temperature since 1750, degrees C

         Args:
            :param temp_atmosphere: Atmospheric temperature at t-1
             :type temp_atmosphere: float
            :param temp_lower: Lower ocean temperature at t-1
             :type temp_lower: float
            :param forcing: Forcings at t
             :type forcing: float

        Returns:
            :returns: T_AT(t-1) + ξ_1 * (F(t) - F2xCO2 / T2xCO2 * T_AT(t-1) - ξ_3 * (T_AT(t-1) - T_Ocean(t-1)))
            :rtype: float
        """
        return (
            temp_atmosphere + self.params.thermal_transfer[0] * (
                forcing - (self.params._forcing_co2_doubling /
                           self.params.temp_co2_doubling) *
                temp_atmosphere - self.params.thermal_transfer[2] *
                (temp_atmosphere - temp_lower)
            )
        )
