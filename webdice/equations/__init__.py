from damages import *
from carbon import *

def set_models(eq, damages_model, carbon_model, prod_frac,
               _mass_atmosphere, _mass_upper, _mass_lower, _mass_pre):
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
    if carbon_model == 'beam':
        eq.carbon_model = BeamCarbon(
            808.9, 772.4, 38620.5, _mass_pre
        )
    else:
        eq.carbon_model = DiceCarbon(
            _mass_atmosphere, _mass_upper, _mass_lower, _mass_pre,
        )
    