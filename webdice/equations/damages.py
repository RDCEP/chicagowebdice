class DamagesModel(object):
    """
    Various damages models, all return trillions $USD
    """
    def __init__(self):
        pass

    def dice(self, gross_output, temp_atmosphere, aa):
        return gross_output - gross_output / (
            1 + aa[0] * temp_atmosphere + aa[1] * temp_atmosphere ** aa[2]
        )