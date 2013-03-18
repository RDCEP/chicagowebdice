import numpy as np


 def dice_output(gross_output, temp_atmosphere, aa, damage_to_prod):
    return gross_output * (1 - 1 / (
        1 + aa[0] * temp_atmosphere + aa[1] * temp_atmosphere ** aa[2]
    ))


def exponential_map(gross_output, temp_atmosphere, aa, damage_to_prod):
    return gross_output * (1 - np.exp(
        -(aa[0] * temp_atmosphere + aa[1] * temp_atmosphere ** aa[2])
    ))


def tipping_point(gross_output, temp_atmosphere, aa, damage_to_prod):
    return gross_output * (1 - 1 / (
        1 + (temp_atmosphere / 20.46) ** 2 + (temp_atmosphere / 6.081) ** 6.754
    ))

def additive_output(gross_output, temp_atmosphere, aa, damage_to_prod):
    return  gross_output * (1 / 1 + (
        gross_output * 6.3745e-5 * temp_atmosphere ** aa[2]
    ))


def productivity_fraction(gross_output, temp_atmosphere, aa, damage_to_prod):
    if damage_to_prod is False:
        return dice_output(gross_output, temp_atmosphere, aa, damage_to_prod)
    return gross_output * (damage_to_prod)