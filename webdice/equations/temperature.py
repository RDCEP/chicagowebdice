from __future__ import division


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
        self._params = params
        self._temp_atmosphere_2005 = params._temp_atmosphere_2000
        self._temp_lower_2005 = params._temp_lower_2000
        self._forcing_co2_doubling = params._forcing_co2_doubling

    @property
    def initial_temps(self):
        return [self._temp_atmosphere_2005, self._temp_lower_2005]

    @initial_temps.setter
    def initial_temps(self, value):
        self._temp_atmosphere_2005 = value[0]
        self._temp_lower_2005 = value[1]

    def get_model_values(self, index, data):
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


class Dice2007(TemperatureModel):
    pass


class LinearTemperature(TemperatureModel):
    def get_model_values(self, index, data):
        if index == 0:
            return self.initial_temps[0], None
        temp_atmosphere = (
            self.initial_temps[0] +
            data.carbon_emitted[index - 1] * .002
        )
        return (
            temp_atmosphere,
            None
        )


class Dice2010(TemperatureModel):
    pass