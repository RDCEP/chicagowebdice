import damages, carbon
import emissions, consumption, productivity, utility


def set_models(eq, damages_model, carbon_model, prod_frac, params):
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
    eq.damages_model = getattr(
        damages, "".join(x.capitalize() for x in damages_model.split('_'))
    )(prod_frac, params)
    eq.carbon_model = getattr(
        carbon, "".join(x.capitalize() for x in carbon_model.split('_'))
    )(params)
    eq.productivity_model = productivity.ProductivityModel(params)
    eq.consumption_model = consumption.ConsumptionModel(params)
    eq.utility_model = utility.UtilityModel(params)
    eq.emissions_model = emissions.EmissionsModel(params)
