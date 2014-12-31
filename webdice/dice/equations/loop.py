import utility
import carbon
import damages
import consumption
import emissions
import productivity
import temperature


class Loop(object):
    """
    Provide getters and setters for model equations
    ...
    Args
    ----
    params : obj
    ...
    Kwargs
    ------
    damages_model : obj
    carbon_model : obj
    ...
    Properties
    ----------
    damages_model : obj
    carbon_model : obj
    utility_model : obj
    emissions_model : obj
    productivity_model : obj
    consumption_model : obj
    ...
    Methods
    -------
    set_models()
    """
    def __init__(self, params):
        self._damages_model = params.damages_model
        self._carbon_model = params.carbon_model
        self._temperature_model = params.temperature_model
        self._emissions_model = params.emissions_model
        self._consumption_model = params.consumption_model
        self._utility_model = params.utility_model
        self._productivity_model = params.productivity_model

    @property
    def damages_model(self):
        return self._damages_model

    @damages_model.setter
    def damages_model(self, value):
        self._damages_model = value

    @property
    def carbon_model(self):
        return self._carbon_model

    @carbon_model.setter
    def carbon_model(self, value):
        self._carbon_model = value

    @property
    def temperature_model(self):
        return self._temperature_model

    @temperature_model.setter
    def temperature_model(self, value):
        self._temperature_model = value

    @property
    def emissions_model(self):
        return self._emissions_model

    @emissions_model.setter
    def emissions_model(self, value):
        self._emissions_model = value

    @property
    def productivity_model(self):
        return self._productivity_model

    @productivity_model.setter
    def productivity_model(self, value):
        self._productivity_model = value

    @property
    def consumption_model(self):
        return self._consumption_model

    @consumption_model.setter
    def consumption_model(self, value):
        self._consumption_model = value

    @property
    def utility_model(self):
        return self._utility_model

    @utility_model.setter
    def utility_model(self, value):
        self._utility_model = value

    def set_models(self, params):
        """Set the models used for damages and climate model

        Args:
            :param params: model parameters
             :type params: DiceParams

        Returns:
            :return: None
             :rtype: None
        """
        self.damages_model = getattr(
            damages, "".join(x.capitalize() for x in params.damages_model.split('_'))
        )(params)
        self.carbon_model = getattr(
            carbon, "".join(x.capitalize() for x in params.carbon_model.split('_'))
        )(params)
        params.temperature_model = 'linear_temperature' \
            if params.carbon_model == 'linear_carbon' \
            else 'dice_%s' % params.dice_version
        self.temperature_model = getattr(
            temperature, "".join(x.capitalize() for x in params.temperature_model.split('_'))
        )(params)
        self.productivity_model = getattr(
            productivity, "".join(x.capitalize() for x in params.productivity_model.split('_'))
        )(params)
        self.consumption_model = getattr(
            consumption, "".join(x.capitalize() for x in params.consumption_model.split('_'))
        )(params)
        self.utility_model = getattr(
            utility, "".join(x.capitalize() for x in params.utility_model.split('_'))
        )(params)
        self.emissions_model = getattr(
            emissions, "".join(x.capitalize() for x in params.emissions_model.split('_'))
        )(params)