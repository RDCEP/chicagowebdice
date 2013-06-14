import carbon, damages
from emissions import DiceEmissions
from consumption import DiceConsumption
from utility import DiceUtility
from productivity import DiceProductivity

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
    """
    def __init__(self, params, damages_model=damages.DiceDamages,
                 carbon_model=carbon.DiceCarbon):
        self._damages_model = damages_model
        self._carbon_model = carbon_model
        self._emissions_model = DiceEmissions(params)
        self._consumption_model = DiceConsumption(params)
        self._utility_model = DiceUtility(params)
        self._productivity_model = DiceProductivity(params)

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
    def emissions_model(self):
        return self._emissions_model

    @emissions_model.setter
    def emissions_model(self, value):
        self._emissions_model = value

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

    @property
    def productivity_model(self):
        return self._productivity_model

    @productivity_model.setter
    def productivity_model(self, value):
        self._productivity_model = value

    def set_models(self, damages_model, carbon_model, prod_frac, params):
        """
        Set the models used for damages and oceanic carbon transfer
        ...
        Args
        ----
        eq: obj, the Dice2007 Loop()
        damages_model: str, name of damages model from the front-end
        carbon_model: str, name of carbon model from the front-end
        prod_frac: float,
        ...
        Returns
        -------
        None
        """
        self.damages_model = getattr(
            damages, "".join(x.capitalize() for x in damages_model.split('_'))
        )(prod_frac, params)
        self.carbon_model = getattr(
            carbon, "".join(x.capitalize() for x in carbon_model.split('_'))
        )(params)
        self.productivity_model = DiceProductivity(params)
        self.consumption_model = DiceConsumption(params)
        self.utility_model = DiceUtility(params)
        self.emissions_model = DiceEmissions(params)