from damages import *
from carbon import *

def set_models(eq, damages_model, carbon_model, prod_frac,
               _mass_atmosphere, _mass_upper, _mass_lower, _mass_pre):
    """
    Set the models used for damages and oceanic carbon transfer
    ...
    Args
    ----
    eq: obj, the Dice2007 Loop()
    damages_model: str, name of damages model from the front-end
    carbon_model: str, name of carbon model from the front-end
    prod_frac: float,
    _mass_atmosphere: float, M_AT at t=0
    _mass_upper: float, M_UP at t=0
    _mass_lower: float, M_LO at t=0
    _mass_pre: float, M_PI at t=0
    ...
    Returns
    -------
    None
    """
    # set damages model
    if damages_model == 'exponential_map':
        eq.damages_model = ExponentialMap(prod_frac)
    elif damages_model == 'tipping_point':
        eq.damages_model = WeitzmanTippingPoint(prod_frac)
    elif damages_model == 'additive_output':
        eq.damages_model = AdditiveDamages(prod_frac)
    elif damages_model == 'productivity_fraction':
        eq.damages_model = ProductivityFraction(prod_frac)
    else:
        eq.damages_model = DamagesModel(prod_frac)
    # set carbon model
    if carbon_model == 'beam':
        eq.carbon_model = BeamCarbon(
            808.9, 772.4, 38620.5, _mass_pre
        )
    else:
        eq.carbon_model = DiceCarbon(
            _mass_atmosphere, _mass_upper, _mass_lower, _mass_pre,
        )
    