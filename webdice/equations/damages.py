import numpy as np

# class DamagesModel(object):
#     """
#     Various damages models, all return trillions $USD
#     """
#     def __init__(self):
#         pass

def after_damages(gross_output, fraction):
    # return (1 - fraction) * gross_output
    return gross_output - gross_output / (1 + fraction)

def dice_output(self, gross_output, temp_atmosphere, aa, damage_to_prod):
    return after_damages(gross_output, (
        aa[0] * temp_atmosphere + aa[1] * temp_atmosphere ** aa[2]
    ))

def exponential_map(self, gross_output, temp_atmosphere, aa, damage_to_prod):
    return after_damages(gross_output, 1 - np.exp(
        -(aa[0] * temp_atmosphere + aa[1] * temp_atmosphere ** aa[2])
    ))

def tipping_point(self, gross_output, temp_atmosphere, aa, damage_to_prod):
    return after_damages(gross_output, (
        (temp_atmosphere / 20.46) ** 2 + (temp_atmosphere / 6.081) ** 6.754
    ))

def additive_output(self, gross_output, temp_atmosphere, aa, damage_to_prod):
    return  after_damages(gross_output, (
        gross_output * 6.3745e-5 * temp_atmosphere ** aa[2]
    ))

def productivity_fraction(self, gross_output, temp_atmosphere, aa, damage_to_prod):
    return after_damages(gross_output, damage_to_prod)

# def dice_output(self, gross_output, temp_atmosphere, aa, damage_to_prod):
#     return gross_output - gross_output / (
#         1 + aa[0] * temp_atmosphere + aa[1] * temp_atmosphere ** aa[2]
#     )