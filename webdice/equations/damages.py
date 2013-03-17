import numpy as np

class DamagesModel(object):
    """
    Various damages models, all return trillions $USD
    """
    def __init__(self):
        pass

    def dice(self, gross_output, temp_atmosphere, aa):
        return aa[0] * temp_atmosphere + aa[1] * temp_atmosphere ** aa[2]

    def exponential_map(self, gross_output, temp_atmosphere, aa):
        return 1 - np.exp(
            -(aa[0] * temp_atmosphere + aa[1] * temp_atmosphere ** aa[2])
        )

    def tipping_point(self, gross_output, temp_atmosphere, aa):
        return (
            (temp_atmosphere / 20.46) ** 2 + (temp_atmosphere / 6.081) ** 6.754
        )

    def additive(self, gross_output, temp_atmosphere, aa):
        return  (
            gross_output * 6.3745e-5 * temp_atmosphere ** aa[2]
        )

    def fractional_tfp(self, gross_output, temp_atmosphere, aa):
        pass

    def damages(self, gross_output, fraction):
        return (1 - fraction) * gross_output