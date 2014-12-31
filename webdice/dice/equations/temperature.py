# -*- coding: utf-8 -*-
from __future__ import division


class TemperatureModel(object):
    """TemperatureModel base class

    """
    def __init__(self, params):
        self.params = params
        self._temp_atmosphere_2005 = params.temp_atmosphere_init
        self._temp_lower_2005 = params.temp_lower_init
        self._forcing_co2_doubling = params.forcing_co2_doubling

    @property
    def initial_temps(self):
        """Initial values for T_{AT} and T_{LO} at t=0

        Returns:
            :return: [ T_{AT}(0), T_{LO}(0) ]
             :rtype: list
        """
        return [self._temp_atmosphere_2005, self._temp_lower_2005]

    @initial_temps.setter
    def initial_temps(self, value):
        self._temp_atmosphere_2005 = value[0]
        self._temp_lower_2005 = value[1]

    def temp_atmosphere(self, temp_atmosphere, temp_lower, forcing):
        """T_{AT}, increase in atmospheric temperature since 1750, degrees C

        Eq: $T_{AT}(t-1) + ξ_{1} * (F(t) - F_{2xCO2} / T_{2xCO2} * T_{AT}(t-1) - ξ_{3} * (T_{AT}(t-1) - T_{LO}(t-1)))$

        Args:
            :param temp_atmosphere: Atmospheric temperature at t-1
             :type temp_atmosphere: float
            :param temp_lower: Lower ocean temperature at t-1
             :type temp_lower: float
            :param forcing: Forcings at t
             :type forcing: float

        Returns:
            :returns: Atmospheric temperature at t
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

        Eq: $T_{LO}(t-1) + ξ_{4} * (T_{AT}(t-1) - T_{LO}(t-1))

        Args:
            :param i: current time step
             :type i: int
            :param df: Matrix of variable values
             :type df: DiceDataMatrix

        Returns:
            :return: Lower ocean temperature at t
             :rtype: float
        """
        return (
            temp_lower + self.params.thermal_transfer[3] *
            (temp_atmosphere - temp_lower)
        )

    def get_model_values(self, i, df):
        """Get values for model variables.

        Args:
            :param i: current time step
            :type i: int
            :param df: Matrix of variables
            :type df: DiceDataMatrix

        Returns:
            :return: Model variables: T_{AT}, T_{LO}
            :rtype: tuple
        """
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
                forcing - (self.params.forcing_co2_doubling /
                           self.params.temp_co2_doubling) *
                temp_atmosphere - self.params.thermal_transfer[2] *
                (temp_atmosphere - temp_lower)
            )
        )


class Dice2013(Dice2010):
    pass